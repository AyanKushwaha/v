# imports ================================================================{{{1
import logging
import os
import re
import sys
import utils.xmlutil as xml

from AbsTime import AbsTime
from RelTime import RelTime
from datetime import datetime
from optparse import OptionParser

from carmensystems.dave import baselib
from utils.xmlutil import xsd
#from utils.dave import EC
from utils.exception import locator
from utils.selctx import BasicContext
try:
    from utils.rave import RaveIterator
    import carmensystems.rave.api as rave
    from tm import TM
except:
    class RaveIterator:
        pass
    rave = None
    TM = None


# setup logging =========================================================={{{1
console = logging.StreamHandler()
console.setFormatter(logging.Formatter('%(name)s: [%(levelname)-8s]: %(message)s'))
logging.getLogger('').handlers = []
log = logging.getLogger('utils.btdtnap')
log.addHandler(console)

#NOTE: Control logging by changing this.
log.setLevel(logging.INFO)

# globals ================================================================{{{1
application = 'bt_dt_nap'
root_name = application
__version__ = '$Revision$'
dtd_file = '%s.dtd' % (application,)



# DutyBlockTimeEntity ----------------------------------------------------{{{2
class DutyBlockTimeCrewEntity(RaveIterator):
    """Iterator class, also contains some constants."""
    entity_name = 'block_time_duty_time'
    comment = "Block time and duty time daily per crew."

    def __init__(self):
        fields = {
            'crew': 'crew.%id%',
        }
        iter = RaveIterator.iter('iterators.roster_set')
        RaveIterator.__init__(self, iter, fields)

# DutyBlockTimeEntity ----------------------------------------------------{{{2
class DutyBlockTimeEntity(RaveIterator):
    """Iterator class, also contains some constants."""
    colnames = (
        ('btdaily', "Block time daily"),
        ('dtkdaily', "Duty time daily k agreement"),
        ('dtoma16daily', "Duty time daily oma16"),
    )

    def __init__(self, lastRun):
        self.now, = rave.eval('fundamental.%now%')
        self.days = int(self.now - lastRun) / 1440
        self.startTime, = rave.eval('round_down(fundamental.%%now%% - %s*24:00, 24:00) - 24:00' % self.days)
        self.endTime = self.startTime + RelTime(24, 0)
        bt_dt_date = 'round_down(%s + fundamental.%%py_index%%*24:00, 24:00)'
        bt_in_period = 'accumulators.%%block_time_in_period_excluding_bought_days%%(%s + fundamental.%%py_index%%*24:00, %s + fundamental.%%py_index%%*24:00)'
        dt_in_period_k_agreement = 'accumulators.%%duty_time_in_period%%(%s + fundamental.%%py_index%%*24:00, %s + fundamental.%%py_index%%*24:00)'
        dt_in_period_oma16 = 'accumulators.%%duty_time_in_interval%%(%s + fundamental.%%py_index%%*24:00, %s + fundamental.%%py_index%%*24:00)'
        fields = {
            'date': bt_dt_date % (self.startTime),
            'btdaily': bt_in_period % (self.startTime, self.endTime),
            'dtkdaily': dt_in_period_k_agreement % (self.startTime, self.endTime),
            'dtoma16daily': dt_in_period_oma16 % (self.startTime, self.endTime),
        }
        iter = RaveIterator.times(self.days)
        RaveIterator.__init__(self, iter, fields)

# get_btdtfile --------------------------------------------------------------{{{2
def get_btdtfile(dir, mode="r"):
    """Get file that stores latest run of BlockTime DutyTime."""
    return open(os.path.join(dir, ".btdt"), mode)

# get_btdt_lastrun --------------------------------------------------------------{{{2
def get_btdt_lastrun(dir):
    """Get latest run of BlockTime DutyTime."""
    try:
        btdt_file = get_btdtfile(dir)
        for line in btdt_file:
            lastRun = AbsTime(line)
            break
        btdt_file.close()
        log.info("First date for BlockTime/DutyTime will be '%s'." % (lastRun))
        return lastRun
    except:
        log.info("No last run recorded for BlockTime/DutyTime, will revert to dump yesterday.")
        return AbsTime(str(datetime.now().date()).replace('-','')).adddays(-1)

# set_btdt_lastrun --------------------------------------------------------------{{{2
def set_btdt_lastrun(dir):
    """Set latest run of DutyTime BlockTime."""
    btdt_file = get_btdtfile(dir, "w")
    print >>btdt_file, str(datetime.now().date()).replace('-','')
    btdt_file.close()

# check_dir --------------------------------------------------------------{{{2
def check_dir(dir, mode=0775):
    """Try to create output directory if not already there."""
    if not os.path.exists(dir):
        os.makedirs(dir, mode)
        log.info("Created directory '%s'." % (dir,))
    return dir


# dump_bt_dt -------------------------------------------------------------{{{2
def dump_bt_dt(dir=os.environ['CARMTMP']):
    """Export the  Blocktime Dutytime "entity" as XML."""
    log.info("BlockTime/DutyTime xml creation started")
    dir = check_dir(dir)
    filename = os.path.join(dir, "%s.xml" % (DutyBlockTimeCrewEntity.entity_name,))
    output = open(filename, "w")
    log.info("Directory: '%s'" % (dir,))
    dbtce = DutyBlockTimeCrewEntity()
    dbte = DutyBlockTimeEntity(get_btdt_lastrun(dir))
    dbtce.link(vals=dbte)

    e = dbtce.entity_name
    bc = BasicContext()

    output.write(str(xml.XMLDocument(xml.COMMENT(DutyBlockTimeCrewEntity.comment), encoding="iso-8859-1")))
    output.write('\n<%s entity="%s" timestamp="%s" type="%s" minCID="%s" maxCID="%s" schema="%s">\n' % (
        root_name,
        e,
        dbte.now, 
        'full',
        0,
        0,
        TM.getSchemaStr()
    ))

    columns = xml.XMLElement('columns')
    columns.append(xml.XMLElement('column', name='crew', type='daveString',
            isRequired='true', desc="Crew ID"))
    columns.append(xml.XMLElement('column', name='date', type='daveAbsTime',
            isRequired='false', desc="Date"))
    for c, desc in dbte.colnames:
        columns.append(xml.XMLElement('column', name=c, type='daveRelTime',
                isRequired='false', desc=desc))
    output.write(str(columns))
    output.write("\n<records>")
    for crew in dbtce.eval(bc.getGenericContext()):
        for r in crew.chain('vals'):
            xml_record = xml.XMLElement(e)
            xml_record.append(xml.string('crew', crew.crew))
            xml_record.append(xml.dateTime('date', getattr(r, 'date')))
            for col, _ in dbte.colnames:
                val = getattr(r, col)
                if not val is None:
                    xml_record.append(xml.duration(col, val))
            output.write("\n")
            output.write(str(xml_record))
    output.write("\n</records>")
    output.write("\n</%s>" % (root_name,))
    output.close()
    log.info("Entity '%s' exported to file '%s'." % (e, filename))
    set_btdt_lastrun(dir)

from tm import TM
import carmensystems.rave.api as R
from AbsTime import AbsTime
import utils.Names
import Cui
import sys
import os

startdate = '01Jan2013'
enddate = '01Mar2013'
nowrun, = R.eval('fundamental.%now%')
now = nowrun.day_floor()
username = utils.Names.username()

def create_entry(crewid, amount):
    crew_generic_entity = TM.table('crew')[(str(crewid),)]
    rec = TM.account_entry.create((TM.createUUID(),))
    rec.crew = crew_generic_entity
    rec.tim = AbsTime(enddate).day_floor()
    rec.account = TM.account_set[('F7S',)]
    rec.source = 'adhoc.sascms5545_script'
    rec.amount = int(amount*100)
    rec.man = False
    rec.rate = 100
    rec.published = True
    rec.reasoncode = 'IN Conversion'
    rec.entrytime = nowrun
    rec.username = username
    rec.si = 'F7S gain for 01Jan2013-28Feb2013'

class F7SGAIN():
    def __init__(self, crewid, legcodes):
        self.crewid = crewid
        self.legcodes = legcodes
        self.gain = 0
        self.exception = ''

    def run(self):
        for legcode in self.legcodes:
            if legcode not in self.exception:
                create_entry(self.crewid, self.gain)
                print "Create entry for", self.crewid, ". Had legcode", legcode, "on roster"
                return 1

        print "crew", self.crewid, "did not get any F7S because", self.legcodes, "on roster"
        return 0

class SKS_CC(F7SGAIN):
    def __init__(self, crewid, legcodes):
        F7SGAIN.__init__(self, crewid, legcodes)
        self.gain = 1.0
        self.exception = ('LA21', 'LA42', 'LA44', 'LA47', 'LA48', 'LA51', 'LA61', 'LA62', 'LA63', 'LA66', 'LA71', 'LA89', 'LA91',
                          'IL12', 'IL14', 'LA91R', 'IL12R', 'IL14R')

class SKD_CC(F7SGAIN):
    def __init__(self, crewid, legcodes):
        F7SGAIN.__init__(self, crewid, legcodes)
        self.gain = 1.5
        self.exception = ('LA47', 'LA51', 'LA76', 'LA89')

class SKN_CC(F7SGAIN):
    def __init__(self, crewid, legcodes):
        F7SGAIN.__init__(self, crewid, legcodes)
        self.gain = 1.0
        self.exception = ('LA41', 'LA44', 'LA48', 'LA51', 'LA63')

def run():
    whereRoster = '(crew.%is_skd% or crew.%is_sks% or crew.%is_skn%)'
    whereRoster += ' and crew.%is_cabin%'
    whereRoster += ' and not (crew.%is_temporary% or crew.%is_temporary_pp_end%)'
    crewdata, = R.eval('sp_crew', R.foreach(R.iter('iterators.roster_set', where=(whereRoster)),
                                            'crew.%id%',
                                            'crew.%region%',
                                            'crew.%is_temporary%',
                                            'crew.%is_temporary_pp_end%',
                                            'crew.%%is_retired_at_date%%(%s)'%startdate,
                                            'crew.%%is_retired_at_date%%(%s)'%enddate,
                                            R.foreach(R.iter('iterators.leg_set', where=('leg.%%start_utc%% <= %s and leg.%%end_utc%% >= %s'%(enddate,startdate))),
                                                      'leg.%code%')
                                                ))
    for (_,crewid,region,temp_start,temp_end,retired_start,retired_end,legs) in crewdata:
        legcodes = [legcode for (_,legcode) in legs]
        if region == 'SKS':
            rc = SKS_CC(crewid, legcodes).run()
        elif region == 'SKD':
            rc = SKD_CC(crewid, legcodes).run()
        elif region == 'SKN':
            rc = SKN_CC(crewid, legcodes).run()

carmusr = os.environ['CARMUSR']
logfile = open(os.path.join(carmusr, 'sascms5545.log'), 'wb')
_before = sys.stdout
sys.stdout=logfile

run()

TM.save()
revid = TM.getSaveRevId()
print "Saved changes with revid %s" % revid
sys.stdout=_before
logfile.close()
Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)

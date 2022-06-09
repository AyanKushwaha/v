from tm import TM
import carmensystems.rave.api as R
from AbsTime import AbsTime
import utils.Names
import Cui

startdate='31Dec2012'
account='F0'
nowrun, = R.eval('fundamental.%now%')
now = nowrun.day_floor()
username = utils.Names.username()

def get_factor(part_time_factor):
    part_time_factor = int(part_time_factor)
    if part_time_factor == 100: return 0.6250
    if part_time_factor >= 89: return 0.5555
    if part_time_factor >= 80: return 0.5000
    if part_time_factor >= 50: return 0.3125
    return "-"

def create_entry(crewid, amount):
    crew_generic_entity = TM.table('crew')[(str(crewid),)]
    rec = TM.account_entry.create((TM.createUUID(),))
    rec.crew = crew_generic_entity
    rec.tim = now
    rec.account = TM.account_set[(account,)]
    rec.source = 'adhoc.F0Conversion'
    rec.amount = int(amount)
    rec.man = True
    rec.rate = (100, -100)[amount < 0]
    rec.published = True
    rec.reasoncode = ('IN Conversion', 'OUT Conversion')[amount < 0]
    rec.entrytime = nowrun
    rec.username = username
    rec.si = '4EXNG Conversion of %s for CC SKD' % account

crewdata, = R.eval('sp_crew', R.foreach(R.iter('iterators.roster_set', where=('crew.%is_skd% and crew.%is_cabin%')),
                                        'crew.%id%',
                                        'crew.%%crew_contract_part_time_factor_at_date%%(%s)'%startdate,
                                        'crew.%%is_retired_at_date%%(%s)'%now,
                                        'compdays.%%balance_at_date%%("%s", %s+24:00)'%(account,now)
                                        ))

for (_,crewid,part_time_factor,is_retired,balance) in crewdata:
    if not get_factor(part_time_factor) == '-':
        amount = balance * get_factor(part_time_factor) - balance
        create_entry(crewid, amount)

TM.save()
revid = TM.getSaveRevId()
print "Saved changes with revid %s" % revid
Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)

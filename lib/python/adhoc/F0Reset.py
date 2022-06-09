from tm import TM
import carmensystems.rave.api as R
from AbsTime import AbsTime
import utils.Names
import Cui

startdate='31Dec2012'
from_account = 'F0'
to_account = 'F3'
nowrun, = R.eval('fundamental.%now%')
now = nowrun.day_floor()
username = utils.Names.username()
    
crewdata, = R.eval('sp_crew', R.foreach(R.iter('iterators.roster_set', where=('crew.%is_skd% and crew.%is_cabin%')),
                                        'crew.%id%',
                                        'crew.%%crew_contract_part_time_factor_at_date%%(%s)'%startdate,
                                        'compdays.%%balance_at_date%%("%s", %s+24:00)'%(from_account,now)
                                        ))

def create_entry(crewid, amount, account):
    
    crew_generic_entity = TM.table('crew')[(str(crewid),)]
    rec = TM.account_entry.create((TM.createUUID(),))
    rec.crew = crew_generic_entity
    rec.tim = now
    rec.account = TM.account_set[(account,)]
    rec.source = 'adhoc.F0Reset'
    rec.amount = int(amount)
    rec.man = True
    rec.rate = (100, -100)[amount < 0]
    rec.published = True
    rec.reasoncode = ('IN Conversion', 'OUT Conversion')[amount < 0]
    rec.entrytime = nowrun
    rec.username = username
    if account == from_account:
        si = '4EXNG Reset %s for CC SKD' % account
    elif account == to_account:
        si = '4ENG Moved %s balance to %s CC SKD' % (from_account, to_account)
    rec.si = si

for (_,crewid,part_time_factor,balance) in crewdata:
    # Reset Account
    create_entry(crewid, -balance, from_account)
    # Move F0 balance to F3
    create_entry(crewid, balance, to_account)
    
TM.save()
revid = TM.getSaveRevId()
print "Saved changes with revid %s" % revid
Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)

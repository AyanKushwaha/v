import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
import AbsTime

__version__ = '2015_11_19'

# 
# This is a standard migrations file that can be reused in every sprint, with change only of the calls to 'set_valid'
# The main purpose is to create the validity paramneter when released to production. After first deployment to PRODTEST the
# validity date should normally set back to a historical value, to be able to test new functionality. Note that this would
# neect to be done by creating a new row and delete the existing, as the validity date is part of the primary key.
#
# Note also how validity of agreemetns is normally used; it tells when an agreement is first applied to rules, using the date of the planning
# period, or in special cases, other date referencing the date. Normally agreements contain stuff that has different expiration time, to any 
# last date of validity is not set. Instead new agreements are implemented, which could either overtake old rules, or make them no longer valid;
# in such cases the test of the rule is modfied to test also for "not new_agreement valid". 
#

def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

hi_date = val_date('31DEC2035')

def set_valid(ops, ag, id, fr_str, descr):
    match_row = {'id':id}
    if len(ag.get_matching_rows(match_row))==0:
        print "validity from",fr_str,"set for",id
        row = ag.crt_row([id, val_date(fr_str), hi_date, descr])
        ag.put_row(ops,row)
    else:
        print "valdity already exist for",id
    

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ag = migrate_table.MigrateTable(dc, fixrunner, 'agreement_validity', ['id','validfrom','validto','si'],2)
    
    ag.load(None)
    set_valid(ops, ag, 'fdc15_sk_se_valid','1JUN2016','fdc15 for SKS_FD and SKIS_FD')

    set_valid(ops, ag, 'k15_qa_FD_feb16','1MAR2016','K15 agreement for QA FD intended for 1FEB2016')
    set_valid(ops, ag, 'k15_qa_CC_daily_duty_hours','1MAR2016','Agreement for QA CC concerning daily duty hours')

    set_valid(ops, ag, 'K15_qa_cc_mar16','1MAR2016','Agreement for QA CC mar 2016')


    return ops
fixit.program = 'rules_validity.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
import AbsTime

__version__ = '2015_10_16'

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
    set_valid(ops, ag, 'k15_jan16','1JAN2016','K15 agreement start date 01JAN2016 ')
    set_valid(ops, ag, 'k15_SKCMS-742-dec15','1DEC2015','K15 Min 12 offset ci and co 01Dec2015')
    set_valid(ops, ag, 'k15_SKCMS-644','1JAN2033','K15 Max blh on LH 2 pilots for crew with hb CPH')
    set_valid(ops, ag, 'k15_leg_in_duty_SKD_FS','1JAN2033','K15 No more than 6 active sectors in dp for SKD-FC')
    set_valid(ops, ag, 'k15_1x24_SKD_FD_AG','30DEC2033','K15 agreement for 1x24 rule for SKD-FD-AG, Unknown start ')
    set_valid(ops, ag, 'k15_feb16','1FEB2016','K15 agreement start date 01FEB2016')


    return ops
fixit.program = 'rules_validity.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



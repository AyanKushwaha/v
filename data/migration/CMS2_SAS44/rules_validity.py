import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
import AbsTime

__version__ = '2017-01-09.1'

# 
# This is a standard migrations file that can be reused in every sprint, with change only of the calls to 'set_valid'
# The main purpose is to create the validity paramneter when released to production. After first deployment to PRODTEST the
# validity date should normally set back to a historical value, to be able to test new functionality. Note that this would
# neect to be done by creating a new row and delete the existing, as the validity date is part of the primary key.
#
# Note also how validity of agreements is normally used; it tells when an agreement is first applied to rules, using the date of the planning
# period, or in special cases, other date referencing the date. Normally agreements contain stuff that has different expiration time, to any 
# last date of validity is not set. Instead new agreements are implemented, which could either overtake old rules, or make them no longer valid;
# in such cases the test of the rule is modfied to test also for "not new_agreement valid". 
#

def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

hi_date = val_date("31DEC2035")

def set_valid(ops, ag, id, fr_str, descr):
    match_row = {"id": id}
    if len(ag.get_matching_rows(match_row)) == 0:
        print "  - validity  - key: '%s' - being set to: '%s', '%s'" % (id, fr_str, descr)
        row = ag.crt_row([id, val_date(fr_str), hi_date, descr])
        ag.put_row(ops,row)
    else:
        print "  - validity - key: '%s' - already exist" % id
    

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    #
    # This is only template - please uncomment this to do actual validity
    #
    ag = migrate_table.MigrateTable(dc, fixrunner, 'agreement_validity', ['id','validfrom','validto','si'], 2)
    
    ag.load(None)
    set_valid(ops, ag, 'stockholm_taxi_17','01FEB2020','Taxi bookings to Stockholm taxi')

    return ops
fixit.program = 'rules_validity.py (%s)' % __version__

if __name__ == '__main__':
    try:
        fixit()
    except fixrunner.OnceException:
        print "    - migration already run with key ",__version__



import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
import AbsTime

__version__ = '2015_11_19'

#
# change of validity from 1 feb to 1 march 
# normally 
#

def val_date(date_str):
    return int(AbsTime.AbsTime(date_str))/24/60

hi_date = val_date('31DEC2035')

def set_valid(ops, ag, id, fr_str, descr, new_fr_str):
    match_row = {'id':id, 'validfrom':val_date(fr_str)}
    if len(ag.get_matching_rows(match_row))==1:
        print "validity from",fr_str," to ",new_fr_str,"set for",id
	row = ag.crt_row([id, val_date(fr_str), hi_date, descr])
        ag.del_row(ops,row)
	
        row = ag.crt_row([id, val_date(new_fr_str), hi_date, descr])
        ag.put_row(ops,row)
    else:
        print "valdity not exakt 1 match",id
    

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ag = migrate_table.MigrateTable(dc, fixrunner, 'agreement_validity', ['id','validfrom','validto','si'],2)
    
    ag.load(None)
    # yes, intended for 1 feb, but presently scheduled for 1mar2016
    set_valid(ops, ag, 'k15qa_feb16','1FEB2016','Cimber union agreement intended for 1feb2016','1MAR2016') 
    set_valid(ops, ag, 'k15_qa_FD_feb16','1FEB2016','K15 agreement for QA FD intended for 1FEB2016','1MAR2016')

    return ops


fixit.program = 'rules_validity.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



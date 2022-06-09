import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
import AbsTime

__version__ = '2015_06_22'


timestart = int(AbsTime.AbsTime('01JAN1986'))/24/60
timeend =   int(AbsTime.AbsTime('31DEC2035'))/24/60


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ag = migrate_table.MigrateTable(dc,fixrunner, 'agmt_group_set' ,['id','validfrom','validto','si'],1)
    print "MigrateTable created"
    ag.load(None)

    row = ag.crt_row(['SNK_CC_AG',timestart,timeend,'Cabin Crew SAS-SNK NO'])
    ag.put_row(ops,row)
    row = ag.crt_row(['NKF_CC_AG',timestart,timeend,'Cabin Crew SAS-NKF NO'])
    ag.put_row(ops,row)
    row = ag.crt_row(['SKN_CC_AG'])
    ag.del_row(ops,row)
    
    ag.write_orig()

    cols = ['id','si','dutypercent','grouptype','pattern','nooffreedays','noofparttime','parttimecode','descshort',
        'desclong','noofvadays','bxmodule','laborunion','congrouptype','conpattern','agmtgroup']
    ce = migrate_table.MigrateTable(dc,fixrunner,'crew_contract_set',cols,1)
    ce.load("agmtgroup='SKN_CC_AG'")
    for row in ce.get_rows():
        if row['agmtgroup'] != 'SKN_CC_AG':
            break
        row['agmtgroup'] = 'NKF_CC_AG'
        ce.put_row(ops,row)
    ce.write_orig() 
    
    print "done,updates=",len(ops)
    #for op in ops:
    #    print str(op)
    return ops


fixit.program = 'skcms_659.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



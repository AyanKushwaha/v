import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
import AbsTime

__version__ = '2015_09_17'


timestart = int(AbsTime.AbsTime('01JAN1986'))/24/60
timeend =   int(AbsTime.AbsTime('31DEC2035'))/24/60


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    cols = ['id','si','name','maintype','crewbunkfc','crewbunkcc','maxfc','maxcc','class1fc',
        'class2fc','class3fc','class1cc','class2cc','class3cc']
    ce = migrate_table.MigrateTable(dc,fixrunner,'aircraft_type',cols,1)
    ce.load("")
    for row in ce.get_rows():
        row['class1fc'] =  row['crewbunkfc']
        row['class3cc'] =  row['crewbunkcc']
        ce.put_row(ops,row)
    ce.write_orig() 
    
    print "done,updates=",len(ops)
    #for op in ops:
    #    print str(op)
    return ops


fixit.program = 'skcms_565.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



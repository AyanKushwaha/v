import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
import AbsTime

__version__ = '2017_01_10'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ag = migrate_table.MigrateTable(dc,fixrunner, 'assignment_attr_set' ,['id','category','si'],1)
    print "MigrateTable created"
    ag.load(None)

    row = ag.crt_row(['IN_CHARGE','Cabin','Cabin in charge in cabin when AP is not used'])
    ag.put_row(ops,row)
    
    ag.write_orig()

    print "done,updates=",len(ops)
    return ops


fixit.program = 'skcms_1239.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



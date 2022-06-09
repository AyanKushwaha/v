import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
import AbsTime
import RelTime

__version__ = '2017_04_10'


@fixrunner.once
@fixrunner.run

def fixit(dc, *a, **k):
    ops = []

    act_set_tbl = migrate_table.MigrateTable(dc, fixrunner, 'activity_set_period', ['id', 'validfrom'],2)
    act_set_tbl.load(None)

    act_set_tbl.del_row(ops, act_set_tbl.crt_row(['E30',0])) 
    act_set_tbl.del_row(ops, act_set_tbl.crt_row(['E50',0])) 
    act_set_tbl.del_row(ops, act_set_tbl.crt_row(['E70',0])) 
    act_set_tbl.del_row(ops, act_set_tbl.crt_row(['E80',0])) 
    act_set_tbl.del_row(ops, act_set_tbl.crt_row(['E90',0])) 

    act_set_tbl.write_orig();
    
    print "Done, updates= ",len(ops)
    return ops


fixit.program = 'skproj_45a (%s)' % __version__

if __name__ == '__main__':
    try:
        fixit()
    except fixrunner.OnceException:
        print "    - migration already run with key ",__version__
                                                                                        

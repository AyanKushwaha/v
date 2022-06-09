import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
import AbsTime

__version__ = '2015_11_24'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    leg_attr_set_table = migrate_table.MigrateTable(dc,fixrunner, 'leg_attr_set' ,['id','category','si'],1)
    print "MigrateTable created"
    leg_attr_set_table.load(None)

    row = leg_attr_set_table.crt_row(['FCBUNKS_CLASS_1','General','Number of first class rest facilities for flight crew'])
    leg_attr_set_table.put_row(ops,row)
    row = leg_attr_set_table.crt_row(['FCBUNKS_CLASS_2','General','Number of second class rest facilities for flight crew'])
    leg_attr_set_table.put_row(ops,row)
    row = leg_attr_set_table.crt_row(['FCBUNKS_CLASS_3','General','Number of third class rest facilities for flight crew'])
    leg_attr_set_table.put_row(ops,row)
    row = leg_attr_set_table.crt_row(['CCBUNKS_CLASS_1','General','Number of first class rest facilities for cabin crew'])
    leg_attr_set_table.put_row(ops,row)
    row = leg_attr_set_table.crt_row(['CCBUNKS_CLASS_2','General','Number of second class rest facilities for cabin crew'])
    leg_attr_set_table.put_row(ops,row)
    row = leg_attr_set_table.crt_row(['CCBUNKS_CLASS_3','General','Number of third class rest facilities for cabin crew'])
    leg_attr_set_table.put_row(ops,row)
    
    leg_attr_set_table.write_orig()
    
    cols = ['id','si','name','maintype','crewbunkfc','crewbunkcc','maxfc','maxcc','class1fc','class2fc','class3fc','class1cc','class2cc','class3cc']
    
    aircraft_type_table = migrate_table.MigrateTable(dc,fixrunner, 'aircraft_type' ,cols ,1)
    aircraft_type_table.load("")
    for row in aircraft_type_table.get_rows():
        row['class2cc'] = row['crewbunkcc']
        row['class3cc'] =0
        if row['id'] == '33R':
            row['class1cc'] = 0
            row['class2cc'] = 0
            row['class3cc'] = 0
            row['class1fc'] = 0
        aircraft_type_table.put_row(ops, row)
    aircraft_type_table.write_orig()
    
    print "done,updates=",len(ops)
    return ops

fixit.program = 'skcms_565.py (%s)' % __version__

if __name__ == '__main__':
    fixit()

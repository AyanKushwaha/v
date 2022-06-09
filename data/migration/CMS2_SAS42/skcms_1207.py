import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
import AbsTime

__version__ = '2016_11_15_a'

vf = int(AbsTime.AbsTime('01JAN1986'))
vt = int(AbsTime.AbsTime('31DEC2035'))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    req_tbl = migrate_table.MigrateTable(dc, fixrunner, "activity_set", ['id','grp','si','recurrent_typ'],1)
    req_tbl.load(None)
    row = req_tbl.crt_row(["WP", "SBA", "Waiting at Airport (prod replace)",""])
    req_tbl.put_row(ops, row)
    row = req_tbl.crt_row(["WO", "SBA", "Waiting Overnight",""])
    req_tbl.put_row(ops, row)
    row = req_tbl.crt_row(["W", "SBA", "Waiting at Airport",""])
    req_tbl.put_row(ops, row)
    row = req_tbl.crt_row(["WTA1", "COD", "Web training Airbus year 1",""])
    req_tbl.put_row(ops, row)
    row = req_tbl.crt_row(["WTA2", "COD", "Web training Airbus year 2",""])
    req_tbl.put_row(ops, row)
    row = req_tbl.crt_row(["WTA3", "COD", "Web training Airbus year 3",""])
    req_tbl.put_row(ops, row)
    row = req_tbl.crt_row(["WTB1", "COD", "Web training Boeing year 1",""])
    req_tbl.put_row(ops, row)
    row = req_tbl.crt_row(["WTB2", "COD", "Web training Boeing year 2",""])
    req_tbl.put_row(ops, row)
    row = req_tbl.crt_row(["WTB3", "COD", "Web training Boeing year 3",""])
    req_tbl.put_row(ops, row)


    req_tbl.write_orig()

    req_tbl = migrate_table.MigrateTable(dc, fixrunner, "activity_set_period", ['id','validfrom','validto','si'],2)
    req_tbl.load(None)
    row = req_tbl.crt_row(["WP",vf,vt,""])
    req_tbl.put_row(ops, row)
    row = req_tbl.crt_row(["WO",vf,vt,""])
    req_tbl.put_row(ops, row)
    row = req_tbl.crt_row(["WTA1",vf,vt,""])
    req_tbl.put_row(ops, row)
    row = req_tbl.crt_row(["WTA2",vf,vt,""])
    req_tbl.put_row(ops, row)
    row = req_tbl.crt_row(["WTA3",vf,vt,""])
    req_tbl.put_row(ops, row)
    row = req_tbl.crt_row(["WTB1",vf,vt,""])
    req_tbl.put_row(ops, row)
    row = req_tbl.crt_row(["WTB2",vf,vt,""])
    req_tbl.put_row(ops, row)
    row = req_tbl.crt_row(["WTB3",vf,vt,""])
    req_tbl.put_row(ops, row)


    req_tbl.write_orig()

    return ops 

fixit.program = 'skcms_1207.py (%s)' % __version__

if __name__ == '__main__':
    try:
        fixit()
    except fixrunner.OnceException:
        print "    - migration already run with key ",__version__


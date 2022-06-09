import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
import AbsTime

__version__ = '2016_09_29'

vf = int(AbsTime.AbsTime('1JUL2016'))/24/60
vt = int(AbsTime.AbsTime('31DEC2035'))/24/60

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    req_tbl = migrate_table.MigrateTable(dc, fixrunner, "country_req_docs", ['country','doc_typ','doc_subtype','validfrom','validto','si'],4)
    req_tbl.load(None)
    row = req_tbl.crt_row(["US", "PASSPORT", "CA,1",vf,vt,""])
    req_tbl.put_row(ops, row)
    row = req_tbl.crt_row(["US", "PASSPORT", "CA,2",vf,vt,""])
    req_tbl.put_row(ops, row)

    req_tbl.write_orig()

    return ops 

fixit.program = 'skcms_1070.py (%s)' % __version__

if __name__ == '__main__':
    try:
        fixit()
    except fixrunner.OnceException:
        print "    - migration already run with key ",__version__


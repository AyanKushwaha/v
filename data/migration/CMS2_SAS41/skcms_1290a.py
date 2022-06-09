import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
import AbsTime

__version__ = '2016_11_10'

vf = int(AbsTime.AbsTime('1JUL2016'))/24/60
vt = int(AbsTime.AbsTime('31DEC2035'))/24/60

def minuteval_date(date_str):
    return int(AbsTime.AbsTime(date_str))

def date_to_int(date_val):
    return date_val if type(date_val) == int else minuteval_date(date_val)



@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    cd_tbl = migrate_table.MigrateTable(dc, fixrunner, "crew_document", ['crew','doc_typ','doc_subtype','validfrom','validto','docno','maindocno','issuer','si','ac_qual'], 4)

    cd_tbl.load("doc_typ = 'REC' and doc_subtype = 'REC'")
    rows = cd_tbl.get_rows()

    print "rows", len(rows) 

    f = open('rec_rec_docs','wb')
    f.write('\n')
    f.write('{\n')
    for r in rows:
        f.write("'"+r['crew']+"' : "+str(r['validto'])+",\n")
    f.write('}\n')
    f.close()

    return ops   

fixit.program = 'skcms_1070a.py (%s)' % __version__

if __name__ == '__main__':
    try:
        fixit()
    except fixrunner.OnceException:
        print "    - migration already run with key ",__version__


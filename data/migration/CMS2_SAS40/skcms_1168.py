import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table

__version__ = '2016_09_06'

def set_ac_empl(ops, tbl, id, descr):
    match_row = {'id':id}
    if len(tbl.get_matching_rows(match_row))==0:
        print "ac_empl set for",id,descr
        row = tbl.crt_row([id, descr])
        tbl.put_row(ops,row)
    else:
        print "row already exist for",id,descr

def convert_minimum_connection(dc, ops):
    print "convert minimum_connection",len(ops)
    cnx_tbl = migrate_table.MigrateTable(dc, fixrunner, 'minimum_connect', ['ac_employer','place','islonghaul','arrtype','deptype','validfrom','validto','cnxfc','cnxcc','trusted'], 6)
    old_tbl = migrate_table.MigrateTable(dc, fixrunner, 'minimum_connection', ['region','place','islonghaul','arrtype','deptype','validfrom','validto','cnxfc','cnxcc','trusted'], 6)
    cnx_tbl.load(None)
    old_tbl.load(None)
    for row in old_tbl.get_rows():
        newrow = cnx_tbl.crt_row([row['region'],row['place'],row['islonghaul'],row['arrtype'],row['deptype'],row['validfrom'],row['validto'],row['cnxfc'],row['cnxcc'],row['trusted']])
        if cnx_tbl.has_row(newrow):
            print "Row already exists minimum_connection: ",newrow
        elif row['region']!='QA':
            cnx_tbl.put_row(ops, newrow)
        if row['region']=='SKD':
            newrow = cnx_tbl.crt_row(['QA',row['place'],row['islonghaul'],row['arrtype'],row['deptype'],row['validfrom'],row['validto'],row['cnxfc'],row['cnxfc'],row['trusted']])
            if cnx_tbl.has_row(newrow):
                print "Row already exists minimum_connection: ",newrow
            else:
                cnx_tbl.put_row(ops, newrow)

    cnx_tbl.write_orig()

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    set_tbl = migrate_table.MigrateTable(dc, fixrunner, "ac_employer_set", ['id','si'],1)
    set_tbl.load(None)
    set_ac_empl(ops, set_tbl, "SKN", "SK SH NO")
    set_ac_empl(ops, set_tbl, "SKD", "SK SH DK")
    set_ac_empl(ops, set_tbl, "SKS", "SK SH SE")
    set_ac_empl(ops, set_tbl, "SKI", "SK LH")
    set_ac_empl(ops, set_tbl, "QA",  "QA SH")
    set_tbl.write_orig()

    convert_minimum_connection(dc, ops)
    print "Done, ops= ",len(ops)
    return ops 

fixit.program = 'skcms_1168.py (%s)' % __version__

if __name__ == '__main__':
    try:
        fixit()
    except fixrunner.OnceException:
        print "    - migration already run with key ",__version__


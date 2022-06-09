import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table

__version__ = '2016_04_02'

def convert_crew_training_log(dc, ops):
    print "convert crew_training_log_tbl ",len(ops)
    crew_training_log_tbl = migrate_table.MigrateTable(dc, fixrunner, 'crew_training_log', ['crew', 'typ', 'code', 'tim', 'attr'], 4)
    crew_training_log_tbl.load(None)
    for row in crew_training_log_tbl.get_matching_rows({'code': '36'}):
        newrow = crew_training_log_tbl.crt_row([row['crew'], row['typ'], '38', row['tim'], row['attr']])
        if crew_training_log_tbl.has_row(newrow):
            print "Row already exists crew_training_log: ",newrow
        else:
            crew_training_log_tbl.put_row(ops, newrow)
        crew_training_log_tbl.del_row(ops, row)
        if len(ops)>50000:
            break
    crew_training_log_tbl.write_orig()

#@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    convert_crew_training_log(dc, ops)
    #_convert_course_content_exc(dc, ops)  no 36 data in db
    #convert_pgt_need(dc, ops) mo valid 36 data in db 
    print "Done, ops= ",len(ops)
    return ops 

fixit.program = 'skcms_703.py (%s)' % __version__

if __name__ == '__main__':
    fixit()

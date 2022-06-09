import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
import AbsTime

__version__ = '2015_11_11'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ag = migrate_table.MigrateTable(dc,fixrunner, 'assignment_attr_set' ,['id','category','si'],1)
    print "MigrateTable created"
    ag.load(None)

    row = ag.crt_row(['BRIEF_NOTIF_NUM','General','Number of notifications regarding check-in on flight'])
    ag.put_row(ops,row)
    row = ag.crt_row(['BRIEF_NOTIF_TIME','General','Time of second checkin-change notification to crew'])
    ag.put_row(ops,row)
    row = ag.crt_row(['BRIEF_ORIGINAL_DELAY','General','The first check-in delay communicated to crew'])
    ag.put_row(ops,row)
    
    ag.write_orig()

    print "done,updates=",len(ops)
    return ops


fixit.program = 'skcms_566.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



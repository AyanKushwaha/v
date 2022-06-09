import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
import AbsTime

__version__ = '2017_04_20'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    bid_periods_group_set = migrate_table.MigrateTable(dc,fixrunner, 'bid_periods_group_set' ,['bid_group','si'],1)
    print "MigrateTable created"
    bid_periods_group_set.load(None)

    row = bid_periods_group_set.crt_row(['FD SH SKN',''])
    bid_periods_group_set.put_row(ops,row)
    row = bid_periods_group_set.crt_row(['FD SH SKS',''])
    bid_periods_group_set.put_row(ops,row)
    row = bid_periods_group_set.crt_row(['FD SH SKD',''])
    bid_periods_group_set.put_row(ops,row)
    row = bid_periods_group_set.crt_row(['FD SH SKN FG',''])
    bid_periods_group_set.put_row(ops,row)
    row = bid_periods_group_set.crt_row(['FD SH SKS FG',''])
    bid_periods_group_set.put_row(ops,row)
    row = bid_periods_group_set.crt_row(['FD SH SKD FG',''])
    bid_periods_group_set.put_row(ops,row)
    row = bid_periods_group_set.crt_row(['FD SH SKN VG',''])
    bid_periods_group_set.put_row(ops,row)
    row = bid_periods_group_set.crt_row(['FD SH SKS VG',''])
    bid_periods_group_set.put_row(ops,row)
    row = bid_periods_group_set.crt_row(['FD SH SKD VG',''])
    bid_periods_group_set.put_row(ops,row)
    
    bid_periods_group_set.write_orig()

    print "done,updates=",len(ops)
    return ops


fixit.program = 'skcms_1434.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



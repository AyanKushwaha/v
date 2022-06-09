

"""
SASCMS-1207

This script will REMOVE all data in the table crew_contact. It will also display all data which
does not originate from an interface. It detects this by looking at the si column. The value for this
must be 'DIG HR-sync', or else it will be treated as a manual entry


"""

import fixrunner


__version__ = '$Revision$'


@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    manual = False
    print "\n"
    for entry in fixrunner.dbsearch(dc, 'crew_contact'):
        if entry['si'] is None or entry['si'] != 'DIG HR-sync':
            print "Manual entry: CREW: %s, TYP: %s, VAL: %s WHICH: %s, SI: %s" % (entry['crew'], entry['typ'], entry['val'], entry['which'], entry['si'])
            manual = True
        ops.append(fixrunner.createOp('crew_contact', 'D', entry))
    if manual:
        print "Keep the manual entries from above and send to SAS for manual insertion to the crew_contact after the migration process is completed"

    if len(ops) > 0:
        print "\n"
        print "After this save all records are deleted."
        print "Do not forget to TRUNCATE THE SCHEMA to completely remove all information properly"
        print "which also includes internal tables such as dave_revision and dave_updated_tables"
        print "This must be done before the table is removed in the following upgrade steps"
    else:
        print "No operations created. Table was already empty"
    return ops


fixit.remark = 'SASCMS-1207 (%s)' % __version__


if __name__ == '__main__':
    fixit()

#!/bin/env python


"""
SKCMS-1779 Add "static" data for crew_qual_acqual airport qualifications
Sprint: SAS68
"""


import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table

__version__ = '2018-05-28'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    crew_qualification_set = migrate_table.MigrateTable(dc, fixrunner, 'crew_qualification_set', ['typ', 'subtype', 'qual_subtype', 'si', 'desclong', 'descshort'], 2)
    crew_qualification_set.load(None)
    apts = crew_qualification_set.get_matching_rows({'typ' : 'AIRPORT'})
    for apt in apts:
        ops.append(fixrunner.createOp('crew_qual_acqual_set', 'N', {'typ': 'AIRPORT', 'subtype': apt['subtype'], 'si' : 'Added in SKCMS-1779'}))
    ops.append(fixrunner.createOp('crew_qualification_set', 'N', {'typ': 'ACQUAL', 'subtype': 'A3A4', 'si' : 'Added in SKCMS-1779'}))

    return ops


fixit.program = 'add_to_qual_set.py (%s)' % __version__
if __name__ == '__main__':
    fixit()

#!/bin/env/python

"""
SKCMS-2054 Modify qualification A3A4 to AWB (Airbus Wide Body). AWB also includes A5 qualification.
Since qual_subtype is part of the key in crew_qual_acqual, we must first add a new row with AWB subtype
then remove the old A3A4 rows.
Sprint: 1903
"""

import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table

__version__ = '2019-02-27'
ops = []


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    # Add AWB to crew_qualification_set if it doesn't exists
    crew_qualification_set = migrate_table.MigrateTable(dc, fixrunner, 'crew_qualification_set',
                                                  ['typ', 'subtype', 'si', 'descshort', 'desclong'], 2)
    crew_qualification_set.load(None)

    add_awb_qual = fixrunner.createOp('crew_qualification_set', 'N',
                                  {'typ': 'ACQUAL',
                                   'subtype': 'AWB',
                                   'si': 'Added in SKCMS-2054'})

    if len(crew_qualification_set.get_matching_rows({'subtype': 'AWB'})) == 0:
        ops.append(add_awb_qual)

    # Add a AWB row for every A3A4 row in crew_qual_acqual
    crew_qual_acqual = migrate_table.MigrateTable(dc, fixrunner, 'crew_qual_acqual',
                                                  ['crew', 'qual_typ', 'qual_subtype', 'acqqual_typ', 'acqqual_subtype',
                                                   'validfrom', 'validto', 'lvl',
                                                   'si'], 6)
    crew_qual_acqual.load(None)
    apts = crew_qual_acqual.get_matching_rows({'qual_subtype': 'A3A4'})

    for entry in apts:
        # Create new entry with AWB qualifications
        ops.append(fixrunner.createOp('crew_qual_acqual', 'N',
                                      {'crew': entry['crew'],
                                       'qual_typ': 'ACQUAL',
                                       'qual_subtype': 'AWB',
                                       'acqqual_typ': entry['acqqual_typ'],
                                       'acqqual_subtype': entry['acqqual_subtype'],
                                       'validfrom': entry['validfrom'],
                                       'validto': entry['validto'],
                                       'lvl': entry['lvl'],
                                       'si': entry['si']}))
    for entry in apts:
        # Remove old A3A4 qualifications
        ops.append(fixrunner.createOp('crew_qual_acqual', 'D', entry))
    ops.append(fixrunner.createOp('crew_qualification_set', 'D',
                                  {'typ': 'ACQUAL',
                                   'subtype': 'A3A4'}))

    return ops


fixit.program = 'AWB_qual.py (%s)' % __version__
if __name__ == '__main__':
    fixit()

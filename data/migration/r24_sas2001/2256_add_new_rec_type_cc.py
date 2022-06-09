"""
SKCMS-2256 Add new recurrent document type for Cabin Crew.
Release: SAS1912
"""


import adhoc.fixrunner as fixrunner

__version__ = '2019-12-20a6'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('crew_document_set', 'N', {'typ': 'REC', 'subtype': 'CRMC', 'si': 'Added in SKCMS-2256'}))

    return ops

fixit.program = '2256_add_new_rec_type_cc.py (%s)' % __version__
if __name__ == '__main__':
    fixit()
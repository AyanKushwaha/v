#!/bin/env python


"""
Copy entries from SAS PROD to SAS TEST for Overtime run #3904. Run this once in
SAS TEST (already done).
"""

import adhoc.fixrunner as fixrunner

from carmensystems.dig.framework.dave import DaveConnector

PROD_URL = 'oracle:cms_production/abvgphqbec_fzp/o@v1crmora1p:1521%v1crmora2p:1521/CARMENP.net.sas.dk'
PROD_SCHEMA = 'cms_production'

__version__ = '$Revision$'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    dc_prod = DaveConnector(PROD_URL, PROD_SCHEMA)
    for rec in fixrunner.dbsearch(dc_prod, 'salary_run_id', 'runid = 3904'):
        del rec['revid']
        ops.append(fixrunner.createop('salary_run_id', 'N', rec))
    for rec in fixrunner.dbsearch(dc_prod, 'salary_basic_data', 'runid = 3904'):
        del rec['revid']
        ops.append(fixrunner.createop('salary_basic_data', 'N', rec))
    return ops


fixit.program = 'cr435_run_in_sas_test_once.py (%s)' % __version__


if __name__ == '__main__':
    fixit()

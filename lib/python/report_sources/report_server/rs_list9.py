

"""
Interface 33_2 - List9.
"""

import os, time
import Crs
from tempfile import mkstemp
from carmensystems.publisher.api import *
import carmensystems.rave.api as R
from report_sources.report_server.rs_if import argfix, add_reportprefix, default_destination


@argfix
@add_reportprefix
def generate(*a, **k):

    # Where to store report files
    exportDir = Crs.CrsGetModuleResource("list9", Crs.CrsSearchModuleDef, "ExportDirectory")
    if exportDir is None:
        exportDir = os.path.expandvars("$CARMTMP")
    # Create directory if it does not exist
    if not os.path.exists(exportDir):
        os.makedirs(exportDir, 0775)
    
    # the PDF report is too big, in order to save memory,
    #   two reports are generated separated by period
    reports = []
    for i in xrange(2):
        # Generate temporary report file name
        (fd, fileName) = mkstemp(
            suffix='.pdf',
            prefix='List9[%d]_%s_' % (i+1, time.strftime('%y%m%d%H%M')),
            dir=exportDir,
            text=True)
        # Generate report
        now = R.eval('fundamental.%now%')
        if i == 0:
            (st, et) = R.eval(
                'add_months(report_common.%month_start%, -1)',
                'report_common.%month_start% - 15*24:00')
        else:
            (st, et) = R.eval(
                'report_common.%month_start% - 15*24:00',
                'report_common.%month_start%')
            
        args = {'firstdate': str(int(st)), 'lastdate': str(int(et))}

        generateReport('report_sources.include.List9',
                       fileName,
                       PDF,
                       args)
        
        reports.append({
            'content-location': fileName,
            'content-type': 'application/pdf',
            'destination': default_destination,
            })
    return reports, False


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof



"""
Interface 33_1 - List12.
"""

import os, time, sys
import Crs
from tempfile import mkstemp
from carmensystems.publisher.api import *
import traceback
from report_sources.report_server.rs_if import argfix, add_reportprefix, default_destination


@argfix
@add_reportprefix
def generate(*a, **k):
    COMPANIES = ['SK','BU']
    MAINRANKS = ['CA','FD']
    BU_BASES = ['OSL','SVG','TRD']  # Company BU only matches these bases
    reports = []
    
    print "** GENERATING LIST12 REPORT WITH ARGS %s, %s **" % (str(a), str(k))

    if k.has_key('base'):
        base = k['base']
    else:
        raise Exception("List12 - Expected parameter 'base'")

    # Where to store report files
    exportDir = Crs.CrsGetModuleResource("list12", Crs.CrsSearchModuleDef, "ExportDirectory")
    if exportDir is None:
        exportDir = os.path.expandvars("$CARMTMP")
    # Create directory if it does not exist
    if not os.path.exists(exportDir):
        os.makedirs(exportDir, 0775)

    monthsBack='1'
    mainranks = MAINRANKS
    ranks = None 
    ranksExcl = None
    if k.has_key('monthsBack'):
        monthsBack=k['monthsBack']
    if k.has_key('mainrank'):
        mainranks=[k['mainrank']]
    if k.has_key('ranks'):
        ranks=k['ranks']
    if k.has_key('ranksExcl'):
        ranksExcl=k['ranksExcl']
    for company in COMPANIES:
      try:
        if company=='BU' and base not in BU_BASES:
            continue
        for mainRank in mainranks:
            # Generate temporary report file name
            if ranks is None:
                rank = mainRank
            else:
                rank = ranks.replace(',','_')
            (fd, fileName) = mkstemp(
                    suffix='.pdf',
                    prefix='List12_%s_%s_%s_%s_' % (company,base,rank,time.strftime('%y%m%d%H%M')),
                    dir=exportDir,
                    text=True)

            # Generate report
            args = {'scheduled': 'yes',
                    'base': base, 'company': company, 'mainRank': mainRank, 'monthsBack': monthsBack}
            if ranks is not None:
                args['ranks'] = ranks
            if ranksExcl is not None:
                args['ranksExcl'] = ranksExcl
            print "Generating report", fileName,"from",os.getpid()
            generateReport('report_sources.include.List12',
                    fileName,
                    PDF,
                    args)
            print "Done!"
            reports.append({
                    'content-location': fileName,
                    'content-type': 'application/pdf',
                    'destination': default_destination,
            })
      except:
        print "Exception caught when generating report for",company
        traceback.print_exc()
    print "I am DONE!"
    return reports, False


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

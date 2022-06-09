#

#
"""
A module that generates reports for one ore more subplans.

The script will for each subplan::
 1. load the subplan
 2. run all reports in crg director(ies), default crew_window_general
 3. store the result in $CARMTMP/reportTests/<subplan path>
 4. create a log file in $CARMTMP/reportTests/<subplan path>/Summary.log
    with success status and generation time for each report

Options:
  -h, --help               this text
  -d, --crgdir= <dir>      include reports from $CARMUSR/crg/<dir>
  -r, --report= <report>   add to list of reports (default all)
  -n <report_name>         output report name (default original_name.txt)
  --solution= <solution>   open an optimizer solution
  --resultdir <dir>        directory where the output should be stored,
                           defaults to: $CARMTMP/reportTests/<subplan path>

Example:
   $CARMUSR/bin/studio.sh -P 'carmtest/reportTests.py -d hidden std_concepts/ba_cc_wwf/lgw_ccr_oct2004/published std_concepts/ba_fc_737/lgw_ccr_oct2004/published'
   
   $CARMUSR/bin/studio.sh -w -P 'carmtest/reportTests.py -d crew_window_general -r RosterStatistics --solution=best_solution reference/ba_cc_wwf_lgw/ccr_oct2004/std-Fairness'
"""

import Cui
from carmstd.plan import SubPlan, LocalPlan
from carmstd.report import Report

import os, dircache, time, sys, getopt

def spOpen(subplan, solution=None):
    lP=LocalPlan(os.path.dirname(subplan))
    sp=SubPlan(os.path.basename(subplan),lP)
    print "loading:" + subplan
    if solution:
        sp.loadSolution(solution)
    else:
        sp.load()

def spReports(subplan, resultDir = None, reportList = [], reportName = None, crgDirs = ["crew_window_general"]):
    """
    Runs all/reportList reports in crgDirs for one subplan
    and store them as text files in the resultDir
    """
    if not resultDir:
        tmpPrefix = os.path.join("$CARMTMP","reportTests", subplan)
    else:
        tmpPrefix = resultDir
    tmpPrefix = os.path.expandvars(tmpPrefix)
    tmpLog = os.path.join(tmpPrefix, "Summary.log")
    if not os.path.exists(tmpPrefix):
      os.system('mkdir -p ' + tmpPrefix)
    else:
      os.system('rm ' + tmpLog)
    os.system('echo ' + subplan + ">>" + tmpLog)

    for crgDir in crgDirs: 
      os.system('echo ' + crgDir + ">>" + tmpLog)
      crgFullPath=os.path.join("$CARMUSR", "crg", crgDir)
      crgFullPath = os.path.expandvars(crgFullPath)
      for report in dircache.listdir(crgFullPath):
	if not report=="CVS" and (reportList==[] or report in reportList):
           start=time.clock()
           if not reportName:
               outPath=os.path.join(tmpPrefix, report+".txt")
           else:
               outPath=os.path.join(tmpPrefix, reportName)
           reportPath=os.path.join(crgDir, report)
	   try:
              print "try generating:"+reportPath+" > "+outPath
	      Report(reportPath).save(outPath)
              resultStr= report + " - %(#)4.3f" % {"#": (time.clock() - start)}
              print "succesfully generated:"+reportPath+" > "+outPath
           except Exception, e:
              print "failed generating:"+reportPath+" > "+outPath
              print e
              resultStr = report + " - failed"
	      # raise
           os.system('echo ' + resultStr + ">>" + tmpLog)

def usage():
    print __doc__

if __name__=='__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd:n:r:", ["solution=", "crgdir=", "resultdir=", "report=", "help"])
    except getopt.GetoptError:
        usage()
        Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)

    crgDir=[]
    reportList=[]
    resultDir= None
    solution=None
    reportName=None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-d", "--crgdir"):
            crgDir.append(a)
        if o == "--solution=":
            solution=a
        if o == "--resultdir": 
            resultDir = a
        if o in ("-n", "--reportname"):
            reportName = a
        if o in ("-r", "--report"):
            reportList.append(a)

    for arg in args:
        try:
            spOpen(arg, solution)
            if len(crgDir) > 0:
                spReports(arg, resultDir, reportList, reportName, crgDir)
            else:
                spReports(arg, resultDir, reportList, reportName)
        except Exception, e:
            print "Failed to open subplan (%s, %s):" % (arg, solution)
            print e
    Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)


#import utils.mdor
#utils.mdor.start(__name__)

import salary.run
#reload(salary.run)
from salary.run import RunData
from AbsTime import AbsTime
import utils.time_util as time_util
from tm import TM

# import os
# from utils.dave import EC
# DB = os.environ.get("DATABASE")
# SCHEMA = os.environ.get("SCHEMA")
# ec = EC(DB, SCHEMA)


"""
# manipulate start and end dates like this:

import carmensystems.rave.api as R
from AbsTime import AbsTime
R.param("salary.%salary_month_start_p%").setvalue(AbsTime("01Sep2015"))
R.param("salary.%salary_month_end_p%").setvalue(AbsTime("01oct2015"))

"""


# crew 38352,21221,28610,11068,21464
def start_run():
    rundata = RunData(
        admcode="T",                        # default: None  (C: cancel, N: normal, R: retro, T: Test)
        note="Terje - test",                # default: None
        runtype="OVERTIME",                # default: PERDIEM  (PERDIEM, OVERTIME, COMPDAYS, TEMP_CREW, ... )
        extsys= "DK",                        # default None  (SE, NO, DK, JP, CN)
        fromStudio=False,                   # default: False
        # monthsBack=1,                      # default: 1
        firstdate=AbsTime("01Sep2015"),    # default: month_start of monthsBack
        lastdate=AbsTime("01Oct2015"),     # default: month_end of monthsBack
        # starttime=AbsTime("10Oct2015"),    # default: now of monthsBack
        # exportformat="FLAT",               # default: "FLAT"
        # noCheckPP=False,                   # default: False
        # spooldir='/home/terjeda/work/CARMUSR/current/current_carmdata/REPORTS/SALARY_EXPORT',
                                            # default: Crs module resource ReleaseDirectory
        commands="start_run",       # for easier grep-ing in log-file
    )
    # rundata_last = RunData(
    #     admcode="T",                        # default: None  (C: cancel, N: normal, R: retro, T: Test)
    #     note="Mahdi Testing",                # default: None
    #     runtype="COMPDAYS",                # default: "PERDIEM"
    #     extsys="SE",                        # default None  (SE, NO, DK, JP, CN)
    #     fromStudio=False,                   # default: False
    #     # monthsBack=1,                      # default: 1
    #     firstdate=AbsTime("01Jun2015"),    # default: month_start of monthsBack
    #     lastdate=AbsTime("01Jul2015 00:01"),     # default: month_end of monthsBack
    #     # starttime=AbsTime("10Aug2015"),    # default: now of monthsBack
    #     # exportformat="FLAT",               # default: "FLAT"
    #     # noCheckPP=False,                   # default: False
    #     # spooldir='/home/terjeda/work/CARMUSR/current/current_carmdata/REPORTS/SALARY_EXPORT',
    #                                         # default: Crs module resource ReleaseDirectory
    #     commands="start_run",       # for easier grep-ing in log-file
    # )
    runid = salary.run.run(rundata)
    return runid


def release_run(runid):
    print "release_run for %d" % runid
    runid_data = TM.salary_run_id[runid, ]
    rundata = RunData(
        runid=runid_data.runid,
        runtype=runid_data.runtype,
        extsys=runid_data.extsys,
        commands="release_run",
    )
    salary.run.release(rundata)



# def runMain():
if __name__ == "__main__":
    print "   ### running ..."
    # print len(QACCCache('01Jul2015', '01Aug2015').set_okIntervals('25995'))
    # qac = QACCCache('01Jul2015', '01Aug2015')
    # print "  ### length is:", str(len(qac.set_okIntervals('15418')))
    # print "  ### length is:", str(len(qac.set_okIntervals('25995')))
#    import dev.terjeda.debug.debug as debug
#    debug.connect(9907)
    runid = start_run()
    print "   ### rundid:", runid
    # runid = 6316
    release_run(runid)
    print "   ### done"

# import pydevd
# try:
#     debughost="devapp01"
#     debugport=5666
#
#     print "Trying to connect to debugger on host \"" + debughost + "\" ,port: " + str(debugport)
#
#     pydevd.settrace(stdoutToServer=True, stderrToServer=True, host=debughost, port=debugport)
#
#     print "Connected to debugger."
#     print "Using pydevd version: " + pydevd.__file__
#     runMain()
# except:
#     print "Failed to connect/attach to debugger. Continuing as normal."
"""
Initialization code for Report Server v2.
"""

import logging
import utils.exception
import os,sys
import traceback

import Cui # to reload etabs
import carmensystems.rave.api as rave
from utils.rave import RaveIterator
from utils.selctx import BasicContext
import modelserver


__console = logging.StreamHandler()
__console.setFormatter(logging.Formatter('%(asctime)s: %(name)s: %(levelname)s %(message)s'))
__rootlogger = logging.getLogger('')
if not __rootlogger.handlers:
    __rootlogger.addHandler(__console)

log = logging.getLogger('dig.rs_init')
log.setLevel(logging.DEBUG)


# prepare ================================================================{{{1
def prepare():
    """This function is called by the Report Server in the setup phase, before
    it starts to clone itself, but after connection to database.

    The purpose of this function is to pre-load as much needed data as possible
    and to "taint" Studio's buffers, so that the following instances of
    ReportWorkers don't have to load all the data themselves.

    This should speed-up the job for the Report Workers.

    cf. Bugzilla #19405.
    """
    log.info("prepare()")
    try:
        setup_rave()
        preload_core()
        preload_accumulators()
        if not 'salary' in os.environ.get('CARM_PROCESS_NAME',''): # Not for CUSTOM
            preload_reports()
            
    except Exception, e:
        log.error("prepare(): %s" % e)
        traceback.print_exc()

    try:
        import_worker()
    except Exception, e:
        log.error("prepare(): %s" % e)
        traceback.print_exc()

    log.info("prepare() ... finished.")



# refresh ================================================================{{{1
def refresh():
    """Code to be run at each refresh, after the plan data has been
    refreshed.
    """
    log.info("refresh()")
    try:
        preload_core()
    except Exception, e:
        log.error("refresh(): %s" % e)

    log.info("refresh() ... finished.")


# Help classes / functions ==============================================={{{1


def import_worker():
    """
    this 'worker' will register services used by crew portal for
    1. getting all trips in open time
    2. get crew info?
    3. create request bids
    
    """
    log.info("importing worker for crew portal communication")

    import interbids.rostering.worker_init
    interbids.rostering.worker_init.setup()
    log.info("import worker done :)!")

    
# setup_rave ============================================================={{{2
def setup_rave():
    # Setup rave parameters for loaded data period
    # Due to a sys-bug, the keyword pp_end_time seems to include the post-buffer
    # in the reportserver. Thus, if we would set the extra_days_loaded_end
    # rave would think that we have loaded a longer period that we actually have.
    # The default value is 0, so by not setting this we get a match between
    # loaded_data_period_end and what is actally loaded
    #import Crs
    #preDbPeriod = Crs.CrsGetModuleResource("config",Crs.CrsSearchModuleDef,"DataPeriodDbPost")
    #rave.param('fundamental.%extra_days_loaded_end%').setvalue(int(preDbPeriod))
    rave.param('fundamental.%is_report_server%').setvalue(True)

    pp_end_time, = rave.eval('pp_end_time')
    pp_start_time, = rave.eval('pp_start_time')
    loaded_start, = rave.eval('fundamental.%loaded_data_period_start%')
    loaded_end, = rave.eval('fundamental.%loaded_data_period_end%')
    log.info("setup_rave(): This is what Rave thinks it has loaded")
    log.info("setup_rave(): Start: %s", loaded_start)
    log.info("setup_rave(): End: %s", loaded_end)
    log.info("setup_rave(): Studio plan period: pp_start_time - pp_end_time: %s-%s" % (pp_start_time, pp_end_time))
    
# preload_reports ========================================================{{{2
def preload_reports():
    # Run all the report services, at least once.
    bc = BasicContext()
    rr = ReportRunner(bc)

    rr.crewBasic()
    rr.crewFlight()
    rr.crewRoster()
    rr.crewList()
    rr.crewLanding()
    rr.futureActivities()
    rr.dutyCalculation()
    rr.getReportList()
    rr.getReportCompDays()
    rr.getReportCrewSlip()
    rr.getReportDutyOvertime()
    rr.getReportPilotLogAccum()
    rr.getReportPilotLogCrew()
    rr.getReportPilotLogFlight()
    rr.getReportPilotLogSim()
    rr.getReportVacation()

# preload_accumulators ==================================================={{{2
def preload_accumulators():
    # Preload accumulator tables
    log.info("preload accumulator tables start...")
    rave.eval('studio_process.%preload_rave%')
    log.info("preload accumulator tables finished")

# preload_core ==========================================================={{{2
def preload_core():
    # Preload core tables in published mode
    # Note: The report server does not preload core tables in
    # the model server in published mode. Any core tables
    # accessed by the report scripts through the model server
    # in published mode must be preloaded here. (ref BZ 25444)
    # The core tables are:
    #  crew
    #  flight_leg
    #  crew_flight_duty
    #  ground_task
    #  crew_ground_duty
    #  crew_activity
    bc = BasicContext()
    if not bc.publishType is None:
        log.info("preload core tables start...")
        tm = modelserver.TableManager.instance()
        log.debug("flight_leg size before: %d" % tm.table('flight_leg').size())
        log.debug("crew size before: %d" % tm.table('crew').size())
        tm.loadTables(['flight_leg', 'crew'])
        log.debug("flight_leg size after: %d" % tm.table('flight_leg').size())
        log.debug("crew size after: %d" % tm.table('crew').size())
        log.info("preload core tables finished")


# ReportRunnerError ------------------------------------------------------{{{2
class ReportRunnerError(Exception):
    msg = ''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)

    def __repr__(self):
        return repr(self.msg)


# ReportRunner -----------------------------------------------------------{{{2
_rs_init_rosters = None
class ReportRunner:
    """Run some different crew services reports."""
    def __init__(self, bc):
        """Get info about an existing crew and an existing flight."""
        global _rs_init_rosters
        log.debug("%s()" % _locator(self),)

        ri = RaveIterator(
            RaveIterator.iter('iterators.roster_set'),
            {
                'empno' : 'crew.%employee_number%',
                'flight_id': 'report_crewlists.%t_first_flight_id%',
                'udor': 'report_crewlists.%t_first_flight_udor%',
                'adep': 'report_crewlists.%t_first_flight_adep%',
                'ades': 'report_crewlists.%t_first_flight_ades%',
                'std_utc': 'report_crewlists.%t_first_flight_std_utc%',
                'std_lt': 'report_crewlists.%t_first_flight_std_lt%',
                'gd_start': 'report_crewlists.%t_first_non_flight_start%',
                'gd_code': 'report_crewlists.%t_first_non_flight_code%',
                'startdate': 'report_crewlists.%t_start_date%',
                'enddate': 'report_crewlists.%t_end_date%',
                'ca1': 'report_crewlists.%t_first_flight_ca1%',
            }
        )
        if _rs_init_rosters is None:
            _rs_init_rosters = ri.eval(bc.getGenericContext())
            log.info("Finished loading global roster set")
        for roster in _rs_init_rosters:
            self.data = roster
            if not roster.udor is None:
                break
        else:
            raise ReportRunnerError("%s(): No rosters found." % _locator(self))

    def crewBasic(self):
        log.debug("%s()" % _locator(self))
        import report_sources.report_server.rs_crewbasic
        self.run(report_sources.report_server.rs_crewbasic.generate, ((), {
            'empno': self.data.empno,
            'searchDate': "%04d%02d%02d" % self.data.udor.split()[:3],
            'getCrewBasicInfo': 'Y',
            'getCrewContact': 'Y',
        }))

    def crewFlight(self):
        log.debug("%s()" % _locator(self))
        import report_sources.report_server.rs_crewflight
        self.run(report_sources.report_server.rs_crewflight.generate, ((), {
            'flightId': self.data.flight_id,
            'originDate': "%04d%02d%02d" % self.data.udor.split()[:3],
            'depStation': self.data.adep,
            'arrStation': self.data.ades,
            'getTimesAsLocal': 'Y',
        }))

    def crewRoster(self):
        log.debug("%s()" % _locator(self))
        import report_sources.report_server.rs_crewroster
        self.run(report_sources.report_server.rs_crewroster.generate, ((), {
            'empno': self.data.empno,
            'getPublishedRoster': 'Y',
            'getTimesAsLocal': 'N',
            'getCrewBasicInfo': 'Y',
            'getFlightLegSVC': 'Y',
            'getSling': 'N',
            'startDate': "%04d%02d%02d" % self.data.startdate.split()[:3],
            'endDate': "%04d%02d%02d" % self.data.enddate.split()[:3],
        }))

    def crewList(self):
        log.debug("%s()" % _locator(self))
        import report_sources.report_server.rs_crewlist
        self.run(report_sources.report_server.rs_crewlist.generate, ((), {
            'activityId': self.data.flight_id,
            'date': "%04d%02d%02d" % self.data.std_utc.split()[:3],
            'requestDateAsOrigin': 'N',
            'requestDateInLocal': 'N',
            'depStation': self.data.adep,
            'arrStation': '',
            'std': "%02d:%02d" % self.data.std_utc.split()[3:5],
            'mainRank': '',
            'getPublishedRoster': 'Y',
            'getTimesAsLocal': 'N',
            'getLastFlownDate': 'Y',
            'getNextFlightDuty': 'Y',
            'getPrevNextDuty': 'Y',
            'getPrevNextAct': 'Y',
            'getCrewFlightDocuments': 'Y',
            'getPackedRoster': 'Y',
            'getPackedRosterFromDate': '',
            'getPackedRosterToDate': '',
        }))

    def crewLanding(self):
        log.debug("%s()" % _locator(self))
        import report_sources.report_server.rs_crewlanding
        self.run(report_sources.report_server.rs_crewlanding.generate, ((), {
            'flightId': self.data.flight_id,
            'originDate': "%04d%02d%02d" % self.data.udor.split()[:3],
            'depStation': self.data.adep,
            'arrStation': self.data.ades,
            'empno': self.data.empno,
        }))

    def futureActivities(self):
        log.debug("%s()" % _locator(self))
        import report_sources.report_server.rs_futureactivities
        self.run(report_sources.report_server.rs_futureactivities.generate, ((), {
            'empno': self.data.empno,
            'startDate': "%04d%02d%02d" % self.data.udor.split()[:3],
        }))

    def dutyCalculation(self):
        log.debug("%s()" % _locator(self))
        import report_sources.report_server.rs_dutycalculation
        self.run(report_sources.report_server.rs_dutycalculation.generate, ((), {
            'perKey': self.data.empno,
            'startDate': "%04d%02d%02d" % self.data.startdate.split()[:3],
            'endDate': "%04d%02d%02d" % self.data.enddate.split()[:3],
            'showNI': 'N',
        }))

    def getReportList(self):
        log.debug("%s()" % _locator(self))
        import report_sources.report_server.rs_getreportlist
        self.run(report_sources.report_server.rs_getreportlist.generate, ((), {}))

    def getReportCompDays(self):
        log.debug("%s()" % _locator(self))
        year = "%04d" % self.data.startdate.split()[0]
        self._getReport(['COMPDAYS', 3, self.data.empno, 'F7', year])

    def getReportCrewSlip(self):
        log.debug("%s()" % _locator(self))
        monthabbr = str(self.data.startdate)[2:5]
        year = "%04d" % self.data.startdate.split()[0]
        self._getReport(['CREWSLIP', 3, self.data.empno, monthabbr, year])

    def getReportDutyOvertime(self):
        log.debug("%s()" % _locator(self))
        monthabbr = str(self.data.startdate)[2:5]
        year = "%04d" % self.data.startdate.split()[0]
        self._getReport(['DUTYOVERTIME', 3, self.data.empno, monthabbr, year])

    def getReportPilotLogAccum(self):
        log.debug("%s()" % _locator(self))
        self._getReport(['PILOTLOGACCUM', 1, self.data.empno])

    def getReportPilotLogCrew(self):
        log.debug("%s()" % _locator(self))
        monthabbr = str(self.data.startdate)[2:5]
        year = "%04d" % self.data.startdate.split()[0]
        self._getReport(['PILOTLOGCREW', 2, self.data.empno, monthabbr, year])

    def getReportPilotLogFlight(self):
        log.debug("%s()" % _locator(self))
        date = "%04d%02d%02d" % self.data.udor.split()[:3]
        self._getReport(['PILOTLOGFLIGHT', 3, self.data.empno, self.data.flight_id, date])

    def getReportPilotLogSim(self):
        log.debug("%s()" % _locator(self))
        monthabbr = str(self.data.startdate)[2:5]
        year = "%04d" % self.data.startdate.split()[0]
        self._getReport(['PILOTLOGSIM', 2, self.data.empno, monthabbr, year])

    def getReportVacation(self):
        log.debug("%s()" % _locator(self))
        year = "%04d" % self.data.startdate.split()[0]
        self._getReport(['VACATION', 3, self.data.empno, "VA", year])

    def run(self, report, a):
        log.debug("%s(%s, %s)" % (_locator(self), report, a))
        try:
            rlist, use_delta = report(a)
            log.debug("... %s" % rlist[0]['content'].split('\n')[0],)
        except Exception, e:
            prev = sys._getframe(1).f_code.co_name
            if prev == '_getReport':
                prev = sys._getframe(2).f_code.co_name
            log.error("%s(%s, %s) failed (last function was '%s'). [%s]" % (_locator(self), report, a, prev, utils.exception.getCause()))

    def _getReport(self, a):
        log.debug("%s()" % _locator(self))
        import report_sources.report_server.rs_getreport
        args = ['GetReport'] + a
        self.run(report_sources.report_server.rs_getreport.generate, (args, {}))


# _locator ---------------------------------------------------------------{{{2
def _locator(o):
    """Return 'module.class.method'."""
    return "%s.%s.%s" % (o.__class__.__module__, o.__class__.__name__,
            sys._getframe(1).f_code.co_name)



# __main__ ==============================================================={{{1
if __name__ == '__main__':
    log.setLevel(logging.DEBUG)
    prepare() # Basic test
    refresh() # Basic test


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

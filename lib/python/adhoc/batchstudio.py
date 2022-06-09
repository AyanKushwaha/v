

"""
Decorator that helps developers run small (one-time) scripts in Studio.

Example:
    import adhoc.batchstudio as batchstudio
    import crewlists.crewlanding as crewlanding
    from AbsTime import AbsTime
    from tm import TM

    @batchstudio.run(plan="TestPlans/Tracking/sk_master_090925/sk_master_090925",
                     plan_start="20090801", plan_end="20090930", ruleset="Tracking")
    def run():
        # IMPORTANT: MUST BE PRELOADED BEFORE newState()
        TM('crew_landing')
        # IMPORTANT: newState() must be called!
        TM.newState()
        crewlanding.run(AbsTime(2009, 8, 19, 0, 0), AbsTime(2009, 9, 24, 0, 0))


    if __name__ == '__main__':
        run()

Note that we use hardcoded values for plan and period. These can of course be
fetched from environment, but remember that argument handling is somewhat
complicated because of the multitude of scripts involved when starting Studio.
"""

__all__ = ['batch_runner', 'run']
__version__ = '$Revision$'
default_ruleset = 'Tracking'

import os
import logging

import __main__
import Cui

from AbsTime import AbsTime
from Variable import Variable


# Set up logging ========================================================={{{1
logging.basicConfig()
log = logging.getLogger('batchstudio')
log.setLevel(logging.INFO)


# BatchRunner ============================================================{{{1
class BatchRunner:
    """This class can be subclassed to make more advanced things."""

    def run(self, plan=None, plan_start=None, plan_end=None, ruleset=default_ruleset):
        """The main function, which is a Python decorator."""
        if plan is None or plan_start is None or plan_end is None:
            raise ValueError("Must give options 'plan', 'plan_start', and, 'plan_end'.")
        def decorator(func):
            def wrapper(*a, **k):
                self.open_plan(plan, plan_start, plan_end, ruleset)
                func(*a, **k)
                self.save_plan()
            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            wrapper.__dict__ = func.__dict__
            return wrapper
        return decorator

    def open_plan(self, plan, plan_start, plan_end, ruleset):
        try:
            pstart = AbsTime(plan_start)
        except:
            log.error("Wrong format of plan_start (%s)" % plan_start)
            raise
        try:
            pend = AbsTime(plan_end)
        except:
            log.error("Wrong format of plan_end (%s)" % plan_end)
            raise

        log.info("Opening plan '%s' with interval '%s' - '%s' and ruleset '%s'." % (
            plan, pstart, pend, ruleset))

        __main__.PERIOD_START = Variable(pstart)
        __main__.PERIOD_END   = Variable(pend)

        try:
            ret = Cui.CuiOpenSubPlan({
                    "FORM": "OPEN_DATABASE_PLAN", 
                    "PERIOD_START":" %s" % pstart,
                    "PERIOD_END":" %s" % pend,
                }, Cui.gpc_info, os.path.dirname(plan), plan,
                Cui.CUI_OPEN_PLAN_FORCE)
        except Exception, e:
            log.error("Failed to open plan '%s'. (%s)", plan, e)
            raise
        Cui.CuiCrcLoadRuleset(Cui.gpc_info, ruleset)

    def save_plan(self):
        try:
            Cui.CuiSavePlans(Cui.gpc_info, 0)
        except Exception, e:
            log.error("Could not save plan. %s" % e)
            raise
        Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)


# batch_runner ==========================================================={{{1
batch_runner = BatchRunner()


# run ===================================================================={{{1
run = batch_runner.run


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

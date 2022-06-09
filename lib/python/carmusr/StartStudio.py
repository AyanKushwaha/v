####################################################

#
# Contains:
#  Startup scripts for Studio
#
# Created: July 2007
# By: Markus Kollind, Jeppesen
#

import os
import time
import Errlog
import Cui
import Gui
import carmstd.plan as plan
import AbsTime
from AbsTime import PREV_VALID_DAY
import time
import Variable as PYV
import utils.ServiceConfig as ServiceConfig
from carmensystems.basics.CancelException import CancelException

def planning():
    pass

def prerostering(plan_path=None):
    Errlog.log("PrePlanner: Starting up...")

    # Gets the plan to load from the XML config files. 
    c = ServiceConfig.ServiceConfig()
    if not plan_path:
	plan_path = c.getProperty("data_model/plan_path")[1]
    lp_path = os.path.dirname(plan_path)

    flags = Cui.CUI_OPEN_PLAN_FORCE
    try:
        ret = Cui.CuiOpenSubPlan(Cui.gpc_info, lp_path, plan_path, flags)
        Errlog.log("PRE::load::opened subplan: %s ret = %s" % (plan_path,ret))
    except CancelException:
        Errlog.log("PRE::load::User cancelled operation")
    except KeyboardInterrupt, e:
        pass
    except Exception, e:
        Errlog.log("PRE::load::Failed to load subplan: %s" % plan_path)
        raise e

    # Display roster
    Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiArea0, Cui.CrewMode, Cui.CuiShowAll)
    
    Errlog.log("PrePlanner: Finished starting up")



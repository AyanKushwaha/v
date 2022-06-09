#

#
#
# Purpose: PlanningGroupSelect is a wrapper around "show" commands
#          to make them show information based on what crew has "opened".
#

import Cui
import Select
import carmusr.tracking.FileHandlingExt

AREA_ACROT_PLANNING_GROUPS = {
                              "SKN": "SKN",
                              "SKD": "SKD",
                              "SKS": "SKS",
                              "SKI": "SK"
                             }

def showACRot(area, filter_method):
    """
    Show rotations for flights belonging to the opened planning group.

    """

    planning_area = \
        carmusr.tracking.FileHandlingExt.open_plan_handler.PLANNING_AREA
    planning_groups = AREA_ACROT_PLANNING_GROUPS.get(planning_area, "*")

    # Perform the selection.
    Select.select({'FILTER_METHOD': filter_method,
                   'leg.%ac_planning_group%': planning_groups,
                   'leg.%is_ground_duty%': False
                   }, area, Cui.AcRotMode)

def showLegalIllegalACRot(area, showType):
    """
    Show legal or illegal rotations and subselect planning group.

    """

    # Show the legal or illegal rotations.
    Cui.CuiDisplayObjects(Cui.gpc_info, area, Cui.AcRotMode, showType)

    # Subselect only rotations of the planning group loaded.
    showACRot(area, "SUBSELECT")

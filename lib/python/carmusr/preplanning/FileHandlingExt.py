

"""
Module containing callback functions that are called by Studio before/after
opening/saving plans.

This module contains definitions for Pre-Studio (Pre-Rostering).
"""

import traceback
import Errlog   
import carmusr.planning.FileHandlingExt
import carmusr.preplanning.actions as actions

MODULE = 'carmusr.preplanning.FileHandlingExt'
# These functions are not changed for PreRostering, use the planning variants
# unchanged.
setDaveLoadFilters = carmusr.planning.FileHandlingExt.setDaveLoadFilters
openPlanPreProc = carmusr.planning.FileHandlingExt.openPlanPreProc


def openPlanPostProc():
    """Call carmusr.planning.FileHandlingExt.openPlanPostProc() and create
    temporary table used for Rudobs."""
    FUNCTION = '::openPlanPostProc::'
    Errlog.log(MODULE+FUNCTION + " Entered")
    carmusr.planning.FileHandlingExt.openPlanPostProc()
    try:
        # Creating temporary (memory) table used for informed Rudob.
        actions.init()
    except Exception, e:
        Errlog.log("FileHandlingExt::openPlanPostProc:: could not create temporary table.")
        traceback.print_exc()
    return 0


def savePlanPreProc():
    """Call carmusr.planning.FileHandlingExt.savePlanPreProc() and collect list
    of crew to be published."""
    FUNCTION = '::savePlanPreProc::'
    Errlog.log(MODULE+FUNCTION + " Entered")
    rc = carmusr.planning.FileHandlingExt.savePlanPreProc()
    # We will have to loop thru the crew list here, since published_roster
    # is an entity just like any other.
    try:
        actions.pre_save_publish()
    except:
        Errlog.log("Error at pre_save_publish.")
        traceback.print_exc()
    return rc


def savePlanPostProc():
    """Call carmusr.planning.FileHandlingExt.savePlanPostProc() and commit
    publication."""
    FUNCTION = '::savePlanPostProc::'
    Errlog.log(MODULE+FUNCTION + " Entered")
    try:
        actions.post_save_publish()
    except:
        Errlog.log("Error at post_save_publish.")
        traceback.print_exc()
    return carmusr.planning.FileHandlingExt.savePlanPostProc()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

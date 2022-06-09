#

#
#
# Purpose: Changeposition is a wrapper to the position change calls.
#          This is to run the trip cleaner on affected legs afterwards.
#
# Author:  Stefan Lennartsson
# Date:    2008-08-21
#

import Cui
import carmensystems.rave.api as R
import carmstd.cfhExtensions as cfhExtensions
import carmusr.tracking.TripTools as TripTools

def changeAssignedPosition(category, position):
    """
    Change position on marked legs.
    Remove any overbooked trips connected to changed leg afterwards.
    """
    windArea = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    workArea = Cui.CuiScriptBuffer
    
    # Get all marked legs.
    marked_legs = Cui.CuiGetLegs(Cui.gpc_info, windArea)
    
    # Make sure all crew with marked legs are within the same maincat.
    Cui.CuiDisplayGivenObjects(Cui.gpc_info, workArea, Cui.CrewMode,
        Cui.LegMode, [str(legid) for legid in marked_legs])
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, workArea, "window")
    cat_for_crew_with_marked_legs, = R.eval("default_context",
        R.foreach(R.iter('iterators.chain_set'), 'crew.%main_func%',))
    for ix, crew_cat in cat_for_crew_with_marked_legs:
        if crew_cat != category:
            cfhExtensions.show(
                "Cannot change position to %s.\n"
                "Both Cabin and Flight Deck activities are marked." % position
                , title="Warning")
            return 1

    # Change position on marked legs in current area.
    Cui.CuiChangeAssignedPosition(Cui.gpc_info,
        category, position, Cui.CUI_CHANGE_ASS_POS_SEG)

    # Call the trip cleaner for all the marked legs.
    TripTools.tripClean(windArea, marked_legs)

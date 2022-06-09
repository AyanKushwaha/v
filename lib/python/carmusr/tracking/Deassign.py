#

#
#
# Purpose: Deassign is a wrapper to the deassign calls.
#          This is to run the trip cleaner on affected legs afterwards.
#          Also contains cancel manually created flight feature
#
# Author:  Stefan Lennartsson
# Date:    2008-08-21
#

import Cui
import Gui
import traceback
import carmusr.tracking.TripTools as TripTools
import carmstd.cfhExtensions as cfhExtensions
import carmensystems.rave.api as rapi
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator
from tm import TM

def deassign(area, ctrlpressed = 0):
    """
    Deassign all marked legs in area.

    """

    # If no legs are marked we should not do anything.
    marked_legs = Cui.CuiGetLegs(Cui.gpc_info, area)
    if len(marked_legs) == 0:
        return
    
    # Deassign the trip.
    deassigned_legs = deleteFromRoster(area)
    if len(deassigned_legs) > 0:
        # Display the deassigned legs in tripmode in the scriptbuffer.
        Cui.CuiDisplayGivenObjects(Cui.gpc_info,
                                   Cui.CuiScriptBuffer,
                                   Cui.CrrMode,
                                   Cui.LegMode,
                                   [str(leg_id) for leg_id in deassigned_legs],
                                   )

        # Call the trip cleaner for all the deassigned legs.
        TripTools.tripClean(Cui.CuiScriptBuffer, deassigned_legs)

    Gui.GuiCallListener(Gui.ActionListener)
    Gui.GuiCallListener(Gui.RefreshListener)

def deleteFromRoster(area):
    fromArea = Cui.CuiAreaIdConvert(Cui.gpc_info, area)
    if fromArea == Cui.CuiNoArea:
        return -1
    legList = deleteMarkedTrip(fromArea)
    return legList

def deleteMarkedTrip(area):
    flags = 0
    try:
        legList = []
        Cui.CuiRemoveAssignments(Cui.gpc_info,area,"",flags,legList)
        return legList
    except:
        traceback.print_exc()
        return []

def cancelManuallyCreatedFlight(area):
    """
    Remove marked test flights in area.

    """

    # Force a syncModel before finding the legs to remove
    Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)

    # Get information about which legs the user have marked
    marked_legs = Cui.CuiGetLegs(Cui.gpc_info, area)

    # For each of the legs we need to get the leg identifier in the generic model consisting of UDOR, FD and ADEP
    # Creating a context object for leg level to be reused inside the loop 
    con = rapi.selected("levels.leg")

    # Converting the variable strings to rave variable objects to be reused inside the loop
    vars = [rapi.var(item) for item in ('leg.udor',
                                        'leg.flight_descriptor',
                                        'leg.start_station')]

    # Storing current context
    currentContext = CuiContextLocator().fetchcurrent()

    for leg in marked_legs:
        # Setting focus on the interesting object
        CuiContextLocator(Cui.CuiWhichArea, "OBJECT", Cui.LegMode, str(leg)).reinstate()

        # Fetch the data from rave
        udor,fd,adep = rapi.eval(con, *vars)

        # Get a reference to the airport.
        adepRef = TM.airport[adep]

        # Get the real flight leg.
        flight = TM.flight_leg[(udor, fd, adepRef)]

        # Get a reference to the cancel statcode
        cancel = TM.leg_status_set["C"]

        # We should only remove test flights
        if flight.statcode.id == "M":
            flight.statcode = cancel

        else:
            cfhExtensions.show("Flight %s is not a manually created flight.\nNot allowed to cancel." %(fd),
                               title="Cancel denied.")   

    # Resetting current context to the one that already was. This is not necessary but could be useful to think about when dealing with contexts.
    currentContext.reinstate()

    # Force a syncModel before finding the legs to remove
    Cui.CuiSyncModels(Cui.gpc_info, Cui.CUI_SAVE_SILENT)

    # Redraw the GUI
    Gui.GuiCallListener(Gui.ActionListener)
    Gui.GuiCallListener(Gui.RefreshListener)



"""
PruneDb

Prunes the database to the selected crew, trips and legs in the windows.
"""

import sys

import Cui
import carmstd.cfhExtensions
import carmensystems.rave.api as R
import carmensystems.studio.plans.Common as Common

debugMode=True

def pruneDb():
  crewList, tripList, flightList, groundDutiesList = getSelectedData()

  if len(crewList) == 0 and len(tripList) == 0 and len(flightList) == 0 and len(groundDutiesList) == 0:
    carmstd.cfhExtensions.show("There must be at least one crew, trip or leg in the open window(s). ")
    return 1

  removeData(crewList, tripList, flightList, groundDutiesList)

  exportDb()


def getSelectedData():
  """
  Gets the crew, trips and legs in the different windows
  """
  crewArea = Cui.CuiGetAreaInMode(Cui.gpc_info, Cui.CrewMode, Cui.CuiNoArea)
  tripArea = Cui.CuiGetAreaInMode(Cui.gpc_info, Cui.CrrMode, Cui.CuiNoArea)
  legArea = Cui.CuiGetAreaInMode(Cui.gpc_info, Cui.LegMode, Cui.CuiNoArea)

  crewInWindow = getCrewInWindow(crewArea)
  tripsInWindow = getTripsInWindow(tripArea)
  flightsInWindow, groundDutiesInWindow = getLegsInWindow(legArea)

  if debugMode:
    print "Selected Crew:"
    print crewInWindow
    print
    print "Selected Trips:"
    print tripsInWindow
    print
    print "Selected Flights:"
    print flightsInWindow
    print
    print "Selected Ground Duties:"
    print groundDutiesInWindow
    print

  return crewInWindow, tripsInWindow, flightsInWindow, groundDutiesInWindow


def getCrewInWindow(crewArea):
  crewInWindow = []
  
  if crewArea != Cui.CuiNoArea:
    # get list of crew id for all crew
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, crewArea, "window")
    crewInWindow, = R.eval("default_context", R.foreach('iterators.roster_set', 'crew.%id%'))

    # Remove the ix
    crewInWindow = [str(crew) for _, crew in crewInWindow]
    
  return crewInWindow


def getTripsInWindow(tripArea):
  tripsInWindow = []
  
  if tripArea != Cui.CuiNoArea:
    # get list of tuples (uuid, udor) for all trips
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, tripArea, "window")
    tripsInWindow, = R.eval("default_context", R.foreach('iterators.trip_set', 'trip.%udor%', 'trip.%uuid%'))

    # Remove the ix
    tripsInWindow = [(udor, str(uuid)) for _, udor, uuid in tripsInWindow]

  return tripsInWindow


def getLegsInWindow(legArea):
  legsInWindow = []
  flightsInWindow = []
  groundDutiesInWindow = []
  
  if legArea != Cui.CuiNoArea:
    # get list of leg ids (udor) for all legs
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, legArea, "window")
    legsInWindow, = R.eval("default_context", R.foreach('iterators.leg_set',
                                                        'ground_duty',
                                                        'flight_carrier',
                                                        'flight_number',
                                                        'flight_suffix',
                                                        'activity_scheduled_start_time',
                                                        'departure_airport_name',
                                                        'ground_uuid',
                                                        'departure_orig'))

    # Separate the flights from the ground duties
    for leg in legsInWindow:
      if leg[1] == False:
        flightsInWindow.append(leg)
      else:
        groundDutiesInWindow.append(leg)

    # Remove the ix and create fd
    flightsInWindow = [(Common.createFd(car, num, suf), int(sobt), adep) for _, _, car, num, suf, sobt, adep, _, _ in flightsInWindow]
    groundDutiesInWindow = [(uuid, int(st)) for _, _, _, _, _, _, _, uuid, st in groundDutiesInWindow]

  return flightsInWindow, groundDutiesInWindow


def removeData(crewList, tripList, flightList, groundDutiesList):
  """
  Removes all the non-selected crew, trips and flights from the database
  """


def exportDb():
  """
  Exports the database into a file
  """

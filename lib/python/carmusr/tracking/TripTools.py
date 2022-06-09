#

#
# Name:    TripTools
#
# Purpose: To be able to maintain crew composition on trips.
#
#          TripClean: Lowers crew composition on overbooked trips.
#          MergeAndSlice: Combines all possible trips,
#                         then splits them on main category.
#
# Author:  Stefan Lennartsson
# Date:    2008-08-18
#

import Cui
import Select

import utils.time_util as time_util
import carmensystems.rave.api as R
import carmensystems.studio.plans.Common

from AbsTime import AbsTime
from utils.rave import RaveIterator

from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator

def tripClean(area, marked_legs):
    """
    Check all trips involved with list of legs to remove any overbooked trips.
    """

    workArea = Cui.CuiScriptBuffer

    # Storing current context
    currentContext = CuiContextLocator().fetchcurrent()

    # Fixed tuple for positions to gain performance.
    positions = ("1","2","3","4","5","6","7","8","9","10")

    # Use leg level when evaluating rave.
    context = R.selected("levels.leg")

    # Dictionary to keep all unique trips. Should be changed to set()
    unique_open_time_trips = {}

    # Setup iterators for each leg to find all equal legs included in trips which are overbooked.
    fi = RaveIterator(RaveIterator.iter('iterators.leg_set'))
    ei = RaveIterator(RaveIterator.iter('equal_legs'))
    ti = RaveIterator(RaveIterator.iter('iterators.trip_set',
                                        where='fundamental.%is_trip% and crew_pos.%overbooked_trip%',
                                        sort_by='crr_identifier'),
                      {'crr_identifier': 'crr_identifier',
                       'trip_length': 'trip.%time%/0:01',
                       },
                      )

    fi.link(ei)
    ei.link(ti)

    # For each leg we need to find any involved trips that can possibly have been changed.
    for leg in marked_legs:
        # Set focus on the leg to use for the rave lookup.
        CuiContextLocator(area, "OBJECT", Cui.LegMode, str(leg)).reinstate()

        # Evaluate rave data
        legData = fi.eval(context)

        # Store all trip identifiers and the length of the trip.
        for legPiece in legData:
            for equalLegPiece in legPiece.chain():
                for tripPiece in equalLegPiece.chain():
                    unique_open_time_trips[tripPiece.crr_identifier] = tripPiece.trip_length

    # Make a list of all trips, placing length of the trip first makes sorting easy.
    trips = []
    for trip_id,tripLength in unique_open_time_trips.iteritems():
        trips.append([tripLength,trip_id])

    if trips:
        # Sort trips on their length, longest trip first.
        # This can reduce the amount of situations where wrong trip gets reduced.
        trips.sort(reverse=True)

        # Use trip level when evaluating rave.
        context = R.selected("levels.trip")

        # Setup trip iterator to find trip properties.
        ti = RaveIterator(RaveIterator.iter('iterators.trip_set',
                                            where='fundamental.%is_trip%',
                                            sort_by='crr_identifier'),
                          {'a_pos1': 'crew_pos.%trip_assigned_pos%(1)',
                           'a_pos2': 'crew_pos.%trip_assigned_pos%(2)',
                           'a_pos3': 'crew_pos.%trip_assigned_pos%(3)',
                           'a_pos4': 'crew_pos.%trip_assigned_pos%(4)',
                           'a_pos5': 'crew_pos.%trip_assigned_pos%(5)',
                           'a_pos6': 'crew_pos.%trip_assigned_pos%(6)',
                           'a_pos7': 'crew_pos.%trip_assigned_pos%(7)',
                           'a_pos8': 'crew_pos.%trip_assigned_pos%(8)',
                           'a_pos9': 'crew_pos.%trip_assigned_pos%(9)',
                           'a_pos10': 'crew_pos.%trip_assigned_pos%(10)',
                           'overbooked_pos1': 'crew_pos.%overbooked_pos1%',
                           'overbooked_pos2': 'crew_pos.%overbooked_pos2%',
                           'overbooked_pos3': 'crew_pos.%overbooked_pos3%',
                           'overbooked_pos4': 'crew_pos.%overbooked_pos4%',
                           'overbooked_pos5': 'crew_pos.%overbooked_pos5%',
                           'overbooked_pos6': 'crew_pos.%overbooked_pos6%',
                           'overbooked_pos7': 'crew_pos.%overbooked_pos7%',
                           'overbooked_pos8': 'crew_pos.%overbooked_pos8%',
                           'overbooked_pos9': 'crew_pos.%overbooked_pos9%',
                           'overbooked_pos10': 'crew_pos.%overbooked_pos10%',
                           },
                          )

        # Reduction will take place on each trip, one at a time.
        # This way any interfering trips with overbooked need won't conflict.
        for trip in trips:
            crr_identifier = str(trip[1])

            # Find the trip and put it in the scriptbuffer.
            Cui.CuiDisplayGivenObjects(Cui.gpc_info,
                                       workArea,
                                       Cui.CrrMode,
                                       Cui.CrrMode,
                                       [crr_identifier],
                                       0)

            # Set focus for rave lookup on the trip.
            CuiContextLocator(workArea, "OBJECT", Cui.CrrMode, crr_identifier).reinstate()

            # Evaluate rave data for the trip.
            theTrip = ti.eval(context)[0]

            # Crew complement vector.
            cc = []

            # For each position, calculate a new assignvalue based on what's possible to reduce.
            for pos in positions:
                newAssignValue = max(getattr(theTrip, 'a_pos'+pos) - getattr(theTrip,'overbooked_pos'+pos),0)
                cc.append(str(newAssignValue))

            # Set focus on trip for properties form to work.
            Cui.CuiSetSelectionObject(Cui.gpc_info, workArea, Cui.CrrMode, crr_identifier)
    
            # Check if there will be any assign value to the trip left.
            if len([c for c in cc if c not in ['','0']]):
                # Bypass properties form to set new crew complement vector on trip.
                Cui.CuiCrrProperties({'FORM':'CRR_FORM','CRR_STD_CREW_COMP':"/".join(cc)},
                                     {'FORM':'CRR_FORM','OK':''},
                                     Cui.gpc_info, workArea, "OBJECT")
            else:
                # Crew complement empty after reduction. Dissolve the trip-chain.
                Cui.CuiRemoveCrr(Cui.gpc_info, workArea, 3, 0)
    
        # Trips will remain after removal unless the trip area is refreshed.
        carmensystems.studio.plans.Common.refreshTripAreas()

    # Resetting current context to the one that already was.
    # Not necessary but could be useful to think about when dealing with contexts.
    currentContext.reinstate()

def mergeAndSlice():
    """
    Merge all trips in currentArea.
    Then slice all trips into main categories.
    """

    # Use CuiWhichArea since slice do not seem to accept any area.
    Cui.CuiMergeIdenticalCrrs(Cui.gpc_info, Cui.CuiWhichArea, "Window", 0)

    # Why do this one not accept any area? Will it always work on CuiWhichArea?
    Cui.CuiSliceIntoMainCategories(Cui.gpc_info, "CRR", "Window")

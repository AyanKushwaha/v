
#
#######################################################
#
#   CrewMeal.py
#
# -----------------------------------------------------
#
# Created:      2009-06-16
# By:           Thomas Rudolfsson
#
# ------------------------------------------------------
#
# Description:
#
# This module contains code to store crew meal attributes.
# Reason to store attributes is to prevent historic values
# to change.
#
# Meal stop: Meal stops are indicated by the attibute
# "MEAL_BREAK", and a string value "X". There are also
# string values "X+" for manual set meal stop, and "X-"
# for manual prevent of meal stop.
#
# Meal stop attributes are stored at roster publish, and
# on each save for modified crew. Historic meal stop should
# never be changed, only future meal stops. This distintion
# is implemented in the rave value meal.%is_assigned_meal_stop%
# which indicate if there is a meal stop after the leb or not.
# Historic data is read from attributes, future are calculated.
# Manual set and prevent are respected.
#
# When storing meal attributes, there is a rave value
# meal.%meal_attr_changed% indicating if this flight has
# a change or not. Only those are updated. Change are
# detected using the algorithm:
#
# export %meal_attr_changed% =
#   if %is_assigned_meal_stop% then
#     not %is_meal_break_attr%
#   else
#     %is_meal_break_attr% and
#     not %is_manual_prevent%;
#
# As %meal_attr_changed% uses stored values for historic values,
# history will not be affected, just have to make sure no manual
# prevents are removed.



import Cui
import carmensystems.rave.api as R
import carmusr.modcrew as modcrew
import modelserver as M
import carmusr.Attributes as Attributes
from utils.rave import RaveIterator
from utils.rave import RaveEvaluator
import time

# ****************** Timer functionality **********************
__times = []
__t = None

def timer(txt=None):
    global __t
    global __times
    if not txt is None:
        __times.append("%s: %.2f s" %(txt, time.time() - __t))
    __t = time.time()

def printTimes(txt=""):
    global __t
    global __times
    time_txts = reduce(lambda a, b: "%s\n    %s" %(a,b), __times)
    print "**************************************************"
    print "%s:\n     %s" % (txt, time_txts)
    print "**************************************************"
    __times = []
    __t = time.time()
# *************************************************************

def update_meals():
    """
    Function to save meal break information on modified crew at save time.
    Called from FileHandlingExt.savePlanPostProc. To keep up performance, only
    modified crew are updated. These are stored in modcrew by earlier stages of save.
    """
    Cui.CuiDisplayGivenObjects(Cui.gpc_info,
                               Cui.CuiScriptBuffer,
                               Cui.CrewMode,
                               Cui.CrewMode,
                               modcrew.get())
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, "window")
    set_attributes_on_crew()
    
def roster_release_publish_meals(area):
    """
    Function called from carmusr.rostering.Publish.py. Used during
    roster publish to store all calculated meal stops. For planning,
    meal.%is_assigned_meal_stop% only considers calculated values.
    """
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "window")
    set_attributes_on_crew()
    Attributes._refresh(["crew_flight_duty_attr", "crew_ground_duty_attr", "crew_activity_attr"])
      
def set_attributes_on_crew():
    """
    Sets meal attributes on all crew in script buffer.
    Only changed attributes are stored.
    """

    str_attr_name = "MEAL_BREAK"
    str_automatic = "X"
    # Get needed values to update the assignment attribute tables.
    # Should be same as in carmusr.Attributes
    legs = RaveIterator(R.iter('iterators.leg_set', where = "meal.%meal_attr_changed% and leg.%starts_in_pp% and not meal.%leg_is_past_operation%"), {
                'crew':              'crew.%id%',
                'id':                'activity_id',
                'ground_activity':   'ground_activity',
                'flight_duty':       'flight_duty',
                'ground_transport':  'ground_transport',
                'udor':              'leg.%udor%',
                'fd':                'leg.%flight_descriptor%',
                'adep':              'leg.%start_station%',
                'uuid':              'leg.%uuid%',
                'st':                'leg.%activity_scheduled_start_time_utc%',
                'code':              'leg.%code%',
                'is_meal_stop':      'meal.%is_assigned_meal_stop%',
                'is_manual_set':     'meal.%is_manual_set%',
                'is_manual_prevent': 'meal.%is_manual_prevent%',
                }).eval('default_context')
    for leg in legs:
        # print leg.id
        if leg.is_meal_stop:
            if leg.flight_duty and not leg.ground_transport:
                Attributes.SetCrewFlightDutyAttr(leg.crew, leg.udor, leg.fd, leg.adep, str_attr_name, False, str=str_automatic)
            elif leg.ground_activity:
                Attributes.SetCrewGroundDutyAttr(leg.crew, leg.udor, leg.uuid, str_attr_name, False, str=str_automatic)
            else:
                Attributes.SetCrewActivityAttr(leg.crew, leg.st, leg.code, str_attr_name, False, str=str_automatic)
        else:
            if leg.flight_duty and not leg.ground_transport:
                Attributes.RemoveCrewFlightDutyAttr(leg.crew, leg.udor, leg.fd, leg.adep, str_attr_name, False)
            elif leg.ground_activity:
                Attributes.RemoveCrewGroundDutyAttr(leg.crew, leg.udor, leg.uuid, str_attr_name, False)
            else:
                Attributes.RemoveCrewActivityAttr(leg.crew, leg.st, leg.code, str_attr_name, False)
           
def meal_stop_force_stop():
    """
    Called from menu scripts to set forced meal stop attribute on marked legs
    """
    marked_legs = Cui.CuiGetLegs(Cui.gpc_info, Cui.CuiWhichArea, "marked")
    for leg in marked_legs:
        Cui.CuiSetSelectionObject(Cui.gpc_info, Cui.CuiWhichArea, Cui.LegMode, str(leg))
        crew = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object", "crew.%id%")
        Attributes.SetAssignmentAttrCurrent('MEAL_BREAK', str='X+', refresh=False)
        modcrew.add(crew)
    Attributes._refresh(["crew_flight_duty_attr", "crew_ground_duty_attr", "crew_activity_attr"])

def meal_stop_force_no_stop():
    """
    Called from menu scripts to set forced no meal stop attribute on marked legs
    """
    marked_legs = Cui.CuiGetLegs(Cui.gpc_info, Cui.CuiWhichArea, "marked")
    for leg in marked_legs:
        Cui.CuiSetSelectionObject(Cui.gpc_info, Cui.CuiWhichArea, Cui.LegMode, str(leg))
        crew = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object", "crew.%id%")
        Attributes.SetAssignmentAttrCurrent('MEAL_BREAK', str='X-', refresh=False)
        modcrew.add(crew)
    Attributes._refresh(["crew_flight_duty_attr", "crew_ground_duty_attr", "crew_activity_attr"])

def meal_stop_automatic():
    """
    Called from menu scripts to remove meal stop attribute on marked legs, thus
    reverting to calculated values
    """
    marked_legs = Cui.CuiGetLegs(Cui.gpc_info, Cui.CuiWhichArea, "marked")
    for leg in marked_legs:
        Cui.CuiSetSelectionObject(Cui.gpc_info, Cui.CuiWhichArea, Cui.LegMode, str(leg))
        crew = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object", "crew.%id%")
        Attributes.RemoveAssignmentAttrCurrent('MEAL_BREAK', refresh=False)
        modcrew.add(crew)
    Attributes._refresh(["crew_flight_duty_attr", "crew_ground_duty_attr", "crew_activity_attr"])

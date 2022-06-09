#

#
__version__ = "$Revision$"
"""
Attribute
Module for doing:
See below
@date:07Oct2008
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""



"""
 Functionality to set and remove attributes on crew,
 leg, or an assignment (crew leg connection).  

------------------------------------------------------
Created:    May 2006
By:         Thomas Rudolfsson

Attributes can exist on three different levels, on leg,
on assignment and on crew. These correspos to attributes
on the following UDM tables:
Leg:
  flight_leg attributes in table flight_leg_attr
  ground_task attributes in table ground_task_attr
Assignment:
  crew_flight_leg attributes in table crew_flight_leg_attr
  crew_ground_task attributes in table crew_ground_task_attr
  crew_activity attributes in table crew_activity_attr
Crew:
  crew attributes in table crew_attr

For each level of attributes, there is a lookup table with
the attributes of that level. These are in tables:
  Leg:        leg_attr_set
  Assignment: assignment_attr_set
  Crew:       crew_attr_set
You can not create an attribute on a level unless it
is in the lookup table for the level.

Attributes in the lookup tables are grouped into
categories using the table attr_category_set.
This is used to group attributes, like training
attributes etc.

There are two general ways of setting attributes in
the API. Either you supply the key values of the object you
want to set the attribute on, or you set the current
selection object prior to the API call. In the latter case,
the API will figure out the proper key using Cui functionality.
The first one is intended to be used from within python scripts,
while the second one is intended to be called directly from
menu files, where the current selection object is already set.

There are three different kinds of attributes, leg attributes,
assignment attributes and crew attributes. There are different
functions to set each kind of attribute.

For flight_leg the key values are:
  udor = Flight departure date UTC
  fd   = Flight designator
  adep = Departure airport name
For ground_task:
  udor = Flight departure date UTC
  uuid = The UUID of the ground duty leg
For activities (assignment attribute only)
  st   = Start time of the activity UTC
  activity = Ground duty code of the avtivity

You can also set values on attributes. There are four
values on each attribute, AbsTime, RelTime, String and
Integer. You supply the values as named arguments to the
set function.

Named arguments:
  abs = AbsTime value of the attribute
  rel = RelTime value of the attribute
  int = Integer value of the attribute
  str = String value of the attribute
  si  = Comment

If an attribute already exist in the model, the values
are simply added, that is, the values specified are added
to the model. Already existing values with no new value
are left unchanged.

There is one corresponding remove function for each set function
If the attribute can not be found, the function returns False,
otherwise True.

The functions also have a refresh parameter, if the API should
automatically sync models when changing. When scripting several
changes, this should be false for performance reasons, and the
users of the API will have to sync the models them self.
"""

import Cui
import Gui
from AbsTime import AbsTime
from RelTime import RelTime
import tm
#import Util

class AttrNotFoundError(Exception):
    def __init__(self):
       Exception.__init__(self,"Attribute not found") 
       
class CrewAttrNotFoundError(AttrNotFoundError):
    def __init__(self, crewid, attr):
        _text = 'CrewAttr: Crewid %s has no attribute %s'%(crewid,attr)
        Exception.__init__(self,_text)

##############################################################################
# SET FUNCTIONS
##############################################################################

def SetFlightLegAttr(udor, fd, adep, attr, refresh=True, **values):
    """Set attribute on a flight_leg"""
    key = _flight_leg_key(udor, fd, adep)
    _attr = _get_create_attr("flight_leg_attr", "leg_attr_set", key, attr)
    _set_values(_attr, values)
    if refresh: _refresh("flight_leg_attr")
    
def SetGroundTaskAttr(udor, uuid, attr, refresh=True, **values):
    """Set attribute on a ground_task"""
    key = _ground_task_key(udor, uuid)
    _attr = _get_create_attr("ground_task_attr", "leg_attr_set", key, attr)
    _set_values(_attr, values)
    if refresh: _refresh("ground_task_attr")
    
def SetCrewFlightDutyAttr(crew, udor, fd, adep, attr, refresh=True, **values):
    """Set attribute on a crew_flight_duty"""
    key = _crew_flight_duty_key(crew, udor, fd, adep)
    _attr = _get_create_attr("crew_flight_duty_attr", "assignment_attr_set",
                             key, attr)
    _set_values(_attr, values)
    if refresh: _refresh("crew_flight_duty_attr")
        
def SetCrewGroundDutyAttr(crew, udor, uuid, attr, refresh=True, **values):
    """Set attribute on a crew_ground_duty"""
    key = _crew_ground_duty_key(crew, udor, uuid)
    _attr = _get_create_attr("crew_ground_duty_attr", "assignment_attr_set",
                             key, attr)
    _set_values(_attr, values)
    if refresh: _refresh("crew_ground_duty_attr")

def SetCrewActivityAttr(crew, st, activity, attr, refresh=True, **values):
    """Set attribute on a crew_activity"""
    key = _crew_activity_key(crew, st, activity)
    _attr = _get_create_attr("crew_activity_attr", "assignment_attr_set",
                             key, attr)
    _set_values(_attr, values)
    if refresh: _refresh("crew_activity_attr")
    
def SetCrewAttr(crew, attr, st="01JAN1986", refresh=True, **values):
    """Set attribute on a crew"""
    key = _crew_key(crew)
    _attr = _get_create_attr("crew_attr", "crew_attr_set", key, attr, st)
    _set_values(_attr, values)
    if refresh: _refresh("crew_attr")

def SetLegAttrCurrent(attr, refresh=True, **values):
    """Set a flight_leg or ground_task attribute on the current selection object
    """
    tab = _get_leg_table_current()
    if tab == "flight_leg":
        udor = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                     "leg.%udor%")
        fd = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                  "leg.%flight_descriptor%")
        adep = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                    "leg.%start_station%")
        SetFlightLegAttr(udor, fd, adep, attr, refresh, **values)
    elif tab == "ground_task":
        udor = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiWhichArea,"object",
                                     "leg.%udor%")
        uuid = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                    "leg.%uuid%")
        SetGroundTaskAttr(udor, uuid, attr, refresh, **values)
    else:
        return 1
        
    return 0
 
def SetAssignmentAttrCurrent(attr, refresh=True, **values):
    """Set a crew_flight_leg, crew_ground_task or crew_activity attribute on
    the current selection object"""
    crew = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                "crew.%id%")
    if not crew:
        return 1
    
    tab = _get_assignment_table_current()
    if tab == "crew_flight_duty":
        udor = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                     "leg.%udor%")
        fd = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                  "leg.%flight_descriptor%")
        adep = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                    "leg.%start_station%")
        SetCrewFlightDutyAttr(crew, udor, fd, adep, attr, refresh, **values)
    elif tab == "crew_ground_duty":
        udor = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiWhichArea,"object",
                                     "leg.%udor%")
        uuid = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                    "leg.%uuid%")
        SetCrewGroundDutyAttr(crew, udor, uuid, attr, refresh, **values)
    elif tab == "crew_activity":
        st = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                   "leg.%activity_scheduled_start_time_utc%")
        code = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                    "leg.%code%")
        SetCrewActivityAttr(crew, st, code, attr, refresh, **values)
    else:
        return 1
        
    return 0

def SetAssignmentAttrAll(attr, refresh=True, **values):
    marked_legs = Cui.CuiGetLegs(Cui.gpc_info, Cui.CuiWhichArea)
    for leg in marked_legs:
        setSelectionObject(Cui.CuiWhichArea, Cui.LegMode, leg)
        SetAssignmentAttrCurrent(attr, refresh=False, **values)
    _refresh(["crew_flight_duty_attr","crew_activity_attr",
              "crew_ground_duty_attr"])
  
def SetCrewAttrCurrent(attr, refresh=True, **values):
    """Set a crew attribute on the current selection object"""
    crew = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                "crew.%id%")
    st = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiWhichArea, "object",
                               "default(leg.%activity_scheduled_start_time_utc%, 01JAN1986)")
    if not crew:
        return 1
    SetCrewAttr(crew, attr, st, refresh, **values)
    
#############################################################################
# Get functions
##############################################################################

def GetCrewAttr(crew, attr, st="01JAN1986"):
    key = _crew_key(crew)
    attribute_entity = _get_attr("crew_attr", "crew_attr_set", key, attr, st)
    if attribute_entity:
        return _get_values(attribute_entity)
    else:
        raise CrewAttrNotFoundError(crew,attr)
    
def GetCrewFlightDutyAttr(crew, udor, fd, adep, attr):
    key = _crew_flight_duty_key(crew, udor, fd, adep)
    attribute_entity = _get_attr("crew_flight_duty_attr",
                                 "assignment_attr_set", key, attr)
    if attribute_entity:
        return _get_values(attribute_entity)
    else:
        raise CrewAttrNotFoundError(crew,attr)
 
def GetCrewGoundDutyAttr(crew, udor, uuid, attr):
    key = _crew_ground_duty_key(crew, udor, uuid)
    attribute_entity = _get_attr("crew_ground_duty_attr",
                                 "assignment_attr_set", key, attr)
    if attribute_entity:
        return _get_values(attribute_entity)
    else:
        raise CrewAttrNotFoundError(crew,attr)
 
def GetCrewActivityAttr(crew, st, activity, attr):
    key = _crew_activity_key(crew, st, activity)
    attribute_entity = _get_attr("crew_activity_attr",
                                 "assignment_attr_set", key, attr)
    if attribute_entity:
        return _get_values(attribute_entity)
    else:
        raise CrewAttrNotFoundError(crew,attr)
    
##############################################################################
# REMOVE FUNCTIONS
##############################################################################

def RemoveFlightLegAttr(udor, fd, adep, attr, refresh=True):
    """Remove attribute on a flight_leg"""
    key = _flight_leg_key(udor, fd, adep)
    return _remove_attr("flight_leg_attr", "leg_attr_set", key, attr, refresh)

def RemoveGroundTaskAttr(udor, uuid, attr, refresh=True):
    """Remove attribute on a ground_task"""
    key = _ground_task_key(udor, uuid)
    return _remove_attr("ground_task_attr", "leg_attr_set", key, attr, refresh)
       
def RemoveCrewFlightDutyAttr(crew, udor, fd, adep, attr, refresh=True):
    """Remove attribute on a crew_flight_duty"""
    key = _crew_flight_duty_key(crew, udor, fd, adep)
    return _remove_attr("crew_flight_duty_attr", "assignment_attr_set",
                        key, attr, refresh)
    
def RemoveCrewGroundDutyAttr(crew, udor, uuid, attr, refresh=True):
    """Remove attribute on a crew_ground_duty"""
    key = _crew_ground_duty_key(crew, udor, uuid)
    return _remove_attr("crew_ground_duty_attr", "assignment_attr_set",
                        key, attr, refresh)

def RemoveCrewActivityAttr(crew, st, activity, attr, refresh=True):
    """Remove attribute on a crew_activity"""
    key = _crew_activity_key(crew, st, activity)
    return _remove_attr("crew_activity_attr", "assignment_attr_set",
                        key, attr, refresh)

def RemoveCrewAttr(crew, attr, st="01JAN1986", refresh=True):
    """Remove attribute on a crew"""
    key = _crew_key(crew)
    return _remove_attr("crew_attr", "crew_attr_set",
                        key, attr, st, refresh)

    
def RemoveLegAttrCurrent(attr, refresh=True):
    """Remove a flight_leg or ground_task attribute on the current selection
    object"""
    tab = _get_leg_table_current()
    if tab == "flight_leg":
        udor = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                     "leg.%udor%")
        fd = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                  "leg.%flight_descriptor%")
        adep = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                    "leg.%start_station%")
        return RemoveFlightLegAttr(udor, fd, adep, attr, refresh)
    elif tab == "ground_task":
        udor = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiWhichArea,"object",
                                     "leg.%udor%")
        uuid = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                    "leg.%uuid%")
        return RemoveGroundTaskAttr(udor, uuid, attr, refresh)
    else:
        return 1
      
def RemoveAssignmentAttrCurrent(attr, refresh=True):
    """Remove a crew_flight_leg or crew_ground_task or crew_activity attribute
    on the current selection object"""
    crew = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                "crew.%id%")
    if not crew:
        return 1
    
    tab = _get_assignment_table_current()
    if tab == "crew_flight_duty":
        udor = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                     "leg.%udor%")
        fd = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                  "leg.%flight_descriptor%")
        adep = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                    "leg.%start_station%")
        return RemoveCrewFlightDutyAttr(crew, udor, fd, adep, attr, refresh)    
    elif tab == "crew_ground_duty":
        udor = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiWhichArea,"object",
                                     "leg.%udor%")
        uuid = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                    "leg.%uuid%")
        return RemoveCrewGroundDutyAttr(crew, udor, uuid, attr, refresh)
    elif tab == "crew_activity":
        st = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                   "leg.%start_utc%")
        code = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                    "leg.%code%")
        return RemoveCrewActivityAttr(crew, st, code, attr, refresh)
    else:
        return 1

def RemoveAllAssignmentAttrAll(category, refresh=True,):
    """Remove all crew_flight_leg, crew_ground_task or crew_activity attribute
    in specified category on all selected objects"""
    
    marked_legs = Cui.CuiGetLegs(Cui.gpc_info, Cui.CuiWhichArea)
    assignment_attr_set = tm.TM.table("assignment_attr_set")
    for leg in marked_legs:
        for attr in assignment_attr_set.search("(category.id=%s)" % category):
            # we need to set the selection object each time because of refresh
            setSelectionObject(Cui.CuiWhichArea, Cui.LegMode, leg)
            RemoveAssignmentAttrCurrent(attr.id)
    if refresh: _refresh("assignment_attr_set")
    return 0

def RemoveAssignmentAttrAll(attr, refresh=True):
    marked_legs = Cui.CuiGetLegs(Cui.gpc_info, Cui.CuiWhichArea)
    for leg in marked_legs:
        setSelectionObject(Cui.CuiWhichArea, Cui.LegMode, leg)
        RemoveAssignmentAttrCurrent(attr, refresh=False)
    _refresh(["crew_flight_duty_attr","crew_activity_attr",
              "crew_ground_duty_attr"])

def RemoveCrewAttrCurrent(attr, refresh=True):
    """Remove a crew attribute on the current selection object"""
    crew = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",
                                "crew.%id%")
    st = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiWhichArea, "object",
                               "default(leg.%start_utc%, 01JAN1986)")
    if not crew:
        return 1
    return RemoveCrewAttr(crew, attr, st, refresh)

##############################################################################
# INTERNAL METHODS
##############################################################################

def _rave_bool_current(name):
    return Cui.CuiCrcEvalBool(Cui.gpc_info, Cui.CuiWhichArea, "object", name)
    
def _get_leg_table_current():
    """Returns "flight_leg" or "ground_task".
    Indicates in which db table the current studio selection object is stored.
    Note that 'None' is returned for personal activities and ground transports.
    """
    if _rave_bool_current("ground_activity"):
        return "ground_task"
    if _rave_bool_current("flight_duty"):
        if not _rave_bool_current("ground_transport"):
            return "flight_leg"
    return None
    
def _get_assignment_table_current():
    """Returns "crew_flight_duty", "crew_ground_duty" or "crew_activity".
    Indicates in which db table the current studio selection object is stored.
    Note that ground transports are a special case of "crew_activity".
    """
    if _rave_bool_current("ground_activity"):
        return "crew_ground_duty"
    if _rave_bool_current("flight_duty"):
        if _rave_bool_current("ground_transport"):
            return "crew_activity"
        return "crew_flight_duty"
    return "crew_activity"

def _flight_leg_key(udor, fd, adep):
    t_airport = tm.TM.table("airport")
    airport = t_airport.getOrCreateRef((adep,))
    t_leg = tm.TM.table("flight_leg")
    return t_leg.getOrCreateRef((_to_abs(udor), fd, airport))

def _ground_task_key(udor, uuid):
    t_leg = tm.TM.table("ground_task")
    return t_leg.getOrCreateRef((_to_abs(udor), uuid))
    
def _crew_flight_duty_key(crew, udor, fd, adep):
    leg = _flight_leg_key(udor, fd, adep)
    t_crew = tm.TM.table("crew")
    crew = t_crew.getOrCreateRef((crew,))
    t_crew_flight_duty = tm.TM.table("crew_flight_duty")
    return t_crew_flight_duty.getOrCreateRef((leg, crew))
    
def _crew_ground_duty_key(crew, udor, uuid):
    task = _ground_task_key(udor, uuid)
    t_crew = tm.TM.table("crew")
    crew = t_crew.getOrCreateRef((crew,))
    t_crew_ground_duty = tm.TM.table("crew_ground_duty")
    return t_crew_ground_duty.getOrCreateRef((task, crew))
    
def _crew_activity_key(crew, st, activity):
    t_crew = tm.TM.table("crew")
    _crew = t_crew.getOrCreateRef((crew,))
    t_as = tm.TM.table("activity_set")
    _as = t_as.getOrCreateRef((activity,))
    t_crew_activity = tm.TM.table("crew_activity")
    return t_crew_activity.getOrCreateRef((_to_abs(st), _crew, _as))
    
def _crew_key(crew):
    t_crew = tm.TM.table("crew")
    return t_crew.getOrCreateRef((crew,))

def _get_create_attr(attr_table_name, set_table_name, key, attr, st="01JAN1986"):
    tm.TM.loadTables([set_table_name, attr_table_name])
    t_set = tm.TM.table(set_table_name)
    set = t_set[attr]
    t_attr = tm.TM.table(attr_table_name)
    try:
        if attr_table_name == "crew_attr":
            _attr = t_attr[(key, _to_abs(st), set)]
            # Add abstime if crew_attr  ( _to_abs(st) )
        else:
            _attr = t_attr[(key, set)]
    except:
        if attr_table_name == "crew_attr":
            _attr = t_attr.create((key, _to_abs(st), set))
            # Add abstime if crew_attr
        else:
            _attr = t_attr.create((key, set))
    return _attr

def _get_attr(attr_table_name, set_table_name, key, attr, st="01JAN1986"):
    tm.TM.loadTables([set_table_name, attr_table_name])
    t_set = tm.TM.table(set_table_name)
    set = t_set[attr]
    t_attr = tm.TM.table(attr_table_name)
    try:
        if attr_table_name == "crew_attr":
            _attr = t_attr[(key, _to_abs(st), set)]
            # Add abstime if crew_attr  ( _to_abs(st) )
        else:
            _attr = t_attr[(key, set)]
    except Exception, err:
        print str(err)
        return None
    return _attr

def _remove_attr(attr_table_name, set_table_name, key, attr, refresh=False):
    tm.TM.loadTables([set_table_name, attr_table_name])
    t_set = tm.TM.table(set_table_name)
    set = t_set[attr]
    t_attr = tm.TM.table(attr_table_name)
    try:
        _attr = t_attr[(key, set)]
        # Add abstime if crew_attr
    except:
        return 1
    _attr.remove()
    if refresh:
        _refresh(attr_table_name)
    return 0
    
def _set_values(attr, values):
    if "rel" in values:
        if values["rel"] is None:
            attr.value_rel = None
        else:
            attr.value_rel = _to_rel(values["rel"])
    if "abs" in values:
        if values["abs"] is None:
            attr.value_abs = None
        else:
            attr.value_abs = _to_abs(values["abs"])
    if "int" in values:
        if values["int"] is None:
            attr.value_int = None
        else:
            attr.value_int = int(values["int"])
    if "str" in values:
        if values["str"] is None:
            attr.value_str = None
        else:
            attr.value_str = str(values["str"])
    if "si" in values:
        if values["si"] is None:
            attr.si = None
        else:
            attr.si = str(values["si"])

def _get_values(attr):
    values = {'rel':attr.value_rel,
              'int':attr.value_int,
              'str':attr.value_str,
              'abs':attr.value_abs,
              'si':attr.si}
    return values
    
def _to_abs(value):
    if type(value) == AbsTime:
        return value
    else:
        return AbsTime(value)

def _to_rel(value):
    if type(value) == RelTime:
        return value
    else:
        return RelTime(value)
    
def _refresh(table):
    print "Refresh %s" % table
    if type(table) == str:
        table = [table,]
    for t in table:
        Cui.CuiReloadTable(t, Cui.CUI_RELOAD_TABLE_SILENT)
    Gui.GuiCallListener(Gui.RefreshListener, "parametersChanged")
    Gui.GuiCallListener(Gui.ActionListener)

# This function belongs elsewhere, but for now it will need to be here.
def setSelectionObject(area, mode, key, showIfNecessary=False):
    """
    Wrapper for Cui.CuiSetSelectionObject.
    Sets current area and default context, so Rave API evaluations will work. 
    """
    
    Cui.CuiSetCurrentArea(Cui.gpc_info, area)
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, 'OBJECT')
    try:
        Cui.CuiSetSelectionObject(Cui.gpc_info, area, mode, str(key))
    except:
        if showIfNecessary:
            Cui.CuiDisplayObjects(Cui.gpc_info, area, mode, Cui.CuiShowAll)
            Cui.CuiSetSelectionObject(Cui.gpc_info, area, mode, str(key))
        else:
            raise

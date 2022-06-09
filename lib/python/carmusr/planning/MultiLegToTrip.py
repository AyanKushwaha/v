#

#
__version__ = "$Revision$"
"""
MultiLegToTrip
Module for doing:
Creating trips from Multilegs 
@date:30Sep2008
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""
import Cui
import Gui
import Crs
import MenuCommandsExt
import Variable
import time
import Errlog

def create_trips(area=Cui.CuiWhichArea):
    work_area = Cui.CuiAreaIdConvert(Cui.gpc_info, area)
    
    # Store original trips so we can find newly created
    old_trip_ids = _get_current_trip_ids(work_area)
    
    # Create new
    _create_trips_from_multilegs(work_area)
    
    # Get newly created trips
    new_trip_ids = _get_diff_trip_ids(_get_current_trip_ids(work_area),old_trip_ids)

    # Split into separate trips is some where created
    if new_trip_ids:
        mod = SuppressDialogModifier()
        _process_trips_after_create(work_area, new_trip_ids)
        # Get newly created trips after split
        new_trip_ids = _get_diff_trip_ids(_get_current_trip_ids(work_area), old_trip_ids)

    # Current assign vector in studio
    assign_vector = Variable.Variable("")
    Cui.CuiGetSubPlanAssignValue(Cui.gpc_info,assign_vector)
    
    Gui.GuiMessage('Created %s trips with crew complement %s'%\
                   (len(new_trip_ids),assign_vector.value))
    
    Cui.CuiDisplayGivenObjects(Cui.gpc_info, work_area,
                               Cui.CrrMode,Cui.CrrMode, new_trip_ids)
    
def _get_current_trip_ids(area):
    Cui.CuiDisplayObjects(Cui.gpc_info, area, Cui.CrrMode, Cui.CuiShowAll)
    return _get_ids_for_area(area)

def _get_ids_for_area(area):
    return [str(id) for id in Cui.CuiGetTrips(Cui.gpc_info,area,"window")]
    
def _get_diff_trip_ids(new_list, old_list):
    return [str(id) for id in new_list if str(id) not in set(old_list)]

def _create_trips_from_multilegs(area):
    filter_bypass = {'FORM': 'my_form',
                     'FL_TIME_BASE': 'RDOP',
                     'FILTER_PRINCIP': 'ANY',
                     'FILTER_METHOD': 'REPLACE',
                     'FILTER_MARK': 'LEG',
                     'CRC_VARIABLE_0': 'leg.is_multileg_flight',
                     'CRC_VALUE_0': 'T',
                     'CRC_VARIABLE_1': 'leg.in_pp',
                     'CRC_VALUE_1': 'T',
                     'CRC_VARIABLE_2': 'planning_area.leg_is_in_planning_area',
                     'CRC_VALUE_2': 'T',
                     'OK': ''}
    Cui.CuiFilterObjects(filter_bypass, Cui.gpc_info,area,"AcRotFilter","my_form",0,Cui.CUI_SILENT)
    bypass = {
        'FORM': 'CuiCreateCrewChainsFromRotation',
        'INCLUDE_LEG': 'Marked',
        'BREAK_AFTER': 'Not Marked',
        'LOCK': 'No',
        'SET_USER_TAG': 'No',
        'OK': '',
        }
    Cui.CuiCreateCrewChainsFromRotation(bypass,Cui.gpc_info,area,"NOT_USED","Crr",0)
    _unmark_and_sync(area)
    
def _process_trips_after_create(area, new_trip_ids):
    Cui.CuiDisplayGivenObjects(Cui.gpc_info, area,
                               Cui.CrrMode,Cui.CrrMode, new_trip_ids)
    mark_last_leg_bypass = {
        'FORM': 'form_mark_crr_filter',
        'FL_TIME_BASE': 'RDOP',
        'FILTER_MARK': 'LEG',
        'CRC_VARIABLE_0': 'leg.is_last_multileg_inside_trip',
        'CRC_VALUE_0': 'T',
        'OK': ''}
    
    Cui.CuiMarkCrrsWithFilter(mark_last_leg_bypass,
                              Cui.gpc_info, area, 0)
    marked_legs = [str(id) for id in Cui.CuiGetLegs(Cui.gpc_info,
                                                    area,
                                                    "marked")]
    for leg_id in marked_legs:
        Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, leg_id)
        Cui.CuiSplitChain(Cui.gpc_info,area,Cui.CUI_SPLIT_SILENT)
    _unmark_and_sync(area)

def _unmark_and_sync(area):
    Cui.CuiUnmarkAllLegs(Cui.gpc_info,area,"WINDOW")
    Cui.CuiSyncModels(Cui.gpc_info)
    
class SuppressDialogModifier:
    def __init__(self):
        _old_option = Crs.CrsGetModuleResource('dialogues',
                                               Crs.CrsSearchModuleDef,
                                               'suppressChangeHomebaseDialogue')
        if  _old_option is None or _old_option.upper() == 'FALSE':
            Errlog.log('MultiLegToTrip.py:: SuppressDialogModifier:'+\
                       ' Setting suppressChangeHomebaseDialogue to true')
            Crs.CrsSetModuleResource('dialogues',
                                     'suppressChangeHomebaseDialogue',
                                     'true',
                                     'temp. changed by multileg2trip script')
            
    def __del__(self):
        Errlog.log('MultiLegToTrip.py:: SuppressDialogModifier:'+\
                   ' reset suppressChangeHomebaseDialogue to false')
        Crs.CrsSetModuleResource('dialogues',
                                 'suppressChangeHomebaseDialogue',
                                 'false',
                                 'should be false')
        
            

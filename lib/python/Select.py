#

#
# This module contains the select functionality previously located in MenuCommands.py
# It is moved to this file to make is usable for other modules.
#
# By Stefan Hammar, Carmen Systems AB, Sept 2004
#

import os
import Cui
import carmensystems.rave.api as rave
import carmusr.HelperFunctions as HelperFunctions
import Errlog
from tempfile import mkstemp

import carmusr.application as application
import utils.AreaSort as AreaSort

if application.isTracking or application.isDayOfOps:
    SORTER = AreaSort.AreaSorter()
else:
    SORTER = AreaSort.StoreAreaSorter()

###########################
# Select filters
###########################

class SelectionEtable:
    """Creates a temporary Etable (in CARMTMP) with selection criteria."""
    def __init__(self, selection):
        """Create and write to temporary file."""
        fd, self.fn = mkstemp(suffix='.etab', prefix='Sel_',
                dir=os.environ['CARMTMP'], text=True)
        f = os.fdopen(fd, 'w')
        f.write("3\nSAttribute,\nSFieldValue,\nSValue,\n")
        c = 0 # counter
        for key, value in selection.items():
            if len(str(value)) > 1024:
                raise ValueError("Select.py:: Trying to use to long string in select. "+\
                                 "Max rave length is 1024 characters.")
            # Assume internal fields start with 'F'
            if key.startswith('F'):
                f.write('"%s", "", "%s",\n' % (key, value))
            else:
                f.write('"CRC_VALUE_%i", "%s", "%s",\n' % (c, key, value))
                c += 1
        f.close()

    def __str__(self):
        """Return file name of temporary Etable."""
        return self.fn

    def unlink(self):
        """Remove the temporary file."""
        os.unlink(self.fn)

         
def mark(markCriterias, windowArea = Cui.CuiWhichArea, dataMode = None):
    """
    Mark filtered objects
    """
    if dataMode == None:
        for mode in range(Cui.MaxAreaModes):
            try:
                Cui.CuiCheckAreaMode(Cui.gpc_info, windowArea, mode)
            except:
                print "CuiCheckAreaMode threw exception in Select.py"
                continue
            dataMode = mode
            break
    etab = SelectionEtable(markCriterias)
    #Cui.CuiDisplayFilteredObjects(Cui.gpc_info, windowArea, dataMode, str(etab))
    Cui.CuiMarkLegsWithFilter(Cui.gpc_info, windowArea, str(etab))
    etab.unlink()
    HelperFunctions.redrawAreaScrollHome(windowArea)
    

def select(selectionCriterias, windowArea = Cui.CuiWhichArea, dataMode = None):
    """
    Select filtered objects
    Ex: To have a fast selection for CP, add in menu_extension
        PythonEvalExpr(\"MenuCommandsExt.select,
                       {'crew.main_func':'CP'},
                       Cui.CuiWhichArea,
                       Cui.CrewMode\")
    """
    
    def getChainIds(windowArea,dataMode):
        #Inline to get ids of objects
        
        if dataMode == Cui.CrewMode:
            chainsInWindow = Cui.CuiGetCrew(Cui.gpc_info, windowArea, "window")
        elif dataMode == Cui.CrrMode:
            chainsInWindow = Cui.CuiGetTrips(Cui.gpc_info, windowArea, "window")
        elif dataMode == Cui.LegMode:
            chainsInWindow = Cui.CuiGetLegs(Cui.gpc_info, windowArea, "window")
        else:
            raise Exception("Select.py:: Not possible to use "+\
                            "implemented for selected CuiAreaMode")
        chainsInWindow = [str(id) for id in  chainsInWindow]
        return chainsInWindow
    gpcWindowArea = Cui.CuiAreaIdConvert(Cui.gpc_info, windowArea)
    # Store which window we are working in!
    print "In Select.select(): Selection:"
    print selectionCriterias
    
    if dataMode == None:
        for mode in range(Cui.MaxAreaModes):
            try:
                Cui.CuiCheckAreaMode(Cui.gpc_info, windowArea, mode)
            except:
                print "CuiCheckAreaMode threw Exception in Select.py"
                continue
            dataMode = mode
            break
    if not "FILTER_METHOD" in selectionCriterias:
        # If FILTER_METHOD isn't explicitly set we assume REPLACE,
        # as in standard selection form.
        # This is the default case for CuiDisplayFilteredObjects
        print "In Select.select() no FILTER_METHOD"
        selectionCriterias["FILTER_METHOD"] = "REPLACE"
    if "FC_LEGAL_CHAIN" in selectionCriterias:
        # filter and display legal rosters also included empty ones
        # to be able to select among legal rosters
        # First displays all legal/illgel chains in scriptbuffer
        # then filters window and select the ones matching prevoius selection
        legality_mode = [Cui.CuiShowIllegal,
                         Cui.CuiShowLegal][selectionCriterias["FC_LEGAL_CHAIN"]=='YES']
        
        del selectionCriterias["FC_LEGAL_CHAIN"] # not needed anymore
        
        etab = SelectionEtable(selectionCriterias)
        Cui.CuiDisplayObjects(Cui.gpc_info,Cui.CuiScriptBuffer,dataMode,
                              legality_mode)
        all_legality_chains = getChainIds(Cui.CuiScriptBuffer ,dataMode)
        
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, gpcWindowArea, 'window')
        Cui.CuiDisplayFilteredObjects(Cui.gpc_info, gpcWindowArea,
                                      dataMode, str(etab))
        
        filtered_chains = getChainIds(gpcWindowArea ,dataMode)
        etab.unlink()
        filtered_legality_chains = [id for id in filtered_chains \
                                    if id in all_legality_chains]
        
        Cui.CuiDisplayGivenObjects(Cui.gpc_info,gpcWindowArea , 
                                   dataMode, dataMode,
                                   filtered_legality_chains, 0)
        
        return 0
        
    elif selectionCriterias["FILTER_METHOD"].upper() == "ADD":
        print "In Select.select() FILTER_METHOD = Add"
        #This must be done to be able to display the chain found in the filtered 
        #selection first in the window. At the end the rest of the chain is added
        #to the window.
        tmpSelectionCriterias = selectionCriterias
        
        chainsInWindow = getChainIds( windowArea,dataMode)
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, Cui.CuiScriptBuffer, 
                                   dataMode, dataMode, chainsInWindow, 0)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, 'window')
        tmpSelectionCriterias["FILTER_METHOD"] = "REPLACE"
        etab = SelectionEtable(tmpSelectionCriterias)

        #Sort out the chain you want to add on the top of the window
        Cui.CuiDisplayFilteredObjects(Cui.gpc_info, Cui.CuiScriptBuffer,
                                      dataMode, str(etab))
        etab.unlink()
        selectedChains = getChainIds(Cui.CuiScriptBuffer,dataMode)
        # Show the selected Chain first and then add the rest of the crew in the
        # window if there are any chain presented
        
        for chainId in selectedChains:
            if chainId in chainsInWindow:
                chainsInWindow.remove(chainId)
        selectedChains.extend(chainsInWindow)
        selectedChains = map(lambda id: str(id),selectedChains)
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, gpcWindowArea, 
                                   dataMode, dataMode, selectedChains, 0)
        
        
    else:
        etab = SelectionEtable(selectionCriterias)
        Cui.CuiDisplayFilteredObjects(Cui.gpc_info, gpcWindowArea, dataMode,
                                      str(etab))
        etab.unlink()
        
    HelperFunctions.redrawAreaScrollHome(windowArea)


#
# Shortcuts to regularly used functions
#
def selectCrew(selectionCriterias={}, usePlanningArea=True,
               area = Cui.CuiWhichArea):
    if usePlanningArea:
        selectionCriterias['planning_area.%crew_is_in_planning_area%'] = 'true'
    select(selectionCriterias, windowArea = area, dataMode = Cui.CrewMode)


def subSelectCrew(selectionCriterias={}, usePlanningArea=False):
    selectionCriterias['FILTER_METHOD'] = 'SUBSELECT'
    selectCrew(selectionCriterias, usePlanningArea)


def addSelectCrew(selectionCriterias={}, usePlanningArea=True):
    selectionCriterias['FILTER_METHOD'] = 'ADD'
    selectCrew(selectionCriterias, usePlanningArea)

    
def selectTrip(selectionCriterias={}, usePlanningArea=True):
    if usePlanningArea:
        selectionCriterias['planning_area.%trip_is_in_planning_area%'] = 'true'
    select(selectionCriterias, dataMode = Cui.CrrMode)
    
    
def selectTripQual(qual, cat=None):
    selectParam(selectTripQual_criteria(qual, cat), 
                {'studio_select.py_select_qual':qual}, 
                dataMode = Cui.CrrMode)


def selectSimQual(qual, cat=None):
    selectParam(selectSimQual_criteria(qual, cat), 
                {'studio_select.py_select_qual':qual}, 
                dataMode = Cui.CrrMode)


def selectSBYQual(qual, cat=None):
    selectParam(selectSBYQual_criteria(qual, cat), 
                {'studio_select.py_select_qual':qual}, 
                dataMode = Cui.CrrMode)
    

def selectTripQual_criteria(qual, cat):
    selectCriteria = {'studio_select.%leg_qual%': qual}
    selectCriteria['leg.%is_deadhead%'] = 'false'
    if cat is not None:
        if cat == "FC":
            selectCriteria['crew_pos.%leg_has_assigned_fc%'] = 'true'
        else:
            selectCriteria['crew_pos.%leg_has_assigned_cc%'] = 'true'
    return selectCriteria


def selectSimQual_criteria(qual, cat):
    selectCriteria = {'leg.%sim_leg_qual%': qual}
    selectCriteria['leg.%is_simulator%'] = 'true'
    if cat is not None:
        if cat == "FC":
            selectCriteria['crew_pos.%leg_has_assigned_fc%'] = 'true'
        else:
            selectCriteria['crew_pos.%leg_has_assigned_cc%'] = 'true'
    return selectCriteria


def selectSBYQual_criteria(qual, cat):
    selectCriteria = {'standby.%sby_ac_qual%': qual}
    selectCriteria['leg.%standby_code_with_qualification%'] = 'true'
    if cat is not None:
        if cat == "FC":
            selectCriteria['crew_pos.%leg_has_assigned_fc%'] = 'true'
        else:
            selectCriteria['crew_pos.%leg_has_assigned_cc%'] = 'true'
    return selectCriteria


def selectAllQual(qual, cat=None):
    selectParam(selectAllQual_criteria(qual, cat), 
                {'studio_select.py_select_qual':qual}, 
                dataMode = Cui.CrrMode)


def selectAllQual_criteria(qual, cat):
    # Trip, Simulator or SBY
    selectCriteria = {'studio_select.%leg_qual%': qual}
    if cat is not None:
        if cat == "FC":
            selectCriteria['crew_pos.%leg_has_assigned_fc_or_trtl%'] = 'true'
        else:
            selectCriteria['crew_pos.%leg_has_assigned_cc%'] = 'true'
    return selectCriteria


def selectTripUsingPlanningAreaBaseFilter(selectionCriterias={}, area=Cui.CuiWhichArea):
    if len(selectionCriterias)>15:
        # If Sel_tmp uses CRC_VALUE_19, basefilter will be ignored!
        Errlog.log("Select.py:: Warning, setting to many filters, basefilter will not work!")
    Cui.CuiSetBaseFilter(Cui.gpc_info, area, Cui.CrrMode, "trip_in_planning_area.sel")
    select(selectionCriterias, dataMode = Cui.CrrMode, windowArea=area)
    
def selectCrewUsingPlanningAreaBaseFilter(selectionCriterias={}, area=Cui.CuiWhichArea):
    if len(selectionCriterias)>15:
        # If Sel_tmp uses CRC_VALUE_19, basefilter will be ignored!
        Errlog.log("Select.py:: Warning, setting to many filters, basefilter will not work!")
    Cui.CuiSetBaseFilter(Cui.gpc_info, area, Cui.CrewMode, "crew_in_planning_area.sel")
    select(selectionCriterias, dataMode = Cui.CrewMode, windowArea=area)
    
def selectLegsUsingPlanningAreaBaseFilter(selectionCriterias={}, area=Cui.CuiWhichArea):
    if len(selectionCriterias)>15:
        # If Sel_tmp uses CRC_VALUE_19, basefilter will be ignored!
        Errlog.log("Select.py:: Warning, setting to many filters, basefilter will not work!")
    Cui.CuiSetBaseFilter(Cui.gpc_info, area, Cui.LegMode, "leg_in_planning_area.sel")
    select(selectionCriterias, dataMode = Cui.LegMode, windowArea=area)
    
def selectCrewOutsidePlanningAreaBaseFilter(selectionCriterias={}, area=Cui.CuiWhichArea):
    #Cui.CuiAreaRevealAllSubplanCrew(Cui.gpc_info, area)
    selectionCriterias['planning_area.%crew_is_in_planning_area%'] = 'false'
    select(selectionCriterias, dataMode = Cui.CrewMode, windowArea=area)

def selectTripsOutsidePlanningAreaBaseFilter(selectionCriterias={}, area=Cui.CuiWhichArea):
    #Cui.CuiRevealAllCrrs(Cui.gpc_info, area)
    # Disable base filtering
    Cui.CuiDisplayObjects(Cui.gpc_info, area, Cui.CrrMode, Cui.CuiShowAll)
    selectionCriterias['planning_area.%trip_is_in_planning_area%'] = 'false'
    select(selectionCriterias, dataMode = Cui.CrrMode, windowArea=area)
    
def selectLegsOutsidePlanningAreaBaseFilter(selectionCriterias={}, area=Cui.CuiWhichArea):
    #Cui.CuiRevealAllCrrs(Cui.gpc_info, area)
    # Disable base filtering
    Cui.CuiDisplayObjects(Cui.gpc_info, area, Cui.LegMode, Cui.CuiShowAll)
    selectionCriterias['planning_area.%leg_is_in_planning_area%'] = 'false'
    select(selectionCriterias, dataMode = Cui.LegMode, windowArea=area)
    
def subSelectTrip(selectionCriterias={}, usePlanningArea=False):
    selectionCriterias['FILTER_METHOD'] = 'SUBSELECT'
    selectTrip(selectionCriterias, usePlanningArea)


def selectAndSort(selectionCriterias={},
                  sortCriteria=None, usePlanningArea=True,
                  dataMode=Cui.CrewMode):
    if dataMode == Cui.CrewMode:
        selectCrew(selectionCriterias, usePlanningArea)
    else:
        selectTrip(selectionCriterias, usePlanningArea)
    Cui.CuiSortArea(Cui.gpc_info,Cui.CuiWhichArea, Cui.CuiSortRuleValue,
                    sortCriteria)
 

def selectParam(selectionCriterias={}, paramSettings={},
                windowArea=Cui.CuiWhichArea, dataMode=None):
    """
    Select filtered objects after setting parameters
    Note: the parameters are not restored
    """
    for key, value in paramSettings.items():
        rave.param(key).setvalue(value)
    select(selectionCriterias, windowArea, dataMode)


def selectParamCrew(selectionCriterias={}, paramSettings=None,
                    usePlanningArea=True):
    if usePlanningArea:
        selectionCriterias['planning_area.%crew_is_in_planning_area%'] = 'true'
    selectParam(selectionCriterias, paramSettings, dataMode = Cui.CrewMode)

    
# The qualification selects need to be separated by category, since there is an
# overlap between ac qualification for FC and CC.
def selectCrewQual(qual, cat=None):
    selectCriteria = {'studio_select.%has_airport_or_aircraft_qln%':'true'}
    if cat is not None:
        if cat == "FC":
            catCriteria = 'crew.is_pilot'
        elif cat == "CC":
            catCriteria = 'crew.is_cabin'
        selectCriteria[catCriteria] = 'true'
    selectParamCrew(selectCriteria,
                    {'studio_select.py_select_qual':qual})


def subSelectCrewQual(qual, cat=None):
    selectCriteria = {'studio_select.%has_airport_or_aircraft_qln%':'true',
                      'FILTER_METHOD':'SUBSELECT'}
    if cat is not None:
        if cat == "FC":
            catCriteria = 'crew.is_pilot'
        elif cat == "CC":
            catCriteria = 'crew.is_cabin'
        selectCriteria[catCriteria] = 'true'
    selectParamCrew(selectCriteria,
                    {'studio_select.py_select_qual':qual},
                    usePlanningArea=False)

# Trip Equipment Selection:
# Select trips that can be manned by crew with a specific qualification  
 
def selectTripEquipment(qual, cat=None, usePlanningArea=False):
    selectTrip(selectTripEquipment_criteria(qual, cat), usePlanningArea)


def subSelectTripEquipment(qual, cat=None):
    subSelectTrip(selectTripEquipment_criteria(qual, cat))


def selectTripEquipment_criteria(qual, cat):
    selectCriteria = {'leg.%qual%': qual}
    if cat is not None:
        if cat == "FC":
            selectCriteria['fundamental.%is_open_cabin_trip%'] = 'false'
        else:
            selectCriteria['fundamental.%is_open_cabin_trip%'] = 'true'
    return selectCriteria

def restore_sorting(area):
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, area)
    SORTER.restore_sorting(area)
    
def sort(area, mode, value):
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, area)
    SORTER.sort(area, mode, value)
    
def sortParam(sortCriteria, paramSettings={}, windowArea=Cui.CuiWhichArea):
    """
    Sort objects after setting parameters
    Note: the parameters are not restored
    """
    for key, value in paramSettings.items():
        rave.param(key).setvalue(value)
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, windowArea)
    sort(area, Cui.CuiSortRuleValue, sortCriteria)
    

## def selectionMaskWrapperForCct(area=Cui.CuiWhichArea):
##     area = Cui.CuiAreaIdConvert(Cui.gpc_info,area)
##     # Get currently visible trips
##     orgSelectedTrips = Cui.CuiGetTrips(Cui.gpc_info, area, 'window')
##     orgSelectedTrips = [str(id) for id in orgSelectedTrips]
##     # Set basefilter
##     try:
##         Cui.CuiSetBaseFilter(Cui.gpc_info,
##                              Cui.CuiScriptBuffer,
##                              Cui.CrrMode,
##                              "region_filter_crr_cct.sel")
##         # Move trips to scriptbuffer
##         Cui.CuiDisplayGivenObjects(Cui.gpc_info, Cui.CuiScriptBuffer,
##                                    Cui.CrrMode,
##                                    Cui.CrrMode,
##                                    orgSelectedTrips,0 )
##         # Perform selection mask on scriptbuffer
##         Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, 'window')
##         Cui.CuiFilterObjects(Cui.gpc_info, Cui.CuiScriptBuffer, "CrrFilter", 0, 0)
##         # Get selected trips
##         selectedTrips = Cui.CuiGetTrips(Cui.gpc_info, Cui.CuiScriptBuffer, 'window')
##         selectedTrips = [str(id) for id in selectedTrips]
##         # Show selected trips in trip window
##         Cui.CuiDisplayGivenObjects(Cui.gpc_info, area, 
##                                    Cui.CrrMode, Cui.CrrMode,selectedTrips , 0)
##         # Reset basefilter in scriptbuffer
##         Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiScriptBuffer,
##                               Cui.AcRotMode,
##                               Cui.CuiShowNone)
##     except KeyboardInterrupt:
##         # Cancel in form, restore selection
##         Cui.CuiDisplayGivenObjects(Cui.gpc_info, area, 
##                                    Cui.CrrMode, Cui.CrrMode,orgSelectedTrips)

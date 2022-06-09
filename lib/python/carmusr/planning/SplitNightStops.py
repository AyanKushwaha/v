import Cui
import Gui
import Select as Select

def splitNightStopsAtHomebaseCrr(currentArea = Cui.CuiScriptBuffer):
    """
    This function splits all trips with night stop(s) at homebase (Crr). 
    """

    # Prompt user 
    if not Gui.GuiYesNo("Split Trips", "Split all trips with night stop(s) at homebase?"):
        return
                     
    # Make sure no legs are marked in the work area.
    Cui.CuiUnmarkAllLegs(Cui.gpc_info, currentArea, 'WINDOW')

    # Filter all trips with night stops at homebase and select the legs ending at homebase
    # before the night stop.
    Select.select({'FILTER_METHOD': 'REPLACE',
                   'FILTER_PRINCIP': 'ANY',
                   'FILTER_MARK': 'LEG',
                   'leg.%in_publ_period%': 'TRUE',
                   'planning_area.%leg_is_in_planning_area%': 'TRUE',
                   'rules_soft_ccp.%leg_is_night_stop_hb%': 'TRUE',
                  }, currentArea, Cui.CrrMode)
    
    nbrOfChains = Cui.CuiGetNumberOfChains(Cui.gpc_info, currentArea)

    # Split marked chains
    if nbrOfChains:
        Cui.CuiSplitChainObjects(Cui.gpc_info, currentArea, 'MARKED',0,0)
    else:
        Gui.GuiMessage("No trips with night stop(s) at homebase to split.")

    # Make sure no legs are marked in the work area.
    Cui.CuiUnmarkAllLegs(Cui.gpc_info, currentArea, 'WINDOW')

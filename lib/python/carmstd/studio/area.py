#######################################################

# area.py
# -----------------------------------------------------
# Studio Application
#
# Created:    2004-12-02
# By:         Carmen
#######################################################
"""
A module containing some useful functions for area handling.
"""
#
# Suitable functions are missing in the Studio API. 
# The implementation of these functions is therefore ugly. 
# 
#
import Errlog, Cui, Csl


def getAreaMode(area):
    """
    Return the mode of the specified area

    Arguments:
        None
    Return value:
        Studio mode, e.g. Cui.CrrMode. See Cui
        If the area does not exist, "Cui.CuiNoArea" is returned.
    """
    mode = Cui.CuiGetAreaMode(Cui.gpc_info, area)
    if mode == Cui.NoMode: #Cui.CuiGetAreaMode returns Cui.NoMode even if the area does not exist
        # Return Cui.NoMode if area exist, otherwise return Cui.CuiNoArea
        return Cui.CuiAreaExists({"WRAPPER" : Cui.CUI_WRAPPER_NO_EXCEPTION}, Cui.gpc_info,area)
    return mode 
        
def getFirstArea(mode, skipIds=[]):
    """
    Get the first area with the requested mode

    Arguments:
        mode: Studio mode, e.g Cui.CrrMode. see Cui
    Return Value:
        First Studio Area with the requested mode
        e.g. Cui.CuiArea1
        If the area does not exist, "Cui.CuiNoArea" is returned.
    """
    if type(skipIds) != type([]):
        skipIds = [skipIds]
    for a in [Cui.CuiArea0, Cui.CuiArea1, Cui.CuiArea2, Cui.CuiArea3]:
        if skipIds and a in skipIds:
            continue
        if getAreaMode(a) == mode:
            return a
    return Cui.CuiNoArea
            
def getAreaModes():
    """
    Returns a list with information about the mode of all 
    the areas in Studio.

    Arguments:
        None
    Return Value:
        List of Studio Area modes for each area.
    """
    modes = []
    for a in range(Cui.CuiAreaN): modes.append(getAreaMode(a))
    return modes

def createNewArea():
    """
    Creates a new area and returns the index of it. 
    Note that max 4 areas are supported. 

    Arguments:
        None
    Return values:
        Int: Index of the created area. Cui.CuiNoArea if 4 areas exist.
    """
    for a in range(Cui.CuiAreaN):
        if Cui.CuiAreaExists({"WRAPPER" : Cui.CUI_WRAPPER_NO_EXCEPTION}, Cui.gpc_info, a) == 0:
            continue
        Cui.CuiOpenArea(Cui.gpc_info, 0)
        return a
    return Cui.CuiNoArea

def getOppositArea(area=Cui.CuiWhichArea):
    """
    Returns the id of an opposite area. If no opposite area 
    exists a new one is created.

    :param area: The area whose opposite we want.
    :type area: :carmsys_man:`CuiAreaId`
    :rtype: :carmsys_man:`CuiAreaId`
    """
    
    if area == Cui.CuiWhichArea:
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    
    for area_candidate in range(Cui.CuiAreaN):
        area_mode = Cui.CuiGetAreaMode(Cui.gpc_info, area_candidate)
        if area_mode != None and area != area_candidate:
            return area_candidate

    return createNewArea()


def promptPush(t=None):
    """
    Prompts a argument text in the Studio status bar.

    Arguments:
        text: String. Message to prompts
              If empty an empty message is prompted
    Return value:
        None
    """
    csl = Csl.Csl()
    if t is None:
        csl.evalExpr('csl_prompt("")')
    else:
        csl.evalExpr('csl_prompt("%s")' % t)

def promptTick():
    """
    Propts a tick in the studio status bar

    Arguments:
        None
    Return value:
        None
    """
    csl = Csl.Csl()
    csl.evalExpr('csl_prompt_tick()')

if __name__ == "__main__":
    "Some self testing"
    Errlog.set_user_message(str(getAreaMode(Cui.CuiArea0)))
    Errlog.set_user_message(str(createNewArea()))
    Errlog.set_user_message(str(getAreaModes()))


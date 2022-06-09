#######################################################

# area.py
# -----------------------------------------------------
# Studio Application
#
# Created:    2005-12-05
# By:         Carmen
#######################################################
"""
Area
Contains functionality for handling studio areas.

The module is application independent and if the
method is not supported an exception is raised.
"""
import Cui

from application import application
if application=="Matador":
    import carmstd.matador.area as a
else:
    import carmstd.studio.area as a


def getAreaMode(area):
    """
    Return the mode of the specified area

    Arguments:
        None
    Return value:
        Studio mode, e.g. Cui.CrrMode. See Cui
        If the area does not exist, "None" is returned.
    """
    return a.getAreaMode(area)

def getFirstArea(mode, skipIds=[]):
    """
    Get the first area with the requested mode

    Arguments:
        mode: Studio mode, e.g Cui.CrrMode. see Cui
        skipIds: area-ids which should be skipped when searching
    Return Value:
        First Studio Area with the requested mode
        e.g. Cui.CuiArea1
        If the area does not exist, "Cui.CuiNoArea" is returned.
    """
    return a.getFirstArea(mode, skipIds)
    
def getAreaModes():
    """
    Returns a list with information about the mode of all 
    the areas in Studio.

    Arguments:
        None
    Return Value:
        List of Studio Area modes for each area.
    """
    return a.getAreaModes()

def createNewArea():
    """
    Creates a new area and returns the index of it. 
    Note that max 4 areas are supported. 
    An exception is generated if you try to create the 5th.

    Arguments:
        None
    Return values:
        Int: Index of the created area
    """
    return a.createNewArea()

def promptPush(text=None):
    """
    Prompts a argument text in the Studio status bar.

    Arguments:
        text: String. Message to prompts
              If empty an empty message is prompted
    Return value:
        None
    """
    a.promptPush(text)

def promptTick():
    """
    Propts a tick in the studio status bar

    Arguments:
        None
    Return value:
        None
    """
    a.promptTick()


def get_opposite_area(area=Cui.CuiWhichArea):
    """
    Returns the id of an opposite area. If no opposite area
    exists a new one is created.

    Note: If more than two windows are used, the core may have
          another idea of opposite window than this function.

    @param area: The area whose opposite we want.
    @type area: CuiAreaId
    @rtype: CuiAreaId
    """
    return a.getOppositArea(area)

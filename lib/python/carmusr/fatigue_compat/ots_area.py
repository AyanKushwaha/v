#
# This file has been copied from NiceToHaveIQ by 'ADM/copy_from_nth'.
# In NiceToHaveIQ the file is found as 'lib/python/nth/studio/area.py'.
# Please do not change the file. Copy new versions from NiceToHaveIQ instead.
#
"""
Functions for handling areas (windows) in Studio.
Complements the `CuiArea` functions in CARMSYS.
"""

import Cui

try:
    from Cui import CancelException
except ImportError:
    # < v16
    CancelException = KeyboardInterrupt


max_number_of_areas = Cui.CuiAreaN


def get_current_area():
    '''
    Returns the currently active area in Studio.
    @rtype: CuiAreaId
    '''
    return Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)


def get_opposite_area(area=Cui.CuiWhichArea):
    """
    Returns the id of an opposite area. If no opposite area
    exists a new one is created.

    @param area: The area whose opposite we want.
    @type area: CuiAreaId
    @rtype: CuiAreaId
    """
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, area)

    for area_candidate in xrange(Cui.CuiAreaN):
        if area_exists(area_candidate) and area != area_candidate:
            return area_candidate

    return create_new_area()


def area_exists(area):
    """
    Checks if an area exists.

    @param area: Area to check.
    @type area: CuiAreaId
    @rtype: bool
    """
    ret = not Cui.CuiAreaExists({"WRAPPER": Cui.CUI_WRAPPER_NO_EXCEPTION},
                                Cui.gpc_info, area)
    return ret


def get_area_mode(area):
    """
    Returns the mode of the specified area
    If the area does not exist, "None" is returned.

    @param area: Area to check.
    @type area: CuiAreaId
    @rtype: AreaMode
    """
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, area)
    if area_exists(area):
        return Cui.CuiGetAreaMode(Cui.gpc_info, area)
    else:
        return None


def create_new_area():
    """
    Creates a new area and returns the index of it.
    Note that max 4 areas are supported.

    @return: The AreaId of the newly created area.
    @rtype: CuiAreaId
    @raise __main__.exception: Raised if trying to create a 5th area
    """
    areas_before = set(a for a in xrange(Cui.CuiAreaN) if area_exists(a))
    Cui.CuiOpenArea(Cui.gpc_info, 0)
    areas_after = set(a for a in xrange(Cui.CuiAreaN) if area_exists(a))
    return list(areas_after - areas_before)[0]


if __name__ == "__main__":
    import Gui
    "Some self testing"
    Gui.GuiMessage(str(get_opposite_area()))
    Gui.GuiMessage(str(get_area_mode(Cui.CuiArea0)))
    Gui.GuiMessage(str(area_exists(Cui.CuiArea0)))
    Gui.GuiMessage(str(create_new_area()))

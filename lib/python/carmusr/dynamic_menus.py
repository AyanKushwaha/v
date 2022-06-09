'''
Dynamic menus for filter, sub-filter, add-filter and select.
'''

import carmensystems.rave.api as r
from Localization import MSGR
import Gui
import MenuState

from carmstd import gui_ext
#from carmstd import translation_type_ext
from carmstd import bag_handler


METHOD_REPLACE = 0
METHOD_SUBFILTER = 1
METHOD_ADD = 2
METHOD_SELECT = 3
METHOD_REPLACE_AND_SELECT = 4
METHOD_SELECT_CREW = 5


class DynamicFilterMenuItems(object):
    """
    Instances of this class (or a sub-class) is what you use in csl
    (i.e. in menu source files and as the argument csl_refresh_expr to DynamicFilterMenuItemSubMenu)
    to define dynamic (parts of) filter menus.
    "items" is a sequence of "item objects".
    An "item object" can be:
      * an instance of a sub-class to DynamicFilterMenuItemAbstract
      * a tuple (the members of the tuple are given as arguments to DynamicFilterMenuItemRave)
    The "items" are defined by a redefined "_get_items" in a sub class

    All additional named arguments become attributes of the instance.
    """

    def __init__(self, menu_name, method=METHOD_REPLACE, **kw):
        self.menu_name = menu_name
        self.method = method
        for ident in kw:
            self.__setattr__(ident, kw[ident])

    def _get_items(self):
        """Implement in sub class"""
        return []

    def create(self):
        """
        Call this yourself from csl.
        """
        created_sub_menus = 0
        for item in self._get_items():
            if not isinstance(item, DynamicFilterMenuItemAbstract):
                item = DynamicFilterMenuItemRave(*item)
            item._create(self.menu_name, self.method, created_sub_menus)
            if isinstance(item, DynamicFilterMenuItemSubMenu):
                created_sub_menus += 1
        return 0


####################################
# Classes you can use as menu items.
####################################

class DynamicFilterMenuItemAbstract(object):
    """
    Common base class for classes that can be used to define one menu item.
    """
    pass


class DynamicFilterMenuItemSubMenu(DynamicFilterMenuItemAbstract):

    def __init__(self, title, csl_refresh_expr=None, **kw):
        """
        The content of the sub-menu can be defined in two ways:
          csl_refresh_expr:
               A csl expression which is executed when Studio is about to
               display the menu. The expression typically contains the
               strings "MENU_NAME" and "METHOD", which are replaced with the
               actual menu name and the actual method identifier.
        Additional arguments:
          kw: Named arguments passed to "gui_ext.add_sub_menu".
        """
        self.title = title
        self.csl_refresh_expr = csl_refresh_expr
        self.kw = kw

    def _create(self, parent_menu_name, method, created_sub_menus):
        menu_name = "%sSub%s%s" % (parent_menu_name, created_sub_menus, method)
        if self.csl_refresh_expr:
            self.csl_refresh_expr = self.csl_refresh_expr.replace("METHOD", "%d" % method).replace("MENU_NAME", menu_name)
        gui_ext.add_sub_menu(parent_menu_name, self.title, menu_name, self.csl_refresh_expr, **self.kw)


class DynamicFilterMenuItemRave(DynamicFilterMenuItemAbstract):

    def __init__(self, title, rave_expr, filter_type='', rave_result="T", **kw):
        self.title = title
        self.rave_expr = rave_expr
        self.filter_type = filter_type
        self.rave_result = rave_result
        self.kw = kw  # Additional arguments for "gui_ext.add_menu_item"

    _method2func = {METHOD_REPLACE: "carmstd.select.filter_by_rave_expression",
                    METHOD_SUBFILTER: "carmstd.select.sub_filter_by_rave_expression",
                    METHOD_ADD: "carmstd.select.add_filter_by_rave_expression",
                    METHOD_SELECT: "carmstd.select.select_by_rave_expression",
                    METHOD_REPLACE_AND_SELECT: "carmstd.select.select_filter_by_rave_expression",
                    METHOD_SELECT_CREW: "carmstd.select.select_crew_by_rave_expression"}

    def _create(self, parent_menu_name, method, *args):

        func = self._method2func[method]

        if method in (METHOD_REPLACE, METHOD_SUBFILTER, METHOD_ADD, METHOD_REPLACE_AND_SELECT):
            py_cmd_args = "rave_expr='%s', rave_result='%s', filter_type='%s'" % (self.rave_expr, self.rave_result, self.filter_type)
        else:
            py_cmd_args = "rave_expr='%s', rave_result='%s'" % (self.rave_expr, self.rave_result)

        py_cmd = "%s(%s)" % (func, py_cmd_args)
        gui_ext.add_menu_item(parent_menu=parent_menu_name,
                              title=self.title,
                              python_action=py_cmd,
                              **self.kw)


class DynamicFilterMenuItemSeparator(DynamicFilterMenuItemAbstract):

    def __init__(self, identifier=None):
        self.identifier = identifier

    def _create(self, parent_menu_name, *args):
        gui_ext.add_separator(parent_menu_name, self.identifier)


class DynamicFilterMenuItemTitle(DynamicFilterMenuItemAbstract):

    def __init__(self, title, identifier=None):
        self.identifier = identifier
        self.title = title

    def _create(self, parent_menu_name, *args):
        Gui.GuiAddMenuTitle(parent_menu_name, None, self.title, None, self.identifier, None)


##########################
# Trip window
##########################

class TripFilterMenu(DynamicFilterMenuItems):

    def _get_items(self):

        if not MenuState.theStateManager.getVal("RuleSetLoaded"):
            return []

        items = []


        if MenuState.theStateManager.getVal("CalibrationLookbackAvailable"):
            csl_refresh_expr = """PythonEvalExpr("carmusr.calibration.gui.FilterCalibrationLookbackMenu('MENU_NAME', METHOD).create()")"""
            items.append(DynamicFilterMenuItemSubMenu(MSGR("Calibration Lookback"),
                                                      csl_refresh_expr,
                                                      mnemonic=MSGR("_LCalibration Lookback")))
        if MenuState.theStateManager.getVal("CalibrationAvailable"):
            csl_refresh_expr = """PythonEvalExpr("carmusr.calibration.gui.FilterCalibrationHistoryMenu('MENU_NAME', METHOD).create()")"""
            items.append(DynamicFilterMenuItemSubMenu(MSGR("Calibration History"),
                                                      csl_refresh_expr,
                                                      mnemonic=MSGR("_HCalibration History")))
            csl_refresh_expr = """PythonEvalExpr("carmusr.calibration.gui.FilterSensitivityIndexMenu('MENU_NAME', METHOD).create()")"""
            items.append(DynamicFilterMenuItemSubMenu(MSGR("Trips with High Sensitivity"),
                                                      csl_refresh_expr,
                                                      mnemonic=MSGR("_STrips with High Sensitivity")))
            items.append(DynamicFilterMenuItemSeparator())

        return items

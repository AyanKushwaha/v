"""
Useful calibration report support functions etc.
"""

import six
from six.moves import range
from six.moves import zip
from functools import reduce
from collections import defaultdict
from collections import Counter
import time

import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave
import Cui
import Gui
from Localization import MSGR
from Variable import Variable
import Errlog
from RelTime import RelTime
from jcms.calibration import plan
import Dates
import Names
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator

from carmusr.calibration import mappings
from carmusr.calibration.mappings import report_generation as rg
from carmusr.calibration.mappings import studio_palette as sp
from carmusr.calibration.mappings import bag_handler
from carmusr.calibration.mappings import date_extensions as de
from carmusr.calibration.util import compare_plan
from carmusr.calibration.util import common
from carmusr.calibration.util import basics
from carmusr.calibration.util import config_per_product

BOLD = prt.font(weight=prt.BOLD)
ITALIC = prt.font(style=prt.ITALIC)
BORDER_LEFT = prt.border(left=1)
LINK_FONT = prt.Font(size=10, style=prt.ITALIC, weight=prt.BOLD)
CODE_FONT = prt.font(face=prt.MONOSPACE)

HEATMAP_RED = "#CC6677"
HEATMAP_BLUE = "#4477AA"
SIMPLE_TABLE_BORDER_GREY = "#B7B8B6"


class CalibReports:

    class VOT:
        title = MSGR('Rule Violations over Time')

    class VOS:
        title = MSGR("Rule Violations over Station")

    class VOW:
        title = MSGR("Rule Violations over Weekdays")

    class RKPI:
        title = "{} {}".format(config_per_product.DEFAULT_VARIANT_KIND_STRING, MSGR("Rule KPIs"))
        timetable_title = MSGR("Timetable Rule KPIs")

    class DABO:
        title = "{} {}".format(config_per_product.DEFAULT_VARIANT_KIND_STRING, MSGR("Dashboard"))
        timetable_title = MSGR("Timetable Dashboard")

    class RVD:
        title = MSGR('Rule Value Distribution')

    class RD:
        title = MSGR('Rule Details')

    class SI:
        title = MSGR('Sensitivity Index Distribution')

    class COMP:
        title = MSGR('Compare Trips with Other Plan')

    class PAT:
        title = MSGR('Pattern Analysis')

    class RCC:
        title = MSGR('Check Rule Consistency')

########################################################################
# Filter + select callback
########################################################################

SELECT_METHOD_PARAMETER_NAME = "report_calibration.select_method_p"


def get_select_action(area, identifiers):
    if identifiers:
        return prt.action(calib_show_and_mark_legs, (area, identifiers))
    else:
        return None


def calib_show_and_mark_legs(current_area, leg_identifiers, always_replace=False):
    """
    Supports additive select.
    """
    if get_area_mode(current_area) == Cui.NoMode:
        Gui.GuiMessage(MSGR("Impossible, the window doesn't contain anything."))
        return

    if always_replace:
        use_add = False
    else:
        try:
            val = str(rave.param(SELECT_METHOD_PARAMETER_NAME).value())
            use_add = val.endswith("add")
        except rave.UsageError:
            use_add = False

    if use_add:
        leg_identifiers = list(set(leg_identifiers) |
                               set(Cui.CuiGetLegs(Cui.gpc_info, current_area, "marked")))

    # To allow undo
    Cui.CuiExecuteFunction('PythonEvalExpr("0")',
                           MSGR("Select and filter legs"),
                           Gui.POT_REDO,
                           Gui.OPA_OPAQUE)
    opposite_area = get_opposite_area(current_area)

    try:
        display_given_objects(leg_identifiers,
                              opposite_area,
                              get_area_mode(current_area),
                              Cui.LegMode)

    except Cui.CancelException:
        Gui.GuiMessage(MSGR("Impossible, you have probably changed the plan or the window content."))

    Cui.CuiUnmarkAllLegs(Cui.gpc_info, current_area, "window")
    Cui.CuiUnmarkAllLegs(Cui.gpc_info, opposite_area, "window")

    for lid in leg_identifiers:
        Cui.CuiSetSelectionObject(Cui.gpc_info, opposite_area, Cui.LegMode, str(lid))
        Cui.CuiMarkLegs(Cui.gpc_info, opposite_area, "object")


def display_given_objects(ids,
                          area,
                          area_type,
                          obj_type):
    '''
    Convenience wrapper around CuiDisplayGivenObjects
    '''

    # This is needed to always get the right sort order. Bug in Cui.CuiDisplayGivenObjects.
    Cui.CuiDisplayObjects(Cui.gpc_info, area, area_type, Cui.CuiShowNone)

    # Since crr_identifier returns an int, we do a little
    # conversion here first for convenience.
    ids = [str(_id) for _id in ids]

    Cui.CuiDisplayGivenObjects(Cui.gpc_info,
                               area,
                               area_type,
                               obj_type,
                               ids,
                               0,  # Flags argument is not used but necessary
                               Cui.Replace,
                               Cui.CuiSortDefault)


##################################################
# Area handling
##################################################

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
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, area)

    for area_candidate in range(Cui.CuiAreaN):
        if area_exists(area_candidate) and area != area_candidate:
            return area_candidate

    return create_new_area()


def create_new_area():
    """
    Creates a new area and returns the index of it.
    Note that max 4 areas are supported.

    @return: The AreaId of the newly created area.
    @rtype: CuiAreaId
    @raise __main__.exception: Raised if trying to create a 5th area
    """
    areas_before = set(a for a in range(Cui.CuiAreaN) if area_exists(a))
    Cui.CuiOpenArea(Cui.gpc_info, 0)
    areas_after = set(a for a in range(Cui.CuiAreaN) if area_exists(a))
    return list(areas_after - areas_before)[0]


###########################################################
# Report Tables
###########################################################

class SimpleTableRow(prt.Row):

    DEFAULT_X_PADDING = 5
    DEFAULT_PADDING = prt.padding(left=DEFAULT_X_PADDING, right=DEFAULT_X_PADDING)

    def __init__(self, *components, **properties):
        if 'padding' in properties:
            self.padding = properties['padding']
            del properties['padding']
        else:
            self.padding = self.DEFAULT_PADDING

        prt.Row.__init__(self, **properties)
        for component in components:
            self.add(component)

    def add(self, component):
        if isinstance(component, prt.Container):
            # We can't assume anything about inner containers.
            # They may contain colspan and other difficulties
            pass
        elif isinstance(component, prt.Box):
            component.set(padding=self.padding)
        elif isinstance(component, int) or isinstance(component, RelTime):
            component = prt.Text(component,
                                 padding=self.padding,
                                 align=prt.RIGHT)
        else:
            component = prt.Text(component,
                                 padding=self.padding)

        return prt.Row.add(self, component)


class SimpleTable(prt.Column):
    """
    The simple table class makes it easier to create simple tables
    with a standardized format:
    Bold Header on ReportBlue background
    [Label | data] on alternating White and ReportLightBlue bg
    Single frame around the table
    """
    def __init__(self, title=None, cross_name='', use_page=True, image=None, border_frame=prt.border_frame(colour=SIMPLE_TABLE_BORDER_GREY)):
        """
        @param title: The header name of the table
        @type title: prt.Box or string
        @param cross_name: prt object name of the SimpleTable instance
                           used together with prt.Crossref()
        @type cross_name: string
        @param use_page: Should page0 breaks be added, default True
        @type use_page: Boolean
        @param image: image to be shown. Default is no icon
        @type image: string
        """
        prt.Column.__init__(self)
        self.use_page = use_page
        self.image = image

        self.num_rows = 0
        self.set(border=border_frame)

        # The title_row will make sure the background is completely coloured
        if title:
            self.title_row = prt.Row(font=prt.font(size=10, weight=prt.BOLD),
                                     background=sp.ReportBlue)
            # The title contains the actual objects (icon + texts)
            # which will be isolated from the rest of the table
            self.title = prt.Row()
            if self.image:
                self.title.add(prt.Image(self.image,
                                         name=cross_name,
                                         padding=prt.padding(2, 2, 2, 2)))
            self.title_row.add(prt.Isolate(self.title))

            self.add_title(title)
            prt.Column.add(self, self.title_row)

        self.link_row = prt.Row(font=prt.font(size=8),
                                border=prt.border(bottom=2, colour=sp.DarkGrey),
                                background=sp.Grey)
        self.num_link = 0

        self.sub_title = SimpleTableRow(font=prt.font(size=7),
                                        border=prt.border(bottom=2, colour=sp.DarkGrey),
                                        background=sp.ReportBlue)
        self.num_st = 0

        self.table = prt.Column()
        prt.Column.add(self, self.table)

    def add_title(self, title):
        """
        Method to add table headers
        @param title: column header
        @type title: string or report object

        @returns: the title object that was just added
        @rtype: report object
        """
        return self.title.add(prt.Isolate(title))

    def add_sub_title(self, sub_title, page_break=False, **kwargs):
        """
        Method to add column headers
        @param sub_title: column header
        @type sub_title: string, string-tuple or report object
        @param page_break: Should subtitle be displayed after a page break, default False
        @type use_page: Boolean
        Remaining named argument are sent as is to prt.Text if a string or string-tuple is given as sub_title.

        @returns: the sub title that was just added
        @rtype: report object
        """

        if isinstance(sub_title, str):
            sub_title = prt.Text(sub_title, **kwargs)
        if isinstance(sub_title, tuple):
            new_subt = prt.Column()
            for mem in sub_title:
                new_subt.add(SimpleTableRow(prt.Text(mem, **kwargs)))
            sub_title = new_subt

        # The sub_title row should only be shown if it is non-empty
        if self.num_st == 0:
            if page_break:
                self.table.add_header(self.sub_title)
            else:
                self.table.add(self.sub_title)

        self.sub_title.add(sub_title)
        self.num_st += 1

        return sub_title

    def add(self, row):
        """
        Method to add one table row of data
        @param row: data row to add to the table.
                    prt.Row used as is.
                    Any other object wrapped in a SimpleTableRow.
        @type row: Any
        @returns: the row that was just added
        @rtype: report row
        """

        if not isinstance(row, prt.Row):
            row = SimpleTableRow(row)

        row.set(background=self.get_background_color_for_row(self.num_rows))

        self.table.add(row)
        self.num_rows += 1

        if self.use_page:
            self.table.page0()

        return row

    @staticmethod
    def get_background_color_for_row(num_rows):
        if num_rows % 2:
            background = sp.ReportLightBlue
        else:
            background = sp.White
        return background


class SimpleDiagram(SimpleTable):
    """
    The simple diagram class inherits from SimpleTable and will override
    the icon to display a diagram image instead.
    """
    def __init__(self, title, cross_name=''):
        """
        @param title: The header name of the table
        @type title: prt.Box or string
        @param cross_name: prt object name of the SimpleDiagram instance
                           used together with prt.Crossref()
        @type cross_name: string
        """
        SimpleTable.__init__(self, title, cross_name=cross_name,
                             use_page=False,
                             image=mappings.image_file_name_diagram)


######################################
# Heatmap
######################################

class Heatmap(SimpleTable):
    """
    Returns a heatmap prt object.

    NOTE: The module report_sources.hidden.test_of_heatmap provides examples using the Heatmap class.

    General about the arguments:
    "value" can (hopefully) be of any type supporting "add" (there is some (ugly) code for RelTime)
    "x_key" and "y_key" can any type.
    "leg_identifiers" is a list of leg-identifiers corresponding to legs in a Studio window.

    @arg current_area: Studio window with legs to select.
    @type current_area: int
    @arg title: the title of the entire heatmap
    @type title: str
    @arg keyvaluedict: a dictionary where each element key is a (x_key, y_key) tuple and each value is a (value, leg_identifiers) tuple.
    @type keyvaluedict: dict
    @arg dividerdict: Optional. Values in keyvaluedict are divided by values in this dictionary and provided as frac_values (float).
    @type dividerdict: dict
    @arg keyname_x: the name (description/header) for the X keys. Default: "key x"
    @type keyname_x: str
    @arg keyname_y: the name (description/header) for the Y keys. Default: "key y"
    @type keyname_y: str
    @arg valuename: the name (description/header) for the values. Default: ""
    @type valuename: str
    @arg value_col_min_width: the minimum width for the value columns
    @type value_col_min_width: int
    @arg x_key_format: format for the x-keys. Default str
    @type x_key_format: str f(x)
    @arg y_key_format: format for the y-keys. Default str
    @type y_key_format: str f(y)
    @arg value_format: format for the values in keyvaluedict. Default str.
    @type value_format: str f(value).
    @arg frac_value_format: format for float(keyvaluedict value) / (dividerdictvalue). Default: lambda v: "%0.0f%%" % (v * 100)
    @type frac_value_format: str f(float)
    @arg divider_value_format: format for the values in dividerdict. Default str.
    @type divider_value_format: str f(value)
    @arg tooltip_format:Format for the tooltip. Default shows x-key, y-key, and value (frac_value if dividerdict is defined)
    @type tooltip_format: str f(x, y, formatted x, formatted y, v[, n, d])
    @arg x_keys: x-keys. Default: all found x-keys sorted.
    @type x_keys: sequence
    @arg y_keys: y-keys. Default: all found y-keys sorted.
    @type y_keys: sequence
    @arg value_align: align for value in keyvaluedict. Default prt.RIGHT
    @type value_align: align in PRT
    @arg frac_value_align: align for frac_value. Default prt.RIGHT
    @type frac_value_align: align in PRT
    @arg divider_value_align: align for value in dividerdict. Default prt.LEFT
    @type divider_value_align: align in PRT
    @arg show_total_row: Show total row. Default: False
    @type show_total_row: bool
    @arg show_total_col: Show total column. Default: False
    @type show_total_col: bool
    @arg total_label: Label of total row/column. Default: MSGR("Total")
    @type total_label:str
    @arg max_colour: Colour of the highest positive value in the matrix. Default: HEATMAP_RED
    @type max_colur: string, #RRGGBB
    @arg min_colour: Colour of the most negative below zero in the matrix. Default: HEATMAP_BLUE
    @type min_colur: string, #RRGGBB
    @arg zero_colour: Colour when the value is zero. Default: studio_palette.White
    @type zero_colour: string, #RRGGBB
    @arg gamma: Gamma value for the colour calculation curve from zero to maximum/minimum
    @type gamma: float
    @arg max_colour_value: The maximum value to use in colouring. Default is the maximum found in a cell.
    @type max_colour_value: Same type as value, but float if dividerdict is defined
    @arg min_colour_value: The minimum value to use in colouring. Default is the minimum found in a cell.
    @type min_colour_value: Same type as value, but float if dividerdict is defined
    @arg font_total_cell: Font for total values in matrix. Default: BOLD.
    @type font_total_cell: prt.font
    @arg font_normal_cell: Font for normal values in matrix. Default: None.
    @type font_normal_cell: prt.font
    @arg use_page: Boolean
    @type use_page: Boolean

    @returns: heatmap
    @type: prt.Column
    """
    def __init__(self,
                 current_area,
                 title,
                 keyvaluedict,
                 dividerdict=None,
                 keyname_x=MSGR("key x"),
                 keyname_y=MSGR("key y"),
                 valuename="",
                 value_col_min_width=None,
                 x_key_format=str,
                 y_key_format=str,
                 value_format=str,
                 frac_value_format=lambda v: "%0.0f%%" % (v * 100),
                 divider_value_format=str,
                 tooltip_format=None,
                 x_keys=[],
                 y_keys=[],
                 value_align=prt.RIGHT,
                 frac_value_align=prt.RIGHT,
                 divider_value_align=prt.LEFT,
                 show_total_row=False,
                 show_total_col=False,
                 total_label=MSGR("Total"),
                 max_colour=HEATMAP_RED,
                 min_colour=HEATMAP_BLUE,
                 zero_colour=sp.White,
                 gamma=1.0,
                 max_colour_value=None,
                 min_colour_value=None,
                 font_total_cell=BOLD,
                 font_normal_cell=None,
                 use_page=True):

        super(Heatmap, self).__init__(title)

        def value_object_when_divider(tooltip, font, frac_value, value, divider_value, value_ids, divider_ids):
            if not my_float(divider_value) and not my_float(value):
                return prt.Text("-", tooltip=tooltip, colspan=num_objects_in_value_cell, align=prt.CENTER)

            return prt.Row(prt.Text(frac_value_format(frac_value) if my_float(divider_value) else MSGR("N/A"),
                                    tooltip=tooltip,
                                    font=font,
                                    align=frac_value_align),
                           prt.Text(value_format(value),
                                    tooltip=tooltip,
                                    font=font,
                                    padding=prt.padding(right=0),
                                    align=value_align,
                                    action=get_select_action(current_area, value_ids)),
                           prt.Text("/",
                                    width=1,  # Work around for layout defect in PRT
                                    tooltip=tooltip,
                                    font=font,
                                    padding=prt.padding(left=0, right=0)),
                           prt.Text(divider_value_format(divider_value),
                                    tooltip=tooltip,
                                    font=font,
                                    padding=prt.padding(left=0),
                                    align=divider_value_align,
                                    action=get_select_action(current_area, divider_ids)))

        primary_value_type = type(six.itervalues(keyvaluedict).next()[0])
        value_type = primary_value_type

        keyvaluedict = defaultdict(lambda: (value_type(0), list()), keyvaluedict)

        # Make sure ALL items in the input dictionaries are displayed.
        existing_x_keys = set(x for x, _ in keyvaluedict) | set((x for x, _ in dividerdict) if dividerdict else ())
        existing_y_keys = set(y for _, y in keyvaluedict) | set((y for _, y in dividerdict) if dividerdict else ())
        x_keys = list(x_keys) + sorted(existing_x_keys - set(x_keys))
        y_keys = list(y_keys) + sorted(existing_y_keys - set(y_keys))

        if dividerdict:
            if tooltip_format is None:
                def tooltip_format(*args):
                    return "%s \n%s \n%0.1f%%" % (args[2], args[3], args[4] * 100)
            values = defaultdict(lambda: (float(), list()))
            num_objects_in_value_cell = 4
            divider_type = type(six.itervalues(dividerdict).next()[0])
            dividerdict = defaultdict(lambda: (divider_type(0), list()), dividerdict)
            primary_value_type = float
            for key, (v, ids) in six.iteritems(keyvaluedict):
                d = my_float(dividerdict[key][0])
                values[key] = (my_float(v) / d if d else 0, ids)
        else:
            if tooltip_format is None:
                def tooltip_format(*args):
                    return "%s \n%s \n%s" % (args[2], args[3], value_format(args[4]))
            values = keyvaluedict
            num_objects_in_value_cell = 1

        cc = ColourCalculator(max_colour_value if max_colour_value is not None else max(primary_value_type(0), max(v for v, _ in six.itervalues(values))),
                              min_colour_value if min_colour_value is not None else min(primary_value_type(0), min(v for v, _ in six.itervalues(values))),
                              max_colour,
                              min_colour,
                              zero_colour,
                              gamma)

        if show_total_col:
            total_row_values = defaultdict(lambda: [value_type(0), list()])
            for (_, y), (v, ids) in six.iteritems(keyvaluedict):
                total_row_values[y][0] += v
                total_row_values[y][1] += ids
            if dividerdict:
                divider_row_values = defaultdict(lambda: divider_type(0))
                for (_, y), (v, ids) in six.iteritems(dividerdict):
                    divider_row_values[y] += v
                for y in total_row_values:
                    d = my_float(divider_row_values[y])
                    total_row_values[y][0] = my_float(total_row_values[y][0]) / d if d else 0
                total_row_values = defaultdict(lambda: [float(), list()], total_row_values)

        if show_total_row:
            total_col_values = defaultdict(lambda: [value_type(0), list()])
            for (x, _), (v, ids) in six.iteritems(keyvaluedict):
                total_col_values[x][0] += v
                total_col_values[x][1] += ids
            if dividerdict:
                divider_col_values = defaultdict(lambda: divider_type(0))
                for (x, _), (v, _) in six.iteritems(dividerdict):
                    divider_col_values[x] += v
                for x in total_col_values:
                    d = my_float(divider_col_values[x])
                    total_col_values[x][0] = my_float(total_col_values[x][0]) / d if d else 0
                total_col_values = defaultdict(lambda: [float(), list()], total_col_values)

        st = self.add_sub_title(valuename)
        st.set(rowspan=2, colspan=2, valign=prt.CENTER, border=prt.border(colour=sp.DarkGrey, right=2, bottom=2))

        st = self.add_sub_title(prt.Column())
        st.add(prt.Text(keyname_x, align=prt.CENTER, valign=prt.CENTER))
        row = st.add(prt.Row())

        if show_total_col:
            row.add(prt.Text(total_label,
                             align=prt.CENTER,
                             valign=prt.BOTTOM,
                             font=prt.font(size=7, weight=prt.BOLD),
                             width=value_col_min_width,
                             colspan=num_objects_in_value_cell))

        for x_key in x_keys:
            row.add(prt.Text(x_key_format(x_key),
                             align=prt.CENTER,
                             valign=prt.BOTTOM,
                             width=value_col_min_width,
                             colspan=num_objects_in_value_cell))

        body = self.add(prt.Row(VerticalText(13, len(keyname_y) * 4, txt=keyname_y, valign=prt.CENTER, background=sp.ReportBlue)))
        matr = body.add(prt.Column())

        row_num = 0
        if show_total_row:
            row_num += 1
            row = matr.add(prt.Row(prt.Text(total_label,
                                            valign=prt.CENTER,
                                            align=prt.RIGHT,
                                            font=prt.font(size=7, weight=prt.BOLD),
                                            background=sp.ReportBlue,
                                            border=prt.border(colour=sp.DarkGrey, right=2))))

            if show_total_col:
                value = sum((val for val, _ in six.itervalues(keyvaluedict)), value_type(0))
                leg_ids = reduce(list.__add__, (ids for _, ids in six.itervalues(total_col_values)))
                if dividerdict:
                    divider_value = sum((val for val, _ in six.itervalues(dividerdict)), divider_type(0))
                    divider_ids = reduce(list.__add__, (ids for _, ids in six.itervalues(dividerdict)))
                    d = my_float(divider_value)
                    frac_value = my_float(value) / d if d else 0
                    tooltip = tooltip_format(None, None, total_label, total_label, frac_value, value, divider_value)
                    prt_object = value_object_when_divider(tooltip, font_total_cell, frac_value, value, divider_value, leg_ids, divider_ids)
                    bg = cc(frac_value)
                else:
                    action = get_select_action(current_area, leg_ids)
                    bg = cc(value / (len(existing_x_keys) * len(existing_y_keys)))
                    prt_object = prt.Text(value_format(value),
                                          align=value_align,
                                          action=action,
                                          font=font_total_cell,
                                          tooltip=tooltip_format(None, None, total_label, total_label, value))

                row.add(prt.Row(prt_object,
                                background=bg,
                                border=prt.border_frame(2, colour=sp.DarkGrey)))

            for x_key in x_keys:
                value, leg_ids = total_col_values[x_key]
                if dividerdict:
                    nominator_value = sum((keyvaluedict[x_key, y_key][0] for y_key in y_keys), value_type(0))
                    tooltip = tooltip_format(x_key, None, x_key_format(x_key), total_label, value, nominator_value, divider_col_values[x_key])
                    prt_object = value_object_when_divider(tooltip,
                                                           font_total_cell,
                                                           value,
                                                           nominator_value,
                                                           divider_col_values[x_key],
                                                           leg_ids,
                                                           reduce(list.__add__, (dividerdict[x_key, y_key][1] for y_key in y_keys)))
                    bg = cc(value)
                else:
                    prt_object = prt.Text(value_format(value),
                                          align=value_align,
                                          tooltip=tooltip_format(x_key, None, x_key_format(x_key), total_label, value),
                                          font=font_total_cell,
                                          action=get_select_action(current_area, leg_ids))
                    bg = cc(value / len(existing_y_keys))

                row.add(prt.Row(prt_object,
                                background=bg,
                                border=prt.border(left=1, right=1, bottom=2, colour=sp.DarkGrey)))

        for y_key in y_keys:

            row_num += 1
            if row_num > 10:
                if use_page:
                    self.page0()
                body = self.add(prt.Row(prt.Text("", background=sp.ReportBlue)))
                matr = body.add(prt.Column())

            row = matr.add(prt.Row(prt.Text(y_key_format(y_key),
                                            valign=prt.CENTER,
                                            align=prt.RIGHT,
                                            font=prt.font(size=7),
                                            background=sp.ReportBlue,
                                            border=prt.border(colour=sp.DarkGrey, right=2))))
            if show_total_col:
                value, leg_ids = total_row_values[y_key]
                if dividerdict:
                    nominator_value = sum((keyvaluedict[x_key, y_key][0] for x_key in x_keys), value_type(0))
                    tooltip = tooltip_format(None, y_key, total_label, y_key_format(y_key), value, nominator_value, divider_row_values[y_key])
                    prt_object = value_object_when_divider(tooltip,
                                                           font_total_cell,
                                                           value,
                                                           nominator_value,
                                                           divider_row_values[y_key],
                                                           leg_ids,
                                                           reduce(list.__add__, (dividerdict[x_key, y_key][1] for x_key in x_keys)))
                    bg = cc(value)
                else:
                    prt_object = prt.Text(value_format(value),
                                          tooltip=tooltip_format(None, y_key, total_label, y_key_format(y_key), value),
                                          align=value_align,
                                          font=font_total_cell,
                                          action=get_select_action(current_area, leg_ids))
                    bg = cc(value / len(existing_x_keys))

                row.add(prt.Row(prt_object,
                                background=bg,
                                border=prt.border(left=1, right=2, bottom=1, colour=sp.DarkGrey)))

            for x_key in x_keys:
                value, leg_ids = values[(x_key, y_key)]
                if dividerdict:
                    tooltip = tooltip_format(x_key,
                                             y_key,
                                             x_key_format(x_key),
                                             y_key_format(y_key),
                                             value,
                                             keyvaluedict[x_key, y_key][0],
                                             dividerdict[x_key, y_key][0])
                    prt_object = value_object_when_divider(tooltip,
                                                           font_normal_cell,
                                                           value,
                                                           keyvaluedict[x_key, y_key][0],
                                                           dividerdict[x_key, y_key][0],
                                                           leg_ids,
                                                           dividerdict[x_key, y_key][1])
                else:
                    prt_object = prt.Text(value_format(value),
                                          tooltip=tooltip_format(x_key, y_key, x_key_format(x_key), y_key_format(y_key), value),
                                          font=font_normal_cell,
                                          align=value_align,
                                          action=get_select_action(current_area, leg_ids))

                row.add(prt.Row(prt_object,
                                background=cc(value),
                                border=prt.border_frame(1, colour=sp.DarkGrey)))


class ColourCalculator(object):

    def __init__(self, max_value, min_value, max_colour=HEATMAP_RED, min_colour=HEATMAP_BLUE, zero_colour=sp.White, gamma=1.0):

        self.maxvalue = my_float(max_value) or 1.0
        self.positive_minvalue = abs(my_float(min_value)) or 1.0
        self.maxcolour_seq = self.code2int_seq(max_colour)
        self.mincolor_seq = self.code2int_seq(min_colour)
        self.zerocolour_seq = self.code2int_seq(zero_colour)
        self.gamma = gamma

    def __call__(self, value):
        if not my_float(value):
            background_colour_seq = self.zerocolour_seq
        else:
            value = my_float(value)
            if value > 0:
                fraction_value = pow((min(value, self.maxvalue)) / self.maxvalue, self.gamma)
                top_colour_seq = self.maxcolour_seq
            else:
                fraction_value = pow((min(abs(value), self.positive_minvalue)) / self.positive_minvalue, self.gamma)
                top_colour_seq = self.mincolor_seq
            background_colour_seq = [int(zcv + fraction_value * (tcv - zcv)) for tcv, zcv in zip(top_colour_seq, self.zerocolour_seq)]

        return self.int_seq2code(background_colour_seq)

    @staticmethod
    def code2int_seq(code):
        return (int(code[1:3], 16), int(code[3:5], 16), int(code[5:7], 16))

    @staticmethod
    def int_seq2code(int_seq):
        return "#%0.2X%0.2X%0.2X" % tuple(int_seq)


class VerticalText(prt.Canvas):

    def __init__(self, *args, **kw):
        self.txt = kw["txt"]
        del kw["txt"]
        prt.Canvas.__init__(self, *args, **kw)

    def draw(self, gc):
        x, y = self.size()
        gc.text(x // 2, y // 2, self.txt, rotate=90,
                font=prt.font(size=7),
                align=prt.CENTER, valign=prt.CENTER)


# Base class for all calibration reports to inherit

class CalibrationReport(prt.Report):

    has_table_view = True
    require_level_duty = False
    critical_rave_param_name = SELECT_METHOD_PARAMETER_NAME
    num_instances = Counter()
    default_variant_key = common.CalibAnalysisVariants.Default.key
    comment = ""

    def __init__(self, *args, **kw):
        super(CalibrationReport, self).__init__(*args, **kw)
        self.num_instances[self.__module__] += 1
        self.warnings = []
        self._my_top_bag_handlers = {}
        self.pconfig = config_per_product.get_config_for_active_product()
        self.add_link_to_rule_details_report_for_rule = None

    def __del__(self):
        self.num_instances[self.__module__] -= 1
        cls = self.__class__
        Errlog.log("\n".join(("CALIBRATION. Log. **********************************************************************",
                              "CALIBRATION. Log. An instance of the report '{}.{}' has been deleted.".format(cls.__module__,
                                                                                                             cls.__name__),
                              "CALIBRATION. Log. *********************************************************************")))

    def store_bag(self):
        self.bag = self.get_top_bag_for_level_and_write_warning_once(mappings.LEVEL_LEG)

    def create(self):
        if self.arg("variant") is None:  # Report instance is ancestor --> set comment.
            CalibrationReport.comment = rave.eval(rave.keyw("report_comment"))[0]

        self.variant = self.arg("variant") or self.default_variant_key

        self.current_context = CuiContextLocator().fetchcurrent()
        self.current_area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        self.current_area_mode = Cui.CuiGetAreaMode(Cui.gpc_info, self.current_area)
        self.comparison_plan_name = compare_plan.ComparisonPlanHandler.get_plan_name(reset_cache_if_needed=True)

        self.define_header()
        self.define_footer()

    def get_top_bag_for_level_and_write_warning_once(self, level_name):
        if level_name not in self._my_top_bag_handlers:
            self._my_top_bag_handlers[level_name] = self.pconfig.levels_dict[level_name].bag_handler_cls()
            if self._my_top_bag_handlers[level_name].warning:
                self.add_warning_text(self._my_top_bag_handlers[level_name].warning)
        return self._my_top_bag_handlers[level_name].bag

    def get_bags_for_cri_and_write_warning_once(self, rule_item):
        top_bag = self.get_top_bag_for_level_and_write_warning_once(rule_item.rule_level)
        my_bags = common.get_atomic_iterator_for_level(top_bag, rule_item.rule_level)() if top_bag else []
        return my_bags

    @classmethod
    def critical_rave_parameter_exist(cls):
        try:
            rave.param(cls.critical_rave_param_name)
            return True
        except rave.RaveError:
            return False

    def test_if_report_can_be_generated_and_store_bag(self):

        self.skip_reason = None

        if self.require_level_duty and self.pconfig.level_duty_name is None:
            self.add_warning_text(MSGR("Configuration error. This report requires a registered duty level"))
            self.skip_reason = "MISSING_LEVEL"
            return

        if not self.critical_rave_parameter_exist():
            self.add_warning_text(MSGR("Definitions needed for the report are missing in the loaded rule set"))
            self.skip_reason = "INCORRECT_RULE_SET"
            return

        if basics.no_or_empty_local_plan():
            self.add_warning_text(MSGR("No or empty local plan"))
            self.skip_reason = "NO_OR_EMPTY_LOCAL_PLAN"
            return

        if self.current_area_mode == Cui.LegSetMode:
            self.add_warning_text(MSGR("The report can't be generated from the leg sets window"))
            self.skip_reason = "LEG_SETS_AS_SOURCE"
            return

        self.store_bag()
        if not self.bag:
            self.skip_reason = "NO_SELECTED_OBJECT"
            return

        if compare_plan.bag_is_comparison_plan_bag(self.bag):
            self.add_warning_text(MSGR("Can't run report on comparison plan legs"))
            self.skip_reason = "COMPARISON_PLAN_LEGS"
            return

    def add_warnings_and_links(self):
        self._add_links()
        self.add_warnings_to_header()

    def _add_links(self):
        variant = self.variant
        same_view = "TABLE" if self.arg('show') == "TABLE" else "OVERVIEW"
        focus_rule_name = self.arg('rule') or ""

        buf = Variable()
        Cui.CuiGetAreaModeString({"WRAPPER": Cui.CUI_WRAPPER_NO_EXCEPTION}, Cui.gpc_info, self.current_area, buf)
        source_info = prt.Text(MSGR("Window {}   ({})").format(self.current_area + 1, buf.value or "-"))

        regenerate = prt.Text(MSGR("Refresh"),
                              font=LINK_FONT,
                              link=prt.link(self.__module__,
                                            {'variant': variant, 'show': same_view, 'rule': focus_rule_name}))

        close_all = self.get_close_all_prt_object()

        if self.skip_reason in ("NO_OR_EMPTY_LOCAL_PLAN", "INCORRECT_RULE_SET", "MISSING_LEVEL"):
            self.add(prt.Isolate(prt.Column(prt.Row(regenerate, close_all, source_info),
                                            width=200)))
            return

        if focus_rule_name:
            cri = self.cr.all_rules_dict.get(focus_rule_name, None)
            if not cri:
                self.add_warning_text(MSGR("The focus rule '{}' does not exist").format(focus_rule_name))
                focus_rule_label = focus_rule_name
            else:
                focus_rule_label = cri.rule_label

            self.add(prt.Isolate(prt.Row(prt.Text(MSGR("Focus rule:")),
                                         prt.Text(focus_rule_label, font=BOLD, height=20),
                                         prt.Text("      "),
                                         prt.Text(MSGR("Skip"), font=LINK_FONT,
                                                  link=prt.link(self.__module__, {'variant': variant, 'show': same_view})))))

        regenerate_nw = prt.Text(MSGR("New") + " ",
                                 font=LINK_FONT,
                                 action=prt.action(lambda m, a: rg.display_prt_report(source=m,
                                                                                      area=a,
                                                                                      scope="window",
                                                                                      rpt_args={'variant': variant,
                                                                                                'show': same_view,
                                                                                                'rule': focus_rule_name}),
                                                   (self.__module__, self.current_area)))

        if self.has_table_view:
            other_view = "TABLE" if self.arg('show') != "TABLE" else "OVERVIEW"
            other_view_str = MSGR("Table") if self.arg('show') != "TABLE" else MSGR("Overview")
            other = prt.Text(other_view_str,
                             font=LINK_FONT,
                             tooltip=MSGR("Generate the {} View of this report.").format(other_view_str),
                             action=prt.action(lambda m, a: rg.display_prt_report(source=m,
                                                                                  area=a,
                                                                                  scope="window",
                                                                                  rpt_args={'variant': variant,
                                                                                            'show': other_view,
                                                                                            'rule': focus_rule_name}),
                                               (self.__module__, self.current_area)))
        else:
            other = prt.Text("")

        if self.add_link_to_rule_details_report_for_rule:
            details = self.get_report_rule_details_link(self.add_link_to_rule_details_report_for_rule)
        else:
            details = prt.Text("")

        select_all = prt.Text(MSGR("Select all legs"),
                              font=LINK_FONT,
                              action=prt.action(Cui.CuiMarkAllLegs, (Cui.gpc_info, self.current_area, "window")))

        if not self.skip_reason and compare_plan.ComparisonPlanHandler.a_plan_is_loaded():
            comp_trips = prt.Text(MSGR("Comparison trips"),
                                  font=LINK_FONT,
                                  action=prt.action(show_comparison_trips, (self.current_area,)))
        else:
            comp_trips = prt.Text("")

        # Note:
        # * "get_form_handler" must be a static method for adequate garbage collection.
        # * The method must be called by the registered action to avoid problems after reload.
        my_get_form_handler = self.get_form_handler
        parameters = prt.Text(MSGR("Parameters") + " ",
                              action=prt.action(lambda: my_get_form_handler(variant).show_form(variant)),
                              font=LINK_FONT)

        buttons = (parameters, regenerate, regenerate_nw, other, details, select_all, comp_trips, close_all, source_info)

        self.add(prt.Isolate(prt.Column(prt.Row(*buttons), "", width=600)))

    def get_close_all_prt_object(self):
        close_all_f = self.close_all
        return prt.Text(MSGR("Close all"),
                        tooltip=MSGR("Close all Calibration reports and forms"),
                        action=prt.action(close_all_f),
                        font=LINK_FONT)

    @classmethod
    def close_all(cls):
        from carmusr.calibration.util import report_forms
        report_forms.close_and_free_all_forms()

        b_type = "BROWSER"
        for b_id, num_instances in six.iteritems(cls.num_instances):
            close_dict = {"ID": b_id, "TYPE": b_type, "button": "CLOSE"}
            for _ in range(num_instances):
                Cui.CuiBypassWrapper("CuiProcessInteraction", Cui.CuiProcessInteraction, (close_dict, b_type, b_id))

    def get_report_rule_details_link(self, rule_key):
        variant = self.variant
        return prt.Text(MSGR("Details"),
                        tooltip=MSGR("Generate the report '{}' with the analysed rule as focus rule.").format(CalibReports.RD.title),
                        font=LINK_FONT,
                        action=prt.action(lambda a: rg.display_prt_report(source="calibration.calibration_rule_details",
                                                                          area=a,
                                                                          scope="window",
                                                                          rpt_args={'variant': variant,
                                                                                    'rule': rule_key}),
                                          (self.current_area,)))

    def define_header(self):
        '''
        Defines the header for calibration reports
        ------------------------------------------------------------------
        Calibration <REPORT TITLE>                          <CLIENT LOGO>
        Planning Period:     01Nov2003 - 02Dec2003
        Rule Set Name:       default_jcp  (Nov03_dated/TRAINING_CAMP_JCP)
        Plan:                TT / BASIC_JCP / Actual / Planned
        Comparison Plan:     TT / BASIC_JCP / Actual / Flown
        Comment*:            This is a report comment
        Warning[s]*:         2 trips were ignored
        ------------------------------------------------------------------
        '''

        ctx_bag = rave.context('default_context').bag()

        h1 = prt.Isolate(prt.Row(prt.Text("Calibration",
                                          padding=prt.padding(right=5, left=2, bottom=2, top=2),
                                          font=prt.font(size=13, weight=prt.BOLD),
                                          valign=prt.CENTER,
                                          colour=sp.JeppesenBlue),
                                 prt.Text(self.get_header_text(),
                                          font=prt.font(size=14, weight=prt.BOLD),
                                          colour=sp.Black)),
                         colspan=2)

        try:
            pp_start, pp_end = rave.eval(ctx_bag,
                                         mappings.rave_variable_for_planning_period_start,
                                         mappings.rave_variable_for_planning_period_end)
        except rave.RaveError:
            pp_start = pp_end = None

        if pp_start:
            pp_text = '%s - %s' % (de.abstime2gui_date_string(pp_start),
                                   de.abstime2gui_date_string(pp_end))
        else:
            pp_text = MSGR('N/A')

        h2 = prt.Row(prt.Text(MSGR('Planning Period: '), font=BOLD),
                     prt.Text(pp_text))

        h3 = prt.Row(prt.Text(MSGR('Rule Set Name: '), font=BOLD),
                     prt.Text('%s   (%s)' % (ctx_bag.rule_set_name(),
                                             ctx_bag.map_parameter_set_name())))

        try:
            plan_name = plan.get_current_sub_plan().get_file_path()
            plan_name = ' / '.join(plan_name.split('/'))
        except ValueError:
            plan_name = MSGR("No plan loaded")

        h4 = prt.Row(prt.Text(MSGR('Plan: '), font=BOLD),
                     prt.Text(plan_name))

        if hasattr(self, "comparison_plan_name"):
            h5 = prt.Row(prt.Text(MSGR('Comparison Plan: '), font=BOLD),
                         prt.Text(self.comparison_plan_name or "-"))
        else:
            h5 = prt.Row()

        if self.comment:
            h6 = prt.Row(prt.Text(MSGR('Comment: '), font=BOLD),
                         prt.Text(self.comment))
        else:
            h6 = prt.Row()

        self.warnings_row_in_header = prt.Row()

        header = prt.Column(prt.Row(prt.Isolate(prt.Column(h1, h2, h3, h4, h5, h6, self.warnings_row_in_header,
                                                           font=prt.font(face=prt.SANSSERIF, size=8),
                                                           colour=sp.VeryDarkGrey)),
                                    prt.Image(mappings.image_file_name_client_logo,
                                              align=prt.RIGHT),
                                    border=prt.border(bottom=1)),
                            prt.Text(''))
        self.add(prt.Header(header,
                            width=self.page_width()))

    def add_warning_text(self, text):
        self.warnings.append(text)

    def add_warnings_to_header(self):
        if self.warnings:
            warning_desc = prt.Text(MSGR("Warning:") if len(self.warnings) == 1 else MSGR("Warnings:"),
                                    font=BOLD)
            warning_texts = prt.Column(*tuple(self.warnings),
                                       colour=sp.BrightRed)
            self.warnings_row_in_header.add(warning_desc)
            self.warnings_row_in_header.add(warning_texts)
        del self.warnings  # To get an exception if warnings are added or used after calling this method.

    def define_footer(self):

        c1 = prt.Column(
            prt.Image('examples/jeppesen_simple_logo.jpg',
                      colspan=2,
                      align=prt.RIGHT,
                      border=prt.border(bottom=1)),

            prt.Row(prt.Text(MSGR('Printed '),
                             Dates.FDatInt2DateTime(Dates.FDatUnix2CarmTimeLT(time.time())),
                             MSGR(' by '), Names.username()),
                    prt.Text(prt.Crossref('current_page'), ' (',
                             prt.Crossref('last_page'), ')',
                             align=prt.RIGHT),
                    font=prt.font(face=prt.SANSSERIF, size=8),
                    colour=sp.VeryDarkGrey))

        self.add(prt.Footer(c1, width=self.page_width()))


#########################################
# Misc
#########################################

class BinHandler(object):

    def __init__(self, start_at=1, bin_size_1=1, number_of_bins_with_size_1=10, bin_size_2=10):
        self.start_at = start_at
        self.bin_size_1 = bin_size_1
        self.number_of_bins_with_size_1 = number_of_bins_with_size_1
        self.bin_size_2 = bin_size_2
        self.max_for_bin_size_1 = self.start_at + self.bin_size_1 * self.number_of_bins_with_size_1

    def value2binnum(self, v):
        if v <= self.max_for_bin_size_1:
            return (v - self.start_at) // self.bin_size_1
        return self.number_of_bins_with_size_1 + (v - self.max_for_bin_size_1) // self.bin_size_2

    def binnum2interval_string(self, b):
        if b < self.number_of_bins_with_size_1:
            start = b * self.bin_size_1 + self.start_at
            end = start + self.bin_size_1 - 1
            if start == end:
                return str(start)
            return "%d - %d" % (start, end)
        start = self.max_for_bin_size_1 + (b - self.number_of_bins_with_size_1) * self.bin_size_2
        end = start + self.bin_size_2 - 1
        if start == end:
            return str(start)
        return "%d - %d" % (start, end)


def my_float(v):
    """
    Needed to survive RelTime. :-(
    """
    try:
        return float(v)
    except TypeError:
        return float(v.getRep())


def show_comparison_trips(area):
    Cui.CuiSetCurrentArea(Cui.gpc_info, area)
    if not Cui.CuiAnyMarkedSegment(Cui.gpc_info, area):
        return

    tbh = bag_handler.MarkedLegsMain()
    num_marked_legs = sum(1 for _ in tbh.bag.atom_set())
    if num_marked_legs > 100:
        if not Gui.GuiYesNo(__name__, MSGR("There are many (%s) selected legs in the window.\nDo you really want to continue?") % num_marked_legs):
            return

    Cui.CuiShowLeg(Cui.gpc_info, area, "marked", Cui.CrrMode, Cui.CuiSortNone, 0, 0, 0, 0, 3)
    # To allow undo
    Cui.CuiExecuteFunction('PythonEvalExpr("0")',
                           MSGR("Show comparison plan trips"),
                           Gui.POT_REDO,
                           Gui.OPA_OPAQUE)

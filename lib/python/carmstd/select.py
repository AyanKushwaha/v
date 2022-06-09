"""
Functions for filtering and selecting in Studio.
"""

import Cui
import Localization as L
import Gui
import carmensystems.rave.api as rave

from carmstd import area


def show_and_mark_legs(current_area, leg_identifiers):
    """
    * Shows the chains containing the legs in the leg_identifier collection in
      the opposite area to current_area. The chains can be of any kind (trip, rosters....),
    * Changes the leg marking to just mark the legs in the leg_identifier collection.
    * Typically used as action in reports.
    """
    # To allow undo
    Cui.CuiExecuteFunction('PythonEvalExpr("0")',
                           L.MSGR("Select and filter legs"),
                           Gui.POT_REDO,
                           Gui.OPA_OPAQUE)
    opposite_area = area.get_opposite_area(current_area)

    try:
        display_given_objects(leg_identifiers,
                              opposite_area,
                              area.get_area_mode(current_area),
                              Cui.LegMode)
    except Cui.CancelException:
        Gui.GuiMessage(L.MSGR("Impossible, you have probably changed the plan or the window content."))

    Cui.CuiUnmarkAllLegs(Cui.gpc_info, current_area, "window")
    Cui.CuiUnmarkAllLegs(Cui.gpc_info, opposite_area, "window")

    for lid in leg_identifiers:
        Cui.CuiSetSelectionObject(Cui.gpc_info, opposite_area, Cui.LegMode, str(lid))
        Cui.CuiMarkLegs(Cui.gpc_info, opposite_area, "object")


def show_trips(crr_identifiers, area, use_list_order=False):
    '''Shows the given list of trips in the specified area and creates a Studio state. To be used from Reports.

    Wraps :carmsys_man:'CuiDisplayGivenObjects'

    Examples
    --------

    .. python::
        trips_bag = ... # Some definition for obtaining trips from Trips window
        for trip_bag in trips_bag:
            interesting_trips = list()
            if interesting_property(trip_bag): # Some property implemented in python
                interesting_trips.append(trip_bag.crr_identifier())
        select.show_trips(interesting_trips, Cui.CuiArea0)

    :param crr_identifiers: A list of trip identifiers
                            (as given by the crr_identifier keyword).
    :type crr_identifiers: 'list' of strings or integers
    :param area: The area in which to show the given trips.
    :type area: :carmsys_man:'CuiAreaId'
    :param use_list_order: Whether to show trips in the order given in
                           the list. Otherwise, use default order of
                           window.
    :type use_list_order: 'bool'
    '''

    Cui.CuiExecuteFunction('PythonEvalExpr("0")',
                           L.MSGR("Show Trips"),
                           Gui.POT_REDO,
                           Gui.OPA_OPAQUE)

    display_given_objects(crr_identifiers,
                          area,
                          Cui.CrrMode,
                          Cui.CrrMode,
                          use_list_order)


def show_crew(crew_identifiers, area, use_list_order=False):
    '''Shows the given list of crew in the specified area and creates a Studio state. To be used from Reports.

    Wraps :carmsys_man:'CuiDisplayGivenObjects'

    Examples
    --------

    .. python::
        crews_bag = ... # Some definition for obtaining crew from Roster window
        for crew_bag in crews_bag:
            interesting_crews = list()
            if interesting_property(crew_bag): # Some property implemented in python
                interesting_crews.append(crew_bag.crr_identifier())
        select.show_crews(interesting_crews, Cui.CuiArea0)

    :param crew_identifiers: A list of crew identifiers
                            (as given by the crr_identifier keyword).
    :type crew_identifiers: 'list' of strings or integers
    :param area: The area in which to show the given crew.
    :type area: :carmsys_man:'CuiAreaId'
    :param use_list_order: Whether to show crew in the order given in
                           the list. Otherwise, use default order of
                           window.
    :type use_list_order: 'bool'
    '''
    Cui.CuiExecuteFunction('PythonEvalExpr("0")',
                           L.MSGR("Show Crew"),
                           Gui.POT_REDO,
                           Gui.OPA_OPAQUE)

    display_given_objects(crew_identifiers,
                          area,
                          Cui.CrewMode,
                          Cui.CrewMode,
                          use_list_order)


def display_given_objects(ids,
                          area,
                          area_type,
                          obj_type,
                          use_list_order=False):

    '''
    Convenience wrapper around CuiDisplayGivenObjects
    '''

    # Since crr_identifier returns an int, we do a little
    # conversion here first for convenience.
    ids = [str(_id) for _id in ids]

    if use_list_order:
        sort_method = Cui.CuiSortNone
    else:
        sort_method = Cui.CuiSortDefault

    Cui.CuiDisplayGivenObjects(Cui.gpc_info,
                               area,
                               area_type,
                               obj_type,
                               ids,
                               0,  # Flags argument is not used but necessary
                               Cui.Replace,
                               sort_method)


def filter_by_rave_expression_cmd(rave_expr,
                                  studio_area=Cui.CuiWhichArea,
                                  rave_result="T",
                                  filter_type='',
                                  princip="ANY",
                                  method="REPLACE",
                                  mark="NONE"):
    """
    Running 'Filter by rave expression' through PythonEvalExpr to make sure that we are able to undo the selection.
    See filter_by_rave_expression. Needed in e.g. in callbacks from PRT.
    """

    if len(rave_expr) > 99:
        raise Exception('Expression too long')

    filter_command = 'carmstd.select.filter_by_rave_expression(%s,%s,%s,%s,%s,%s,%s)' % (repr(rave_expr),
                                                                                         repr(studio_area),
                                                                                         repr(rave_result),
                                                                                         repr(filter_type),
                                                                                         repr(princip),
                                                                                         repr(method),
                                                                                         repr(mark))

    Cui.CuiExecuteFunction('PythonEvalExpr("%s")' % (filter_command),
                           "FilterByExpression",
                           Gui.POT_REDO,
                           Gui.OPA_OPAQUE)


def add_filter_by_rave_expression(*args, **kw):
    filter_by_rave_expression(method="ADD", *args, **kw)


def sub_filter_by_rave_expression(*args, **kw):
    filter_by_rave_expression(method="SUBFILTER", *args, **kw)


def select_filter_by_rave_expression(*args, **kw):
    filter_by_rave_expression(mark='Trip', *args, **kw)


def filter_by_rave_expression(rave_expr,
                              studio_area=Cui.CuiWhichArea,
                              rave_result="T",
                              filter_type='',
                              princip="ANY",
                              method="REPLACE",
                              mark="NONE"):
    """
    Filter by rave expression.

    Examples
    --------

    .. python::
        # Shows all trips whose home base is GOT in the first window (area).
        >>> filter_by_rave_expression('trip.%homebase% = "GOT"',
                                      Cui.CuiArea0, filter_type = 'CrrFilter')

        # Sub-selects all trips in the first window whose home base is GOT.
        >>> filter_by_rave_expression('trip.%homebase% = "GOT"',
                                      Cui.CuiArea0, method = 'SUBFILTER')

    :param rave_expr: The Rave expression to filter by (must include %)
                      Rave expression should include %-signs. Must be less
                      than 100 characters long.
    :type rave_expr: 'str'
    :param studio_area: Studio area where the filter should be applied.
    :type studio_area: :carmsys_man:'CuiAreaId'
    :param rave_result: The result of the expression. Default value is 'True'
    :type rave_result: 'str'
    :param filter_type:  What kind of filter type to use for filter. Decides what \
                        filter form that will be used. \
                        'LegFilter','RtdFilter','CrrFilter','CrewFilter',\
                        'LegSet-Filter', 'ACRotFilter' or 'SubCrrFilter'. Empty string
                        sets the filter type to the default for the area.
    :type filter_type: 'str'
    :param princip: Filter principle to use.'ANY' or 'ALL'
    :type princip: 'str'
    :param method: Filter method to use.'ADD','SUBFILTER','REPLACE'
    :type method: 'str'
    :param mark: Specifies if the selected level should be marked. E.g. TRIP
    :type mark: 'str'
    """

    if len(rave_expr) > 99:
        raise Exception('Expression too long')

    rave_expr = rave_expr.replace('_@_', '"')
    byp = [('FORM', 'filterByRaveExpression'),
           ('DEFAULT', ''),
           ('FILTER_PRINCIP', L.bl_msgr(princip)),
           ('FILTER_METHOD', L.bl_msgr(method)),
           ('FILTER_MARK', L.bl_msgr(mark)),
           ('CRC_VARIABLE_0', rave_expr),
           ('CRC_VALUE_0', rave_result)]

    # Run the filter command.
    Cui.CuiFilterObjects(byp, Cui.gpc_info,
                         studio_area, filter_type,
                         'filterByRaveExpression', 0)


def select_by_rave_expression_cmd(rave_expr,
                                  studio_area,
                                  rave_result="T",
                                  princip="ANY",
                                  mark="LEG"):
    """
    Running 'Select by rave expression' through PythonEvalExpr to make sure that we are able to undo the selection.
    See select_by_rave_expression. Needed in e.g. in call backs from PRT.
    """

    if len(rave_expr) > 99:
        raise Exception('Expression too long')

    selection_command = 'carmstd.select.select_by_rave_expression(%s,%s,%s,%s,%s)' % (repr(rave_expr),
                                                                                      repr(studio_area),
                                                                                      repr(rave_result),
                                                                                      repr(princip),
                                                                                      repr(mark))

    Cui.CuiExecuteFunction('PythonEvalExpr("%s")' % (selection_command),
                           "form_select_by_rave_expr",
                           Gui.POT_REDO,
                           Gui.OPA_OPAQUE)


def select_by_rave_expression(rave_expr,
                              studio_area=Cui.CuiWhichArea,
                              rave_result="T",
                              princip="ANY",
                              mark="LEG"):
    """
    Select by rave expression.

    Examples
    --------

    .. python::
        # The following are equivalent and will select all
        # legs in all trips which has GOT as home base:
        >>> select_by_rave_expression('trip.%homebase% = "GOT"', Cui.CuiArea0)
        >>> select_by_rave_expression('trip.%homebase%', Cui.CuiArea0, 'GOT')

    :param rave_expr: Rave expression. Either a rave variable or rave expression.
                      Rave expression should include %-signs. Must be less
                      than 100 characters long.
    :type rave_expr: 'str'
    :param studio_area: Studio area where the filter should be applied.
    :type studio_area: :carmsys_man:'CuiAreaId'
    :param rave_result: The result of the expression. Default value is 'True'
    :type rave_result: 'str'
    :param princip: Filter principle to use.'ANY' or 'ALL'. Default value i ANY.
    :type princip: 'str'
    :param mark: Specifies what level that should be selected. E.g. LEG, Duty, Trip. Default value is LEG
    :type mark: 'str'
    """

    if len(rave_expr) > 99:
        raise Exception('Expression too long')

    rave_expr = rave_expr.replace('_@_', '"')
    byp = [('FORM', 'form_select_by_rave_expr'),
           ('DEFAULT', ''),
           ('FILTER_PRINCIP', L.bl_msgr(princip)),
           ('FILTER_MARK', L.bl_msgr(mark))]

    if type(rave_expr) == str:
        byp.append(('CRC_VARIABLE_0', rave_expr))
        byp.append(('CRC_VALUE_0', rave_result))
    else:
        for ix, (r_expr, r_result) in enumerate(zip(rave_expr, rave_result)):
            byp.append(('CRC_VARIABLE_%s' % ix, r_expr))
            byp.append(('CRC_VALUE_%s' % ix, r_result))

    # Run the command.
    Cui.CuiMarkWithFilter(byp, Cui.gpc_info,
                          studio_area, None,
                          'form_select_by_rave_expr')


def select_crew_by_rave_expression(rave_expr, rave_result="T"):
    select_by_rave_expression(rave_expr,
                              rave_result=rave_result,
                              mark="CREW")


def sort_by_rave_expression(rave_expr,
                            studio_area=Cui.CuiWhichArea):
    """
    Sort by rave expression.
    """

    Cui.CuiSortArea(Cui.gpc_info,
                    studio_area,
                    Cui.CuiSortRaveExpression,
                    rave_expr)


def sort_by_rave_expression_cmd(rave_expr,
                                studio_area=Cui.CuiWhichArea):
    """
    Sort by rave expression (wrapped in CuiExecuteFunction).
    """

    python_cmd = 'carmstd.select.sort_by_rave_expression(%s,%s)' % (repr(rave_expr),
                                                                    repr(studio_area))

    csl_cmd = 'PythonEvalExpr("%s")' % python_cmd.replace('"', '\\"')

    Cui.CuiExecuteFunction('PythonEvalExpr("%s")' % csl_cmd,
                           "form_select_by_rave_expr",
                           Gui.POT_REDO,
                           Gui.OPA_OPAQUE)


def show_opt_input():
    """
    Displays the input as was given to the optimizer. Behaviour depends
    on whether a rostering or pairing rule set is loaded.
    """

    if not area.area_exists(Cui.CuiArea0):
        area.create_new_area()
    if not area.area_exists(Cui.CuiArea1):
        area.create_new_area()

    # Instead of looking at the ruleset type, it would probably be better
    # to check whether the loaded solution was generated by APC or Matador,
    # but I couldn't find a simple way of doing that.
    if rave.eval('fundamental.%is_rostering_ruleset%')[0]:
        show_rostering_opt_input()
    else:
        show_pairing_opt_input()


def show_rostering_opt_input():
    """
    Displays the roster optimizer input in window 0 and
    the trip optimizer input in window 1.
    """
    Cui.CuiDisplayFilteredObjects(Cui.gpc_info, Cui.CuiArea0,
                                  Cui.CrewMode, "crew_apc_tag")
    Cui.CuiDisplayFilteredObjects(Cui.gpc_info, Cui.CuiArea1,
                                  Cui.CrrMode, "apc_crr_tag")


def show_pairing_opt_input():
    """
    Displays the trip optimizer input in window 0 and
    the duty optimizer input in window 1.
    """
    Cui.CuiDisplayFilteredObjects(Cui.gpc_info, Cui.CuiArea0,
                                  Cui.CrrMode, "apc_crr_tag")
    Cui.CuiDisplayFilteredObjects(Cui.gpc_info, Cui.CuiArea1,
                                  Cui.RtdMode, "apc_crr_tag")

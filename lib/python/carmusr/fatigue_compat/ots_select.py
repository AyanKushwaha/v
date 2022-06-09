"""
Functions for filtering and selecting in Studio.
"""

import Cui
import Localization as L
import Gui
import carmensystems.rave.api as rave


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

    filter_command = 'carmusr.fatigue_compat.ots_select.filter_by_rave_expression(%s,%s,%s,%s,%s,%s,%s)' % (repr(rave_expr),
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
    :type rave_expr: `str`
    :param studio_area: Studio area where the filter should be applied.
    :type studio_area: :carmsys_man:`CuiAreaId`
    :param rave_result: The result of the expression. Default value is 'True'
    :type rave_result: `str`
    :param filter_type:  What kind of filter type to use for filter. Decides what \
                        filter form that will be used. \
                        'LegFilter','RtdFilter','CrrFilter','CrewFilter',\
                        'LegSet-Filter', 'ACRotFilter' or 'SubCrrFilter'. Empty string
                        sets the filter type to the default for the area.
    :type filter_type: `str`
    :param princip: Filter principle to use.'ANY' or 'ALL'
    :type princip: `str`
    :param method: Filter method to use.'ADD','SUBFILTER','REPLACE'
    :type method: `str`
    :param mark: Specifies if the selected level should be marked. E.g. TRIP
    :type mark: `str`
    """

    if len(rave_expr) > 99:
        raise Exception('Expression too long')

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




'''
Miscellaneous functions extending the :carmsys_man:'Cui' library.

:author: Petter Remen <petter.remen@jeppesen.com>
:since: 12 Mar, 2010
'''

import types

from carmensystems.mave.core import ETable
import Cui
import Gui
import Csl

from carmstd import etab_ext


def set_message_area(msg):
    """
    Displays a message in the message area (also called the prompt area).
    """

    csl = Csl.Csl()
    csl.evalExpr('csl_prompt("%s")' % msg)


def set_trip_names(names_dict):
    '''
    Sets trip names.
    :param names_dict: A map from crr_identifiers to trip names.
    '''
    Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiScriptBuffer,
                          Cui.CrrMode, Cui.CuiShowAll)
    for crr_identifier, trip_name in names_dict.items():
        Cui.CuiSetSelectionObject(Cui.gpc_info, Cui.CuiScriptBuffer,
                                  Cui.CrrMode, str(crr_identifier))
        Cui.CuiSetCrrName(Cui.gpc_info, Cui.CuiScriptBuffer, str(trip_name))

    Cui.CuiClearArea(Cui.gpc_info, Cui.CuiScriptBuffer)
    refresh()


def reload_table(table, do_save=True, do_refresh=True, removeSp=False):
    """
    Reloads a table in Studio.

    :param table: Either the path to a table
        (see 'carmstd.etab_ext.get_existing_absolute_etab_path' for more info) or an ETable object.
    :type table: String or carmensystems.mave.core.ETable

    :param do_save: Whether to save the ETable object to disk before reloading.
    :type do_save: Boolean

    :param do_refresh: Whether to perform a refresh() after reloading the table.
    :type do_refresh: Boolean
    """

    if isinstance(table, types.StringTypes):
        _reload_table_by_path(table, removeSp)
    elif isinstance(table, ETable):
        if do_save:
            table.save()
        _reload_table_by_path(table.getPath(), removeSp)

    if do_refresh:
        refresh()


def _reload_table_by_path(etab_path, removeSp=False):
    if not etab_path:
        raise ValueError('Path is empty')

    if etab_path[0] == '/':
        abs_etab_path = etab_path
    else:
        try:
            abs_etab_path = etab_ext.get_existing_absolute_etab_path(etab_path)
        except etab_ext.EtableNotFoundException:
            raise ValueError('Table does not exist: %s' % etab_path)

    rel_etab_path = etab_ext.get_relative_path(abs_etab_path)

    if removeSp and rel_etab_path.startswith('SpLocal/'):
        rel_etab_path = rel_etab_path[8:]

    Cui.CuiReloadTable(rel_etab_path)


def recalculate_crew_need():
    csl = Csl.Csl()
    csl.evalExpr('gpc_reset_required_cc()')


def refresh(recalc_crew_need=True):
    '''Refreshes the GUI.

    Typically you would call this after editing an external
    table (make sure to do a :carmsys_man:'CuiReloadTable'
    first!) or changing a parameter from within Python.

    This function will also recalculate crew need if the parameter says so
    (don't do it too often - performance!)
    '''

    Gui.GuiCallListener(Gui.RefreshListener,
                        "parametersChanged")

    # The Assign Value in the Tool-bar listens to ActionEvents
    Gui.GuiCallListener(Gui.ActionListener)

    if recalc_crew_need:
        # Update crew need
        recalculate_crew_need()

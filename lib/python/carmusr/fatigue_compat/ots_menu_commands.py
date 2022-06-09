"""
 menu_commands
 This file contains some of the functions that can be called from the menu
 source files in $CARMUSR/.

 The module is imported into the __main__ module at start up of Studio
 and functions should be called using "PythonEvalExpr(menu_commands.<function>)".

@date: 20090701
@org: Jeppesen Systems AB

"""

import traceback
import Cui
import Errlog
import Localization as L
import carmensystems.rave.api as r  # @UnusedImport
from __main__ import exception as CarmException  # @UnresolvedImport

#import carmstd.select as select
import carmusr.fatigue_compat.ots_select as select


def filter_by_expr(rave_expression, selection="NONE"):
    """
    Functions that performs a filter in the current Studio area
    The filter is defined by a rave expression.
    E.g. 'trip.%is_domestic% and trip.%num_legs% >3'

    @param rave_expression: Rave expression. Either a rave variable or rave expression.\
                      Rave expression should include %-signs.
    @type rave_expression: String
    @param selection: Specifies if the selected level should be marked. E.g. TRIP, Duty, Leg
    @type selection: String
    """
    try:
        window = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        select.filter_by_rave_expression_cmd(rave_expression, window, "True", "", "ANY", "REPLACE", selection)

    except CarmException:
        Errlog.set_user_message(L.MSGR("Could not perform filter"))
        traceback.print_exc()




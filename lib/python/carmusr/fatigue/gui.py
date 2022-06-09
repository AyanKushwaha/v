"""
Contains GUI functions for fatigue implementation in Studio.
Adds dynamic filtering on right-click general menu.

@author: Angelo Stroppa
@organization: Jeppesen Systems AB
@since: 27Oct2010
"""

import carmensystems.rave.api as rave

#from carmstd.gui_ext import add_menu_item
from carmusr.fatigue_compat.ots_gui_ext import add_menu_item
import carmusr.fatigue_compat.ots_menu_commands

def dynamic_filter_alertness_menu():
    for ix in range(1, 5):
        param_variable = 'studio_fatigue.%%alertness_marker_%d%%' % ix
        param_value, = rave.eval(param_variable)
        filter_variable = 'studio_fatigue.%%alertness_less_than_marker_%d%%' % ix
        add_menu_item(parent_menu='FilterAlertnessValues',
                      title='Less than %s' % param_value,
                      python_action="carmusr.fatigue_compat.ots_menu_commands.filter_by_expr('%s')" % filter_variable)

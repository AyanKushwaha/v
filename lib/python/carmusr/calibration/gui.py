'''
Created on 14 Aug 2017

@author: danielr
'''

import carmensystems.rave.api as rave
from Localization import MSGR
import MenuState

from carmusr import dynamic_menus

DynamicFilterMenuItems = dynamic_menus.DynamicFilterMenuItems
DynamicFilterMenuItemRave = dynamic_menus.DynamicFilterMenuItemRave
DynamicFilterMenuItemTitle = dynamic_menus.DynamicFilterMenuItemTitle
DynamicFilterMenuItemSeparator = dynamic_menus.DynamicFilterMenuItemSeparator


# Define menu state

class CalibrationAvailable(MenuState.MenuState):

    def isActive(self):
        try:
            rave.eval('calibration.%sensitivity_index_level_1%')[0]
            return True
        except rave.RaveError:
            return False


CalibrationAvailable(["CalibrationAvailable"], MenuState.ACTION_EVENT)


class CalibrationLookbackAvailable(MenuState.MenuState):

    def isActive(self):
        try:
            rave.eval('calibration_lookback.%times_to_use_in_specified_rules%')[0]
            return True
        except rave.RaveError:
            return False


CalibrationLookbackAvailable(["CalibrationLookbackAvailable"], MenuState.ACTION_EVENT)


class FilterCalibrationLookbackMenu(DynamicFilterMenuItems):

    def _get_items(self):
        return [DynamicFilterMenuItemRave(MSGR('NOP Leg'), "not_operating", filter_type="CrrFilter"),
                DynamicFilterMenuItemRave(MSGR('Overlap with Next Leg'), "calibration_move_mappings.%overlap%", filter_type="CrrFilter"),
                DynamicFilterMenuItemRave(MSGR('Implausible Connection'), "calibration_mappings.%leg_implausible_connection%", filter_type="CrrFilter"),
                DynamicFilterMenuItemRave(MSGR('Delay Causing Duty Changes'), "calibration_move_mappings.%leg_causing_duty_changes%", filter_type="CrrFilter"),
                DynamicFilterMenuItemSeparator(),
                DynamicFilterMenuItemRave(MSGR('Any Issue Above'), "calibration_move_mappings.%leg_with_lookback_issue%", filter_type="CrrFilter"),
                DynamicFilterMenuItemSeparator(),
                DynamicFilterMenuItemRave(MSGR('Has Delay Code of Interest'), "studio_calibration.%has_delay_code_of_interest%", filter_type="CrrFilter"),
                DynamicFilterMenuItemRave(MSGR('Next Leg Has Delay Code of Interest'), "studio_calibration.%next_leg_has_delay_code_of_interest%", filter_type="CrrFilter")]


class FilterCalibrationHistoryMenu(DynamicFilterMenuItems):

    def _get_items(self):
        return [DynamicFilterMenuItemRave(MSGR('Too Few Matched Flights for Arrival Deviations'), "studio_calibration.%too_few_arr_dev_matches%", filter_type="CrrFilter"),
                DynamicFilterMenuItemRave(MSGR('Too Few Matched Flights for Turnout Changes'),
                                          "studio_calibration.%too_few_turnout_changes_matches%", filter_type="CrrFilter")]


class FilterSensitivityIndexMenu(DynamicFilterMenuItems):

    def _get_items(self):
        items = [DynamicFilterMenuItemTitle(MSGR("Duty Sensitivity Index")),
                 DynamicFilterMenuItemSeparator()]

        for ix in xrange(1, 5):
            param_variable = 'calibration.%%sensitivity_index_level_%d%%' % ix
            param_value, = rave.eval(param_variable)
            filter_variable = 'calibration.%%sensitivity_index_weighted_no_cc%% > %s' % param_value
            items.append(DynamicFilterMenuItemRave(MSGR('More than %s') % param_value, filter_variable, filter_type="CrrFilter"))
        return items

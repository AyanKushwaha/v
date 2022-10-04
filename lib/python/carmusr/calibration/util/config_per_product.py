"""
Created on 19 Nov 2020

@author: steham
"""


from __future__ import absolute_import
import os
from collections import namedtuple

from Localization import MSGR

from carmusr.calibration import mappings
from carmusr.calibration.mappings import bag_handler
from carmusr.calibration.util import config_per_product_rule_details as rule_details_config
from carmusr.calibration.util import config_per_product_si as si_config


class ProductConfig(object):

    def __init__(self,
                 product_name,
                 levels,
                 si_components,
                 si_report_variable_name='calibration.%sensitivity_index_weighted_no_cc%',
                 allow_pos_filtering=True):
        self.product_name = product_name
        self.levels_ordered = levels
        self.levels_dict = dict((l.name, l) for l in self.levels_ordered)
        self.level_names_ordered = list(l.name for l in self.levels_ordered)
        self.level_duty_name = self._get_level_name("LEVEL_DUTY")
        self.level_trip_name = self._get_level_name("LEVEL_TRIP")
        self.level_duty_defined = self.level_duty_name is not None
        self.level_trip_defined = self.level_trip_name is not None
        self.si_components = si_components
        self.si_report_variable_name = si_report_variable_name
        self.allow_pos_filtering = allow_pos_filtering

    def _get_level_name(self, var_in_mappings):
        level_name = mappings.__dict__.get(var_in_mappings, None)
        if level_name is None:
            return None
        if level_name not in self.levels_dict:
            return None
        return level_name

LevelInfo = namedtuple("LevelInfo",
                       "name, objects_name_in_gui, bag_handler_cls, atomic_iterator_name, rave_var_name_rule_failure_time, rule_details_cls")

# Levels must be ordered from the "smallest" to "biggest"
pairing_levels = (LevelInfo(name=mappings.LEVEL_LEG,
                            objects_name_in_gui=MSGR("legs"),
                            bag_handler_cls=bag_handler.MarkedLegsMain,
                            atomic_iterator_name="atom_set",
                            rave_var_name_rule_failure_time="report_calibration.rule_failure_time_for_leg_utc",
                            rule_details_cls=rule_details_config.RuleDetailsLegRule),
                  LevelInfo(name=mappings.LEVEL_DUTY,
                            objects_name_in_gui=MSGR("duties"),
                            bag_handler_cls=bag_handler.MarkedDutiesMain,
                            atomic_iterator_name=mappings.LEVEL_DUTY_ATOMIC_ITERATOR_NAME,
                            rave_var_name_rule_failure_time="report_calibration.rule_failure_time_for_duty_utc",
                            rule_details_cls=rule_details_config.RuleDetailsDutyRule),
                  LevelInfo(name=mappings.LEVEL_TRIP,
                            objects_name_in_gui=MSGR("trips"),
                            bag_handler_cls=bag_handler.MarkedTripsMain,
                            atomic_iterator_name=mappings.LEVEL_TRIP_ATOMIC_ITERATOR_NAME,
                            rave_var_name_rule_failure_time="report_calibration.rule_failure_time_for_trip_utc",
                            rule_details_cls=rule_details_config.RuleDetailsTripRule)
                  )


def get_config_for_active_product():
    forced_product = os.getenv("CALIBRATION_FORCED_PRODUCT")

    if forced_product == "PairingWithoutTripLevel":
        config_to_use = ProductConfig(product_name=forced_product,
                                      levels=pairing_levels[:-1],
                                      si_components=(si_config.MIN_CONN_TIME, si_config.MIN_REST_TIME),
                                      )
    elif forced_product == "PairingWithoutDutyLevel":
        config_to_use = ProductConfig(product_name=forced_product,
                                      levels=[pairing_levels[0], pairing_levels[2]],
                                      si_components=(si_config.MIN_CONN_TIME,),
                                      si_report_variable_name='calibration.%sensitivity_index_weighted_max_in_trip_no_cc%',
                                      )
    elif forced_product == "PairingWithOnlyLegLevelNoPosFilteringEtc":
        config_to_use = ProductConfig(product_name=forced_product,
                                      levels=[pairing_levels[0]],
                                      si_components=(si_config.MIN_CONN_TIME,),
                                      si_report_variable_name='calibration.%min_connection_time_index%',
                                      allow_pos_filtering=False,
                                      )
    else:
        config_to_use = ProductConfig(product_name="Pairing",
                                      si_components=(si_config.MIN_CONN_TIME,
                                                     si_config.MIN_REST_TIME,
                                                     si_config.MAX_DUTY_TIME),
                                      levels=pairing_levels,
                                      )
    return config_to_use


#
# Some static settings
#

DEFAULT_VARIANT_KIND_STRING = MSGR("Trip")
DEFAULT_VARIANT_RULE_TABLE_NAME = "TripRuleRegistrationTable"

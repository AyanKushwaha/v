'''
Common stuff in Calibration for Rave code generation, KPI generation and reports which typically depend on
defintions in the product specification.

Created on 24 Nov 2020

@author: steham
'''

from Localization import MSGR

from carmusr.calibration.util import basics
from carmusr.calibration.util import config_per_product


def get_atomic_iterator_for_level(bag, level_name):
    pconfig = config_per_product.get_config_for_active_product()
    if level_name in pconfig.levels_dict:
        return basics.deep_getattr(bag, pconfig.levels_dict[level_name].atomic_iterator_name)
    msg = "Unsupported level: {}. Supported levels are {}.".format(level_name, ", ".join(pconfig.level_names_ordered))
    raise ValueError(msg)


# The variants of the calibration analysis tools

class CalibAnalysisVariants:

    class Default:
        key = "default"
        title = "{} {}".format(config_per_product.DEFAULT_VARIANT_KIND_STRING, MSGR("analysis"))
        crs_table_name = config_per_product.DEFAULT_VARIANT_RULE_TABLE_NAME

    class TimetableAnalysis:
        key = "timetable"
        title = MSGR("Timetable analysis")
        crs_table_name = "TimetableRuleRegistrationTable"

    @classmethod
    def key2class(cls, key):
        if key == cls.TimetableAnalysis.key:
            return cls.TimetableAnalysis
        return cls.Default

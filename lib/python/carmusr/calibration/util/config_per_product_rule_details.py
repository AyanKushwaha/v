'''
Classes used in the config_per_product for definition of the details table in the Rule Details report.
'''

from Localization import MSGR
import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave

from carmusr.calibration import mappings
from carmusr.calibration.util import basics


class RuleDetailsItem(object):

    # Note: rave_obj may be a definition which returns one of the strings S_ROWNUM,
    #       S_LEGAL, S_LIMIT, S_VALUE, S_DIFF, S_CAT or S_NVALID when calculated by rave.eval.
    # The label can be a string, a string-tuple or a prt-object.

    def __init__(self, label, rave_obj, label_prt_props={"align": prt.RIGHT}, value_prt_props={"align": prt.RIGHT}):
        self.label = label
        self.rave_obj = rave_obj
        self.label_prt_props = label_prt_props
        self.value_prt_props = value_prt_props


class RuleDetails(object):

    @classmethod
    def get_default_first_items(cls):
        return (RuleDetailsItem(MSGR("Row"), '"S_ROWNUM"'),)

    @classmethod
    def get_default_last_items(cls):
        return (RuleDetailsItem(MSGR("Legal"), '"S_LEGAL"'),
                RuleDetailsItem(MSGR("Category"), '"S_CAT"'),
                RuleDetailsItem(MSGR("Limit"), '"S_LIMIT"'),
                RuleDetailsItem(MSGR("Value"), '"S_VALUE"'),
                RuleDetailsItem(MSGR("Diff"), '"S_DIFF"'))

    @classmethod
    def get_slice_item(cls):
        return RuleDetailsItem((MSGR("#"), MSGR("Valid")), '"S_NVALID"')

    @classmethod
    def get_items(cls):
        return cls.get_default_first_items() + (cls.get_slice_item(),) + cls.get_default_last_items()


class RuleDetailsLegRule(RuleDetails):

    @classmethod
    def get_items(cls):
        items = cls.get_default_first_items()
        items += (RuleDetailsItem(MSGR("From"), rave.var("calibration_mappings.leg_start_station")),
                  RuleDetailsItem(MSGR("To"), rave.var("calibration_mappings.leg_end_station")),
                  RuleDetailsItem(MSGR("Next"), rave.var("calibration_mappings.next_leg_end_station")),
                  RuleDetailsItem((MSGR("Flight"), MSGR("no")),
                                  rave.var("calibration_mappings.leg_flight_nr_str")),
                  RuleDetailsItem(MSGR("Dep. (UTC)"), rave.var("calibration_mappings.leg_start_utc")),
                  RuleDetailsItem(MSGR("Arr. (UTC)"), rave.var("calibration_mappings.leg_end_utc")),
                  RuleDetailsItem((MSGR("Arr. time of"), MSGR("day (local)")), rave.var("calibration_mappings.leg_end_od_lt")),
                  cls.get_slice_item())

        arr_dev_var = basics.get_rave_variable("calibration_history.has_arr_dev")
        # arr_dev_var is None if  CARMSYS < 26.7, assume arr_dev table exists, otherwise ask!
        if arr_dev_var is None or rave.eval(arr_dev_var)[0]:
            items += (RuleDetailsItem(MSGR("P1"), basics.get_rave_variable("calibration_history.flight_arr_dev_by_percentile_minutes")),
                      RuleDetailsItem(MSGR("P2"), basics.get_rave_variable("calibration_history.flight_arr_dev_by_percentile_2_minutes")),
                      RuleDetailsItem((MSGR("Historic"), MSGR("samples")),
                                      basics.get_rave_variable("calibration_history.arr_dev_flight_count")))

        if basics.operational_codes_table_is_considered():
            items += (RuleDetailsItem(MSGR("Delay code"), basics.get_rave_variable("studio_calibration.delay_code_str")),
                      RuleDetailsItem((MSGR("Next delay"), MSGR("code")),
                                      basics.get_rave_variable("studio_calibration.next_leg_delay_code_str"),
                                      ))

        return items + cls.get_default_last_items()


class RuleDetailsDutyRule(RuleDetails):

    @classmethod
    def get_items(cls):

        items = cls.get_default_first_items()
        items += (RuleDetailsItem((MSGR("Duty Start"), MSGR("Station")), rave.var("calibration_mappings.duty_start_station")),
                  RuleDetailsItem((MSGR("Duty End"), MSGR("Station")), rave.var("calibration_mappings.duty_end_station")),
                  RuleDetailsItem(MSGR("Duty Start (UTC)"), rave.var("calibration_mappings.duty_start_utc")),
                  RuleDetailsItem(MSGR("Key"), rave.var("report_calibration.duty_content_string"),
                                  {"align": prt.CENTER},
                                  {"align": prt.LEFT, "valign": prt.CENTER, "font": prt.font(size=7, weight=prt.BOLD), "width": 250}),
                  cls.get_slice_item())

        return items + cls.get_default_last_items()


class RuleDetailsTripRule(RuleDetails):

    @classmethod
    def get_items(cls):
        items = cls.get_default_first_items()
        items += (RuleDetailsItem(MSGR("Base"), rave.var("calibration_mappings.homebase")),
                  RuleDetailsItem(MSGR("Name"), rave.first(rave.level(mappings.LEVEL_LEG), rave.keyw("crr_name"))),
                  RuleDetailsItem(MSGR("Start (UTC)"), rave.first(rave.level(mappings.LEVEL_DUTY), rave.var("calibration_mappings.duty_start_utc"))),
                  RuleDetailsItem(MSGR("Key"), rave.var("report_calibration.trip_content_string"),
                                  {"align": prt.CENTER},
                                  {"align": prt.LEFT, "valign": prt.CENTER, "font": prt.font(size=7, weight=prt.BOLD), "width": 250}),
                  cls.get_slice_item())

        return items + cls.get_default_last_items()

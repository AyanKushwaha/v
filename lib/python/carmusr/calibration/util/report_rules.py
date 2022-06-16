"""
Calibration report classes for the reports VOS, VOT, VOW and RVD.
"""


from collections import defaultdict, Counter

import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave
from Localization import MSGR, bl_msgr
import Crs
import Cui
from RelTime import RelTime

from carmusr.calibration.util import calibration_rules as calib_rules
from carmusr.calibration.util import config_per_product
from carmusr.calibration.util import complement
from carmusr.calibration.util import compare_plan
from carmusr.calibration.util import basics
from carmusr.calibration.util import report_util as ru


# General visualisation #########################################

SINGLE_BAR_WIDTH = 0.5
CHART_HEIGHT = 210
CHART_WIDTH_DEFAULT = 570
CHART_WIDTH_WHEN_MANY_VALUES = 740
CHART_MAX_VALUES_FOR_NORMAL_WIDTH = 75
CHART_MAX_VALUES_FOR_ALL_X_TICS = 100
CHART_MAX_X_TICS_WHEN_MANY_X = 20


def get_chart_width(num_x_values):
    return CHART_WIDTH_DEFAULT if num_x_values <= CHART_MAX_VALUES_FOR_NORMAL_WIDTH else CHART_WIDTH_WHEN_MANY_VALUES


def get_x_tics_divider(num_x_values):
    if num_x_values <= CHART_MAX_VALUES_FOR_ALL_X_TICS:
        return 1
    return 1 + (num_x_values // CHART_MAX_X_TICS_WHEN_MANY_X)


"""
 STUDIO-2167: Enum values/remarks not possible to extract from python.
 Hence, enum remarks defined here and in calibration_lookback
"""
LB_ENUM_REMARKS = {'calibration_lookback.rule_time_scheduled_start_actual_end': 'Scheduled start, actual end',
                   'calibration_lookback.rule_time_actual_start_actual_end': 'Actual start, actual end'}

##############################################################
# Base classes for Rule Analysis reports.
##############################################################


class _RuleAnalysisReport(ru.CalibrationReport):
    """
    Base classes for the reports RVD, VOT, VOS, VOW and RD.
    """

    def get_comp_key_and_cat_handler(self, cri):

        if self.current_area_mode in (Cui.AcRotMode, Cui.LegMode) or not self.comparison_plan_name:
            comp_key_var = None
        else:
            comp_key_var = getattr(cri, calib_rules.COMP_KEY)

        if comp_key_var:
            comp_plan_slices = compare_plan.ComparisonPlanHandler.collect_slices_from_comparison_plan(comp_key_var, cri.rule_level)
        else:
            comp_plan_slices = None

        return comp_key_var, compare_plan.CategoriesHandler(comp_plan_slices, cri)

    @classmethod
    def add_lookback_parameter_setting_to_prt_table(cls, table):
        try:
            lb_p = rave.param("calibration_lookback.times_to_use_in_specified_rules")
            val_txt = "{} ({})".format(lb_p.remark(), bl_msgr(LB_ENUM_REMARKS[str(lb_p.value())]))
            cls.add_settings_table_row(table, MSGR("Lookback parameter:"), val_txt)
        except rave.RaveError:
            pass

    @classmethod
    def add_delay_code_setting_to_prt_table(cls, table):
        try:
            delay_codes_p = rave.paramset('studio_calibration.delay_codes_of_interest')
            value = ', '.join(map(str, (delay_codes_p.getValues())))
            if not value:
                return
            val_txt = '{} ({})'.format(delay_codes_p.remark(), value)
            cls.add_settings_table_row(table, MSGR("Delay codes:"), val_txt)
        except rave.RaveError:
            pass

    def generate_settings_table(self):
        settings_table = self.get_settings_table()
        if settings_table.num_rows > 0:
            self.add(prt.Isolate(settings_table))
            self.add("")

    def get_settings_table(self):
        table = self.get_empty_settings_table()
        if self.comparison_plan_name and self.current_area_mode in (Cui.AcRotMode, Cui.LegMode):
            self.add_settings_table_row(table,
                                        MSGR("Note:"),
                                        MSGR("The comparison plan is ignored when the report is generated from legs or rotations"))
        self.add_lookback_parameter_setting_to_prt_table(table)
        self.add_delay_code_setting_to_prt_table(table)
        self.add_crew_pos_filter_to_settings_table(table)
        return table

    def get_empty_settings_table(self):
        return ru.SimpleTable(MSGR("Settings"), use_page=False)

    @classmethod
    def add_settings_table_row(cls, table, setting_txt, value_txt):
        row = table.add(prt.Text(setting_txt, align=prt.LEFT, font=ru.BOLD))
        row.add(prt.Text(value_txt, align=prt.LEFT))

    def add_crew_pos_filter_to_settings_table(self, table):
        if not self.pconfig.allow_pos_filtering:
            return
        if self.current_area_mode in (Cui.AcRotMode, Cui.LegMode):
            filter_txt = MSGR("Always 1 when rotations or free legs are considered")
        else:
            filter_txt = "{} ({})".format(complement.CrewPosFilter.get_pos_filter_param_remark(),
                                          complement.CrewPosFilter.get_pos_filter_param_value())
        self.add_settings_table_row(table, MSGR("Crew positions:"), filter_txt)

    def set_skip_reason_and_create_cr(self):

        self.test_if_report_can_be_generated_and_store_bag()

        if self.skip_reason not in ("NO_OR_EMPTY_LOCAL_PLAN", "INCORRECT_RULE_SET"):
            self.cr = calib_rules.CalibrationRuleContainer(self.variant)

            crewpos_error_txt = complement.refresh_and_get_error_message_if_something_is_wrong()
            if crewpos_error_txt:
                self.add_warning_text(crewpos_error_txt)
                self.skip_reason = "ERROR_FROM_CREW_POS_HANDLING"

        if self.skip_reason:
            return

        if not self.cr.all_rules:
            self.skip_reason = "NO_REGISTERED_RULES"
            self.add_warning_text(self.cr.no_registered_rules_reason())
            return


class _RuleViolations(_RuleAnalysisReport):
    """
    Base class for VOT, VOS and VOW
    """

    def generate_summary_header(self, show_categories):
        summary_table = ru.SimpleTable(MSGR("Violation Summary"), use_page=True)
        text = MSGR("Rule")
        if show_categories:
            text += MSGR(", Category")
        summary_table.add_sub_title(prt.Text(text))
        summary_table.add_sub_title(prt.Text(MSGR("Violations"))).set(colspan=2, border=ru.BORDER_LEFT)
        summary_table.add_sub_title(prt.Text(MSGR("In 1st bin"))).set(colspan=2, border=ru.BORDER_LEFT)
        summary_table.add_sub_title(prt.Text(MSGR("Sum"))).set(colspan=2, border=ru.BORDER_LEFT)
        summary_table.add_sub_title(prt.Text(MSGR("Valid"))).set(border=ru.BORDER_LEFT)
        summary_table.add_sub_title(prt.Text(MSGR("Bin size"))).set(border=ru.BORDER_LEFT)
        return summary_table

    def generate_summary_for_one_rule(self, summary_table, violation_data, show_categories):
        assert isinstance(violation_data, ViolationData)

        rule_title = violation_data.rule_title

        if show_categories:
            def add_row(container, cat, cat_format, viol, viol_format, viol_perc, viol_perc_format):

                cells = (prt.Text(cat, **cat_format),
                         prt.Text(viol, border=ru.BORDER_LEFT, **viol_format),
                         prt.Text(viol_perc, **viol_perc_format),
                         prt.Text("", border=ru.BORDER_LEFT),
                         prt.Text(""),
                         prt.Text("", border=ru.BORDER_LEFT),
                         prt.Text(""),
                         prt.Text("", border=ru.BORDER_LEFT),
                         prt.Text("", border=ru.BORDER_LEFT),
                         prt.Text(""))
                container.add(prt.Row(*cells))

            # Show rule name as header for breakdown
            rule_header = prt.Column(prt.Text(rule_title, font=ru.BOLD))
            summary_table.add(rule_header)
            for category in filter(None, violation_data.cat_handler.get_sorted_categories()):
                count = violation_data.illegal_cat_cnt[category]
                text_illegal_cat_action = ru.get_select_action(self.current_area,
                                                               violation_data.illegal_identifier_cat_dict[category])

                viol_format = {'align': prt.RIGHT, 'action': text_illegal_cat_action}
                cat_format = {'tooltip': violation_data.cat_handler.categories[category].desc}

                add_row(summary_table, category, cat_format,
                        violation_data.illegal_cat_cnt[category], viol_format,
                        basics.ratio_str(count, violation_data.num_valid), viol_format)

                if violation_data.illegal_subcat_cnt and self.arg("show") == "TABLE":
                    slicecat_map = violation_data.illegal_subcat_cnt[category]
                    # Using the preferred order of compare categories.
                    slice_categories = [cat for cat in
                                        compare_plan.SliceCompareCategory.all()
                                        if cat.title in slicecat_map.keys()]
                    subcat_row = prt.Column()
                    summary_table.add(subcat_row)
                    for slice_cat in slice_categories:
                        subcat_title = slice_cat.title
                        count = slicecat_map.get(subcat_title)
                        identifiers = violation_data.illegal_identifier_subcat_dict[category][subcat_title]
                        text_illegal_subcat_action = ru.get_select_action(self.current_area, identifiers)

                        style_subcat = {'tooltip': slice_cat.desc,
                                        'align': prt.LEFT, 'padding': prt.padding(left=20),
                                        'font': ru.ITALIC}
                        style_value = {'action': text_illegal_subcat_action,
                                       'align': prt.RIGHT}
                        add_row(subcat_row,
                                subcat_title, style_subcat,
                                count, style_value,
                                '', {})
            total_font = ru.BOLD
            total_first_cell = prt.Text(MSGR('Total'), font=total_font)
        else:
            total_font = None
            total_first_cell = prt.Text(rule_title)

        text_illegal_action = ru.get_select_action(self.current_area,
                                                   violation_data.illegal_identifier_list)
        text_valid_action = ru.get_select_action(self.current_area,
                                                 violation_data.valid_identifier_list)
        text_in_bin_action = ru.get_select_action(self.current_area,
                                                  violation_data.in_bin_identifier_list)
        num_sum = violation_data.num_illegal + violation_data.num_in_bin
        text_sum_action = ru.get_select_action(self.current_area,
                                               violation_data.in_bin_identifier_list + violation_data.illegal_identifier_list)

        total_cells = (total_first_cell,
                       prt.Text(violation_data.num_illegal,
                                border=ru.BORDER_LEFT,
                                align=prt.RIGHT, action=text_illegal_action, font=total_font),
                       prt.Text(basics.ratio_str(violation_data.num_illegal,
                                                 violation_data.num_valid),
                                align=prt.RIGHT, action=text_illegal_action, font=total_font),
                       prt.Text(violation_data.num_in_bin,
                                border=ru.BORDER_LEFT,
                                align=prt.RIGHT, action=text_in_bin_action, font=total_font),
                       prt.Text(basics.ratio_str(violation_data.num_in_bin,
                                                 violation_data.num_valid),
                                align=prt.RIGHT, action=text_in_bin_action, font=total_font),
                       prt.Text(num_sum,
                                border=ru.BORDER_LEFT,
                                align=prt.RIGHT, action=text_sum_action, font=total_font),
                       prt.Text(basics.ratio_str(num_sum, violation_data.num_valid),
                                align=prt.RIGHT, action=text_sum_action, font=total_font),
                       prt.Text(violation_data.num_valid,
                                border=ru.BORDER_LEFT,
                                align=prt.RIGHT, action=text_valid_action, font=total_font),
                       prt.Text(violation_data.bin,
                                border=ru.BORDER_LEFT,
                                align=prt.RIGHT, font=total_font)
                       )
        summary_table.add(prt.Row(*total_cells))


class _RuleViolationsOverStationOrTime(_RuleViolations):
    """
    Base class for VOT and VOS
    """

    def get_details_table_with_header(self, title, sub_title, vdata):
        table = ru.SimpleTable(title, use_page=True)
        table.add_sub_title(prt.Text(sub_title, align=prt.LEFT, font=ru.BOLD))

        viol_col = prt.Column(prt.Text(MSGR("Violations"), colspan=2, align=prt.LEFT, font=ru.BOLD))
        if vdata.cat_handler.has_categories():
            subsubrow = prt.Row()
            for category in vdata.cat_handler.get_sorted_categories():
                subsubrow.add(prt.Text(category, colspan=2, align=prt.LEFT, border=ru.BORDER_LEFT))
            subsubrow.add(prt.Text(MSGR("Total"), colspan=2, align=prt.LEFT, border=ru.BORDER_LEFT,
                                   font=ru.BOLD))
            viol_col.add(subsubrow)
        subrow = prt.Row(viol_col)
        subrow.add(prt.Text(MSGR("In 1st bin (%s)" % vdata.bin), colspan=2, font=ru.BOLD,
                            border=ru.BORDER_LEFT))
        subrow.add(prt.Text(MSGR("Sum"), colspan=2, align=prt.LEFT, font=ru.BOLD, border=ru.BORDER_LEFT))
        subrow.add(prt.Text(MSGR("Valid"), align=prt.LEFT, font=ru.BOLD, border=ru.BORDER_LEFT))
        subtitle = prt.Column(prt.Text(vdata.rule_title, align=prt.CENTER, font=ru.BOLD), subrow)
        subtitle.set(border=ru.BORDER_LEFT)
        table.add_sub_title(subtitle)

        return table

    def add_data_row(self, table, heading,
                     n_ill, n_in_bin, n_valid,
                     ill_id_list, in_bin_id_list, valid_id_list, cat_handler,
                     ill_cat_cnt, ill_id_cat_dict,
                     **text_kwargs):

        row = table.add(prt.Text(heading, **text_kwargs))
        select_illegal_action = ru.get_select_action(self.current_area,
                                                     ill_id_list)
        select_in_bin_action = ru.get_select_action(self.current_area,
                                                    in_bin_id_list)
        select_valid_action = ru.get_select_action(self.current_area,
                                                   valid_id_list)
        if cat_handler.has_categories():
            for category in cat_handler.get_sorted_categories():
                num_illegal_cat = ill_cat_cnt[category]
                select_cat_action = ru.get_select_action(self.current_area,
                                                         ill_id_cat_dict[category])
                row.add(prt.Text(num_illegal_cat,
                                 align=prt.RIGHT, action=select_cat_action, border=ru.BORDER_LEFT, **text_kwargs))
                row.add(prt.Text(basics.ratio_str(num_illegal_cat, n_valid),
                                 align=prt.RIGHT, action=select_cat_action, **text_kwargs))

        row.add(prt.Text("%s" % (n_ill), align=prt.RIGHT,
                         action=select_illegal_action, border=ru.BORDER_LEFT, **text_kwargs))
        row.add(prt.Text("%s" % (basics.ratio_str(n_ill, n_valid)), align=prt.RIGHT,
                         action=select_illegal_action, **text_kwargs))

        row.add(prt.Text("%s" % (n_in_bin), align=prt.RIGHT,
                         action=select_in_bin_action, border=ru.BORDER_LEFT, **text_kwargs))
        row.add(prt.Text("%s" % (basics.ratio_str(n_in_bin, n_valid)),
                         align=prt.RIGHT, action=select_in_bin_action, **text_kwargs))

        row.add(prt.Text("%s" % (n_ill + n_in_bin), align=prt.RIGHT,
                         border=ru.BORDER_LEFT, **text_kwargs))
        row.add(prt.Text("%s" % (basics.ratio_str(n_ill + n_in_bin, n_valid)),
                         align=prt.RIGHT, **text_kwargs))

        row.add(prt.Text("%s" % n_valid, align=prt.RIGHT,
                         border=ru.BORDER_LEFT, action=select_valid_action, **text_kwargs))


########################################################################################
# Class used by VOT, VOS and VOW reports (VOW only for summary table).
########################################################################################

class ViolationData(object):
    """
    Violation data per rule,
    counting valid, illegal, in 1st bin..
    """
    def __init__(self, cat_handler=None):
        self.rule_title = ""
        self.rule_str = ""
        self.level = ""
        self.bin = 0

        self.num_valid = 0
        self.num_illegal = 0
        self.num_in_bin = 0
        self.illegal_cat_cnt = Counter()
        self.illegal_cat_dim_cnt = defaultdict(Counter)
        self.illegal_dim_cnt = Counter()
        self.valid_dim_cnt = Counter()
        self.in_bin_dim_cnt = Counter()

        self.valid_identifier_dim_dict = defaultdict(list)
        self.valid_identifier_list = []
        self.illegal_identifier_cat_dim_dict = defaultdict(lambda: defaultdict(list))
        self.illegal_identifier_dim_dict = defaultdict(list)
        self.illegal_identifier_cat_dict = defaultdict(list)
        self.illegal_identifier_list = []
        self.in_bin_identifier_dim_dict = defaultdict(list)
        self.in_bin_identifier_list = []

        # Slice Compare category - sub-category to main-category
        self.illegal_subcat_cnt = defaultdict(Counter)
        self.illegal_identifier_subcat_dict = defaultdict(lambda: defaultdict(list))

        self.cat_handler = cat_handler

    def add_illegal(self, cat, slice_cat_title, num_crew, cnt_dim, id_dim, identifiers):
        self.num_illegal += num_crew

        self.illegal_cat_cnt[cat] += num_crew

        self.illegal_cat_dim_cnt[cat][cnt_dim] += num_crew
        self.illegal_dim_cnt[cnt_dim] += num_crew

        self.illegal_identifier_cat_dim_dict[cat][id_dim] += identifiers
        self.illegal_identifier_dim_dict[id_dim] += identifiers
        self.illegal_identifier_cat_dict[cat] += identifiers
        self.illegal_identifier_list += identifiers

        if slice_cat_title:
            self.illegal_subcat_cnt[cat][slice_cat_title] += num_crew
            self.illegal_identifier_subcat_dict[cat][slice_cat_title] += identifiers

    def add_valid(self, cnt_dim, num_crew, id_dim, identifiers):
        self.valid_dim_cnt[cnt_dim] += num_crew
        self.num_valid += num_crew

        self.valid_identifier_dim_dict[id_dim] += identifiers
        self.valid_identifier_list += identifiers

    def add_in_bin(self, cnt_dim, num_crew, id_dim, identifiers):
        if cnt_dim is not None:
            self.in_bin_dim_cnt[cnt_dim] += num_crew
        self.num_in_bin += num_crew

        if id_dim is not None:
            self.in_bin_identifier_dim_dict[id_dim] += identifiers
        self.in_bin_identifier_list += identifiers


############################################################################
# Definitions for VOT and VOW
############################################################################

class TimeZoneHandler(object):

    def __init__(self):
        self.pconfig = config_per_product.get_config_for_active_product()
        self.time_zone_ref_station = self.get_time_zone_ref_station()
        if not self.time_zone_ref_station:
            self.hours_utc_offset = self.get_utc_time_offset_when_not_ref_station()

    def get_rule_failure_time(self, bag, level):
        raw_rule_time = rave.eval(bag, rave.var(self.pconfig.levels_dict[level].rave_var_name_rule_failure_time))[0]

        if self.time_zone_ref_station:
            hours_utc_offset = bag.report_calibration.station_hours_utc_diff(self.time_zone_ref_station, raw_rule_time)
        else:
            hours_utc_offset = self.hours_utc_offset

        return raw_rule_time + RelTime(60 * hours_utc_offset)

    @staticmethod
    def get_time_zone():
        time_zone_param = rave.param('report_calibration.%vot_time_zone%')
        return time_zone_param.value()

    @classmethod
    def get_utc_time_offset_when_not_ref_station(cls):
        time_zone_str = str(cls.get_time_zone())
        hours = int(time_zone_str.split("_")[-1])
        hours = -hours if "minus" in time_zone_str else hours
        return hours

    @classmethod
    def get_time_zone_ref_station(cls):
        time_zone = cls.get_time_zone()
        if time_zone == rave.enumval("report_calibration.reference"):
            return Crs.CrsGetModuleResource("preferences", Crs.CrsSearchModuleDef, "DstAirport")
        return None

    @classmethod
    def add_info_to_prt_table(cls, table):
        time_zone_ref_station = TimeZoneHandler.get_time_zone_ref_station()
        if time_zone_ref_station:
            if time_zone_ref_station != "***":
                time_zone_info = MSGR("{} (reference airport)").format(time_zone_ref_station)
            else:
                time_zone_info = MSGR("UTC (undefined reference airport)")
        else:
            hours_utc_offset = cls.get_utc_time_offset_when_not_ref_station()
            time_zone_info = MSGR("UTC") + ("%+i" % hours_utc_offset if hours_utc_offset != 0 else "")
        tz_row = table.add(prt.Text(MSGR("Time zone: "),
                                    align=prt.LEFT,
                                    font=ru.BOLD))
        tz_row.add(prt.Text(time_zone_info, align=prt.LEFT))


def add_time_stuff_to_settings_table(table):
    TimeZoneHandler.add_info_to_prt_table(table)
    show_label = True
    for param_name in ("report_calibration.use_scheduled_time_as_rule_time_p",
                       "report_calibration.use_end_time_of_object_as_rule_failure_time_p"):
        try:
            param = rave.param(param_name)
        except rave.UsageError:
            continue
        label = MSGR("Rule time: ") if show_label else ""
        row = table.add(prt.Text(label, align=prt.LEFT, font=ru.BOLD))
        row.add(prt.Text("{0} ({1})".format(param.remark(), param.value())))
        show_label = False


# Helpers: Create Ranges ######################################


def get_counter_values_as_list(index, counter):
    return [counter[ix] for ix in index]


# Helpers: Report interaction ##################################

class Tooltip(object):
    """
    Gives a tooltip like:
        {NAME}
        {xval}
        Total: {totals}
        {y_label}: {yval}

    Use in charttooltip
    """
    def __init__(self, name, totals=None, x_map=lambda x: x, x_fmt='%s', y_fmt='%s', y_label=''):
        self.name = name
        self.totals = totals
        self.x_fmt = x_fmt
        self.y_label = y_label
        self.y_fmt = y_fmt
        self.x_map = x_map

    def __call__(self, x, y):
        try:
            t = self.totals[x] if self.totals else None
        except KeyError:
            t = '-'
        return '\n'.join(filter(None, (self.name,
                                       self.x_fmt % self.x_map(x),
                                       MSGR("Total: ") + self.y_fmt % t if t is not None else "",
                                       ": ".join(filter(None, (self.y_label, self.y_fmt % y))))))

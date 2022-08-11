"""
Definitions common for the reports VOS, VOT, VOW, RVD and RD.
"""


from __future__ import absolute_import
from six.moves import map
from six.moves import range
from six.moves import zip
from collections import defaultdict, OrderedDict
from copy import deepcopy
import traceback

import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave
from Localization import MSGR, bl_msgr
import Crs
import Cui
from RelTime import RelTime
import Errlog

from carmusr.calibration.mappings import DrawExt
from carmusr.calibration.mappings import studio_palette as sp
from carmusr.calibration.util import calibration_rules as calib_rules
from carmusr.calibration.util import config_per_product
from carmusr.calibration.util import complement
from carmusr.calibration.util import compare_plan
from carmusr.calibration.util import basics
from carmusr.calibration.util import report_util as ru

# General visualisation #########################################

SINGLE_BAR_WIDTH = 0.7

"""
 STUDIO-2167: Enum values/remarks not possible to extract from python.
 Hence, enum remarks defined here and in calibration_lookback
"""
LB_ENUM_REMARKS = {'calibration_lookback.rule_time_scheduled_start_actual_end': 'Scheduled start, actual end',
                   'calibration_lookback.rule_time_actual_start_actual_end': 'Actual start, actual end'}


##############################################################
# Base class for Rule Analysis reports.
##############################################################

class _RuleAnalysisReport(ru.CalibrationReport):
    """
    Base class for the reports RVD, VOT, VOS, VOW and RD.
    """

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


#########################################################################################################
# PlanningObject creation, RuleSummary handling, tables and graphs. Used by RD, RVD, VOS and VOT reports.
#########################################################################################################

class PlanningObject(object):

    def __init__(self):
        self.is_valid = None
        self.num_crew = None
        self.is_legal = None
        self.in_first_bin = None
        self.value = None
        self.limit = None
        self.diff = None
        self.cat = None
        self.sub_cat = None
        self.leg_identifiers = None


class PlanningObjectCreator(object):

    def __init__(self, report, cri):
        self.report = report
        self.cri = cri

        if report.current_area_mode in (Cui.AcRotMode, Cui.LegMode) or not report.comparison_plan_name:
            comp_key_var = None
        else:
            comp_key_var = getattr(cri, calib_rules.COMP_KEY)

        if comp_key_var:
            comp_plan_slices = compare_plan.ComparisonPlanHandler.collect_slices_from_comparison_plan(comp_key_var, cri.rule_level)
        else:
            comp_plan_slices = None

        self.comp_key_var = comp_key_var
        self.cat_handler = compare_plan.CategoriesHandler(comp_plan_slices, cri)

    def get_objects_and_bags(self):
        leg_or_ac_mode_in_window = self.report.current_area_mode in (Cui.AcRotMode, Cui.LegMode)
        comp_key_var = self.comp_key_var
        max_diff_for_bin_one = self.cri.max_diff_for_bin_one
        is_valid_var = getattr(self.cri, calib_rules.IS_VALID).rave_obj
        limit_var = getattr(self.cri, calib_rules.LIMIT).rave_obj
        value_var = getattr(self.cri, calib_rules.VALUE).rave_obj
        rule_body_expr = self.cri.rule_body_expr

        for bag in self.report.get_bags_for_cri_and_write_warning_once(self.cri):
            po = PlanningObject()
            po.leg_identifiers = [leg_bag.leg_identifier() for leg_bag in bag.atom_set()]

            if leg_or_ac_mode_in_window:
                tripslice_or_crew_comp = 1
                po.num_crew = 1
            else:
                tripslice_or_crew_comp = compare_plan.filtered_slice_from_bag(comp_key_var, bag)
                po.num_crew = tripslice_or_crew_comp.complement_sum()

            po.is_valid = False

            if not po.num_crew:
                yield po, bag
                continue

            if not rave.eval(bag, is_valid_var)[0]:
                yield po, bag
                continue

            is_legal, = rave.eval(bag, rule_body_expr)
            if is_legal is None:
                yield po, bag
                continue

            po.is_legal = is_legal
            po.is_valid = True

            po.limit, po.value = rave.eval(bag, limit_var, value_var)
            abs_diff = abs(po.limit - po.value)
            po.diff = abs_diff if is_legal else -abs_diff

            if is_legal:
                po.in_first_bin = po.diff <= max_diff_for_bin_one
                yield po, bag
            else:
                po.sub_cat, cats_and_crew = self.cat_handler.get_and_register_cat(bag, tripslice_or_crew_comp)
                num_items = len(cats_and_crew)  # Normally 1, sometimes 2.
                for ix in range(num_items):
                    po2 = po if ix + 1 == num_items else deepcopy(po)
                    po2.cat, po2.num_crew = cats_and_crew[ix]
                    yield po2, bag


class RuleSummaryItem(object):

    max_number_of_values = 4

    def __init__(self, values=None, leg_ids=None):
        self.values = values or [0] * self.max_number_of_values
        self.leg_ids = set(leg_ids or ())

    def add(self, values, leg_ids):
        for ix, val in enumerate(values):
            self.values[ix] += val
        self.leg_ids |= set(leg_ids)

    def __sub__(self, other):
        return RuleSummaryItem([v1 - v2 for v1, v2 in zip(self.values, other.values)],
                               self.leg_ids - other.leg_ids)


class RuleSummaryHandler(object):

    def __init__(self, consider_sub_cats=False):
        self.selected = RuleSummaryItem()
        self.valid = RuleSummaryItem()
        self.legal = RuleSummaryItem()
        self.in_first_bin = RuleSummaryItem()
        self.categories = defaultdict(RuleSummaryItem)
        self.consider_sub_cats = consider_sub_cats

    def __getattr__(self, name):
        if name == "not_valid":
            self.not_valid = self.selected - self.valid
            return getattr(self, name)
        if name == "illegal":
            self.illegal = self.valid - self.legal
            return getattr(self, name)
        if name == "outside_first_bin":
            self.outside_first_bin = self.legal - self.in_first_bin
            return getattr(self, name)
        if name == "illegal_or_in_first_bin":
            self.illegal_or_in_first_bin = self.valid - self.outside_first_bin
            return getattr(self, name)
        raise AttributeError("The class 'RuleSummaryHandler' doesn't have the attribute '{}'".format(name))

    def get_item(self, key):
        """
        key may be one of the attributes or the name of a category.
        """
        if hasattr(self, key):
            return getattr(self, key)
        return self.categories[key]

    def add_from_po(self, po, skip_selected=False, additional_values_for_valid_legal_and_illegal=()):
        """
        Adds values to for the PlanningObject relevant summary attributes.
        """
        if skip_selected and not po.is_valid:
            return

        basic_values = (po.num_crew,)
        identifiers = po.leg_identifiers

        if not skip_selected:
            self.selected.add(basic_values, identifiers)

        if not po.is_valid:
            return

        more_values = basic_values + additional_values_for_valid_legal_and_illegal

        self.valid.add(more_values, identifiers)
        if po.is_legal:
            self.legal.add(more_values, identifiers)
            if po.in_first_bin:
                self.in_first_bin.add(basic_values, identifiers)
        else:
            self.categories[po.cat].add(basic_values, identifiers)
            if self.consider_sub_cats and po.sub_cat:
                self.categories[(po.cat, po.sub_cat)].add(basic_values, identifiers)


# Summary tree table from RuleSummaryHandler.

def get_summary_table(rsh, cri, current_area, cat_handler):

    pconfig = config_per_product.get_config_for_active_product()

    def get_cell(item, label, show_percentage_of_valid=True, colour=None, tooltip=None, show_border=True, label_font=None, label_offset=False):
        val = item.values[0]
        action = ru.get_select_action(current_area, item.leg_ids)
        row1 = prt.Row()
        if colour:
            row1.add(LegendColourIndicator(colour, valign=prt.CENTER))
        row1.add(prt.Text(label,
                          tooltip=tooltip,
                          valign=prt.CENTER,
                          padding=prt.padding(left=25) if label_offset else None,
                          font=label_font))
        row = ru.SimpleTableRow(prt.Isolate(row1, valign=prt.CENTER),
                                prt.Text(val,
                                         align=prt.RIGHT,
                                         valign=prt.CENTER,
                                         action=action),
                                border=prt.border_frame(1, colour=ru.SIMPLE_TABLE_BORDER_GREY) if show_border else None)
        if show_percentage_of_valid:
            row.add(prt.Text(basics.ratio_str(val, rsh.valid.values[0]),
                             align=prt.RIGHT,
                             tooltip=MSGR("Percentage of Valid"),
                             action=action,
                             valign=prt.CENTER))
        return row

    bin_remark = getattr(cri, calib_rules.BIN).remark()
    bin_value = getattr(cri, calib_rules.BIN).value()

    table = ru.SimpleTable(MSGR("Summary"), use_page=False)

    kind_of_planning_objects_str_1 = pconfig.levels_dict[getattr(cri, calib_rules.RULE_NAME).level_name].objects_name_in_gui
    kind_of_planning_objects_str_2 = kind_of_planning_objects_str_1[0].upper() + kind_of_planning_objects_str_1[1:]
    tooltip = MSGR("Number of planning objects (from selected {}) after crew position filtering.").format(kind_of_planning_objects_str_1)
    table.add_sub_title(kind_of_planning_objects_str_2,
                        tooltip=tooltip,
                        colspan=5)

    table.add_sub_title(MSGR("Legality"), colspan=3)
    table.add_sub_title(MSGR("Category"), colspan=1)

    prt.Column.add(table, prt.Isolate(ru.SimpleTableRow(prt.Text(MSGR("Rule"), font=ru.BOLD),
                                                        cri.rule_label)))

    table.add_sub_title(prt.Text(MSGR("Bin size: {}").format(bin_value),
                                 align=prt.RIGHT,
                                 tooltip=MSGR("Bin size parameter: '{}'").format(bin_remark)))
    row1 = prt.Column.add(table, prt.Row())
    row1.add(get_cell(rsh.selected, MSGR("Selected"), label_font=ru.BOLD, show_percentage_of_valid=False))
    col1 = row1.add(prt.Column())
    row2 = col1.add(get_cell(rsh.valid, MSGR("Valid"), label_font=ru.BOLD))
    col1.add(prt.Isolate(get_cell(rsh.not_valid, MSGR("Not Valid"),
                                  label_font=ru.BOLD,
                                  show_percentage_of_valid=False, show_border=False)))

    col2 = row2.add(prt.Column())
    row_legal = col2.add(prt.Row(get_cell(rsh.legal, MSGR("Legal"), label_font=ru.BOLD)))
    col_legal = row_legal.add(prt.Column())
    if rsh.outside_first_bin.leg_ids:
        col_legal.add(get_cell(rsh.outside_first_bin,
                               basics.OUTSIDE_FIRST_BIN_LABEL,
                               colour=basics.OUTSIDE_FIRST_BIN_COLOUR))
    if rsh.in_first_bin.leg_ids:
        col_legal.add(get_cell(rsh.in_first_bin,
                               basics.IN_FIRST_BIN_LABEL,
                               colour=basics.IN_FIRST_BIN_COLOUR))
    row_illegal = col2.add(prt.Row(get_cell(rsh.illegal, MSGR("Illegal"), label_font=ru.BOLD)))
    cat_col = row_illegal.add(prt.Column())
    for cat_name in cat_handler.get_sorted_categories():
        col_for_one_cat = cat_col.add(prt.Column(border=prt.border_frame(1, colour=ru.SIMPLE_TABLE_BORDER_GREY)))
        col_for_one_cat.add(get_cell(rsh.categories[cat_name],
                                     cat_name,
                                     show_border=False,
                                     colour=cat_handler.bar_color(cat_name),
                                     tooltip=cat_handler.categories[cat_name].desc))
        if rsh.consider_sub_cats:
            for sub_cat_cls in compare_plan.SliceCompareCategory.all():
                key = (cat_name, sub_cat_cls.title)
                if key in rsh.categories:
                    col_for_one_cat.add(prt.Row(get_cell(rsh.categories[key],
                                                         sub_cat_cls.title,
                                                         show_border=False,
                                                         label_offset=True,
                                                         label_font=ru.ITALIC,
                                                         show_percentage_of_valid=False,
                                                         tooltip=sub_cat_cls.desc),
                                        ""))
    return table


class LegendColourIndicator(prt.Canvas):

    def __init__(self, legend_fill_colour, legend_border=False, size=11, *args, **kw):
        self.legend_fill_colour = legend_fill_colour
        self.legend_border = legend_border
        prt.Canvas.__init__(self, size, size, *args, **kw)

    def draw(self, gc):
        gc.coordinates(-100, -100, 100, 100)
        de = DrawExt(self, gc)
        de.square(0, 0,
                  de.cx2p(200),
                  colour=sp.Black if self.legend_border else None,
                  fill=self.legend_fill_colour,
                  valign=prt.CENTER,
                  align=prt.CENTER)


## Single rule diagram based on data in RuleSummaryHandlers ##

def get_single_rule_diagram(title,
                            ordered_x_keys,
                            rshs,  # DefaultDict{x_key: RuleSummaryHandler}
                            xaxis_name,
                            current_area,
                            cat_handler,
                            include_legal=True,
                            show_percentage_of_valid=False,
                            xkey2label=lambda key: str(key),
                            bar_width=1):
    datas = defaultdict(list)
    x_label2key = OrderedDict()
    sorted_categories = cat_handler.get_sorted_categories()
    legal_attr_keys = ["outside_first_bin", "in_first_bin"] if include_legal else []

    for x_key in ordered_x_keys:
        x_label = xkey2label(x_key)
        x_label2key[x_label] = x_key

        for item_key in sorted_categories + legal_attr_keys:
            val = rshs[x_key].get_item(item_key).values[0]
            if show_percentage_of_valid:
                val = basics.percentage_value(val, rshs[x_key].valid.values[0])
            datas[item_key].append((x_label, val))

    def get_series(item_key, colour, label):
        return prt.Series(datas[item_key],
                          graph=prt.Bar(width=bar_width, fill=colour),
                          action=prt.chartaction(MyDiagramAction(current_area, item_key, x_label2key, rshs)),
                          tooltip=prt.charttooltip(MyDiagramTooltip(label, x_label2key, rshs, cat_handler)))

    series_list = []
    for cat in reversed(sorted_categories):
        series_list.append(get_series(cat, cat_handler.bar_color(cat), cat))
    if include_legal:
        series_list.append(get_series("in_first_bin", basics.IN_FIRST_BIN_COLOUR, basics.IN_FIRST_BIN_LABEL))
        series_list.append(get_series("outside_first_bin", basics.OUTSIDE_FIRST_BIN_COLOUR, basics.OUTSIDE_FIRST_BIN_LABEL))

    return get_chart(title, xaxis_name, x_label2key, series_list, show_percentage_of_valid)


class MyDiagramAction(object):

    def __init__(self, area, item_key, xlabel2key_dict, rshs):
        self.area = area
        self.item_key = item_key   # cat name or name of rsh-attr.
        self.rshs = rshs
        self.xlabel2key_dict = xlabel2key_dict

    def __call__(self, x, _y):
        ids = self.rshs[self.xlabel2key_dict[x]].get_item(self.item_key).leg_ids
        ru.calib_show_and_mark_legs(self.area, ids)


class MyDiagramTooltip(object):

    def __init__(self, label_this, xlabel2key_dict, rshs, cat_handler):
        self.label_this = label_this
        self.rshs = rshs
        self.xlabel2key_dict = xlabel2key_dict
        self.cat_handler = cat_handler

    def __call__(self, x, _):
        # Almost nothing written to log file by default if an exception is raised here.
        try:
            return self._do_call(x)
        except:
            Errlog.log(traceback.format_exc())
            raise

    def _do_call(self, x):

        rsh = self.rshs[self.xlabel2key_dict[x]]
        res = []
        res.append(self.label_this)
        res.append("")
        res.append(x)
        res.append("")
        self.add_tooltip_common_to_str_list(res, rsh, self.cat_handler)
        return "\n".join(res)

    @staticmethod
    def add_tooltip_common_to_str_list(res, rsh, cat_handler):

        def get_row(title, val, offset=4):
            return "{}{}: {} ({})".format(" " * offset, title, val, basics.percentage_string(val, rsh.valid.values[0]))

        res.append(get_row(MSGR("Valid"), rsh.valid.values[0], offset=0))
        res.append(get_row(MSGR("Legal"), rsh.legal.values[0], offset=2))
        if rsh.outside_first_bin.values[0]:
            res.append(get_row(basics.OUTSIDE_FIRST_BIN_LABEL, rsh.outside_first_bin.values[0]))
        if rsh.in_first_bin.values[0]:
            res.append(get_row(basics.IN_FIRST_BIN_LABEL, rsh.in_first_bin.values[0]))
        res.append(get_row(MSGR("Illegal"), rsh.illegal.values[0], offset=2))
        for cat in cat_handler.get_sorted_categories():
            if rsh.categories[cat].values[0]:
                res.append(get_row(cat, rsh.categories[cat].values[0]))


def get_chart(title, xaxis_name, x_label2key, series_list, show_percentage_of_valid, on_top=True):
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

    chart = ru.SimpleDiagram(prt.Text(title, valign=prt.CENTER))
    num_x_values = len(x_label2key)
    rotate_tags = num_x_values * (max(len(xl) for xl in x_label2key) + 1) > 92
    x_labels_to_show = set([x for x in x_label2key][0::get_x_tics_divider(num_x_values)])
    xaxis_format = lambda v: v if v in x_labels_to_show else ""
    chart.add(prt.Isolate(prt.Chart(get_chart_width(num_x_values),
                                    CHART_HEIGHT,
                                    prt.Combine(*tuple(series_list),
                                                yaxis_name=MSGR("% of Valid") if show_percentage_of_valid else MSGR("# Planning objects"),
                                                on_top=on_top),
                                    xaxis_name=xaxis_name,
                                    background=sp.White,
                                    xaxis_rotate_tags=rotate_tags,
                                    xaxis_format=xaxis_format)))
    return chart


## Per bin table based on data in RuleSummaryHandlers ##

def get_per_bin_table(title,
                      ordered_bin_keys,
                      rshs,  # DefaultDict{bin_key: RuleSummaryHandler}
                      bins_col_label,
                      total_rsh,  # RuleSummaryHandler
                      current_area,
                      cat_handler,
                      show_percentage_of_valid=False,
                      binkey2label=lambda bin_key: prt.Text(bin_key, colspan=3)):

    border_before_main = prt.border(left=1)
    border_before_cat = prt.border(left=1, colour=ru.SIMPLE_TABLE_BORDER_GREY)
    kwargs_main = dict(colspan=2, valign=prt.CENTER, font=ru.BOLD, border=border_before_main)
    kwargs_cat = dict(colspan=2, valign=prt.CENTER, border=border_before_cat)

    table = ru.SimpleTable(title, use_page=True)
    table.add_sub_title(prt.Text(bins_col_label, colspan=3, valign=prt.CENTER, font=ru.BOLD))
    table.add_sub_title(prt.Text(MSGR("Valid"), **kwargs_main))
    table.add_sub_title(prt.Text(MSGR("Legal"), **kwargs_main))
    if total_rsh.outside_first_bin.leg_ids:
        table.add_sub_title(prt.Text(basics.OUTSIDE_FIRST_BIN_LABEL, **kwargs_cat))
    if total_rsh.in_first_bin.leg_ids:
        table.add_sub_title(prt.Text(basics.IN_FIRST_BIN_LABEL, **kwargs_cat))
    table.add_sub_title(prt.Text(MSGR("Illegal"), **kwargs_main))
    if cat_handler.has_categories():
        for cat in cat_handler.get_sorted_categories():
            table.add_sub_title(_split_label_if_long(cat), **kwargs_cat)
    table.add_sub_title(prt.Text(MSGR("Illegal + {}").format(basics.IN_FIRST_BIN_LABEL),
                                 colspan=2, valign=prt.CENTER, border=border_before_main))

    def get_row(bin_key):

        def get_cell(rso, **kwargs):
            action = ru.get_select_action(current_area, rso.leg_ids)
            row = ru.SimpleTableRow(**kwargs)
            text = row.add(prt.Text(rso.values[0], align=prt.RIGHT, action=action))
            if show_percentage_of_valid and rso is not rsh.valid:
                row.add(prt.Text(basics.percentage_string(rso.values[0], rsh.valid.values[0]),
                                 tooltip=MSGR("Percentage of Valid"),
                                 align=prt.RIGHT, action=action))

            else:
                text.set(colspan=2)
            return row

        row = ru.SimpleTableRow()
        if bin_key == "TOTAL":
            font = ru.BOLD
            rsh = total_rsh
            row.add(prt.Text(MSGR("Total"), colspan=3, font=font))
        else:
            font = None
            rsh = rshs[bin_key]
            row.add(binkey2label(bin_key))

        row.add(get_cell(rsh.valid, font=font, border=border_before_main))
        row.add(get_cell(rsh.legal, font=font, border=border_before_main))
        if total_rsh.outside_first_bin.leg_ids:
            row.add(get_cell(rsh.outside_first_bin, font=font, border=border_before_cat))
        if total_rsh.in_first_bin.leg_ids:
            row.add(get_cell(rsh.in_first_bin, font=font, border=border_before_cat))
        row.add(get_cell(rsh.illegal, font=font, border=border_before_main))
        if cat_handler.has_categories():
            for cat in cat_handler.get_sorted_categories():
                row.add(get_cell(rsh.categories[cat], font=font, border=border_before_cat))
        row.add(get_cell(rsh.illegal_or_in_first_bin, font=font, border=border_before_main))
        return row

    for bin_key in ordered_bin_keys:
        table.add(get_row(bin_key))
    table.add(get_row("TOTAL"))

    return table


def _split_label_if_long(text):
    len_txt = len(text)
    if len_txt < 20:
        return text
    just_after_middle_ix = 2 + len_txt // 2
    for offset in range(len_txt // 2 - 5):
        for direction in (1, -1):
            cand_ix = just_after_middle_ix + (direction * offset)
            if text[cand_ix] == " ":
                return (text[:cand_ix], text[cand_ix + 1:])
    return text


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

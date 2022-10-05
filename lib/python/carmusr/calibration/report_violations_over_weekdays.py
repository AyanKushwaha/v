from __future__ import absolute_import
from __future__ import division
import six
from six.moves import range
import math
import traceback
from collections import defaultdict

from Localization import MSGR
import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave
import Errlog

from carmusr.calibration.mappings import date_extensions as de
from carmusr.calibration.util import basics
from carmusr.calibration.util import report_rules
from carmusr.calibration.util import report_util as ru


class RuleViolationsOverWeekdays(report_rules._RuleAnalysisReport):

    RULE_PARAM = 'report_calibration.vow_rule'
    has_table_view = False

    @staticmethod
    def get_header_text():
        return ru.CalibReports.VOW.title

    @staticmethod
    def get_form_handler(_variant):
        from carmusr.calibration.util import report_forms as rf
        return rf.vow_param_form_handler

    @classmethod
    def get_rule_key(cls):
        ix_rule, = rave.eval(cls.RULE_PARAM)
        return "%s" % ix_rule

    def create(self):

        self.setpaper(orientation=prt.LANDSCAPE, size=prt.A3)
        super(RuleViolationsOverWeekdays, self).create()

        self.set_skip_reason_and_create_cr()

        if self.skip_reason is not None:
            self.add_warnings_and_links()
            return

        bins_per_day = rave.param("report_calibration.vow_bins_per_day").value()
        self.bin_size = basics.ONE_DAY / bins_per_day
        self.gamma = rave.param("report_calibration.vow_centi_gamma").value() / 100

        rule_str = self.arg("rule") or self.get_rule_key()
        tzh = report_rules.TimeZoneHandler()

        if rule_str not in self.cr.all_rules_dict:
            self.add_warning_text(MSGR("No rule selected to analyse"))
            self.add_warnings_and_links()
            return

        self.add_link_to_rule_details_report_for_rule = rule_str

        cri = self.cr.get_rule_item(rule_str)
        level = cri.rule_level
        poc = report_rules.PlanningObjectCreator(self, cri)

        self.cat_handler = poc.cat_handler
        self.rshs = defaultdict(report_rules.RuleSummaryHandler)

        for po, bag in poc.get_objects_and_bags():

            self.rshs[(None, None)].add_from_po(po)

            if not po.is_valid:
                continue

            rule_time = tzh.get_rule_failure_time(bag, level)

            time_of_day_key = int(rule_time.time_of_day() / self.bin_size) * self.bin_size
            weekday_ix = int(rule_time.time_of_week() / basics.ONE_DAY) + 1

            self.rshs[(weekday_ix, time_of_day_key)].add_from_po(po, skip_selected=True)
            # Sub-totals needed for the tooltips:
            self.rshs[(None, time_of_day_key)].add_from_po(po, skip_selected=True)
            self.rshs[(weekday_ix, None)].add_from_po(po, skip_selected=True)

        self.add_warnings_and_links()
        self.generate_settings_table()

        self.add(prt.Isolate(report_rules.get_summary_table(self.rshs[(None, None)], cri, self.current_area, poc.cat_handler)))
        self.add("")
        self.page()

        if not self.rshs[(None, None)].valid.leg_ids:
            return

        self.add_heatmaps()

    def get_settings_table(self):
        table = self.get_empty_settings_table()
        self.add_lookback_parameter_setting_to_prt_table(table)
        self.add_crew_pos_filter_to_settings_table(table)
        report_rules.add_time_stuff_to_settings_table(table)
        return table

    def add_heatmaps(self):

        def get_one_heatmap_common(*args, **kw):

            return ru.Heatmap(self.current_area,
                              *args,
                              keyname_x=MSGR("Weekday"),
                              keyname_y=MSGR("Time of day"),
                              x_keys=[7] + list(range(1, 7)),
                              y_keys=[v * self.bin_size for v in range(int(math.ceil(basics.ONE_DAY / self.bin_size)))],
                              x_key_format=de.day_num2gui_weekday_short_name,
                              y_key_format=lambda v: "%s - %s" % (v, min(basics.ONE_DAY, v + self.bin_size) - basics.ONE_MINUTE),
                              show_total_row=True,
                              show_total_col=True,
                              gamma=self.gamma,
                              value_col_min_width=60,
                              **kw)

        def get_one_heatmap_with_divider(title, item_key=None, legend_colour=None, tooltip_title=None, **kw):
            item_key = item_key or title
            tooltip_title = tooltip_title or title
            if legend_colour:
                title = prt.Row(report_rules.LegendColourIndicator(legend_colour,
                                                                   legend_border=True,
                                                                   padding=prt.padding(left=2),
                                                                   valign=prt.CENTER),
                                title)
            return get_one_heatmap_common(title,
                                          get_heatmap_data(item_key),
                                          dividerdict=valid_data,
                                          max_colour_value=1.0,
                                          tooltip_format=MyTooltip(tooltip_title, self.rshs, self.cat_handler),
                                          **kw)

        def get_heatmap_data(item_name):
            ret = defaultdict(lambda: [int(), list()])
            for key, rsh in six.iteritems(self.rshs):
                if None in key:
                    continue
                rso = rsh.get_item(item_name)
                ret[key] = (rso.values[0], list(rso.leg_ids))
            return ret

        valid_data = get_heatmap_data("valid")

        if self.rshs[(None, None)].illegal.leg_ids:
            hm = get_one_heatmap_with_divider(MSGR("Violations"), "illegal", tooltip_title=MSGR("Illegal"))
            self.add(prt.Isolate(hm))
            self.add("")
            self.page()

        if self.cat_handler.has_categories():
            exp_col = prt.Column("")
            for cat in self.cat_handler.get_sorted_categories():
                hm = get_one_heatmap_with_divider(cat, legend_colour=self.cat_handler.bar_color(cat))
                exp_col.add(hm)
                exp_col.add("")
                exp_col.page()
            self.add(prt.Expandable(MSGR("Violations Per Category"), exp_col))
            self.add("")

        if self.rshs[(None, None)].in_first_bin.leg_ids:
            hm = get_one_heatmap_with_divider(basics.IN_FIRST_BIN_LABEL, "in_first_bin", basics.IN_FIRST_BIN_COLOUR)
            self.add(prt.Isolate(hm))
            self.add("")
            self.page()

        if self.rshs[(None, None)].outside_first_bin.leg_ids:
            exp_col = prt.Column("")
            hm = get_one_heatmap_with_divider(basics.OUTSIDE_FIRST_BIN_LABEL,
                                              "outside_first_bin",
                                              basics.OUTSIDE_FIRST_BIN_COLOUR,
                                              max_colour=basics.HEATMAP_BLUE)
            exp_col.add(hm)
            exp_col.add("")
            exp_col.page()
            self.add(prt.Expandable(basics.OUTSIDE_FIRST_BIN_LABEL, exp_col))
            self.add("")

        hm = get_one_heatmap_common(MSGR("Valid"),
                                    valid_data,
                                    tooltip_format=MyTooltip(MSGR("Valid"), self.rshs, self.cat_handler),
                                    max_colour=basics.HEATMAP_BLUE)
        self.add(prt.Isolate(hm))


class MyTooltip(object):

    def __init__(self, label_this, rshs, cat_handler):
        self.label_this = label_this
        self.rshs = rshs
        self.cat_handler = cat_handler

    def __call__(self, *args):
        # Almost nothing written to log file by default if an exception is raised here.
        try:
            return self._do_call(*args)
        except:
            Errlog.log(traceback.format_exc())
            raise

    def _do_call(self, x, y, fmt_x, fmt_y, v, *argv):

        if argv:
            row1 = "{}: {} ({})".format(self.label_this, argv[0], basics.percentage_string(*argv))
        else:
            row1 = "{}: {}".format(self.label_this, v)

        res = []
        res.append(row1)
        res.append("")
        res.append(fmt_x)
        res.append(fmt_y)
        res.append("")
        report_rules.MyDiagramTooltip.add_tooltip_common_to_str_list(res, self.rshs[(x, y)], self.cat_handler)
        return "\n".join(res)

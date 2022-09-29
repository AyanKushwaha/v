from __future__ import absolute_import
from __future__ import division
from six.moves import map
from six.moves import range
from six.moves import zip

import math
from collections import defaultdict

from Localization import MSGR
import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave

from carmusr.calibration.util import calibration_rules as calib_rules
from carmusr.calibration.util import report_rules
from carmusr.calibration.util import report_util as ru
from carmusr.calibration.util import basics

VALUE_IX = 1
DIFF_IX = 2
LIMIT_IX = 3


class RuleValueDistribution(report_rules._RuleAnalysisReport):

    RULE_PARAM = 'report_calibration.dist_rule'

    @staticmethod
    def get_basic_header_text():
        return ru.CalibReports.RVD.title

    def get_header_text(self):
        return self.get_basic_header_text() + (MSGR(" - Table View") if self.is_table_view() else "")

    @staticmethod
    def get_form_handler(_variant):
        from carmusr.calibration.util import report_forms as rf
        return rf.rvd_param_form_handler

    @staticmethod
    def get_rule_key():
        ix_rule, = rave.eval(RuleValueDistribution.RULE_PARAM)
        return "%s" % ix_rule

    def create(self):

        self.setpaper(orientation=prt.LANDSCAPE, size=prt.A3 if self.is_table_view() else prt.A4)

        super(RuleValueDistribution, self).create()

        self.set_skip_reason_and_create_cr()
        if self.skip_reason is not None:
            self.add_warnings_and_links()
            return

        rule_str = self.arg("rule") or RuleValueDistribution.get_rule_key()

        if rule_str not in self.cr.all_rules_dict:
            self.add_warning_text(MSGR("No rule selected to analyse"))
            self.add_warnings_and_links()
            return

        self.add_link_to_rule_details_report_for_rule = rule_str

        self.cri = self.cr.get_rule_item(rule_str)

        self.populate_data()

        self.add_warnings_and_links()

        self.generate_settings_table()

        self.add(prt.Isolate(report_rules.get_summary_table(self.rule_summary_handler, self.cri, self.current_area, self.cat_handler)))
        self.add("")
        self.page()

        if not self.values:
            return

        self.add_rule_statistics_table()
        self.add("")
        self.page()

        if self.is_table_view():
            self.add_dist_tables()
        else:
            self.add_dist_diagrams()

    def populate_data(self):
        self.limits = []
        self.values = []
        self.diffs = []
        self.crew_multipliers = []
        self.rule_summary_handler = report_rules.RuleSummaryHandler()
        self.value_dist = defaultdict(report_rules.RuleSummaryHandler)
        self.diff_dist = defaultdict(report_rules.RuleSummaryHandler)

        self.bin_value = getattr(self.cri, calib_rules.BIN).value()

        poc = report_rules.PlanningObjectCreator(self, self.cri)
        self.cat_handler = poc.cat_handler

        for po, _bag in poc.get_objects_and_bags():

            if not po.is_valid:
                self.rule_summary_handler.add_from_po(po)
                continue

            self.limits.append(po.limit)
            self.values.append(po.value)
            self.diffs.append(po.diff)
            self.crew_multipliers.append(po.num_crew)

            extra_value_tuple = (po.num_crew * int(po.value), po.num_crew * int(po.diff), po.num_crew * int(po.limit))

            self.rule_summary_handler.add_from_po(po, additional_values_for_valid_legal_and_illegal=extra_value_tuple)
            self.value_dist[self.get_bin_id(po.value)].add_from_po(po, skip_selected=True)
            self.diff_dist[self.get_bin_id(po.diff)].add_from_po(po, skip_selected=True)

    def add_rule_statistics_table(self):
        percentiles = (1, 5, 10, 25, 50, 75, 90, 95, 99)

        table = ru.SimpleTable(MSGR("Rule Statistics"), use_page=False)
        for h in ["", MSGR("Average"), MSGR("Min")] + ["%s%%" % p for p in percentiles] + [MSGR("Max")]:
            table.add_sub_title(prt.Text(h, align=prt.RIGHT, valign=prt.BOTTOM))

        table.add_sub_title(prt.Column(prt.Text(MSGR("Total"), align=prt.CENTER),
                                       ru.SimpleTableRow(prt.Text(MSGR("Illegal"), align=prt.RIGHT),
                                                         prt.Text(MSGR("Legal"), align=prt.RIGHT),
                                                         prt.Text(MSGR("Valid"), align=prt.RIGHT)),
                                       border=prt.border(left=1)))

        self.add_statistics_row(table, MSGR("Limit:"), self.limits, percentiles, LIMIT_IX)
        self.add_statistics_row(table, MSGR("Value:"), self.values, percentiles, VALUE_IX)
        self.add_statistics_row(table, MSGR("Difference:"), self.diffs, percentiles, DIFF_IX)

        self.add(prt.Isolate(table))

    def add_statistics_row(self, table, heading, value_list, perc, value_index):
        # workaround: Some numpy functions like percentile don't work well with RelTime interpolation
        value_type = type(value_list[0])
        value_list_int = list(map(int, value_list))

        value_list_int_crew_adjusted = []
        for val, crew in zip(value_list_int, self.crew_multipliers):
            value_list_int_crew_adjusted += [val] * crew

        row = table.add(prt.Text(heading, align=prt.LEFT, font=ru.BOLD))
        row.add(prt.Text("%s" % value_type(basics.round_to_int(basics.mean(value_list_int_crew_adjusted))), align=prt.RIGHT))
        row.add(prt.Text("%s" % min(value_list), align=prt.RIGHT))

        percentiles = [value_type(basics.round_to_int(p)) for p in basics.percentile(value_list_int_crew_adjusted, perc)]
        for p in percentiles:
            row.add(prt.Text("%s" % p, align=prt.RIGHT))

        row.add(prt.Text("%s" % max(value_list), align=prt.RIGHT, border=prt.border(right=1)))

        row.add(prt.Text(value_type(self.rule_summary_handler.illegal.values[value_index]),
                         align=prt.RIGHT,
                         action=ru.get_select_action(self.current_area, self.rule_summary_handler.illegal.leg_ids)))
        row.add(prt.Text(value_type(self.rule_summary_handler.legal.values[value_index]),
                         align=prt.RIGHT,
                         action=ru.get_select_action(self.current_area, self.rule_summary_handler.legal.leg_ids)))
        row.add(prt.Text(value_type(self.rule_summary_handler.valid.values[value_index]),
                         align=prt.RIGHT,
                         action=ru.get_select_action(self.current_area, self.rule_summary_handler.valid.leg_ids)))

    def add_dist_tables(self):
        kwargs = dict(total_rsh=self.rule_summary_handler,
                      current_area=self.current_area,
                      cat_handler=self.cat_handler,
                      binkey2label=self.bin2prt_label_object)
        self.add(prt.Isolate(report_rules.get_per_bin_table(*self.get_args_rvd(), **kwargs)))
        self.add("")
        self.page()
        self.add(prt.Isolate(report_rules.get_per_bin_table(*self.get_args_rdd(), **kwargs)))

    def add_dist_diagrams(self):
        kwargs = dict(current_area=self.current_area,
                      cat_handler=self.cat_handler,
                      xkey2label=self.bin2label)
        self.add(prt.Isolate(report_rules.get_single_rule_diagram(*self.get_args_rvd(), **kwargs)))
        self.add("")
        self.page()
        self.add(prt.Isolate(report_rules.get_single_rule_diagram(*self.get_args_rdd(), **kwargs)))

    def get_args_rvd(self):
        return (MSGR("Rule Value Distribution"),
                range(self.get_bin_id(min(self.values)), self.get_bin_id(max(self.values)) + 1),
                self.value_dist,
                MSGR("Value"))

    def get_args_rdd(self):
        return (MSGR("Rule Difference Distribution"),
                range(self.get_bin_id(min(self.diffs)), self.get_bin_id(max(self.diffs)) + 1),
                self.diff_dist,
                MSGR("Difference"))

    def get_bin_id(self, value):
        return int(math.floor((value - self.cri.min_diff_for_bin_one) / self.bin_value))

    def get_bin_start_and_end(self, bin_):
        bin_start = self.bin_value * bin_ + self.cri.min_diff_for_bin_one
        # Each bin ends one unit before the next starts
        bin_end = bin_start + self.bin_value - self.cri.bin_resolution
        return bin_start, bin_end

    def bin2label(self, bin_):
        bin_start, bin_end = self.get_bin_start_and_end(bin_)
        if bin_start == bin_end:
            return "%5s" % bin_start
        return "%5s  -  %5s" % (bin_start, bin_end)

    def bin2prt_label_object(self, bin_):
        bin_start, bin_end = self.get_bin_start_and_end(bin_)
        if bin_start == bin_end:
            return ru.SimpleTableRow(prt.Text(bin_start, align=prt.RIGHT, colspan=3))
        return ru.SimpleTableRow(prt.Text(bin_start, align=prt.RIGHT),
                                 "-",
                                 bin_end)

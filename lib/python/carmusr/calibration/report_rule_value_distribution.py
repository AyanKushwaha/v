
import math
from collections import defaultdict

from Localization import MSGR
import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave
import Cui

from carmusr.calibration.mappings import studio_palette
from carmusr.calibration.util import calibration_rules as calib_rules
from carmusr.calibration.util import complement
from carmusr.calibration.util import report_rules
from carmusr.calibration.util import report_util as ru
from carmusr.calibration.util import basics


class RuleValueDistribution(report_rules._RuleAnalysisReport):

    RULE_PARAM = 'report_calibration.dist_rule'

    @staticmethod
    def get_basic_header_text():
        return ru.CalibReports.RVD.title

    def get_header_text(self):
        return self.get_basic_header_text() + (MSGR(" - Table View") if self.arg('show') == "TABLE" else "")

    @staticmethod
    def get_form_handler(_variant):
        from carmusr.calibration.util import report_forms as rf
        return rf.rvd_param_form_handler

    @staticmethod
    def get_rule_key():
        ix_rule, = rave.eval(RuleValueDistribution.RULE_PARAM)
        return "%s" % ix_rule

    def __init__(self, *args, **kw):

        super(RuleValueDistribution, self).__init__(*args, **kw)

        self.legals = []
        self.limits = []
        self.values = []
        self.diffs = []
        self.identifiers = []
        self.crew_multipliers = []
        self.total_illegal_diff = None
        self.value_zero = None
        self.valid_identifiers = []
        self.illegal_identifiers = []

        self.cri = None
        self.bin_value = None

        self.diff_bins = None
        self.diff_dist = (defaultdict(int), defaultdict(int))
        self.diff_identifiers = (defaultdict(list), defaultdict(list))

        self.value_bins = None
        self.value_dist = (defaultdict(int), defaultdict(int))
        self.value_identifiers = (defaultdict(list), defaultdict(list))

    def create(self):

        self.setpaper(orientation=prt.LANDSCAPE)

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
        my_bags = self.get_bags_for_cri_and_write_warning_once(self.cri)

        self.populate_data(my_bags)

        self.add_warnings_and_links()

        self.generate_settings_table()

        self.add_overview_table()
        if not self.values:
            return

        self.add("")
        self.add_rule_statistics_table()
        self.add("")
        self.page()

        if self.arg('show') == "TABLE":
            self.add_dist_tables()
        else:
            self.add_dist_diagrams()

    def get_bin_id(self, value):
        return int(math.floor((value - self.cri.min_diff_for_bin_one) / self.bin_value))

    def append_to_lists(self, is_legal, limit, value, diff, identifiers, crew_multiplier):
        self.legals.append(is_legal)
        self.limits.append(limit)
        self.values.append(value)
        self.diffs.append(diff)
        self.identifiers.append(identifiers)
        self.crew_multipliers.append(crew_multiplier)

    def populate_data(self, my_set):
        is_valid_var = getattr(self.cri, calib_rules.IS_VALID).rave_obj
        limit_var = getattr(self.cri, calib_rules.LIMIT).rave_obj
        value_var = getattr(self.cri, calib_rules.VALUE).rave_obj
        rule_body_expr = self.cri.rule_body_expr

        self.bin_value = getattr(self.cri, calib_rules.BIN).value()
        self.value_zero = type(self.bin_value)(0)
        self.total_illegal_diff = self.value_zero

        for bag in my_set:
            is_valid, = rave.eval(bag, is_valid_var)
            if not is_valid:
                continue

            is_legal, = rave.eval(bag, rule_body_expr)
            if is_legal is None:
                continue

            if self.current_area_mode in (Cui.AcRotMode, Cui.LegMode):
                num_crew_multiplier = 1
            else:
                num_crew_multiplier = complement.CrewPosFilter.filtered_complement_sum(bag)
            if not num_crew_multiplier:
                continue

            limit, value = rave.eval(bag, limit_var, value_var)

            abs_diff = abs(limit - value)
            diff = abs_diff if is_legal else -abs_diff

            leg_identifiers = [leg_bag.leg_identifier() for leg_bag in bag.atom_set()]

            self.valid_identifiers += leg_identifiers
            if not is_legal:
                self.illegal_identifiers += leg_identifiers
                self.total_illegal_diff += (diff * num_crew_multiplier)

            # Append data to all lists
            self.append_to_lists(is_legal,
                                 limit,
                                 value,
                                 diff,
                                 leg_identifiers,
                                 num_crew_multiplier)

            key = self.get_bin_id(diff)
            self.diff_dist[int(is_legal)][key] += num_crew_multiplier
            self.diff_identifiers[int(is_legal)][key] += leg_identifiers

            key = self.get_bin_id(value)
            self.value_dist[int(is_legal)][key] += num_crew_multiplier
            self.value_identifiers[int(is_legal)][key] += leg_identifiers

        if len(self.diffs) and len(self.values):
            diff_min = min(self.diffs)
            diff_max = max(self.diffs)
            self.diff_bins = range(self.get_bin_id(diff_min),
                                   self.get_bin_id(diff_max) + 1)

            value_min = min(self.values)
            value_max = max(self.values)
            self.value_bins = range(self.get_bin_id(value_min),
                                    self.get_bin_id(value_max) + 1)

    def add_overview_table(self):
        table = ru.SimpleTable(MSGR("Rule Overview"), use_page=False)

        row = table.add(prt.Text(MSGR("Rule:"),
                                 align=prt.LEFT,
                                 font=ru.BOLD))
        row.add(prt.Text(self.cri.rule_label, align=prt.LEFT))

        row = table.add(prt.Text(MSGR("Bin size parameter:"),
                                 align=prt.LEFT,
                                 font=ru.BOLD))

        row.add(prt.Text("%s (%s)" % (getattr(self.cri, calib_rules.BIN).remark(), self.bin_value), align=prt.LEFT))

        num = 0
        num_illegal = 0
        for (is_legal, crew) in zip(self.legals, self.crew_multipliers):
            num += crew
            num_illegal += crew - is_legal * crew

        valid_action = prt.action(ru.calib_show_and_mark_legs,
                                  (self.current_area, self.valid_identifiers))
        row = table.add(prt.Text(MSGR("Number of valid:"),
                                 align=prt.LEFT,
                                 font=ru.BOLD))
        row.add(prt.Text("%s" % num, align=prt.LEFT, action=valid_action))

        illegal_action = prt.action(ru.calib_show_and_mark_legs,
                                    (self.current_area, self.illegal_identifiers))
        row = table.add(prt.Text(MSGR("Number of illegal:"),
                                 align=prt.LEFT,
                                 font=ru.BOLD))
        row.add(prt.Text("%s" % num_illegal, align=prt.LEFT, action=illegal_action))

        row = table.add(prt.Text(MSGR("Total value:"),
                                 align=prt.LEFT,
                                 font=ru.BOLD))

        total_value = self.value_zero
        for (val, crew) in zip(self.values, self.crew_multipliers):
            total_value += val * crew

        row.add(prt.Text("%s" % total_value, align=prt.LEFT))

        sum_diff = self.value_zero
        for (diff, crew) in zip(self.diffs, self.crew_multipliers):
            sum_diff += diff * crew

        sum_legal = sum_diff - self.total_illegal_diff

        row = table.add(prt.Text(MSGR("Total difference (illegal / legal):"),
                                 align=prt.LEFT,
                                 font=ru.BOLD))
        row.add(prt.Text(("%s (%s / %s)" % (sum_diff, self.total_illegal_diff, sum_legal)), align=prt.LEFT))

        self.add(prt.Isolate(table))

    def add_summary_row(self, table, heading, value_list, perc):
        # workaround: Some numpy functions like percentile don't work well with RelTime interpolation
        value_type = type(value_list[0])
        value_list_int = map(int, value_list)

        value_list_int_crew_adjusted = []
        for (val, crew) in zip(value_list_int, self.crew_multipliers):
            value_list_int_crew_adjusted += [val] * crew

        row = table.add(prt.Text(heading, align=prt.LEFT, font=ru.BOLD))
        row.add(prt.Text("%s" % value_type(round(basics.mean(value_list_int_crew_adjusted))), align=prt.RIGHT))
        row.add(prt.Text("%s" % min(value_list), align=prt.RIGHT))

        percentiles = map(lambda p: value_type(round(p)), basics.percentile(value_list_int_crew_adjusted, perc))
        for p in percentiles:
            row.add(prt.Text("%s" % p, align=prt.RIGHT))

        row.add(prt.Text("%s" % max(value_list), align=prt.RIGHT))

    def add_rule_statistics_table(self):
        title = MSGR("Rule Statistics")
        percentiles = (1, 5, 10, 25, 50, 75, 90, 95, 99)
        headings = ["", MSGR("Average"), MSGR("Min")] + ["%s%%" % p for p in percentiles] + [MSGR("Max")]

        table = ru.SimpleTable(title, use_page=False)
        for h in headings:
            table.add_sub_title(prt.Text(h, align=prt.RIGHT))

        self.add_summary_row(table, MSGR("Limit:"), self.limits, percentiles)
        self.add_summary_row(table, MSGR("Value:"), self.values, percentiles)
        self.add_summary_row(table, MSGR("Difference:"), self.diffs, percentiles)

        self.add(prt.Isolate(table))

    def add_dist_tables(self):
        value_table_head, value_table_rows = self.get_dist_table(*self.get_args_rvd())
        diff_table_head, diff_table_rows = self.get_dist_table(*self.get_args_rdd())
        # We must put the two tables in one Column to allow page breaks in PDF.
        table_column = prt.Column()
        self.add(prt.Isolate(table_column))
        table_column.add(prt.Row(value_table_head, " ", diff_table_head))
        len_val = len(value_table_rows)
        len_dif = len(diff_table_rows)
        get_dummy_obj = lambda: prt.Text("", background=studio_palette.White, colspan=6)
        for ix in xrange(max(len_val, len_dif)):
            table_column.add(prt.Row(value_table_rows[ix] if ix < len_val else get_dummy_obj(),
                                     prt.Text(" ", background=studio_palette.White),
                                     diff_table_rows[ix] if ix < len_dif else get_dummy_obj(),
                                     background=ru.SimpleTable.get_background_color_for_row(ix)))
            table_column.page0()

    def get_dist_table(self, title, bins, dist, identifiers):
        dist_table = ru.SimpleTable(title, use_page=False)
        dist_table.add_sub_title(prt.Text(MSGR("Range"), colspan=3))
        dist_table.add_sub_title(prt.Text(MSGR("Number of  Illegal"), width=100, align=prt.RIGHT))
        dist_table.add_sub_title(prt.Text(MSGR("Legal")))
        dist_table.add_sub_title(prt.Text(MSGR("Valid")))
        dist_table_rows = []

        # bins are either int or RelTime.
        for bin_ in bins:
            bin_start, bin_end = self.get_bin_start_and_end(bin_)
            num_legal, num_illegal = self.get_num_legal_and_illegal(bin_, dist)
            legal_identifiers, illegal_identifiers = self.get_identfiers_legal_and_illegal(bin_, identifiers)

            table_action_legal = ru.get_select_action(self.current_area, legal_identifiers)
            table_action_illegal = ru.get_select_action(self.current_area, illegal_identifiers)
            table_action_both = ru.get_select_action(self.current_area, legal_identifiers + illegal_identifiers)

            # Note: Colspan in 'get_dummy_obj' must match the number of items here.
            row = ru.SimpleTableRow(prt.Text(bin_start, align=prt.RIGHT),
                                    border=prt.border(colour=ru.SIMPLE_TABLE_BORDER_GREY, left=1, right=1,
                                                      bottom=1 if bin_ == bins[-1] else None))
            row.add("-")
            row.add(bin_end)
            row.add(prt.Text("%s" % num_illegal, action=table_action_illegal, align=prt.RIGHT))
            row.add(prt.Text("%s" % num_legal, action=table_action_legal, align=prt.RIGHT))
            row.add(prt.Text("%s" % (num_legal + num_illegal), action=table_action_both, align=prt.RIGHT))
            dist_table_rows.append(row)

        return dist_table, dist_table_rows

    def add_dist_diagrams(self):
        self.add_dist_diagram(*self.get_args_rvd())
        self.add("")
        self.page()
        self.add_dist_diagram(*self.get_args_rdd())

    def add_dist_diagram(self, title, bins, dist, identifiers):
        current_area = self.current_area

        data_legal = []
        data_illegal = []
        legal_identifiers_x = {}
        illegal_identifiers_x = {}
        # bins are either int or RelTime.
        for bin_ in bins:
            bin_start, bin_end = self.get_bin_start_and_end(bin_)
            bin_label = "%5s  -  %5s" % (bin_start, bin_end)

            num_legal, num_illegal = self.get_num_legal_and_illegal(bin_, dist)
            data_legal.append((bin_label, num_legal))
            data_illegal.append((bin_label, num_illegal))

            legal_identifiers, illegal_identifiers = self.get_identfiers_legal_and_illegal(bin_, identifiers)
            legal_identifiers_x[bin_label] = legal_identifiers
            illegal_identifiers_x[bin_label] = illegal_identifiers

        action_legal = prt.chartaction(lambda x, _, idx=legal_identifiers_x:
                                       ru.calib_show_and_mark_legs(current_area, idx[x]))
        action_illegal = prt.chartaction(lambda x, _, idx=illegal_identifiers_x:
                                         ru.calib_show_and_mark_legs(current_area, idx[x]))

        serie_illegal = prt.Series(data_illegal,
                                   graph=prt.Bar(width=1, fill=studio_palette.JeppesenBlue),
                                   legends=[(MSGR("Illegal"), studio_palette.JeppesenBlue)],
                                   action=action_illegal,
                                   tooltip=prt.charttooltip(report_rules.Tooltip(MSGR("bin size / # illegal"))))
        serie_legal = prt.Series(data_legal,
                                 legends=[(MSGR("Legal"), studio_palette.ReportBlue)],
                                 graph=prt.Bar(width=1, fill=studio_palette.ReportBlue),
                                 action=action_legal,
                                 tooltip=prt.charttooltip(report_rules.Tooltip(MSGR("bin size / # legal"))))

        chart = ru.SimpleDiagram(prt.Text(MSGR(title), valign=prt.CENTER))
        num_x_values = len(bins)
        rotate_tags = num_x_values > 8
        tic_values = set([it[0] for it in data_legal][0::report_rules.get_x_tics_divider(num_x_values)])
        xaxis_format = lambda v: v if v in tic_values else ""
        chart.add(prt.Isolate(prt.Chart(report_rules.get_chart_width(num_x_values),
                                        report_rules.CHART_HEIGHT,
                                        prt.Combine(serie_illegal, serie_legal,
                                                    yaxis_name=MSGR("Frequency"),
                                                    on_top=True),
                                        xaxis_name=MSGR(title),
                                        background=studio_palette.White,
                                        xaxis_rotate_tags=rotate_tags,
                                        xaxis_format=xaxis_format)))
        self.add(prt.Isolate(chart))

    def get_args_rvd(self):
        return (MSGR("Rule Value Distribution"),
                self.value_bins,
                self.value_dist,
                self.value_identifiers)

    def get_args_rdd(self):
        return (MSGR("Rule Difference Distribution"),
                self.diff_bins,
                self.diff_dist,
                self.diff_identifiers)

    def get_bin_start_and_end(self, bin_):
        bin_start = self.bin_value * bin_ + self.cri.min_diff_for_bin_one
        # Each bin ends one unit before the next starts
        bin_end = bin_start + self.bin_value - self.cri.bin_resolution
        return bin_start, bin_end

    def get_num_legal_and_illegal(self, bin_, dist):
        return dist[1].get(bin_, 0), dist[0].get(bin_, 0)

    def get_identfiers_legal_and_illegal(self, bin_, identifiers):
        return identifiers[1].get(bin_, []), identifiers[0].get(bin_, [])

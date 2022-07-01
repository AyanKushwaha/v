
import math
from collections import defaultdict

from Localization import MSGR
import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave
import Cui

from carmusr.calibration.mappings import date_extensions as de
from carmusr.calibration.util import complement
from carmusr.calibration.util import basics
from carmusr.calibration.util import report_rules
from carmusr.calibration.util import report_util as ru
from carmusr.calibration.util import calibration_rules as cr


class RuleViolationsOverWeekdays(report_rules._RuleViolations):

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

        self.setpaper(orientation=prt.LANDSCAPE)
        super(RuleViolationsOverWeekdays, self).create()

        self.set_skip_reason_and_create_cr()

        if self.skip_reason is not None:
            self.add_warnings_and_links()
            return

        bins_per_day = rave.param("report_calibration.vow_bins_per_day").value()
        self.bin_size = basics.ONE_DAY / bins_per_day
        self.gamma = float(rave.param("report_calibration.vow_centi_gamma").value()) / 100

        rule_str = self.arg("rule") or self.get_rule_key()
        tzh = report_rules.TimeZoneHandler()

        if rule_str not in self.cr.all_rules_dict:
            self.add_warning_text(MSGR("No rule selected to analyse"))
            self.add_warnings_and_links()
            return

        self.add_link_to_rule_details_report_for_rule = rule_str

        cri = self.cr.get_rule_item(rule_str)
        level = cri.rule_level
        my_bags = self.get_bags_for_cri_and_write_warning_once(cri)

        self.my_rule_body_expr = cri.rule_body_expr
        self.rule_label = cri.rule_label
        is_valid_var = getattr(cri, cr.IS_VALID).rave_obj

        limit_var = getattr(cri, cr.LIMIT).rave_obj
        value_var = getattr(cri, cr.VALUE).rave_obj
        self.bin_value, = rave.eval(getattr(cri, cr.BIN))

        self.violations = defaultdict(lambda: [int(), list()])
        self.valid = defaultdict(lambda: [int(), list()])
        self.in_first_bin = defaultdict(lambda: [int(), list()])

        for bag in my_bags:

            is_valid, = rave.eval(bag, is_valid_var)
            if not is_valid:
                continue

            is_legal, = rave.eval(bag, self.my_rule_body_expr)
            if is_legal is None:
                # Void rules body count as void valid, i.e. not at all
                continue
            if self.current_area_mode in (Cui.AcRotMode, Cui.LegMode):
                num_crew = 1
            else:
                num_crew = complement.CrewPosFilter.filtered_complement_sum(bag)
            if num_crew == 0:
                continue

            identifiers = [leg_bag.leg_identifier() for leg_bag in bag.atom_set()]
            rule_time = tzh.get_rule_failure_time(bag, level)

            time_of_day_key = int(rule_time.time_of_day() / self.bin_size) * self.bin_size
            weekday_ix = int(rule_time.time_of_week() / basics.ONE_DAY) + 1

            self.valid[(weekday_ix, time_of_day_key)][0] += num_crew
            self.valid[(weekday_ix, time_of_day_key)][1] += identifiers

            if not is_legal:
                self.violations[(weekday_ix, time_of_day_key)][0] += num_crew
                self.violations[(weekday_ix, time_of_day_key)][1] += identifiers
            else:
                limit, value = rave.eval(bag, limit_var, value_var)
                diff = abs(limit - value)
                if diff <= cri.max_diff_for_bin_one:
                    self.in_first_bin[(weekday_ix, time_of_day_key)][0] += num_crew
                    self.in_first_bin[(weekday_ix, time_of_day_key)][1] += identifiers

        if not self.valid:
            self.add_warning_text(MSGR("No selected planning object is valid for rule '{}'.").format(cri.rule_label))

        self.add_warnings_and_links()
        self.generate_settings_table()
        if not self.valid:
            return
        self.add_summary_table()
        self.add_heatmaps()

    def get_settings_table(self):
        table = self.get_empty_settings_table()
        self.add_lookback_parameter_setting_to_prt_table(table)
        self.add_crew_pos_filter_to_settings_table(table)
        report_rules.add_time_stuff_to_settings_table(table)
        return table

    def add_summary_table(self):
        vd = report_rules.ViolationData()
        vd.num_valid = sum(v for v, _ in self.valid.itervalues())
        vd.valid_identifier_list = reduce(list.__add__, (ids for _, ids in self.valid.itervalues()), list())

        vd.num_illegal = sum(v for v, _ in self.violations.itervalues())
        vd.illegal_identifier_list = reduce(list.__add__, (ids for _, ids in self.violations.itervalues()), list())

        vd.num_in_bin = sum(v for v, _ in self.in_first_bin.itervalues())
        vd.in_bin_identifier_list = reduce(list.__add__, (ids for _, ids in self.in_first_bin.itervalues()), list())

        vd.rule_title = self.rule_label
        vd.bin = self.bin_value

        summary_table = self.generate_summary_header(False)
        self.generate_summary_for_one_rule(summary_table, vd, False)
        self.add(prt.Isolate(summary_table))
        self.add("")

    def add_heatmaps(self):

        def get_one_heatmap_common(*args, **kw):

            return ru.Heatmap(self.current_area,
                              *args,
                              keyname_x=MSGR("Weekday"),
                              keyname_y=MSGR("Time of day"),
                              x_keys=[7] + range(1, 7),
                              y_keys=[v * self.bin_size for v in range(int(math.ceil(float(int(basics.ONE_DAY)) / float(int(self.bin_size)))))],
                              x_key_format=de.day_num2gui_weekday_short_name,
                              y_key_format=lambda v: "%s - %s" % (v, min(basics.ONE_DAY, v + self.bin_size) - basics.ONE_MINUTE),
                              show_total_row=True,
                              show_total_col=True,
                              gamma=self.gamma,
                              value_col_min_width=60,
                              **kw)

        def get_one_heatmap_with_divider(title, values):
            return get_one_heatmap_common(title,
                                          values,
                                          dividerdict=self.valid,
                                          max_colour_value=1.0)

        col = prt.Column()
        self.add(prt.Isolate(col))
        if self.violations:
            col.add(get_one_heatmap_with_divider(MSGR("Violations"), self.violations))
            col.add("")
            col.page()

        if self.in_first_bin:
            col.add(get_one_heatmap_with_divider(MSGR("In 1st bin"), self.in_first_bin))
            col.add("")
            col.page()

        if self.valid:
            hm = get_one_heatmap_common(MSGR("Valid"),
                                        self.valid,
                                        max_colour="#4477AA")
            self.add(prt.Isolate(hm))

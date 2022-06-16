
from Localization import MSGR
import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave
import Cui

from carmusr.calibration.mappings import date_extensions as de
from carmusr.calibration.mappings import report_generation as rg
from carmusr.calibration.mappings import studio_palette
from carmusr.calibration.util import compare_plan
from carmusr.calibration.util import basics
from carmusr.calibration.util import report_rules
from carmusr.calibration.util import report_util as ru
from carmusr.calibration.util import calibration_rules as cr


class RuleViolationsOverTime(report_rules._RuleViolationsOverStationOrTime):

    @staticmethod
    def get_basic_header_text():
        return ru.CalibReports.VOT.title

    def get_header_text(self):
        return self.get_basic_header_text() + (MSGR(" - Table View") if self.arg('show') == "TABLE" else "")

    @staticmethod
    def get_form_handler(_variant):
        from carmusr.calibration.util import report_forms as rf
        return rf.vot_param_form_handler

    @staticmethod
    def get_rule_key(i=1):
        param_variable = 'report_calibration.%%vot_rule_%d%%' % i
        ix_rule, = rave.eval(param_variable)
        return "%s" % ix_rule

    def __init__(self, *args, **kw):
        report_rules._RuleViolationsOverStationOrTime.__init__(self, *args, **kw)
        self.violation_data_list = []
        self.min_day = None
        self.max_day = None

    def show_categories_in_summary(self):
        return len(self.violation_data_list) == 1 and self.violation_data_list[0].cat_handler.has_categories()

    def create(self):
        self.setpaper(orientation=prt.LANDSCAPE)

        super(RuleViolationsOverTime, self).create()

        self.set_skip_reason_and_create_cr()

        if self.skip_reason is not None:
            self.add_warnings_and_links()
            return

        if self.arg("rule"):
            rules = [self.arg("rule")]
            if rules[0] not in self.cr.all_rules_dict:
                self.add_warning_text(MSGR("The selected rule, {}, does not exist").format(rules[0]))
                self.add_warnings_and_links()
                return
        else:
            rules = [rule_key for rule_key in (self.get_rule_key(ix) for ix in range(1, 5))
                     if rule_key in self.cr.all_rules_dict]

            if len(rules) == 0:
                self.add_warning_text(MSGR("No rule selected to analyse"))
                self.add_warnings_and_links()
                return

        if len(rules) == 1:
            self.add_link_to_rule_details_report_for_rule = rules[0]

        self.start_day_ref = rave.eval(rave.keyw("global_lp_period_start"))[0]
        tzh = report_rules.TimeZoneHandler()

        for rule_str in rules:

            cri = self.cr.get_rule_item(rule_str)
            my_bags = self.get_bags_for_cri_and_write_warning_once(cri)
            level = cri.rule_level
            my_rule_body_expr = cri.rule_body_expr

            comp_key_var, cat_handler = self.get_comp_key_and_cat_handler(cri)
            violation_data = report_rules.ViolationData(cat_handler)

            is_valid_var = getattr(cri, cr.IS_VALID).rave_obj
            limit_var = getattr(cri, cr.LIMIT).rave_obj
            value_var = getattr(cri, cr.VALUE).rave_obj
            bin_value = getattr(cri, cr.BIN).value()

            for bag in my_bags:
                is_valid, = rave.eval(bag, is_valid_var)
                if not is_valid:
                    # False or void
                    continue
                is_legal, = rave.eval(bag, my_rule_body_expr)
                if is_legal is None:
                    # Void rules body count as void valid, i.e. not at all
                    continue

                if self.current_area_mode in (Cui.AcRotMode, Cui.LegMode):
                    tripslice_or_crew_comp = 1
                    num_crew = 1
                else:
                    tripslice_or_crew_comp = compare_plan.filtered_slice_from_bag(comp_key_var, bag)
                    num_crew = tripslice_or_crew_comp.complement_sum()

                if num_crew == 0:
                    continue

                day_in_pp = int(tzh.get_rule_failure_time(bag, level) - self.start_day_ref) / 1440
                self.min_day = min(day_in_pp, self.min_day) if self.min_day is not None else day_in_pp
                self.max_day = max(day_in_pp, self.max_day) if self.max_day is not None else day_in_pp
                gui_date_str = self.get_gui_date_str_from_pp_day(day_in_pp)
                identifiers = [leg_bag.leg_identifier() for leg_bag in bag.atom_set()]
                violation_data.add_valid(day_in_pp, num_crew, gui_date_str, identifiers)

                if not is_legal:
                    subcat, cats_and_crew = cat_handler.get_and_register_cat(bag, tripslice_or_crew_comp)
                    for cat, ncrew in cats_and_crew:
                        violation_data.add_illegal(cat, subcat, ncrew, day_in_pp, gui_date_str, identifiers)
                else:
                    limit, value = rave.eval(bag, limit_var, value_var)
                    diff = abs(limit - value)
                    if diff <= cri.max_diff_for_bin_one:
                        violation_data.add_in_bin(day_in_pp, num_crew, gui_date_str, identifiers)
            # end of bag loop

            violation_data.rule_title = cri.rule_label
            violation_data.rule_str = rule_str
            violation_data.level = level
            violation_data.bin = bin_value
            self.violation_data_list.append(violation_data)
        # end of rule iteration

        self.add_warnings_and_links()
        self.generate_settings_table()
        self.generate_summary()
        self.page()

        if self.min_day is not None and self.max_day is not None:
            self.day_list, self.days_num_in_pp = self.get_day_lists(self.min_day, self.max_day)
            # we have at least one valid object selected
            if self.arg('show') == "TABLE":
                self.add_details_tables()
            else:
                self.generate_diagrams()

    def get_settings_table(self):
        table = super(RuleViolationsOverTime, self).get_settings_table()
        report_rules.add_time_stuff_to_settings_table(table)
        return table

    def add_details_tables(self):

        for vdata in self.violation_data_list:
            full_details_table = self.get_details_table_with_header(MSGR("Rule Violations per Day"), MSGR("Date"), vdata)

            illeg_list = report_rules.get_counter_values_as_list(self.days_num_in_pp, vdata.illegal_dim_cnt)
            valid_list = report_rules.get_counter_values_as_list(self.days_num_in_pp, vdata.valid_dim_cnt)
            in_bin_list = report_rules.get_counter_values_as_list(self.days_num_in_pp, vdata.in_bin_dim_cnt)

            for day_ix, day_str in enumerate(self.day_list):
                self.add_data_row(full_details_table, day_str,
                                  illeg_list[day_ix], in_bin_list[day_ix], valid_list[day_ix],
                                  vdata.illegal_identifier_dim_dict[day_str], vdata.in_bin_identifier_dim_dict[day_str],
                                  vdata.valid_identifier_dim_dict[day_str], vdata.cat_handler,
                                  {lb_cat: vdata.illegal_cat_dim_cnt[lb_cat][self.days_num_in_pp[day_ix]] for lb_cat in vdata.cat_handler.categories},
                                  {lb_cat: vdata.illegal_identifier_cat_dim_dict[lb_cat][self.days_num_in_pp[day_ix]]
                                   for lb_cat in vdata.cat_handler.categories})

            self.add_data_row(full_details_table, MSGR("Total"),
                              vdata.num_illegal, vdata.num_in_bin, vdata.num_valid,
                              vdata.illegal_identifier_list, vdata.in_bin_identifier_list,
                              vdata.valid_identifier_list, vdata.cat_handler,
                              vdata.illegal_cat_cnt, vdata.illegal_identifier_cat_dict,
                              font=ru.BOLD)

            self.add("")
            if len(self.violation_data_list) == 1:
                self.add(prt.Isolate(full_details_table))
            else:
                action = prt.action(lambda m, a, rule_str: rg.display_prt_report(source=m,
                                                                                 area=a,
                                                                                 scope="window",
                                                                                 rpt_args={"show": "OVERVIEW",
                                                                                           "rule": rule_str}),
                                    (self.__module__, self.current_area, vdata.rule_str))
                self.add(prt.Expandable(prt.Text(vdata.rule_title, font=ru.LINK_FONT),
                                        prt.Isolate(prt.Column(prt.Text(""),
                                                               prt.Row(prt.Text(MSGR("Overview"), font=ru.LINK_FONT, action=action),
                                                                       " ",
                                                                       self.get_report_rule_details_link(vdata.rule_str)),
                                                               prt.Text(""),
                                                               full_details_table))))

    def get_chart(self, content):
        num_x_values = len(self.day_list)
        tic_values = set(self.day_list[0::report_rules.get_x_tics_divider(num_x_values)])
        xaxis_format = lambda v: v if v in tic_values else ""
        return prt.Chart(report_rules.get_chart_width(num_x_values),
                         report_rules.CHART_HEIGHT,
                         content,
                         xaxis_rotate_tags=len(self.day_list) > 10,
                         xaxis_name=MSGR("Date"),
                         background=studio_palette.White,
                         xaxis_format=xaxis_format)

    def get_diagrams_and_summary_per_rule(self):

        prt_objects = []
        current_area = self.current_area

        for ix, vdata in enumerate(self.violation_data_list):
            sorted_categories = vdata.cat_handler.get_sorted_categories() or [""]
            s_illeg_nr = []
            s_percentage_nr = []
            if vdata.cat_handler.has_categories():
                totals = {day: vdata.illegal_dim_cnt[day_num]
                          for day, day_num in zip(self.day_list, self.days_num_in_pp)}
            else:
                totals = None
            valid_list = report_rules.get_counter_values_as_list(self.days_num_in_pp, vdata.valid_dim_cnt)

            for lb_cat in sorted_categories:
                illeg_list = report_rules.get_counter_values_as_list(self.days_num_in_pp, vdata.illegal_cat_dim_cnt[lb_cat])
                action = prt.chartaction(lambda x, _, identifier_dict=vdata.illegal_identifier_cat_dim_dict[lb_cat]:
                                         ru.calib_show_and_mark_legs(current_area, identifier_dict[x]))
                bar_j = prt.Bar(width=report_rules.SINGLE_BAR_WIDTH, fill=vdata.cat_handler.bar_color(ix, lb_cat))
                label = lb_cat if lb_cat else vdata.rule_title
                serie_j = prt.Series(zip(self.day_list, illeg_list),
                                     graph=bar_j,
                                     label=label,
                                     action=action,
                                     tooltip=prt.charttooltip(report_rules.Tooltip(vdata.rule_title, totals=totals,
                                                                                   y_label=lb_cat)))
                s_illeg_nr.append(serie_j)

                ratio_per_day = [basics.percentage_value(num_illegal, num_valid)
                                 for num_illegal, num_valid
                                 in zip(illeg_list, valid_list)]
                if vdata.cat_handler.has_categories():
                    ratio_totals = {day: basics.percentage_value(vdata.illegal_dim_cnt[day_num], num_valid)
                                    for day, day_num, num_valid
                                    in zip(self.day_list, self.days_num_in_pp, valid_list)}
                else:
                    ratio_totals = None
                serie_j = prt.Series(zip(self.day_list, ratio_per_day),
                                     graph=bar_j,
                                     label=label,
                                     action=action,
                                     tooltip=prt.charttooltip(report_rules.Tooltip(vdata.rule_title, totals=ratio_totals,
                                                                                   y_fmt=basics.PERC_FMT, y_label=lb_cat)))
                s_percentage_nr.append(serie_j)

            viol_chart_1 = ru.SimpleDiagram(prt.Text(MSGR("Rule Violations Over Time"), valign=prt.CENTER))
            viol_chart_1.add(prt.Isolate(self.get_chart(prt.Combine(on_top=True, yaxis_name=MSGR("Number of violations"), *s_illeg_nr))))

            viol_chart_2 = ru.SimpleDiagram(prt.Text(MSGR("Rule Violations in Percentage of Valid Over Time"),
                                                     valign=prt.CENTER))
            viol_chart_2.add(prt.Isolate(self.get_chart(prt.Combine(on_top=True, yaxis_name=MSGR("Violations in %"), *s_percentage_nr))))

            summary = self.generate_summary_header(vdata.cat_handler.has_categories())
            self.generate_summary_for_one_rule(summary, vdata, vdata.cat_handler.has_categories())

            prt_objects.append((summary, viol_chart_1, viol_chart_2))

        return prt_objects

    def get_multi_rule_diagrams(self):
        current_area = self.current_area
        s_illeg_nr = []
        s_percentage_nr = []

        for ix, vdata in enumerate(self.violation_data_list):
            tot_illegal_list = report_rules.get_counter_values_as_list(self.days_num_in_pp, vdata.illegal_dim_cnt)
            tot_action = prt.chartaction(lambda x, _, identifier_dict=vdata.illegal_identifier_dim_dict:
                                         ru.calib_show_and_mark_legs(current_area, identifier_dict[x]))
            tot_width = min(0.8 / len(self.violation_data_list), report_rules.SINGLE_BAR_WIDTH)
            tot_bar = prt.Bar(width=tot_width,
                              offset=0.1 + ix * tot_width if tot_width < report_rules.SINGLE_BAR_WIDTH else None,
                              fill=compare_plan.COLORS[ix])
            tot_serie_j = prt.Series(zip(self.day_list, tot_illegal_list),
                                     graph=tot_bar,
                                     label=vdata.rule_title,
                                     action=tot_action,
                                     tooltip=prt.charttooltip(report_rules.Tooltip(vdata.rule_title)))
            s_illeg_nr.append(tot_serie_j)
            valid_list = report_rules.get_counter_values_as_list(self.days_num_in_pp, vdata.valid_dim_cnt)
            ratio_per_day = [basics.percentage_value(num_illegal, num_valid)
                             for num_illegal, num_valid
                             in zip(tot_illegal_list, valid_list)]
            tot_serie_j = prt.Series(zip(self.day_list, ratio_per_day),
                                     graph=tot_bar,
                                     label=vdata.rule_title,
                                     action=tot_action,
                                     tooltip=prt.charttooltip(report_rules.Tooltip(vdata.rule_title,
                                                                                   y_fmt=basics.PERC_FMT)))
            s_percentage_nr.append(tot_serie_j)

        viol_chart_1 = ru.SimpleDiagram(prt.Text(MSGR("Rule Violations Over Time"), valign=prt.CENTER))
        viol_chart_1.add(prt.Isolate(self.get_chart(prt.Combine(on_top=False, yaxis_name=MSGR("Number of violations"), *s_illeg_nr))))

        viol_chart_2 = ru.SimpleDiagram(prt.Text(MSGR("Rule Violations in Percentage of Valid Over Time"),
                                                 valign=prt.CENTER))
        viol_chart_2.add(prt.Isolate(self.get_chart(prt.Combine(on_top=False, yaxis_name=MSGR("Violations in %"), *s_percentage_nr))))

        return viol_chart_1, viol_chart_2

    def generate_diagrams(self):
        if len(self.violation_data_list) == 1:
            main_diagrams = self.get_diagrams_and_summary_per_rule()[0][-2:]
            per_rule_diagrams = []
        else:
            main_diagrams = self.get_multi_rule_diagrams()
            per_rule_diagrams = self.get_diagrams_and_summary_per_rule()

        self.add("")
        for diagram in main_diagrams:
            self.page()
            self.add(prt.Isolate(diagram))
            self.add("")

        for rule_ix, (sums, dia1, dia2) in enumerate(per_rule_diagrams):
            rule_key = self.violation_data_list[rule_ix].rule_str
            action = prt.action(lambda m, a, rk: rg.display_prt_report(source=m,
                                                                       area=a,
                                                                       scope="window",
                                                                       rpt_args={"show": "TABLE",
                                                                                 "rule": rk}),
                                (self.__module__, self.current_area, rule_key))
            self.add(prt.Expandable(prt.Text(self.violation_data_list[rule_ix].rule_title, font=ru.LINK_FONT),
                                    prt.Column(prt.Text(""),
                                               prt.Isolate(prt.Row(prt.Text(MSGR("Table"), font=ru.LINK_FONT, action=action),
                                                                   " ",
                                                                   self.get_report_rule_details_link(rule_key))),
                                               prt.Text(""), sums, prt.Text(""), dia1, prt.Text(""), dia2)))
            self.page()
            self.add("")

    def generate_summary(self):
        summary_table = self.generate_summary_header(self.show_categories_in_summary())
        self.add(prt.Isolate(prt.Column(summary_table, width=report_rules.CHART_WIDTH_DEFAULT)))
        for vd in self.violation_data_list:
            self.generate_summary_for_one_rule(summary_table, vd, self.show_categories_in_summary())

    def get_day_lists(self, min_day, max_day):
        """
        min_day :: int, max_day :: int
          -> days_in_pp :: [AbsTime], days_num_in_pp :: [int]
        """
        days_num_in_pp = range(min_day, max_day + 1)
        days_in_pp = [self.get_gui_date_str_from_pp_day(day) for day in days_num_in_pp]
        return days_in_pp, days_num_in_pp

    def get_gui_date_str_from_pp_day(self, day_in_pp):
        return de.abstime2gui_date_string(self.start_day_ref + day_in_pp * basics.ONE_DAY)

from __future__ import absolute_import
from __future__ import division
from six.moves import range
from six.moves import zip
from collections import defaultdict, OrderedDict
import sys

from Localization import MSGR
import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave

from carmusr.calibration.mappings import date_extensions as de
from carmusr.calibration.mappings import report_generation as rg
from carmusr.calibration.mappings import studio_palette
from carmusr.calibration.util import basics
from carmusr.calibration.util import report_rules
from carmusr.calibration.util import report_util as ru

BAR_COLORS_MULTI_RULES = [studio_palette.Blue,
                          studio_palette.JeppesenLightBlue,
                          studio_palette.JeppesenBlue,
                          studio_palette.Slate]


class ValuesForOneRule(object):

    def __init__(self, cri, cat_handler, consider_sub_cats=False):
        self.rsh_total = report_rules.RuleSummaryHandler(consider_sub_cats)
        self.rshs = defaultdict(report_rules.RuleSummaryHandler)
        self.cri = cri
        self.cat_handler = cat_handler


class RuleViolationsOverTime(report_rules._RuleAnalysisReport):

    @staticmethod
    def get_basic_header_text():
        return ru.CalibReports.VOT.title

    def get_header_text(self):
        return self.get_basic_header_text() + (MSGR(" - Table View") if self.is_table_view() else "")

    @staticmethod
    def get_form_handler(_variant):
        from carmusr.calibration.util import report_forms as rf
        return rf.vot_param_form_handler

    @staticmethod
    def get_rule_key(i=1):
        param_variable = 'report_calibration.%%vot_rule_%d%%' % i
        ix_rule, = rave.eval(param_variable)
        return "%s" % ix_rule

    def create(self):
        self.setpaper(orientation=prt.LANDSCAPE, size=prt.A3 if self.is_table_view() else prt.A4)

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

        self.values_per_rule_list = []
        self.min_day = sys.maxsize
        self.max_day = -sys.maxsize

        if len(rules) == 1:
            self.add_link_to_rule_details_report_for_rule = rules[0]

        self.start_day_ref = rave.eval(rave.keyw("global_lp_period_start"))[0]
        tzh = report_rules.TimeZoneHandler()

        for rule_str in rules:

            cri = self.cr.get_rule_item(rule_str)
            level = cri.rule_level
            poc = report_rules.PlanningObjectCreator(self, cri)
            values_for_this_rule = ValuesForOneRule(cri, poc.cat_handler, consider_sub_cats=self.is_table_view())

            for po, bag in poc.get_objects_and_bags():

                values_for_this_rule.rsh_total.add_from_po(po)

                if not po.is_valid:
                    continue

                day_in_pp = int(tzh.get_rule_failure_time(bag, level) - self.start_day_ref) // 1440
                self.min_day = min(day_in_pp, self.min_day)
                self.max_day = max(day_in_pp, self.max_day)

                values_for_this_rule.rshs[day_in_pp].add_from_po(po, skip_selected=True)

            self.values_per_rule_list.append(values_for_this_rule)

        self.day_list, self.days_num_in_pp = self.get_day_lists(self.min_day, self.max_day)

        self.add_warnings_and_links()
        self.generate_settings_table()
        self.generate_summary_table()
        self.page()

        if self.is_table_view():
            self.generate_table_view_content()
        else:
            self.generate_overview_content()

    def get_settings_table(self):
        table = super(RuleViolationsOverTime, self).get_settings_table()
        report_rules.add_time_stuff_to_settings_table(table)
        return table

    def generate_summary_table(self):
        if len(self.values_per_rule_list) == 1:
            table = self.get_summary_table_for_one_rule(self.values_per_rule_list[0])
        else:
            table = self.get_summary_table_for_many_rules()
        self.add(prt.Isolate(table))

    def get_summary_table_for_one_rule(self, rv):
        return report_rules.get_summary_table(rv.rsh_total,
                                              rv.cri,
                                              self.current_area,
                                              rv.cat_handler)

    def get_summary_table_for_many_rules(self):
        table = ru.SimpleTable(MSGR("Summary"), use_page=True)
        table.add_sub_title(prt.Text(MSGR("Rule")))
        table.add_sub_title(prt.Text(MSGR("Valid"), border=prt.border(left=1)))
        table.add_sub_title(prt.Text(MSGR("Legal"), colspan=2, border=prt.border(left=1)))
        table.add_sub_title(prt.Text(MSGR("Illegal"), colspan=2, border=prt.border(left=1)))

        def get_cell(rsh, rso, show_percent, tooltip=None):
            action = ru.get_select_action(self.current_area, rso.leg_ids)
            row = ru.SimpleTableRow(border=prt.border(left=1))
            row.add(prt.Text(rso.values[0], align=prt.RIGHT, action=action, tooltip=tooltip))
            if show_percent:
                row.add(prt.Text(basics.percentage_string(rso.values[0], rsh.valid.values[0]),
                                 tooltip=MSGR("Percentage of Valid"),
                                 align=prt.RIGHT, action=action))
            return row

        for ix, rv in enumerate(self.values_per_rule_list):
            rsh = rv.rsh_total
            row = table.add(ru.SimpleTableRow())
            row.add(prt.Isolate(prt.Row(report_rules.LegendColourIndicator(BAR_COLORS_MULTI_RULES[ix], valign=prt.CENTER),
                                        rv.cri.rule_label)))
            row.add(get_cell(rsh, rsh.valid, False))
            row.add(get_cell(rsh, rsh.legal, True, tooltip=self.get_categories_tooltip(rv, True)))
            row.add(get_cell(rsh, rsh.illegal, True, tooltip=self.get_categories_tooltip(rv, False)))

        return table

    @staticmethod
    def get_categories_tooltip(rv, legal_cats=True):
        # Legal OR illegal categories are considered.

        def get_row(title, val):
            return "  {}: {} ({})".format(title, val, basics.percentage_string(val, rsh.valid.values[0]))

        rsh = rv.rsh_total
        res = [MSGR("{} categories:").format(MSGR("Legal") if legal_cats else MSGR("Illegal"))]
        if legal_cats:
            if rsh.outside_first_bin.leg_ids:
                res.append(get_row(basics.OUTSIDE_FIRST_BIN_LABEL, rsh.outside_first_bin.values[0]))
            if rsh.in_first_bin.leg_ids:
                res.append(get_row(basics.IN_FIRST_BIN_LABEL, rsh.in_first_bin.values[0]))
            res.append("")
            res.append(MSGR("Bin size: {}").format(rv.cri.bin_value))
        else:
            for cat in rv.cat_handler.get_sorted_categories():
                if rsh.categories[cat].leg_ids:
                    res.append(get_row(cat, rsh.categories[cat].values[0]))
        return "\n".join(res)

    def generate_table_view_content(self):
        for rv in self.values_per_rule_list:
            self.add("")
            self.page()

            if rv.rsh_total.valid.leg_ids:
                table = report_rules.get_per_bin_table(MSGR("Rule Violations over Time"),
                                                       self.days_num_in_pp,
                                                       rv.rshs,
                                                       MSGR("Date"),
                                                       rv.rsh_total,
                                                       self.current_area,
                                                       rv.cat_handler,
                                                       show_percentage_of_valid=True,
                                                       binkey2label=lambda d: prt.Text(self.get_gui_date_str_from_pp_day(d), colspan=3))
            else:
                table = prt.Row()

            if len(self.values_per_rule_list) == 1:
                self.add(prt.Isolate(table))
            else:
                action = prt.action(lambda m, a, rk: rg.display_prt_report(source=m,
                                                                           area=a,
                                                                           scope="window",
                                                                           rpt_args={"show": "OVERVIEW",
                                                                                     "rule": rk}),
                                    (self.__module__, self.current_area, rv.cri.rule_key))
                self.add(prt.Expandable(prt.Text(rv.cri.rule_label, font=ru.LINK_FONT),
                                        prt.Column("",
                                                   prt.Isolate(prt.Row(prt.Text(MSGR("Overview"), font=ru.LINK_FONT, action=action),
                                                                       prt.Text("", width=20),
                                                                       self.get_report_rule_details_link(rv.cri.rule_key))),
                                                   "",
                                                   prt.Isolate(self.get_summary_table_for_one_rule(rv)),
                                                   "",
                                                   prt.Isolate(table))))

    def generate_overview_content(self):
        self.add("")

        if len(self.values_per_rule_list) == 1:
            self.add(self.get_diagrams_for_one_rule(self.values_per_rule_list[0]))
            return

        self.add(self.get_multi_rule_diagrams())
        self.page()

        for rv in self.values_per_rule_list:
            action = prt.action(lambda m, a, rk: rg.display_prt_report(source=m,
                                                                       area=a,
                                                                       scope="window",
                                                                       rpt_args={"show": "TABLE",
                                                                                 "rule": rk}),
                                (self.__module__, self.current_area, rv.cri.rule_key))
            self.add(prt.Expandable(prt.Text(rv.cri.rule_label, font=ru.LINK_FONT),
                                    prt.Column("",
                                               prt.Isolate(prt.Row(prt.Text(MSGR("Table"), font=ru.LINK_FONT, action=action),
                                                                   prt.Text("", width=20),
                                                                   self.get_report_rule_details_link(rv.cri.rule_key))),
                                               "",
                                               prt.Isolate(self.get_summary_table_for_one_rule(rv)),
                                               "",
                                               self.get_diagrams_for_one_rule(rv))))
            self.page()
            self.add("")

    def get_diagrams_for_one_rule(self, rv):
        res = prt.Column()
        if rv.rsh_total.valid.leg_ids:
            if rv.rsh_total.illegal.leg_ids:
                res.add(self.get_single_rule_diagram(rv, MSGR("Rule Violations over Time"), include_legal=False))
                res.page()
                res.add("")
            res.add(self.get_single_rule_diagram(rv, MSGR("Categories in Percentage of Valid over Time"), show_percentage_of_valid=True))
            res.page()
            res.add("")
            res.add(self.get_single_rule_diagram(rv, MSGR("Valid over Time")))
        return res

    def get_single_rule_diagram(self, rv, title, include_legal=True, show_percentage_of_valid=False):
        return prt.Isolate(report_rules.get_single_rule_diagram(title,
                                                                self.days_num_in_pp,
                                                                rv.rshs,
                                                                MSGR("Date"),
                                                                self.current_area,
                                                                rv.cat_handler,
                                                                include_legal=include_legal,
                                                                show_percentage_of_valid=show_percentage_of_valid,
                                                                xkey2label=self.get_gui_date_str_from_pp_day,
                                                                bar_width=report_rules.SINGLE_BAR_WIDTH))

    def get_multi_rule_diagrams(self):
        if sum(rv.rsh_total.illegal.values[0] for rv in self.values_per_rule_list) == 0:
            return prt.Row()

        ret = prt.Column()
        ret.add(self.get_multi_rule_diagram(MSGR("Rule Violations Over Time")))
        ret.page()
        ret.add("")
        ret.add(self.get_multi_rule_diagram(MSGR("Rule Violations in Percentage of Valid Over Time"), True))
        ret.page()
        ret.add("")
        return ret

    def get_multi_rule_diagram(self, title, show_percentage_of_valid=False):

        x_label2key = OrderedDict(zip(self.day_list, self.days_num_in_pp))

        series_list = []
        bar_width = 0.8 / len(self.values_per_rule_list)

        for ix, rv in enumerate(self.values_per_rule_list):
            if not rv.rsh_total.illegal.leg_ids:
                continue
            data = []
            for pp_day in self.days_num_in_pp:
                val = rv.rshs[pp_day].illegal.values[0]
                if show_percentage_of_valid:
                    val = basics.percentage_value(val, rv.rshs[pp_day].valid.values[0])
                data.append((self.get_gui_date_str_from_pp_day(pp_day), val))
            series_list.append(prt.Series(data,
                                          graph=prt.Bar(offset=0.1 + ix * bar_width,
                                                        width=bar_width,
                                                        fill=BAR_COLORS_MULTI_RULES[ix]),
                                          action=prt.chartaction(report_rules.MyDiagramAction(self.current_area, "illegal", x_label2key, rv.rshs)),
                                          tooltip=prt.charttooltip(report_rules.MyDiagramTooltip(MSGR("Illegal. Rule: ") + rv.cri.rule_label,
                                                                                                 x_label2key, rv.rshs, rv.cat_handler))))

        dia = report_rules.get_chart(title, MSGR("Date"), x_label2key, series_list, show_percentage_of_valid, False)
        return prt.Isolate(dia)

    def get_day_lists(self, min_day, max_day):
        """
        min_day :: int, max_day :: int
          -> days_in_pp :: [AbsTime], days_num_in_pp :: [int]
        """
        days_num_in_pp = list(range(min_day, max_day + 1))
        days_in_pp = [self.get_gui_date_str_from_pp_day(day) for day in days_num_in_pp]
        return days_in_pp, days_num_in_pp

    def get_gui_date_str_from_pp_day(self, day_in_pp):
        return de.abstime2gui_date_string(self.start_day_ref + day_in_pp * basics.ONE_DAY)

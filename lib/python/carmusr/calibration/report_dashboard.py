"""
Calibration dashboard - a prt report
"""


from __future__ import absolute_import
import six
from functools import reduce

import Cui
import jcms.calibration.comparison_plan
from Localization import MSGR
import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave
from RelTime import RelTime

from carmusr.calibration import report_rule_kpis
from carmusr.calibration import report_compare_plans
from carmusr.calibration import report_pattern_analysis
from carmusr.calibration import mappings
from carmusr.calibration.mappings import report_generation as rg
from carmusr.calibration.mappings import studio_palette as sp
from carmusr.calibration.mappings import bag_handler
from carmusr.calibration.util import report_util as ru
from carmusr.calibration.util.rule_kpis_imp import RuleData
from carmusr.calibration.util import compare_plan
from carmusr.calibration.util import pie_chart
from carmusr.calibration.util import basics
from carmusr.calibration.util import common
from carmusr.calibration.util import complement

pie_height = 20


class Report(ru.CalibrationReport):

    has_table_view = False

    def get_header_text(self):
        if self.variant == common.CalibAnalysisVariants.TimetableAnalysis.key:
            return ru.CalibReports.DABO.timetable_title
        return ru.CalibReports.DABO.title

    @staticmethod
    def get_form_handler(variant):
        from carmusr.calibration.util import report_forms as rf
        if variant == common.CalibAnalysisVariants.TimetableAnalysis.key:
            return rf.dabo_tta_param_form_handler
        return rf.dabo_param_form_handler

    def create(self):
        self.setpaper(orientation=prt.PORTRAIT, size=prt.A3)
        super(Report, self).create()

        self.test_if_report_can_be_generated_and_store_bag()
        if self.skip_reason:
            self.add_warnings_and_links()
            return

        # Slice filtering is not used so we just refresh the CrewCategories class
        complement.CrewCategories._refresh_if_needed()

        if self.current_area_mode not in (Cui.LegMode, Cui.AcRotMode):
            # The comparison plan is considered in the Rule KPI section for calculation of category on crew-chains.
            # We therefore do this call here so we can use 'reset_cache_if_needed=False' down in the rule-kpi calculations.
            self.compare_plan_name = compare_plan.ComparisonPlanHandler.get_plan_name(reset_cache_if_needed=True)

        rule_kpis_handler = report_rule_kpis.RuleKPIforPRTReport(self, consider_categories=True)
        rule_kpis_handler.collect_data()

        main_row = prt.Row()
        rule_table = rule_kpis_handler.get_table(self.get_rule_kpi_defs(rule_kpis_handler.cr), use_rule_filter=True)
        kpi_report_title = (ru.CalibReports.RKPI.timetable_title
                            if self.variant == common.CalibAnalysisVariants.TimetableAnalysis.key
                            else ru.CalibReports.RKPI.title)
        rule_table.title_row.add(self.get_report_generation_link(MSGR("More KPIs"),
                                                                 "calibration_rule_kpis",
                                                                 tooltip=MSGR("Generate the report '%s'") % kpi_report_title,
                                                                 align=prt.RIGHT))
        main_row.add(prt.Isolate(rule_table))

        if self.current_area_mode == Cui.CrrMode:
            main_row.add(prt.Text("", width=12))
            second_column = prt.Column()
            main_row.add(prt.Isolate(second_column))

            if compare_plan.ComparisonPlanHandler.a_plan_is_loaded():
                row = prt.Row(self.get_compare_plan_kpis())
            else:
                row = prt.Text(MSGR("Load Comparison Plan..."),
                               font=ru.LINK_FONT,
                               action=prt.action(jcms.calibration.comparison_plan.load))
            second_column.add(prt.Isolate(row))

            if self.pconfig.level_duty_defined:
                second_column.add("")
                second_column.add(prt.Isolate(self.get_pattern_table()))

        # Must be done here to get all warnings at the top.
        self.add_warnings_and_links()
        self.add(main_row)

    def get_pattern_table(self):

        tbh = bag_handler.WindowChains()
        dc = report_pattern_analysis.DataCreator(tbh.bag,
                                                 self.current_area,
                                                 self.compare_plan_name,
                                                 self.current_area_mode)
        dc.collect_data()
        patterns = dc.bin_patterns

        table = ru.SimpleTable(MSGR("Patterns"), use_page=False)
        table.title_row.add(self.get_report_generation_link(MSGR("More KPIs"),
                                                            "calibration_pattern_analysis",
                                                            tooltip=MSGR("Generate the report '%s'") % ru.CalibReports.PAT.title,
                                                            align=prt.RIGHT))
        table.add_sub_title("")
        table.add_sub_title(prt.Text(MSGR("In current plan"), border=prt.border(left=1)))
        if self.compare_plan_name:
            table.add_sub_title(prt.Text(MSGR("Only in current"), border=prt.border(left=1)))
            table.add_sub_title(prt.Text(MSGR("Change"), border=prt.border(left=1)))

        all_ids = set(reduce(list.__iadd__, (pd.get_ids() for pd in six.itervalues(patterns)), []))
        all_ids_action = ru.get_select_action(self.current_area, all_ids)

        row = table.add(ru.SimpleTableRow(prt.Text("Number of patterns", valign=prt.CENTER), font=prt.font(size=8)))

        row.add(prt.Text(len(patterns),
                         action=all_ids_action,
                         border=prt.border(left=1, right=1),
                         valign=prt.CENTER, align=prt.RIGHT))

        if self.compare_plan_name:
            num_zero_completed_patterns = sum(1 for pd in six.itervalues(patterns) if pd.fraction_of_crew_with_pattern_on_same_day_in_comp_plan() == 0)
            ids_zero_completed_patterns = set(reduce(list.__iadd__, (pd.get_ids() for pd in six.itervalues(patterns)
                                                                     if pd.fraction_of_crew_with_pattern_on_same_day_in_comp_plan() == 0), []))
            action_zero_completed_patterns = ru.get_select_action(self.current_area, ids_zero_completed_patterns)

            num_fully_completed_patterns = sum(1 for pd in six.itervalues(patterns) if pd.fraction_of_crew_with_pattern_on_same_day_in_comp_plan() == 1)
            ids_fully_completed_patterns = set(reduce(list.__iadd__, (pd.get_ids() for pd in six.itervalues(patterns)
                                                                      if pd.fraction_of_crew_with_pattern_on_same_day_in_comp_plan() == 1), []))

            num_partly_completed_patterns = len(patterns) - num_fully_completed_patterns - num_zero_completed_patterns
            ids_partly_completed_patterns = all_ids - ids_fully_completed_patterns - ids_zero_completed_patterns

            row.add(prt.Text(num_zero_completed_patterns,
                             action=action_zero_completed_patterns,
                             tooltip="Number of 0% completed patterns",
                             border=prt.border(right=1),
                             valign=prt.CENTER, align=prt.RIGHT))

            pie_members = (pie_chart.PieMember(MSGR("0% completed patterns"), num_zero_completed_patterns,
                                               fill=basics.HEATMAP_RED,
                                               action=action_zero_completed_patterns),
                           pie_chart.PieMember(MSGR("Partly completed patterns"), num_partly_completed_patterns,
                                               fill=sp.LightRed,
                                               action=ru.get_select_action(self.current_area, ids_partly_completed_patterns)),
                           pie_chart.PieMember(MSGR("100% completed patterns"), num_fully_completed_patterns,
                                               fill=sp.ReportLightBlue,
                                               action=ru.get_select_action(self.current_area, ids_fully_completed_patterns)))
            row.add(pie_chart.PieChart(pie_height, pie_height, pie_members, "", align=prt.CENTER, padding=prt.padding(bottom=1)))

        row = table.add(ru.SimpleTableRow(prt.Text("Total block time", valign=prt.CENTER), font=prt.font(size=8)))

        tot_block = sum(pat.total_block_time() for pat in six.itervalues(patterns))
        row.add(prt.Text(RelTime(tot_block),
                         action=all_ids_action,
                         border=prt.border(left=1, right=1),
                         valign=prt.CENTER, align=prt.RIGHT))

        if self.compare_plan_name:
            tot_not_completed_block_time = sum(pat.not_flown_block_time() for pat in six.itervalues(patterns))
            tot_completed_block_time = tot_block - tot_not_completed_block_time
            completed_ids = set(reduce(list.__iadd__, (pd.get_completed_ids() for pd in six.itervalues(patterns)), []))
            not_completed_ids = all_ids - completed_ids
            not_completed_action = ru.get_select_action(self.current_area, not_completed_ids)

            row.add(prt.Text(RelTime(tot_not_completed_block_time),
                             action=not_completed_action,
                             tooltip="Total block time in not completed instances",
                             border=prt.border(right=1),
                             valign=prt.CENTER, align=prt.RIGHT))

            pie_members = (pie_chart.PieMember(MSGR("Block time in not completed instances"), RelTime(tot_not_completed_block_time),
                                               fill=basics.HEATMAP_RED,
                                               action=not_completed_action),
                           pie_chart.PieMember(MSGR("Block time in completed instances"), RelTime(tot_completed_block_time),
                                               fill=sp.ReportLightBlue,
                                               action=ru.get_select_action(self.current_area, completed_ids)))
            row.add(pie_chart.PieChart(pie_height, pie_height, pie_members, "", align=prt.CENTER, padding=prt.padding(bottom=1)))

        return table

    def get_report_generation_link(self, link_text, module_name, **kw):
        report_package = "calibration"
        report_full_name = report_package + "." + module_name
        variant = self.variant
        return prt.Text(link_text,
                        font=ru.LINK_FONT,
                        action=prt.action(lambda a: rg.display_prt_report(source=report_full_name,
                                                                          area=a,
                                                                          scope="window",
                                                                          rpt_args={'variant': variant}),
                                          (self.current_area,)),
                        **kw)

    def get_compare_plan_kpis(self):
        table = ru.SimpleTable(MSGR("Comparison plan"), use_page=False)
        table.title_row.add(self.get_report_generation_link(MSGR("More KPIs"),
                                                            "calibration_compare_trips_with_other_plan",
                                                            tooltip=MSGR("Generate the report '%s'") % ru.CalibReports.COMP.title,
                                                            align=prt.RIGHT))

        current_plan_data = report_compare_plans.PlanData(self, None,
                                                          report_compare_plans.get_planned_ac_change_rave_variable(),
                                                          reduced_set_of_data=True)

        cph = compare_plan.ComparisonPlanHandler
        ref_plan_data = cph.saved_other.get("PLAN_DATA", None) or cph.saved_other.get("PLAN_DATA_REDUCED", None)
        if not ref_plan_data:
            ref_plan_data = report_compare_plans.PlanData(self, compare_plan.get_comparison_plan_bag(),
                                                          rave.var("calibration_mappings.aircraft_change"),
                                                          reduced_set_of_data=True)
            cph.saved_other["PLAN_DATA_REDUCED"] = ref_plan_data

        table.add_sub_title(prt.Row(prt.Text(MSGR("Statistics")),
                                    prt.Text(MSGR("In current plan"),
                                             border=prt.border(left=1, right=1)),
                                    prt.Text(MSGR("Only in current"),
                                             border=prt.border(left=1, right=1)),
                                    prt.Text(MSGR("Change"))))

        def add_row_to_table(title, num_current, current_ids, num_common, common_ids, num_changed_kind=None, changed_kind_ids=None, kind_change_text=None):
            row = table.add(ru.SimpleTableRow(prt.Text(title, valign=prt.CENTER), font=prt.font(size=8)))
            row.add(prt.Text(num_current or "-",
                             action=ru.get_select_action(self.current_area, current_ids),
                             align=prt.RIGHT, valign=prt.CENTER, border=prt.border(left=1, right=1)))

            if not num_current:
                row.add(prt.Text("-", valign=prt.CENTER, align=prt.RIGHT, height=pie_height))
                row.add(prt.Text("-", valign=prt.CENTER, align=prt.CENTER, border=prt.border(left=1), height=pie_height))
                return

            num_only_in_current = num_current - num_common
            only_in_current_ids = set(current_ids) - set(common_ids)
            if num_changed_kind:
                num_only_in_current -= num_changed_kind
                only_in_current_ids -= set(changed_kind_ids)

            row.add(prt.Text(num_only_in_current or "-",
                             action=ru.get_select_action(self.current_area, only_in_current_ids),
                             align=prt.RIGHT, valign=prt.CENTER, border=prt.border(left=1, right=1)))

            members = []
            members.append(pie_chart.PieMember(MSGR("Only in current"), num_only_in_current,
                                               fill=basics.HEATMAP_RED,
                                               action=ru.get_select_action(self.current_area, only_in_current_ids)))
            if num_changed_kind is not None:
                members.append(pie_chart.PieMember(kind_change_text, num_changed_kind,
                                                   fill=sp.LightRed,
                                                   action=ru.get_select_action(self.current_area, changed_kind_ids)))
            members.append(pie_chart.PieMember(MSGR("Unchanged"), num_common,
                                               fill=sp.ReportLightBlue,
                                               action=ru.get_select_action(self.current_area, common_ids)))

            row.add(pie_chart.PieChart(pie_height + 3, pie_height, members, "", padding=prt.padding(bottom=1)))

        def add_kpi_to_table(title, s1, s2):
            common_current_data = s1.common_data(s2)
            add_row_to_table(title, len(s1), s1.all_leg_keys(), len(common_current_data), common_current_data.all_leg_keys())

        if self.pconfig.level_trip_defined:
            add_kpi_to_table(MSGR('Trips, ignoring deadheads'), current_plan_data.trip_keys['trip_no_dh'], ref_plan_data.trip_keys['trip_no_dh'])
        if self.pconfig.level_duty_defined:
            add_kpi_to_table(MSGR('Duties, ignoring deadheads'), current_plan_data.duty_keys['duty_no_dh'], ref_plan_data.duty_keys['duty_no_dh'])
        add_kpi_to_table(MSGR('Active legs'), current_plan_data.leg_keys['active'], ref_plan_data.leg_keys['active'])

        table.table.add(prt.Column(*report_compare_plans.get_connection_setting_info_strings(),
                                   font=prt.font(size=7),
                                   border=prt.border(bottom=2, colour=sp.DarkGrey),
                                   background=sp.ReportBlue))

        def add_conn_kpi_to_table(title, s1, s2, s3, change_kind_txt, s1b=None):
            s12 = s1.common_data(s2)
            s13 = s1.common_data(s3)
            if not s1b:
                add_row_to_table(title, len(s1), s1.all_leg_keys(), len(s12), s12.all_leg_keys(), len(s13), s13.all_leg_keys(), change_kind_txt)
                return
            s12b = s1b.common_data(s3)
            s13b = s1b.common_data(s2)
            add_row_to_table(title,
                             len(s1) + len(s1b),
                             s1.all_leg_keys() + s1b.all_leg_keys(),
                             len(s12) + len(s12b),
                             s12.all_leg_keys() + s12b.all_leg_keys(),
                             len(s13) + len(s13b),
                             s13.all_leg_keys() + s13b.all_leg_keys(),
                             change_kind_txt)

        add_conn_kpi_to_table(MSGR('Connections'), current_plan_data.leg_keys['conn'], ref_plan_data.leg_keys['conn'],
                              ref_plan_data.leg_keys['turn'], MSGR("Connection > turn"))
        add_conn_kpi_to_table(MSGR('Turns'), current_plan_data.leg_keys['turn'], ref_plan_data.leg_keys['turn'],
                              ref_plan_data.leg_keys['conn'], MSGR("Turn > connection"))
        add_conn_kpi_to_table(MSGR('Connections & turns'), current_plan_data.leg_keys['turn'], ref_plan_data.leg_keys['turn'],
                              ref_plan_data.leg_keys['conn'], MSGR("Turn <-> conn"), current_plan_data.leg_keys['conn'])
        return table

    ## See "rule_kpis_imp.get_kpi_defs" for a description of the structure we create here.
    def get_rule_kpi_defs(self, cr):

        def my_circle_diagram(rd, current_area):

            num_valid = rd.get_num_valid_crew_slices()
            if not num_valid:
                return prt.Text("-", height=pie_height)
            if rd.categories_have_been_calculated():
                tooltip_header = "100% illegal, showing categories\n--------------------------------------------\n\n"
                tooltip_footer = ""
                num_per_cat_code = rd.get_num_crew_per_category()
                ids_per_cat_code = rd.get_leg_identifiers_per_crew_category()
                members = []
                for cat_code in rd.cat_handler.get_sorted_categories():
                    members.append(pie_chart.PieMember(cat_code,
                                                       num_per_cat_code[cat_code],
                                                       fill=rd.cat_handler.bar_color(cat_code),
                                                       action=ru.get_select_action(current_area, ids_per_cat_code[cat_code])))
            else:
                tooltip_header = MSGR("Legal & Illegal\n--------------------\n\n")
                tooltip_footer = MSGR("\n\nBin size: {}").format(rd.data_type(rd.bin_size))
                num_illegal = rd.get_num_illegal_crew_slices()
                num_bin1 = rd.get_num_crew_slices_in_first_bin()
                num_other = num_valid - num_bin1 - num_illegal
                other_ids = set(rd.get_all_ids()) - set(rd.get_illegal_ids()) - set(rd.get_in_first_bin_ids())

                members = (pie_chart.PieMember(MSGR("Illegal"), num_illegal,
                                               fill=basics.ILLEGAL_COLOUR,
                                               action=ru.get_select_action(current_area, rd.get_illegal_ids())),
                           pie_chart.PieMember(MSGR("Legal. {}").format(basics.IN_FIRST_BIN_LABEL), num_bin1,
                                               fill=basics.IN_FIRST_BIN_COLOUR,
                                               action=ru.get_select_action(current_area, rd.get_in_first_bin_ids())),
                           pie_chart.PieMember(MSGR("Legal. {}").format(basics.OUTSIDE_FIRST_BIN_LABEL), num_other,
                                               fill=basics.OUTSIDE_FIRST_BIN_COLOUR,
                                               action=ru.get_select_action(current_area, other_ids)))
            return pie_chart.PieChart(pie_height + 3, pie_height, members, tooltip_header, tooltip_footer, padding=prt.padding(bottom=1))

        def get_description_text_for_tooltip(rd):
            title = "Description of '%s'\n" % rd.label
            underline = "-" * 120 + "\n"
            text = rd.description or "-"
            return title + underline + text

        current_area = self.current_area
        defs = []
        defs.append(("  ", 1, "", 3, lambda rd: rd.label, "S", None, {"width": 250, "tooltip": get_description_text_for_tooltip}))
        defs.append((MSGR("Valid"), 1, "#", 3, RuleData.get_num_valid_crew_slices, "I", RuleData.get_all_ids, {}))
        if self.variant == common.CalibAnalysisVariants.TimetableAnalysis.key:
            defs.append((MSGR("Legal"), 1, "#", 3, RuleData.get_num_legal_crew_slices, "I", RuleData.get_legal_ids, {}))
        defs.append((MSGR("Illegal"), 1, "#", 3, RuleData.get_num_illegal_crew_slices, "I", RuleData.get_illegal_ids, {}))
        defs.append(("  ", 1, "  ", 3, lambda rd: my_circle_diagram(rd, current_area), "U", None, {"align": prt.CENTER}))
        if self.variant != common.CalibAnalysisVariants.TimetableAnalysis.key:
            defs.append((MSGR("Diff"), 1, MSGR("5%"), 3, lambda rd: RuleData.get_percentile_diff(rd, 5), "RT", None, {}))
        defs.append((MSGR("Reports"), 4, "RVD", 0, lambda _rd: prt.Image(mappings.image_file_name_diagram), "U", "RVD", {"align": prt.CENTER}))
        defs.append((None, None, "VOS", 0, lambda rd: prt.Image(mappings.image_file_name_diagram) if rd.key in cr.station_rules_dict else prt.Text(""),
                     "U", "VOS", {"align": prt.CENTER}))
        defs.append((None, None, "VOT", 0, lambda _rd: prt.Image(mappings.image_file_name_diagram), "U", "VOT", {"align": prt.CENTER}))
        defs.append((None, None, "VOW", 0, lambda _rd: prt.Image(mappings.image_file_name_table), "U", "VOW", {"align": prt.CENTER}))
        return tuple(defs)

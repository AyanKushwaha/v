"""
Detailed rule KPIs report.
"""


from __future__ import absolute_import
import six

from Localization import MSGR
from RelTime import RelTime
import carmensystems.publisher.api as prt

from carmusr.calibration.mappings import studio_palette as sp
from carmusr.calibration.mappings import report_generation as rg
from carmusr.calibration.util import calibration_rules as calib_rules
from carmusr.calibration.util import report_util as ru
from carmusr.calibration.util import rule_kpis_imp
from carmusr.calibration.util import common


class Report(ru.CalibrationReport):

    has_table_view = False

    def get_header_text(self):
        if self.variant == common.CalibAnalysisVariants.TimetableAnalysis.key:
            return ru.CalibReports.RKPI.timetable_title
        return ru.CalibReports.RKPI.title

    @staticmethod
    def get_form_handler(variant):
        from carmusr.calibration.util import report_forms as rf
        if variant == common.CalibAnalysisVariants.TimetableAnalysis.key:
            return rf.kpi_tta_param_form_handler
        return rf.kpi_param_form_handler

    def create(self):
        self.setpaper(orientation=prt.LANDSCAPE, size=prt.A3)
        super(Report, self).create()

        self.test_if_report_can_be_generated_and_store_bag()
        if self.skip_reason:
            self.add_warnings_and_links()
            return

        rkp = RuleKPIforPRTReport(self)
        rkp .collect_data()
        self.add_warnings_and_links()
        self.add(prt.Isolate(rkp.get_table(rule_kpis_imp.get_kpi_defs(self.variant))))


class RuleKPIforPRTReport(object):

    def __init__(self, report_instance, consider_categories=False):
        self.report_instance = report_instance
        self.consider_categories = consider_categories

    def collect_data(self):
        self.rule_datas = []
        self.cr = calib_rules.CalibrationRuleContainer(self.report_instance.variant)

        for calib_rule in self.cr.all_rules:
            my_bags = self.report_instance.get_bags_for_cri_and_write_warning_once(calib_rule)
            self.rule_datas.append(rule_kpis_imp.RuleData(calib_rule, my_bags, self.consider_categories))

    @staticmethod
    def my_format(rd, type_s, val):
        val = rule_kpis_imp.kpi_round_etc(rd, type_s, val)
        if val is None:
            return "-"
        if type_s == "RT" and rd.data_type is RelTime:
            return RelTime(val)
        return val

    def get_table(self, kpi_defs, use_rule_filter=False):

        table = ru.SimpleTable("Rule KPIs", use_page=False)

        sub_title_col = prt.Column()
        table.add_sub_title(sub_title_col)
        sub_title_row_1 = sub_title_col.add(prt.Row())
        sub_title_row_2 = sub_title_col.add(prt.Row())

        other_reports = {"RVD": (ru.CalibReports.RVD.title, "calibration.calibration_rule_value_distribution"),
                         "VOT": (ru.CalibReports.VOT.title, "calibration.calibration_violations_over_time"),
                         "VOS": (ru.CalibReports.VOS.title, "calibration.calibration_violations_over_station"),
                         "VOW": (ru.CalibReports.VOW.title, "calibration.calibration_violations_over_weekdays")}

        for label1, colspan, label2, is_last, _vf, _t, _if, _kw in kpi_defs:
            if label1:
                sub_title_row_1.add(prt.Text(label1, colspan=colspan, align=prt.CENTER,
                                             border=prt.border(right=1 if (is_last & 2) else None)))
            sub_title_row_2.add(prt.Text(label2, align=prt.CENTER, border=prt.border(right=1 if is_last & 1 else None)))

        for rule_data in self.rule_datas:

            if use_rule_filter:
                if (ru.hide_rule_off() and not rule_data.rule_is_on()) or (ru.hide_if_no_valid() and rule_data.get_num_valid_crew_slices() == 0):
                    continue

            row = table.add(prt.Row(border=prt.border(inner_wall=1, colour=sp.Grey),
                                    font=prt.font(size=8)))
            for label1, _cs, label2, is_last, value_calc, type_s, leg_id_calc_or_report, kw in kpi_defs:
                if type_s == "U":
                    item = row.add(value_calc(rule_data))
                else:
                    item = row.add(prt.Text(self.my_format(rule_data, type_s, value_calc(rule_data))))
                item.set(border=prt.border(right=1 if is_last & 1 else None))

                for attr_name, attr_value in six.iteritems(kw):
                    if attr_name in ("align", "valign"):
                        continue
                    if callable(attr_value):
                        attr_value = attr_value(rule_data)
                    item.set(**{attr_name: attr_value})

                # valign and align must be set in the same call. Bug?
                item.set(align=kw.get("align", prt.LEFT if type_s in ("S", "U") else prt.RIGHT),
                         valign=kw.get("valign", prt.CENTER))

                if leg_id_calc_or_report is None:
                    continue
                if not isinstance(leg_id_calc_or_report, str):
                    item.set(action=ru.get_select_action(self.report_instance.current_area, leg_id_calc_or_report(rule_data)))
                    continue

                rule_key = rule_data.key
                if leg_id_calc_or_report == "VOS" and rule_key not in self.cr.station_rules_dict:
                    continue
                report_name, report_module = other_reports[leg_id_calc_or_report]
                item.set(tooltip=MSGR("Generate the report '{}' with\n '{}' as focus rule.").format(report_name, rule_data.label))
                variant = self.report_instance.variant
                item.set(action=prt.action(lambda m, a, r: rg.display_prt_report(source=m,
                                                                                 area=a,
                                                                                 scope="window",
                                                                                 rpt_args={'rule': r,
                                                                                           'variant': variant}),
                                           (report_module, self.report_instance.current_area, rule_key)))

        if not self.rule_datas:
            table.add(prt.Text(self.cr.no_registered_rules_reason(), colour=sp.BrightRed))

        return table

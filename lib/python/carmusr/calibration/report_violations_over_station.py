from __future__ import absolute_import
from collections import defaultdict

from Localization import MSGR
import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave

from carmusr.calibration.mappings import translation_type_ext
from carmusr.calibration.util import report_rules
from carmusr.calibration.util import report_util as ru
from carmusr.calibration.util import calibration_rules as cr


class RuleViolationsOverStation(report_rules._RuleAnalysisReport):

    @staticmethod
    def get_basic_header_text():
        return ru.CalibReports.VOS.title

    def get_header_text(self):
        return self.get_basic_header_text() + (MSGR(" - Table View") if self.is_table_view() else "")

    @staticmethod
    def get_form_handler(_variant):
        from carmusr.calibration.util import report_forms as rf
        return rf.vos_param_form_handler

    @staticmethod
    def get_rule_key():
        param_variable = 'report_calibration.station_rule'
        ix_rule, = rave.eval(param_variable)
        return "%s" % ix_rule

    def has_illegal_stations(self):
        return self.rule_summary_handler.illegal.leg_ids

    def get_sorted_illegal_stations(self):
        return sorted(stn for stn in self.rshs if self.rshs[stn].illegal.leg_ids)

    def get_sorted_valid_stations(self):
        return sorted(stn for stn in self.rshs)

    def create(self):
        self.setpaper(orientation=prt.LANDSCAPE, size=prt.A3 if self.is_table_view() else prt.A4)

        super(RuleViolationsOverStation, self).create()

        self.set_skip_reason_and_create_cr()

        if self.skip_reason is not None:
            self.add_warnings_and_links()
            return

        rule_str = self.arg("rule") or self.get_rule_key()

        if rule_str not in self.cr.station_rules_dict:
            self.add_warning_text(MSGR("No rule selected to analyse"))
            self.add_warnings_and_links()
            return

        cri = self.cr.get_station_item(rule_str)
        station_var = getattr(cri, cr.STATION).rave_obj

        poc = report_rules.PlanningObjectCreator(self, cri)
        self.cat_handler = poc.cat_handler
        self.rule_summary_handler = report_rules.RuleSummaryHandler(consider_sub_cats=self.is_table_view())
        self.rshs = defaultdict(report_rules.RuleSummaryHandler)

        for po, bag in poc.get_objects_and_bags():

            self.rule_summary_handler.add_from_po(po)

            if not po.is_valid:
                continue

            try:  # Adequate level of station attribute not checked in calib_rules for performance reasons.
                station, = rave.eval(bag, station_var)
            except rave.RaveError as e:
                self.add_warning_text(MSGR("CONFIGURATION ERROR. Incorrect station definition. %s.") % e)
                self.add_warnings_and_links()
                return
            if station is None:
                station = MSGR("Station not defined")

            self.rshs[translation_type_ext.station_id2gui(station)].add_from_po(po, skip_selected=True)

        self.add_link_to_rule_details_report_for_rule = rule_str
        self.add_warnings_and_links()
        self.generate_settings_table()

        self.add(prt.Isolate(report_rules.get_summary_table(self.rule_summary_handler, cri, self.current_area, self.cat_handler)))
        self.add("")
        self.page()

        if not self.rule_summary_handler.valid.leg_ids:
            return

        if self.is_table_view():
            self.generate_and_add_station_details_table()
        else:
            if self.has_illegal_stations():
                self.generate_and_add_diagram(MSGR("Rule Violations over Station"), include_legal=False)
            self.generate_and_add_diagram(MSGR("Categories in Percentage of Valid over Station"), show_percentage_of_valid=True)
            self.generate_and_add_diagram(MSGR("Valid over Station"))

    def generate_and_add_diagram(self, title, include_legal=True, show_percentage_of_valid=False):
        dia = report_rules.get_single_rule_diagram(title,
                                                   self.get_sorted_valid_stations() if include_legal else self.get_sorted_illegal_stations(),
                                                   self.rshs,
                                                   MSGR("Station"),
                                                   self.current_area,
                                                   self.cat_handler,
                                                   include_legal=include_legal,
                                                   show_percentage_of_valid=show_percentage_of_valid,
                                                   bar_width=report_rules.SINGLE_BAR_WIDTH)
        self.add(prt.Isolate(dia))
        self.add("")
        self.page()

    def generate_and_add_station_details_table(self):
        self.add(prt.Isolate(report_rules.get_per_bin_table(MSGR("Rule Violations over Station"),
                                                            self.get_sorted_valid_stations(),
                                                            self.rshs,
                                                            MSGR("Station"),
                                                            self.rule_summary_handler,
                                                            self.current_area,
                                                            self.cat_handler,
                                                            show_percentage_of_valid=True
                                                            )))
        self.add("")
        self.page()

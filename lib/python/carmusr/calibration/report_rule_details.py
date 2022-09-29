from __future__ import absolute_import
from six.moves import range

from Localization import MSGR
from AbsTime import AbsTime
import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave

from carmusr.calibration.mappings import date_extensions as de
from carmusr.calibration.util import basics
from carmusr.calibration.util import report_rules
from carmusr.calibration.util import report_util as ru
from carmusr.calibration.util import config_per_product


class Report(report_rules._RuleAnalysisReport):

    has_table_view = False

    RULE_PARAM = 'report_calibration.details_rule'

    @staticmethod
    def get_header_text():
        return ru.CalibReports.RD.title

    @staticmethod
    def get_form_handler(_variant):
        from carmusr.calibration.util import report_forms as rf
        return rf.rd_param_form_handler

    @staticmethod
    def get_rule_key():
        ix_rule, = rave.eval(Report.RULE_PARAM)
        return "%s" % ix_rule

    def create(self):

        self.setpaper(orientation=prt.LANDSCAPE, size=prt.A3)

        super(Report, self).create()

        self.set_skip_reason_and_create_cr()
        if self.skip_reason is not None:
            self.add_warnings_and_links()
            return

        rule_str = self.arg("rule") or self.get_rule_key()

        if rule_str not in self.cr.all_rules_dict:
            self.add_warning_text(MSGR("No rule selected to analyse"))
            self.add_warnings_and_links()
            return

        self.cri = self.cr.get_rule_item(rule_str)

        self.populate_data()

        self.add_warnings_and_links()

        self.generate_settings_table()

        self.add(prt.Isolate(report_rules.get_summary_table(self.rule_summary_handler, self.cri, self.current_area, self.cat_handler)))
        self.add("")
        self.page()

        if not self.values:
            return

        self.add_detail_table()

    def populate_data(self):
        self.detail_items = config_per_product.get_config_for_active_product().levels_dict[self.cri.rule_level].rule_details_cls.get_items()
        self.detail_values = []
        self.legals = []
        self.limits = []
        self.values = []
        self.diffs = []
        self.identifiers = []
        self.crew_multipliers = []
        self.categories = []
        self.in_first_bins = []
        self.rule_summary_handler = report_rules.RuleSummaryHandler(consider_sub_cats=True)

        poc = report_rules.PlanningObjectCreator(self, self.cri)
        self.cat_handler = poc.cat_handler

        detail_rave_objs = tuple(item.rave_obj for item in self.detail_items)

        for po, bag in poc.get_objects_and_bags():

            self.rule_summary_handler.add_from_po(po)

            if not po.is_valid:
                continue

            detail_rave_values = [de.abstime2gui_datetime_string(item) if isinstance(item, AbsTime) else item
                                  for item in rave.eval(bag, *detail_rave_objs)]

            self.detail_values.append(detail_rave_values)
            self.legals.append(po.is_legal)
            self.limits.append(po.limit)
            self.values.append(po.value)
            self.diffs.append(po.diff)
            self.identifiers.append(po.leg_identifiers)
            self.crew_multipliers.append(po.num_crew)
            self.categories.append(po.cat)
            self.in_first_bins.append(po.in_first_bin)

    def add_detail_table(self):
        title = MSGR("Details")
        table = ru.SimpleTable(title, use_page=True)
        for item in self.detail_items:
            table.add_sub_title(item.label, **item.label_prt_props)

        for ix in range(len(self.detail_values)):
            special_values = {"S_ROWNUM": (ix + 1),
                              "S_DIFF": self.diffs[ix],
                              "S_LIMIT": self.limits[ix],
                              "S_VALUE": self.values[ix],
                              "S_LEGAL": self.legals[ix],
                              "S_CAT": self.get_cat_text(ix),
                              "S_NVALID": self.crew_multipliers[ix]}
            action = prt.action(ru.calib_show_and_mark_legs,
                                (self.current_area, self.identifiers[ix]))

            row = table.add(ru.SimpleTableRow())
            for colix, value in enumerate(self.detail_values[ix]):
                if isinstance(value, str) and value in special_values:
                    value = special_values[value]
                row.add(prt.Text("%s" % value, action=action, **self.detail_items[colix].value_prt_props))
                colix += 1
        self.add(prt.Isolate(table))

    def get_cat_text(self, ix):
        if self.legals[ix]:
            return basics.IN_FIRST_BIN_LABEL if self.in_first_bins[ix] else basics.OUTSIDE_FIRST_BIN_LABEL
        return self.categories[ix]

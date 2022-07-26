from Localization import MSGR
from AbsTime import AbsTime
import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave
import Cui

from carmusr.calibration.mappings import date_extensions as de
from carmusr.calibration.util import calibration_rules as calib_rules
from carmusr.calibration.util import complement
from carmusr.calibration.util import compare_plan
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

    def __init__(self, *args, **kw):

        super(Report, self).__init__(*args, **kw)

        self.detail_items = []
        self.detail_values = []

        self.legals = []
        self.limits = []
        self.values = []
        self.diffs = []
        self.identifiers = []
        self.crew_multipliers = []
        self.categories = []
        self.in_first_bins = []

    def create(self):

        self.setpaper(orientation=prt.LANDSCAPE, size=prt.A3)

        super(Report, self).create()

        self.set_skip_reason_and_create_cr()
        if self.skip_reason is not None:
            self.add_warnings_and_links()
            return

        rule_str = self.arg("rule") or Report.get_rule_key()

        if rule_str not in self.cr.all_rules_dict:
            self.add_warning_text(MSGR("No rule selected to analyse"))
            self.add_warnings_and_links()
            return

        self.cri = self.cr.get_rule_item(rule_str)

        self.detail_items = config_per_product.get_config_for_active_product().levels_dict[self.cri.rule_level].rule_details_cls.get_items()

        self.populate_data()

        self.add_warnings_and_links()

        self.generate_settings_table()

        self.add_overview_table()
        self.add("")
        self.page()

        if not self.values:
            return

        self.add_detail_table()

    def append_to_lists(self, detail_values, is_legal, limit, value, diff, identifiers, crew_multiplier, cat, in_first_bin):
        self.detail_values.append(detail_values)
        self.legals.append(is_legal)
        self.limits.append(limit)
        self.values.append(value)
        self.diffs.append(diff)
        self.identifiers.append(identifiers)
        self.crew_multipliers.append(crew_multiplier)
        self.categories.append(cat)
        self.in_first_bins.append(in_first_bin)

    def populate_data(self):
        is_valid_var = getattr(self.cri, calib_rules.IS_VALID).rave_obj
        limit_var = getattr(self.cri, calib_rules.LIMIT).rave_obj
        value_var = getattr(self.cri, calib_rules.VALUE).rave_obj
        rule_body_expr = self.cri.rule_body_expr
        comp_key_var, self.cat_handler = self.get_comp_key_and_cat_handler(self.cri)

        self.bin_value = getattr(self.cri, calib_rules.BIN).value()

        detail_rave_objs = tuple(item.rave_obj for item in self.detail_items)

        for bag in self.get_bags_for_cri_and_write_warning_once(self.cri):
            is_valid, = rave.eval(bag, is_valid_var)
            if not is_valid:
                continue

            is_legal, = rave.eval(bag, rule_body_expr)
            if is_legal is None:
                continue

            if self.current_area_mode in (Cui.AcRotMode, Cui.LegMode):
                tripslice_or_crew_comp = 1
                num_crew_multiplier = 1
            else:
                tripslice_or_crew_comp = compare_plan.filtered_slice_from_bag(comp_key_var, bag)
                num_crew_multiplier = tripslice_or_crew_comp.complement_sum()

            if not num_crew_multiplier:
                continue

            limit, value = rave.eval(bag, limit_var, value_var)

            abs_diff = abs(limit - value)
            diff = abs_diff if is_legal else -abs_diff

            leg_identifiers = [leg_bag.leg_identifier() for leg_bag in bag.atom_set()]

            detail_rave_values = [de.abstime2gui_datetime_string(item) if isinstance(item, AbsTime) else item
                                  for item in rave.eval(bag, *detail_rave_objs)]

            if not is_legal:
                in_first_bin = None
                _subcat, cats_and_crew = self.cat_handler.get_and_register_cat(bag, tripslice_or_crew_comp)
            else:
                in_first_bin = diff <= self.cri.max_diff_for_bin_one
                cats_and_crew = ((None, num_crew_multiplier),)

            for cat, ncrew in cats_and_crew:
                # Append data to all lists
                self.append_to_lists(detail_rave_values,
                                     is_legal,
                                     limit,
                                     value,
                                     diff,
                                     leg_identifiers,
                                     ncrew,
                                     cat,
                                     in_first_bin)

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

        num_valid = 0
        num_illegal = 0
        ids_valid = []
        ids_illegal = []
        for is_legal, crew, ids in zip(self.legals, self.crew_multipliers, self.identifiers):
            num_valid += crew
            ids_valid += ids
            if not is_legal:
                num_illegal += crew
                ids_illegal += ids

        valid_action = prt.action(ru.calib_show_and_mark_legs,
                                  (self.current_area, ids_valid))
        row = table.add(prt.Text(MSGR("Number of valid:"),
                                 align=prt.LEFT,
                                 font=ru.BOLD))
        row.add(prt.Text("%s" % num_valid, align=prt.LEFT, action=valid_action))

        illegal_action = prt.action(ru.calib_show_and_mark_legs,
                                    (self.current_area, ids_illegal))
        row = table.add(prt.Text(MSGR("Number of illegal:"),
                                 align=prt.LEFT,
                                 font=ru.BOLD))
        row.add(prt.Text("%s" % num_illegal, align=prt.LEFT, action=illegal_action))

        self.add(prt.Isolate(table))

    def get_cat_text(self, ix):
        if self.legals[ix]:
            return MSGR("In first bin") if self.in_first_bins[ix] else ""
        return self.categories[ix] or MSGR("Undefined")

    def add_detail_table(self):
        title = MSGR("Rule Details")
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

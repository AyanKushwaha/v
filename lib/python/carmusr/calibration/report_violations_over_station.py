
from Localization import MSGR
import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave
import Cui

from carmusr.calibration.mappings import translation_type_ext
from carmusr.calibration.mappings import studio_palette
from carmusr.calibration.util import report_rules
from carmusr.calibration.util import compare_plan
from carmusr.calibration.util import basics
from carmusr.calibration.util import report_util as ru
from carmusr.calibration.util import calibration_rules as cr


class RuleViolationsOverStation(report_rules._RuleViolationsOverStationOrTime):

    @staticmethod
    def get_basic_header_text():
        return ru.CalibReports.VOS.title

    def get_header_text(self):
        return self.get_basic_header_text() + (MSGR(" - Table View") if self.arg('show') == "TABLE" else "")

    @staticmethod
    def get_form_handler(_variant):
        from carmusr.calibration.util import report_forms as rf
        return rf.vos_param_form_handler

    @staticmethod
    def get_rule_key():
        param_variable = 'report_calibration.station_rule'
        ix_rule, = rave.eval(param_variable)
        return "%s" % ix_rule

    def show_categories_in_summary(self):
        return self.violation_data.cat_handler.has_categories()

    def has_illegal_stations(self):
        return any(self.violation_data.illegal_dim_cnt.itervalues())

    def get_sorted_illegal_stations(self):
        return sorted(self.violation_data.illegal_dim_cnt.keys())

    def get_sorted_valid_stations(self):
        return sorted(self.violation_data.valid_dim_cnt.keys())

    def create(self):
        self.setpaper(orientation=prt.LANDSCAPE)

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
        my_bags = self.get_bags_for_cri_and_write_warning_once(cri)

        my_rule_body_exp = cri.rule_body_expr
        station_var = getattr(cri, cr.STATION).rave_obj

        comp_key_var, cat_handler = self.get_comp_key_and_cat_handler(cri)
        self.violation_data = report_rules.ViolationData(cat_handler)

        is_valid_var = getattr(cri, cr.IS_VALID).rave_obj
        limit_var = getattr(cri, cr.LIMIT).rave_obj
        value_var = getattr(cri, cr.VALUE).rave_obj
        self.violation_data.bin = getattr(cri, cr.BIN).value()

        for bag in my_bags:
            is_valid, = rave.eval(bag, is_valid_var)
            if not is_valid:
                # Void or False
                continue

            is_legal, = rave.eval(bag, my_rule_body_exp)
            if is_legal is None:
                # Void rules body count as void valid, i.e. not at all
                continue

            if self.current_area_mode in (Cui.AcRotMode, Cui.LegMode):
                tripslice_or_num_crew = 1
                num_crew = 1
            else:
                tripslice_or_num_crew = compare_plan.filtered_slice_from_bag(comp_key_var, bag)
                num_crew = tripslice_or_num_crew.complement_sum()
            if not num_crew:
                continue

            try:  # Adequate level of station attribute not checked in calib_rules for performance reasons.
                station, = rave.eval(bag, station_var)
            except rave.RaveError as e:
                self.add_warning_text(MSGR("CONFIGURATION ERROR. Incorrect station definition. %s.") % e)
                self.add_warnings_and_links()
                return
            if station is None:
                station = MSGR("Station not defined")

            identifiers = [leg_bag.leg_identifier() for leg_bag in bag.atom_set()]
            self.violation_data.add_valid(station, num_crew, station, identifiers)

            if not is_legal:
                subcat, cats_and_crew = cat_handler.get_and_register_cat(bag, tripslice_or_num_crew)
                for cat, ncrew in cats_and_crew:
                    self.violation_data.add_illegal(cat, subcat, ncrew, station, station, identifiers)
            else:
                limit, value = rave.eval(bag, limit_var, value_var)
                diff = abs(limit - value)
                if diff <= cri.max_diff_for_bin_one:
                    self.violation_data.add_in_bin(station, num_crew, station, identifiers)
        # end of bag loop

        if not self.violation_data.num_valid:
            self.add_warning_text(MSGR("No selected planning object is valid for rule '{}'.").format(cri.rule_label))
            self.add_warnings_and_links()
            return

        self.violation_data.rule_title = cri.rule_label
        self.violation_data.level = cri.rule_level
        self.violation_data.rule_str = rule_str

        self.add_link_to_rule_details_report_for_rule = rule_str
        self.add_warnings_and_links()
        self.generate_settings_table()
        self.generate_summary()

        if self.arg('show') == "TABLE":
            self.generate_station_details_table()
        else:
            if self.has_illegal_stations():
                self.generate_diagrams()

    def generate_diagrams(self):
        vdata = self.violation_data
        current_area = self.current_area
        station_list = self.get_sorted_illegal_stations()
        valid_value_list = report_rules.get_counter_values_as_list(station_list, vdata.valid_dim_cnt)

        sorted_categories = vdata.cat_handler.get_sorted_categories()
        s_illeg_nr = []
        s_percentage_nr = []
        for lb_cat in sorted_categories:
            illegal_value_list = report_rules.get_counter_values_as_list(station_list, vdata.illegal_cat_dim_cnt[lb_cat])
            action = prt.chartaction(lambda x, _, identifier_dict=vdata.illegal_identifier_cat_dim_dict[lb_cat]:
                                     ru.calib_show_and_mark_legs(current_area, identifier_dict[x]))
            bar = prt.Bar(width=report_rules.SINGLE_BAR_WIDTH, fill=vdata.cat_handler.bar_color(0, lb_cat))
            label = lb_cat if lb_cat else vdata.rule_title
            totals = vdata.illegal_dim_cnt if vdata.cat_handler.has_categories() else None
            serie_1 = prt.Series(zip(station_list, illegal_value_list),
                                 graph=bar,
                                 label=label,
                                 action=action,
                                 tooltip=prt.charttooltip(report_rules.Tooltip(vdata.rule_title,
                                                                               x_map=translation_type_ext.station_id2gui,
                                                                               totals=totals, y_label=lb_cat)))

            s_illeg_nr.append(serie_1)
            ratio_per_day = [basics.percentage_value(x, y) for x, y in zip(illegal_value_list, valid_value_list)]
            ratio_totals = {stn: basics.percentage_value(vdata.illegal_dim_cnt[stn], num_valid)
                            for stn, num_valid in zip(station_list, valid_value_list)} if vdata.cat_handler.has_categories() else None

            serie_2 = prt.Series(zip(station_list, ratio_per_day),
                                 graph=bar,
                                 label=label,
                                 action=action,
                                 tooltip=prt.charttooltip(report_rules.Tooltip(vdata.rule_title, totals=ratio_totals,
                                                                               x_map=translation_type_ext.station_id2gui,
                                                                               y_label=lb_cat, y_fmt=basics.PERC_FMT)))
            s_percentage_nr.append(serie_2)

        self.add("")
        self.page()
        viol_chart_1 = ru.SimpleDiagram(prt.Text(MSGR("Rule Violations Over Station"), valign=prt.CENTER))
        num_x_values = len(station_list)
        rotate_tags = num_x_values * (max(len(stn) for stn in station_list) + 1) > 92
        chart_width = report_rules.get_chart_width(num_x_values)
        x_tic_values = set(station_list[0::report_rules.get_x_tics_divider(num_x_values)])
        xaxis_format = lambda v: translation_type_ext.station_id2gui(v) if v in x_tic_values else ""
        viol_chart_1.add(prt.Isolate(prt.Chart(chart_width, report_rules.CHART_HEIGHT,
                                               prt.Combine(yaxis_name=MSGR("Number of violations"),
                                                           yaxis_limits=(None, None), *s_illeg_nr),
                                               xaxis_name=MSGR("Station"),
                                               xaxis_format=xaxis_format,
                                               background=studio_palette.White,
                                               xaxis_rotate_tags=rotate_tags)))

        self.add(prt.Isolate(viol_chart_1))

        self.add("")
        self.page()
        viol_chart_2 = ru.SimpleDiagram(prt.Text(MSGR("Rule Violations in Percentage of Valid Over Station"),
                                                 valign=prt.CENTER))
        viol_chart_2.add(prt.Isolate(prt.Chart(chart_width, report_rules.CHART_HEIGHT,
                                               prt.Combine(yaxis_name=MSGR("Violations in %"),
                                                           yaxis_limits=(None, None), *s_percentage_nr),
                                               xaxis_name=MSGR("Station"),
                                               xaxis_format=xaxis_format,
                                               background=studio_palette.White,
                                               xaxis_rotate_tags=rotate_tags)))

        self.add(prt.Isolate(viol_chart_2))

    def add_total_row(self, summary_table):
        vdata = self.violation_data
        self.add_data_row(summary_table, MSGR('Total'),
                          vdata.num_illegal, vdata.num_in_bin, vdata.num_valid,
                          vdata.illegal_identifier_list, vdata.in_bin_identifier_list,
                          vdata.valid_identifier_list, vdata.cat_handler,
                          vdata.illegal_cat_cnt, vdata.illegal_identifier_cat_dict,
                          font=ru.BOLD)

    def add_station_rows(self, table):
        vdata = self.violation_data
        for station in self.get_sorted_valid_stations():
            self.add_data_row(table, translation_type_ext.station_id2gui(station),
                              vdata.illegal_dim_cnt[station], vdata.in_bin_dim_cnt[station], vdata.valid_dim_cnt[station],
                              vdata.illegal_identifier_dim_dict[station], vdata.in_bin_identifier_dim_dict[station],
                              vdata.valid_identifier_dim_dict[station], vdata.cat_handler,
                              {lb_cat: vdata.illegal_cat_dim_cnt[lb_cat][station] for lb_cat in vdata.cat_handler.categories},
                              {lb_cat: vdata.illegal_identifier_cat_dim_dict[lb_cat][station] for lb_cat in vdata.cat_handler.categories})

    def generate_summary(self):
        summary_table = self.generate_summary_header(self.show_categories_in_summary())
        self.add(prt.Isolate(prt.Column(summary_table, width=report_rules.CHART_WIDTH_DEFAULT)))
        self.generate_summary_for_one_rule(summary_table, self.violation_data, self.show_categories_in_summary())

    def generate_station_details_table(self):
        self.add("")
        self.page()
        details_table = self.get_details_table_with_header(MSGR('Rule Violations per Station'),
                                                           MSGR('Station'),
                                                           self.violation_data)
        self.add_station_rows(details_table)
        self.add_total_row(details_table)
        self.add(prt.Isolate(details_table))

"""
Implementation of the calibration report Pattern Analysis
"""


from __future__ import division
from __future__ import absolute_import
import six
from six.moves import range
from functools import reduce
from collections import defaultdict
import itertools as it

import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave
from Localization import MSGR, bl_msgr
from RelTime import RelTime
import Cui

from carmusr.calibration import mappings
from carmusr.calibration.mappings import studio_palette as sp
from carmusr.calibration.mappings import bag_handler
from carmusr.calibration.util import basics
from carmusr.calibration.util import report_util
from carmusr.calibration.util import compare_plan


class ReportPatternAnalysis(report_util.CalibrationReport):

    require_level_duty = True

    def store_bag(self):
        self.tbh = bag_handler.WindowChains()
        self.bag = self.tbh.bag
        if self.tbh.warning:
            self.add_warning_text(self.tbh.warning)

    @staticmethod
    def get_basic_header_text():
        return report_util.CalibReports.PAT.title

    def get_header_text(self):
        return self.get_basic_header_text() + (MSGR(" - Table View") if self.arg('show') == "TABLE" else "")

    @staticmethod
    def get_form_handler(_variant):
        from carmusr.calibration.util import report_forms as rf
        return rf.pat_param_form_handler

    def create(self):

        self.setpaper(orientation=prt.LANDSCAPE)
        super(ReportPatternAnalysis, self).create()

        self.test_if_report_can_be_generated_and_store_bag()
        if self.skip_reason:
            self.add_warnings_and_links()
            return

        warning = self.prepare()
        if warning:
            self.add_warning_text(warning)

        self.add_warnings_and_links()
        self.setting_and_overview_row = prt.Row()
        self.add(prt.Isolate(self.setting_and_overview_row))
        self.setting_and_overview_col1 = self.setting_and_overview_row.add(prt.Column())
        self.add_settings_tables()
        self.setting_and_overview_col1.add(" ")
        self.add_overview()
        self.add("")
        self.page()

        if not self.bin_patterns:
            return

        if self.arg("show") == "TABLE":
            self.prepare_for_table()
            self.add_table()
        else:
            self.add_heatmaps()

    def prepare(self):

        self.gamma = rave.param("report_calibration.pat_centi_gamma").value() / 100

        if self.current_area_mode in (Cui.AcRotMode, Cui.LegMode):
            self.comp_full_name_if_relevant = ""
        else:
            self.comp_full_name_if_relevant = self.comparison_plan_name

        cd = DataCreator(self.bag, self.current_area, self.comp_full_name_if_relevant, self.current_area_mode)
        mess = cd.collect_data()
        self.bin_patterns = cd.bin_patterns
        self.use_filter = cd.use_filter
        if self.use_filter:
            self.bin_patterns_before_filtering = cd.bin_patterns_before_filtering
            self.num_legs_filter_param_names = cd.num_legs_filter_param_names

        return mess

    def prepare_for_table(self):

        if not self.bin_patterns:
            return

        # The corresponding labels are defined in TableViewSettingAlternatives
        common_methods = (BinPatternData.not_flown_block_time,
                          BinPatternData.total_block_time,
                          BinPatternData.fraction_of_crew_with_pattern_on_same_day_in_comp_plan,
                          lambda pd: pd.num_legs,
                          BinPatternData.get_num_crew_with_pattern,
                          lambda pd: len(pd.instances))

        table_colour_sel = rave.param("report_calibration.pat_table_colour_based_on").value()
        table_colour_reversed = rave.param("report_calibration.pat_table_reversed_colouring").value()
        if table_colour_sel == 7:
            gi = it.cycle((sp.White, sp.ReportLightBlue))
            BinPatternData.cc = lambda *_: next(gi)
            BinPatternData.colour_method = lambda *_: None
        else:
            table_col_m = common_methods[table_colour_sel - 1]
            cc = report_util.ColourCalculator(max(table_col_m(pat) for pat in six.itervalues(self.bin_patterns)),
                                              0,
                                              zero_colour=basics.HEATMAP_RED if table_colour_reversed else sp.White,
                                              max_colour=sp.White if table_colour_reversed else basics.HEATMAP_RED,
                                              gamma=self.gamma)
            BinPatternData.cc = cc
            BinPatternData.colour_method = table_col_m

        table_sort_sel = rave.param("report_calibration.pat_table_sort_order").value()
        self.table_sort_reversed = rave.param("report_calibration.pat_table_reversed_sort_order").value()
        self.table_sort_m = (common_methods + (lambda pd: pd.pattern,))[table_sort_sel - 1]

    def add_settings_tables(self):
        table = report_util.SimpleTable(MSGR("Settings"), use_page=False)
        self.setting_and_overview_col1.add(prt.Isolate(table))
        if not self.comp_full_name_if_relevant and self.comparison_plan_name:
            row = table.add(prt.Text(MSGR("Note:"),
                                     align=prt.LEFT,
                                     font=report_util.BOLD))
            row.add(prt.Text(MSGR("The comparison plan is ignored when the report is generated from legs or rotations"), align=prt.LEFT))
        row = table.add(prt.Text(rave.param(BinMatchingPatternHandler.parameter_name).remark() + ":",
                                 align=prt.LEFT,
                                 font=report_util.BOLD))
        row.add(prt.Text("%s" % BinMatchingPatternHandler.get_remark_of_selected(), align=prt.LEFT))
        if self.comp_full_name_if_relevant:
            row = table.add(prt.Text(rave.param(CompMatchingPatternHandler.parameter_name).remark() + ":",
                                     align=prt.LEFT,
                                     font=report_util.BOLD))
            row.add(prt.Text("%s" % CompMatchingPatternHandler.get_remark_of_selected(), align=prt.LEFT))

        p = rave.param("report_calibration.pat_use_filter")
        row = table.add(prt.Text(p.remark() + ":", font=report_util.BOLD, align=prt.LEFT))
        row.add(prt.Text(bl_msgr(str(p.value())), align=prt.LEFT))

        if self.use_filter:
            filter_table = report_util.SimpleTable(MSGR("Filter Settings"), use_page=False)
            self.setting_and_overview_row.add(" ")
            self.setting_and_overview_row.add(prt.Isolate(filter_table, rowspan=3))
            filter_items = ("report_calibration.pat_filter_max_completion",) + self.num_legs_filter_param_names
            for pn in filter_items:
                p = rave.param(pn)
                row = filter_table.add(prt.Text(p.remark() + ":", font=report_util.BOLD, align=prt.LEFT))
                row.add(prt.Text(bl_msgr(str(p.value())), align=prt.LEFT))

    def add_overview(self):
        table = report_util.SimpleTable(MSGR("Overview"), use_page=False)

        self.setting_and_overview_col1.add(prt.Isolate(table))

        if self.use_filter:
            table.add_sub_title("")
            table.add_sub_title(MSGR("Considered"))
            table.add_sub_title(MSGR("Before filtering"))

        rows = [table.add(report_util.SimpleTableRow(label + ":", **kwargs))
                for label, kwargs
                in ((MSGR("Number of patterns"), {}),
                    (MSGR("Number of pattern instances"), {}),
                    (MSGR("Number of fully sliced pattern instances"), {"border": prt.border(bottom=1, colour=sp.DarkGrey)}),
                    (MSGR("Number of 0% completed patterns"), {}),
                    (MSGR("Number of partly completed patterns"), {}),
                    (MSGR("Number of 100% completed patterns"), {"border": prt.border(bottom=1, colour=sp.DarkGrey)}),
                    (MSGR("Total block time in completed instances"), {}),
                    (MSGR("Total block time in not completed instances"), {}),
                    (MSGR("Total block time"), {}),
                    (MSGR("Percentage of block time in completed instances"), {}))]

        def add_to_rows(rows, patterns):
            all_ids = set(reduce(list.__iadd__, (pd.get_ids() for pd in six.itervalues(patterns)), []))
            all_action = report_util.get_select_action(self.current_area, all_ids)
            rows[0].add(prt.Text(len(patterns), align=prt.RIGHT, action=all_action))
            rows[1].add(sum(len(pat.instances) for pat in six.itervalues(patterns)))
            rows[2].add(sum(pat.get_num_crew_with_pattern() for pat in six.itervalues(patterns)))

            num_zero_completed_patterns = sum(1 for pd in six.itervalues(patterns) if pd.fraction_of_crew_with_pattern_on_same_day_in_comp_plan() == 0)
            ids_zero_completed_patterns = set(reduce(list.__iadd__, (pd.get_ids() for pd in six.itervalues(patterns)
                                                                     if pd.fraction_of_crew_with_pattern_on_same_day_in_comp_plan() == 0), []))

            num_fully_completed_patterns = sum(1 for pd in six.itervalues(patterns) if pd.fraction_of_crew_with_pattern_on_same_day_in_comp_plan() == 1)
            ids_fully_completed_patterns = set(reduce(list.__iadd__, (pd.get_ids() for pd in six.itervalues(patterns)
                                                                      if pd.fraction_of_crew_with_pattern_on_same_day_in_comp_plan() == 1), []))

            num_partly_completed_patterns = len(patterns) - num_fully_completed_patterns - num_zero_completed_patterns
            ids_partly_completed_patterns = all_ids - ids_fully_completed_patterns - ids_zero_completed_patterns

            rows[3].add(prt.Text(num_zero_completed_patterns, align=prt.RIGHT,
                                 action=report_util.get_select_action(self.current_area, ids_zero_completed_patterns)))
            rows[4].add(prt.Text(num_partly_completed_patterns, align=prt.RIGHT,
                                 action=report_util.get_select_action(self.current_area, ids_partly_completed_patterns)))
            rows[5].add(prt.Text(num_fully_completed_patterns, align=prt.RIGHT,
                                 action=report_util.get_select_action(self.current_area, ids_fully_completed_patterns)))

            tot_block = sum(pat.total_block_time() for pat in six.itervalues(patterns))
            tot_not_flown_block = sum(pat.not_flown_block_time() for pat in six.itervalues(patterns))
            tot_flown_block = tot_block - tot_not_flown_block

            completed_ids = set(reduce(list.__iadd__, (pd.get_completed_ids() for pd in six.itervalues(patterns)), []))
            action = report_util.get_select_action(self.current_area, completed_ids)
            rows[6].add(prt.Text(RelTime(tot_flown_block), align=prt.RIGHT, action=action))

            action = report_util.get_select_action(self.current_area, all_ids - completed_ids)
            rows[7].add(prt.Text(RelTime(tot_not_flown_block), align=prt.RIGHT, action=action))

            rows[8].add(prt.Text(RelTime(tot_block), align=prt.RIGHT, action=all_action))

            rows[9].add(prt.Text("%0.1f%%" % ((100 * tot_flown_block) / tot_block if tot_block else 0.0),
                                 align=prt.RIGHT))

        add_to_rows(rows, self.bin_patterns)

        if self.use_filter:
            add_to_rows(rows, self.bin_patterns_before_filtering)

    def add_table(self):
        table = report_util.SimpleTable(MSGR("Patterns"), use_page=True)
        self.add(prt.Isolate(table))

        info_lables = prt.Column(report_util.SimpleTableRow(prt.Text("", colspan=6),
                                                            prt.Text(MSGR("Block time"), border=prt.border(left=1), colspan=4, align=prt.CENTER)),
                                 report_util.SimpleTableRow(MSGR("Row"),
                                                            MSGR("Key"),
                                                            MSGR("Instances"),
                                                            MSGR("Slices"),
                                                            MSGR("Num legs"),
                                                            MSGR("Completion"),
                                                            prt.Text(MSGR("Completed"), border=prt.border(left=1)),
                                                            prt.Text(MSGR("Not Completed"), align=prt.RIGHT),
                                                            prt.Text(MSGR("Tot"), align=prt.RIGHT),
                                                            prt.Text(MSGR("Per slice")),
                                                            ))
        table.add_sub_title(info_lables)

        for ix, pd in enumerate(sorted(six.itervalues(self.bin_patterns), key=self.table_sort_m, reverse=self.table_sort_reversed)):
            v = (ix + 1,
                 prt.Text(pd.pattern,
                          width=350 if len(pd.pattern) > 60 else None,  # The best we can do without support for minwidth.
                          tooltip=pd.get_details_tooltip_string_all(),
                          action=pd.get_action_all()),
                 len(pd.instances),
                 pd.get_num_crew_with_pattern(),
                 pd.num_legs,
                 prt.Text("%0.1f%%" % (100 * pd.fraction_of_crew_with_pattern_on_same_day_in_comp_plan()), align=prt.RIGHT),
                 prt.Text(RelTime(pd.total_block_time() - pd.not_flown_block_time()),
                          action=pd.get_action_completed(),
                          tooltip=pd.get_details_tooltip_string_completed(),
                          align=prt.RIGHT),
                 prt.Text(RelTime(pd.not_flown_block_time()),
                          action=pd.get_action_not_completed(),
                          tooltip=pd.get_details_tooltip_string_not_completed(),
                          align=prt.RIGHT),
                 prt.Text(RelTime(pd.total_block_time()),
                          tooltip=pd.get_details_tooltip_string_all(),
                          action=pd.get_action_all(),
                          align=prt.RIGHT),
                 prt.Text(RelTime(pd.total_block_time() // pd.get_num_crew_with_pattern()), align=prt.RIGHT),
                 )

            r = table.add(report_util.SimpleTableRow(*v,
                                                     border=prt.border(colour=sp.LightGrey, top=1)
                                                     ))
            if pd.cc is not None:
                r.set(background=pd.get_background())

    def add_heatmaps(self):

        self.bh_num_slices = report_util.BinHandler(1,
                                                    rave.param("report_calibration.pat_slices_bin_size_1").value(),
                                                    rave.param("report_calibration.pat_slices_num_bins_with_size_1").value(),
                                                    rave.param("report_calibration.pat_slices_bin_size_2").value())
        self.num_slices_default_bins = range(15)

        bins_x = 20
        bin_size_x = 100 // bins_x

        aggregated_data = defaultdict(list)

        for pat in six.itervalues(self.bin_patterns):
            foc = pat.fraction_of_crew_with_pattern_on_same_day_in_comp_plan()
            if foc == 0:
                x_value = -1  # We use the x-value -1 for exact 0.
            else:
                x_value = int(100 * foc / bin_size_x)
            y_value = self.bh_num_slices.value2binnum(pat.get_num_crew_with_pattern())
            aggregated_data[(x_value, y_value)].append(pat)

        aggregated_data_for_heatmap_1 = defaultdict(lambda: (int(), list()))
        aggregated_data_for_heatmap_2 = defaultdict(lambda: (int(), list()))

        for key, pat_list in six.iteritems(aggregated_data):
            ids = reduce(list.__iadd__, (pat.get_ids() for pat in pat_list), [])
            aggregated_data_for_heatmap_1[key] = (len(pat_list), ids)
            aggregated_data_for_heatmap_2[key] = (sum(pat.total_block_time() for pat in pat_list), ids)

        def my_tooltip_f(x, y, *_):
            if x is None and y is None:
                patterns = reduce(list.__iadd__, six.itervalues(aggregated_data), [])
            elif x is None:
                patterns = reduce(list.__iadd__, (pats for (_, ykey), pats in six.iteritems(aggregated_data) if y == ykey), [])
            elif y is None:
                patterns = reduce(list.__iadd__, (pats for (xkey, _), pats in six.iteritems(aggregated_data) if x == xkey), [])
            else:
                patterns = aggregated_data[(x, y)]
            total_block_time = RelTime(sum(pat.total_block_time() for pat in patterns))
            total_block_time_nc = RelTime(sum(pat.not_flown_block_time() for pat in patterns))
            total_slices = sum(pat.get_num_crew_with_pattern() for pat in patterns)
            total_instances = sum(len(pat.instances) for pat in patterns)
            total_patterns = len(patterns)

            return "\n".join([MSGR("Patterns: %d") % total_patterns,
                              MSGR("Instances: %d") % total_instances,
                              MSGR("Slices: %d") % total_slices,
                              MSGR("Total block time: %s") % total_block_time,
                              MSGR("Uncompleted block time: %s") % total_block_time_nc])

        def get_hm(title, data, value_format):
            return report_util.Heatmap(self.current_area,
                                       title,
                                       data,
                                       show_total_row=True,
                                       show_total_col=True,
                                       keyname_x=MSGR("Completion (%)"),
                                       keyname_y=MSGR("# Slices"),
                                       value_col_min_width=26,
                                       value_format=value_format,
                                       x_keys=range(-1, bins_x + 1),
                                       x_key_format=lambda x: "{}{}{}".format(">" if x == 0 else "",
                                                                              max(x, 0) * bin_size_x,
                                                                              "" if x in (-1, bins_x) else " -"),
                                       y_keys=self.num_slices_default_bins,
                                       y_key_format=self.bh_num_slices.binnum2interval_string,
                                       gamma=self.gamma,
                                       tooltip_format=my_tooltip_f,
                                       font_normal_cell=prt.font(size=8),
                                       font_total_cell=prt.font(size=8, weight=prt.BOLD)
                                       )

        hm1 = get_hm(MSGR("Number of patterns"),
                     aggregated_data_for_heatmap_1,
                     value_format=lambda v: ("%s" % v) if v else "-",
                     )

        hm2 = get_hm(MSGR("Block Time (hours)"),
                     aggregated_data_for_heatmap_2,
                     value_format=lambda v: ("%s" % ((v + 30) // 60)) if int(v) else "-"
                     )

        self.add(prt.Isolate(hm1))
        self.add("")
        self.add(prt.Isolate(hm2))


class TableViewSettingAlternatives(object):

    _common_menu = [MSGR("Alternatives"),
                    "1. " + MSGR("Not completed block time"),
                    "2. " + MSGR("Total block time"),
                    "3. " + MSGR("Completion"),
                    "4. " + MSGR("Num legs"),
                    "5. " + MSGR("Crew slices"),
                    "6. " + MSGR("Instances")]

    colouring_menu = _common_menu + ["7. " + MSGR("Default")]
    sorting_menu = _common_menu + ["7. " + MSGR("Pattern key")]

    def __init__(self):
        raise NotImplementedError


class DataCreator(object):

    def __init__(self, bag, current_area, comp_full_name_if_relevant, area_mode):
        self.bag = bag
        self.current_area = current_area
        self.comp_full_name_if_relevant = comp_full_name_if_relevant
        self.area_mode = area_mode

    def collect_data(self):

        self.min_duty_connection_time = int(rave.eval("calibration_mappings.min_duty_connection_time")[0])

        self.bin_patterns = defaultdict(BinPatternData)
        self.partly_marked_patterns = 0
        BinPatternInstance.prepare_for_creation_of_instances(self.comp_full_name_if_relevant)

        for chain_bag in self.bag.chain_set():
            for bin_pattern_key, pattern_instance in self._get_pattern_instances_in_chain(chain_bag):
                self.bin_patterns[bin_pattern_key].add(bin_pattern_key, pattern_instance, self.current_area)

        BinPatternInstance.free_resources_after_creation_of_instances()

        mess = None
        if self.partly_marked_patterns:
            if self.partly_marked_patterns == 1:
                mess = MSGR("One partly selected pattern instance has been ignored")
            else:
                mess = MSGR("%s partly selected pattern instances have been ignored") % self.partly_marked_patterns

        del self.partly_marked_patterns
        del self.min_duty_connection_time

        self.use_filter = rave.param("report_calibration.pat_use_filter").value()
        if self.use_filter:
            self.num_legs_filter_param_names = ("report_calibration.pat_filter_keep_one_leg_patterns",
                                                "report_calibration.pat_filter_keep_two_legs_patterns",
                                                "report_calibration.pat_filter_keep_three_legs_patterns",
                                                "report_calibration.pat_filter_keep_four_legs_patterns",
                                                "report_calibration.pat_filter_keep_five_legs_patterns",
                                                "report_calibration.pat_filter_keep_six_or_more_legs_patterns")
            num_legs_filter_setting = tuple(rave.param(pn).value() for pn in self.num_legs_filter_param_names)
            max_completion_to_show = rave.param("report_calibration.pat_filter_max_completion").value() / 100

            self.bin_patterns_before_filtering = self.bin_patterns
            self.bin_patterns = {pat: data for pat, data in self.bin_patterns_before_filtering.items()
                                 if data.fraction_of_crew_with_pattern_on_same_day_in_comp_plan() <= max_completion_to_show
                                 and num_legs_filter_setting[min(data.num_legs, 6) - 1]}

        return mess

    def _get_pattern_instances_in_chain(self, chain_bag):

        if not any(lbag.marked() for lbag in chain_bag.atom_set()):
            return

        if self.area_mode in (Cui.AcRotMode, Cui.LegMode):
            crew_comp = 1
        else:
            crew_comp = rave.eval(chain_bag, rave.first(rave.Level.atom(), rave.var("calibration_mappings.crew_complement")))[0]
        trip_name = rave.eval(chain_bag, rave.first(rave.Level.atom(), rave.keyw("crr_name")))[0]
        base = chain_bag.calibration_mappings.homebase()

        # We use LB leg attributes and can't trust leg order.
        # To minimise (time consuming) Rave lookups we traverse the chain twice.

        pattern_data_per_ix = {}
        at_least_one_selected_leg = False
        selected = True
        first_leg_ix = 0
        pat_start = prev_end = None

        for ix, lbag in enumerate(chain_bag.atom_set(sort_by="report_calibration.pat_leg_start_utc_bin_matching")):
            leg_start = lbag.report_calibration.pat_leg_start_utc_bin_matching()
            if not pat_start:
                pat_start = leg_start
            if prev_end and leg_start - prev_end > self.min_duty_connection_time:
                pattern_data_per_ix[first_leg_ix] = (selected, pat_start, prev_end, leg_start)
                if at_least_one_selected_leg and not selected:
                    self.partly_marked_patterns += 1
                at_least_one_selected_leg = False
                selected = True
                first_leg_ix = ix
                pat_start = leg_start
            m = lbag.marked()
            if m:
                at_least_one_selected_leg = True
            if not m:
                selected = False
            prev_end = lbag.report_calibration.pat_leg_end_utc_bin_matching()

        pattern_data_per_ix[first_leg_ix] = (selected, pat_start, prev_end, None)
        if at_least_one_selected_leg and not selected:
            self.partly_marked_patterns += 1
        pattern_data_per_ix[ix + 1] = None  # For last leg checking

        pat_instance = this_pat_end = next_pat_start = None
        for ix, lbag in enumerate(chain_bag.atom_set(sort_by="report_calibration.pat_leg_start_utc_bin_matching")):
            if ix in pattern_data_per_ix:
                if pat_instance:
                    pat_key = pat_instance.finalize(lbag, this_pat_end, next_pat_start)
                    yield (pat_key, pat_instance)
                    pat_instance = None
                selected, this_pat_start, this_pat_end, next_pat_start = pattern_data_per_ix[ix]
                if selected:
                    pat_instance = BinPatternInstance(crew_comp, trip_name, base, this_pat_start)
            if pat_instance:
                is_last_leg = (ix + 1) in pattern_data_per_ix
                pat_instance.add_leg(lbag, is_last_leg)

        if pat_instance:
            pat_key = pat_instance.finalize(None, None, None)
            yield (pat_key, pat_instance)


class BinPatternInstance(object):

    @classmethod
    def prepare_for_creation_of_instances(cls, comp_full_name_if_relevant):

        if comp_full_name_if_relevant:
            comp_match_def_var = CompMatchingPatternHandler.get_matching_rave_variable()
            cls.keys_in_comp_plan = set(compare_plan.ComparisonPlanHandler.get_keys(comp_match_def_var,
                                                                                    mappings.LEVEL_DUTY))
        else:
            cls.keys_in_comp_plan = set()
        cls.comp_matching_key_ix = CompMatchingPatternHandler.get_selected_ix()

        cls.bin_matching_key_ix = BinMatchingPatternHandler.get_selected_ix()
        if cls.bin_matching_key_ix == 1:
            cls.leg_key_var = rave.var("report_calibration.pat_flight_key_bin_matching")
        else:
            cls.leg_key_var = rave.var("calibration_mappings.leg_start_station")

    @classmethod
    def free_resources_after_creation_of_instances(cls):
        del cls.keys_in_comp_plan
        del cls.leg_key_var
        del cls.bin_matching_key_ix
        del cls.comp_matching_key_ix

    def __init__(self, crew_comp, trip_name, base, this_pat_start):
        self.crew_comp = crew_comp
        self.trip_name = trip_name
        self.base = base
        self.start_utc = this_pat_start
        self.block_time = 0
        self.ids = []
        self.leg_bin_keys = []
        self.leg_comp_keys = []

    def add_leg(self, leg_bag, is_last):
        if not self.ids:  # first leg
            self.leg_comp_keys.append(leg_bag.report_calibration.pat_initial_string_first_leg_comp_matching())
            if self.bin_matching_key_ix == 1:
                self.leg_bin_keys.append(leg_bag.calibration_mappings.leg_start_station())  # Just for readability of pattern string
        self.block_time += leg_bag.report_calibration.pat_block_time_leg_bin_matching()
        self.ids.append(leg_bag.leg_identifier())
        self.leg_comp_keys.append(leg_bag.report_calibration.pat_flight_key_comp_matching())
        self.leg_bin_keys.append(rave.eval(leg_bag, self.leg_key_var)[0])
        if is_last:
            if self.bin_matching_key_ix == 2:
                self.leg_bin_keys.append(leg_bag.calibration_mappings.leg_end_station())
            if self.comp_matching_key_ix == 1:
                self.end_of_last_leg_comp = leg_bag.report_calibration.pat_leg_end_utc_comp_matching()

    def finalize(self, first_leg_next_pat_bag, pat_end, next_pat_start):

        bin_pattern_key = " ".join(self.leg_bin_keys)
        comp_pattern_key = " ".join(self.leg_comp_keys)
        if first_leg_next_pat_bag and self.bin_matching_key_ix == 1:
            bin_pattern_key += " %d %s" % ((next_pat_start - pat_end) // 1440,
                                           first_leg_next_pat_bag.report_calibration.pat_flight_key_bin_matching())
        if first_leg_next_pat_bag and self.comp_matching_key_ix == 1:
            full_days_to_next = (first_leg_next_pat_bag.report_calibration.pat_leg_start_utc_comp_matching() - self.end_of_last_leg_comp) // 1440
            comp_pattern_key += " %d %s" % (full_days_to_next, first_leg_next_pat_bag.report_calibration.pat_flight_key_comp_matching())
            del self.end_of_last_leg_comp
        self.in_comp_plan = comp_pattern_key in self.keys_in_comp_plan
        self.comp_match_string = comp_pattern_key

        del self.leg_bin_keys
        del self.leg_comp_keys

        return bin_pattern_key


class BinPatternData(object):

    info_lables = (MSGR("Pattern key"),
                   MSGR("Instances"),
                   MSGR("Crew slices"),
                   MSGR("Completion"),
                   MSGR("Num legs"),
                   MSGR("Block time / crew slices"),
                   MSGR("Tot. Block time"),
                   MSGR("Tot. not completed block time"))

    MAX_NUM_INSTANCES_IN_DETAILED_TOOLTIP = 25

    # Set from code using the class
    cc = None
    colour_method = None

    def __init__(self):
        self.instances = []
        self.pattern = None
        self.num_legs = None
        self._num_crew_with_pattern = None
        self._num_crew_with_pattern_in_comp_plan_on_same_date = None
        self._fraction_of_crew_with_pattern_on_same_day_in_comp_plan = None
        self._total_block_time = None
        self._action_all = None
        self._not_flown_block_time = None
        self._ids = None
        self._completed_ids = None
        self._not_completed_ids = None

    def add(self, pattern, instance, current_area):
        if not self.pattern:
            self.pattern = pattern
            self.current_area = current_area
            self.num_legs = len(instance.ids)
        self.instances.append(instance)

    def get_ids(self):
        if self._ids is None:
            self._ids = reduce(list.__iadd__, (ins.ids for ins in self.instances), [])
        return self._ids

    def get_completed_ids(self):
        if self._completed_ids is None:
            self._completed_ids = reduce(list.__iadd__, (ins.ids for ins in self.instances if ins.in_comp_plan), [])
        return self._completed_ids

    def get_not_completed_ids(self):
        if self._not_completed_ids is None:
            self._not_completed_ids = reduce(list.__iadd__, (ins.ids for ins in self.instances if not ins.in_comp_plan), [])
        return self._not_completed_ids

    def get_num_crew_with_pattern(self):
        if self._num_crew_with_pattern is None:
            self._num_crew_with_pattern = sum(ins.crew_comp for ins in self.instances)
        return self._num_crew_with_pattern

    def get_num_crew_with_pattern_in_comp_plan_on_same_date(self):
        if self._num_crew_with_pattern_in_comp_plan_on_same_date is None:
            self._num_crew_with_pattern_in_comp_plan_on_same_date = sum(ins.crew_comp for ins in self.instances if ins.in_comp_plan)
        return self._num_crew_with_pattern_in_comp_plan_on_same_date

    def fraction_of_crew_with_pattern_on_same_day_in_comp_plan(self):
        if self._fraction_of_crew_with_pattern_on_same_day_in_comp_plan is None:
            self._fraction_of_crew_with_pattern_on_same_day_in_comp_plan = (self.get_num_crew_with_pattern_in_comp_plan_on_same_date() /
                                                                            self.get_num_crew_with_pattern())
        return self._fraction_of_crew_with_pattern_on_same_day_in_comp_plan

    def not_flown_block_time(self):
        if self._not_flown_block_time is None:
            self._not_flown_block_time = sum(ins.crew_comp * ins.block_time for ins in self.instances if not ins.in_comp_plan)
        return self._not_flown_block_time

    def total_block_time(self):
        if self._total_block_time is None:
            self._total_block_time = sum((ins.crew_comp * ins.block_time for ins in self.instances))
        return self._total_block_time

    def get_details_tooltip_string_all(self):
        data = ["%s / %s / %s / %s / %s / %s\n    %s" % (ix + 1, it.trip_name, it.crew_comp, it.in_comp_plan,
                                                         RelTime(it.block_time), it.base, it.comp_match_string)
                for ix, it in enumerate(sorted(self.instances, key=lambda it: it.start_utc))]
        title = MSGR("%d INSTANCES\n\n# / Trip name / Num slices / Completed / Block time per slice / Base\n   Comp plan matching key\n") % len(data)
        cont = "\n".join(data[:self.MAX_NUM_INSTANCES_IN_DETAILED_TOOLTIP])
        if len(data) > self.MAX_NUM_INSTANCES_IN_DETAILED_TOOLTIP:
            cont += "\n .... and %s more ..." % (len(data) - self.MAX_NUM_INSTANCES_IN_DETAILED_TOOLTIP)
        return title + cont

    def get_details_tooltip_string_completed(self):
        data = ["%s / %s / %s / %s / %s\n    %s" % (ix + 1, it.trip_name, it.crew_comp, RelTime(it.block_time), it.base, it.comp_match_string)
                for ix, it in enumerate(sorted((ins for ins in self.instances if ins.in_comp_plan), key=lambda it: it.start_utc))]
        cont = "\n".join(data[:self.MAX_NUM_INSTANCES_IN_DETAILED_TOOLTIP])
        if cont:
            if len(data) > self.MAX_NUM_INSTANCES_IN_DETAILED_TOOLTIP:
                cont += MSGR("\n .... and %s more ...") % (len(data) - self.MAX_NUM_INSTANCES_IN_DETAILED_TOOLTIP)
            title = MSGR("%d COMPLETED INSTANCES\n# / Trip name / Num slices / Block time per slice / Base\n   Comp plan matching key \n") % len(data)
        else:
            title = MSGR("No instances are completed")
        return title + cont

    def get_details_tooltip_string_not_completed(self):
        data = ["%s / %s / %s / %s / %s\n    %s" % (ix + 1, it.trip_name, it.crew_comp, RelTime(it.block_time), it.base, it.comp_match_string,)
                for ix, it in enumerate(sorted((ins for ins in self.instances if not ins.in_comp_plan), key=lambda it: it.start_utc))]
        cont = "\n".join(data[:self.MAX_NUM_INSTANCES_IN_DETAILED_TOOLTIP])
        if cont:
            if len(data) > self.MAX_NUM_INSTANCES_IN_DETAILED_TOOLTIP:
                cont += MSGR("\n .... and %s more ...") % (len(data) - self.MAX_NUM_INSTANCES_IN_DETAILED_TOOLTIP)
            title = MSGR("%d NOT COMPLETED INSTANCES\n# / Trip name / Num slices / Block time per slice / Base\n   Comp plan matching key\n") % len(data)
        else:
            title = MSGR("All instances are completed")

        return title + cont

    def get_background(self):
        return self.cc(self.colour_method())

    def get_action_all(self):
        if self._action_all is None:
            self._action_all = report_util.get_select_action(self.current_area, self.get_ids())
        return self._action_all

    def get_action_completed(self):
        return report_util.get_select_action(self.current_area, self.get_completed_ids())

    def get_action_not_completed(self):
        return report_util.get_select_action(self.current_area, self.get_not_completed_ids())


class _MatchingPatternHandler(object):

    alternatives = [MSGR("Alternatives")]
    parameter_name = None

    @classmethod
    def get_selected_ix(cls):
        return rave.param(cls.parameter_name).value()

    @classmethod
    def get_remark_of_selected(cls):
        return cls.alternatives[cls.get_selected_ix()]


class BinMatchingPatternHandler(_MatchingPatternHandler):

    alternatives = _MatchingPatternHandler.alternatives + ["1. " + MSGR("Same legs in duty and after layover"),
                                                           "2. " + MSGR("Same stations in duty")]
    parameter_name = "report_calibration.pat_bin_pattern_p"


class CompMatchingPatternHandler(_MatchingPatternHandler):

    alternatives = _MatchingPatternHandler.alternatives + ["1. " + MSGR("Same date and same legs in duty and after layover"),
                                                           "2. " + MSGR("Same date and same legs in duty")]
    parameter_name = "report_calibration.pat_comp_pattern_p"

    @classmethod
    def get_matching_rave_variable(cls):
        return rave.var("report_calibration.pat_key_comp_matching_" + str(rave.param(cls.parameter_name).value()))

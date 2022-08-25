"""
Sensitivity Index Distribution report class
"""


from __future__ import division
from __future__ import absolute_import
from six.moves import range
from six.moves import zip
from functools import reduce

import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave
from Localization import MSGR
import Cui

from carmusr.calibration.mappings import studio_palette as sp
from carmusr.calibration.util import report_util
from carmusr.calibration.util import basics
from carmusr.calibration.util import common


def get_bar_colour(x, si_limits):
    limits = len(si_limits)
    # Called with None from PRT framework as part of setup
    if x is None or limits > 0 and x < si_limits[0]:
        return sp.ReportLightBlue
    elif limits > 1 and x < si_limits[1]:
        return sp.ReportBlue
    elif limits > 2 and x < si_limits[2]:
        return sp.JeppesenLightBlue
    else:
        return sp.JeppesenBlue


def calculate_range_and_step_size(value_min, value_max, approx_no_steps):
    assert approx_no_steps > 0
    value_max = max(value_min + 1, value_max)
    rng = abs(value_max - value_min)
    rng_resolution = max(len(str(abs(value_min))), len(str(abs(value_max))))
    best_step = 1
    best_proximity = abs(rng - approx_no_steps)
    best_step_found = False
    for r in [10 ** i for i in range(1, rng_resolution)]:
        for j in range(1, 9):
            step = r * j
            proximity = abs(rng // step - approx_no_steps)
            if best_proximity >= proximity:
                best_step, best_proximity = step, proximity
            else:
                best_step_found = True
                break
        if best_step_found:
            break

    rng_start = value_min - abs(value_min % best_step)
    rng_end = (abs(value_max // best_step) + 1) * best_step
    return (rng_start, rng_end, best_step)


class SensitivityIndexDistributionReport(report_util.CalibrationReport):
    '''
    Percent values to use in statistics
    '''
    percent_1 = 0.01  # 1% reversed
    percent_2 = 0.025  # 2.5% reversed
    percent_3 = 0.05  # 5% reversed
    percent_4 = 0.1  # 10% reversed

    has_table_view = False

    @staticmethod
    def get_header_text():
        return report_util.CalibReports.SI.title

    def store_bag(self):
        self.rave_var = rave.var(self.pconfig.si_report_variable_name)
        self.level_info = self.pconfig.levels_dict[self.rave_var.level().name()]
        self.bag = self.get_top_bag_for_level_and_write_warning_once(self.level_info.name)

    @staticmethod
    def get_form_handler(_variant):
        from carmusr.calibration.util import report_forms as rf
        return rf.si_param_form_handler

    def create(self):
        self.setpaper(orientation=prt.LANDSCAPE)

        super(SensitivityIndexDistributionReport, self).create()

        self.test_if_report_can_be_generated_and_store_bag()
        if self.skip_reason:
            self.add_warnings_and_links()
            return

        '''
        Graph dimensions
        '''

        self.show_zeroes = False
        self.approx_steps = 40

        # Used for graph colouring.
        si_limits = [rave.param('calibration.sensitivity_index_level_{}'.format(ix)).getValue() for ix in range(1, 5)]

        zero_sensitivity_count = 0
        zero_ids = []
        sensitivity_index_list = []
        leg_identifiers_per_object = []
        plan_total_si = 0
        object_iterator = common.get_atomic_iterator_for_level(self.bag, self.level_info.name)
        for obag in object_iterator(sort_by=self.pconfig.si_report_variable_name):
            crew_comp = 1 if self.current_area_mode in (Cui.AcRotMode, Cui.LegMode) else obag.calibration_mappings.crew_complement()
            if not crew_comp:
                continue
            rave_value = rave.eval(obag, self.rave_var)[0]
            if rave_value != 0 or self.show_zeroes:
                sensitivity_index_list += [rave_value] * crew_comp
                # it is enough to store the leg identifiers for the first planning object.
                leg_identifiers_per_object += [[leg_bag.leg_identifier() for leg_bag in obag.atom_set()]] + [[]] * (crew_comp - 1)
                plan_total_si += rave_value * crew_comp
            else:
                zero_sensitivity_count += crew_comp
                zero_ids.append([leg_bag.leg_identifier() for leg_bag in obag.atom_set()])

        if not sensitivity_index_list:
            self.add_warning_text(MSGR('No {} in selection with a sensitivity index > 0.').format(self.level_info.objects_name_in_gui))
            self.add_warnings_and_links()
            return

        self.add_warnings_and_links()

        # real min and max values from si distribution
        real_min = min(sensitivity_index_list)
        real_max = max(sensitivity_index_list)

        self.xmin, self.xmax, self.step = calculate_range_and_step_size(real_min, real_max, self.approx_steps)

        # Recalculate number of bins
        self.steps = (self.xmax - self.xmin) // self.step

        data, grouped_legs = self.plot_ranges(sensitivity_index_list, leg_identifiers_per_object)
        all_index_list = [0] * zero_sensitivity_count + sensitivity_index_list

        current_area = self.current_area  # To avoid reference to report instance from registered action.

        action = prt.chartaction(lambda x, _: report_util.calib_show_and_mark_legs(current_area,
                                                                                   reduce(list.__iadd__, grouped_legs[x], [])))
        graph = prt.Bar(fill=lambda x, _: get_bar_colour(x, si_limits),
                        width=0.8)

        si_histogram = report_util.SimpleDiagram(prt.Text(MSGR("Sensitivity Index Distribution"),
                                                          valign=prt.CENTER))

        si_histogram.add(prt.Isolate(
            prt.Chart(400,
                      200,
                      prt.Series(data,
                                 graph=graph,
                                 yaxis_name=MSGR("Number of {}").format(self.level_info.objects_name_in_gui),
                                 action=action),
                      xaxis_name=MSGR("Predicted Sensitivity"),
                      xaxis_limits=(self.xmin,
                                    self.xmax))))

        h0 = prt.Row("",
                     MSGR("Lowest%s" % ("" if self.show_zeroes else ">0")),
                     MSGR("Highest"),
                     MSGR("Total"),
                     MSGR("Average"),
                     MSGR("Num {}").format(self.level_info.objects_name_in_gui))

        num_objects = len(all_index_list)
        v0 = prt.Row("",
                     min(sensitivity_index_list),
                     max(sensitivity_index_list),
                     plan_total_si,
                     basics.round_to_int(plan_total_si / num_objects),
                     num_objects)

        h1 = prt.Row(*(prt.Text(it)
                       for it in (MSGR("Statistics (for worst % of {})").format(self.level_info.objects_name_in_gui),
                                  "%g%%" % (SensitivityIndexDistributionReport.percent_1 * 100),
                                  "%g%%" % (SensitivityIndexDistributionReport.percent_2 * 100),
                                  "%g%%" % (SensitivityIndexDistributionReport.percent_3 * 100),
                                  "%g%%" % (SensitivityIndexDistributionReport.percent_4 * 100))),
                     border=prt.border_frame(1))

        perc2idx = lambda p: int(num_objects * (1 - p))  # @IgnorePep8

        v1 = prt.Row(MSGR("Lowest Sensitivity:"),
                     all_index_list[perc2idx(SensitivityIndexDistributionReport.percent_1)],
                     all_index_list[perc2idx(SensitivityIndexDistributionReport.percent_2)],
                     all_index_list[perc2idx(SensitivityIndexDistributionReport.percent_3)],
                     all_index_list[perc2idx(SensitivityIndexDistributionReport.percent_4)])

        v2 = prt.Row(MSGR("Average Sensitivity:"),
                     basics.round_to_int(basics.mean(all_index_list[perc2idx(SensitivityIndexDistributionReport.percent_1):])),
                     basics.round_to_int(basics.mean(all_index_list[perc2idx(SensitivityIndexDistributionReport.percent_2):])),
                     basics.round_to_int(basics.mean(all_index_list[perc2idx(SensitivityIndexDistributionReport.percent_3):])),
                     basics.round_to_int(basics.mean(all_index_list[perc2idx(SensitivityIndexDistributionReport.percent_4):])))

        si_histogram.add(prt.Column(h0, v0, prt.Row(""), h1, v1, v2))

        # Draws si details table
        si_details = report_util.SimpleTable(MSGR('Sensitivity Details'), use_page=False)
        si_details.add_sub_title(prt.Text(MSGR('Sensitivity Range')))
        si_details.add_sub_title(prt.Text(MSGR('Number of {}').format(self.level_info.objects_name_in_gui)))
        si_details2 = prt.Column()
        MAX_ROWS_IN_TAB_1 = 18
        index = 0
        num_data = len(data)

        if not self.show_zeroes:
            range_text = prt.Text("0", align=prt.RIGHT)
            row = si_details.add(range_text)
            ids = reduce(list.__iadd__, zero_ids, [])
            num_legs_text = prt.Text(zero_sensitivity_count,
                                     action=report_util.get_select_action(self.current_area, ids),
                                     align=prt.RIGHT)
            row.add(num_legs_text)

        while index < num_data:
            # The data is grouped with the center of the interval as the key
            interval_key = data[index][0]
            interval_start = data[index][0] - self.step // 2
            interval_end = interval_start + self.step - 1

            # Adjustments for 0 values
            if not self.show_zeroes and interval_start == 0:
                interval_start = 1

            num_legs_in_interval = data[index][1]
            legs_in_interval = reduce(list.__iadd__, grouped_legs[interval_key], [])

            range_text = prt.Text("%s-%s" % (interval_start, interval_end),
                                  align=prt.RIGHT)

            action = report_util.get_select_action(self.current_area, legs_in_interval)

            num_legs_text = prt.Text(num_legs_in_interval,
                                     align=prt.RIGHT,
                                     action=action)

            # Two tables needed for support of page breaks in PDF.
            if index <= MAX_ROWS_IN_TAB_1:
                row = si_details.add(range_text)
                row.add(num_legs_text)
                if index == MAX_ROWS_IN_TAB_1 and num_data > MAX_ROWS_IN_TAB_1:
                    row.set(border=prt.border(bottom=1, colour=sp.White))
            else:
                si_details2.add(prt.Row("", "",
                                        report_util.SimpleTableRow(range_text, num_legs_text,
                                                                   border=prt.border(colour=report_util.SIMPLE_TABLE_BORDER_GREY,
                                                                                     left=1, right=1,
                                                                                     bottom=1 if index + 1 == num_data else None),
                                                                   background=report_util.SimpleTable.get_background_color_for_row(index + 1)
                                                                   )))
                si_details2.page0()
            index = index + 1

        # Draws histogram and details table
        self.add(prt.Row(prt.Isolate(si_histogram), " ", si_details))
        self.page()
        self.add(si_details2)

    def plot_ranges(self, index_list, leg_identifiers):
        """
        Calculates the values for each bar in the histogram,
        representing the number of chains with values in the range
        [Xn, Xn + step-1]
        """

        # Creates a list with the si values for each interval
        # The centre of the interval is used to make the histogram easier to interpret
        interval_value = [0] * (self.steps + 1)
        for index in range(self.steps + 1):
            # Store the centre values for the bars on the x-axis
            interval_value[index] = self.xmin + index * self.step + self.step // 2

        # Creates a list containing the number of si values(chains) for each interval
        interval_count = [0] * (self.steps)

        # This dictionary will be a mappings from x_val -> leg_identifiers
        # Initializing to empty lists
        grouped_legs = dict()
        for x_val in interval_value:
            grouped_legs[x_val] = list()

        for (ix, index) in enumerate(index_list):
            pos = (index - self.xmin) // self.step
            interval_count[pos] += 1
            grouped_legs.setdefault(interval_value[pos], list()).append(leg_identifiers[ix])

        # list of lists with intervals and counters
        data = list(zip(interval_value, interval_count))

        return (data, grouped_legs)

"""
Alertness report classes
"""

import Gui
import Cui
import carmensystems.publisher.api as prt
from Localization import MSGR
from BSIRAP import RelTime
from Airport import Airport

from carmusr.fatigue.kpi import mean
from carmusr.fatigue_compat.ots_studiopalette import studio_palette
from carmusr.fatigue_compat.ots_area import get_opposite_area
from carmusr.fatigue_compat.ots_standardreport import SimpleDiagram, SimpleTable, StandardReport


def get_bar_colour(x, low_alertness_limit):

    if (x < low_alertness_limit):
        return studio_palette.ReportBlue
    else:
        return studio_palette.ReportLightBlue


class AlertnessDistributionReport(StandardReport):
    '''
    Percent values to use in alertness statistics
    '''
    percent_1 = 0.01   # 1%
    percent_2 = 0.025  # 2.5%
    percent_3 = 0.05   # 5%
    percent_4 = 0.1    # 10%

    def get_header_text(self):
        return MSGR('Alertness Distribution Report')

    def create(self):

        self.setpaper(orientation=prt.LANDSCAPE)
        self.warning = ""
        super(AlertnessDistributionReport, self).standard_header()
        super(AlertnessDistributionReport, self).standard_footer()

        # Store the current area and bag for interaction
        current_area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        filter_area = get_opposite_area(current_area)

        '''
        Graph dimensions
        '''
        self.xmin = 0
        self.xmax = 10000
        self.steps = 40
        self.step = int((self.xmax - self.xmin) / self.steps)
        self.max_abs = max(abs(self.xmin), abs(self.xmax))
        # Used for graph colouring
        low_alertness_limit = 3000
        # Used for creation of Alertness Details table to the right
        self.must_show_details_limit = 4000
        self.preferred_show_details_boxes = 18

        bag = self.get_bag()
        alertness_index_list = []
        leg_identifiers = []
        plan_afr = 0
        for leg_bag in bag.atom_set(where='fatigue.%leg_should_be_checked_for_alertness% and fatigue.%trip_should_be_checked_for_alertness%',
                                    sort_by='fatigue.%alertness_leg_tod_value%'):
            alertness_index_list.append(leg_bag.fatigue.alertness_leg_tod_value())
            leg_identifiers.append(str(leg_bag.leg_identifier()))
            plan_afr += leg_bag.fatigue.leg_afr()

        if not alertness_index_list:
            self.add(prt.Text('No valid alertness legs in selection.'))
            return

        # real min and max values from alertness distribution
        real_min = min(alertness_index_list)
        real_max = max(alertness_index_list)

        # Round down/up to nearest interval-limit using modulus and set new limits
        self.xmin = max(self.xmin,
                        real_min - real_min % self.step)
        self.xmax = min(self.xmax,
                        real_max + (self.step - real_max % self.step))
        # Recalculate number of bins
        self.steps = (self.xmax - self.xmin) / self.step

        data, grouped_legs = self.plot_ranges(alertness_index_list, leg_identifiers)
        no_data_legs = len(alertness_index_list)

        # Note.
        # If instance variables or class methods are used in the lambda functions
        # the report instances are never removed.

        action = prt.chartaction(lambda x, _: show_legs(current_area, filter_area, grouped_legs[x]))
        graph = prt.Bar(fill=lambda x, _: get_bar_colour(x, low_alertness_limit),
                        width=0.8)

        alertness_histogram = SimpleDiagram(prt.Text(MSGR("Alertness Distribution"),
                                                     valign=prt.CENTER))

        alertness_histogram.add(prt.Isolate(
            prt.Chart(400,
                      200,
                      prt.Series(data,
                                 graph=graph,
                                 yaxis_name=MSGR("Number of Positions"),
                                 action=action),
                      xaxis_name=MSGR("Predicted Alertness, CAS points"),
                      xaxis_limits=(self.xmin,
                                    self.xmax))))

        h0 = prt.Row("",
                     MSGR("Lowest"),
                     MSGR("AFR"),
                     MSGR("NFR"),
                     MSGR("Positions"))

        v0 = prt.Row("",
                     min(alertness_index_list),
                     int(plan_afr),
                     int(plan_afr / len(alertness_index_list)),
                     len(alertness_index_list))

        h1 = prt.Row(*(prt.Text(it)
                       for it in (MSGR("Statistics (for worst % of legs)"),
                                  "%g%%" % round(AlertnessDistributionReport.percent_1 * 100, 1),
                                  "%g%%" % round(AlertnessDistributionReport.percent_2 * 100, 1),
                                  "%g%%" % round(AlertnessDistributionReport.percent_3 * 100, 1),
                                  "%g%%" % round(AlertnessDistributionReport.percent_4 * 100, 1))),
                     border=prt.border_frame(1))

        v1 = prt.Row(MSGR("Best alertness:"),
                     alertness_index_list[max(0, int(no_data_legs * AlertnessDistributionReport.percent_1) - 1)],
                     alertness_index_list[max(0, int(no_data_legs * AlertnessDistributionReport.percent_2) - 1)],
                     alertness_index_list[max(0, int(no_data_legs * AlertnessDistributionReport.percent_3) - 1)],
                     alertness_index_list[max(0, int(no_data_legs * AlertnessDistributionReport.percent_4) - 1)])

        v2 = prt.Row(MSGR("Average alertness:"),
                     int(mean(alertness_index_list[0:max(1, int(no_data_legs * AlertnessDistributionReport.percent_1))])),
                     int(mean(alertness_index_list[0:max(1, int(no_data_legs * AlertnessDistributionReport.percent_2))])),
                     int(mean(alertness_index_list[0:max(1, int(no_data_legs * AlertnessDistributionReport.percent_3))])),
                     int(mean(alertness_index_list[0:max(1, int(no_data_legs * AlertnessDistributionReport.percent_4))])))

        alertness_histogram.add(prt.Column(h0, v0, prt.Row(""), h1, v1, v2))

        # Draws alertness details table
        alertness_details = SimpleTable(MSGR('Alertness Details'), use_page=False)
        alertness_details.add_sub_title(prt.Text(MSGR('Alertness Range')))
        alertness_details.add_sub_title(prt.Text(MSGR('Number of Positions')))

        index = 0
        num_data = len(data)
        while index < num_data and (index < self.preferred_show_details_boxes or
                                    data[index][0] < self.must_show_details_limit):
            # The data is grouped with the center of the interval as the key
            interval_key = data[index][0]
            interval_start = data[index][0] - self.step / 2
            interval_end = interval_start + self.step - 1
            num_legs_in_interval = data[index][1]
            legs_in_interval = grouped_legs[interval_key]

            range_text = prt.Text("%s-%s" % (interval_start, interval_end))

            action = prt.action(show_legs, (current_area,
                                            filter_area,
                                            legs_in_interval))
            num_legs_text = prt.Text(num_legs_in_interval,
                                     align=prt.RIGHT,
                                     action=action
                                     )

            row = alertness_details.add(range_text)
            row.add(num_legs_text)
            index = index + 1

        # Draws histogram and details table
        self.add(prt.Row(prt.Isolate(alertness_histogram), " ", alertness_details))

    def plot_ranges(self, index_list, leg_identifiers):
        """
        Calculates the values for each bar in the histogram,
        representing the number of chains with values in the range
        [Xn, Xn + step-1]
        """

        # Creates a list with the alertness values for each interval
        # The centre of the interval is used to make the histogram easier to interpret
        interval_value = [0] * (self.steps + 1)
        for index in range(self.steps + 1):
            # Store the centre values for the bars on the x-axis
            interval_value[index] = self.xmin + index * self.step + self.step / 2

        # Creates a list containing the number of alertness values(chains) for each interval
        interval_count = [0] * (self.steps)

        # This dictionary will be a mappings from x_val -> leg_identifiers
        # Initializing to empty lists
        grouped_legs = dict()
        for x_val in interval_value:
            grouped_legs[x_val] = list()

        for (ix, index) in enumerate(index_list):
            pos = (index - self.xmin) / self.step
            interval_count[pos] += 1
            grouped_legs.setdefault(interval_value[pos], list()).append(leg_identifiers[ix])

        # list of lists with intervals and counters
        data = zip(interval_value, interval_count)

        return (data, grouped_legs)


def show_legs(current_area, filter_area, leg_identifiers):

    # Adds a state to the UNDO stack
    Cui.CuiExecuteFunction('PythonEvalExpr("0")',
                           'Show alertness legs',
                           Gui.POT_REDO,
                           Gui.OPA_OPAQUE)

    Cui.CuiDisplayGivenObjects(Cui.gpc_info,
                               filter_area,
                               Cui.CuiGetAreaMode(Cui.gpc_info, current_area),
                               Cui.LegMode,
                               leg_identifiers)

    Cui.CuiUnmarkAllLegs(Cui.gpc_info,
                         filter_area,
                         "window")

    for leg_identifier in leg_identifiers:
        Cui.CuiSetSelectionObject(Cui.gpc_info,
                                  filter_area,
                                  Cui.LegMode,
                                  leg_identifier)
        Cui.CuiMarkLegs(Cui.gpc_info, filter_area, "object")


def get_weekday(time):
    """
    @param time: time to evaluate weekday on
    @type time: RelTime or Abstime
    @returns: Weekday for time
    @rtype: String
    """
    index = int(time.time_of_week() / RelTime("24:00"))

    return ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")[index]


def day_range(first_day, end_day):
    """
    Generator of days to loop over from first_day to end_day
    @param first_day: First day of the loop
    @type first_day: AbsTime
    @param end_day: Last day of the loop
    @type end_day: AbsTime
    """

    day = first_day
    while day <= end_day:
        yield day
        day = day.adddays(1)


# gantt functions to draw gantt boxes
def get_bar_width(date):
    """
    Returns the width of the bar. It is doubled for Mondays.
    @param date: The date to evaluate bar width on
    @type date: AbsTime
    @returns: bar width
    @rtype: int
    """

    if date.time_of_week() / RelTime("24:00") == 0:
        return 2
    return 1


class Gantt(prt.Canvas):
    """
    Kind of abstract class to derive from. It represents
    a Gantt. The bars for the days are drawn.
    The child class must have a draw method.
    """
    def __init__(self, start_day, end_day, width, height, **kw):
        prt.Canvas.__init__(self, width, height, **kw)
        self.start_day = start_day
        self.end_day = end_day

    def draw(self, gc):
        """
        Has to be called in the draw method of the child class.
        """
        _, y0, _, y1 = gc.get_coordinates()
        gc.coordinates(self.start_day, y0, self.end_day, y1)
        self._draw_bars(gc, y0, y1)

    def _draw_bars(self, gc, y0, y1):
        """
        draw the bars of the gantt.
        the get_bar_width function is called to determine the width of the bars.
        """
        for day in day_range(self.start_day.day_floor(),
                             self.end_day.day_ceil()):
            gc.path([(day, y0), (day, y1)], width=get_bar_width(day))


class GanttHeader(Gantt):
    def draw(self, gc):

        # calls the parent draw method for the bars
        Gantt.draw(self, gc)

        # computes the 'y' positions
        _, y0, _, y1 = gc.get_coordinates()
        text_height = gc.text_size("CODE")[1]
        padding = int((y1 - y0 - 2 * text_height) / 2)
        weekday_pos = y1 - padding
        date_pos = y0 + padding + text_height

        for day in day_range(self.start_day, self.end_day):
            _, _, date, _, _ = day.split()

            # draw weekday string
            gc.text(day + RelTime('12:00'),
                    weekday_pos,
                    MSGR(get_weekday(day)),
                    align=prt.CENTER)

            # draw date number
            gc.text(day + RelTime('12:00'),
                    date_pos,
                    date,
                    align=prt.CENTER)


class FatigueRosterGantt(Gantt):
    """
    object used to draw the crew gantt.
    """
    def __init__(self, start_day, end_day, width, roster_bag, **kw):
        self.leg_list = []
        self.start_day = start_day
        self.chain_name = roster_bag.report_fatigue.chain_id()
        self.name_array = []

        for leg_bag in roster_bag.fatigue_mappings.frms_leg_set():
            leg_start = leg_bag.report_fatigue.leg_start_hb()
            leg_end = leg_bag.report_fatigue.leg_end_hb()

            if leg_start > end_day or leg_end < start_day:
                continue

            if leg_bag.report_fatigue.ignore_leg():
                # The leg has been pruned away so we do not draw it
                continue

            leg = {}

            leg['start'] = leg_bag.report_fatigue.leg_start_hb()
            leg['end'] = leg_bag.report_fatigue.leg_end_hb()
            leg['is_deadhead'] = leg_bag.report_fatigue.is_deadhead()
            leg['is_ground_transport'] = leg_bag.report_fatigue.is_ground_transport()
            leg['is_flight_duty'] = leg_bag.report_fatigue.is_flight_duty()
            leg['is_on_duty'] = leg_bag.report_fatigue.is_work()
            leg['is_first_in_trip'] = leg_bag.report_fatigue.is_first_in_trip()
            leg['prev_leg_end'] = leg_bag.report_fatigue.prev_leg_end()

            leg['last_in_duty'] = leg_bag.report_fatigue.is_last_in_duty()
            leg['first_in_duty'] = leg_bag.report_fatigue.is_first_in_duty()
            leg['capi_arrival'] = leg_bag.report_fatigue.arrival_hb()
            leg['sleep_start'] = leg_bag.report_fatigue.sleep_start()
            leg['sleep_end'] = leg_bag.report_fatigue.sleep_end()

            leg['time_zone_diff'] = str(leg_bag.report_fatigue.leg_end_lt() -
                                        leg_bag.report_fatigue.leg_end_hb())

            leg['start_lt'] = leg_bag.report_fatigue.leg_start_lt()
            leg['end_lt'] = leg_bag.report_fatigue.leg_end_lt()
            leg['start_station'] = leg_bag.report_fatigue.leg_start_station()
            leg['end_station'] = leg_bag.report_fatigue.leg_end_station()
            leg['leg_id'] = leg_bag.report_fatigue.leg_id_string()
            leg['leg_short_id'] = leg_bag.report_fatigue.leg_short_id()
            leg['tod_alertness_value'] = leg_bag.report_fatigue.alertness_leg_tod_value()
            self.leg_list.append(leg)

        # the 'y' positions of the different texts and rectangle
        self.leg_top = 40
        Gantt.__init__(self, start_day, end_day, width, 50, **kw)

    def set_name_array(self, name_array):
        self.name_array = name_array

    def draw(self, gc):
        # calls the parent draw method where the bars are drawn
        Gantt.draw(self, gc)

        # this method is redefined in the sub classes
        # draws the information in the gantt view
        self.draw_legs(gc)

    def draw_legs(self, gc):
        for leg in self.leg_list:
            # Draw leg

            if leg['is_ground_transport']:
                color = studio_palette.Ground_Transport
            elif leg['is_deadhead']:
                color = studio_palette.Deadhead_leg
            elif leg['is_flight_duty']:
                color = studio_palette.Leg_in_RTD
            elif leg['is_on_duty']:
                color = studio_palette.Task
            else:
                color = studio_palette.Pact

            alertness_string = ""
            if leg['tod_alertness_value'] > 0:
                alertness_string = "\nAlertness (TOD): %s" % leg['tod_alertness_value']
            gc.rectangle(leg['start'],
                         self.leg_top,
                         leg['end'] - leg['start'],
                         20,
                         tooltip="%s%s\n%s %s - %s %s%s" % (
                             " " * 15,
                             leg['leg_id'],
                             leg['start_station'],
                             "%02d:%02d" % leg['start'].split()[-2:],
                             "%02d:%02d" % leg['end'].split()[-2:],
                             leg['end_station'],
                             alertness_string),
                         fill=color, linewidth=1,
                         colour=studio_palette.Black)
            # Draw leg-info for first and last activity in duties
            leginfo = ""
            al = None
            if (leg['last_in_duty'] or leg['first_in_duty']):
                leginfo = leg['leg_short_id']
            if leg['last_in_duty'] and leg['first_in_duty']:
                al = prt.CENTER
            elif leg['last_in_duty']:
                al = prt.LEFT
            elif leg['first_in_duty']:
                al = prt.RIGHT
            if leginfo:
                gc.text(leg['start'] + (leg['end'] - leg['start']) / 2,
                        self.leg_top + 6, leginfo, align=al, font=prt.font(size=6))

            # Draw trip-connector
            if not leg['is_first_in_trip']:
                gc.rectangle(leg['prev_leg_end'], self.leg_top - 10 + 1,
                             leg['start'] - leg['prev_leg_end'], 2, fill=studio_palette.Black)

            # Draw sleep opportunity
            args = (leg['capi_arrival'] + leg['sleep_start'], 5,
                    leg['sleep_end'] - leg['sleep_start'], 5)
            kw = {"tooltip": "%s - %s" % ("%02d:%02d" % (leg['capi_arrival'] + leg['sleep_start']).split()[-2:],
                                          "%02d:%02d" % (leg['capi_arrival'] + leg['sleep_end']).split()[-2:])}
            if leg['last_in_duty']:
                kw["tooltip"] = "Sleep opportunity between duties\n" + kw["tooltip"]
                gc.rectangle(*args, **kw)

                if leg['time_zone_diff'] != "0:00":
                    tzstring = str(leg['time_zone_diff'])
                    if tzstring[0] != "-":
                        tzstring = "+" + tzstring
                    gc.text(leg['end'] + RelTime("0:30"),
                            self.leg_top,
                            "tz: " + tzstring,
                            align=prt.LEFT, font=prt.font(size=6))
            else:
                kw["tooltip"] = "Sleep opportunity in split duty\n" + kw["tooltip"]
                kw["fill"] = studio_palette.LightGrey
                kw["colour"] = studio_palette.Black
                gc.rectangle(*args, **kw)

            if leg['last_in_duty'] and leg['is_flight_duty']:
                gc.text(leg['end'] - RelTime("0:30"),
                        self.leg_top - 25,
                        str(leg['end'])[-5:],
                        align=prt.LEFT, font=prt.font(size=6))

                gc.text(leg['end'] + RelTime("0:30"),
                        self.leg_top - 15,
                        leg['end_station'],
                        align=prt.LEFT, font=prt.font(size=6))
            if leg['first_in_duty'] and leg['is_flight_duty']:
                gc.text(leg['start'] + RelTime("0:30"),
                        self.leg_top - 25,
                        str(leg['start'])[-5:],
                        align=prt.RIGHT, font=prt.font(size=6))
                gc.text(leg['start'] - RelTime("0:30"),
                        self.leg_top - 15,
                        leg['start_station'],
                        align=prt.RIGHT, font=prt.font(size=6))


class FatigueChart(Gantt):
    """
    object used to draw the crew gantt.
    """
    def __init__(self, start_day, end_day, width, step, roster_bag, **kw):

        self.night_period = []
        self.fatigue_list = []
        self.min = 0
        self.max = 10000

        night_begin = None
        prev_date_time = None
        valid_range = False
        cur_fatigue_list = []
        limit = end_day + step

        # Get crew homebase for start-day
        base_airport = Airport(roster_bag.report_fatigue.base_airport(start_day))

        earliest = roster_bag.report_fatigue.chain_start_utc()
        latest = roster_bag.report_fatigue.chain_end_utc()

        wanted_start = base_airport.getUTCTime(start_day)
        wanted_end = base_airport.getUTCTime(limit)

        # ival_start and ival_end are in UTC
        ival_start = max(wanted_start, earliest)
        ival_end = min(wanted_end, latest)
        if not ival_start or not ival_end or ival_start > ival_end:
            # We couldn't get a valid time-period for the chain, not a valid CAPI chain
            # Either outside of prediction period or only activity_type "" / "OF" legs
            # Skip prediction
            alertnessvalues = []
        else:
            alertnessvalues = roster_bag.capi_test(ival_start, ival_end, step)

        # current_date_time is in homebase time
        current_date_time = start_day + (ival_start - wanted_start)

        for value in alertnessvalues:
            if value > 0 or value < 10000:
                valid_range = True
            if not night_begin and value < 0:
                night_begin = current_date_time

            if night_begin and value > 0:
                # Crew wake-up, Add night period to list
                self.night_period.append((night_begin, prev_date_time))
                night_begin = None

            value = abs(value)

            if valid_range:
                cur_fatigue_list.append((current_date_time, value,
                                         roster_bag.report_fatigue.flying(current_date_time)
                                         ))
            prev_date_time = current_date_time
            current_date_time = current_date_time + step

        if cur_fatigue_list:
            self.fatigue_list.append(cur_fatigue_list)

        Gantt.__init__(self, start_day, end_day, width, 200, **kw)

    def draw(self, gc):

        gc.coordinates(self.start_day, self.min, self.end_day, self.max)

        # Draw more fine grained 250 CAS points steps
        step = 250
        begin = self.min
        while begin < self.max:
            if begin not in [0, 2500, 5000, 7500, 10000]:
                gc.path([(self.start_day, begin), (self.end_day, begin)],
                        colour=studio_palette.LightGrey)
            begin = begin + step

        # Draw sleep periods
        for (start, end) in self.night_period:
            args = (start, self.max,
                    end - start, self.max)
            kw = {"tooltip": "Predicted sleep\n%s - %s" % ("%02d:%02d" % (start).split()[-2:],
                                                           "%02d:%02d" % (end).split()[-2:]),
                  "fill": studio_palette.LightGrey}
            gc.rectangle(*args, **kw)

        # Draw alertness prediction
        # The code traverses the predictions and draws a path every time the report_fatigue.%flying%(t)
        # switches or once the end of the list is reached
        prune_carry_in = True
        for _l in self.fatigue_list:
            cl = []
            cci = _l[0][2]
            for x, y, ci in _l:
                if prune_carry_in and y < 1:
                    # We skip points of illegal alertness value in the beginning of the prediction
                    continue
                if prune_carry_in and y > 0:
                    prune_carry_in = False
                cl.append((x, y))
                if cci != ci or x == _l[-1][0]:
                    gc.path(cl, width=2 if cci else 1,
                            colour=studio_palette.DarkRed if cci else studio_palette.Black)
                    cci = ci
                    cl = [(x, y)]

        # Draw thicker lines
        step = 2500

        begin = self.min
        while begin < self.max:
            gc.text(self.start_day + RelTime("1:00"),
                    begin,
                    begin,
                    align=prt.LEFT)
            gc.path([(self.start_day, begin), (self.end_day, begin)])
            begin = begin + step

        #
        # calls the parent draw method where the calendar bars are drawn
        #
        Gantt.draw(self, gc)


class AlertnessPlotReport(StandardReport):

    def get_set(self):
        # Override in report_sources/x/y.py
        raise NotImplementedError()

    def get_header_text(self):
        """
        Should return the text you want to be in the
        header of the report (e.g. Check Legality)
        """
        return MSGR('Alertness Plot Report')

    def create(self):

        self.setpaper(orientation=prt.LANDSCAPE)
        self.report_width = self.page_width()
        self.warning = ""
        super(AlertnessPlotReport, self).standard_header()
        super(AlertnessPlotReport, self).standard_footer()

        for chain_bag in self.get_set():
            self.add('')
            self.add('')
            self.add(prt.Text(chain_bag.report_fatigue.chain_id()))

            self.first_day, self.end_day = self.get_plot_interval(chain_bag)

            self.add_column_header()

            self.add_roster_gantt(chain_bag)

            self.add_fatigue_chart(chain_bag)

            self.page()

    def get_plot_interval(self, chain_bag):
        start = chain_bag.report_fatigue.selected_interval_start()
        end = chain_bag.report_fatigue.selected_interval_end()

        return (start, end)

    def add_column_header(self):
        """
        add the column header with one cell per day,
        including weekday and day of the month
        """
        self.add(GanttHeader(self.first_day,
                             self.end_day,
                             self.report_width,
                             25,
                             border=prt.border_frame(2)))

    def add_roster_gantt(self, tripbag):
        """
        add the gant view representing a trip
        """
        roster_gantt = FatigueRosterGantt(self.first_day,
                                          self.end_day,
                                          self.report_width,
                                          tripbag)

        self.add(prt.Row(roster_gantt,
                         border=prt.border_frame(2)))

    def add_fatigue_chart(self, tripbag):
        """
        add the fatigue curve for each trip in the report
        """
        fatigue_chart = FatigueChart(self.first_day,
                                     self.end_day,
                                     self.report_width,
                                     RelTime("00:05"),
                                     tripbag)

        self.add(prt.Row(fatigue_chart,
                         border=prt.border_frame(2)))
        s = MSGR("Worst flight") + " " + \
            str(tripbag.report_fatigue.min_alertness(self.first_day, self.end_day)) + \
            ", " + \
            MSGR(str(tripbag.report_fatigue.min_alertness_text())) + \
            " " + \
            str(tripbag.report_fatigue.min_alertness_time(self.first_day, self.end_day)) + \
            " (" +\
            MSGR(str(tripbag.report_fatigue.min_alertness_mode())) + \
            ") "
        self.add(prt.Row(s))


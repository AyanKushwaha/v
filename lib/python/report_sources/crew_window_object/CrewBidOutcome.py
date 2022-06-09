# -*- coding: iso-8859-15 -*-
"""
Crew Bid Outcome report
"""
from itertools import izip
import collections
import os

import Cui
from carmensystems.mave import etab
import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave

from report_sources.include.SASReport import SASReport
from report_sources.include.studiopalette import studio_palette as sp
from carmstd import bag_handler
from report_sources.include.TOBidsWeeklyStatistics import create_timeoff_bids_weekly_statistics
from report_sources.include.ReportUtils import DataCollection
from RelTime import RelTime

cellWidths = (100, 100, 100, 100)
aligns = (prt.LEFT, prt.LEFT, prt.LEFT, prt.LEFT)


# A Lifestyle is defined with
#   name: Report name for the Lifestyle
#   combination: True/False if Single or Combination Lifestyle
#   combination_trip: A Lifestyle making up the trip part of the combination
#   combination_shift: A Lifestyle making up the shift part of the combination
LIFESTYLE_DEFINITIONS = {
    "early_ends_pref": {
        "name": "Morning Person",
        "combination": False,
        "combination_trip": None,
        "combination_shift": None},

    "late_starts_pref": {
        "name": "Evening Person",
        "combination": False,
        "combination_trip": None,
        "combination_shift": None},

    "nights_at_home_pref": {
        "name": "Nights at Home",
        "combination": False,
        "combination_trip": None,
        "combination_shift": None},

    "nights_at_home_early_ends_pref": {
        "name": "Nights at Home + Morning Person",
        "combination": True,
        "combination_trip": "nights_at_home_pref",
        "combination_shift": "early_ends_pref"},

    "nights_at_home_late_starts_pref": {
        "name": "Nights at Home + Evening Person",
        "combination": True,
        "combination_trip": "nights_at_home_pref",
        "combination_shift": "late_starts_pref"},

    "comm23_days_pref": {
        "name": "Nights Away from Home 2-3 days",
        "combination": False,
        "combination_trip": None,
        "combination_shift": None},

    "comm23_days_early_ends_pref": {
        "name": "Nights Away from Home 2-3 days + Morning Person",
        "combination": True,
        "combination_trip": "comm23_days_pref",
        "combination_shift": "early_ends_pref"},

    "comm23_days_late_starts_pref": {
        "name": "Nights Away from Home 2-3 days + Evening Person",
        "combination": True,
        "combination_trip": "comm23_days_pref",
        "combination_shift": "late_starts_pref"},

    "comm35_days_pref": {
        "name": "Nights Away from Home 3-5 days",
        "combination": False,
        "combination_trip": None,
        "combination_shift": None},

    "comm35_days_early_ends_pref": {
        "name": "Nights Away from Home 3-5 days + Morning Person",
        "combination": True,
        "combination_trip": "comm35_days_pref",
        "combination_shift": "early_ends_pref"},

    "comm35_days_late_starts_pref": {
        "name": "Nights Away from Home 3-5 days + Evening Person",
        "combination": True,
        "combination_trip": "comm35_days_pref",
        "combination_shift": "late_starts_pref"},

    "west_destinations_pref": {
        "name": "Longhaul West/USA",
        "combination": False,
        "combination_trip": None,
        "combination_shift": None},

    "east_destinations_pref": {
        "name": "Longhaul East/Asia",
        "combination": False,
        "combination_trip": None,
        "combination_shift": None},

    "any_longhaul_destinations_pref": {
        "name": "Longhaul Any",
        "combination": False,
        "combination_trip": None,
        "combination_shift": None},
}


LifestyleData = collections.namedtuple(
    "LifestyleData",
    ("chosen_lifestyle", "name", "fulfillment",
     "num_fulfilled", "num_available",
     "combination", "combination_trip_name",
     "combination_trip_fulfillment", "combination_trip_num_fulfilled",
     "combination_shift_name", "combination_shift_fulfillment",
     "combination_shift_num_fulfilled"))

DATED_BID_DATA_ELEMENTS = ("weight", "type", "times_granted")
DatedBidData = collections.namedtuple(
    "DatedBidData",
    DATED_BID_DATA_ELEMENTS)


StopBidData = collections.namedtuple(
    "StopBidData",
    DATED_BID_DATA_ELEMENTS + ("station", "min_duration", "max_duration", "start_date", "end_date"))

TimeOffBidData = collections.namedtuple(
    "TimeOffBidData",
    DATED_BID_DATA_ELEMENTS + ("start_date", "end_date"))

FlightIdBidData = collections.namedtuple(
    "FlightIdBidData",
    DATED_BID_DATA_ELEMENTS + ("flight_id", "date"))

CheckInBidData = collections.namedtuple(
    "CheckInBidData",
    DATED_BID_DATA_ELEMENTS + ("after_time", "total_bids"))

CheckOutBidData = collections.namedtuple(
    "CheckOutBidData",
    DATED_BID_DATA_ELEMENTS + ("before_time", "total_bids"))

LifestyleKpis = collections.namedtuple(
    "LifestyleKpis",
    ("name", "number_bidders_kpi", "fulfillment_kpi"))


LifestyleStats = collections.namedtuple(
    "LifestyleStats",
    ("name", "number_bidders", "fulfillment"))

StopBidStats = collections.namedtuple(
    "StopBidStats",
    ("distributions",))

FlightIdStats = collections.namedtuple(
    "FlightIdStats",
    ("distributions",))


NON_LH_LIFESTYLE_STAT_KPIS = (
    LifestyleKpis(
        "Morning Person",
        "kpi.%distribution_morning_person%",
        "kpi.%avg_fulfillment_morning_person%"),
    LifestyleKpis(
        "Evening Person",
        "kpi.%distribution_evening_person%",
        "kpi.%avg_fulfillment_evening_person%"),
    LifestyleKpis(
        "Nights at Home",
        "kpi.%distribution_nights_home%",
        "kpi.%avg_fulfillment_nights_home%"),
    LifestyleKpis(
        "Nights at Home + Morning Person",
        "kpi.%distribution_nights_at_home_early_ends%",
        "kpi.%avg_fulfillment_nights_at_home_early_ends%"),
    LifestyleKpis(
        "Nights at Home + Evening Person",
        "kpi.%distribution_nights_at_home_late_starts%",
        "kpi.%avg_fulfillment_nights_at_home_late_starts%"),
    LifestyleKpis(
        "Nights Away from Home 2-3 days",
        "kpi.%distribution_commuter_2_3_days%",
        "kpi.%avg_fulfillment_commuter_2_3_days%"),
    LifestyleKpis(
        "Nights Away from Home 2-3 days + Morning Person",
        "kpi.%distribution_commuter_2_3_days_early_ends%",
        "kpi.%avg_fulfillment_commuter_2_3_days_early_ends%"),
    LifestyleKpis(
        "Nights Away from Home 2-3 days + Evening Person",
        "kpi.%distribution_commuter_2_3_days_late_starts%",
        "kpi.%avg_fulfillment_commuter_2_3_days_late_starts%"),
    LifestyleKpis(
        "Nights Away from Home 3-5 days",
        "kpi.%distribution_commuter_3_5_days%",
        "kpi.%avg_fulfillment_commuter_3_5_days%"),
    LifestyleKpis(
        "Nights Away from Home 3-5 days + Morning Person",
        "kpi.%distribution_commuter_3_5_days_early_ends%",
        "kpi.%avg_fulfillment_commuter_3_5_days_early_ends%"),
    LifestyleKpis(
        "Nights Away from Home 3-5 days + Evening Person",
        "kpi.%distribution_commuter_3_5_days_late_starts%",
        "kpi.%avg_fulfillment_commuter_3_5_days_late_starts%"))

LH_LIFESTYLE_STAT_KPIS = (
    LifestyleKpis(
        "Longhaul West/USA",
        "kpi.%distribution_west_destinations%",
        "kpi.%avg_fulfillment_west_destinations%"),
    LifestyleKpis(
        "Longhaul East/Asia",
        "kpi.%distribution_east_destinations%",
        "kpi.%avg_fulfillment_east_destinations%"))

LH_CC_LIFESTYLE_STAT_KPIS = LH_LIFESTYLE_STAT_KPIS + (
    LifestyleKpis(
        "Longhaul Any",
        "kpi.%distribution_any_longhaul_destinations%",
        "kpi.%avg_fulfillment_any_longhaul_destinations%"),)

CrewData = collections.namedtuple(
    "CrewData",
    ("lifestyles", "dated_bids"))


class Report(SASReport):

    GRANTED_COLOUR = sp.DarkGreen
    DECLINED_COLOUR = sp.BrightRed

    def create(self):
        self.modify_pp()
        SASReport.create(self, "Crew Bid Outcome Report", usePlanningPeriod=True)

        # When called by the GenerateCrewBidOutcomePDFs script the script value is
        # set to either 'Crew' or 'Summary'
        self.include_crew = True
        self.include_summary = True
        script_value = self.arg('script')
        if script_value == 'Crew':
            self.include_summary = False
            bag_wrapper = bag_handler.CurrentChain()
        elif script_value == 'Summary':
            self.include_crew = False
            bag_wrapper = bag_handler.WindowChains()
        else:
            bag_wrapper = bag_handler.MarkedRostersLeft()
        self.bag = bag_wrapper.bag

        if self.include_crew:
            per_crew_data = self.per_crew_data(self.bag)
        else:
            per_crew_data = []

        plan_data = self.plan_data()

        if self.include_summary:
            joint_crew_data = self.joint_crew_data(plan_data)
            stop_bid_distributions = joint_crew_data.dated_bids[1].distributions
            trip_data = self.trip_data(stop_bid_distributions)
        else:
            joint_crew_data = []
            trip_data = []

        scheduler_note = self.scheduler_note()

        self._create(plan_data.pp_start, per_crew_data,
                     joint_crew_data, trip_data, scheduler_note)
        self.reset_pp()

    def _create(self, pp_start, per_crew_data, joint_crew_data,
                trip_stats, scheduler_note):

        if self.include_crew:
            for crew_string, lifestyle_data, dated_bid_data in per_crew_data:
                self.add(self.create_title_text(crew_string))

                self.add(self.create_section_header("My Lifestyle Fulfillment"))
                if lifestyle_data.chosen_lifestyle:
                    self.add(self.lifestyle_fulfillment(lifestyle_data))
                else:
                    self.add(prt.Text("You did not place a lifestyle bid for this period."))
                self.add("")

                self.add(self.create_section_header("My Bid Fulfillment"))
                if dated_bid_data:
                    self.add(self.dated_bid_fulfillment(dated_bid_data))
                else:
                    self.add(prt.Text("You had no dated bids in this period."))
                self.add("")
                self.page()

        if self.include_summary:
            pp_start_text = str(pp_start)
            pp_text = "%s %s" % (pp_start_text[2:5], pp_start_text[5:9])
            self.add(self.create_section_header("Group Lifestyle Statistics (%s)" % pp_text))
            self.add(self.lifestyle_statistics(joint_crew_data.lifestyles))
            self.add("")
            self.page()
            self.add(self.create_section_header("Group Bid Statistics"))
            self.add(self.dated_bid_statistics(
                joint_crew_data.dated_bids, trip_stats))
            self.page()

        if scheduler_note:
            self.add("")
            self.add(self.create_section_header("Scheduler note"))
            self.add(prt.Row(prt.Text(scheduler_note)))

    def get_timeoff_bids_data(self, dates):

        dt = self.data["TimeOff"]
        headers = ["Placed Bids", "Fulfilled Bids", "Ratio (%)"]

        window_chains_bh = bag_handler.WindowChains()
        window_chains_bag = window_chains_bh.bag

        for date in dates:
            t_bids, = rave.eval(window_chains_bag, "report_ls_bid_stats.%total_timeoff_bids_on_day%(" + str(date) + ")")
            g_bids, = rave.eval(window_chains_bag, "report_ls_bid_stats.%total_granted_timeoff_bids_on_day%(" + str(date) + ")")
            p_bids, = rave.eval(window_chains_bag, "report_ls_bid_stats.%percent_granted_timeoff_bids_on_day%(" + str(date) + ")")

            dt.add(headers[0], date, t_bids)
            dt.add(headers[1], date, g_bids)
            dt.add(headers[2], date, p_bids)

    @staticmethod
    def per_crew_data(rosters_bag):
        per_crew_data = []
        for roster_bag in rosters_bag.iterators.roster_set():
            (crew_string, lifestyle, lifestyle_fulfillment,
             lifestyle_num_fulfilled, lifestyle_num_available) = rave.eval(
                roster_bag, "report_common.%crew_string%",
                "lifestyle.%chosen_lifestyle%", "lifestyle.%fulfillment%",
                "lifestyle.%num_days_satisfying_fulfillment%",
                "lifestyle.%num_days_available_for_fulfillment%")

            # Unpack values from LIFESTYLE_DEFINITIONS
            name = LIFESTYLE_DEFINITIONS.get(lifestyle, {}).get("name", lifestyle)
            combination = LIFESTYLE_DEFINITIONS.get(lifestyle, {}).get("combination", False)
            combination_trip = LIFESTYLE_DEFINITIONS.get(lifestyle, {}).get("combination_trip", None)
            combination_shift = LIFESTYLE_DEFINITIONS.get(lifestyle, {}).get("combination_shift", None)

            # Only generate if we have all the data configured
            if combination and combination_trip and combination_shift:
                (trip_lifestyle_fulfillment, trip_lifestyle_num_fulfilled) = rave.eval(
                    roster_bag,
                    'lifestyle.%fulfillment_func%("{0}")'.format(combination_trip),
                    'lifestyle.%num_days_satisfying_fulfillment_func%("{0}")'.format(combination_trip))
                (shift_lifestyle_fulfillment, shift_lifestyle_num_fulfilled) = rave.eval(
                    roster_bag,
                    'lifestyle.%fulfillment_func%("{0}")'.format(combination_shift),
                    'lifestyle.%num_days_satisfying_fulfillment_func%("{0}")'.format(combination_shift))
            else:
                trip_lifestyle_fulfillment = 0
                trip_lifestyle_num_fulfilled = 0
                shift_lifestyle_fulfillment = 0
                shift_lifestyle_num_fulfilled = 0
            trip_lifestyle_name = LIFESTYLE_DEFINITIONS.get(combination_trip, {}).get("name", combination_trip)
            shift_lifestyle_name = LIFESTYLE_DEFINITIONS.get(combination_shift, {}).get("name", combination_shift)

            lifestyle_data = LifestyleData(
                lifestyle, name, lifestyle_fulfillment,
                lifestyle_num_fulfilled, lifestyle_num_available,
                combination, trip_lifestyle_name,
                trip_lifestyle_fulfillment, trip_lifestyle_num_fulfilled,
                shift_lifestyle_name, shift_lifestyle_fulfillment,
                shift_lifestyle_num_fulfilled)

            dated_bid_data = {}
            for ix in xrange(1, roster_bag.bid.crew_num_bids() + 1):
                if not roster_bag.bid.is_dated_bid(ix):
                    continue

                weight = roster_bag.bid.points_text(ix)
                times_granted = roster_bag.bid.get_roster_granted_value(ix)
                bid_type = roster_bag.bid.type_of_bid(ix)

                if roster_bag.bid.is_stop_bid(ix):
                    station = roster_bag.bid.bid_str1(ix)
                    min_duration, _ = roster_bag.bid.rel1(ix,0).split()
                    max_duration, _ = roster_bag.bid.rel2(ix,0).split()
                    start_date = roster_bag.bid.abs1(ix, 0).ddmonyyyy()[:9]
                    end_date = roster_bag.bid.abs2(ix, 0).ddmonyyyy()[:9]
                    bid = StopBidData(weight, bid_type, times_granted, station, min_duration, max_duration, start_date, end_date)
                    dated_bid_data.setdefault("stop_bid", []).append(bid)

                elif roster_bag.bid.is_timeoff_bid(ix):
                    start_date = roster_bag.bid._abs1(ix, 0).ddmonyyyy()[:9]
                    end_date = roster_bag.bid._abs2(ix, 0).ddmonyyyy()[:9]
                    bid = TimeOffBidData(weight, bid_type, times_granted, start_date, end_date)
                    dated_bid_data.setdefault("time_off_bid", []).append(bid)

                elif roster_bag.bid.is_flightid_bid(ix):
                    flight_id = roster_bag.bid.bid_str1(ix, 0)
                    date = roster_bag.bid.abs1(ix, 0).ddmonyyyy()[:9]
                    bid = FlightIdBidData(weight, bid_type, times_granted, flight_id, date)
                    dated_bid_data.setdefault("flight_id_bid", []).append(bid)

                elif roster_bag.bid.is_checkin_bid(ix):
                    after_time = roster_bag.bid.rel1(ix,0)                    
                    (total_checkin_bids, )= rave.eval(roster_bag, "report_ls_bid_stats.%total_checkin_bids%(" + str(ix) + ")") 
                    bid = CheckInBidData(weight, bid_type, times_granted, after_time, total_checkin_bids)
                    dated_bid_data.setdefault("checkIn_bid", []).append(bid)

                elif roster_bag.bid.is_checkout_bid(ix):
                    before_time = roster_bag.bid.rel2(ix,0)
                    (total_checkout_bids, ) = rave.eval(roster_bag, "report_ls_bid_stats.%total_checkout_bids%(" + str(ix) + ")")  
                    bid = CheckOutBidData(weight, bid_type, times_granted, before_time, total_checkout_bids)
                    dated_bid_data.setdefault("checkIn_bid", []).append(bid)
                
                else:
                    bid = DatedBidData(weight, bid_type, times_granted)
                dated_bid_data.setdefault(weight, []).append(bid)

            per_crew_data.append((crew_string, lifestyle_data,
                                  dated_bid_data))
        return per_crew_data

    @staticmethod
    def plan_data():
        PlanData = collections.namedtuple(
            "PlanData",
            ("pp_start", "pp_end",
             "plan_is_fd_lh", "plan_is_cc"))
        vals = rave.eval(
            "fundamental.%pp_start%", "fundamental.%pp_end%",
            "report_ls_bid_stats.%plan_is_fd_lh%",
            "report_ls_bid_stats.%plan_is_cc%")
        return PlanData(*vals)

    def joint_crew_data(self, plan_data):
        window_chains_bh = bag_handler.WindowChains()
        window_chains_bag = window_chains_bh.bag
        lifestyle_stats = []

        if plan_data.plan_is_cc:
            ls_kpis = NON_LH_LIFESTYLE_STAT_KPIS + LH_CC_LIFESTYLE_STAT_KPIS
        elif plan_data.plan_is_fd_lh:
            ls_kpis = LH_LIFESTYLE_STAT_KPIS
        else:
            ls_kpis = NON_LH_LIFESTYLE_STAT_KPIS

        for name, num_bidders_kpi, avg_fulfillment_kpi in ls_kpis:
            number_bidders, avg_fulfillment = rave.eval(
                window_chains_bag,
                num_bidders_kpi, avg_fulfillment_kpi)
            lifestyle_stats.append(
                LifestyleStats(name, number_bidders, avg_fulfillment))

        num_granted_timeoff_bids, num_timeoff_bids = rave.eval(
            window_chains_bag,
            "report_ls_bid_stats.%total_granted_timeoff_bids%",
            "report_ls_bid_stats.%total_timeoff_bids%")
        try:
            avg_granted_timeoff_bids = int(round(
                100. * num_granted_timeoff_bids / num_timeoff_bids))
        except ZeroDivisionError:
            avg_granted_timeoff_bids = 0

        window_crew_ids = set()
        for roster_bag in window_chains_bag.iterators.roster_set():
            window_crew_ids.add(roster_bag.crew.id())

        sbid_distributions, flt_distributions = self.get_bidtable_stats(
            plan_data, window_crew_ids)

        sbid_stats = StopBidStats(sbid_distributions)
        flt_stats = FlightIdStats(flt_distributions)
        return CrewData(lifestyle_stats,
                        (avg_granted_timeoff_bids, sbid_stats, flt_stats))

    def trip_data(self, stop_bid_distributions):
        num_stops = collections.defaultdict(int)
        uniq_trips = set()
        where_filter = "trip.%in_pp% and not trip.%is_locked% and trip.%has_only_flight_duty%"

        rosters_bw = bag_handler.WindowChains(area=Cui.CuiArea0)
        for roster_bag in rosters_bw.bag.iterators.roster_set():
            for trip_bag in roster_bag.iterators.trip_set(where=where_filter):
                trip_key = trip_bag.report_ls_bid_stats.trip_descriptor()
                if trip_key not in uniq_trips:
                    uniq_trips.add(trip_key)
                    for destination in stop_bid_distributions:
                        if trip_bag.report_ls_bid_stats.trip_grants_stop_bid(destination):
                            num_stops[destination] += 1

        trips_bw = bag_handler.WindowChains(area=Cui.CuiArea1)
        if trips_bw.bag:
            for trip_bag in trips_bw.bag.iterators.trip_set(where=where_filter):
                trip_key = trip_bag.report_ls_bid_stats.trip_descriptor()
                if trip_key not in uniq_trips:
                    uniq_trips.add(trip_key)
                    for destination in stop_bid_distributions:
                        if trip_bag.report_ls_bid_stats.trip_grants_stop_bid(destination):
                            num_stops[destination] += 1

        return num_stops

    def get_bidtable_stats(self, plan_data, crew_ids):
        station_stats = collections.defaultdict(int)
        flightid_stats = collections.defaultdict(int)

        session = etab.Session()
        bid_table_path = rave.eval("bid.%table%")[0]
        full_path = os.path.expandvars(os.path.join("$CARMDATA/ETABLES", bid_table_path))
        bid_table = etab.load(session, full_path)
        for bidrow in bid_table:
            if bidrow.empno not in crew_ids:
                continue
            bid_in_pp = rave.eval(
                "time_utils.%%times_overlap%%(%s, %s, %s, %s)" %
                (plan_data.pp_start, plan_data.pp_end,
                 bidrow.abs1, bidrow.abs2))[0]
            if not bid_in_pp:
                continue

            if bidrow.bidtype == 'Stop':
                station_stats[bidrow.str1] += 1
            elif bidrow.bidtype == 'Flight':
                bid_key = (bidrow.str1, str(bidrow.abs1))
                flightid_stats[bid_key] += 1
        return station_stats, flightid_stats

    def lifestyle_fulfillment(self, lifestyle_data):
        ls_elem = prt.Column()
        ls_elem.add(prt.Row(prt.Text(
            "Chosen lifestyle: %s" % lifestyle_data.name,
            font=prt.Font(weight=prt.BOLD))))
        print lifestyle_data
        if lifestyle_data.combination:
            ls_elem_string1 = "Your combined lifestyle matches {0} work days out of {1} total work days ({2}%)"
            ls_elem.add(ls_elem_string1.format(lifestyle_data.num_fulfilled,
                                               lifestyle_data.num_available,
                                               lifestyle_data.fulfillment))
            ls_elem_string2 = 'Your preferred trip length "{0}" matches {1} out of {2} total work days ({3}%)'
            ls_elem.add(ls_elem_string2.format(lifestyle_data.combination_trip_name,
                                               lifestyle_data.combination_trip_num_fulfilled,
                                               lifestyle_data.num_available,
                                               lifestyle_data.combination_trip_fulfillment))
            ls_elem_string3 = 'Your preferred shift pattern "{0}" matches {1} out of {2} total work days ({3}%)'
            ls_elem.add(ls_elem_string3.format(lifestyle_data.combination_shift_name,
                                               lifestyle_data.combination_shift_num_fulfilled,
                                               lifestyle_data.num_available,
                                               lifestyle_data.combination_shift_fulfillment))
        else:
            ls_elem_string = "Your lifestyle matches {0} work days out of {1} total work days ({2}%)"
            ls_elem.add(ls_elem_string.format(lifestyle_data.num_fulfilled,
                                              lifestyle_data.num_available,
                                              lifestyle_data.fulfillment))
        return ls_elem

    def lifestyle_statistics(self, lifestyle_statistics):
        header = self.create_table_header(
            "Lifestyle",
            "Number of crew in group",
            "Avg lifestyle fulfillment")
        table = prt.Column()
        table.add(header)
        for name, number_bidders, avg_fulfillment in lifestyle_statistics:
            table.add(prt.Row(
                name,
                number_bidders,
                "%s%%" % avg_fulfillment))
        return table

    def dated_bid_fulfillment(self, dated_bid_data):
        db_elem = prt.Column()
        header = self.create_table_header("Priority", "Type", "Additional Information", "Status")
        db_elem.add(header)

        labels = {"high": "HIGH",
                  "medium": "MEDIUM",
                  "low": "LOW"}
        for internal_label, external_label in labels.iteritems():
            priority_bids = dated_bid_data.get(internal_label)
            if priority_bids:
                for bid_data in priority_bids:

                    ad_info = ""
                    # Use overflow variable if displayed text takes too much space in report
                    # Populate overflow_row using prt.Row with text to be displayed in new row
                    overflow = False
                    overflow_row = None
                    status_txt = ""
                    comment = ""
                    if bid_data.type == "Stop":
                        duration = ("(%sh - %sh)" %(bid_data.min_duration, bid_data.max_duration) 
                                    if (bid_data.min_duration <> bid_data.max_duration) else "")
                        end_date = "UFN" if bid_data.end_date == "01JAN2036" else bid_data.end_date
                        stop_suffix = "" if bid_data.times_granted == 1 else "s"
                        ad_info = "%s %s: %s stop%s" % (bid_data.station, duration, bid_data.times_granted, stop_suffix)
                        overflow = True
                        ad_info_overflow = "%s - %s" % (bid_data.start_date, end_date)
                        overflow_row = prt.Row("",
                                            "",
                                            ad_info_overflow,
                                            "")

                    elif bid_data.type == "TimeOff":
                        ad_info = "%s - %s" % (bid_data.start_date, bid_data.end_date)

                    elif bid_data.type == "Flight":
                        ad_info = "%s %s" % (bid_data.flight_id, bid_data.date)

                    elif bid_data.type == "CheckIn":
                        ad_info = "%s %s" % ("After ", bid_data.after_time)
                        comment = " after day off"
                        status_txt = self.check_in_out_bid_status_text(bid_data.times_granted, bid_data.total_bids )

                    elif bid_data.type == "CheckOut":
                        ad_info = "%s %s" % ("Before ", bid_data.before_time)
                        comment = " before day off"
                        status_txt = self.check_in_out_bid_status_text(bid_data.times_granted, bid_data.total_bids)
                                            
                    if(not status_txt): 
                        status_txt = self.dated_bid_status_text(bid_data.times_granted)

                    db_elem.add(prt.Row(external_label,
                                        bid_data.type + comment,
                                        ad_info,
                                        status_txt))
                    # Add extra row if needed
                    if overflow:
                        db_elem.add(overflow_row)
        return db_elem


    def dated_bid_status_text(self, times_granted):
        if times_granted:
            return prt.Text("Granted", colour=self.GRANTED_COLOUR)
        else:
            return prt.Text("Not granted", colour=self.DECLINED_COLOUR)

    def check_in_out_bid_status_text(self, times_granted, total_bids):
        if times_granted:
            return prt.Text("Granted (" + str(times_granted) + " out of " + str(total_bids) + ")", colour=self.GRANTED_COLOUR)
        else:
            return prt.Text("Not granted", colour=self.DECLINED_COLOUR)


    def dated_bid_statistics(self, dated_bid_data, trip_stats):
        dbs = prt. Column()
        subsection_font = prt.Font(weight=prt.BOLD)

        dbs.add(prt.Text("Time Off", font=subsection_font, border=None))

        dates = []
        pp_start, pp_end = rave.eval('fundamental.%pp_start%', 'fundamental.%pp_end%')
        date = pp_start
        while date < pp_end:
            dates.append(date)
            date += RelTime(24, 0)

        self.data = dict()
        self.data['TimeOff'] = DataCollection('TimeOff', dates=dates, sumCategory="_")
        self.get_timeoff_bids_data(dates)

        time_off_row = prt.Row(create_timeoff_bids_weekly_statistics(self.data['TimeOff'], self.HEADERBGCOLOUR))
        dbs.add(prt.Isolate(time_off_row))

        timeoff_fulfillment, stop_bid_stats, flight_id_stats = dated_bid_data
        dbs.add("")

        dbs.add(prt.Text(
            "Top five most bidded destinations",
            font=subsection_font,
            border=None))
        dbs.add(self.create_table_header("Destination bid",
                                         "Total number of available stops",
                                         "Nr of submitted bids"))
        for _, biditem in izip(range(5), sorted(stop_bid_stats.distributions.iteritems(),
                                                key=lambda (k, v): v, reverse=True)):
            st, bidnum = biditem
            dbs.add(prt.Row(
                st,
                trip_stats[st],
                bidnum))

        dbs.add("")
        dbs.add(prt.Text(
            "Top three most bidded flights on a specific date",
            font=subsection_font, border=None))
        dbs.add(self.create_table_header("Flight ID", "Date", "Nr of submitted bids"))
        for _, biditem in izip(range(3), sorted(flight_id_stats.distributions.iteritems(),
                                                key=lambda (k, v): v, reverse=True)):
            (flight_id, flight_date), bidnum = biditem
            flight_date = flight_date[:10]
            dbs.add(prt.Row(
                flight_id,
                flight_date,
                bidnum))

        return dbs

    def scheduler_note(self):
        return rave.eval("lifestyle.%scheduler_note_p%")[0]

    def create_table_header(self, *headerItems):
        inputRow = prt.Row(font=prt.Font(weight=prt.BOLD), border=None,
                           background=self.HEADERBGCOLOUR)
        pad = prt.padding(2, 2, 2, 2)
        items = zip(headerItems, cellWidths, aligns)
        for (item, itemwidth, itemalign) in items:
            inputRow.add(prt.Text(item, width=itemwidth,
                                  align=itemalign, padding=pad))
        return inputRow

    def create_section_header(self, header_text):
        return prt.Text(header_text, font=prt.font(size=11, weight=prt.BOLD),
                        padding=prt.padding(top=5, bottom=5, right=5))

    def create_title_text(self, title_text):
        return prt.Text(
            str(title_text), font=prt.font(size=14, weight=prt.BOLD))

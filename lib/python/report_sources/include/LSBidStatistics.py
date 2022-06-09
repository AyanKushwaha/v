"""
 $Header$

 Lifestyle & Bid Statistics

"""
import collections

from report_sources.include.SASReport import SASReport
import carmensystems.publisher.api as prt
import carmensystems.rave.api as R
from report_sources.include.ReportUtils import DataCollection
from RelTime import RelTime
from report_sources.include.TOBidsWeeklyStatistics import create_timeoff_bids_weekly_statistics

CONTEXT = 'default_context'
TITLE = 'Lifestyle / Bid Statistics'
cellWidths = (100, 215, 100, 100)
aligns = (prt.LEFT, prt.LEFT, prt.LEFT, prt.LEFT, prt.LEFT)


class LSBidStatistics(SASReport):

    def create_table_header(self, headerItems, cell_widths=None):
        inputRow = prt.Row(font=prt.Font(weight=prt.BOLD), border=None,
                           background=self.HEADERBGCOLOUR)
        pad = prt.padding(2, 2, 2)
        if cell_widths is None:
            cell_widths = cellWidths
        items = zip(headerItems, cell_widths, aligns)
        for (item, itemwidth, itemalign) in items:
            inputRow.add(prt.Text(item, width=itemwidth,
                                  align=itemalign, padding=pad))
        return inputRow

    def create_section_header(self, header_text):
        return prt.Text(header_text, font=prt.font(size=10, weight=prt.BOLD),
                        padding=prt.padding(top=5, bottom=5, right=5),
                        width=200)

    def create(self, reportType):
        self.modify_pp()

        # Get the mode, dated or standard, and the output format
        self.dated, = R.eval(CONTEXT, 'crg_pairing_statistics.%is_dated_mode%')
        self.weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        self.datesAndWeekdays = None
        self.data = dict()

        if self.dated:
            SASReport.create(self, TITLE, orientation=prt.LANDSCAPE, usePlanningPeriod=True)
        else:
            SASReport.create(self, TITLE, orientation=prt.PORTRAIT, usePlanningPeriod=True)

        # Get Planning Period start and end and generate a list with the dates
        # in the planning period.
        pp_start,pp_end = R.eval('fundamental.%pp_start%','fundamental.%pp_end%')
        self.dates = []
        date = pp_start
        while date < pp_end:
            self.dates.append(date)
            date += RelTime(24,0)

        # Get an even number of dates
        odd_dates = len(self.dates) % 2 == 1
        if odd_dates:
            self.dates.append(self.dates[-1] + RelTime(24, 0))


        self.add(self.create_section_header("General Bidding Statistics"))
        self.add(self.create_general_bid_statistics())
        self.add("")
        self.page()
        self.add(self.create_section_header("Lifestyle Fulfillment"))
        self.add(prt.Isolate(self.create_lifestyle_fulfillment_statistics()))
        self.add("")
        self.page()
        self.add(self.create_section_header("Bids Fulfillment"))
        self.add(self.create_bid_fulfillment_statistics())
        self.add("")
        self.page()
        self.add(self.create_dated_bids_details())
        self.add("")
        self.page()
        self.add(self.create_section_header("Time Off Bids Statistics"))
        self.add(self.create_timeoff_bids_statistics())
        self.add(create_timeoff_bids_weekly_statistics(self.data['TimeOff'], self.HEADERBGCOLOUR))
        self.add("")
        self.page()

        self.reset_pp()

    def create_general_bid_statistics(self):
        bid_stats_labels = [
            "Number of crew",
            "Number of bids",
            "Number of crew with bids in period",
            "Number of crew with lifestyle bid",
            "Number of crew with no granted bids",
        ]
        gbs_data = self.get_general_bid_statistics_data()
        bid_stats_values = [
            gbs_data.num_crew,
            gbs_data.num_bids,
            (gbs_data.num_crew_with_db, gbs_data.bidding_crew_percentage),
            (gbs_data.num_crew_with_lifestyle, gbs_data.lifestyling_crew_percentage),
            (gbs_data.num_crew_with_no_granted_pp_bids,
             gbs_data.percent_crew_with_no_granted_pp_bids)
        ]

        return self.create_stats_table(bid_stats_labels, bid_stats_values, percent=True)

    def get_general_bid_statistics_data(self):
        GeneralStats = collections.namedtuple(
            "GeneralStats",
            ("num_crew",
             "num_bids",
             "num_crew_with_db",
             "bidding_crew_percentage",
             "num_crew_with_lifestyle",
             "lifestyling_crew_percentage",
             "num_crew_with_no_granted_pp_bids",
             "percent_crew_with_no_granted_pp_bids",
             ))

        vals = R.eval(
            CONTEXT,
            "report_ls_bid_stats.%num_crew%",
            "report_ls_bid_stats.%num_bids%",
            "report_ls_bid_stats.%num_crew_with_db%",
            "report_ls_bid_stats.%bidding_crew_percentage%",
            "report_ls_bid_stats.%num_crew_with_lifestyle%",
            "report_ls_bid_stats.%lifestyling_crew_percentage%",
            "report_ls_bid_stats.%num_crew_with_no_granted_pp_bids%",
            "report_ls_bid_stats.%percent_crew_with_no_granted_pp_bids%",
        )
        return GeneralStats(*vals)

    def create_lifestyle_fulfillment_statistics(self):
        sh_labels = ["Morning Person",
                     "Evening Person",
                     "Nights at Home",
                     "Nights at Home + Morning Person",
                     "Nights at Home + Evening Person",
                     "Nights Away from Home 2-3 days",
                     "Nights Away from Home 2-3 days + Morning Person",
                     "Nights Away from Home 2-3 days + Evening Person",
                     "Nights Away from Home 3-5 days",
                     "Nights Away from Home 3-5 days + Morning Person",
                     "Nights Away from Home 3-5 days + Evening Person",
        ]

        lh_labels = ["Longhaul West/USA","Longhaul East/Asia",]

        lh_labels_cc = lh_labels + ["Longhaul Any",]

        lsf = self.get_lifestyle_fulfillment_data()

        sh_ls = [(lsf.distribution_morning_person, lsf.avg_fulfillment_morning_person),
                 (lsf.distribution_evening_person, lsf.avg_fulfillment_evening_person),

                 (lsf.distribution_nights_home, lsf.avg_fulfillment_nights_home),
                 (lsf.distribution_nights_at_home_early_ends, lsf.avg_fulfillment_nights_at_home_early_ends, lsf.avg_sec_fulfillment_nights_at_home_early_ends),
                 (lsf.distribution_nights_at_home_late_starts, lsf.avg_fulfillment_nights_at_home_late_starts, lsf.avg_sec_fulfillment_nights_at_home_late_starts),

                 (lsf.distribution_commuter_2_3_days, lsf.avg_fulfillment_commuter_2_3_days),
                 (lsf.distribution_commuter_2_3_days_early_ends, lsf.avg_fulfillment_commuter_2_3_days_early_ends, lsf.avg_sec_fulfillment_commuter_2_3_days_early_ends),
                 (lsf.distribution_commuter_2_3_days_late_starts, lsf.avg_fulfillment_commuter_2_3_days_late_starts, lsf.avg_sec_fulfillment_commuter_2_3_days_late_starts),

                 (lsf.distribution_commuter_3_5_days, lsf.avg_fulfillment_commuter_3_5_days),
                 (lsf.distribution_commuter_3_5_days_early_ends, lsf.avg_fulfillment_commuter_3_5_days_early_ends, lsf.avg_sec_fulfillment_commuter_3_5_days_early_ends),
                 (lsf.distribution_commuter_3_5_days_late_starts, lsf.avg_fulfillment_commuter_3_5_days_late_starts, lsf.avg_sec_fulfillment_commuter_3_5_days_late_starts),]

        lh_ls = [(lsf.distribution_west_destinations, lsf.avg_fulfillment_west_destinations),
                 (lsf.distribution_east_destinations, lsf.avg_fulfillment_east_destinations),
                 (lsf.distribution_any_longhaul_destinations, lsf.avg_fulfillment_any_longhaul_destinations),]

        if lsf.plan_is_cc:
            lsf_values = sh_ls + lh_ls
            lsf_labels = sh_labels + lh_labels_cc
        elif lsf.plan_is_fd_lh:
            lsf_values = lh_ls
            lsf_labels = lh_labels
        else:
            lsf_values = sh_ls
            lsf_labels = sh_labels

        header = self.create_table_header(
            ("Lifestyle", "Number of crew in group (avg. fulfillment)", "Secondary fulfillment*"))
        ls_summary = self.create_stats_table(lsf_labels, lsf_values,
                                             header=header, percent=True)

        # add the average of averages
        summed_avgs = sum((x[1] for x in lsf_values)) * 1.
        lsf_mean = summed_avgs / max(1, len(filter(lambda ls_vals: ls_vals[0], lsf_values)))
        ls_summary.add(prt.Row("Average (unweighted)", "%.f%%" % lsf_mean,
                               background='#f4f4f4'))

        ls_summary.add(prt.Text("*Secondary fulfillment presents the average fulfillment for work days matching one (or both) of the combined lifestyle elements depending on parameter",
                                align=prt.LEFT, font=prt.Font(style=prt.ITALIC)))

        return ls_summary

    def get_lifestyle_fulfillment_data(self):
        LSFulfillment = collections.namedtuple(
            "LSFulfillment",
            ("plan_is_fd_lh",
             "plan_is_cc",

             "distribution_morning_person",
             "avg_fulfillment_morning_person",

             "distribution_evening_person",
             "avg_fulfillment_evening_person",

             "distribution_nights_home",
             "avg_fulfillment_nights_home",

             "distribution_nights_at_home_early_ends",
             "avg_fulfillment_nights_at_home_early_ends",
             "avg_sec_fulfillment_nights_at_home_early_ends",

             "distribution_nights_at_home_late_starts",
             "avg_fulfillment_nights_at_home_late_starts",
             "avg_sec_fulfillment_nights_at_home_late_starts",

             "distribution_commuter_2_3_days",
             "avg_fulfillment_commuter_2_3_days",

             "distribution_commuter_2_3_days_early_ends",
             "avg_fulfillment_commuter_2_3_days_early_ends",
             "avg_sec_fulfillment_commuter_2_3_days_early_ends",

             "distribution_commuter_2_3_days_late_starts",
             "avg_fulfillment_commuter_2_3_days_late_starts",
             "avg_sec_fulfillment_commuter_2_3_days_late_starts",

             "distribution_commuter_3_5_days",
             "avg_fulfillment_commuter_3_5_days",

             "distribution_commuter_3_5_days_early_ends",
             "avg_fulfillment_commuter_3_5_days_early_ends",
             "avg_sec_fulfillment_commuter_3_5_days_early_ends",

             "distribution_commuter_3_5_days_late_starts",
             "avg_fulfillment_commuter_3_5_days_late_starts",
             "avg_sec_fulfillment_commuter_3_5_days_late_starts",

             "distribution_west_destinations",
             "avg_fulfillment_west_destinations",

             "distribution_east_destinations",
             "avg_fulfillment_east_destinations",

             "distribution_any_longhaul_destinations",
             "avg_fulfillment_any_longhaul_destinations",))

        vals = R.eval(
            CONTEXT,
            "report_ls_bid_stats.%plan_is_fd_lh%",
            "report_ls_bid_stats.%plan_is_cc%",

            "kpi.%distribution_morning_person%",
            "kpi.%avg_fulfillment_morning_person%",

            "kpi.%distribution_evening_person%",
            "kpi.%avg_fulfillment_evening_person%",

            "kpi.%distribution_nights_home%",
            "kpi.%avg_fulfillment_nights_home%",

            "kpi.%distribution_nights_at_home_early_ends%",
            "kpi.%avg_fulfillment_nights_at_home_early_ends%",
            "kpi.%avg_sec_fulfillment_nights_at_home_early_ends%",

            "kpi.%distribution_nights_at_home_late_starts%",
            "kpi.%avg_fulfillment_nights_at_home_late_starts%",
            "kpi.%avg_sec_fulfillment_nights_at_home_late_starts%",

            "kpi.%distribution_commuter_2_3_days%",
            "kpi.%avg_fulfillment_commuter_2_3_days%",

            "kpi.%distribution_commuter_2_3_days_early_ends%",
            "kpi.%avg_fulfillment_commuter_2_3_days_early_ends%",
            "kpi.%avg_sec_fulfillment_commuter_2_3_days_early_ends%",

            "kpi.%distribution_commuter_2_3_days_late_starts%",
            "kpi.%avg_fulfillment_commuter_2_3_days_late_starts%",
            "kpi.%avg_sec_fulfillment_commuter_2_3_days_late_starts%",

            "kpi.%distribution_commuter_3_5_days%",
            "kpi.%avg_fulfillment_commuter_3_5_days%",

            "kpi.%distribution_commuter_3_5_days_early_ends%",
            "kpi.%avg_fulfillment_commuter_3_5_days_early_ends%",
            "kpi.%avg_sec_fulfillment_commuter_3_5_days_early_ends%",

            "kpi.%distribution_commuter_3_5_days_late_starts%",
            "kpi.%avg_fulfillment_commuter_3_5_days_late_starts%",
            "kpi.%avg_sec_fulfillment_commuter_3_5_days_late_starts%",

            "kpi.%distribution_west_destinations%",
            "kpi.%avg_fulfillment_west_destinations%",

            "kpi.%distribution_east_destinations%",
            "kpi.%avg_fulfillment_east_destinations%",

            "kpi.%distribution_any_longhaul_destinations%",
            "kpi.%avg_fulfillment_any_longhaul_destinations%",
        )

        return LSFulfillment(*vals)

    def create_bid_fulfillment_statistics(self):
        bid_fulfillment_labels = [
            "Average roster points",
            "Roster points target",
            "Crew below target (high + 2*medium + 2*low)"
        ]

        db_fulfillment_data = self.get_bid_fulfillment_data()

        bid_fulfillment_values = [
            db_fulfillment_data.average_roster_points,
            db_fulfillment_data.rp_target,
            (db_fulfillment_data.num_crew_below_bid_target,
             db_fulfillment_data.percent_crew_below_bid_target)
        ]
        return self.create_stats_table(bid_fulfillment_labels, bid_fulfillment_values, percent=True)


    def create_timeoff_bids_statistics(self):
        self.data['TimeOff'] = DataCollection('TimeOff', dates=self.dates, sumCategory= "_")

        calendarBox = prt.Column()
        if self.dated:
            half_dates = len(self.dates) / 2
            date_intervals = [self.dates[:half_dates],
                              self.dates[half_dates:]]
        else:
            date_intervals = [self.dates]
        for dates in date_intervals:
            calendarBox.add(self.getCalendarRow(dates, leftHeader = 'Date', isDated = self.dated))
            calendarBox.add(self.get_timeoff_bids_data(dates))
            calendarBox.add(prt.Row(''))
        return calendarBox

    def get_timeoff_bids_data(self, dates):
        dt = self.data["TimeOff"]
        headers = ["Placed Bids", "Fulfilled Bids", "Ratio (%)"]
        box = prt.Column()
        total_bids = []
        granted_bids = []
        percent_bids = []
        for date in dates:
            t_bids, = R.eval("report_ls_bid_stats.%total_timeoff_bids_on_day%(" + str(date) +")")
            g_bids, = R.eval("report_ls_bid_stats.%total_granted_timeoff_bids_on_day%(" + str(date) +")")
            p_bids, = R.eval("report_ls_bid_stats.%percent_granted_timeoff_bids_on_day%(" + str(date) +")")
            total_bids.append(t_bids)
            granted_bids.append(g_bids)
            percent_bids.append(p_bids)
            dt.add(headers[0], date, t_bids)
            dt.add(headers[1], date, g_bids)
            dt.add(headers[2], date, p_bids)

        box.add(self.dataRow(headers[0],total_bids))
        box.add(self.dataRow(headers[1],granted_bids))
        box.add(self.dataRow(headers[2],percent_bids, percent=True))

        return box

    def dataRow(self, header, items, percent=None):
        """
        Generates a row in the appropriate format.
        """
        output = prt.Row()

        output.add(prt.Text(header, font=prt.Font(weight=prt.BOLD), align=prt.LEFT))

        for item in items:
            if percent:
                item = str(item)+ "%"

            output.add(prt.Text(item, align=prt.RIGHT))

        return output


    def get_bid_fulfillment_data(self):
        DBFulfillment = collections.namedtuple(
            "LSFulfillment",
            ("average_roster_points",
             "rp_target",
             "num_crew_below_bid_target",
             "percent_crew_below_bid_target"))

        vals = R.eval(
            CONTEXT,
            "report_ls_bid_stats.%average_roster_points%",
            "report_ls_bid_stats.%rp_target%",
            "report_ls_bid_stats.%num_crew_below_bid_target%",
            "report_ls_bid_stats.%percent_crew_below_bid_target%"
        )

        return DBFulfillment(*vals)

    def get_dated_bids_details_data(self):
        DBDetails = collections.namedtuple(
            "DBDetails",
            ("total_timeoff_bids",
             "total_granted_timeoff_bids",
             "percent_granted_timeoff_bids",
             "total_flightid_bids",
             "total_granted_flightid_bids",
             "percent_granted_flightid_bids",
             "total_stop_bids",
             "total_times_granted_stop_bids",
             "total_granted_stop_bids",
             "percent_granted_stop_bids",
             "total_checkin_bids_overall",
             "total_granted_checkin_bids",
             "total_checkout_bids_overall",
             "total_granted_checkout_bids",
             "num_granted_bids",
             "num_bids"))

        vals = R.eval(
            "report_ls_bid_stats.%total_timeoff_bids%",
            "report_ls_bid_stats.%total_granted_timeoff_bids%",
            "report_ls_bid_stats.%percent_granted_timeoff_bids%",
            "report_ls_bid_stats.%total_flightid_bids%",
            "report_ls_bid_stats.%total_granted_flightid_bids%",
            "report_ls_bid_stats.%percent_granted_flightid_bids%",
            "report_ls_bid_stats.%total_stop_bids%",
            "report_ls_bid_stats.%total_times_granted_stop_bids%",
            "report_ls_bid_stats.%total_granted_stop_bids%",
            "report_ls_bid_stats.%percent_granted_stop_bids%",
            "report_ls_bid_stats.%total_checkin_bids_overall%",
            "report_ls_bid_stats.%total_granted_checkin_bids%",
            "report_ls_bid_stats.%total_checkout_bids_overall%",
            "report_ls_bid_stats.%total_granted_checkout_bids%",
            "report_ls_bid_stats.%crew_total_granted_bids%",
            "report_ls_bid_stats.%crew_total_bids%"
        )
        return DBDetails(*vals)

    def create_dated_bids_details(self):
        general_bids_data = self.get_dated_bids_details_data()
        mdata = self.get_bid_matrix_data()
        mat_vals = [
            ("TimeOff",
             mdata.granted_num_timeoff_bids_low, mdata.total_num_timeoff_bids_low,
             mdata.granted_num_timeoff_bids_medium, mdata.total_num_timeoff_bids_medium,
             mdata.granted_num_timeoff_bids_high, mdata.total_num_timeoff_bids_high,
             general_bids_data.total_granted_timeoff_bids, general_bids_data.total_timeoff_bids),
            ("FlightId",
             mdata.granted_num_flightid_bids_low, mdata.total_num_flightid_bids_low,
             mdata.granted_num_flightid_bids_medium, mdata.total_num_flightid_bids_medium,
             mdata.granted_num_flightid_bids_high, mdata.total_num_flightid_bids_high,
             general_bids_data.total_granted_flightid_bids, general_bids_data.total_flightid_bids),
            ("Stop",
             mdata.granted_num_stop_bids_low, mdata.total_num_stop_bids_low,
             mdata.granted_num_stop_bids_medium, mdata.total_num_stop_bids_medium,
             mdata.granted_num_stop_bids_high, mdata.total_num_stop_bids_high,
             general_bids_data.total_granted_stop_bids, general_bids_data.total_stop_bids),
            ("CheckIn",
             mdata.granted_num_checkin_bids_low, mdata.total_num_checkin_bids_low,
             mdata.granted_num_checkin_bids_medium, mdata.total_num_checkin_bids_medium,
             mdata.granted_num_checkin_bids_high, mdata.total_num_checkin_bids_high,
             general_bids_data.total_granted_checkin_bids, general_bids_data.total_checkin_bids_overall),
            ("CheckOut",
             mdata.granted_num_checkout_bids_low, mdata.total_num_checkout_bids_low,
             mdata.granted_num_checkout_bids_medium, mdata.total_num_checkout_bids_medium,
             mdata.granted_num_checkout_bids_high, mdata.total_num_checkout_bids_high,
             general_bids_data.total_granted_checkout_bids, general_bids_data.total_checkout_bids_overall)
        ]
        tots = ("TOTAL",
                mdata.granted_num_bids_low, mdata.total_num_bids_low,
                mdata.granted_num_bids_medium, mdata.total_num_bids_medium,
                mdata.granted_num_bids_high, mdata.total_num_bids_high,
                general_bids_data.num_granted_bids, general_bids_data.num_bids)

        bmat = prt.Column()
        bmat.add(self.create_table_header(("", "LOW", "MEDIUM", "HIGH", "TOTAL"),
                                          (70, 70, 70, 70, 70)))

        for tup in mat_vals:
            r = prt.Row()
            r.add(prt.Text(tup[0], font=prt.Font(weight=prt.BOLD)))
            for i in xrange(1, 8, 2):  # (1, 3, 5, 7)
                r.add("%s / %s (%.f%%)" %
                      (tup[i], tup[i + 1], tup[i] * 100. / tup[i + 1]
                       if tup[i + 1] else 0))
            bmat.add(r)

        totals = prt.Row(background='#f4f4f4')
        totals.add(prt.Text(tots[0], font=prt.Font(weight=prt.BOLD)))
        for i in xrange(1, 8, 2):  # (1, 3, 5, 7)
            totals.add("%s / %s (%.f%%)" %
                       (tots[i], tots[i + 1], tots[i] * 100. / tots[i + 1]
                        if tots[i + 1] else 0))
        bmat.add(totals)

        bmat.add("")
        stbid_details = (general_bids_data.total_granted_stop_bids,
                         general_bids_data.total_times_granted_stop_bids)

        bmat.add(
            prt.Row(
                "Total stops per granted bid ratio",
                "%s / %s (avg %.1f)" %
                (stbid_details[1], stbid_details[0], stbid_details[1] * 1. / stbid_details[0]
                 if stbid_details[0] else 0)))
        bmat.add("")
        return prt.Isolate(bmat)

    def get_bid_matrix_data(self):
        DBMData = collections.namedtuple(
            "DBMData",
            ("total_num_timeoff_bids_low",
             "total_num_timeoff_bids_medium",
             "total_num_timeoff_bids_high",
             "granted_num_timeoff_bids_low",
             "granted_num_timeoff_bids_medium",
             "granted_num_timeoff_bids_high",
             "total_num_stop_bids_low",
             "total_num_stop_bids_medium",
             "total_num_stop_bids_high",
             "granted_num_stop_bids_low",
             "granted_num_stop_bids_medium",
             "granted_num_stop_bids_high",
             "total_num_flightid_bids_low",
             "total_num_flightid_bids_medium",
             "total_num_flightid_bids_high",
             "granted_num_flightid_bids_low",
             "granted_num_flightid_bids_medium",
             "granted_num_flightid_bids_high",
             "total_num_checkin_bids_low",
             "total_num_checkin_bids_medium",
             "total_num_checkin_bids_high",
             "granted_num_checkin_bids_low",
             "granted_num_checkin_bids_medium",
             "granted_num_checkin_bids_high",
             "total_num_checkout_bids_low",
             "total_num_checkout_bids_medium",
             "total_num_checkout_bids_high",
             "granted_num_checkout_bids_low",
             "granted_num_checkout_bids_medium",
             "granted_num_checkout_bids_high",
             "total_num_bids_low",
             "granted_num_bids_low",
             "total_num_bids_medium",
             "granted_num_bids_medium",
             "total_num_bids_high",
             "granted_num_bids_high",
             ))

        vals = R.eval(
            "report_ls_bid_stats.%total_num_timeoff_bids_low%",
            "report_ls_bid_stats.%total_num_timeoff_bids_medium%",
            "report_ls_bid_stats.%total_num_timeoff_bids_high%",
            "report_ls_bid_stats.%granted_num_timeoff_bids_low%",
            "report_ls_bid_stats.%granted_num_timeoff_bids_medium%",
            "report_ls_bid_stats.%granted_num_timeoff_bids_high%",
            "report_ls_bid_stats.%total_num_stop_bids_low%",
            "report_ls_bid_stats.%total_num_stop_bids_medium%",
            "report_ls_bid_stats.%total_num_stop_bids_high%",
            "report_ls_bid_stats.%granted_num_stop_bids_low%",
            "report_ls_bid_stats.%granted_num_stop_bids_medium%",
            "report_ls_bid_stats.%granted_num_stop_bids_high%",
            "report_ls_bid_stats.%total_num_flightid_bids_low%",
            "report_ls_bid_stats.%total_num_flightid_bids_medium%",
            "report_ls_bid_stats.%total_num_flightid_bids_high%",
            "report_ls_bid_stats.%granted_num_flightid_bids_low%",
            "report_ls_bid_stats.%granted_num_flightid_bids_medium%",
            "report_ls_bid_stats.%granted_num_flightid_bids_high%",
            "report_ls_bid_stats.%total_num_checkin_bids_low%",
            "report_ls_bid_stats.%total_num_checkin_bids_medium%",
            "report_ls_bid_stats.%total_num_checkin_bids_high%",
            "report_ls_bid_stats.%granted_num_checkin_bids_low%",
            "report_ls_bid_stats.%granted_num_checkin_bids_medium%",
            "report_ls_bid_stats.%granted_num_checkin_bids_high%",
            "report_ls_bid_stats.%total_num_checkout_bids_low%",
            "report_ls_bid_stats.%total_num_checkout_bids_medium%",
            "report_ls_bid_stats.%total_num_checkout_bids_high%",
            "report_ls_bid_stats.%granted_num_checkout_bids_low%",
            "report_ls_bid_stats.%granted_num_checkout_bids_medium%",
            "report_ls_bid_stats.%granted_num_checkout_bids_high%",
            "report_ls_bid_stats.%total_num_bids_low%",
            "report_ls_bid_stats.%granted_num_bids_low%",
            "report_ls_bid_stats.%total_num_bids_medium%",
            "report_ls_bid_stats.%granted_num_bids_medium%",
            "report_ls_bid_stats.%total_num_bids_high%",
            "report_ls_bid_stats.%granted_num_bids_high%"
        )

        return DBMData(*vals)

    def create_stats_table(self, labels, values, header=None, percent=False):
        stats_row = prt.Column()
        if header:
            stats_row.add(header)
        for label, val in zip(labels, values):
            value_str = ""
            if isinstance(val, tuple):
                vals = tuple((f if f else "0" for f in val))
                value_str = "%s (%s" % (vals[0], vals[1])
                value_str += "%)"
            else:
                value_str = val
            if isinstance(val, tuple) and len(val) == 3:
                sec_value_str = "%s" % vals[2]
                sec_value_str += "%"
                stats_row.add(prt.Row(label, value_str, sec_value_str))
            else:
                stats_row.add(prt.Row(label, value_str))
        return stats_row

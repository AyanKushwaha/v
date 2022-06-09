"""
Resource Pool Bid Days

This report shows an overview of Resource Pool Days for Production bids.
"""

# imports ================================================================{{{1
from AbsTime import AbsTime
from Cui import CuiCrcGetParameterAsString
from Cui import CuiCrcSetParameterFromString
from RelTime import RelTime
from Variable import Variable
from carmensystems.publisher.api import BOLD
from carmensystems.publisher.api import Column
from carmensystems.publisher.api import Font
from carmensystems.publisher.api import ITALIC
from carmensystems.publisher.api import LANDSCAPE
from carmensystems.publisher.api import Row
from carmensystems.publisher.api import Text
from datetime import datetime
from report_sources.include.SASReport import SASReport
import Tkinter, tkFileDialog    # Tk is used for displaying "Save as..." dialog for CSV
import carmensystems.rave.api as R
import os

# constants =============================================================={{{1
#CONTEXT = 'default_context'
CONTEXT = 'sp_crew'
TITLE = 'Resource Pool Bid Days'
CSV_DIR = "/samba-share/reports/ResourcePoolBidDays"

WRITE_COPY_TO_CSV = True

# classes ================================================================{{{1

# TableTitleRow----------------------------------------------------------------{{{2
class TableTitleRow(Row):
    """
    Create a right aligned row intended for table column headers
    """

    def __init__(self, *args):
        # Create a basic row
        Row.__init__(self, *args)

        # Add formatting
        self.set(font=Font(size=9, style=ITALIC, weight=BOLD))


class DateRangeDialog:
    """Pop-up dialog to enter the date range of the report"""
    def __init__(self, parent, start_date, end_date):
        self._start_date = start_date
        self._end_date = end_date
        self._min_start_date = start_date
        self._max_end_date = end_date

        top = self.top = Tkinter.Toplevel(parent)
        self.start_label = Tkinter.Label(top, text='Start date')
        self.start_label.pack()

        self.start_entry_box = Tkinter.Entry(top)
        self.start_entry_box.insert(Tkinter.END, start_date.ddmonyyyy()[:9])
        self.start_entry_box.pack()

        self.end_label = Tkinter.Label(top, text='End date')
        self.end_label.pack()

        self.end_entry_box = Tkinter.Entry(top)
        self.end_entry_box.insert(Tkinter.END, end_date.ddmonyyyy()[:9])
        self.end_entry_box.pack()

        self.message_label = Tkinter.Label(top)
        self.message_label.pack()

        self.my_submit_button = Tkinter.Button(top, text='Done', command=self.done)
        self.my_submit_button.pack()

    def done(self):
        """Collect and validate data. If data is OK then destroy dialog, else report problem text to user"""
        try:
            self._start_date = AbsTime(self.start_entry_box.get()).day_floor()
        except:
            self.message_label.config(text='Start date format not recognized: %s' % self.start_entry_box.get())
            return

        try:
            self._end_date = AbsTime(self.end_entry_box.get()).day_floor() + RelTime(23, 59)
        except:
            self.message_label.config(text='End date format not recognized: %s' % self.end_entry_box.get())
            return

        if self._start_date < self._min_start_date:
            self.message_label.config(text='Start date must not be earlier than %s' % self._min_start_date)
            return

        if self._end_date > self._max_end_date:
            self.message_label.config(text='End date must not be later than %s' % self._max_end_date)
            return

        if self._end_date < self._start_date:
            self.message_label.config(text='End date must be later than start date')
            return

        self.top.destroy()

    def get_date_range(self):
        """Get the date range that was entered in the dialog"""
        return (self._start_date, self._end_date)


# BidStatistics-------------------------------------------------------------{{{2
class ResourcePoolBidDays(SASReport):
    """
    Create the report using the Python Publisher API.
    """

    def create(self):
        # Basic setup
        SASReport.create(self, TITLE, usePlanningPeriod=True, orientation=LANDSCAPE)

        # Get Planning Period start and end
        pp_start, pp_end = R.eval('fundamental.%pp_start%', 'fundamental.%pp_end%')

        period_start, period_end = ask_date_range(pp_start, pp_end)

        if WRITE_COPY_TO_CSV:
            timestamp = datetime.now()
            try:
                if not os.path.isdir(CSV_DIR):
                    os.makedirs(CSV_DIR)
                # display Tk "Save as..." dialog
                tk_root = Tkinter.Tk()
                tk_root.withdraw()          # hides Tk main window
                saveas_dlg_options = {}
                saveas_dlg_options["defaultextension"] = ".csv"
                saveas_dlg_options["filetypes"] = [("CSV files", ".csv"), ("All files", ".*")]
                saveas_dlg_options["initialdir"] = CSV_DIR
                saveas_dlg_options["initialfile"] = "ResourcePoolBidDays_%s_%s_%s.csv" % (str(timestamp.year), str(timestamp.month).zfill(2), str(timestamp.day).zfill(2))
                saveas_dlg_options["title"] = "Save as"
                saveas_dlg_options["parent"] = tk_root
                csv_filename = tkFileDialog.asksaveasfilename(**saveas_dlg_options)
                tk_root.destroy()
                csv_fd = open(csv_filename, "wb")
            except Exception as exc:
                print "Error opening CSV file: %s: %s" % (str(csv_filename), str(exc))

        old_bids_table = Variable("")
        CuiCrcGetParameterAsString('bid.table_para', old_bids_table)
        CuiCrcSetParameterFromString('bid.table_para', Variable("bids_rp"))

        month_end = (period_start.month_floor() + RelTime(0, 1)).month_ceil()
        date = period_start
        dates = []
        while date < period_end:
            dates.append(date)
            date += RelTime(24, 0)

        period_column = Column()
        period_column.add(Row("Shown period: %s - %s" % (period_start.ddmonyyyy()[:9], period_end.ddmonyyyy()[:9])))
        self.add(period_column)

        ##########################################
        # Create area with data on bids
        h_row, h_csv_row = self.headerRow(dates)

        column = Column()
        column.add_header(h_row)
        if WRITE_COPY_TO_CSV:
            csv_fd.write('Report ' + TITLE + '\n')
            csv_fd.write('\n')
            csv_fd.write('Created: %s;;Period: %s-%s\n' % (datetime.now(), period_start.ddmonyyyy()[:9], period_end.ddmonyyyy()[:9]))
            csv_fd.write('\n')
            csv_fd.write(h_csv_row + '\n')

        rp_bids_query = R.foreach(R.times('bid.%crew_num_bids%', where='bid.%type_of_bid%(fundamental.%py_index%)="DaysForProduction"'),
                                  'bid.%abs1%(fundamental.%py_index%, 0)',
                                  'bid.%abs2%(fundamental.%py_index%, 0)')

        rp_trips_query = R.foreach(R.iter('iterators.trip_set',
                                          where='trip.%is_on_duty% and trip.%start_hb% < ' + str(period_end) + ' and trip.%end_hb% > ' +  str(period_start)),
                                   'trip.%start_hb%',
                                   'trip.%end_hb%')

        rp_crew_query = R.foreach(R.iter('iterators.roster_set',
                                         where='crg_resource_pool_bid_days.%crew_is_rp%',
                                         sort_by='crg_resource_pool_bid_days.%crew_name%'),
                                  'crg_resource_pool_bid_days.%crew_employee_number%',
                                  'crg_resource_pool_bid_days.%crew_name%',
                                  'crg_resource_pool_bid_days.%crew_group%',
                                  rp_trips_query,
                                  rp_bids_query)
        rp_crew, = R.eval(CONTEXT, rp_crew_query)

        for crew in rp_crew:
            all_bids = crew[-1]
            all_trips = crew[-2]

            bid_dates = ["" for _ in dates]

            for bid in all_bids:
                bid_start = max(bid[1], period_start)
                bid_end = bid[2]
                while bid_start < bid_end and bid_start < period_end:
                    index = int((bid_start - period_start) / RelTime(24, 0))
                    bid_dates[index] = '1'
                    bid_start = bid_start + RelTime(24, 0)

            for trip in all_trips:
                trip_start = max(trip[1].day_floor(), period_start)
                trip_end = trip[2].day_ceil()
                while trip_start < trip_end and trip_start < period_end:
                    index = int((trip_start - period_start) / RelTime(24, 0))
                    bid_dates[index] = 'P'
                    trip_start = trip_start + RelTime(24, 0)

            num_bids = 0
            max_index = int((min(period_end, month_end) - period_start) / RelTime(24, 0))
            for index in range(0, max_index):
                if bid_dates[index] != "":
                    num_bids = num_bids + 1

            row = list(crew[1:4]) + [num_bids] + bid_dates
            if WRITE_COPY_TO_CSV:
                csv_row = ';'.join([str(field) for field in row]) + '\n'
                csv_fd.write(csv_row)
            bid_row = [Text(str(t)) for t in row]
            column.add(Row(*bid_row))
            column.page0()

        self.add(column)

        CuiCrcSetParameterFromString('bid.table_para', old_bids_table)


    def headerRow(self, dates):
        """Generate table header"""
        left_headers = ['Empno', 'Name', 'Group', 'Sum bid days month 1']
        tmp_row = self.getCalendarRow(dates, leftHeaders=left_headers)
        tmp_csv_row = self.getCalendarRow(dates, leftHeaders=left_headers, csv=True)
        return tmp_row, tmp_csv_row


def ask_date_range(start_date, end_date):
    """Ask for the date range with a popup dialog"""
    tk_root = Tkinter.Tk()
    tk_root.withdraw()          # hides Tk main window
    input_dialog = DateRangeDialog(tk_root, start_date, end_date)
    tk_root.wait_window(input_dialog.top)
    date_range = input_dialog.get_date_range()
    tk_root.destroy()
    return date_range


# End of file

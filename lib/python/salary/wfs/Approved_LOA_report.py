"""
Approved LOA report
This report shows an overview of leave of absence based on daily file received from WFS
"""

from AbsTime import AbsTime
from datetime import date
from tm import TM
from carmensystems.publisher.api import Column
from carmensystems.publisher.api import LANDSCAPE
from carmensystems.publisher.api import Row
from report_sources.include.SASReport import SASReport
from carmensystems.publisher.api import *
import xlsxwriter
import os
import csv
import Cfh
import Localization
# constants =============================================================={{{1
TITLE = 'Approved Leave of Absence'
headers = ['Employment number','Crew ID', 'Region', 'Base', 'Rank', 'Absence code', ' Total requested time','Time type', 'Abscence start date', 'Absence end date','Absence flag', 'Time stamp']
carmdata = os.environ['CARMDATA']
source = os.path.join(carmdata, 'REPORTS/SALARY_WFS/')
# classes ================================================================{{{1
class selection_box(Cfh.Box):
    """
    Selection box that lets user specify date range and crew region and category
    """
    def __init__(self, title):
        Cfh.Box.__init__(self, 'DATE_SELECTION_BOX', title)
        today = to_AbsTime(date.today())
        self._st_txt = Cfh.Label(self, 'L_START_DATE', Localization.MSGR('Start date'))
        self._st_txt.setLoc(Cfh.CfhLoc(1, 0))

        self._et_txt = Cfh.Label(self, 'L_END_DATE', Localization.MSGR('End date'))
        self._et_txt.setLoc(Cfh.CfhLoc(2, 0))

        self._start_date = Cfh.Date(self, 'START_DATE', today)
        self._start_date.setLoc(Cfh.CfhLoc(1, 8))

        self._end_date = Cfh.Date(self, 'END_DATE', today)
        self._end_date.setLoc(Cfh.CfhLoc(2, 8))

        self._st_tz = Cfh.Label(self, 'L_START_TZ', Localization.MSGR('CET'))
        self._st_tz.setLoc(Cfh.CfhLoc(1, 20))

        self._et_tz = Cfh.Label(self, 'L_END_TZ', Localization.MSGR('CET'))
        self._et_tz.setLoc(Cfh.CfhLoc(2, 20))

        self._category_label = Cfh.Label(self, "CATEGORY_LABEL",
                                        Cfh.Area(Cfh.Loc(3, 0)), "Category:")
        self._category_entry = CategoryString(self, "CATEGORY_VALUE",
                                               Cfh.Area(Cfh.Dim(10, 1), Cfh.Loc(3, 6)), 4, "CC")

        self._region_label = Cfh.Label(self, "REGION_LABEL",
                                        Cfh.Area(Cfh.Loc(4, 0)), "Region:")
        self._region_entry = RegionString(self, "REGION_VALUE",
                                        Cfh.Area(Cfh.Dim(10, 1), Cfh.Loc(4, 6)), 4, "SKD")

        self._ok = Cfh.Done(self, "OK")
        self._ok.setText(Localization.MSGR("OK"))
        self._ok.setMnemonic(Localization.MSGR("_OK"))

        self._cancel = Cfh.Cancel(self, "Cancel")
        self._cancel.setText(Localization.MSGR("Cancel"))
        self._cancel.setMnemonic(Localization.MSGR("_Cancel"))

        self.build()
        self.show(True)
        self._choice = self.loop()

    def __nonzero__(self):
        return self._choice == Cfh.CfhOk

    @property
    def start_date(self):
        return AbsTime(self._start_date.valof())

    @property
    def end_date(self):
        return AbsTime(self._end_date.valof()) + RelTime(24, 0)

    @property
    def region(self):
        return self._region_entry.valof()

    @property
    def category(self):
        return self._category_entry.valof()


class CategoryString(Cfh.String):
    def __init__(self, parent, *a, **k):
        Cfh.String.__init__(self, parent, *a, **k)
        self.parent = parent
        self.setMandatory(True)
        self.setMenuOnly(True)
        self.setMenuString("Category;FD;CC")
        self.setStyle(Cfh.CfhSChoiceCombo)



class RegionString(Cfh.String):
    def __init__(self, parent, *a, **k):
        Cfh.String.__init__(self, parent, *a, **k)
        self.parent = parent
        self.setMandatory(False)
        self.setMenuOnly(True)
        self.setMenuString("Region;All;SKD;SKN;SKS;SKI")
        self.setStyle(Cfh.CfhSChoiceCombo)


class Approved_LOA_report(SASReport):
    """
    Create the report using the Python Publisher API.
    """
    def create(self):
        input = selection_box('Approved LOA report')
        start_date = input.start_date
        end_date = input.end_date.adddays(-1)
        region =input.region
        category = input.category[0]
        SASReport.create(self, TITLE, orientation=LANDSCAPE)
        header = self.getTableHeader(items = headers)
        rows = open_csv_file(start_date, end_date, region, category)
        column = Column()
        column.add_header(header)
        if rows:
            for row in rows:
                column.add(Row(*row))
                column.page0()
        else:
            column.add("No LOA information for selected date/s")
        create_excel_report(rows, start_date, end_date)
        self.add(column)

def open_csv_file(start_date, end_date, region, category):
    """ Open the source csv files based on selected dates, files are stored as list of lists,
    where each list contains a row of a csv file, skip empty rows and header rows, gets crew ID, rank, base, region and category from crew_employment table"""
    files = []
    rows = []
    # If variable one_day_only is true, only check file from today, otherwise, check files from range
    for filename in os.listdir(source):
        if 'WFS_CMS' in filename and not '-' in filename and (start_date <= AbsTime((filename[12:20:])) <= end_date):
            files.append(filename)
    for file in files:
        with open(source+file, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0] != 'EMPLOYEE_ID':
                    extperkey = row[0]
                    timestamp = to_AbsTime(row[8][0:10:])
                    if get_crew_info(extperkey, timestamp):
                        crew, crew_category, crew_region, crew_base, crew_rank = get_crew_info(extperkey, timestamp)
                    else:
                        # If extperkey does not correspond to any crew in crew_employment
                        crew=crew_category=crew_region=crew_base=crew_rank = ""
                    # If crew corresponds to category and region, or if region and category is unknown
                    if category == crew_category and (region == crew_region or region == "All") or crew_region == crew_category == "":
                        row.pop(6)
                        row.insert(1, crew)
                        row.insert(2, crew_region)
                        row.insert(3, crew_base)
                        row.insert(4, crew_rank)
                        if row not in rows:
                            rows.append(row)
    return rows

def create_excel_report(rows, start_date, end_date):
    """Generation of excel report. Moved out from create to make it easier to call from reporthandler"""
    if start_date == end_date:
        date_range = str(start_date)[0:9:]
    else:
        date_range = (str(start_date))[0:9:] + '-' + str(end_date)[0:9:]
    workbook = xlsxwriter.Workbook('/samba-share/reports/LOA_report/LOA_report_{}.xlsx'.format(date_range))
    bold = workbook.add_format({'bold': True})
    white_bg = workbook.add_format({'border': 1,
                                    'text_wrap': True,
                                    'font_name': 'Arial',
                                    'font_size': 10,
                                    'align': 'center'})

    light_blue_bg = workbook.add_format({'bg_color': '#CCFFFF',
                                         'border': 1,
                                         'text_wrap': True,
                                         'font_name': 'Arial',
                                         'font_size': 10,
                                         'align': 'center'})
    EN_col = 0
    CID_col = 1
    REG_col = 2
    BAS_col = 3
    RAN_col = 4
    AC_col = 5
    TRT_col = 6
    TT_col = 7
    ASD_col = 8
    AED_col = 9
    AF_col = 10
    TS_col = 11
    r = 0

    worksheet = workbook.add_worksheet("Leave of absence")

    worksheet.set_column(EN_col, EN_col, 13)
    worksheet.set_column(CID_col, CID_col, 13)
    worksheet.set_column(REG_col, REG_col, 13)
    worksheet.set_column(BAS_col, BAS_col, 13)
    worksheet.set_column(RAN_col, RAN_col, 13)
    worksheet.set_column(AC_col, AC_col, 40)
    worksheet.set_column(TRT_col, TRT_col, 13)
    worksheet.set_column(TT_col, TT_col, 13)
    worksheet.set_column(ASD_col, ASD_col, 20)
    worksheet.set_column(AED_col, AED_col, 20)
    worksheet.set_column(AF_col, AF_col, 13)
    worksheet.set_column(TS_col, TS_col, 20)

    worksheet.write(r, EN_col, 'Employment number', light_blue_bg)
    worksheet.write(r, CID_col, 'Crew ID', light_blue_bg)
    worksheet.write(r, REG_col, 'Region', light_blue_bg)
    worksheet.write(r, BAS_col, 'Base', light_blue_bg)
    worksheet.write(r, RAN_col, 'Rank', light_blue_bg)
    worksheet.write(r, AC_col, 'Absence code', light_blue_bg)
    worksheet.write(r, TRT_col, 'Total requested', light_blue_bg)
    worksheet.write(r, TT_col, 'Time type', light_blue_bg)
    worksheet.write(r, ASD_col, 'Absence start date', light_blue_bg)
    worksheet.write(r, AED_col, 'Absence end date', light_blue_bg)
    worksheet.write(r, AF_col, 'Absence flag', light_blue_bg)
    worksheet.write(r, TS_col, 'Time stamp', light_blue_bg)
    r += 1

    for row in rows:
        c = 0
        id = row[0]
        for element in row:
            worksheet.write(r, c, element, white_bg)
            c += 1
        r += 1

    workbook.close()


def get_crew_info(crew_id, date):
    """ Returns crew info from crew_employment table based on extperkey and date """
    for entry in TM.crew_employment.search('(extperkey=%s)'%crew_id):
        if date >= entry.validfrom and date < entry.validto:
            return entry.crew.id, entry.crewrank.maincat.id, entry.region.id, entry.base.id, entry.crewrank.id
    return None


def to_AbsTime(date):
    """ Auxiliary function to format date correctly"""
    return AbsTime(str(date).replace("-", ""))

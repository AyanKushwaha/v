"""
Daily Alert SVS report
This report shows daily track alert data for SVS flights
"""

from AbsTime import AbsTime
from datetime import timedelta,date
from tm import TM
from carmensystems.publisher.api import Column
from carmensystems.publisher.api import LANDSCAPE
from carmensystems.publisher.api import Row
from report_sources.include.SASReport import SASReport
from carmensystems.publisher.api import *
from utils.xmlutil import dateTime
import xlsxwriter
import os
import csv
import Cfh
import Localization
import calendar
# constants =============================================================={{{1
TITLE = 'Daily Alert Monitor Report'
headers = ['Crew', 'ActivityType', 'Activity Id', 'Rule', 'Description', 'Alert Group', 'Severity', 'Alert Time', 'Deadline', 'Limit Value',  'Actual Value', 'Signature', 'Generated Time' , 'Updated Time', 'Updated by']
owner = 'SVS'
last_day_of_prev_month  =  date.today(). replace(day=1) - timedelta(days=1)
start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)
last_day_of_the_month = date.today().replace(day = calendar.monthrange(date.today().year, date.today().month)[1]) + timedelta(days=1)
start = AbsTime(str(start_day_of_prev_month).replace("-", ""))
end = AbsTime(str(last_day_of_the_month).replace("-", ""))


# methods  ================================================================{{{1
def DateYYMMDD(atime):
    """Convert AbsTime to date in format YYMMDD."""
    if atime is None:
        return 6 * ' '
    (y, m, d, H, M) = atime.split()[:5]
    return ("%04d%02d%02d" % atime.split()[:3])[2:]

def get_crew_info():
    print start
    print end
    i = 0
    j = 0
    for ext in TM.crew_employment.search('(carrier=%s)'%owner):
        for alert in TM.track_alert.search("(&(alerttime<%s)(alerttime>=%s)(empno=%s))" % (end,start,ext.extperkey)):
            print "The alert list is " ,alert.empno, " ; " ,alert.activity.atype.id, " ; " , alert.activity.id, " ; " , alert.rule, " ; " ,alert.description, " ; " ,alert.alertgroup, " ; " ,alert.severity," ; " ,alert.alerttime, " ; " ,alert.deadline, " ; " ,alert.limitval, " ; " ,alert.actualval, " ; " ,alert.signature, " ; " ,alert.generatedtime, " ; " ,alert.updatedtime, " ; " ,alert.updatedby
            i += 1
    for alert in TM.track_alert.search("(&(alerttime<%s)(alerttime>=%s))" % (end,start)):
        if owner in alert.activity.id:
           print "The alert list is " ,alert.empno, " ; " ,alert.activity.atype.id, " ; " , alert.activity.id, " ; " , alert.rule, " ; " ,alert.description, " ; " ,alert.alertgroup, " ; " ,alert.severity," ; " ,alert.alerttime, " ; " ,alert.deadline, " ; " ,alert.limitval, " ; " ,alert.actualval, " ; " ,alert.signature, " ; " ,alert.generatedtime, " ; " ,alert.updatedtime, " ; " ,alert.updatedby
           j += 1

    print "The final value of i=%s and j=%s " % (str(i),str(j))

def generate_records():
    rows_ = []
    rows = []
    row = []
    for ext in TM.crew_employment.search('(carrier=%s)'%owner):
        for alert in TM.track_alert.search("(&(alerttime<%s)(alerttime>=%s)(empno=%s))" % (end,start,ext.extperkey)):
            row = []
            row = [str(alert.empno), str(alert.activity.atype.id), str(alert.activity.id), str(alert.rule), str(alert.description), str(alert.alertgroup), str(alert.severity), str(alert.alerttime), str(alert.deadline),  str(alert.limitval),  str(alert.actualval),  str(alert.signature), str(alert.generatedtime), str(alert.updatedtime),  str(alert.updatedby), DateYYMMDD(alert.alerttime)]
            if row not in rows_: 
               rows_.append(row)
         
 
    for alert in TM.track_alert.search("(&(alerttime<%s)(alerttime>=%s))" % (end,start)):
        if owner in alert.activity.id:
           row = []
           row = [str(alert.empno), str(alert.activity.atype.id), str(alert.activity.id), str(alert.rule), str(alert.description), str(alert.alertgroup), str(alert.severity), str(alert.alerttime), str(alert.deadline),  str(alert.limitval),  str(alert.actualval),  str(alert.signature), str(alert.generatedtime), str(alert.updatedtime),  str(alert.updatedby), DateYYMMDD(alert.alerttime)]
           if row not in rows_:
              rows_.append(row)



    rows_.sort(key = lambda rows_: rows_[15])
    for r in rows_:
        value=r.pop()        
        if r not in rows:
           rows.append(r)   
    return rows


def create_excel_report(rows, start_date):
    """Generation of excel report. Moved out from create to make it easier to call from reporthandler"""
    date_range = str(start_date)[0:9:]
    workbook = xlsxwriter.Workbook('/samba-share/reports/daily_alert_svs/SVS_ACTIVE_ALERTS_{}.xlsx'.format(date_range))
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
    CRW_col = 0
    ATY_col = 1
    ATI_col = 2
    RUL_col = 3
    DES_col = 4
    ALG_col = 5
    SEV_col = 6
    ALT_col = 7
    DDL_col = 8
    LIV_col = 9
    ACV_col = 10
    SIG_col = 11
    GEN_col = 12
    UPD_col = 13
    UPB_col = 14
    r = 0

    worksheet = workbook.add_worksheet("Daily alert report")

    worksheet.set_column(CRW_col, CRW_col, 8)
    worksheet.set_column(ATY_col, ATY_col, 15)
    worksheet.set_column(ATI_col, ATI_col, 50)
    worksheet.set_column(RUL_col, RUL_col, 80)
    worksheet.set_column(DES_col, DES_col, 80)
    worksheet.set_column(ALG_col, ALG_col, 30)
    worksheet.set_column(SEV_col, SEV_col, 10) 
    worksheet.set_column(ALT_col, ALT_col, 20)
    worksheet.set_column(DDL_col, DDL_col, 20)
    worksheet.set_column(LIV_col, LIV_col, 20)
    worksheet.set_column(ACV_col, ACV_col, 20)
    worksheet.set_column(SIG_col, SIG_col, 20)
    worksheet.set_column(GEN_col, GEN_col, 20)
    worksheet.set_column(UPD_col, UPD_col, 20)
    worksheet.set_column(UPB_col, UPB_col, 40)

    worksheet.write(r, CRW_col, 'Crew', light_blue_bg)
    worksheet.write(r, ATY_col, 'Activity Type', light_blue_bg)
    worksheet.write(r, ATI_col, 'Activity Id', light_blue_bg)
    worksheet.write(r, RUL_col, 'Rule', light_blue_bg)
    worksheet.write(r, DES_col, 'Description', light_blue_bg)
    worksheet.write(r, ALG_col, 'Alert Group', light_blue_bg)
    worksheet.write(r, SEV_col, 'Severity', light_blue_bg)
    worksheet.write(r, ALT_col, 'Alert Time', light_blue_bg)
    worksheet.write(r, DDL_col, 'Deadline', light_blue_bg)
    worksheet.write(r, LIV_col, 'Limit Value', light_blue_bg)
    worksheet.write(r, ACV_col, 'Actual Value', light_blue_bg)
    worksheet.write(r, SIG_col, 'Signature', light_blue_bg)
    worksheet.write(r, GEN_col, 'Generated Time', light_blue_bg)
    worksheet.write(r, UPD_col, 'Updated Time', light_blue_bg)
    worksheet.write(r, UPB_col, 'Updated by', light_blue_bg)
    r += 1

    for row in rows:
        c = 0
        for element in row:
            worksheet.write(r, c, element, white_bg)
            c += 1
        r += 1

    workbook.close()

def to_AbsTime(date):
    """ Auxiliary function to format date correctly"""
    return AbsTime(str(date).replace("-", ""))

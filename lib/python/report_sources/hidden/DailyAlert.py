from alert.svs.daily_alert_svs import *
from report_sources.hidden.GenerateAlertSVS import *
from datetime import date

def send_daily_alert():
      today = to_AbsTime(date.today())
      rows =  generate_records()
      print rows
      create_excel_report(rows, today)
      send_email(str(today)[0:9:])

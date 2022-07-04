"""
Daily alert report for SVS
"""
from alert.svs.daily_alert_svs import generate_records, create_excel_report, to_AbsTime
import logging
from report_sources.report_server.rs_if import argfix
from smtplib import SMTP
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import os
from datetime import date
"""
Entry point for the report server
"""
logging.basicConfig()
log = logging.getLogger('daily_alert_svs')
log.setLevel(logging.DEBUG)

samba_source = '/samba-share/reports/daily_alert_svs/'
test_addresses = ['cms.support@sas.dk']
prod_addresses = ['joakim.aven@sas.se','michael.almgren@sas.se','michael.visonj@sas.se', 'cms.support@sas.dk']

@argfix
def generate(*a, **k):
    """ Generating excel report """
    today = to_AbsTime(date.today())
    rows = generate_records()
    if rows:
       create_excel_report(rows, today)
       send_email(str(today)[0:9:])
    else:
        send_email("")
    files = []
    return files

def send_email(date):
    """ Sending the email to crew control """
    try:
        msg = MIMEMultipart()
        if os.environ.get("HOSTNAME") == "cweupcmssm01.sas.local":
           print "The environment is PROD"
           recipients = prod_addresses
           msg['Subject'] = "SVS_ACTIVE_ALERTS_{}".format(date)
           msg['From'] =  'cms-no-reply@sas.se'
        else:
            print "The environment is TEST or DEV"
            recipients = test_addresses
            msg['Subject'] = "TEST-SVS_ACTIVE_ALERTS_{}".format(date)
            msg['From'] =  'test-no-reply@sas.se'              
        msg['To'] = ",".join(recipients)
        msg['Cc'] = ''
        msg['Date'] = formatdate(localtime=True)
        file_name = "SVS_ACTIVE_ALERTS_{}.xlsx".format(date)
        file_source = os.path.join(samba_source, file_name)
        body = ("Dear All\n\n"
               "This mail contains the daily alert report for SVS in attachment\n\n"
               "Regards\n"
               "CMS Support Team")
        msg.attach(MIMEText(body + "\r\n\r\n"))
        msg.preamble = "Sent by carmadm"
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(file_source, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(os.path.basename(file_source)))
        msg.attach(part)
        s = SMTP('localhost', 25)
        s.sendmail( msg['From'], recipients, msg.as_string())
        s.quit()
    except Exception as e:
        log.debug('Daily_alert_report: Could not send email: {}'.format(e))

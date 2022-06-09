"""
Granted LOA report
"""
from salary.wfs.Approved_LOA_report import open_csv_file, create_excel_report, to_AbsTime
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
log = logging.getLogger('LOA_report')
log.setLevel(logging.DEBUG)

samba_source = '/samba-share/reports/LOA_report/'
categories = ['F', 'C']
"""cc_addresses = ['resource.cc.cph@sas.se', 'resource.cc.osl@sas.se', 'resource.cc.sto@sas.se']
fc_addresses = ['resource.fd.737.osl@sas.se ', 'resource.fd.737.sto@sas.se',
                'resource.fd.a2.cph@sas.se', 'resource.fd.a2.osl@sas.se',
                'resource.fd.a2.sto@sas.se', 'resource.fd.lh@sas.se', 'resource.fd.mff@sas.se']"""
cc_addresses = []
fc_addresses = []

@argfix
def generate(*a, **k):
    """ Generating excel report """
    today = to_AbsTime(date.today())
    #Possible to add more categories lates, i.e. C_SKD, F_SKS etc
    for category in categories:
        region = "All"
        rows = open_csv_file(today, today, region, category)
        if rows:
            create_excel_report(rows, today, today)
            send_email(str(today)[0:9:], category)
        else:
            send_email("", category)
    files = []
    return files

def send_email(date, category):
    """ Sending the email to planners """
    try:
        msg = MIMEMultipart()
        msg['Subject'] = 'Daily LOA report'
        msg['From'] =  'no-reply@sas.se'
        #Todo: email address based on category
        if category == 'C':
            recipients = cc_addresses
        else:
            recipients = fc_addresses
        
        msg['To'] = ",".join(recipients)
        msg['Cc'] = ''
        msg['Date'] = formatdate(localtime=True)
        if not date:
            body = "No LOA approved on this date"
            msg.attach(MIMEText(body+"\r\n\r\n"))
            msg.preamble = "Sent by carmadm"
        else:
            file_name = "LOA_report_{}.xlsx".format(date)
            file_source = os.path.join(samba_source, file_name)
            body = "This email contains the daily LOA report"
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
        log.debug('LOA_report: Could not send email: {}'.format(e))

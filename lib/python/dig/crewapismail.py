"""
Send CREW API report via mail:
"""

# imports ================================================================{{{1
import logging
import os
import sys
import shutil
from carmensystems.dig.framework import carmentime
from carmensystems.dig.framework.handler import MessageHandlerBase,CallNextHandlerResult
from carmensystems.dig.framework import dave
from carmensystems.dig.messagehandlers.dave import DaveContentType
from smtplib import SMTP
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
from datetime import date

logging.basicConfig()
log = logging.getLogger('apis_mail_report')
log.setLevel(logging.DEBUG)


# classes ================================================================{{{1

# CrewAPISMail ---------------------------------------------------------{{{2
class CrewAPISMail(MessageHandlerBase):
    """
    Comment.
    """
    def __init__(self, name=None):
        super(CrewAPISMail,self).__init__(name)
    
    def handle(self, message):
        self.send_email()        
        return CallNextHandlerResult()
 

    def send_email(self):
   
       try:
           to_addresses = ['arun.ayyadurai@sas.dk']
           cc_addresses = []
           recipients = to_addresses
           ignored = {"MAIL", "ARCHIVE", "OUTBOX"}
           report_source = "/opt/Carmen/CARMTMP/ftp/out/APIS_MAIL/OUTBOX/"
           mail_source = "/opt/Carmen/CARMTMP/ftp/out/APIS_MAIL/OUTBOX/MAIL/"
           mail_temp_source = "/opt/Carmen/CARMTMP/ftp/out/APIS_MAIL/OUTBOX/MAIL/ARCHIVE"
           dirs = [x for x in os.listdir(report_source) if x not in ignored]
           i = 0    
           for file in dirs:
               if i == 0:          
                 file1 = file.replace("_", " ").split()
                 subject = str(file1[0] + " " +  file1[1] + " " + file1[2] + " " + file1[3] + file1[4].lstrip('0') + " " + file1[5] + " "  + file1[6])   
                 file2 = file1[3] + file1[4].lstrip('0') + "_" + "crew" + "_" + file1[-1] + ".txt"
                 shutil.copy(os.path.join(report_source, file),  os.path.join(mail_source, file2))                                  
                 file_name = file2
                 mail_sending(subject,recipients,mail_source,file_name)
                 os.rename(os.path.join(mail_source, file_name),  os.path.join(mail_temp_source, file))                                    
               i = i + 1

       except Exception as e:
           log.debug('CREW_API: Could not send email: {}'.format(e))
         
    

def mail_sending(sub,rec,ml_source,fl_name):
    file_source = os.path.join(ml_source, fl_name)
    msg = MIMEMultipart()
    msg['From'] =  'sysmond_test@sas.dk'
    msg['To'] = ",".join(rec)
    msg['Cc'] = ''
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = str(sub)
    body = ""
    msg.attach(MIMEText(body + "\r\n\r\n"))
    msg.preamble = "Sent by carmadm"
    part = MIMEBase('application', "octet-stream")
    attachment = open(file_source, "rb")
    part.set_payload((attachment).read())
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(os.path.basename(file_source)))
    msg.attach(part)
    s = SMTP('localhost', 25)
    s.sendmail( msg['From'], rec, msg.as_string())
    s.quit()


      

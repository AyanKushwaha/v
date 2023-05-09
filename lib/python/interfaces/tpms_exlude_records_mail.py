import os
#import smtplib
from smtplib import SMTP
from datetime import date,time,datetime
from email import Encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate,COMMASPACE
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


sender_email= 'no-reply@sas.se' #''
sender_password=''
recipients_email=['STOOL.Archive@sas.dk','peter.yao@sas.se']
#subject='Exclude Records CSV File'
mail_body='This email contains a csv file attachment'


exclude_path = os.path.join(os.environ['CARMTMP'], 'ftp', 'exclude_records')
#timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
timestamp = datetime.now().strftime('%Y%m%d%H%M')
csv_filepath = (exclude_path + '/exclude_records_{}.csv'.format(timestamp))
csv_filename = '/exclude_records_{}.csv'.format(timestamp)
csv_file_source = os.path.join(exclude_path, csv_filename)

print(csv_filepath)
print(csv_filename)
print(csv_file_source)
# os.path.join(os.environ['CARMTMP'], 'ftp', 'exclude_records')
# create a MIME multipart message


def send_email():
    msg = MIMEMultipart()
    msg['Subject'] = 'Exclude Records CSV'
    msg['From'] = sender_email
    msg['To'] = ",".join(recipients_email)
    msg['Cc'] = ''
    msg['Date'] = formatdate(localtime=True)
    msg.attach(MIMEText(mail_body + "\r\n\r\n"))
    msg.preamble = 'Sent by CMS'

    with open(csv_filepath, 'rb') as csv_file:
        attached = MIMEBase('application', 'octet-stream')
        attached.set_payload(open(csv_filepath, 'rb').read())
        Encoders.encode_base64(attached)
        attached = MIMEApplication(csv_file.read(), _subtype='csv')
        attached.add_header('Content-Disposition', 'attachment; filename="{}"'.format(os.path.basename(csv_file_source)))
        #attached.add_header('Content-Disposition', 'attachment', filename= csv_filename)
        msg.attach(attached)
 

    server=SMTP('smtp.sas.local', 25)
    server.sendmail(sender_email, recipients_email, msg.as_string())
    server.quit()
    print('Email with CSV attachment sent successfully')

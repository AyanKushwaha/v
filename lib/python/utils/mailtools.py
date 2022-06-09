

"""
Utilities for sending mail from CMS using smtplib and MIME.
"""

import datetime
import smtplib

from email import Encoders
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from utils import ServiceConfig as C

__all__ = ['send_mail', 'mail']

sender = 'CMS@localhost'


def send_mail(filename, recipient, sender=sender, subject=None):
    """Send a text file given by 'filename' to 'address', which is an email
    address. The file will be attached to the email as a MIME attachment and
    also shown inline."""
    fp = open(filename, 'r')
    file_content = fp.read()
    fp.close()
    mpart = mime_message(recipient, file_content, sender, subject)
    b64 = MIMEBase('application', 'octet-stream')
    b64.set_payload(file_content)
    Encoders.encode_base64(b64)
    b64.add_header('Content-disposition', 'attachment', filename="%s_%s.txt" % (
        subject, datetime.datetime.now().strftime("%04Y-%02m-%02dT%02H%02M%02S")))
    mpart.attach(b64)
    mail(recipient, str(mpart), sender)


def mail(recipient, message, sender=sender):
    """Send a message using SMTP."""
    s = smtplib.SMTP()
    sc = C.ServiceConfig()
    s.connect(sc.getProperty("dig_settings/mail/host")[1], int(sc.getProperty("dig_settings/mail/port")[1]))
    s.sendmail(sender, recipient, message)
    s.quit()


def mime_message(recipient, message, sender=sender, subject=None):
    """Create a MIME-formatted message."""
    mpart = MIMEMultipart()
    if not subject is None:
        mpart['Subject'] = '[CMS] %s' % subject
    mpart['To'] = recipient
    mpart['From'] = sender
    mpart.preamble = "You need a MIME compatible mail reader."
    mtext = MIMEText(message)
    mtext.add_header('Content-disposition', 'inline')
    mpart.attach(mtext)
    return mpart


def send_mime_message(recipient, message, sender=sender, subject=None):
    """Send a text string in a MIME-formatted message."""
    msg = mime_message(recipient, message, sender, subject)
    mail(recipient, str(msg), sender)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

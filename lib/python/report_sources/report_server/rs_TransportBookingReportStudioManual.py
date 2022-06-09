#

#
"""
Transport Booking Report.
"""
from hotel_transport.TransportBookingRun import transportBookingRun
"""
global_dists = [
{'destination': 
[
('mail', 
{'attachmentName': '20180801.TransportForecast.ALL.AAL1-6.pdf', 
'to': 'mahdi@hiq.se, Henrik.Edholm@hiq.se', 
'mfrom': 'carmadm@sas.dk', 
'cc': 'Hawre.Aziz@hiq.se', 
'subject': 'Transport Forecast - ALL - AAL1'})
], 
'content-type': 'application/pdf', 
'content-location': '/opt/Carmen/CARMUSR/r24_sas67_live/current_carmdata/REPORTS/TRANSPORT/20180801.TransportForecast.ALL.AAL1-6.pdf'}
]
"""
global_transport_forecast_reports = []
"""
Entry point for the report server
"""
def generate(param):
    bookingUpdate = False
    forecast = False
    performed = False
    if isinstance(param,list):
        l,d = param
    else:
        d = param
    if d.has_key('forecast'):
        forecast = d['forecast'] == 'True'
    if d.has_key('bookingUpdate'):
        bookingUpdate = d['bookingUpdate'] == 'True'
    if d.has_key('performed'):
        performed = d['performed'] == 'True'
        
    # Generate Booking or Forecast reports
    reports = transportBookingRun(bookingUpdate=bookingUpdate,
                                  forecast=forecast,
                                  performed=performed)
    
    print "##############################"
    print reports
    print "##############################"
    return (reports, True) # True means delta is used



def send_emails():
    import sys, os
    from smtplib import SMTP
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEBase import MIMEBase
    from email.MIMEText import MIMEText
    from email.Utils import COMMASPACE, formatdate
    from email import Encoders

    if len(global_transport_forecast_reports) == 0:
        global global_transport_forecast_reports
        print "### Going to generte report and save it to global varible"
        global_transport_forecast_reports ,_delta = generate({'bookingUpdate': "False", 'performed': "False", 'forecast': "True"})
    dists = global_transport_forecast_reports
    print "### type dists) %s" % str(type(dists))
    print "### len distinations: %d" % len(dists)
    for d in dists:
        for sending_method, md in d["destination"]:
            if sending_method == 'mail':
                msg = MIMEMultipart()
                msg['Subject'] = md["subject"]
                msg['From'] = md["mfrom"]
                msg['To'] = md["to"]
                msg_to = md["to"].split(',')
                if md.has_key('cc') and len(md["cc"]) > 0:
                    msg_to.append(md["cc"].split(','))
                    msg['Cc'] = md["cc"]
                else:
                    msg['Cc'] = ""
                msg['Date'] = formatdate(localtime=True) 
                body = "This email contains transport forecast report"
                msg.attach(MIMEText(body+"\r\n\r\n"))
                msg.preamble = "Sended by carmadm"
                part = MIMEBase('application', "pdf")
                part.set_payload(open(d["content-location"],"rb").read())
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="%s"' % (md["attachmentName"]))
                msg.attach(part)
                s = SMTP('localhost', 25)
                s.sendmail( msg['From'], msg_to, msg.as_string())
                s.quit()
                print msg['From'] + " " + msg['To'] + msg['Cc'] 
            else:
               print "### Sending method is not email and should be sent by: " + sending_method
    print "### Emails has been send"



send_emails()


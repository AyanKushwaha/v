#! /usr/bin/env python

from __future__ import print_function

import sys, os
import subprocess
from smtplib import SMTP                                                                                                                       
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

# First create folder to copy all Perdiem pdf file there.
# Then: find /opt/Carmen/CARMUSR/r22_sas48_user/current_carmdata/REPORTS/SALARY_REPORTS/ -name 'PerDiemStm*' -type d -ctime -1 | grep "8099\|8102\|8183\|8101\|8100" | xargs -I item cp -r item PerDiemStmt_resend_2017-05-18_13-13-58
# then: find . -name "*.pdf" -exec mv /opt/Carmen/CARMUSR/r22_sas48_user/current_carmdata/REPORTS/SALARY_REPORTS/PerDiemStmt_resend_2017-05-18_13-13-58/ {} \;
# then: rm -R PerDiemStm*
def run():
	# path = "/home/mahdiab/Downloads/scripts/"
	#  path = "/tmp/"
	#  path = "/opt/Carmen/CARMUSR/r22_sas48_user/current_carmdata/REPORTS/SALARY_REPORTS/PerDiemStmt_resend_2017-05-18_13-13-58/"

	id_months = [(10106, 'April 2017'),
		     (10109, 'May 2017'),
		     (10112, 'June 2017'),
		     (10115, 'July 2017'),
		     (10118, 'August 2017'),
		     (10134, 'December 2017')]
	sites = ['OSL', 'SVG', 'TRD']

	send = False

	for id, month in id_months:
		for site in sites:
			cmd = ["find", "/opt/Carmen/CARMDATA/carmdata_cms2/REPORTS/SALARY_REPORTS", "-type", "d", "-name", "PerDiemStmt_%08d_%s_*" % (id, site)]
			print("Command: %s" % cmd)
			p = subprocess.Popen(cmd,
					     stdout=subprocess.PIPE,
					     stderr=subprocess.PIPE)
			out, err = p.communicate()
			print(out)
			print(err)
			paths = out.rstrip('\n').split('\n')
			print(paths)

			for path in paths:
				print("Path:",path)
				files = []
				for f in os.listdir(path):
					if f.endswith('.pdf'):
						files.append(f)
				#  print (files)
				for f in files:
					cid = f.split('.')[0]
					# print(cid)
					#  exit(1)
					runtype = "Per Diem"
					msg = MIMEMultipart()
					msg['Subject'] = "PerDiem Statement %s - DO NOT REPLY" % month
					msg['From'] = "carmadm@carmen.se"
					msg['To'] = "%s@sas.dk" % cid
					if cid == '':
						send = True
					#msg['To'] = "christer.gustavsson@hiq.se "# TODO: add users
					msg['Date'] = formatdate(localtime=True) 
					body = "This email contains a Per Diem report"
					msg.attach(MIMEText(body+"\r\n\r\n"))
					msg.preamble = "Sent by carmadm"
					part = MIMEBase('application', "pdf")
					part.set_payload(open(os.path.join(path, "%s.pdf" % cid),"rb").read())
					Encoders.encode_base64(part)
					part.add_header('Content-Disposition', 'attachment; filename="%s_%s.pdf"' % (runtype, cid))
					msg.attach(part)
					if send:
						try:
							s = SMTP('localhost', 25)
							s.sendmail( msg['From'],  msg['To'], msg.as_string())
							s.quit()
						except:
							print("ERROR: Could not send!!!")
					else:
						print("Skipping send!")
					print( msg['From'],  msg['To'], msg['Subject'])
					print ("Email has been sent")



if __name__ == "__main__":
	run()

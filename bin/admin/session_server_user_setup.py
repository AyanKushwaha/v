#!/usr/bin/env python 

#  from __future__ import print_function

__author__="Mahdi Abdinejadi <mahdi.abdinejadi@hiq.se>"
__version__= "0.3"


"""
Simple Carmen Session server configuration xml file modifier
"""

import os
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
#  import xml.etree.ElementTree as ET
from lxml import etree
import logging

#  carmuser = "SAS56"

def run():
	success = False
	ap = ArgumentParser(description=__doc__, formatter_class=RawDescriptionHelpFormatter)
	gp = ap.add_mutually_exclusive_group()

	gp.add_argument('-a', '--add', default=False, action='store_true', help='Add carmuser to session server configuration file')
	gp.add_argument('-r', '--remove', default=False, action='store_true', help='Set old carmuser name to be removed from systems.xml')
	ap.add_argument('-s', '--systemname', help='Set the carm system name  variable to PROD, PROD_HISTORY, PROD_TEST,CMSDEV and default is $CARMSYSTEMNAME')
	ap.add_argument('-l', '--livefeed', default=False, action='store_true', help='Attach livefeed suffix to user and update old one')
	ap.add_argument('-n', '--name', default="NotExists", help='Set the name of session server carmuser default is to $CARMUSR folder')
	ap.add_argument('-c', '--carmuser', help='Set the carmuser to be add or removed Default is environment variable $CARMUSER')
	ap.add_argument('-f', '--xmlfile', help='Set Session server configuration xml file')
	ap.add_argument('-v', '--verbose', default=False, action='store_true', help='Set logging to verbose (debug level)')
	args = ap.parse_args()

	if args.verbose:
		logging.basicConfig(format="%(filename)s %(levelname)-8s: %(message)s", level=logging.DEBUG)
	else:
		logging.basicConfig(format="%(filename)s %(levelname)-8s: %(message)s", level=logging.INFO)

	if args.carmuser:
		carmuser = args.carmuser
	else:
		try:
			carmuser = os.path.basename(os.environ["CARMUSR"])
		except KeyError as ke:
			logging.error("Please set carmuser argument or run cmsshell to CARMUSR environment variable set")
			exit(1)
		except Exception as e:
			logging.error("Unexpected error carmuser! " + str(e))
			exit(1)


	if args.add:
		if args.systemname and args.systemname.upper() in ["PROD", "PROD_HISTORY", "PROD_TEST", "CMSDEV"]:
			carmsystemname = args.systemname.upper()
		else:
			try:
				carmsystemname = os.environ["CARMSYSTEMNAME"]
			except KeyError as ke:
				logging.error("Please set systemname variable argument or run cmsshell to CARMSYSTEMNAME environment variable set")
				exit(1)
			except Exception as e:
				logging.error("Unexpected error setting carmsystemname! " + str(e) )

	#  carmuser_upper = carmuser.upper()
	#  config_file = "/opt/Carmen/SessionServer/bin/user/systems.xml"
	#  config_file="systems.xml"
	config_file = ""
	if args.xmlfile:
		config_file = args.xmlfile
		logging.debug("config_file is set to: " + config_file)
	else:

		try:
			if os.path.isfile("/opt/Carmen/SessionServer/user/etc/systems.xml"):
				config_file = "/opt/Carmen/SessionServer/user/etc/systems.xml"
			if os.getenv("CARMSYSTEMNAME") in ["PROD_TEST", "CMSDEV" ] and \
					os.path.isfile("/opt/Carmen/SessionServer/user/etc/systems.xml"):
						config_file = "/opt/Carmen/SessionServer/user/etc/systems.xml"
		except KeyError as ke:
			logging.error("Please set CARMSYSTEMNAME variable or run cmsshell to get systemname variable set")
			exit(1)
		except Exception:
			exit(1)

	if config_file == "":
		logging.error("Please set the session sever config xml file")
		exit(1)
	else:
		logging.debug("config_file is set to: " + config_file)

	tree = etree.parse(config_file)
	root = tree.getroot()
	success = False
	for sys in root.findall('system'):
		if sys.findall('CARMUSR')[0].text == carmuser or \
			sys.findall('CARMUSR')[0].text.split('/')[-1] == carmuser or \
			sys.get('name') == args.name.upper() or sys.get('name') == args.name.upper() + "_LIVEFEED" :
			removed_result = remove_carmuser(root,sys)
			if args.remove:
				success = removed_result
				break
	if args.add:
		for sys in root.findall('system'):
			if carmuser not in [ x.text for x in sys.findall('CARMUSR')]:
				if args.name and args.name != "NotExists":
					success = add_carmuser(root, carmuser, carmsystemname, args.livefeed, args.name )
				else:
					success = add_carmuser(root, carmuser, carmsystemname, args.livefeed)
				break
			else:
				success = True # Carmuser is already added
		#  print "Not yet get the Carmuser"
	if not success:
		logging.info("Did not add or remove the carmuser in session server config file at: " +  config_file)
		exit(0)
	else:
		logging.info("Successfully modified session server config file at: " + config_file)
	tree.write(config_file,xml_declaration=True,encoding="ISO-8859-1", pretty_print=True)
	logging.debug("XML file is produced at: " + config_file)


def remove_carmuser(root, sys):
	#  logging.debug("Got a remove command to remove: " + str(sys))
	root.remove(sys)
	logging.debug("Removed xml element" + str(sys))
	return True

def add_carmuser(root, carmuser, carmsystemname, livefeed, name=""):
    if not name or name == "":
        name = carmuser.split("/")[-1]
    if livefeed: 
        if carmsystemname in ["PROD", "PROD_HISTORY"]:
            logging.debug("Adding _LIVEFEED suffix in PROD or PROD_HISTORY is not allowed")
        else:
		    name += "_LIVEFEED"
	logging.debug("XML element name is: " + name)
	sys = """
<system name="{0}">
  <CARMUSR>/opt/Carmen/CARMUSR/{1}</CARMUSR>
  <CARMDATA>/opt/Carmen/CARMUSR/{1}/current_carmdata</CARMDATA>
  <CARMTMP>/opt/Carmen/CARMUSR/{1}/current_carmtmp_cct</CARMTMP>
  <CARMSYS>/opt/Carmen/CARMUSR/{1}/current_carmsys_cct</CARMSYS>
  <CARMSYSTEMNAME>{2}</CARMSYSTEMNAME>
  <CARMROLE>Administrator</CARMROLE>
  <CARMSGE>-l studioHost</CARMSGE>
</system>

""".format(name.upper(), carmuser, carmsystemname)
	et_sys = etree.fromstring(sys)
	root.append(et_sys)
	logging.debug("Added the following xml element to root \n" + sys)
	return True


if '__name__' != '__main__':
    run()
    exit(0)


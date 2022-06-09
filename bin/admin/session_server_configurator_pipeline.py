#!/usr/bin/env python 

__author__="Ralf Damaschke, Mahdi Abdinejadi"
__version__= "0.4"


"""
This script modifies the Session Server user configuration XML file on deployment via the Azure DevOps pipeline
"""

import os
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from lxml import etree
import logging

def run():
    args = get_args()
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(args.xmlfile, parser)
    root = tree.getroot()
    # Removing older deployments of same major version
    for sys in root.findall("system"):
        if args.major in sys.get("name"):
            root.remove(sys)
            logging.debug("Removed system " + sys.get("name"))
    add_system(root, args.path, args.environment, args.livefeed, args.major + "_" + args.minor)
    tree.write(args.xmlfile, xml_declaration=True,encoding="ISO-8859-1", pretty_print=True)
    logging.info("Successfully modified Session Server config file at: " + args.xmlfile)


def get_args():
    ap = ArgumentParser(description=__doc__, formatter_class=RawDescriptionHelpFormatter)
    ap.add_argument('-m', '--major', required=True, help='Major version of the deployment')
    ap.add_argument('-n', '--minor', required=True, help='Minor version of the deployment')
    ap.add_argument('-e', '--environment', help='The value to be assigned to the CARMSYSTEMNAME variable (e.g., PROD, PROD_TEST, etc.). Default is $CARMSYSTEMNAME')
    ap.add_argument('-l', '--livefeed', action='store_true', help='Attach livefeed suffix to user and update old one')
    ap.add_argument('-p', '--path', help='The path of the deployment. Default is $CARMUSR')
    ap.add_argument('-f', '--xmlfile', help='Path of Session server configuration XML file to be modified. Default is /opt/Carmen/SessionServer/user/etc/systems.xml')
    ap.add_argument('-v', '--verbose', action='store_true', help='Set logging to verbose (debug level)')
    args = ap.parse_args()

    if args.verbose:
        logging.basicConfig(format="%(filename)s %(levelname)-8s: %(message)s", level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(filename)s %(levelname)-8s: %(message)s", level=logging.INFO)

    args.major = args.major.upper()

    if not args.path:
        try:
            args.path = os.path.basename(os.environ["CARMUSR"])
        except KeyError as ke:
            logging.error("Please set path argument or run cmsshell to set CARMUSR environment variable")
            exit(1)
        except Exception as e:
            logging.error("Unexpected exception when trying to retrieve deployment path! " + str(e))
            exit(1)

    if args.environment and args.environment.upper() in ["PROD", "PROD_HISTORY", "PROD_TEST", "CMSDEV"]:
        args.environment = args.environment.upper()
    else:
        try:
            args.environment = os.environ["CARMSYSTEMNAME"].upper()
        except KeyError as ke:
            logging.error("Please set environment variable argument or run cmsshell to CARMSYSTEMNAME environment variable set")
            exit(1)
        except Exception as e:
            logging.error("Unexpected error setting carmsystemname! " + str(e) )

    if not args.xmlfile:
        try:
            if os.path.isfile("/opt/Carmen/SessionServer/user/etc/systems.xml"):
                args.xmlfile = "/opt/Carmen/SessionServer/user/etc/systems.xml"
        except KeyError as ke:
            logging.error("Session Server configuration XML file not found at default location. Please set xmlfile argument.")
            exit(1)
        except Exception:
            exit(1)

    return args     


def add_system(root, path, carmsystemname, livefeed, name):
    logging.debug("About to add new system")
    if not name:
        name = path.split("/")[-1]
    if livefeed: 
        if carmsystemname in ["PROD", "PROD_HISTORY"]:
            logging.debug("Adding _LIVEFEED suffix in PROD or PROD_HISTORY is not allowed")
        else:
            name += "_SPLT"
    logging.debug("XML element name is: " + name)
    sys = """
<system name="{0}">
  <CARMUSR>{1}</CARMUSR>
  <CARMDATA>{1}/current_carmdata</CARMDATA>
  <CARMTMP>{1}/current_carmtmp_cct</CARMTMP>
  <CARMSYS>{1}/current_carmsys_cct</CARMSYS>
  <CARMSYSTEMNAME>{2}</CARMSYSTEMNAME>
  <CARMROLE>Administrator</CARMROLE>
  <CARMSGE>-l studioHost</CARMSGE>
</system>

""".format(name.upper(), path, carmsystemname)
    et_sys = etree.fromstring(sys)
    root.insert(1, et_sys) # New sys should be at the top, after the include tag
    logging.debug("Added the following xml element to root \n" + sys)


if '__name__' != '__main__':
    run()
    exit(0)


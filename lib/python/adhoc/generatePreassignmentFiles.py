"""
Depending on the report servers running, this script will generate xml files for each crew which will show their fixed patterns
Usage:
    bin/startMirador.sh --script -s adhoc.generatePreassignmentFiles

"""

import sys, os, time
from tm import TM
from carmensystems.common.ServiceConfig import ServiceConfig
import traceback
from AbsTime import AbsTime
import xmlrpclib


class BaseError(Exception):
    pass

class TaskNameUpdater(object):
    def __init__(self, schema, dburl):
        self._schema = str(schema)
        self._dburl = str(dburl)
        self.now = AbsTime(time.strftime('%d%b%Y %H:%M', time.gmtime()))

    def connect(self):
        """
        Creates and opens connection to a DAVE database
        """
        sys.stdout.write("Connecting to url = %s, schema = %s ..." % (self._dburl, self._schema))
        TM.connect(self._dburl, self._schema, '')
        TM.loadSchema()
        sys.stdout.write(" ...Connected!\n")

    def __del__(self):
        """
        Closes down connections to the DAVE database
        """
        sys.stdout.write("Closing down database connection ...")
        TM.disconnect()
        sys.stdout.write(" Done!\n")


    def _getCrewRank(self, table, crew_id):
        """
        Returns the crew rank today
        """
        for entry in table.search('(crew=%s)'%crew_id):
            if self.now >= entry.validfrom and self.now < entry.validto:
                return entry.crewrank.maincat.id
        return None


    def run(self):
        self.connect()
        print "Loading tables"
        TM(["crew"])
        TM(["crew_employment"])
        TM.newState()

        print "Running.."

        config = ServiceConfig()
        cp_latest = config.getServiceUrl('cp_latest')
        cp_latest = cp_latest.rsplit('/', 1)[0]

        print "Connecting to cp_latest=%s" % cp_latest
        service = xmlrpclib.ServerProxy(cp_latest)

        directory = os.path.join(os.environ['CARMDATA'],
                                 'crewportal',
                                 'datasource',
                                 'preassignments')
        if not os.path.exists(directory):
            os.makedirs(directory)

        for row in [_ for _ in TM.crew]:
            try:
                rank = self._getCrewRank(TM.crew_employment, row.id)
                if rank == None:
                    print "Crew not found! %s" % row.id
                    continue

                fileloc = os.path.join(directory, row.id)

                xml_request = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><getRosterCarryoutParameters biddingCrewId="%s" authenticatedCrewId="automatic" id="automatic" xmlns="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getrostercarryout"/>' % row.id

                print "Generating preassignment file for %s" % row.id
                data = service.get_roster_carryout(xml_request)
                filename = open(fileloc, 'w')
                print >> filename, data
                filename.close()

            except Exception, edata:
                print "\n Error : %s %s\n%s" % (row.id, row.name, edata)
                raise

        print "Done, exiting..."


def usage():
    print __doc__


def main():
    db_url = os.environ["DB_URL"]
    schema = os.environ["SCHEMA"]

    updater_object = TaskNameUpdater(schema, db_url)
    updater_object.run()
    del updater_object

main()

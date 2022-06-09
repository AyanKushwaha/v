"""
Depending on the report servers running, this script will generate xml files for each crew which will show their fixed patterns
Usage:
    bin/startMirador.sh --manpower --script -s adhoc.generateFixedPatternFiles

"""
__verision__ = "$Revision$"
__author__ = "Berkay Beygo, Jeppesen"

import sys, os, time
from tm import TM
from carmensystems.common.ServiceConfig import ServiceConfig
import traceback
from AbsTime import AbsTime

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
        server_f = ""
        server_c = ""
        # for (_service, _process, _host, _url) in config.getServices():
        #    if _service == 'portal_manpower_f':
        #        server_f = _url
        #    if _service == 'portal_manpower_c':
        #        server_c = _url
                
        server_f = config.getServiceUrl('portal_manpower_f')
        server_c = config.getServiceUrl('portal_manpower_c')
                
        server_f = server_f.rsplit('/',1)[0]
        server_c = server_c.rsplit('/',1)[0]      
        
        import xmlrpclib
        print "Connecting to portal_manpower_f=%s, portal_manpower_c=%s"%(server_f, server_c)
        service_f = xmlrpclib.ServerProxy(server_f)
        service_c = xmlrpclib.ServerProxy(server_c)

        dir = os.path.join(os.environ['CARMDATA'],
                           'crewportal',
                           'datasource',
                           'fixed_pattern')
        if not os.path.exists(dir):
            os.makedirs(dir)
        
        for row in [_ for _ in TM.crew]:
            try:
                rank = self._getCrewRank(TM.crew_employment, row.id)
                if (rank == None):
                    print "Crew not found! %s", row.id
                    continue

                fileloc = os.path.join(dir, row.id)
                
                xml_request = '<?xml version="1.0" encoding="UTF-8"?><jmp:getAssignmentsRequest authenticatedCrewId="automatic" biddingCrewId="%s" id="automatic" xmlns:jmp="http://carmen.jeppesen.com/bids/backendcommunication/jmp/v2"/>'%(row.id)

                if(rank == 'C'):
                    print "Generating fixed_pattern_file for C..", row.id
                    z = service_c.carmensystems.manpower.bids.jmp_get_assignments(xml_request)
                    filename = open (fileloc, 'w')
                    print >> filename, z
                    filename.close()
                if(rank == 'F'):
                    print "Generating fixed_pattern_file for F..", row.id
                    z = service_f.carmensystems.manpower.bids.jmp_get_assignments(xml_request)
                    filename = open (fileloc, 'w')
                    print >> filename, z
                    filename.close()
                    
            except Exception, e:
                traceback.print_exc()
                print "\n Error :", row.name, e
                pass
        
        print "Done, exiting..."
        
def usage():
    print __doc__

def main(args):
    db_url = os.environ["DB_URL"]
    schema = os.environ["SCHEMA"]

    updaterObj = TaskNameUpdater(schema, db_url)
    updaterObj.run()
    del updaterObj

main(sys.argv)

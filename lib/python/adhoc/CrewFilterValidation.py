
"""
This script will change departure and arrivals for all vacations to crews station

Usage:
    bin/startMirador.sh --manpower --script -s adhoc.CrewFilterValidation

"""
__verision__ = "$Revision$"
__author__ = "Max Franklin, Jeppesen"

import sys, os
from tm import TM
from carmensystems.manpower.private.util.crew_filter import CrewFilter
from carmensystems.manpower.util.system import StaticAdvice
from carmensystems.manpower.util.crew_filter_sub_definition import CrewFilterSubPartDefinition
from carmusr.manpower.general_api_sas import GeneralApiSas

class MyCrewFilter(CrewFilter):

    @staticmethod
    def getSubPartDefinition(proceed):
        g = GeneralApiSas()
        return g.crewFilterGetSubDefinition()

CrewFilter.getSubPartDefinition = StaticAdvice(CrewFilter.getSubPartDefinition, MyCrewFilter.getSubPartDefinition)

class CrewFilterValidation(object):
    def __init__(self, schema, dburl):
        self._schema = str(schema)
        self._dburl = str(dburl)


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
    
    def run(self):
        self.connect()

        print "Loading tables"
        TM(["crew_filter"])
        TM.newState()

        print "####### Analyzing crew filters #######"
        empCount=0
        baseNotFound=0
        crewDict={}
        for row in TM.crew_filter:
            try:
                text = CrewFilter(TM, (row.name, row.cat)).CheckFilterValue()
                if text:
                    print row.selvalue
                    print text, "\n"
            except Exception, e:
                print "error with: ", row.selvalue, e
                raise
        print "#######################################"

def usage():
    print __doc__

def main(args):
    db_url = os.environ["DB_URL"]
    schema = os.environ["SCHEMA"]

    fixer = CrewFilterValidation(schema, db_url)
    fixer.run()
    del fixer

main(sys.argv)

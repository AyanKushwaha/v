
"""
This script will find and delete all optional base variants where the main kernel is missing.
If the main kernel is missing studio will have severe stability issues.

Usage:
    mirador -s adhoc.OptRemover <schema> <dburl> <fromdate> <todate>

"""
__verision__ = "$Revision$"
__author__ = "Christoffer Sandberg, Jeppesen"

import os, sys, time
from tm import TM
import AbsTime
import RelTime
import AbsDate
from carmensystems.dave import dmf  
import Errlog
from optparse import OptionParser

class OptRemover:
    def __init__(self, schema, dburl, from_time, to_time, commit=True):
        self._schema = str(schema)
        self._dburl = str(dburl)
        self._entityConn = None
        self._conn = None
        self._trip_start = from_time
        self._trip_end = to_time
        self._dbPeriodStart = self._trip_start
        self._dbPeriodEnd = self._trip_end
        self._threeyrsbefstart = self._dbPeriodStart - RelTime.RelTime(3*366*24*60)
        self._oneyrbefstart = self._dbPeriodStart - RelTime.RelTime(366*24*60)
        self._threemonthsbefstart = self._dbPeriodStart - RelTime.RelTime(3*30*1440)
        self._threemonthsafterend = self._dbPeriodEnd + RelTime.RelTime(3*30*1440)
        max_trip_length = 5
        max_number_of_days_with_optional_variant_deadheads_before_trip = 1
        self._period_trip_start = self._dbPeriodStart - RelTime.RelTime(max_trip_length*1440)
        self._period_trip_end = self._dbPeriodEnd + RelTime.RelTime(max_number_of_days_with_optional_variant_deadheads_before_trip*1440)
        self._leg_start = self._period_trip_start - RelTime.RelTime(max_number_of_days_with_optional_variant_deadheads_before_trip*1440)
        self._leg_end = self._period_trip_end + RelTime.RelTime(max_trip_length*1440)
        self._commit = commit

    def connect(self):
        """
        Creates and opens connection to a DAVE database
        """
        sys.stdout.write("Connecting to url = %s, schema = %s ..." % (self._dburl, self._schema))
        TM.connect(self._dburl, self._schema, '')
        TM.loadSchema()
        self._entityConn = dmf.EntityConnection()
        self._entityConn.open(self._dburl, self._schema)
        self._conn = dmf.Connection(self._dburl)
        sys.stdout.write(" ...Connected!\n")

    def __del__(self):
        """
        Closes down connections to the DAVE database
        """
        sys.stdout.write("Closing down database connection ...")
        self._entityConn.close()
        self._conn.close()
        TM.disconnect()
        sys.stdout.write(" Done!\n")

    def run(self):
        self.connect()

        param_filters = [("period", "start", str(self._dbPeriodStart)[0:9]),
                         ("period", "end", str(self._dbPeriodEnd)[0:9]),
                         ("period", "start_time", str(self._dbPeriodStart)),
                         ("period", "end_time", str(self._dbPeriodEnd)),
                         ("period", "threeyrsbefstart", str(self._threeyrsbefstart)),
                         ("period", "oneyrbefstart", str(self._oneyrbefstart)),
                         ("period", "threemonthsbefstart", str(self._threemonthsbefstart)),
                         ("period", "threemonthsafterend", str(self._threemonthsafterend)),
                         ("period", "trip_start", str(self._period_trip_start)),
                         ("period", "trip_end", str(self._period_trip_end)),
                         ("period", "leg_start", str(self._leg_start)),
                         ("period", "leg_end", str(self._leg_end))]

        for (selection, param, value) in param_filters:
            Errlog.log("\t Setting Filter: %s.%s = %s" % (selection, param, value))
            TM.addSelection(selection, param, value)

        Errlog.log("Loading tables...")
        TM(["trip", "trip_flight_duty", "trip_ground_duty", "trip_activity", "crew_base_set"])
        TM.newState()
        Errlog.log("Done Loading tables")

        Errlog.log("Working on trips")

        trips_to_remove = []
        legs_to_remove = []

        # Simple algorithm, find entities in trip, which only consists of elements with '-' as base
        # These are from a studio perspective broken, and needs to be removed

        for trip in TM.trip:
            # Only evaluate on trips that can have optional variants
            if not trip.optionalvariant:
                continue
            have_opt = False
            have_krn = False
            legs = []
            for row in trip.referers('trip_flight_duty', 'trip'):
                legs.append(row)
                if str(row.getRefI('base')) == '-':
                    have_krn = True
                    break
                else:
                    have_opt = True

            # This trip have a kernel, we can stop here
            if have_krn:
                continue

            for row in trip.referers('trip_ground_duty', 'trip'):
                legs.append(row)
                if str(row.getRefI('base')) == '-':
                    have_krn = True
                    break
                else:
                    have_opt = True
                    
            if not have_krn and have_opt:
                trips_to_remove.append(trip)
                legs_to_remove.extend(legs)



        for row in trips_to_remove:
            Errlog.log("%s remove the following TRIP: %s " % (('Would','Will')[self._commit], str(row)))
            if self._commit:
                row.remove()
        for row in legs_to_remove:
            Errlog.log("%s remove the following TRIP LEG: %s " % (('Would','Will')[self._commit], str(row)))
            if self._commit:
                row.remove()

        if self._commit:
            Errlog.log("Saving to databse...")
            TM.save()
            Errlog.log("... Done")

        Errlog.log("Done, exiting")


if __name__ == 'carmusr.OptRemover':
    usage = " %prog --connect $DB_URL --schema $DB_SCHEMA [--no-commit] <from date> <to date>\n  --connect and --schema are mandatory."
    parser = OptionParser(usage=usage)
    parser.add_option('-c', '--connect', 
            dest="connect", 
            help="Database connect string.")
    parser.add_option('-s', '--schema', 
            dest="schema", 
            help="Database schema string.")
    parser.add_option('-n', '--no-commit', 
            dest="commit",
            action="store_false",
            default=True,
            help="Don't commit any changes to database.")
    opts, args = parser.parse_args(list(sys.argv[1:]))

    if len(args) != 2:
        parser.error("Two few arguments, need <from-date> and <to-date>")

    if opts.schema is None:
        parser.error("Must supply option 'schema'.")
    if opts.connect is None:
        parser.error("Must supply option 'connect'.")
    try:
        from_time = AbsTime.AbsTime(args[0])
    except:
        parser.error("The 'from-date' argument is in wrong format, should be DDMonthYYYY.")
    try:
        to_time = AbsTime.AbsTime(args[1])
    except:
        parser.error("The 'to-date' argument is in wrong format, should be DDMonthYYYY.")

    if from_time >= to_time:
        parser.error("'to-date' needs to be greater than 'from-date'")

    remover = OptRemover(schema=opts.schema,dburl=opts.connect,
                         from_time = from_time, to_time = to_time,
                         commit=opts.commit)
    remover.run()
    del remover


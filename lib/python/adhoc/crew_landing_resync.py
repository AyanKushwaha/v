

"""
Resync a date intervall to match a migrated file of crew landings.
There will be a 3 day gap due to datamigration, this script fixes that.
"""

import logging
import os
import sys
from optparse import OptionParser

import tm
import modelserver


from AbsTime import AbsTime
from AbsDate import AbsDate

from Etab import Etable

from utils.dave import EC, RW


logging.basicConfig()
log = logging.getLogger('crew_landing_resync')

## 7
## Sleg_fd         ? "Crew_act_log  fltid",
## Aleg_udor       ? "Crew_act_log origdate",
## Sleg_adep       ? "Dated_flt_leg stncdfr",
## Screw           ? "Crew_act_log perkey",
## Sairport        ? "Dated_flt_leg stncdto",
## Inr_landings    ? "Crew_act_log landings",
## Bactiv          ? "Y when landings>=1 ellers N",

class MyIter:
    class Record:
        def __init__(self, parent, row):
            self.leg_udor = row[parent.coldict['leg_udor']]
            self.leg_fd = row[parent.coldict['leg_fd']]
            self.leg_adep = row[parent.coldict['leg_adep']]
            self.crew = row[parent.coldict['crew']]
            self.airport = row[parent.coldict['airport']]
            self.nr_landings = row[parent.coldict['nr_landings']]
            self.activ = row[parent.coldict['activ']]

        def __str__(self):
            return "Udor %s, FD %s, Adep %s, Crew %s, Airport %s, Activ %s, nr_landings %s" %(
                self.leg_udor, self.leg_fd, self.leg_adep, self.crew, self.airport, self.activ, self.nr_landings)

    def __init__(self, etab):
        self.etab = etab
        self.coldict = {}
        for col in ('leg_udor', 'leg_adep', 'leg_fd', 'crew', 'airport',
                    'nr_landings', 'activ'):
            self.coldict[col] = etab.getColumnPos(col) - 1

    def __iter__(self):
        for row in self.etab:
            yield self.Record(self, row)




class CrewLandingSync(object):
    def __init__(self, dburl, schema):
        self._dburl = dburl
        self._schema = schema
        self.TM = tm.TMC(self._dburl, self._schema)

    #@param String etable_location Path to etab file
    #@param AbsTime fromDate Inclusive 'fromdate', as an AbsTime
    #@param AbsTime toDate Inclusive 'todate', as an AbsTime
    def run(self, etable_location, fromDate, toDate):
        
        # Activate DAVE filters
        filter_params = [("period_crew_landing", "start", str(fromDate)[0:9]),
                         ("period_crew_landing", "end", str(toDate)[0:9]),
                         ("period_crew_landing", "start_time", str(fromDate)),
                         ("period_crew_landing", "end_time", str(toDate)),
                         ("period_flight_leg", "start", str(fromDate)[0:9]),
                         ("period_flight_leg", "end", str(toDate)[0:9]),
                         ("period_flight_leg", "start_time", str(fromDate)),
                         ("period_flight_leg", "end_time", str(toDate))]
        for (selection, param, value) in filter_params:
            print "Setting Filter: %s.%s = %s" % (selection, param, value) 
            self.TM.addSelection(selection, param, value)

        # Create etab iterator
        path = os.path.join('.', etable_location)
        etab = Etable(path)
        etab_iterator = MyIter(etab)
        print "Created etable iterator for: %s" % (path)

        outside_filter = 0
        missing_flight = 0
        missing_crew = 0
        changed = 0
        added = 0


        startDate = AbsDate(fromDate)
        endDate = AbsDate(toDate)

        tables = ['crew','crew_landing', 'flight_leg', 'airport']
        self.TM(tables)
        self.TM.newState()

        for row in etab_iterator:
            not_added = True # Just for counting.. ugly
            
            # See if we are inside out period
            leg_udor = AbsDate(row.leg_udor)
            if leg_udor>endDate or leg_udor<startDate:
                outside_filter+=1
                continue

            # See if the record exists
            adep = self.TM.airport[(row.leg_adep,)]
            apt =  self.TM.airport[(row.airport,)]

            try:
                crew = self.TM.crew[(row.crew,)]
            except modelserver.EntityNotFoundError:
                missing_crew += 1
                continue    

            try:
                flight = self.TM.flight_leg[(AbsTime(leg_udor), row.leg_fd, adep)]
            except modelserver.EntityNotFoundError:
                print "Missing flight %s from %s on %s, ignoring. All values; %s" % (row.leg_fd, adep.id, leg_udor, row)
                missing_flight += 1
                continue

            try:
                rec = self.TM.crew_landing[(flight, crew, apt)]
            except modelserver.EntityNotFoundError:
                rec = self.TM.crew_landing.create((flight, crew, apt))
                added += 1
                not_added = False

            rec.activ = row.activ == 'Y'
            rec.nr_landings = int(row.nr_landings)
            if not_added:
             changed += 1



        print "Updated           %d" % (changed)
        print "Added             %d" % (added)
        print "Outside of filter %d" % (outside_filter)
        print "Missing flight    %d" % (missing_flight)
        print "Missing crew      %d" % (missing_crew)

        print "Saving"
        self.TM.save()
        print "Save done"
        

if __name__ == 'adhoc.crew_landing_resync':
    parser = OptionParser()
    parser.add_option('-c', '--connect', 
            dest="connect", 
            help="Database connect string.")
    parser.add_option('-s', '--schema', 
            dest="schema", 
            help="Database schema string.")
    opts, args = parser.parse_args(list(sys.argv[1:]))

    if opts.schema is None:
        parser.error("Must supply option 'schema'.")
    if opts.connect is None:
        parser.error("Must supply option 'connect'.")

    if len(args) != 3:
        parser.error("Must supply three arguments: file, fromdate, todate")


    table = args[0]
    fromDate = AbsTime(args[1])
    toDate = AbsTime(args[2])

    print "Table: %s, from: %s, to: %s" % (table, fromDate, toDate)

    updater = CrewLandingSync(opts.connect, opts.schema)
    updater.run(table, fromDate, toDate)
    del updater

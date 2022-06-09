##################################################33
#

#
# Created:
#  Jonas Carlsson, Jeppesen, January 2006
#
"""
Production Move Info report

This report lists alternative crew on dates where flights
originating from a certain duty base are manned with crew from a
different duty base. It is used to minimize the amount of deadhead
flights.
"""

from carmensystems.publisher.api import *
import carmensystems.rave.api as R
from report_sources.include.SASReport import SASReport
from AbsDate import AbsDate
from RelTime import RelTime
from AbsTime import AbsTime
import Dates
import time
import math

class ProductionMoveInfo(SASReport):
    def create(self, scope='window', context='default_context'):

        # Basic setup
        SASReport.create(self, 'Production Move Info', orientation=PORTRAIT)

        # Iterators
        pm_iter = R.iter('crg_trip.production_conflict_trip_set',
                         where=('crg_trip.%trip_set_can_have_production_conflict%'),
                         sort_by=('crg_trip.%is_base_variant_in_pp%',
                                  'crg_trip.%first_active_departure_date%',
                                  'crg_trip.%first_active_arrival_station%',
                                  'crg_trip.%first_active_assigned_func%',
                                  'trip.%days%'))

        trips_iter = R.iter('iterators.trip_set')

        # Evaluate rave expression
        pm, = R.eval(context, R.foreach(pm_iter,
                                        'crg_trip.%is_base_variant_in_pp%',
                                        'crg_date.%print_date%(crg_trip.%first_active_departure_date%)',
                                        'crg_trip.%first_active_arrival_station%',
                                        'crg_trip.%first_active_assigned_func%',
                                        R.foreach(trips_iter,
                                                  'crg_date.%print_date%(crg_trip.%first_active_departure_date%)',
                                                  'report_common.%employee_number%',
                                                  'report_common.%crew_firstname%',
                                                  'report_common.%crew_surname%',
                                                  'crew.%aircraft_qlns%',
                                                  'crg_trip.%first_active_flight_no%',
                                                  'crg_trip.%first_active_ac_type%',
                                                  'crg_trip.%last_active_ac_type%',
                                                  'crg_trip.%first_active_departure_station%',
                                                  'report_common.%crew_homebase%')))


        # Create report layout
        d = ""
        for p in pm:
            if p[1]:

                if p[2] <> d:
                    d = p[2]
                    datehdr = Row("Departure: %s" % p[2])
                    datehdr.set(font = self.HEADERFONT)
                    self.add(datehdr)
                    self.add(self.getTableHeader(('Empno', 'Name', 'Ac qual', 'Flight no',
                                              'Ac out', 'Ac home', 'Dep airp', 'Position', 'Duty-base')))
                
                trips = p[-1]
                for t in trips:
                    self.add(Row(t[2], t[3] + ', ' + t[4],
                                 t[5], t[6], t[7], t[8], t[9],
                                 p[4], t[10]))

                self.add(Row(''))
                self.page0()
                
# End of file




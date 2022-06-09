

"""
Passive Booking Forecast
"""

from carmensystems.publisher.api import *
import carmensystems.rave.api as R
import os
from tempfile import mkstemp
import Cfh
import Cui
from AbsDate import AbsDate
from RelTime import RelTime
import carmstd.cfhExtensions
from report_sources.include.SASReport import SASReport


class PassiveForecastReport(SASReport):
    """
    PassiveForecastReport is used to create a passive booking forecast
    for a given period.
    """

    def create(self):
        """
        Creates a PassiveForecastReport.
        """
        SASReport.create(self, 'Passive Booking Forecast/Performed')

        fromDate = AbsDate(self.arg('FROM_DATE'))
        toDate = AbsDate(self.arg('TO_DATE'))

        # Check if there are any deadheads or ground transports
        check, = R.eval(
            'sp_crew_chains',
            'not crg_deadhead.%any_deadheads% and not crg_deadhead.%any_ground_transports%')

        if check:
            self.add(Row(Text('NO DEADHEADS REQUIRED')))
            self.add(Row(Text('NO GROUND TRANSPORTS REQUIRED')))

        else:
            # Deadheads
            self.content('DH', fromDate, toDate)
    
            # Ground transports
            self.content('GT', fromDate, toDate)

    def content(self, posType, fromDate, toDate):
        carriers, = R.eval(
            'sp_crew_chains',
            R.foreach(
            R.iter('iterators.flight_carrier_set',
                   where='crg_deadhead.%%any_of_this_positioning_type%%(crg_deadhead.%s)' % posType,
                   sort_by='leg.%flight_carrier%'),
            'leg.%flight_carrier%',
            R.foreach(
            R.iter('iterators.unique_leg_set',
                   where=('crg_deadhead.%%is_this_positioning_type%%(crg_deadhead.%s)' % posType,
                          'crg_deadhead.%%leg_start%% >= %s' % fromDate,
                          'round_down(crg_deadhead.%%leg_start%%, 24:00) <= %s' % toDate,
                          'crew_pos.%leg_assigned% > 0'),
                   sort_by=('crg_deadhead.%leg_start%',
                            'leg.%flight_nr%')),
            'leg.%flight_nr%',
            'crg_basic.%leg_number%',
            'crg_basic.%flight_suffix%',
            'aircraft_type',
            'crg_date.%print_date%(crg_deadhead.%leg_start%)',
            'crg_date.%print_time%(crg_deadhead.%leg_start%)',
            'leg.%start_station%',
            'leg.%end_station%',
            'crg_date.%print_time%(crg_deadhead.%leg_end%)',
            'crg_crew_pos.%leg_assigned_sum%(crg_crew_pos.AllCat, crg_crew_pos.SumLegSet)',
            'crg_crew_pos.%leg_assigned_vector%(crg_crew_pos.Cockpit, crg_crew_pos.SumLegSet)',
            'crg_crew_pos.%leg_assigned_vector%(crg_crew_pos.Cabin, crg_crew_pos.SumLegSet)')))

        if posType == 'DH':
            header = 'Passive Bookings'
        else:
            header = 'Ground Transports'

        for (ix, carrier, legs) in carriers:
            if len(legs) == 0:
                continue
            self.add(Row(Text('%s for carrier %s between %s & %s' % (header,
                                                                     carrier,
                                                                     fromDate,
                                                                     toDate),
                              colspan=6,
                              font=font(weight=BOLD))))
            self.add(self.getTableHeader(('Flight',
                                          'Eqp',
                                          'Date',
                                          'Departure/Arrival',
                                          'Required Seats')))
            color = True
            for (ix, flight, legNo, flightSuffix, aircraft,
                 startDate, startTime, startStation, endStation, endTime,
                 assigned, cockpit, cabin) in legs:
                color = not color
                if color:
                    bgColor = '#dedede'
                else:                
                    bgColor = '#ffffff'
                self.add(
                    Row(Text('%s %s%s' % (carrier, flight, flightSuffix)),
                        Text('%s' % aircraft),
                        Text('%s' % startDate),
                        Text('%s %s-%s %s' % (startTime, startStation,
                                              endStation, endTime)),
                        Text('%s [%s][%s]' % (assigned, cockpit, cabin)),
                        background=bgColor))
                self.page0()

            self.add(Row(' '))


def runReport():
    """
    Creates a form where user may select a period to create a passive booking
    forecast report for.
    """
    passiveBookingForm = PassiveBookingForecastForm()
    if passiveBookingForm.loop() == Cfh.CfhOk:
        fromDate = 'FROM_DATE=%s' % AbsDate(passiveBookingForm.getFromDate())
        toDate = 'TO_DATE=%s' % AbsDate(passiveBookingForm.getToDate())
        args = ' '.join([fromDate, toDate])
        rpt = 'PassiveForecastReport.py'
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info,
                                       Cui.CuiNoArea,
                                       'plan',
                                       rpt,
                                       0,
                                       args)


class PassiveBookingForecastForm(Cfh.Box):
    """
    A form used for selecting information needed to create a passive booking
    forecast report.
    """
    def __init__(self):
        Cfh.Box.__init__(self, 'Passive Booking Forecast')

        self.date1 = Cfh.Date(self, 'DATE1')
        self.date1.setMandatory(1)
        self.date2 = Cfh.Date(self, 'DATE2')
        self.date2.setMandatory(1)
        self.ok = Cfh.Done(self, 'OK')
        self.cancel = Cfh.Cancel(self, 'CANCEL')

        layout = """
FORM;A_FORM;Passive Booking Forecast
FIELD;DATE1;From Date
FIELD;DATE2;To Date
BUTTON;OK;`OK`;`_OK`
BUTTON;CANCEL;`Cancel`;`_Cancel`
"""

        (fd, fileName) = mkstemp()
        f = os.fdopen(fd, 'w')
        f.write(layout)
        f.close()
        self.load(fileName)
        os.unlink(fileName)
        self.show(True)

    def getFromDate(self):
        return self.date1.valof()

    def getToDate(self):
        return self.date2.valof()



"""
APIS Flights

Show flights that require APIS information to be sent within a time frame.
"""

import Cui
import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave

from AbsTime import AbsTime

from report_sources.include.SASReport import SASReport
from utils.rave import RaveIterator
from tm import TM


# used by carmusr.paxlst.mmi
title = 'APIS Flights'


class Report(SASReport):
    rows_per_page = 58

    def create(self):
        startdate = self.arg('STARTDATE')
        enddate = self.arg('ENDDATE')
        if startdate is not None:
            startdate = AbsTime(int(startdate))
        if enddate is not None:
            enddate = AbsTime(int(enddate))
        sort_by_country = bool(int(self.arg('SORT_BY_COUNTRY')))
        the_title = ''.join((
            title, 
            self.date_fmt(startdate, enddate), 
            ('', ' sorted by country')[sort_by_country],
        ))
        SASReport.create(self, the_title, showPlanData=False)
        flights = self.reshuffle(get_flights(startdate, enddate), sort_by_country)
        if flights:
            rowno = 1
            first = True
            current_country = None
            for leg in flights:
                if first or rowno > self.rows_per_page:
                    if not first:
                        self.add_footnote()
                        self.newpage()
                    self.add(prt.Row(
                        H2('Flight'),
                        H2('UDOR'),
                        H2('STD*'),
                        H2('ETD*'),
                        H2('ADEP'),
                        H2('ADES'),
                        H2('STA*'),
                        H2('ETA*'),
                        H2('From'),
                        H2('To'),
                        H2('Last reported**')))
                    first = False
                    rowno = 1
                if sort_by_country and isinstance(leg, str):
                    # Ugly hack, if leg is a string, then use it as a country name
                    self.add(prt.Row('', rowspan=10))
                    self.add(prt.Row(prt.Text(leg, 
                            font=prt.Font(weight=prt.BOLD, style=prt.ITALIC)), 
                        rowspan=10))
                    rowno += 2
                    current_country = leg
                    continue
                last_reported = self.get_last_reported(leg, country = current_country)
                std = self.get_time(leg.std_utc)
                sta = self.get_time(leg.sta_utc)
                etd = self.get_time(leg.etd_utc)
                eta = self.get_time(leg.eta_utc)
                self.add(prt.Row(
                    leg.flight,
                    isodate(leg.udor),
                    std,
                    etd,
                    leg.adep,
                    leg.ades,
                    sta,
                    eta,
                    leg.start_country,
                    leg.end_country,
                    last_reported))
                rowno += 1
            if rowno <= self.rows_per_page:
                self.add_footnote()
        else:
            self.add(prt.Row(H2("No APIS flights found within time frame %s - %s." % (startdate, enddate))))

    def add_footnote(self):
        self.add(prt.Isolate(VSpace()))
        self.add(prt.Isolate(prt.Column(
            prt.Row(
                prt.Column('*'), prt.Column(FootNote('All times are in UTC.'))),
            prt.Row(
                prt.Column('**'), prt.Column(FootNote
                                             ("Last reported: time of the latest APIS transmission or the last time when APIS information was fetched from the system. A value of '?' in 'Last reported' indicates that the log entry was not available."))))))

    def date_fmt(self, st, et):
        if st is None and et is None:
            return ''
        return ' (%s - %s)' % (isodatetime(st), isodatetime(et))

    def get_last_reported(self, leg, country = None):
        try:
            airport = TM.airport[(leg.adep,)]
            flight_leg = TM.flight_leg[(leg.udor, leg.fd, airport)]                
            timestamp = 0
            rep_country = "ERR"
            TM("paxlst_log")
            for row in flight_leg.referers('paxlst_log', 'flight'):
                if (int(row.timestmp) > int(timestamp)) and ((country == None) or (country == row.country.id)):
                    timestamp = row.timestmp
                    rep_country = row.country.id
            if int(timestamp) == 0:
                return ""
            else:
                return "%s (%s)" % (isodatetime(timestamp), rep_country)
        except:
            return "?"

    def get_time(self, t):
        if t is None or int(t) == 0:
            return ""
        else:
            return isodatetime(t)

    def get_flyovers(self, flight):
        flyovers = []
        fo_table = TM.flyover
#       print "YES!"
#       #print dir(flight)
        print flight.std_utc
        for fo in fo_table:
            if (fo.country_a.id, fo.country_b.id) in [(flight.start_country, flight.end_country), (flight.end_country, flight.start_country)]:
#                print "flight in table"
#                print "fo.validfrom:", fo.validfrom
                if flight.std_utc >= fo.validfrom:
#                    print "flight.stc_utc >= fo.validfrom"
#                    print "fo.validto:", fo.validto
                    if fo.validto not in [None, ""]:
#                        print "fo.validto not empty"
                        if flight.std_utc < fo.validto:
#                            print "std_utc < validto"
                            flyovers.append(fo.flyover.id)
                    else:
                        flyovers.append(fo.flyover.id)
        return flyovers

    def reshuffle(self, flights, sort_by_country):
        """Return list sorted by country and time if 'sort_by_country' is
        True."""
        if not sort_by_country:
            return flights
        T = {}
        L = []
        for f in flights:
            for country in (f.start_country, f.end_country):
                # To make it possible for the same flight to be listed for
                # both the departure and arrival countries.
                if f.ie_neu:
                    apis_countries = rave.set('leg.apis_countries_ie').members()
                elif f.dk_nsch:
                    apis_countries = rave.set('leg.apis_countries_dk').members()
                elif f.no_nsch:
                    apis_countries = rave.set('leg.apis_countries_no').members()
                else:
                    apis_countries = rave.set('leg.apis_countries').members()
                if country in apis_countries:
                    if country in T:
                        T[country].append(f)
                    else:
                        T[country] = [f]
            for country in self.get_flyovers(f):
                if country in T:
                    T[country].append(f)
                else:
                    T[country] = [f]
        for c in sorted(T):
            # Ugly hack, add the country name to the list of legs...
            L.append(c)
            for f in T[c]:
                L.append(f)
        return L


def isodate(d):
    if d is None:
        return ''
    return "%04d-%02d-%02d" % d.split()[:3]


def isodatetime(t):
    if t is None:
        return ''
    return "%04d-%02d-%02d %02d:%02d" % t.split()[:5]


def H1(*a, **k):
    k['font'] = prt.Font(size=10, weight=prt.BOLD)
    k['padding'] = prt.padding(2, 12, 2, 2)
    return prt.Text(*a, **k)


def H2(*a, **k):
    k['font'] = prt.Font(size=8, weight=prt.BOLD)
    return prt.Text(*a, **k)


def H3(*a, **k):
    k['font'] = prt.Font(size=5, weight=prt.BOLD)
    return prt.Text(*a, **k)


def FootNote(*a, **k):
    k['font'] = prt.Font(size=6)
    return prt.Text(*a, **k)


def VSpace(*a, **k):
    """Empty row of height 16."""
    k['height'] = 16
    return prt.Row(*a, **k)


def get_default_start():
    """Default is from now until end of day."""
    now, = rave.eval('fundamental.%now%')
    return now


def get_default_end():
    """Default is end of today."""
    return get_default_start().day_ceil()


def get_flights(startdate=None, enddate=None):
    where_expr = ['leg.%is_apis%']
    if startdate is not None:
        where_expr.append('leg.%%end_utc%% >= %s' % startdate)
    if enddate is not None:
        where_expr.append('leg.%%start_utc%% <= %s' % enddate)
    ri = RaveIterator(RaveIterator.iter('iterators.flight_leg_set',
            where=tuple(where_expr),
            sort_by='leg.%start_utc%',
        ), {
            'flight': 'report_crewlists.%leg_flight_id%',
            'fd': 'report_crewlists.%leg_flight_descriptor%',
            'udor': 'report_crewlists.%leg_udor%',
            'adep': 'report_crewlists.%leg_adep%',
            'ades': 'report_crewlists.%leg_ades%',
            'std_utc': 'report_crewlists.%leg_std_utc%',
            'sta_utc': 'report_crewlists.%leg_sta_utc%',
            'etd_utc': 'report_crewlists.%leg_etd_utc%',
            'eta_utc': 'report_crewlists.%leg_eta_utc%',
            'start_country': 'report_crewlists.%leg_start_country%',
            'end_country': 'report_crewlists.%leg_end_country%',
            'no_nsch': 'report_crewlists.%leg_is_no_nsch%',
            'dk_nsch': 'report_crewlists.%leg_is_dk_nsch%',
            'ie_neu': 'report_crewlists.%leg_is_ie_neu%'
        })
    return ri.eval('sp_crew')


def run(startdate=None, enddate=None, sort_by_country=False):
    report = 'apis_flights.py'
    a = []
    if startdate is not None:
        a.append('STARTDATE=%s' % int(AbsTime(startdate)))
    if enddate is not None:
        a.append('ENDDATE=%s' % int(AbsTime(enddate)))
    a.append('SORT_BY_COUNTRY=%s' % int(sort_by_country))
    args = ' '.join(a)
    Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiNoArea, 'plan', report,
            0, args)


if __name__ == '__main__':
    run("20100202 22:00", "20100202 23:50")


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof



"""
APIS log

Show APIS transmission log, data comes from 'paxlst_log'.
"""

import Cui
import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave

from AbsTime import AbsTime

from utils.divtools import fd_parser
from report_sources.include.SASReport import SASReport
from tm import TM


# Used by carmusr.paxlst.mmi
title = 'FCM Transmission Report'


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
        rows = self.reshuffle(get_paxlst(startdate, enddate), sort_by_country)
        if rows:
            rowno = 1
            first = True
            used_countries = set()
            for row in rows:
                if first or rowno > self.rows_per_page:
                    if not first:
                        self.add_footnote()
                        self.newpage()
                    self.add(prt.Row(
                        H2('FCM Type*'),
                        H2('Time stamp'),
                        H2('Flight'),
                        H2('ADEP'),
                        H2('ADES**'),
                        H2('Country'),
                        H2('#Crew'),
                        H2('MCL***'),
                        H2('Interchange#'),
                        H2('Reference'),
                        H2('Revision#')))
                    first = False
                    rowno = 1
                if sort_by_country and not row.country.id in used_countries:
                    used_countries.add(row.country.id)
                    self.add(prt.Row('', rowspan=10))
                    self.add(prt.Row(prt.Text(row.country.id, 
                            font=prt.Font(weight=prt.BOLD, style=prt.ITALIC)), 
                        rowspan=10))
                    rowno += 2
                fcm_type = ''
                if bool(row.ismcl):
                    mcl = row.changetype
                    fcm_type = 'MCL'
                else:
                    mcl = ''
                    fcm_type = 'FCM'
                if row.cnt is None:
                    # This is ugly, but maybe not enough reason to change the data model
                    if row.country.id == 'CN':
                        fcm_type = 'PDF'
                    count = ''
                else:
                    count = str(row.cnt)
                flight, adep, ades = self.fmt_flight(row)
                self.add(prt.Row(
                    prt.Text(fcm_type),
                    prt.Text(self.isotime(row.timestmp)),
                    prt.Text(flight),
                    prt.Text(adep),
                    prt.Text(ades),
                    prt.Text(row.country.id),
                    prt.Text(count, align=prt.RIGHT),
                    prt.Text(mcl),
                    prt.Text(str(row.interchange), align=prt.RIGHT),
                    prt.Text(row.refid),
                    prt.Text(str(row.revision), align=prt.RIGHT)))
                rowno += 1
            if rowno <= self.rows_per_page:
                self.add_footnote()
        else:
            self.add(prt.Row(H2("No FCM or MCL transmissions found within requested interval.")))

    def fmt_flight(self, row):
        try:
            flight = row.flight
            if flight is None:
                return '', '', ''
            fd = fd_parser(flight.fd)
            udor = flight.udor
            adep = flight.adep.id
            ades = flight.ades.id
        except:
            # old legs, not loaded
            f = str(row.getRefI('flight')).split('+')
            if f is None:
                return '', '', ''
            fd = fd_parser(f[1])
            udor = AbsTime(f[0])
            adep = f[2]
            ades = ''
        return "%s %04d%s/%02d" % (fd.carrier, fd.number, fd.suffix, udor.split()[2]), adep, ades

    def add_footnote(self):
        self.add(prt.Isolate(VSpace()))
        self.add(prt.Isolate(prt.Column(
            prt.Row(prt.Column('*'),
                prt.Column(FootNote('FCM = Flight Crew Manifest, PDF = Crew Manifest in PDF format, MCL = Master Crew List.'))),
            prt.Row(prt.Column('**'),
                prt.Column(FootNote('ADES is only shown for legs in loaded data period.'))),
            prt.Row(prt.Column('***'),
                prt.Column(FootNote('G = Added records, H = Deleted records, I = Changed records.'))))))

    def date_fmt(self, st, et):
        def dstr(d):
            if d is None:
                return ''
            return "%04d-%02d-%02d" % d.split()[:3]
        if st is None and et is None:
            return ''
        return ' (%s - %s)' % (dstr(st), dstr(et))

    def isotime(self, t):
        if t is None:
            return ''
        return "%04d-%02d-%02d %02d:%02d" % t.split()[:5]

    def reshuffle(self, rows, sort_by_country):
        """Return list sorted by country and time if 'sort_by_country' is
        True."""
        if not sort_by_country:
            L = [(row.timestmp, row.interchange, row.revision, row) for row in rows]
            L.sort()
            return [x[3] for x in L]
        L = [(row.country.id, row.timestmp, row.interchange, row.revision, row) for row in rows]
        L.sort()
        return [x[4] for x in L]


def get_paxlst(st, et):
    flt = []
    if not st is None:
        flt.append('(timestmp>=%s)' % st)
    if not et is None:
        flt.append('(timestmp<%s)' % et)
    TM("paxlst_log")
    if not flt:
        return list(TM.paxlst_log)
    else:
        if len(flt) == 1:
            return list(TM.paxlst_log.search(flt[0]))
        else:
            return list(TM.paxlst_log.search('(&%s)' % ''.join(flt)))


def H1(*a, **k):
    k['font'] = prt.Font(size=10, weight=prt.BOLD)
    k['padding'] = prt.padding(2, 12, 2, 2)
    return prt.Text(*a, **k)


def H2(*a, **k):
    k['font'] = prt.Font(size=8, weight=prt.BOLD)
    return prt.Text(*a, **k)


def FootNote(*a, **k):
    k['font'] = prt.Font(size=6)
    return prt.Text(*a, **k)


def VSpace(*a, **k):
    """Empty row of height 16."""
    k['height'] = 16
    return prt.Row(*a, **k)


def get_default_start():
    """Default is for the last three days."""
    now, = rave.eval('fundamental.%now%')
    return now.day_floor().adddays(-3)


def get_default_end():
    """Default is end of today."""
    now, = rave.eval('fundamental.%now%')
    return now.day_ceil()


def run(startdate=None, enddate=None, sort_by_country=False):
    report = 'apis_log.py'
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
    run()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

"""
APIS info

Show the information that is sent to authorities in a readable format.
"""

import Cui
import carmensystems.publisher.api as prt

from AbsTime import AbsTime

from carmusr.paxlst.crew_iter import crewlist, FaultExtractor
from utils.divtools import fd_parser
from report_sources.include.SASReport import SASReport
from utils.edifact.tools import ISO3166_1 as co
from utils.edifact import latin1_to_edifact, alnum
from utils.divtools import fmt_list, i2rm


class Report(SASReport):
    crew_per_page = 7
    colors = prt.ColourPalette(red="#FF3333")

    def create(self):
        fd = self.arg('FD')
        udor = AbsTime(int(self.arg('UDOR')))
        adep = self.arg('ADEP')
        title = 'Crew Manifest (FCM)'
        SASReport.create(self, title, showPlanData=False)
        fx = MyFaultExtractor()
        rows = crewlist(fd, udor, adep)
        if rows:
            first = True
            for leg in rows:
                self.add(self.flight_box(leg))
                clist = list(leg)
                if clist:
                    p_nr_crew = 1
                    first = True
                    for crew in clist:
                        if first or p_nr_crew > self.crew_per_page:
                            if not first:
                                self.add_footnote()
                                self.newpage()
                            first = False
                            p_nr_crew = 1
                        self.add(VSpace())
                        self.add(prt.Row(
                            prt.Column(
                                self.c_info_box(crew),
                                self.c_birth_box(crew),
                                self.c_address_box(crew)),
                            prt.Column(self.c_document_box(crew, leg.end_country))))
                        faults = fx.test(crew, leg)
                        if faults:
                            problem = "PROBLEM%s" % ('', 'S')[len(faults) > 1]
                            for fault in fmt_list("%s : %s." % (problem, ', '.join(["(%s) %s" % (f.number, f) for f in faults])), width=140):
                                self.add(self.c_fail_box(fault))
                        p_nr_crew += 1
                    if p_nr_crew <= self.crew_per_page:
                        self.add_footnote()
                    if fx.remedies:
                        self.newpage()
                        self.add(self.remedy_box(fx))
                else:
                    self.add(prt.Row(H2("No crew assigned to flight (fd=%s, udor=%s, adep=%s)." % (fd, udor, adep))))
        else:
            self.add(prt.Row(H2("Flight not found (fd=%s, udor=%s, adep=%s)." % (fd, udor, adep))))

    def add_footnote(self):
        self.add(prt.Isolate(VSpace()))
        self.add(prt.Isolate(prt.Column(
            prt.Row(
                prt.Column('*', colspan=2), prt.Column(FootNote('CR1 = Cockpit crew and individuals in cockpit, CR2 = Cabin crew,'
                    ' CR3 = Airline operation management with cockpit access.'
                    ' CR4 = Cargo non-cockpit crew and/or non-crew individuals.'))),
            prt.Row(
                prt.Column(), prt.Column(FootNote('CR5 = Pilots on A/C but not on duty.'))),
            prt.Row(prt.Column(), prt.Column()),
            prt.Row(
                prt.Column('**'), prt.Column(FootNote('Visa information is only sent to Chinese authorities for non-Chinese crew (PDF).'
                    ' License information is not sent to UK authorities.'))))))

    def flight_box(self, leg):
        return prt.Isolate(prt.Column(
            prt.Row(H3("Flight"), H3("UDOR"), H3("STD"), H3("ADEP"),
                H3("ADES"), H3("STA"), H3("From"), H3("To"), H3("A/C")),
            prt.Row(H2(leg.fd), H2(isodate(leg.udor)),
                H2(isodatetime(leg.std)), H2(leg.adep), H2(leg.ades),
                H2(isodatetime(leg.sta)), H2(self.safe_alpha2to3(leg.start_country)),
                H2(self.safe_alpha2to3(leg.end_country)), H2(leg.ac_reg))))

    def remedy_box(self, fx):
        col = prt.Column(
            prt.Isolate(prt.Column(
                VSpace(),
                prt.Row(prt.Text("Recommended actions", font=prt.Font(size=12,
                    weight=prt.BOLD), colour=self.colors.red)),
                VSpace())))
        for remedy in fx.get_remedies():
            first = True
            for tip in fmt_list(remedy, width=140):
                if first:
                    col.add(prt.Row(remedy.number, tip, colour=self.colors.red))
                    first = False
                else:
                    col.add(prt.Row('', tip, colour=self.colors.red))
            col.add(VSpace("", ""))
        return prt.Isolate(col)

    def safe_alpha2to3(self, c):
        try:
            return co.alpha2to3(c)
        except:
            return "???"

    def c_info_box(self, c):
        return prt.Isolate(prt.Column(
            prt.Row(H3("DHS Category*"), H3("Surname"), H3("Given Name"), H3("Gender"), H3("Nationality")),
            prt.Row(c.dhs_category, H2(mrz(c.sn)), H2(mrz(c.gn)), c.gender,
                self.safe_alpha2to3(c.nationality))))

    def c_birth_box(self, c):
        return prt.Isolate(prt.Column(
            prt.Row(H3("Birthday"), H3("Place of Birth"), H3("State of Birth"), H3("Country of Birth")),
            prt.Row(isodate(c.birthday), mrz(c.birth_place), mrz(c.birth_state),
                self.safe_alpha2to3(c.birth_country))))

    def c_address_box(self, c):
        return prt.Isolate(prt.Column(
            prt.Row(H3("Street"), H3("City"), H3("State"), H3("Postal Code"), H3("Country")),
            prt.Row(mrz(c.res_street), mrz(c.res_city), mrz(c.res_state),
                mrz(c.res_postal_code), self.safe_alpha2to3(c.res_country))))

    def c_document_box(self, c, end_country):
        box = prt.Column(
            prt.Row(H3("Type of Document**"), H3("Document Identifier"), H3("Issuer"), H3("Expires")))
        if c.passport:
            box.add(prt.Row("PASSPORT", alnum(c.passport),
                self.safe_alpha2to3(c.passport_issuer), isodate(c.passport_validto)))
        if c.visa and (c.visa_issuer == end_country):
            box.add(prt.Row("VISA", alnum(c.visa), self.safe_alpha2to3(c.visa_issuer),
                isodate(c.visa_validto)))
        if hasattr(c, 'license'):
            if c.license:
                box.add(prt.Row("LICENSE", alnum(c.license),
                    self.safe_alpha2to3(c.license_issuer), isodate(c.license_validto)))
        return prt.Isolate(box)

    def c_fail_box(self, f):
        return prt.Isolate(prt.Row(
            prt.Text(f, colour=self.colors.red, font=prt.Font(weight=prt.BOLD))))


class f_string(str):
    """A trick to be able to put an attribute on a string."""
    def __new__(cls, x):
        return str.__new__(cls, x)


class MyFaultExtractor(FaultExtractor):
    def get_code(self, num, text):
        """To use roman numerals instead."""
        f = f_string(text)
        f.number = i2rm(num).lower()
        return f


def mrz(s):
    return latin1_to_edifact(s, level="MRZ")


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


def run(fd, udor, adep):
    report = 'apis_info.py'
    args = 'FD=%s UDOR=%s ADEP=%s' % (''.join(fd.split()), int(AbsTime(udor)), adep)
    Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiNoArea, 'plan', report,
            0, args)


if __name__ == '__main__':
    run("SK904", "20100202", "EWR")


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof



"""
Crew Manifests in PDF format.

This format was first used for flight to China, after a couple of Change
Requests, this format is also (currently) supported for flights to Thailand and
Japan.

See more documentation in:
 * 33.9 Crew Manifest CN
 * CR SASCMS-2318 - Crew Manifest TH
 * CR SASCMS-2372 - Crew Manifest JP
 * CR SASCMS-2700 - Crew Manifest AE

"""

import logging
import os
import traceback
import time

import carmensystems.publisher.api as P
import carmensystems.rave.api as R
import carmusr.paxlst.crew_iter as crew_iter
import carmusr.paxlst.db as db

from AbsTime import AbsTime
from RelTime import RelTime

from tm import TM
from utils.divtools import fd_parser
from utils.edifact import latin1_to_edifact
from utils.edifact.tools import ISO3166_1 as co
from utils.rave import RaveIterator
from utils.selctx import BasicContext
from utils.TimeServerUtils import now_datetime


log = logging.getLogger('report_sources.hidden.CrewManifestPDF')


# module variables ======================================================={{{1
# mapping from position to occupation
crew_pos = {
    'FC': "CAPTAIN",
    'FP': "PILOT",
    'FR': "TECH",
    'AP': "PURSER",
    'AS': "STEWARD",
    'AH': "HOST",
}

# Number of days ahead to look for
default_daysahead = 5

# Configured countries.
configured_countries = ('CN', 'JP', 'TH', 'AE')


# CrewManifestPDF ========================================================{{{1
class CrewManifestPDF(P.Report):
    """
    Create the PDF report using Carmen Publisher.

    Uses 'carmusr.paxlst.crewiter.crewlist(fd, udor, adep)' to get
    a crew list to iterate.
    """
    
    country = None
    show_visa = False # True for CN, false for TH and JP
    show_passport_expiry = False # True for CN, false for TH and JP
    no_col_width = 26
    passport_expiry_col_width = 48
    name_col_width = 360
    nationality_col_width = 60
    sex_col_width = 30
    birth_date_col_width = 50
    occupation_col_width = 74
    visa_no_col_width = 80
    visa_type_col_width = 30

    def create(self):
        self.set(font=P.Font(face=P.SANSSERIF,size=8))
        self.setpaper(orientation=P.LANDSCAPE)
        if self.show_visa:
            self.name_col_width = self.name_col_width - self.visa_no_col_width - self.visa_type_col_width
        if self.show_passport_expiry:
            no_reduct = 5
            nat_reduct = 5
            sex_reduct = 7
            birth_date_reduct = 10
            occ_reduct = 13
            visa_no_reduct = 10
            self.no_col_width = self.no_col_width - no_reduct
            self.name_col_width = self.name_col_width - (self.passport_expiry_col_width - visa_no_reduct - occ_reduct - birth_date_reduct - sex_reduct - nat_reduct - no_reduct)
            self.sex_col_width = self.sex_col_width - sex_reduct
            self.birth_date_col_width = self.birth_date_col_width - birth_date_reduct
            self.nationality_col_width = self.nationality_col_width - nat_reduct
            self.occupation_col_width = self.occupation_col_width - occ_reduct
            self.visa_no_col_width = self.visa_no_col_width - visa_no_reduct

        # Create a crew list based on the arguments, note that 'leg' has
        # attributes *AND* is iterable (actually a modified RaveIterator).
        fd = self.arg('FD')
        # [acosta:07/332@01:22] Note that the stupid interface cannot accept
        # arguments that are integers, so first we transforms the integer to
        # string, then creates an AbsTime from the int value of the parameter
        # string.
        udor = AbsTime(int(self.arg('UDOR')))
        adep = self.arg('ADEP')
        try:
            leg = crew_iter.crewlist(fd, udor, adep, self.country)[0]
        except:
            traceback.print_exc()
            raise ValueError("No legs found. (fd=%s, udor=%s, adep=%s)" % (fd, udor, adep))

        # Has to add header first, sigh...
        self.add(self.reportHeader(leg))
        self.add(self.reportFooter())

        i = 0
        for crew in leg:
            i += 1
            if crew.passport:
                doctype = "PASSPORT"
            else:
                doctype = ""
            try:
                validto = crew.passport_validto
                (y, m, d) = validto.split()[:3]
                # Reverse order, no century
                passport_validto = "%02d%02d%02d" % (d, m, y % 100)
            except:
                passport_validto = ""
            try:
                (y, m, d) = crew.birthday.split()[:3]
                # Reverse order, no century
                birthday = "%02d%02d%02d" % (d, m, y % 100)
            except:
                birthday = ""
            if crew.nationality != self.country:
                try:
                    # first letter of subtype (CN,CREW) -> 'C'
                    visa_type = crew.visa_type.split(',')[0][0]
                except:
                    visa_type = ""
                for_stays_of = ""
                try:
                    if leg.end_country == self.country:
                        for_stays_of = "%d" % int(crew.for_stays_of)
                except:
                    pass
            else:
                visa_type = ""
                for_stays_of = ""
            sn = latin1_to_edifact(crew.sn)
            gn = latin1_to_edifact(crew.gn)
            if len(sn) + len(gn) + 1 > 40:
                name = P.Column(P.Text(sn, border=P.border(left=1, right=1, top=1)),
                    P.Text(gn, border=P.border(left=1, right=1, bottom=1)), width=self.name_col_width)
            else:
                name = P.Column(P.Text("%s %s" % (sn, gn)), width=self.name_col_width, border=P.border_all(1))
            a_row = P.Row(P.Column(P.Text(i), width=self.no_col_width, border=P.border_all(1)),
                          P.Column(P.Text(crew.passport), width=80, border=P.border_all(1)),
                          font=P.Font(size=10, weight=None))
            if self.show_passport_expiry:
                a_row.add(P.Column(P.Text(passport_validto), width=self.passport_expiry_col_width, border=P.border_all(1)))
            a_row.add(name)
            a_row.add(P.Column(P.Text(co.alpha2to3(crew.nationality)), width=self.nationality_col_width, border=P.border_all(1)))
            a_row.add(P.Column(P.Text(crew.gender), width=self.sex_col_width, border=P.border_all(1)))
            a_row.add(P.Column(P.Text(birthday), width=self.birth_date_col_width, border=P.border_all(1)))
            a_row.add(P.Column(P.Text(self._getOccupation(crew.position, crew.gender)), width=self.occupation_col_width, border=P.border_all(1)))
            if self.show_visa:
                a_row.add(P.Column(P.Text(crew.visa), width=self.visa_no_col_width, border=P.border_all(1)))
                a_row.add(P.Column(P.Text(visa_type), width=self.visa_type_col_width, border=P.border_all(1)))
            a_row.add(P.Column(P.Text(for_stays_of), width=40, border=P.border_all(1)))
            a_row.add(P.Column(P.Text(doctype), width=70, border=P.border_all(1)))
            self.add(P.Isolate(a_row))
        if self.planningArea() != "ALL":
            self.add(
                P.Isolate(P.Column(
                    P.Text('This report is generated using filtered data. The crew list may be incomplete.'),
                    P.Text('To avoid this, open Studio using the "ALL" region.'),
                )))

    def _getOccupation(self, position, gender):
        """Translate from position to 'CAPTAIN', 'HOST', 'HOSTESS', ..."""
        o = crew_pos.get(position, "HOST")
        if o == "HOST" and gender == "F":
            return o + "ESS"
        return o

    def reportHeader(self, leg):
        """General information about the flight, dates, places, reg."""
        nr_crew = len(list(leg))

        # h1 - top of paper
        h1 = P.Row(P.Text('LIST OF ENTRY/DEPARTURE FLIGHT AND STAFF PATTERN',
            colspan=9,
            align=P.CENTER,
            colour="#000000",
            font=P.Font(size=18, weight=P.BOLD)))

        # Date
        h2 = P.Row(P.Text(str(leg.sta).split()[0],
            colspan=9, 
            align=P.CENTER,
            font=P.Font(size=18, weight=P.BOLD)))

        # Chinese text stored as images, english text is displayed below the
        # pictures.
        if self.country == 'CN':
            ac_or_comp_nat_col = P.Column(P.Text("Company"),
                                          P.Text("Registered at"),
                                          width=68,
                                          border=P.border_frame(1))
        else:
            ac_or_comp_nat_col = P.Column(P.Text("Nationality"),
                                          P.Text("of Aircraft"),
                                          width=68,
                                          border=P.border_frame(1))
        h3 = P.Isolate(P.Row(
             P.Column(P.Text("Type of"),
                 P.Text("Aircraft"),
                 width=68,
                 border=P.border_frame(1)),
             P.Column(P.Text("Flight"),
                 P.Text("number"),
                 width=60,
                 border=P.border_frame(1)),
             P.Column(P.Text("Airline"),
                 P.Text(" "),
                 width=60,
                 border=P.border_frame(1)),
             P.Column(P.Text("Origin/Destination"),
                 P.Text("Country"),
                 width=108,
                 border=P.border_frame(1)),
             P.Column(P.Text("Registration"),
                 P.Text("of Aircraft"),
                 width=68,
                 border=P.border_frame(1)),
             ac_or_comp_nat_col,
             P.Column(P.Text("Total crew of Entry"),
                 P.Text("Departure or Transit"),
                 width=138, 
                 border=P.border_frame(1)),
             P.Column(P.Text("Disembarked"),
                 P.Text("Passengers"),
                 width=111,
                 border=P.border_frame(1)),
             P.Column(P.Text("Transit"),
                 P.Text("Passengers"),
                 width=111,
                 border=P.border_frame(1)),
             font=P.Font(size=10, weight=P.BOLD)))

        from_to = "%s/%s - %s/%s" % (
                leg.adep, co.alpha2to3(leg.start_country),
                leg.ades, co.alpha2to3(leg.end_country))
        # Investigate: Shouldn't A/C nationality be maintained in 'aircraft' entity?
        # Right now it's empty...
        if self.country == 'CN':
            ac_or_comp_nat_txt = 'SWE'
        else:
            ac_or_comp_nat_txt = {'OY': 'DNK', 'LN': 'NOR', 'SE': 'SWE'}.get(leg.ac_reg[:2], ' ')
        h4 = P.Isolate(P.Row(
             P.Column(P.Text(leg.ac_type), width=68),
             P.Column(P.Text(leg.fd_number), width=60),
             P.Column(P.Text(leg.fd_carrier), width=60),
             P.Column(P.Text(from_to), width=108),
             P.Column(P.Text(leg.ac_reg), width=68),
             P.Column(P.Text(ac_or_comp_nat_txt), width=68),
             P.Column(P.Text(nr_crew), width=138),
             P.Column(P.Text(" "), width=111),
             P.Column(P.Text(" "), width=111),
             font=P.Font(size=10, weight=P.BOLD),
             height=20,
             border=P.border_all(1)))

        h5_row = P.Row(P.Column(P.Text("No"), 
                                width=self.no_col_width, 
                                border=P.border_frame(1)),
                       P.Column(P.Text("No. of Passport"),
                                width=80,
                                border=P.border_frame(1)),
                       font=P.Font(size=10, weight=P.BOLD))
        if self.show_passport_expiry:
            h5_row.add(P.Column(P.Text("Passport"),
                                P.Text("Expiry"),
                                P.Text("Date"),
                                width=self.passport_expiry_col_width,
                                border=P.border_frame(1)))
        h5_row.add(P.Column(P.Text("Full Name"),
                            width=self.name_col_width,
                            border=P.border_frame(1)))
        h5_row.add(P.Column(P.Text("Nationality"),
                            width=self.nationality_col_width, border=P.border_frame(1) ))
        h5_row.add(P.Column(P.Text("Sex"),
                            width=self.sex_col_width,
                            border=P.border_frame(1)))
        h5_row.add(P.Column(P.Text("Date of"),
                            P.Text("Birth"),
                            width=self.birth_date_col_width,
                            border=P.border_frame(1)))
        h5_row.add(P.Column(P.Text("Occupation"),
                            width=self.occupation_col_width,
                            border=P.border_frame(1)))
        if self.show_visa:
            h5_row.add(P.Column(P.Text("No. of Visa"),
                                width=self.visa_no_col_width,
                                border=P.border_frame(1)))
            h5_row.add(P.Column(P.Text("Type"),
                                P.Text("of"),
                                P.Text("Visa"),
                                width=self.visa_type_col_width,
                                border=P.border_frame(1)))
        h5_row.add(P.Column(P.Text("For"),
                 P.Text("stay(s)"),
                 P.Text("of"),
                 width=40,
                 border=P.border_frame(1)))
        h5_row.add(P.Column(P.Text("Type of"),
                 P.Text("Document"),
                 width=70,
                 border=P.border_frame(1)))
        h5 = P.Isolate(h5_row)
        return P.Header(P.Row(P.Column(h1, h2, h3, h4, h5)), width=800)

    def planningArea(self):
        try:
            pa = R.param("planning_area.%filter_company_p%").value()
            if not pa: pa = "ALL"
        except:
            pa = "ALL"
        return pa

    def reportFooter(self):
        """Signatures."""
        f1 = P.Isolate(P.Row(
            P.Column(P.Text("Signature of staff"),
                width=100, 
                border=P.border_frame(1)),
            P.Column(P.Text(" "),
                width=118, 
                border=P.border_frame(1)),
            P.Column(P.Text("To be filled and sealed by immigration"),
                width=200, 
                border=P.border_frame(1)),
            P.Column(P.Text(" "),
                width=118,
                border=P.border_frame(1)),
            P.Column(P.Text("Seal of Airline"),
                width=140,
                border=P.border_frame(1)),
            P.Column(P.Text(" "),
                width=118,
                border=P.border_frame(1)),
            font=P.Font(size=10, weight=P.BOLD), height=40))
        return P.Footer(P.Column(f1), width=800)


# functions =============================================================={{{1

def generate_one(fd=None, origsuffix='', udor=None, adep=None, country=None,
        maildest=None, subtype=None, rcpttype=None):
    """Create one PDF report for a flight (to/from country)."""

    if fd is None:
        raise ValueError("CrewManifestPDF.generate_one(): argument 'fd' is missing.")
    if udor is None:
        raise ValueError("CrewManifestPDF.generate_one(): argument 'udor' is missing.")
    if adep is None:
        raise ValueError("CrewManifestPDF.generate_one(): argument 'adep' is missing.")

    if country not in configured_countries: # maybe we should raise an Exception here? (configuration error)
        return [], False

    return_list = []

    try:
        udor_a = AbsTime(udor)
        udor = str(int(udor_a))
    except Exception, e:
        raise ValueError("CrewManifestPDF.generate_one(): argument 'udor' (=%s) in wrong format. %s" % (udor, e))
    
    # Generate the PDF
    filename = report(fd, udor, adep, country)
        
    # Log the creation.
    ticket = db.get_cl_ticket(country, fd, udor_a, adep)
    ticket.save()

    # For the mail message
    f = fd_parser(fd)
    if origsuffix != '':
        f.suffix = origsuffix
    date = str(udor_a).split()[0] # i.e. 20AUG2007
    suffix = f.suffix.replace(' ', '')
    mail_params = {
        'subject': 'Crew Manifest for %s - %s/%s (nr %d)' % (
            country, f.flight_id.strip(), date, ticket.revision),
        'attachmentName': "Crew_Manifest_%s_%s%03d%s_%s_%d.pdf" % (
            country, f.carrier, f.number, suffix, date, ticket.revision),
        }
    if subtype:
        mail_params['subtype'] = subtype
    if rcpttype:
        mail_params['rcpttype'] = rcpttype
    return_list.append({
        'content-location': filename,
        'content-type': 'application/pdf',
        'destination': [(maildest, mail_params)],
    })
        
    return return_list, True


def generate_many(daysahead=default_daysahead, country=None):
    """Iterate all flights that go to or come from country (=CN), create a
    report for each of them."""

    return_list = []
    ri = RaveIterator(RaveIterator.iter('report_crewlists.flight_country_leg_set', 
        where=(
            'report_crewlists.%leg_is_flight%',
            'report_crewlists.%%touches_country%%("%s")' % country,
            'report_crewlists.%%in_next_days%%(%s)' % daysahead,
        )), {
            'fd': 'report_crewlists.%leg_flight_descriptor%',
            'udor': 'report_crewlists.%leg_udor%',
            'adep': 'report_crewlists.%leg_adep%',
            'origsuffix': 'report_crewlists.%origsuffix%',
            'maildest': 'report_crewlists.%mail_dest%',
        })
    for leg in ri.eval(BasicContext().getGenericContext()):
        return_list.extend(generate_one(fd=leg.fd, udor=leg.udor, adep=leg.adep,
            origsuffix=leg.origsuffix, country=country, maildest='CREW_MANIFEST', subtype='PDF', rcpttype=country)[0])

    return return_list, True


def report(fd, udor, adep, country):
    """Return PDF file with the report."""
    d = os.path.expandvars("$CARMDATA/REPORTS/CREW_MANIFESTS")
    if not os.path.isdir(d):
        os.makedirs(d)
    filename = os.path.join(d, 'FCM_%s_%s_%s_%s_%s' % (
        country,
        ''.join(fd.split()), 
        "%04d%02d%02d" % AbsTime(int(udor)).split()[:3],
        adep,
        now_datetime().strftime("%Y%m%d_%H%M%S")))
    log.info("%s manifest file %s" % (country, filename))
    try:
        P.generateReport('report_sources.hidden.CrewManifest%s' % country,
                filename, P.PDF, {'FD':fd, 'UDOR': udor, 'ADEP': adep})
        filename += '.pdf'
    except Exception, e:
        log.error('Could not create crew manifest. - %s' % e)
        raise
    return filename


def reportSelectedFlight(country):
    import Cui
    fd = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object", "report_crewlists.%leg_flight_descriptor%").replace(' ','')
    udor = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiWhichArea, "object", "report_crewlists.%leg_udor%")
    adep = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object", "report_crewlists.%leg_adep%")
    args = 'FD=%s UDOR=%s ADEP=%s' % (fd, udor, adep)
    report = 'CrewManifest%s.py' % country
    Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiNoArea, 'plan', report, 0, args)


bit = reportSelectedFlight


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    bit()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

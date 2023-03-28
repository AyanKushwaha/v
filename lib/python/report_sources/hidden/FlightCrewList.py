# Created 9th Feb 2007 by Yaser Mohamed
# [acosta:08/027@22:03] Rewritten almost all code...
# [acosta:08/029@15:20] Added PAX figures and look-up in database.
# [acosta:08/031@10:14] Added PACT and Ground Duty information.
# [acosta:08/100@13:34] Solution for BZ 26277.

"""
Create a list of crew on a selected flight/activity.

Notes:
 - does not take care of published/not informed.
"""

# imports ================================================================{{{1
import Cui
import carmensystems.rave.api as R

from carmensystems.publisher.api import *

from report_sources.include.SASReport import SASReport
from tm import TM
from utils.dave import EC
from utils.rave import RaveIterator
from utils.paxfigures import PaxInfo
from carmusr.paxlst.crew_iter import crewlist as CrewList


# Sorting of Crew ========================================================{{{1

# CrewSorted -------------------------------------------------------------{{{2
class CrewSorted:
    """Class that mimics the sorting algorithm used in Rave module 'crew' (see
    'crew.%sort_key%')"""

    # Sort order for passive/deadhead crew
    passive_table = {
        'FC': 1,
        'FP': 2,
        'FS': 3,
        'FR': 4,
        'AP': 5,
        'AS': 6,
        'AH': 7,
    }
    max_passive = max(passive_table.values()) + 1
    scc_crewid = None

    def __call__(self, crewlist):
        """'crewlist' is a list of crew with a number of attributes:
        ('seniority', 'crewid', 'category', 'main_cat', 'rank')"""
        self.scc_crewid = self.get_scc(crewlist)
        return self.sorted_crew(crewlist)

    def get_scc(self, crewlist):
        """Return crewid of crew that is SCC for this flight."""
        # List of cabin crew flying active and not supernumerary
        L = [(x.seniority, x) for x in crewlist if x.main_cat == 'C' and
                x.is_active and x.category != 'AU' and x.has_scc_qual]
        L.sort()
        cc_list = [x for _, x in L]
        for c in cc_list:
            if c.category == 'AP':
                return c.crewid               
        if cc_list:
            return cc_list[0].crewid
        # Will return None otherwise



    def sorted_crew(self, crewlist):
        """Return list of sorted crew."""
        L = [(self.sort_key(crew), crew) for crew in crewlist]
        L.sort()
        return [crew for _, crew in L]

    # The rest is structured to match the Rave code conceptually.
    def sort_key(self, crew):
        return 10000 * self.sort_key_1(crew) + crew.seniority

    def sort_key_1(self, crew):
        if crew.is_active:
            return self.sort_key_active(crew)
        else:
            return 10 + self.sort_key_passive(crew)

    def sort_key_active(self, crew):
        is_scc = (crew.crewid == self.scc_crewid)
        if crew.category == 'FC':
            return 2
        elif crew.category == 'FP':
            return 3
        elif crew.category in ('FS', 'FR'):
            return 4
        elif crew.category == 'FU':
            return 5
        elif is_scc and crew.category in ('AP', 'AS', 'AH'):
            return 6
        elif not is_scc and crew.category == 'AP':
            return 7
        elif not is_scc and crew.rank == 'AP' and crew.category in ('AS', 'AH'):
            return 8
        elif not is_scc and crew.rank in ('AS', 'AH') and crew.category == 'AS':
            return 8
        elif not is_scc and crew.rank in ('AS', 'AH') and crew.category == 'AH':
            return 9
        else:
            return 10

    def sort_key_passive(self, crew):
        return self.passive_table.get(crew.rank, self.max_passive)


# crew_sorted ------------------------------------------------------------{{{2
crew_sorted = CrewSorted()


# RaveIterator classes ==================================================={{{1

# FlightIter -------------------------------------------------------------{{{2
class FlightIter(RaveIterator):
    """Rave variables that are evalutated on the flight."""
    def __init__(self):
        fields = {
            'ac_type': 'leg.%ac_type%',
            'adep': 'leg.%start_station%',
            'ades': 'leg.%end_station%',
            'category_code': 'leg.%category_code%',
            'code': 'leg.%code%',
            'flight_descriptor': 'leg.%flight_descriptor%',
            'flight_name': 'leg.%flight_name%',
            'group_code_description': 'leg.%group_code_description%',
            'is_flight': 'leg.%is_flight_duty%',
            'is_ground_duty': 'leg.%is_ground_duty%',
            'is_pact': 'leg.%is_pact%',
            'sta': 'leg.%end_UTC%',
            'sta_lt': 'leg.%end_lt%',
            'std': 'leg.%start_UTC%',
            'std_lt': 'leg.%start_lt%',
            'tail_id': 'leg.%tail_id%',
            'udor': 'leg.%udor%',
            'uuid': 'leg.%uuid%',
        }
        iter = RaveIterator.iter('iterators.leg_set')
        RaveIterator.__init__(self, iter, fields)


# CrewIter ---------------------------------------------------------------{{{2
class CrewIter(RaveIterator):
    """Rave variables that are evalutated for each crew member."""
    def __init__(self, searchdate='leg.%start_hb%'):
        fields = {
            'ac_qual': 'report_crewlists.%%crew_ac_qlns%%(%s)' % searchdate,
            'category': 'crew_pos.%assigned_function%',
            'crewid': 'crew.%id%',
            'duty_code': 'duty_code.%leg_code%',
            'empno': 'report_crewlists.%crew_empno%',
            'has_scc_qual': 'report_crewlists.%%crew_scc%%(%s)' % searchdate,
            'is_appointed_in_charge': 'attributes.%is_in_charge%',
            'homebase': 'report_crewlists.%%crew_base%%(%s)' % searchdate,
            'is_active': 'leg.%is_active_flight%',
            'logname': 'report_crewlists.%%crew_logname_at_date%%(%s)' % searchdate,
            'main_cat': 'report_crewlists.%%crew_main_rank%%(%s)' % searchdate,
            'next_act': 'crg_flight_crew.%next_flight_nr%',
            'next_time': 'crg_flight_crew.%next_flight_time%',
            'prev_act': 'crg_flight_crew.%previous_flight_nr%',
            'prev_time': 'crg_flight_crew.%previous_flight_time%',
            'rank': 'report_crewlists.%%crew_title_rank%%(%s)' % searchdate,
            'sub_category': 'report_crewlists.%%crew_sub_category%%(%s)' % searchdate,
            'seniority': 'report_crewlists.%%crew_seniority%%(%s)' % searchdate,
        }
        iter = RaveIterator.iter('iterators.leg_set', 
                sort_by='report_crewlists.%sort_key%', 
                where='fundamental.%is_roster%')
        RaveIterator.__init__(self, iter, fields)


# PRT formatting functions ==============================================={{{1
def AText(*a, **k):
    """Text aligned to BOTTOM (used as 'base' class). (See also Bugzilla
    #23730)."""
    k['valign'] = BOTTOM
    return Text(*a, **k)


def H1(*a, **k):
    """Header text level 1: size 12, bold, space above."""
    k['font'] = Font(size=12, weight=BOLD)
    # Add some space on top of the header.
    k['padding'] = padding(2, 12, 2, 2)
    return AText(*a, **k)


def H2(*a, **k):
    """Header text level 2: size 9 bold."""
    k['font'] = Font(size=9, weight=BOLD)
    return AText(*a, **k)


def BText(*a, **k):
    """Bold text."""
    k['font'] = Font(weight=BOLD)
    return AText(*a, **k)


def RowSpacer(*a, **k):
    """An empty row of height 24."""
    k['height'] = 24
    return Row(*a, **k)


def RText(*a, **k):
    """Text aligned to right (for numbers) added extra padding to the right to
    create a nicer looking report."""
    k['align'] = RIGHT
    k['padding'] = padding(2, 2, 12, 2)
    return AText(*a, **k)


# FlightCrewList (the PRT report) ========================================{{{1
class FlightCrewList(SASReport):
    """The actual report, using PRT toolkit."""

    def create(self):
        """Create the report."""
        SASReport.create(self, 'Crew List', False)

        add_comment = False
        f, crewlist, nop_crewlist = flight_and_crew()

        if not hasattr(self, 'paxinfo'):
            self.paxinfo = PaxInfo()

        # Add info about the flight
        if f.is_flight:
            self._flight_header(f)
        else:
            self._activity_header(f)
            
        fc_header = cc_header = passive_header = crew_header = True
        table = None

        # Loop crew
        for c in crewlist:
            # Create header for each crew category if not already
            # there.
            chief = ''
            if f.is_flight: 
                if fc_header and c.main_cat == 'F':
                    table = self._crew_table("Flight Deck")
                    fc_header = False
                    chief = ' (C)'
                elif cc_header and c.main_cat == 'C':
                    table = self._crew_table("Cabin Crew")
                    cc_header = False
                    chief = ' (C)'
                elif passive_header and not c.is_active:
                    table = self._crew_table("Passive/Deadhead")
                    passive_header = False
            elif crew_header:
                table = self._crew_table("Crew")
                crew_header = False

            # Better to catch this early (should never happen).
            assert table is not None

            if isinstance(c, CrewDataFromEC):
                duty_code = prev_act = next_act = prev_time = next_time = '**'
                add_comment = True
            else:
                duty_code, prev_act, next_act = c.duty_code, c.prev_act, c.next_act
                prev_time = self._to_time(c.prev_time)
                next_time = self._to_time(c.next_time)

            # sort qualifications otherwise the info from database and info
            # from Rave will have different sort orders.
            ac_qual = ' '.join(sorted(c.ac_qual.split()))

            table.add(
                Row(
                    AText("%s" % c.empno),
                    AText("%s" % c.logname),
                    AText("%s" % c.homebase),
                    AText("%s" % c.ac_qual),
                    AText("%s" % duty_code),
                    AText("%s%s" % (c.rank, c.sub_category)),
                    RText("%s" % c.seniority),
                    AText("%s%s" % (c.category, chief)),
                    AText("%s" % prev_act),
                    AText("%s" % prev_time),
                    AText("%s" % next_act),
                    AText("%s" % next_time)))

        # Loop non-operating crew
        if len(nop_crewlist) > 0:
            table = self._crew_nop_crew_table("Non Operating Crew")

        for nop in nop_crewlist:
            table.add(
                Row(
                    AText("%s" % nop.crew_id),
                    AText("%s" % nop.position),
                    AText("%s, %s" % (nop.sn, nop.gn))))

        self.add(RowSpacer())
        if add_comment:
            self.add(BText("(**) Not available, crew not loaded in plan."))

    def _activity_header(self, f):
        self.add(H1("Activity Info"))
        self.add(
            Isolate(
                Row(
                    Column(
                        Row(H2("Activity")),
                        Row(H2("Code:"), AText("%s" % f.code)),
                        Row(H2("Category:"), AText("%s" % f.category_code)),
                        Row(H2("Description:"), AText("%s" % (f.group_code_description or '')))),
                    Column(width=20),
                    Column(
                        Row(H2("Start")),
                        Row(H2("Local:"), AText(f.std_lt)),
                        Row(H2("UTC:"), AText(f.std)),
                        Row(H2("Station:"), AText("%s" % f.adep))),
                    Column(width=20),
                    Column(
                        Row(H2("End")),
                        Row(H2("Local:"), AText(f.sta_lt)),
                        Row(H2("UTC:"), AText(f.sta)),
                        Row(H2("Station:"), AText("%s" % f.ades))))))

    def _flight_header(self, f):
        self.add(H1("Flight Info"))
        self.add(
            Isolate(
                Row(
                    Column(
                        Row(H2("Flight:"), AText("%s" % f.flight_name)),
                        Row(H2("Date:"), AText("%s" % str(f.udor).split()[0])),
                        Row(H2("AC type:"), AText("%s" % f.ac_type), rowspan=2),
                        Row(H2("Tail ID:"), AText("%s" % (f.tail_id or '')))),
                    Column(width=20),
                    Column(
                        Row(H2("Departure")),
                        Row(H2("Time:"), AText(self._to_time(f.std))),
                        Row(H2("Station:"), AText("%s" % f.adep), rowspan=2)),
                    Column(width=20),
                    Column(
                        Row(H2("Arrival")),
                        Row(H2("Time:"), AText(self._to_time(f.sta))),
                        Row(H2("Station:"), AText("%s" % f.ades), rowspan=2)),
                    Column(width=20),
                    self._pax_table(f))))

    def _crew_table(self, text):
        """Return Column with headers for each crew group (Flight Deck, Cabin
        and Passive/DH."""
        self.add(RowSpacer())
        self.add(H1(text))
        col = Column(
            Row(
                BText("Emp No"),
                BText("Name"),
                Column(
                    Row(BText("Home")),
                    Row(BText("Base"))),
                BText("A/C Qual"),
                Column(
                    Row(BText("Duty")),
                    Row(BText("Code"))),
                BText("Rank"),
                BText("Seniority"),
                BText("Category"),
                Column(
                    Column(BText("Previous"), colspan=2),
                    Row(BText("Activity"), BText("End"))),
                Column(
                    Column(BText("Next"), colspan=2),
                    Row(BText("Activity"), BText("Start"))),
                background=self.HEADERBGCOLOUR))
        self.add(col)
        return col

    def _crew_nop_crew_table(self, text):
        self.add(RowSpacer())
        self.add(H1(text))
        col = Column(
            Row(
                BText("Emp No"),
                BText("Type"),
                BText("Name"),
                background=self.HEADERBGCOLOUR))
        self.add(col)
        return col

    def _pax_table(self, leg):
        """Return Column with PAX table."""
        p = self.paxinfo(leg.udor, leg.flight_name, leg.adep)
        # Service classes in specified order
        svcs = ('C', 'M')
        # Values per service class
        ppax = {}
        bpax = {}
        apax = {}
        # Totals (all service classes)
        tppax = tbpax = tapax = 0
        for y in p:
            svc = y.svc
            if y.svc == 'Y':
                svc = 'M'
            ppax[svc] = ppax.get(svc, 0) + (y.ppax or 0)
            bpax[svc] = bpax.get(svc, 0) + (y.bpax or 0)
            apax[svc] = apax.get(svc, 0) + (y.apax or 0)
            tppax += (y.ppax or 0)
            tbpax += (y.bpax or 0)
            tapax += (y.apax or 0)
        return Isolate(
            Row(
                Column(
                    Row(H2("Service Class"), *[H2(x, width=24, align=RIGHT) for x in svcs]),
                    Row(H2("PAX (prognosis)"), *[AText(ppax.get(x, ""), align=RIGHT) for x in svcs]),
                    Row(H2("PAX (budget)"), *[AText(bpax.get(x, ""), align=RIGHT) for x in svcs]),
                    Row(H2("PAX (actual)"), *[AText(apax.get(x, ""), align=RIGHT) for x in svcs])),
                Column(
                    Row(H2("Tot", width=24, align=RIGHT)),
                    Row(AText(tppax, align=RIGHT)),
                    Row(AText(tbpax, align=RIGHT)),
                    Row(AText(tapax, align=RIGHT)))))

    def _to_time(self, a):
        """Return Hours:Minutes from AbsTime."""
        if a is None:
            return '-'
        else:
            return "%02d:%02d" % a.split()[3:5]


# CrewDataFromEC ========================================================={{{1
class CrewDataFromEC(object):
    """Get data from entitites, put the attributes in this class so that it
    will have the same attributes as an Entry from a Rave iteration."""

    def __init__(self, ec, cdb):
        """ec is an EC object, cdb is a row from crew_flight_duty or
        crew_ground_duty, the difference is not too serious right here..."""
        # These values are too difficult to get by using EntityConnection, so
        # we just skip them: ('prev_act', 'prev_time', 'next_act', 'next_time',
        # 'duty_code')

        # id, category, is_active from crew_flight_duty
        self.crewid = cdb.crew
        self.category = cdb.pos
        self.is_active = cdb.pos not in ('DH')
        self.has_scc_qual = False

        # searchdate: using udor is not quite the same as using
        # 'leg.%start_hb%, but it can never be more than 24 hours wrong.
        try:
            searchdate = int(cdb.leg_udor)
        except:
            # From crew_ground_duty, use trip
            searchdate = int(cdb.trip_udor)

        # Search filter used in many of the queries.
        sfilter = "crew = '%s' AND validfrom <= %d AND validto > %d" % (self.crewid, searchdate, searchdate)

        # empno, base, rank from crew_employment
        for c in ec.crew_employment.search(sfilter):
            self.empno = c.extperkey
            self.homebase = c.base
            self.rank = c.titlerank
            if ec.inReadTxn():
                ec.endReadTxn()
            break

        # logname, main_cat from crew
        for c in ec.crew.search("id = '%s'" % cdb.crew):
            self.logname = c.logname
            if ec.inReadTxn():
                ec.endReadTxn()
            break

        # seniority from crew_seniority
        for c in ec.crew_seniority.search(sfilter):
            self.seniority = c.seniority
            if ec.inReadTxn():
                ec.endReadTxn()
            break

        # main_cat (indirectly) from crew_rank_set
        try:
            self.main_cat = rank_to_cat(ec, self.rank)
        except:
            # Should not happen, but you never know with crappy input data.
            raise ValueError("Cannot get main category for rank '%s', check entity crew_rank_set." % self.rank)

        # ac_qual, scc_qual from crew_qualifications
        quals = []
        for c in ec.crew_qualification.search(sfilter + " AND qual_typ = 'ACQUAL'"):
            quals.append(c.qual_subtype)

        if quals:
            self.ac_qual = ' '.join([str(x) for x in quals])

        if self.main_cat == 'C':
            self.has_scc_qual = (self.rank == 'AP'
                or list(ec.crew_qualification.search(sfilter + " AND qual_typ = 'POSITION' AND qual_subtype = 'SCC'"))
                or list(ec.crew_qualification.search(sfilter + " AND qual_typ = 'INSTRUCTOR' AND qual_subtype = 'LINST'")))

    def __getattr__(self, value):
        """Return value of attribute or None if attribute is not set."""
        try:
            return object.__getattr__(self, value)
        except:
            return None

    def __str__(self):
        """For basic tests."""
        return ';'.join(['%s=%s' % (k, v) for k, v in self.__dict__.iteritems()])


# Rank2Cat ---------------------------------------------------------------{{{2
class Rank2Cat(dict):
    """Build dictionary of crew ranks, the value will be 'C' for cabin crew or
    'F' for flight deck."""
    def __init__(self):
        """ec is an EntityConnection."""
        dict.__init__(self)
        self.__filled = False

    def __call__(self, ec, rank):
        if not self.__filled:
            for e in ec.crew_rank_set:
                self[e.id] = e.maincat
            self.__filled = True
        return self[rank]


# rank_to_cat ------------------------------------------------------------{{{2
# Mapping from rank to category. (Cache)
rank_to_cat = Rank2Cat()


# functions =============================================================={{{1

# flight_and_crew --------------------------------------------------------{{{2
def flight_and_crew():
    """
    Return tuple: (flight, crewlist)
    The idea is to try first with simple Rave evaluation, if not all crew is
    returned this way i.e. not all crew was loaded, then the try to use an
    EntityConnection to get information about the remaining crew.
    """
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info,
            Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea), 'OBJECT')

    fi = FlightIter()
    ei = RaveIterator(RaveIterator.iter('equal_legs'))
    ci = CrewIter()
    fi.link(ei)
    ei.link(ci)

    crewlist = []
    nop_crewlist = []

    for flight in fi.eval(R.selected(R.Level.atom())):
        for equal_leg in flight:
            for crew in equal_leg:
                crewlist.append(crew)

        # SKWD-566: 
        # Below CrewList(...) call is causing unwanted filtering to happen in studio 
        # while generating the report. This is caused by a call down the chain to 
        # Cui.gpc_set_crew_chains_by_flight(...). If SAS decides that work with NOP
        # should be continued below part needs to be rewritten to avoid the same bug 
        # as in SKWD-566. 
        #rows = CrewList(flight.flight_descriptor, flight.udor, flight.adep, with_nop=True)
        #for leg in rows:
        #    for nop in leg.chain('nop'):
        #        nop_crewlist.append(nop)
        break
    else:
        raise ValueError("No flight found!")

    if flight.is_pact:
        return flight, ci.eval(R.selected(R.Level.atom())), nop_crewlist

    # Check using EntityConnection if there is any crew that was not loaded.
    ec = EC(TM.getConnStr(), TM.getSchemaStr())
    if flight.is_ground_duty and flight.uuid:
        cdb = list(ec.crew_ground_duty.search("task_udor = %d AND task_id = '%s'" % (
            int(flight.udor) / 1440, flight.uuid)))
    else:
        cdb = list(ec.crew_flight_duty.search("leg_fd = '%s' AND leg_udor = %d and leg_adep = '%s'" % (
            flight.flight_descriptor, int(flight.udor) / 1440, flight.adep)))

    if len(crewlist) == len(cdb):
        # No need to use database, we have everything loaded.
        return flight, crew_sorted(crewlist), nop_crewlist

    dbcrew = set([x.crew for x in cdb])
    dbrave = set([x.crewid for x in crewlist])
    # Get the difference
    crew_to_fix = dbcrew - dbrave

    # Append entries from crew_flight_duty
    for db_entry in [x for x in cdb if x.crew in crew_to_fix]:
        crewlist.append(CrewDataFromEC(ec, db_entry))

    # The list has to be re-sorted...
    return flight, crew_sorted(crewlist), nop_crewlist

# runReport --------------------------------------------------------------{{{2
def runReport():
    """Run the report (from outside.)"""
    Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiWhichArea,'object',
            "FlightCrewList.py", 0, 0)


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    runReport()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

# [acosta:07/327@16:47] Created.
# [acosta:07/334@13:30] Updated with "incremental" / "full" MCL.
# [acosta:08/274@16:21] New scheme for creating incremental MCL.

"""
Create a number of CrewManifests.

Interface 33.8 Crew Manifest US
Interface CR12 Crew Manifest JP
Interface CR26 Crew Manifest TH
Interface CR95, CR136 Crew Manifest CN
Interface CR164 Crew Manifest IN

and

Master Crew List for U.S.A.
"""

import warnings

import carmensystems.rave.api as rave

import utils.edifact as edifact
import utils.edifact.tools as tools
import carmusr.paxlst.crew_iter as crew_iter
import carmusr.paxlst.db as db
import carmusr.paxlst.paxlst_impl as paxlst_impl

from AbsTime import AbsTime
from RelTime import RelTime

from tm import TM
from utils.edifact.tools import ISO3166_1 as co
from utils.ServiceConfig import ServiceConfig
from utils.divtools import fd_parser
from utils.edifact import latin1_to_edifact


# Configuration data ====================================================={{{1

class conf:
    """Sender's attributes."""
    # [acosta:07/330@10:27] Is this same for all implementations?
    sender_id = 'SCANDINAVIAN AIRLINES'
    apis_id = 'APIS*43A' # [acosta:08/301@13:56] Not used anymore.
    reporter_sn = 'Malmqvist'
    reporter_gn = 'Hans'
    reporter_phone = '004687972974'
    reporter_fax = '004687974050'
    mcl_carrier = 'SK'
    maxsize = 3480


# Generic ================================================================{{{1
class CrewList(list):
    """Generic crew list, base class."""
    def __str__(self):
        return ''.join([str(x) for x in self])

    def segment_group_1(self):
        """
        Segment group 1: NAD-CTA-COM
        Sender's contact information.
        """
        L = []
        # NAD, Name and address
        nad = self.p.NAD('MS', conf.reporter_sn)
        if hasattr(conf, 'reporter_gn'):
            nad.name.name2 = conf.reporter_gn
        L.append(nad)

        # CTA, Contact information (not used).

        # COM, Communication contact
        com = self.p.COM()
        com.contact1.id = conf.reporter_phone
        com.contact1.qual = 'TE'
        com.contact2.id = conf.reporter_fax
        com.contact2.qual = 'FX'
        L.append(com)
        return L

    def segment_group_5(self, crew, doctype):
        """
        Segment group 5: DOC-DTM-GEI-RFF-LOC-CPI-QTY
        Travel document details.
        """
        L = []
        if doctype == 'PASSPORT':
            if hasattr(crew, 'passport') and crew.passport:
                # DOC: Document details.
                L.append(self.p.DOC('P', crew.passport))

                # DTM: Dates/times related to document.
                L.append(self.p.DTM('36', AbsTime(crew.passport_validto)))

                # GEI: Processing information (not used)

                # RFF: Reference (not used)

                # LOC: Place (country, city) where document was issued.
                if hasattr(crew, 'passport_issuer') and crew.passport_issuer:
                    L.append(self.p.LOC('91', co.alpha2to3(crew.passport_issuer)))

                # CPI: Charge payment instructions (not used)
                # QTY: Quantity (not used)
        elif doctype == 'LICENCE':
            if hasattr(crew, 'license') and crew.license:
                L.append(self.p.DOC('L', crew.license))
                L.append(self.p.DTM('36', AbsTime(crew.license_validto)))
                if hasattr(crew, 'license_issuer') and crew.license_issuer:
                    L.append(self.p.LOC('91', co.alpha2to3(crew.license_issuer)))
        elif doctype == 'VISA':
            if hasattr(crew, 'visa') and crew.visa:
                L.append(self.p.DOC('V', crew.visa))
                if hasattr(crew, 'visa_validto') and crew.visa_validto:
                    L.append(self.p.DTM('36', AbsTime(crew.visa_validto)))
                if hasattr(crew, 'visa_issuer') and crew.visa_issuer:
                    L.append(self.p.LOC('91', co.alpha2to3(crew.visa_issuer)))
        return L


# Master Crew List ======================================================={{{1

# MCLObject --------------------------------------------------------------{{{2
class MCLObject(tuple):
    """Object used for comparison and manipulation of records in the MCL.  This
    object will be initialized with a record that can either be the result of a
    Rave iteration or the result of iterating thru records in the entity 'mcl'.
    This way it is possible to compare the stored data with actual data."""

    # NOTE: The three first fields are used to decide whether the receiving
    # system needs a combination of 'delete' and 'add' or simply a 'change'.
    # See CR 355 for details.  (When e.g. a name is changed, we cannot simply
    # send a 'change' record, since the recieving system will not be able to
    # find the record that has been changed, for USA the main fields used for
    # identification are 'sn', 'gn' and 'birthday'.)
    attribs = (
        'sn', 'gn', 'birthday', 'gender', 'nationality', 'birth_place',
        'birth_state', 'birth_country', 'res_street', 'res_city',
        'res_postal_code', 'res_country', 'dhs_category', 'passport',
        'passport_issuer', 'passport_validto', 'license',
        'license_issuer', 'license_validto',
    )
    # The three first fields are important, see comment above.
    nr_key_attribs = 3

    def __new__(cls, rec):
        """Using tuple to simplify comparison operations."""
        return tuple.__new__(cls, [cls.strify(getattr(rec, x)) for x in cls.attribs])

    def __init__(self, rec):
        """Save reference to original object."""
        self.rec = rec

    def keys(self):
        """Return fields that decide if we are dealing with a 'DELETE' + 'NEW',
        or simply a 'CHANGE'."""
        return self[:self.nr_key_attribs]

    def rec_copy(self):
        """Return a dummy object, with attributes copied."""
        class RecCopy:
            pass
        r = RecCopy()
        for attr in self.attribs:
            setattr(r, attr, self.strify(getattr(self.rec, attr)))
        return r

    def add_rec(self, country_ref):
        """Add a new record to the 'mcl' table."""
        crew_ref = TM.crew[self.rec.id,]
        newrec = TM.mcl.create((country_ref, crew_ref))
        for a in self.attribs:
            setattr(newrec, a, str(getattr(self.rec, a)))

    def del_rec(self):
        """Remove a record from the 'mcl' table."""
        self.rec.remove()

    def mod_rec(self, other):
        """Modify a record in the 'mcl' table."""
        for a in self.attribs:
            setattr(self.rec, a, str(getattr(other.rec, a)))

    @classmethod
    def strify(cls,attr):
        if attr is None:
            return ''
        return str(attr)


# MasterCrewList ---------------------------------------------------------{{{2
class MasterCrewList(list):
    """Master Crew List, used by US Dept of Homeland Security, to this date it
    is not known if other countries use this.  This class holds lists of all
    interchanges to be sent, both added, changed and deleted crew.  MCL() is
    used to create each of these interchange types."""
    def __init__(self, rosters, country):
        """Each change type (added, changed, deleted) has to  be in it's own
        message."""
        list.__init__(self)
        self.country = country

        if country == 'US':
            self.p = paxlst_impl.MCL_US
        else:
            raise ValueError("MasterCrewList(): Current implementation only supports MCL to 'US'.")

        self.now = now()
        # This could potentially differ between implementations, but since we
        # right now only use MCL for USA...
        added, changed, deleted = self.get_diffs(rosters)
        if added:
            self.extend(MCL(self, added, 'G'))
        if deleted:
            self.extend(MCL(self, deleted, 'H'))
        if changed:
            self.extend(MCL(self, changed, 'I'))

    def __str__(self):
        """For basic tests only."""
        return '\n'.join(self)

    def get_diffs(self, rosters):
        """Compare list of roster values with the ones in our local "copy" of
        MCL.  Return three lists: added, changed and deleted."""
        added = []
        changed = []
        deleted = []

        # Data from the 'mcl' table with crew id as key.
        mcl = {}
        # Data from a roster iteration with crew id as key.
        latest = {}

        country_ref = TM.country[self.country,]
        for rec in country_ref.referers('mcl', 'mcl'):
            try:
                mcl[rec.id.id] = MCLObject(rec)
            except Exception, e:
                warnings.warn("Record in entity 'mcl' refers to noexisting crew '%s'. [%s]" % (
                    rec.getRefI('id'), e))
                rec.remove()

        for rec in rosters:
            latest[rec.id] = MCLObject(rec)

        for id in latest:
            if not id in mcl:
                added.append(latest[id].rec)
                latest[id].add_rec(country_ref)
            elif latest[id] != mcl[id]:
                if latest[id].keys() != mcl[id].keys():
                    # any of 'gn', 'sn', 'birthday' was modified
                    added.append(latest[id].rec)
                    # Using a copy of 'rec', since rec is changed later (by
                    # mod_rec()) and we want to keep the original values.
                    deleted.append(mcl[id].rec_copy())
                else:
                    # any other attribute was changed
                    changed.append(latest[id].rec)
                mcl[id].mod_rec(latest[id])

        for id in mcl:
            if not id in latest:
                deleted.append(mcl[id].rec)
                mcl[id].del_rec()

        return added, changed, deleted


# MCL --------------------------------------------------------------------{{{2
class MCL(CrewList):
    """Actual Master Crew List message."""
    def __init__(self, caller, rosters, status):
        CrewList.__init__(self)
        self.status = status
        # Use data from parent object
        self.p = caller.p
        self.now = caller.now
        self.ticket = db.get_mcl_ticket(country=caller.country,
                changetype=status)
        self.make_list(rosters)

    def make_list(self, rosters):
        """Create the MCL."""
        mesno = 1
        i, m = self.get_interchange() 
        m.unh.status.sequence = '%02d' % mesno
        # NOTE: CNT is the total count of crew reported on this MCL message,
        # not the total on all MCLs.
        crew_per_msg = 1
        for crew in rosters:
            sg4 = self.segment_group_4(crew)
            cnt = self.p.CNT(crew_per_msg)
            # Add two for the continuation marker
            if i.size() + sg4.size() + cnt.size() + 2 > conf.maxsize:
                if mesno == 1:
                    m.unh.status.first_last = 'C'
                mesno += 1
                m.append(self.p.CNT(crew_per_msg - 1))
                self.ticket.save(crew_per_msg - 1)
                self.append(str(i))
                i, m = self.get_interchange()
                m.unh.status.sequence = '%02d' % mesno
                crew_per_msg = 1
            else:
                crew_per_msg += 1
            m.extend(sg4)
        m.append(cnt)
        if mesno != 1:
            m.unh.status.first_last = 'F'
        self.ticket.save(crew_per_msg)
        self.append(str(i))

    def get_interchange(self):
        """Create the "envelope"."""
        seqno = self.ticket.get_seqno()
        iref = "SK%06d" % seqno
        i = self.p.Interchange(self.now, iref)
        f = self.p.FunctionalGroup(conf.sender_id, self.now, reference='%s10' % iref)
        m = self.p.Message(reference="%s11" % iref, access_reference="%s%02d" % (self.ticket.refid, self.ticket.revision))
        f.append(m)
        i.append(f)

        # BGM: Beginning of message
        m.append(self.p.BGM('336', self.status))

        # RFF: Reference, TN Transaction reference number
        m.append(self.p.RFF('TN', self.ticket.refid, self.ticket.revision))

        # Reporter
        m.extend(self.segment_group_1())

        # "Flight itinerary" (different meaning for MCL)
        m.extend(self.segment_group_2())
        return i, m
         
    def segment_group_2(self):
        """
        Segment group 2: TDT-DTM-SG3
        MCL uses a somewhat different version, since MCL does not handle a
        flight.
        """
        L = []

        # TDT: Transport information
        L.append(self.p.TDT("%s%02.2dMCL" % (conf.mcl_carrier, self.ticket.revision), conf.mcl_carrier))
        # DTM: Date/Time/Period
        # - According to the UN/EDIFACT specification the DTM tag is mandatory in
        #   this location. The US and China specifications however contradicts
        #   the official UN specification by not specifying the DTM tag in this
        #   location.
        #
        #   Tests conducted with China indicates that including the DTM causes
        #   errors and it is therefore commented out.

        # Segment group 3 (associated locations and dates)
        # Filing location/date
        L.append(self.p.LOC('188', 'XXX'))
        L.append(self.p.DTM('554', self.now))

        # Segment group 3 (associated locations and dates)
        # Reporting location/date
        L.append(self.p.LOC('172', 'TST'))
        L.append(self.p.DTM('554', self.now))
        return L

    def segment_group_4(self, crew):
        """
        Segment group 4:
        NAD-ATT-DTM-MEA-GEI-FTX-LOC-COM-EMP-NAT-RFF-SG5-SG6-SG7
        Crew member details.
        """
        L = edifact.Elist()

        # NAD: Name and address
        nad = self.p.NAD('FM', crew.sn, gn=crew.gn, street=crew.res_street, city=crew.res_city, postal_id=crew.res_postal_code, country=co.alpha2to3(crew.res_country))

        L.append(nad)

        # ATT: Gender
        L.append(self.p.ATT(crew.gender))

        # DTM: Date of birth
        # [acosta:08/274@16:26] Had to use AbsTime here, since if the record
        # came from the database, then it would be stored as a string.
        L.append(self.p.DTM('329', AbsTime(crew.birthday)))

        # MEA: Measurements, e.g. height (not used)
        # GEI: Change of information indicator. (not used)
        # FTX: Free text (e.g. ticketing) (not used)

        # LOC: Country of residence (unique for MCL)
        L.append(self.p.LOC('174', co.alpha2to3(crew.res_country)))
        # LOC: Associated locations (in this case place of birth).
        L.append(self.p.LOC('180', co.alpha2to3(crew.birth_country),
            city_of_birth=crew.birth_place,
            province_of_birth=crew.birth_state))

        # COM: Communications information. (not used)

        # EMP: Employment details
        L.append(self.p.EMP(crew.dhs_category))

        # NAT: Nationality
        L.append(self.p.NAT(co.alpha2to3(crew.nationality)))

        # RFF: Reference (reservation details) (not used).

        # Segment Group 5 (PASSPORT)
        L.extend(self.segment_group_5(crew, 'PASSPORT'))

        # Segment Group 5 (LICENCE)
        L.extend(self.segment_group_5(crew, 'LICENCE'))
        return L


# CrewMainfest ==========================================================={{{1
class CrewManifest(CrewList):
    def __init__(self, legs, country):
        CrewList.__init__(self)
        try:
            leg = legs[0]
        except:
            raise ValueError("No leg found.")
        self.now = now()
        # strip '_fo' 'RU' before setting instance variable
        self.country = "RU" if country == "RU_fo" else country
        # NOTE: SAS has to provide information
        # about the special recipients for CN,JP and TH
        self.document_id = 'C'
        if country == 'JP':
            self.p = paxlst_impl.PAXLST_JP
            self.recipient = 'JPCSAPIS'
        elif country == 'TH':
            self.p = paxlst_impl.PAXLST_TH
            self.recipient = '*TH*'
        elif country == 'US':
            self.p = paxlst_impl.PAXLST_US
            self.recipient = 'USCSAPIS'
        elif country == 'CA':
            self.p = paxlst_impl.PAXLST_CA
            self.recipient = 'CBSAAPIS'
        elif country == 'CN':
            self.p = paxlst_impl.PAXLST_CN
            self.recipient = 'CNADAPIS'
        elif country == 'IN':
            self.p = paxlst_impl.PAXLST_IN
            self.recipient = 'FABINXS'
        elif country == 'DK':
            self.p = paxlst_impl.PAXLST_DK
            self.recipient = 'DKGOVAPI'
        elif country == 'NO':
            self.p = paxlst_impl.PAXLST_NO
            self.recipient = 'NORAPIS'
        elif country == 'MX':
            self.p = paxlst_impl.PAXLST_MX
            self.recipient = 'MEXTTXH' # Test
            # self.recipient = 'MEXIMXH' # Production
        elif country == 'GB':
            self.p = paxlst_impl.PAXLST_UK
            self.recipient = 'UKBAUS' # US PAXLST option, otherwise 'UKBAOP'
            # For BGM segment, unique for UK
            # NOTE: The value of 'C' is OK with UK, indicates that it's a
            # pre-departure message
            if int(self.now) > int(leg.std_utc) - 45: # check for slack, maybe it should be less??
                self.document_id = 'CLOB' # Confirmed crew, msg sent <60m before STD
        elif country == 'TR':
            self.p = paxlst_impl.PAXLST_TR
            self.recipient = 'TR.DGMM'
        # RU should work as for UK
        elif country == 'RU':
            self.p = paxlst_impl.PAXLST_RU
            self.recipient = 'ACDPDP'
        elif country == 'RU_fo':
            self.p = paxlst_impl.PAXLST_RU_fo
            self.recipient = 'ACDPDP'
        else:
            raise ValueError("CrewManifest(): country must be one of 'JP', 'TH', 'US', 'CN', 'IN', 'GB', 'RU', 'RU_fo', 'TR', 'DK', 'MX', 'CA', 'NO'.")
        self.ticket = db.get_cl_ticket(country=self.country, fd=leg.fd, udor=leg.udor, adep=leg.adep) # XXX
        self.make_list(leg)

    def make_list(self, leg):
        """Create the crew list."""
        mesno = 1
        i, m = self.get_interchange(leg)
        m.unh.status.sequence = '%02d' % mesno
        crew_per_msg = 1
        # NOTE: For crew manifests CNT is total number of crew on the
        # *flight*, not the total number of crew sent in each message.
        all_crew = leg.chain('crew')
        nr_of_crew = len(all_crew)
        cnt = self.p.CNT(nr_of_crew)
        for crew in (all_crew):
            # Use a temporary list, if message size flows over, then add this
            # list to a new interchange.
            sg4 = self.segment_group_4(crew, leg)
            # Add two for the continuation marker
            if i.size() + sg4.size() + cnt.size() + 2 > conf.maxsize:
                if mesno == 1:
                    m.unh.status.first_last = 'C'
                mesno += 1
                m.append(cnt)
                self.ticket.save(crew_per_msg - 1)
                self.append(str(i))
                i, m = self.get_interchange(leg)
                m.unh.status.sequence = '%02d' % mesno
                crew_per_msg = 1
            else:
                crew_per_msg += 1
            m.extend(sg4)
        m.append(cnt)
        if mesno != 1:
            m.unh.status.first_last = 'F'
        self.ticket.save(crew_per_msg)
        self.append(str(i))

    def get_interchange(self, leg):
        """Create the "envelope"."""
        seqno = self.ticket.get_seqno()
        iref = "SK%06d" % seqno
        if leg.ac_owner == "SVS":
            conf.sender_id = 'SAS Link'
        else:
            conf.sender_id = 'SCANDINAVIAN AIRLINES'
        
        ref_tmp = iref
        if self.country == "CA":
            refid_no1, refid_no2 = "%s" %(str(tools.edi_date(leg.std_utc))), "%s" %(str(tools.edi_time(leg.std_utc)))
            refid_no = "%s%s" %(refid_no1,refid_no2)
            ref_tmp = refid_no
        i = self.p.Interchange(conf.sender_id, self.recipient, self.now, ref_tmp) # XXX
        #i = self.p.Interchange(conf.sender_id, self.recipient, self.now, mesno)
        reference_tmp = '%s10' % iref
        if self.country == "CA":
            reference_tmp = refid_no2
        f = self.p.FunctionalGroup(conf.sender_id, self.recipient, self.now, reference=reference_tmp)
        
        access_reference_tmp ="%s%02d" % (self.ticket.refid, self.ticket.revision)
        reference_tmp1 = "%s11" % iref
        if self.country == "NO":
            fd_no = fd_parser(leg.fd)
            refid_no = "%s%s%s/%s/%s" % ( fd_no.carrier,
                fd_no.number, fd_no.suffix, str(tools.edi_date(leg.std_utc)), str(tools.edi_time(leg.std_utc)))
            access_reference_tmp = refid_no

        if self.country == "CA":
            fd_no = fd_parser(leg.fd)
            refid_no3 = "%s%s%s/%s/%s" % ( fd_no.carrier,fd_no.number, fd_no.suffix, refid_no1, refid_no2)
            access_reference_tmp = refid_no3
            reference_tmp1 = refid_no
        m = self.p.Message(reference=reference_tmp1, access_reference=access_reference_tmp)
        f.append(m)
        i.append(f)

        # Beginning of message
        m.append(self.p.BGM('250', self.document_id))

        # Reference (not allowed for JP, NO)
        if self.country not in ('JP', 'NO'):
            m.append(self.p.RFF('TN', self.ticket.refid, self.ticket.revision))

        # Reporter
        m.extend(self.segment_group_1())

        # Flight itinerary
        m.extend(self.segment_group_2(leg))

        return i, m
    
    def segment_group_5_CA(self, crew, doctype):
        """
        Segment group 5: DOC-DTM-GEI-RFF-LOC-CPI-QTY specially for CA
        Travel document details.
        """
        L = []
        if doctype == 'PASSPORT':
            if hasattr(crew, 'passport') and crew.passport:
                # DOC: Document details.
                L.append(self.p.DOC('P', crew.passport))

                # DTM: Dates/times related to document.
                L.append(self.p.DTM('36', AbsTime(crew.passport_validto)))

                # GEI: Processing information (not used)

                # RFF: Reference (not used)

                # LOC: Place (country, city) where document was issued.
                if hasattr(crew, 'passport_issuer') and crew.passport_issuer:
                    L.append(self.p.LOC('91', crew.passport_issuer))
                    
                # CPI: Charge payment instructions (not used)
                # QTY: Quantity (not used)
        elif doctype == 'LICENCE':
            if hasattr(crew, 'license') and crew.license:
                L.append(self.p.DOC('L', crew.license))
                L.append(self.p.DTM('36', AbsTime(crew.license_validto)))
                if hasattr(crew, 'license_issuer') and crew.license_issuer:
                    L.append(self.p.LOC('91', crew.license_issuer))
                    
        elif doctype == 'VISA':
            if hasattr(crew, 'visa') and crew.visa:
                L.append(self.p.DOC('V', crew.visa))
                if hasattr(crew, 'visa_validto') and crew.visa_validto:
                    L.append(self.p.DTM('36', AbsTime(crew.visa_validto)))
                if hasattr(crew, 'visa_issuer') and crew.visa_issuer:
                    L.append(self.p.LOC('91', crew.visa_issuer))
                    
        return L


    def segment_group_2(self, leg):
        """
        Segment group 2: TDT-DTM-SG3
        MCL uses a somewhat different version, since MCL does not handle a
        flight.
        """
        L = []
        # Flight info
        # NOTE: Suffix is not used
        L.append(self.p.TDT("%s%03d" % (leg.fd_carrier, leg.fd_number), leg.fd_carrier))
        # DTM: Date/Time/Period
        # - According to the UN/EDIFACT specification the DTM tag is mandatory in
        #   this location. The US and China specifications however contradicts
        #   the official UN specification by not specifying the DTM tag in this
        #   location.
        #
        #   Tests conducted with China indicates that including the DTM causes
        #   errors and it is therefore commented out.

        # Segment group 3 
        L.append(self.p.LOC('125', leg.adep))
        L.append(self.p.DTM('189', leg.std))

        # Segment group 3 
        L.append(self.p.LOC('87', leg.ades))
        L.append(self.p.DTM('232', leg.sta))

        # LOC 92 (subsequent port) not used
        return L

    def segment_group_4(self, crew, leg):
        """
        Segment group 4:
        NAD-ATT-DTM-MEA-GEI-FTX-LOC-COM-EMP-NAT-RFF-SG5-SG6-SG7
        Crew member details.
        """
        L = edifact.Elist()

        # NAD: Name and Address
        if self.country == "CA":
            nad = self.p.NAD('FM', crew.sn, gn=crew.gn, street=crew.res_street, city=crew.res_city, postal_id=crew.res_postal_code, country=crew.res_country)
        else:
            nad = self.p.NAD('FM', crew.sn, gn=crew.gn, street=crew.res_street, city=crew.res_city, postal_id=crew.res_postal_code, country=co.alpha2to3(crew.res_country))
    
        L.append(nad)
      
        # ATT: Gender
        L.append(self.p.ATT(crew.gender))

        # DTM: Date of birth
        L.append(self.p.DTM('329', crew.birthday))

        # MEA: Measurements (not used)
        # GEI: Change of information indicator. (not used)
        # FTX: Free text (not used)

        # LOC: Place of birth and other locations
        # Question: Is this really for US only?
        if leg.end_country == 'US':
            # 22 - airport of first arrival
            L.append(self.p.LOC('22', leg.ades))
            # 174 country of residence
            L.append(self.p.LOC('174', co.alpha2to3(crew.res_country)))
        # 178 - Airport of embarkation (not mentioned for UK)
        L.append(self.p.LOC('178', leg.adep))
        # 179 - Airport of debarkation (not mentioned for UK)
        L.append(self.p.LOC('179', leg.ades))

        # 180 - Place of birth
        # [acosta:09/127@01:55] Not mentioned in UK document.
        if self.country == "NO":
            tmp_locstr = "LOC+180+"+ str(co.alpha2to3(crew.birth_country)) + ":::" + latin1_to_edifact(crew.birth_place, level="MRZ") + "'"
            L.append(tmp_locstr)
        elif self.country == "CA":
            tmp_locstr = "LOC+180+"+ str(crew.birth_country) + "'"
            L.append(tmp_locstr)
        else:
            L.append(self.p.LOC('180', co.alpha2to3(crew.birth_country),
                city_of_birth=crew.birth_place,
                province_of_birth=crew.birth_state))

        # COM: Communcation contact (only used for TR)
        if leg.end_country == 'TR':
            com = self.p.COM('658')
            fon = str(crew.phone_primary)
            fon = fon.replace('+', '00')
            com.contact1.id = fon
            com.contact1.qual = 'TE'
            L.append(com)

        # EMP: Employment details (only sent to US Authorities)
        if self.country in ['US', "RU", "RU_fo"]:
            L.append(self.p.EMP(crew.dhs_category)) 

        # NAT: Nationality
        if self.country == "CA":
            L.append(self.p.NAT(crew.nationality))
        else:
            L.append(self.p.NAT(co.alpha2to3(crew.nationality)))

        # RFF: Reference (not used, passengers only [booking ref])

        # Segment Group 5 (PASSPORT)
        if self.country == "CA":
            L.extend(self.segment_group_5_CA(crew, 'PASSPORT'))
        else:
            L.extend(self.segment_group_5(crew, 'PASSPORT'))

        # Segment Group 5 (LICENCE), Not used for UK
        if self.country not in ('GB',):
            if self.country == "CA":
                L.extend(self.segment_group_5_CA(crew, 'LICENCE'))
            else:
                L.extend(self.segment_group_5(crew, 'LICENCE'))

        # MAX TWO DOC Segments per crew
        #if self.country == 'CN':
        #    L.extend(self.segment_group_5(crew, 'VISA'))

        return L


# SITAAddresses =========================================================={{{1
class SITAAddresses(object):
    """Help class. Provide functions that can get SITA addresses from the site
    configuration (XML)."""

    # This must match the "xpath" in XML site configuration.
    address_path_fmt = "dig_reports/SITA_addresses/%s"

    def __init__(self, country):
        self.country = country
        self.sc = ServiceConfig()
        self.__sender = None
        self.__recipents = None

    @property
    def sender(self):
        """Get SITA address of sender (e.g. CPHBUSK), this address is stored in
        site configuration: dig_reports/SITA_addresses/sender"""
        if self.__sender is None:
            self.__sender = self.sc.getPropertyValue(self.address_path_fmt % 'sender')
        return self.__sender

    @property
    def recipients(self):
        """Return list of SITA recipient addresses for this country."""
        # Transform CN to cn, and GB to gb
        if self.__recipents is None:
            self.__recipents = [x[1] for x in self.sc.getProperties(self.address_path_fmt % (
                'recipients/%s' % self.country.lower()))]
        return self.__recipents

    def add_recipient(self, recipient, message):
        """Prepend message with two rows of SITA addresses (for Telex) like
        this:

        PEKKN1E
        .CPHBUSK
        UNA:+.? 'UNB+UNOA:4+SCANDINAVIAN AIRLINES:ZZ+USCSAPIS:ZZ+090623:........

        """
        return '\n'.join((recipient, "." + self.sender, message))


# functions =============================================================={{{1

# crewlist ---------------------------------------------------------------{{{2
def crewlist(udor=None, fd=None, adep=None, country="US"):
    """Return Crew Manifest, which is a list of EDIFACT interchanges."""
    return [str(x) for x in CrewManifest(crew_iter.crewlist(fd, udor, adep), country)]


# mcl --------------------------------------------------------------------{{{2
def mcl(date=None, country="US"):
    """Return Master Crew List (US), which is a list of EDIFACT
    interchanges."""
    if date is None:
        date = now()
    else:
        date = AbsTime(date)
    return [str(x) for x in MasterCrewList(crew_iter.mcl(date), country)]


# complete_mcl -----------------------------------------------------------{{{2
def complete_mcl(date=None, country="US"):
    """Return MCL with *all* long-haul crew, to be used for initial load
    or to sync our copy with MCL."""
    reset_mcl(country)
    return mcl(date, country)


# reset_mcl --------------------------------------------------------------{{{2
def reset_mcl(country):
    """Remove all entries from "our" MCL."""
    for row in TM.country[country,].referers('mcl', 'mcl'):
        row.remove()


# now --------------------------------------------------------------------{{{2
def now():
    """Return current time."""
    return rave.eval('fundamental.%now%')[0]


# remove_fcmerror --------------------------------------------------------{{{2
def remove_fcmerror(fd, udor, adep):
    """Remove flight_leg_attr with value FCMERROR."""
    fd = fd_parser(fd).flight_descriptor
    udor = AbsTime(udor)
    adep_ref = TM.airport[(adep,)]
    flight_leg_key = TM.flight_leg[(udor, fd, adep_ref)]
    set_key = TM.leg_attr_set[('FCMERROR',)]
    try:
        record = TM.flight_leg_attr[(flight_leg_key, set_key)]
        record.remove()
    except:
        pass


# bit --------------------------------------------------------------------{{{2
def bit():
    """Basic test"""
    #print CrewManifest(crew_iter.crewlist("SK937", "20070716", "CPH"), "US")
    #print CrewManifest(crew_iter.crewlist("SK925", "20080301", "CPH"), "US")
    #for x in crew_iter.mcl("20080314"):
    #    print x

    edifact.debug = False
    #print '\n'.join(crewlist("20080301", "SK973", "CPH"))
    #print '\n'.join(mcl())
    print '\n'.join(complete_mcl())
    #print complete_mcl()


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    bit()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

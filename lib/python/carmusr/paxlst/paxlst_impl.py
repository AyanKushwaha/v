# [acosta:07/327@16:52] Created.

"""
PAXLST implementations for JP, US, TH, CN and IN
Very little information about the JP and TH formats.
"""

import utils.edifact.tools as tools
from utils.edifact.messages import PAXLST
from utils.edifact import latin1_to_edifact, alnum


# PAXLST_US =============================================================={{{1
class PAXLST_US(PAXLST):
    """
    General structure:

    UNA UNB UNG UNH BGM RFF         Segment group 0 (1)
    NAD COM                         Segment group 1 (1 - 5)     Sender's ref
    TDT                             Segment group 2 (1 - 10)    Flight id
    LOC DTM                         Segment group 3 (1 - 99)    Leg info
    NAD ATT DTM GEI LOC EMP NAT RFF Segment group 4 (1 - 99999) Crew
    DOC DTM LOC                     Segment group 5 (1 - 5)     Crew Docs
    CNT UNT UNE UNZ                 Segment group 0 (1)
    """
    # UNB ----------------------------------------------------------------{{{3
    class UNB(PAXLST.UNB):
        def __init__(self, sender=None, recipient=None, date_time=None, reference=None):
            """
            sender      : 0004       Sender identification.
                - sender_id = 'MCCL*TSA' for Master Crew List

            recipient   : 0010       Recipient identification.
                - for tests use 'DHSTEST' as receiver.id

            date_time   : 0017, 0019 Date/time of preparation.
            reference   : 0020       Interchange control reference. 
            """
            PAXLST.UNB.__init__(self)
            assert None not in (sender, recipient, reference) or date_time is None, \
                    "Required parameters are ('sender', 'recipient', 'date_time', 'reference')."
            self.syntax.id = 'UNOA'
            self.syntax.version = '4'
            self.sender.id = sender 
            self.sender.qual = 'ZZ'
            self.recipient.id = recipient
            self.recipient.qual = 'ZZ'
            self.date_time.date = tools.edi_date(date_time)
            self.date_time.time = tools.edi_time(date_time)
            self.reference = reference
            self.application = 'APIS'


    # UNG ----------------------------------------------------------------{{{3
    class UNG(PAXLST.UNG):
        """
        NOTE: This segment (together with with UNE) is MANDATORY for DHS (USA)
        """
        def __init__(self, sender=None, recipient=None, date_time=None, reference=None):
            """
            sender      : 0040       Application sender's identification.
            recipient   : 0044       Recipient's indentification.
                - for tests use 'DHSTEST' (US PAXLST)
            date_time   : 0017, 0019 Date/Time of preparation. (AbsTime)
            reference   : 0048       Functional group ref number.
            NOTE! this could be different from reference in UNB
            """
            PAXLST.UNG.__init__(self)
            assert None not in (sender, recipient, reference) or date_time is not None, \
                    "Required parameters are ('sender', 'recipient', 'date_time', 'reference')."
            self.group_id = 'PAXLST'
            self.sender.id = sender
            self.recipient.id = recipient
            self.date_time.date = tools.edi_date(date_time)
            self.date_time.time = tools.edi_time(date_time)
            self.reference = reference
            self.agency = 'UN'
            self.version.number = 'D'
            self.version.release = '05B'


    # UNH ----------------------------------------------------------------{{{3
    class UNH(PAXLST.UNH):
        def __init__(self, reference=None, access_reference=None,
                sequence=None, first_last=None):
            """
            reference        : 0062       Message reference number
            access_reference : 0068       Common access reference
            sequence         : 0070       Sequence of transfers (01, 02, ...)
            first_last       : 0072       'C' or 'F'
            Note! single message will have 01, sequence of three messages will have
            '01:C', '02', '03:F'
            """
            PAXLST.UNH.__init__(self)
            assert reference is not None, "Required parameters are ('reference')."
            self.reference = reference
            self.id.association = 'IATA'
            if not access_reference is None:
                self.access_reference = access_reference
            if not sequence is None:
                self.status.sequence = sequence
            if not first_last is None:
                assert first_last in ('', 'C', 'F'), "first_last must be one of ('', 'C', 'F')"
                self.status.first_last = first_last


    # ATT ----------------------------------------------------------------{{{3
    class ATT(PAXLST.ATT):
        """ Used to identify gender. """
        def __init__(self, gender):
            """
            detail : C956      Attribute detail
                'M'   - Male
                'F'   - Female
            """
            assert gender in ('M', 'F'), "Gender has to be one of ('M', 'F')"
            PAXLST.ATT.__init__(self)
            self.qual = '2' # Attribute refers to a person
            self.detail = gender


    # BGM ----------------------------------------------------------------{{{3
    class BGM(PAXLST.BGM):
        def __init__(self, name_code, document_id):
            """
            name_code   : 1001     Document name code
                '250'    - Crew List Declaration
                '336'    - Master Crew List.
            
            document_id : 1004     Document id
                For Crew List:
                'C'      - Passenger Flight Regular Scheduled Crew.
                'CC'     - Passenger Flight, Crew Change.
                'B'      - Cargo Flight, Regular Scheduled Crew.
                'BC'     - Cargo Flight, Crew Change.
                'A'      - Overflight, Passenger.
                'D'      - Overflight, Cargo.
                'E'      - Domestic Continuance, Passenger Flight, Regular Scheduled.
                'EC'     - Domestic Continuance, Passenger Flight, Crew Change.
                'F'      - Domestic Continuance, Cargo Flight, Regular Scheduled.
                'FC'     - Domestic Continuance, Cargo Flight, Crew Change.
                For Master Crew List:
                'G'      - "Add" record
                'H'      - "Delete" record
                'I'      - "Change" record
            """
            PAXLST.BGM.__init__(self)
            self.name = name_code
            self.id = document_id


    # CNT ----------------------------------------------------------------{{{3
    class CNT(PAXLST.CNT):
        def __init__(self, quantity, type_code_qual='41'):
            """
            type_code_qual  : 6069     Control total type code qualifier
                '41'    - Total number of crew (not reported number)
                '42'    - Total number of passengers (not reported number)

            number          : 6066     Control total quantity
            """
            PAXLST.CNT.__init__(self)
            self.control.qual = type_code_qual
            self.control.quantity = quantity


    # DOC ----------------------------------------------------------------{{{3
    class DOC(PAXLST.DOC):
        def __init__(self, code, id):
            """
            code    : 1001     Document name code
                'P'     - Passport
                'C'     - Permanent resident card
                'A'     - Resident alien card
                'M'     - US Military ID
                'T'     - Re-entry permit or refugee permit
                'I'     - NEXUS/SENTRI card
                'F'     - Facilitation card
                'L'     - Pilots license (crew members only)

            id       : 1004     Document identifier
            """
            PAXLST.DOC.__init__(self)
            self.name.code = code
            self.name.code_list = '110' # US DHS Special codes
            self.name.agency = '111' # Dept of Homeland Security
            # NOTE: US authorities have an extra restriction on the document
            # identifier, it can't contain any dashes '-' or other special
            # characters cf. WP Int-FAT 327. I have not seen this restriction
            # anywhere else... [acosta:09/114@17:35] 
            self.details = alnum(id)


    # DTM ----------------------------------------------------------------{{{3
    class DTM(PAXLST.DTM):
        def __init__(self, qual, date_time):
            """
            qual      :  2005       Date or time or period function code qualifier 
                '36'    - Date of expire for passport
                '189'   - STD               Question: should it be atd or std?
                '232'   - STA
                '554'   - Master Crew List arrival and departure
                '329'   - Date of birth

            date_time :  2380        Date or time or period text

            format_code :  2379        Date or time or period format code
                '101'   - yymmdd
                '201'   - yymmddHHMM   # Question: Why is not '203' used (with century)?
            """
            PAXLST.DTM.__init__(self)
            self.date_time.qual = qual
            if int(qual) in (36, 329):
                self.date_time.text = tools.edi_date(date_time)
            else:
                self.date_time.text = tools.edi_datetime(date_time)
                self.date_time.format = '201'


    # EMP ----------------------------------------------------------------{{{3
    class EMP(PAXLST.EMP):
        def __init__(self, category):
            """
            category    : 9005      Employment category description code
                'CR1'   - Cockpit crew and individuals in cockpit
                'CR2'   - Cabin crew
                'CR3'   - Airline operation management with cockpit access.
                'CR4'   - Cargo non-cockpit crew and/or non-crew individuals.
                'CR5'   - Pilots on A/C but not on duty (deadhead).
            """
            PAXLST.EMP.__init__(self)
            self.qual = '1' # Primary employment
            self.category.code = category
            self.category.code_list = '110' # US DHS Special Codes
            self.category.agency = '111' # Dept of Homeland Security


    # GEI ----------------------------------------------------------------{{{3
    class GEI(PAXLST.GEI):
        def __init__(self, indicator):
            """
            indicator   : 7365      Processing indicator description code
                '36'    - Changed information (only changed data sent)
                'ZZZ'   - Mutually defined (in this context: verified info)
            """
            PAXLST.GEI.__init__(self)
            self.qual = '4' # Party type information
            self.indicator = indicator


    # LOC ----------------------------------------------------------------{{{3
    class LOC(PAXLST.LOC):
        def __init__(self, qual, id, city_of_birth=None, province_of_birth=None):
            """
            qual    : 3227      Location function code qualifier
                '22'    - Airport of first arrival into US
                '87'    - ADES
                '91'    - Gate Pass issue location/place of document issue.
                '92'    - ADEP and ADES  (Domestic US, routing)
                '125'   - ADEP (From/to USA and overflight)
                '174'   - Country of residence.
                '178'   - Airport of embarkation.
                '179'   - Airport of debarkation.
                '180'   - Place of birth
                '188'   - Filing location (Master Crew List)
                '192'   - Reporting location (Master Crew List) (Correct loc)

            location: 3225      Location name code (in this case three letter IATA code)

            city_of_birth     : 3222        First related location name
                - City of birth (crew reporting only)

            province_of_birth : 3222        Second related location name
                - State or province of birth (crew reporting only)
            """
            PAXLST.LOC.__init__(self)
            self.qual = qual
            self.id = id
            if not city_of_birth is None:
                self.related1.name = latin1_to_edifact(city_of_birth, level="MRZ")
            if not province_of_birth is None and province_of_birth:
                self.related2.name = latin1_to_edifact(province_of_birth, level="MRZ")


    # NAD ----------------------------------------------------------------{{{3
    class NAD(PAXLST.NAD):
        def __init__(self, qual, sn, gn=None, mn=None, street=None, city=None,
                state=None, postal_id=None, country=None):
            """
            qual        : 3035      Party function code qualifier
                'MS'    - Document/message issuer/sender
                          (For segment group 1, use MS + last name)
                'FM'    - Crew member
                'DDT'   - Intransit Crew member

            party_id    : 3039      Party identifier
                ''      - Not used

            name_addr   : 3124      Name and address description
                ''      - Not used (unstructured)

            sn          : 3036(1)   Surname
            gn          : 3036(2)   Given name
            mn          : 3036(3)   Middle name
            street      : 3042      Street and number or P.O. box id
            city        : 3164      City name
            state       : 3229      Country sub-entity name code
            postal_id   : 3251      Postal identification code
            country     : 3207      Country name code
            """
            PAXLST.NAD.__init__(self)
            # 3036 surname:given name:middle name 
            # Use passport MRZ (Machine Readable Zone)
            # John W. Doe - DOE<<JOHN<<W - DOE:JOHN:W
            self.qual = qual

            # CR 185, Names must not contain '-' or "'"
            self.name.name1 = latin1_to_edifact(sn, level="MRZ")
            if not gn is None:
                self.name.name2 = latin1_to_edifact(gn, level="MRZ")
            if not mn is None:
                self.name.name3 = latin1_to_edifact(mn, level="MRZ")
            if not street is None:
                # Truncating street addresses longer than 35 chars
                if len(street) > 35:
                    street = street[0:35]
                self.street = latin1_to_edifact(street, level="MRZ")
            if not city is None:
                self.city = latin1_to_edifact(city, level="MRZ")
            if not state is None:
                self.state = latin1_to_edifact(state, level="MRZ")
            if not postal_id is None:
                self.postal_id = latin1_to_edifact(postal_id, level="MRZ")
            if not country is None:
                self.country = latin1_to_edifact(country, level="MRZ")


    # NAT ----------------------------------------------------------------{{{3
    class NAT(PAXLST.NAT):
        def __init__(self, nationality):
            """
            nationality:    3293    Nationality name code (three letter ISO
                                    3166 country code)
            """
            PAXLST.NAT.__init__(self)
            self.qual = '2' # Current nationality
            self.nationality = nationality

    
    # RFF -----------------------------------------------------------------{{{3
    class RFF(PAXLST.RFF):
        """
        line        : 1156      Document line identifier
            ''      - Not used (For passengers, i.e. baggage tag)
        version     : 4000      Reference version identifier
            ''      - Not used (For passengers)
        """
        def __init__(self, qual, id, revision):
            """
            qual     : 1153    Reference code qualifier
                'TN'    - Transaction reference number

            id       : 1154    Reference qualifier
                Transaction id in sender's system.

            revision : 1060    Revision identifier
                Revision id in sender's system.
            """
            PAXLST.RFF.__init__(self)
            self.reference.qual = qual
            self.reference.id = id
            self.reference.revision = revision


    # TDT ----------------------------------------------------------------{{{3
    class TDT(PAXLST.TDT):
        def __init__(self, flight_id, carrier):
            """
            flight_id   : 8028      Means of transport journey identifier
            carrier     : 3127      Carrier identifier
            """
            PAXLST.TDT.__init__(self)
            self.qual = '20' # Main carriage transport
            self.id = flight_id
            self.carrier = carrier


# MCL_US ================================================================={{{1
class MCL_US(PAXLST_US):
    """
    A few small differences from the PAXLST message used for Crew Manifests:
    - The sender_id is always 'MCCL*TSA'
    - The recipient_id is always 'USCSAPIS'
    - The applications is 'APIS'
    """
    # UNB ----------------------------------------------------------------{{{3
    class UNB(PAXLST_US.UNB):
        def __init__(self, date_time=None, reference=None):
            PAXLST_US.UNB.__init__(self, 'MCCL*TSA', 'USCSAPIS', date_time, reference)
            self.application = 'APIS'

    # UNG ----------------------------------------------------------------{{{3
    class UNG(PAXLST_US.UNG):
        def __init__(self, sender, date_time=None, reference=None):
            PAXLST_US.UNG.__init__(self, sender, 'USCSAPIS', date_time, reference)
            self.recipient.qual = 'ZZ'


# PAXLST_TH =============================================================={{{1
class PAXLST_TH(PAXLST_US):
    """
    Not much info available, assuming format identical to the US format.
    """
    # UNB ----------------------------------------------------------------{{{3
    class UNB(PAXLST_US.UNB):
        def __init__(self, sender=None, recipient=None, date_time=None, reference=None):
            PAXLST_US.UNB.__init__(self, sender, recipient, date_time, reference)
            self.application = 'BKKAIXH'


# PAXLST_JP =============================================================={{{1
# Assuming JP is identical to US
PAXLST_JP = PAXLST_US


# PAXLST_CN =============================================================={{{1
# See: Advance Passenger Information China Implementation Guide v.1.0.3 2008
class PAXLST_CN(PAXLST_US):
    # UNB ----------------------------------------------------------------{{{3
    class UNB(PAXLST_US.UNB):
        def __init__(self, sender=None, recipient=None, date_time=None, reference=None):
            PAXLST_US.UNB.__init__(self, sender, recipient, date_time, reference)
            self.application = 'APIS'

    # UNG ----------------------------------------------------------------{{{3
    class UNG(PAXLST_US.UNG):
        def __init__(self, sender=None, recipient=None, date_time=None, reference=None):
            PAXLST_US.UNG.__init__(self, sender, recipient, date_time, reference)
            self.version.release = '02B'
            self.sender.qual = 'ZZ'

    # UNH ----------------------------------------------------------------{{{3
    class UNH(PAXLST_US.UNH):
        def __init__(self, reference=None, access_reference=None, sequence=None, first_last=None):
            PAXLST_US.UNH.__init__(self, reference, access_reference)
            self.id.release = '02B'

    # LOC ----------------------------------------------------------------{{{3
    class LOC(PAXLST_US.LOC):
        def __init__(self, qual, id, city_of_birth=None, province_of_birth=None):
            if qual == "180":
                city_of_birth = None
            PAXLST_US.LOC.__init__(self, qual, id, city_of_birth, province_of_birth)

    # BGM ----------------------------------------------------------------{{{3
    class BGM(PAXLST.BGM):
        def __init__(self, name_code, document_id):
            """CN does not use document_id (1004)"""
            PAXLST.BGM.__init__(self)
            self.name = name_code

    # DOC ----------------------------------------------------------------{{{3
    class DOC(PAXLST.DOC):
        def __init__(self, code, id):
            """
            code    : 1001     Document name code
                'P'     - Passport (issuer: Yes)
                'PT'    - P.R. China Travel Permit (*)
                'PL'    - P.R. China Exit and Entry Permit (*)
                'W'     - Travel Permit to and from HK and Macao (*)
                'A'     - Travel Permit to and from HK and Maco for Public
                          Affairs (*)
                'Q'     - Travel Permit to HK and Macao (*)
                'C'     - Travel Permit of HK and Macao Residents to and from
                          Mainland (*)
                'D'     - Travel Permit of Mainland Residents to and from
                          Taiwan (*)
                'T'     - Travel Permit of Taiwan Residents to and from
                          Mainland (*)
                'S'     - Seefarer's Passport (issuer: Yes)
                'F'     - Approved non-standard identity documents used for
                          travel. (issuer: Yes, no expiry date)

                'V'     - Visa
                'AC'    - Crew Member Certificate

            id       : 1004     Document identifier
            """
            PAXLST.DOC.__init__(self)
            self.name.code = code
            self.name.code_list = '110' # Customs special code
            self.name.agency = 'ZZZ'
            self.details = id

    # TDT ----------------------------------------------------------------{{{3
    class TDT(PAXLST.TDT):
        def __init__(self, flight_id, carrier=None):
            """
            flight_id   : 8028      Means of transport journey identifier

            Carrier (3127) not used for China.
            """
            PAXLST.TDT.__init__(self)
            self.qual = '20' # Main carriage transport
            self.id = flight_id


# PAXLST_UK =============================================================={{{1
# See: e-Borders Carrier Interface Control Document for PAXLST TDI-TDN-SI
# (Annex), Doc Ref: EB-SD-00614, Issue nr 4.0
class PAXLST_UK(PAXLST_US):
    """UK accepts PAXLST/US and other implementations, there are however some
    things that differ."""
    # UNB ----------------------------------------------------------------{{{3
    class UNB(PAXLST_US.UNB):
        def __init__(self, sender=None, recipient=None, date_time=None, reference=None):
            PAXLST_US.UNB.__init__(self, sender, recipient, date_time, reference)
            self.application = 'APIS'

    # BGM ----------------------------------------------------------------{{{3
    # Removed exception for BGM (UK) since it seems to be unsupported
    # (see WP Int-FAT 358)
    # Re-introduced as part of CR 336 and updated to use "US PAXLST option" as
    # specified in document DB-SD-00614 (7.0) [acosta:09/265@13:32] 
    class BGM(PAXLST.BGM):
        def __init__(self, name_code, document_id):
            """
            name_code   : 1001     Document name code
              e-Borders PAXLST (not used here):
                '250'    - Crew List Declaration (departure and pre-departure)
                '745'    - Passenger List (not used here, departure and
                           pre-departure)
              US PAXLST option:
            ->  '250'    - Pre-departure message for crew
            ->  '250'    - Departure message for crew
                '266'    - Departure message for passengers
                '745'    - Pre-departure message for passengers
            
            document_id : 1004     Document id
              e-Borders PAXLST (not used here):
                Pre-departure (passengers and crew)
                    'CI' - Reporting pre-departure (check-in) submission.

                Departure (passengers and crew)
                    'DC' - Reporting list of departure confirmations
                    'DE' - Reporting either list of departure exceptions
                           (not used) or a nil departure exception message.

              e-Borders US PAXLST option (which we use):
                Pre-departure:
                    for passengers:
                        element 1004 is not to be used. Omitting this element
                        indicates it is a pre-departure message. If this
                        element is used the manifest data will not be processed
                        by e-Borders.
                    for crew:
                        Omitting element 1004 indicates it is a pre-departure
            ->          message. If element 1004 has any value other than
            ->          'CLOB', 'CLNB' or 'CL' this will also indicate it is a
            ->          pre-departure message.
                Departures:
                    for passengers:
                        Possible values are:
            ->              'CLOB' - departure confirmation message.
                            'CLNB' - departure exception message.
                            'CL'   - Nil departure exception message containing
                                     no passengers.
                        If this element has any value other than 'CLOB', 'CLNB'
                        or 'CL' the manifest data will not be processed by
                        e-Borders.
                    for crew:
                        Possible values are:
                            'CLOB' - departure confirmation message.
                            'CLNB' - departure exception message.
                            'CL'   - Nil departure exception messaeg containing
                                     no crew.

            document_ver: 1056     Version id
                '1.0'    - Always 1.0 for e-Borders
            ->  NOT USED for US PAXLST option. If this element is used the
                element data will not be processed by e-Borders.
            """
            # NOTE: The value of document_id will be assigned by the caller
            # (which has a idea of what time it is right now). Possible values
            # are 'C' (for pre-departure) and 'CLOB' (for departure
            # confirmation).
            PAXLST.BGM.__init__(self)
            self.name = name_code
            self.id = document_id

    # DOC ----------------------------------------------------------------{{{3
    class DOC(PAXLST.DOC):
        def __init__(self, code, id):
            """
            code    : 1001     Document name code
                'P'     - Passport (issuer: Yes)
                'G'     - Group Passport
                'A'     - National Identity Card or Resident Card (Exact use
                          defined by issuing state)
                'C'     - National Identity Card or Resident Card (Exact use
                          defined by issuing state)
                'I'     - National Identity Card or Resident Card (Exact use
                          defined by issuing state)
                'M'     - Military Identification
                'D'     - Diplomatic Identification
                'AC'    - Crew Member Certificate
                'IP'    - Passport Card
                'F'     - Approved non-standard identity documents used for
                          travel.

            id       : 1004     Document identifier
            """
            PAXLST.DOC.__init__(self)
            self.name.code = code
            self.name.code_list = '110' # Customs special code
            self.name.agency = '109'
            self.details = id

# PAXLST_CA  =============================================================={{{1
# Assuming CA is *almost* identical to UK ...
# ... but a few changes (ref SKCMS-2938)
class PAXLST_CA(PAXLST_UK):
    # UNB ----------------------------------------------------------------{{{3
    class UNB(PAXLST_US.UNB):
        def __init__(self, sender=None, recipient=None, date_time=None, reference=None):
            PAXLST_US.UNB.__init__(self, sender, recipient, date_time, reference)
            self.application = 'APIS'
            
    class EMP(PAXLST.EMP):
        def __init__(self, category):
            """
            category    : 9005      Employment category description code
                'CR1'   - Cockpit crew and individuals in cockpit
                'CR2'   - Cabin crew
                'CR3'   - Airline operation management with cockpit access.
                'CR4'   - Cargo non-cockpit crew and/or non-crew individuals.
                'CR5'   - Pilots on A/C but not on duty (deadhead).
            """
            PAXLST.EMP.__init__(self)
            self.qual = '1'
            self.category.code = category

        # DOC ----------------------------------------------------------------{{{3
    class DOC(PAXLST.DOC):
        def __init__(self, code, id):
            """
            code    : 1001     Document name code
                'P'     - Passport (issuer: Yes)
                'G'     - Group Passport
                'A'     - National Identity Card or Resident Card (Exact use
                          defined by issuing state)
                'C'     - National Identity Card or Resident Card (Exact use
                          defined by issuing state)
                'I'     - National Identity Card or Resident Card (Exact use
                          defined by issuing state)
                'M'     - Military Identification
                'D'     - Diplomatic Identification
                'AC'    - Crew Member Certificate
                'IP'    - Passport Card
                'F'     - Approved non-standard identity documents used for
                          travel.

            id       : 1004     Document identifier
            """
            PAXLST.DOC.__init__(self)
            self.name.code = code
            self.name.code_list = '110' # Customs special code
            self.name.agency = '111'
            self.details = alnum(id)

    # UNG ----------------------------------------------------------------{{{3
    class UNG(PAXLST_US.UNG):
        def __init__(self, sender=None, recipient=None, date_time=None, reference=None):
            PAXLST_US.UNG.__init__(self, sender, recipient, date_time, reference)
            self.version.release = '13B'
            
    # UNH ----------------------------------------------------------------{{{3
    class UNH(PAXLST_US.UNH):
        def __init__(self, reference=None, access_reference=None, sequence=None, first_last=None):
            PAXLST_US.UNH.__init__(self, reference, access_reference)
            self.id.release = '13B'

# PAXLST_TR =============================================================={{{1
# Assuming TR is *almost* identical to UK ...
# ... but a few changes (ref SKCMS-528)
#class PAXLST_TR(PAXLST_US):
class PAXLST_TR(PAXLST_UK):
    # UNB ----------------------------------------------------------------{{{3
    class UNB(PAXLST_US.UNB):
        def __init__(self, sender=None, recipient=None, date_time=None, reference=None):
            PAXLST_US.UNB.__init__(self, sender, recipient, date_time, reference)
            self.application = 'TYBS'

    class EMP(PAXLST.EMP):
        def __init__(self, category):
            """
            category    : 9005      Employment category description code
                'CR1'   - Cockpit crew and individuals in cockpit
                'CR2'   - Cabin crew
                'CR3'   - Airline operation management with cockpit access.
                'CR4'   - Cargo non-cockpit crew and/or non-crew individuals.
                'CR5'   - Pilots on A/C but not on duty (deadhead).
            """
            PAXLST.EMP.__init__(self)
            self.qual = '1'
            self.category.code = category

        # DOC ----------------------------------------------------------------{{{3
    class DOC(PAXLST.DOC):
        def __init__(self, code, id):
            """
            code    : 1001     Document name code
                'P'     - Passport (issuer: Yes)
                'G'     - Group Passport
                'A'     - National Identity Card or Resident Card (Exact use
                          defined by issuing state)
                'C'     - National Identity Card or Resident Card (Exact use
                          defined by issuing state)
                'I'     - National Identity Card or Resident Card (Exact use
                          defined by issuing state)
                'M'     - Military Identification
                'D'     - Diplomatic Identification
                'AC'    - Crew Member Certificate
                'IP'    - Passport Card
                'F'     - Approved non-standard identity documents used for
                          travel.

            id       : 1004     Document identifier
            """
            PAXLST.DOC.__init__(self)
            self.name.code = code
            #self.name.code_list = '110' # Customs special code
            #self.name.agency = '109'
            self.details = id

    # UNG ----------------------------------------------------------------{{{3
    class UNG(PAXLST_US.UNG):
        def __init__(self, sender=None, recipient=None, date_time=None, reference=None):
            PAXLST_US.UNG.__init__(self, sender, recipient, date_time, reference)
            self.version.release = '12B'
            # TODO self.sender.qual = 'ZZ'

    # UNH ----------------------------------------------------------------{{{3
    class UNH(PAXLST_US.UNH):
        def __init__(self, reference=None, access_reference=None, sequence=None, first_last=None):
            PAXLST_US.UNH.__init__(self, reference, access_reference)
            self.id.release = '12B'

    # LOC ----------------------------------------------------------------{{{3
    #class LOC(PAXLST_US.LOC):
    #    def __init__(self, qual, id, city_of_birth=None, province_of_birth=None):
    #        if qual == "180":
    #            city_of_birth = None
    #            province_of_birth = None
    #        PAXLST_US.LOC.__init__(self, qual, id, city_of_birth, province_of_birth)

# PAXLST_DK =============================================================={{{1
# Assuming DK is *almost* identical to UK ...
class PAXLST_DK(PAXLST_UK):
    # UNB ----------------------------------------------------------------{{{3
    class UNB(PAXLST_US.UNB):
        def __init__(self, sender=None, recipient=None, date_time=None, reference=None):
            PAXLST_US.UNB.__init__(self, sender, recipient, date_time, reference)
            self.application = 'APIS'

    class EMP(PAXLST.EMP):
        def __init__(self, category):
            """
            category    : 9005      Employment category description code
                'CR1'   - Cockpit crew and individuals in cockpit
                'CR2'   - Cabin crew
                'CR3'   - Airline operation management with cockpit access.
                'CR4'   - Cargo non-cockpit crew and/or non-crew individuals.
                'CR5'   - Pilots on A/C but not on duty (deadhead).
            """
            PAXLST.EMP.__init__(self)
            self.qual = '1'
            self.category.code = category

        # DOC ----------------------------------------------------------------{{{3
    class DOC(PAXLST.DOC):
        def __init__(self, code, id):
            """
            code    : 1001     Document name code
                'P'     - Passport (issuer: Yes)
                'G'     - Group Passport
                'A'     - National Identity Card or Resident Card (Exact use
                          defined by issuing state)
                'C'     - National Identity Card or Resident Card (Exact use
                          defined by issuing state)
                'I'     - National Identity Card or Resident Card (Exact use
                          defined by issuing state)
                'M'     - Military Identification
                'D'     - Diplomatic Identification
                'AC'    - Crew Member Certificate
                'IP'    - Passport Card
                'F'     - Approved non-standard identity documents used for
                          travel.

            id       : 1004     Document identifier
            """
            PAXLST.DOC.__init__(self)
            self.name.code = code
            #self.name.code_list = '110' # Customs special code
            #self.name.agency = '109'
            self.details = id

    # UNG ----------------------------------------------------------------{{{3
    #class UNG(PAXLST_US.UNG):
    #    def __init__(self, sender=None, recipient=None, date_time=None, reference=None):
    #        PAXLST_US.UNG.__init__(self, sender, recipient, date_time, reference)
    #        self.version.release = '12B'
            # TODO self.sender.qual = 'ZZ'

    # UNH ----------------------------------------------------------------{{{3
    #class UNH(PAXLST_US.UNH):
    #    def __init__(self, reference=None, access_reference=None, sequence=None, first_last=None):
    #        PAXLST_US.UNH.__init__(self, reference, access_reference)
    #        self.id.release = '12B'

    # LOC ----------------------------------------------------------------{{{3
    #class LOC(PAXLST_US.LOC):
    #    def __init__(self, qual, id, city_of_birth=None, province_of_birth=None):
    #        if qual == "180":
    #            city_of_birth = None
    #            province_of_birth = None
    #        PAXLST_US.LOC.__init__(self, qual, id, city_of_birth, province_of_birth)


# PAXLST_MX =============================================================={{{1
# Assuming MX is *almost* identical to UK ...
class PAXLST_MX(PAXLST_UK):
    # UNB ----------------------------------------------------------------{{{3
    class UNB(PAXLST_US.UNB):
        def __init__(self, sender=None, recipient=None, date_time=None, reference=None):
            PAXLST_US.UNB.__init__(self, sender, recipient, date_time, reference)
            self.application = 'APIS'

    class EMP(PAXLST.EMP):
        def __init__(self, category):
            """
            category    : 9005      Employment category description code
                'CR1'   - Cockpit crew and individuals in cockpit
                'CR2'   - Cabin crew
                'CR3'   - Airline operation management with cockpit access.
                'CR4'   - Cargo non-cockpit crew and/or non-crew individuals.
                'CR5'   - Pilots on A/C but not on duty (deadhead).
            """
            PAXLST.EMP.__init__(self)
            self.qual = '1'
            self.category.code = category

        # DOC ----------------------------------------------------------------{{{3
    class DOC(PAXLST.DOC):
        def __init__(self, code, id):
            """
            code    : 1001     Document name code
                'P'     - Passport (issuer: Yes)
                'G'     - Group Passport
                'A'     - National Identity Card or Resident Card (Exact use
                          defined by issuing state)
                'C'     - National Identity Card or Resident Card (Exact use
                          defined by issuing state)
                'I'     - National Identity Card or Resident Card (Exact use
                          defined by issuing state)
                'M'     - Military Identification
                'D'     - Diplomatic Identification
                'AC'    - Crew Member Certificate
                'IP'    - Passport Card
                'F'     - Approved non-standard identity documents used for
                          travel.

            id       : 1004     Document identifier
            """
            PAXLST.DOC.__init__(self)
            self.name.code = code
            self.details = id


# PAXLST_RU =============================================================={{{1
# Assuming RU is *almost* identical to UK ...
# ... but a few changes (ref SKCMS-528)
class PAXLST_RU(PAXLST_UK):

    class EMP(PAXLST.EMP):
        def __init__(self, category):
            """
            category    : 9005      Employment category description code
                'CR1'   - Cockpit crew and individuals in cockpit
                'CR2'   - Cabin crew
                'CR3'   - Airline operation management with cockpit access.
                'CR4'   - Cargo non-cockpit crew and/or non-crew individuals.
                'CR5'   - Pilots on A/C but not on duty (deadhead).
            """
            PAXLST.EMP.__init__(self)
            self.qual = '1'
            self.category.code = category


class PAXLST_RU_fo(PAXLST_UK):

    class EMP(PAXLST.EMP):
        def __init__(self, category):
            PAXLST.EMP.__init__(self)
            self.qual = '1'
            self.category.code = category

    class TDT(PAXLST.TDT):
        def __init__(self, flight_id, carrier):
            PAXLST.TDT.__init__(self)
            self.qual = '34'
            self.id = flight_id
            self.carrier = carrier

    class BGM(PAXLST.BGM):
        def __init__(self, name_code, document_id):
            PAXLST.BGM.__init__(self)
            self.id = document_id
            self.id.id = "A"
            self.name = name_code


# PAXLST_IN =============================================================={{{1
# Assuming IN is identical to US
PAXLST_IN = PAXLST_US


# Notes =================================================================={{{1
# DHS implementation
#   
#       UNG                     M 1
#   |---UNH                     M 1
#   |---BGM                     M 1
#   |---RFF                     C 1
#   |---Segment Group 1         C 5
#   |   |---NAD                 M 1
#   |   +---COM                 C 1    <--
#   +---Segment Group 2         M 10
#   |   |---TDT                 M 1
#   |   +---Segment Group 3     C 99
#   |       |---LOC             M 1
#   |       +---DTM             C 1    <--
#   +---Segment Group 4         C 99999
#   |   |---NAD                 M 1
#   |   |---ATT                 C 1    <--
#   |   |---DTM                 C 1    <--
#   |   |---GEI                 C 2    <--
#   |   |---LOC                 M 5    <--
#   |   |---COM                 C 1
#   |   |---EMP                 M 1    <--
#   |   |---NAT                 C 1    <--
#   |   |---RFF                 C 5    <--
#   |   |---Segment Group 5     C 5
#   |       |---DOC             M 1
#   |       |---DTM             C 1    <--
#   |       +---LOC             C 1    <--
#   |---CNT                     M 1
#   +---UNT                     M 1

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

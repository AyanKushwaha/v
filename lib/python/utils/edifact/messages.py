
# changelog{{{2
# [acosta:07/313@15:33] First implementation.
# }}}

"""
UN/EDIFACT PAXLST

Generic implementation, should work for any airline using UN/EDIFACT PAXLST.
"""

import utils.edifact.segments as segments
import utils.edifact.tools as tools

from utils.edifact import EDIFACT, Composite

# PAXLST ================================================================{{{1
class PAXLST(EDIFACT):
    """
    Note: The version described is D.05B

    Message structure

    Pos    Tag Name                                      S   R

    0010   UNH Message header                            M   1     
    0020   BGM Beginning of message                      M   1     
    0030   RFF Reference                                 C   1     
    0040   DTM Date/time/period                          C   9     

    0050       ----- Segment group 1  ------------------ C   5-----------+
    0060   NAD Name and address                          M   1           |
    0070   CTA Contact information                       C   1           |
    0080   COM Communication contact                     C   9-----------+

    0090       ----- Segment group 2  ------------------ M   10----------+
    0100   TDT Transport information                     M   1           |
    0110   DTM Date/time/period                          M   1           |
                                                                         |
    0120       ----- Segment group 3  ------------------ C   99---------+|
    0130   LOC Place/location identification             M   1          ||
    0140   DTM Date/time/period                          C   5----------++

    0150       ----- Segment group 4  ------------------ C   99999-------+
    0160   NAD Name and address                          M   1           |
    0170   ATT Attribute                                 C   9           |
    0180   DTM Date/time/period                          C   9           |
    0190   MEA Measurements                              C   9           |
    0200   GEI Processing information                    C   5           |
    0210   FTX Free text                                 C   99          |
    0220   LOC Place/location identification             C   25          |
    0230   COM Communication contact                     C   1           |
    0240   EMP Employment details                        C   9           |
    0250   NAT Nationality                               C   9           |
    0260   RFF Reference                                 C   1           |
                                                                         |
    0270       ----- Segment group 5  ------------------ C   5----------+|
    0280   DOC Document/message details                  M   1          ||
    0290   DTM Date/time/period                          C   5          ||
    0300   GEI Processing information                    C   9          ||
    0310   RFF Reference                                 C   9          ||
    0320   LOC Place/location identification             C   2          ||
    0330   CPI Charge payment instructions               C   1          ||
    0340   QTY Quantity                                  C   9----------+|
                                                                         |
    0350       ----- Segment group 6  ------------------ C   99---------+|
    0360   GID Goods item details                        M   1          ||
    0370   FTX Free text                                 C   9          ||
    0380   QTY Quantity                                  C   9----------+|
                                                                         |
    0390       ----- Segment group 7  ------------------ C   1----------+|
    0400   TDT Transport information                     M   1          ||
    0410   FTX Free text                                 C   1----------++
    0420   CNT Control total                             C   1     
    0430   AUT Authentication result                     C   1     
    0440   UNT Message trailer                           M   1     
    """

    # UNA, UNB, UNT, UNE, UNZ inherited from EDIFACT

    class UNH(EDIFACT.UNH):
        """
        0010   UNH, Message header
        A service segment starting and uniquely identifying a message.  The
        message type code for the Passenger list message is PAXLST.

        Note: Passenger list messages conforming to this document must contain
        the following data in segment UNH, composite S009:

        Data element  0065 PAXLST
                      0052 D
                      0054 05B
                      0051 UN
        """
        def __init__(self):
            EDIFACT.UNH.__init__(self)
            self.id.type = 'PAXLST'
            self.id.version = 'D'
            self.id.release = '05B'
            self.id.agency = 'UN'

    ATT = segments.ATT
    BGM = segments.BGM
    CNT = segments.CNT
    COM = segments.COM
    CPI = segments.CPI
    CTA = segments.CTA
    DOC = segments.DOC
    DTM = segments.DTM
    EMP = segments.EMP
    FTX = segments.FTX
    GEI = segments.GEI
    GID = segments.GID
    LOC = segments.LOC
    MEA = segments.MEA
    NAD = segments.NAD
    NAT = segments.NAT
    QTY = segments.QTY
    RFF = segments.RFF
    TDT = segments.TDT


# Notes =================================================================={{{1

# UN/PAXLST D.05B

# 0020   BGM, Beginning of message
#        A segment to indicate the type and function of the message.
# 
# 0030   RFF, Reference
#        A segment to specify message reference.
# 
# 0040   DTM, Date/time/period
#        A segment to specify associated dates/times as required related to
#        the message.
# 
# 
# 0050   Segment group 1:  NAD-CTA-COM
#        A group of segments to specify name and/or address, person or
#        department in the originating administration who can provide further
#        information about the data in the message.
# 
# 0060      NAD, Name and address
#           A segment to identify the name, address and related function.
# 
# 0070      CTA, Contact information
#           A segment to identify a person or department in the sending
#           administration to contact.
# 
# 0080      COM, Communication contact
#           A segment to identify communication numbers of departments or
#           persons to whom communication should be directed (e.g.  telephone
#           and/or fax number).
# 
# 
# 0090   Segment group 2:  TDT-DTM-SG3
#        A group of segments to indicate information related to each leg of
#        the mode of transport.
# 
# 0100      TDT, Transport information
#           A segment to specify details of transport related to each leg,
#           including means of transport, mode of transport name and/or number
#           of vessel and/or vehicle and/or flight.
# 
# 0110      DTM, Date/time/period
#           A segment to specify associated dates and/or times as required
#           related to details of transport.
# 
# 
# 0120      Segment group 3:  LOC-DTM
#           A group of segments indicating associated locations and dates.
# 
# 0130         LOC, Place/location identification
#              A segment to specify locations such as place of departure,
#              place of destination, country of ultimate destination, country
#              and/or place of transit, country of transit termination, etc.
#              of a passenger/crew.
# 
# 0140         DTM, Date/time/period
#              A segment to specify associated dates and/or times as required
#              related to locations.
# 
# 
# 0150   Segment group 4:  NAD-ATT-DTM-MEA-GEI-FTX-LOC-COM-EMP-NAT-RFF-
#                          SG5-SG6-SG7
#        A group of segments to indicate if passenger or crew member, personal
#        details (name, title, sex and marital status), date of birth,
#        attributes such as height, hair and eye colour, and other related
#        details.
# 
# 0160      NAD, Name and address
#           A segment specifying name of the passenger or crew member.
# 
# 0170      ATT, Attribute
#           A segment specifying passenger's and/or crew attributes such as
#           complexion and build.
# 
# 0180      DTM, Date/time/period
#           A segment to specify date of birth.
# 
# 0190      MEA, Measurements
#           To specify physical measurements, (e.g. height).
# 
# 0200      GEI, Processing information
#           A segment to specify indicators such as risk assessment.
# 
# 0210      FTX, Free text
#           A segment specifying other related passenger/crew information
#           (e.g. ticketing information).
# 
# 0220      LOC, Place/location identification
#           A segment indicating country of birth and port/place of origin
#           (embarkation), transit and destination (disembarkation) of a
#           passenger and/or crew.
# 
# 0230      COM, Communication contact
#           A segment to identify a communication number of a department or a
#           person to whom communication should be directed (e.g.  passenger
#           telephone details).
# 
# 0240      EMP, Employment details
#           A segment to indicate the occupation of a passenger or the rank of
#           crew.
# 
# 0250      NAT, Nationality
#           A segment to indicate the nationality of a passenger and/or crew.
# 
# 0260      RFF, Reference
#           A segment specifying the number assigned by a supplier that
#           identifies a passenger's reservation.
# 
# 
# 0270      Segment group 5:  DOC-DTM-GEI-RFF-LOC-CPI-QTY
#           A group of segments to indicate the travel document details, date
#           and time, reference, place and/or location identification, charge
#           payment instructions and quantity.
# 
# 0280         DOC, Document/message details
#              A segment identifying passenger and/or crew travel documents,
#              such as passports, visas etc.
# 
# 0290         DTM, Date/time/period
#              A segment to specify associated dates/times related to
#              documents.
# 
# 0300         GEI, Processing information
#              A segment to specify processing indicators, such as document
#              holder, alias, endorsee etc.
# 
# 0310         RFF, Reference
#              A segment to specify document reference.
# 
# 0320         LOC, Place/location identification
#              A segment indicating the country that issued the document
#              and/or the city where a related document was issued.
# 
# 0330         CPI, Charge payment instructions
#              A segment to identify methods of payment for transport charges.
# 
# 0340         QTY, Quantity
#              A segment to identify passenger type counts (e.g. child, adult,
#              infant, etc.).
# 
# 
# 0350      Segment group 6:  GID-FTX-QTY
#           A group of segments indicating the personal effects associated
#           with a passenger or crew member.
# 
# 0360         GID, Goods item details
#              A segment to identify the line item number, as well as the type
#              and number of packages.
# 
# 0370         FTX, Free text
#              A segment to indicate the description of the effects.
# 
# 0380         QTY, Quantity
#              A segment to indicate the quantity of the effects.
# 
# 
# 0390      Segment group 7:  TDT-FTX
#           A group of segments identifying transport details related to the
#           passenger or crew member.
# 
# 0400         TDT, Transport information
#              A segment to identify transport details related to the NAD
#              segment.
# 
# 0410         FTX, Free text
#              A segment to identify free text information on passenger
#              transport details.
# 
# 0420   CNT, Control total
#        A segment specifying control totals such as the total number of
#        passengers/ crew members in the message.
# 
# 0430   AUT, Authentication result
#        A segment to specify the results of the application of an
#        authentication procedure, including the authenticity of sender to
#        ensure integrity of data.
# 
# 0440   UNT, Message trailer
#        A service segment ending a message, giving the total number of
#        segments in the message (including the UNH & UNT) and the control
#        reference number of the message.

#   
#   |---UNH                     M 1
#   |---BGM                     M 1
#   |---RFF                     C 1
#   |---DTM                     C 9
#   |---Segment Group 1         C 5
#   |   |---NAD                 M 1
#   |   |---CTA                 C 1
#   |   +---COM                 C 9
#   +---Segment Group 2         M 10
#   |   |---TDT                 M 1
#   |   |---DTM                 M 1
#   |   +---Segment Group 3     C 99
#   |       |---LOC             M 1
#   |       +---DTM             C 5
#   +---Segment Group 4         C 99999
#   |   |---NAD                 M 1
#   |   |---ATT                 C 9
#   |   |---DTM                 C 9
#   |   |---MEA                 C 9
#   |   |---GEI                 C 5
#   |   |---FTX                 C 99
#   |   |---LOC                 C 25
#   |   |---COM                 C 1
#   |   |---EMP                 C 9
#   |   |---NAT                 C 9
#   |   |---RFF                 C 1
#   |   |---Segment Group 5     C 5
#   |   |   |---DOC             M 1
#   |   |   |---DTM             C 5
#   |   |   |---GEI             C 9
#   |   |   |---RFF             C 9
#   |   |   |---LOC             C 2
#   |   |   |---CPI             C 1
#   |   |   +---QTY             C 9
#   |   |---Segment Group 6     C 99
#   |   |   |---GID             M 1
#   |   |   |---FTX             C 9
#   |   |   +---QTY             C 9
#   |   +---Segment Group 7     C 1
#   |       |---TDT             M 1
#   |       +---FTX             C 1
#   |---CNT                     C 1
#   |---AUT                     C 1
#   +---UNT                     M 1
#   

# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=3:
# eof

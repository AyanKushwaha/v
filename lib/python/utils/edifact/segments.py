
# changelog{{{2
# [acosta:07/313@15:33] First implementation.
# }}}

"""
EDIFACT Segments (other than service segments).
"""

from utils.edifact import Segment


# ATT ===================================================================={{{1
class ATT(Segment):
    """
    Segment: ATT,  ATTRIBUTE

    Function: To identify a specific attribute.

    010    9017 ATTRIBUTE FUNCTION CODE QUALIFIER          M    1 an..3

    020    C955 ATTRIBUTE TYPE                             C    1
           9021  Attribute type description code           C      an..17
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           9020  Attribute type description                C      an..70

    030    C956 ATTRIBUTE DETAIL                           C    5
           9019  Attribute description code                C      an..17
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           9018  Attribute description                     C      an..256
    """
    def __init__(self, *a):
        Segment.__init__(self, 'ATT', *a)
        self(
            'qual',
            ('type', ('code', 'code_list', 'agency', 'description')),
            ('detail', ('code', 'code_list', 'agency', 'description')),
        )


# AUT ===================================================================={{{1
class AUT(Segment):
    """
    Segment: AUT,  AUTHENTICATION RESULT

    Function: To specify results of the application of an authentication
    procedure.

    010    9280 VALIDATION RESULT TEXT                     M    1 an..35

    020    9282 VALIDATION KEY IDENTIFIER                  C    1 an..35
    """
    def __init__(self, *a):
        Segment.__init__(self, 'AUT', *a)
        self('result', 'key')


# BGM ===================================================================={{{1
class BGM(Segment):
    """
    Segment: BGM, Beginning of Message

    Function: To indicate the type and function of a message and to
    transmit the identifying number.

    010    C002 DOCUMENT/MESSAGE NAME                      C    1
           1001  Document name code                        C      an..3
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           1000  Document name                             C      an..35

    020    C106 DOCUMENT/MESSAGE IDENTIFICATION            C    1
           1004  Document identifier                       C      an..35
           1056  Version identifier                        C      an..9
           1060  Revision identifier                       C      an..6

    030    1225 MESSAGE FUNCTION CODE                      C    1 an..3

    040    4343 RESPONSE TYPE CODE                         C    1 an..3
    """
    def __init__(self, *a):
        Segment.__init__(self, 'BGM', *a)
        self(
            ('name', ('code', 'code_list', 'agency', 'name')),
            ('id', ('id', 'version', 'revision')),
            'function',
            'response_type'
        )


# CNT ===================================================================={{{1
class CNT(Segment):
    """
    Segment: CNT, Control Total

    Function: To provide control total.

    010    C270 CONTROL                                    M    1
           6069  Control total type code qualifier         M      an..3
           6066  Control total quantity                    M      n..18
           6411  Measurement unit code                     C      an..8
    """
    def __init__(self, *a):
        Segment.__init__(self, 'CNT', *a)
        self(
            ('control', ('qual', 'quantity', 'unit')),
        )


# COM ===================================================================={{{1
class COM(Segment):
    """
    Segment: COM, Communication Contact

    Function: To identify a communication number of a department or a
    person to whom communication should be directed.

    010    C076 COMMUNICATION CONTACT                      M    3
           3148  Communication address identifier          M      an..512
           3155  Communication address code qualifier      M      an..3
    
    Example: COM+(?+46) 31 161231:TE+(?+46) 707 110166:FX'
    """
    def __init__(self, *a):
        Segment.__init__(self, 'COM', *a)
        self(
            ('contact1', ('id', 'qual')),
            ('contact2', ('id', 'qual')),
            ('contact3', ('id', 'qual')),
        )


# CPI ===================================================================={{{1
class CPI(Segment):
    """
    Segment: CPI,  CHARGE PAYMENT INSTRUCTIONS

    Function: To identify a charge.

    010    C229 CHARGE CATEGORY                            C    1
           5237  Charge category code                      M      an..3
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3

    020    C231 METHOD OF PAYMENT                          C    1
           4215  Transport charges payment method code     M      an..3
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3

    030    4237 PAYMENT ARRANGEMENT CODE                   C    1 an..3
    """
    def __init__(self, *a):
        Segment.__init__(self, 'CPI', *a)
        self(
            ('category', ('code', 'code_list', 'agency')),
            ('method', ('code', 'code_list', 'agency')),
            'payment_code'
        )


# CTA ===================================================================={{{1
class CTA(Segment):
    """
    Segment: CTA,  CONTACT INFORMATION

    Function: To identify a person or a department to whom communication should
    be directed.

    010    3139 CONTACT FUNCTION CODE                      C    1 an..3

    020    C056 DEPARTMENT OR EMPLOYEE DETAILS             C    1
           3413  Department or employee name code          C      an..17
           3412  Department or employee name               C      an..3
    """
    def __init__(self, *a):
        Segment.__init__(self, 'CTA', *a)
        self(
            'contact',
            ('details', ('code', 'name'))
        )


# DOC ===================================================================={{{1
class DOC(Segment):
    """
    Segment: DOC, Document/Message Details

    Function: To identify documents and details directly related to it.

    010    C002 DOCUMENT/MESSAGE NAME                      M    1
           1001  Document name code                        C      an..3
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           1000  Document name                             C      an..35

    020    C503 DOCUMENT/MESSAGE DETAILS                   C    1
           1004  Document identifier                       C      an..35
           1373  Document status code                      C      an..3
           1366  Document source description               C      an..70
           3453  Language name code                        C      an..3
           1056  Version identifier                        C      an..9
           1060  Revision identifier                       C      an..6

    030    3153 COMMUNICATION MEDIUM TYPE CODE             C    1 an..3

    040    1220 DOCUMENT COPIES REQUIRED QUANTITY          C    1 n..2

    050    1218 DOCUMENT ORIGINALS REQUIRED QUANTITY       C    1 n..2
    """
    def __init__(self, *a):
        Segment.__init__(self, 'DOC', *a)
        self(
           ('name', ('code', 'code_list', 'agency', 'name')),
           ('details', ('id', 'status', 'source', 'lang', 'version', 'revision')),
           'medium',
           'copies_quantity',
           'originals_quantity',
        )


# DTM ===================================================================={{{1
class DTM(Segment):
    """
    Segment: DTM, Date/Time/Period

    Function: To specify date, and/or time, or period.

    010    C507 DATE/TIME/PERIOD                           M    1
           2005  Date or time or period function code
                 qualifier                                 M      an..3
           2380  Date or time or period text               C      an..35
           2379  Date or time or period format code        C      an..3
    """
    def __init__(self, *a):
        Segment.__init__(self, 'DTM', *a)
        self(
            ('date_time', ('qual', 'text', 'format'))
        )


# EMP ===================================================================={{{1
class EMP(Segment):
    """
    Segment: EMP, Employment Details

    Function: To specify employment details.

    010    9003 EMPLOYMENT DETAILS CODE QUALIFIER          M    1 an..3

    020    C948 EMPLOYMENT CATEGORY                        C    1
           9005  Employment category description code      C      an..3
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           9004  Employment category description           C      an..35

    030    C951 OCCUPATION                                 C    1
           9009  Occupation description code               C      an..3
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           9008  Occupation description                    C      an..35
           9008  Occupation description                    C      an..35

    040    C950 QUALIFICATION CLASSIFICATION               C    1
           9007  Qualification classification description
                 code                                      C      an..3
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           9006  Qualification classification description  C      an..35
           9006  Qualification classification description  C      an..35

    050    3494 JOB TITLE DESCRIPTION                      C    1 an..35

    060    9035 QUALIFICATION APPLICATION AREA CODE        C    1 an..3'
    """
    def __init__(self, *a):
        Segment.__init__(self, 'EMP', *a)
        self(
            'qual',
            ('category', ('code', 'code_list', 'agency', 'description')),
            ('occupation', ('code', 'code_list', 'agency', 'occupation1', 'occupation2')),
            ('classification', ('code', 'code_list', 'agency', 'description1', 'description2')),
            'title',
            'application_area',
        )


# FTX ===================================================================={{{1
class FTX(Segment):
    """
    Segment: FTX, FREE TEXT

    Function: To provide free form or coded text information.

    010    4451 TEXT SUBJECT CODE QUALIFIER                M    1 an..3

    020    4453 FREE TEXT FUNCTION CODE                    C    1 an..3

    030    C107 TEXT REFERENCE                             C    1
           4441  Free text description code                M      an..17
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3

    040    C108 TEXT LITERAL                               C    1
           4440  Free text                                 M      an..512
           4440  Free text                                 C      an..512
           4440  Free text                                 C      an..512
           4440  Free text                                 C      an..512
           4440  Free text                                 C      an..512

    050    3453 LANGUAGE NAME CODE                         C    1 an..3

    060    4447 FREE TEXT FORMAT CODE                      C    1 an..3
    """
    def __init__(self, *a):
        Segment.__init__(self, 'FTX', *a)
        self(
            'subject',
            'function',
            ('reference', ('code', 'code_list', 'agency')),
            ('text', ('text1', 'text2', 'text3', 'text4', 'text5')),
            'language',
            'format'
        )


# GEI ===================================================================={{{1
class GEI(Segment):
    """
    Segment: GEI, Processing Information

    Function: To identify processing information.

    010    9649 PROCESSING INFORMATION CODE QUALIFIER      M    1 an..3

    020    C012 PROCESSING INDICATOR                       C    1
           7365  Processing indicator description code     C      an..3
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           7364  Processing indicator description          C      an..35

    030    7187 PROCESS TYPE DESCRIPTION CODE              C    1 an..17
    """
    def __init__(self, *a):
        Segment.__init__(self, 'GEI', *a)
        self(
            'qual',
            ('indicator', ('code', 'code_list', 'agency', 'description')),
            'description',
        )


# GID ===================================================================={{{1
class GID(Segment):
    """
    Segment: GID,  GOODS ITEM DETAILS

    Function: To indicate totals of a goods item.

    010    1496 GOODS ITEM NUMBER                          C    1 n..5

    020    C213 NUMBER AND TYPE OF PACKAGES                C    1
           7224  Package quantity                          C      n..8
           7065  Package type description code             C      an..17
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           7064  Type of packages                          C      an..35
           7233  Packaging related description code        C      an..3

    030    C213 NUMBER AND TYPE OF PACKAGES                C    1
           7224  Package quantity                          C      n..8
           7065  Package type description code             C      an..17
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           7064  Type of packages                          C      an..35
           7233  Packaging related description code        C      an..3

    040    C213 NUMBER AND TYPE OF PACKAGES                C    1
           7224  Package quantity                          C      n..8
           7065  Package type description code             C      an..17
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           7064  Type of packages                          C      an..35
           7233  Packaging related description code        C      an..3

    050    C213 NUMBER AND TYPE OF PACKAGES                C    1
           7224  Package quantity                          C      n..8
           7065  Package type description code             C      an..17
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           7064  Type of packages                          C      an..35
           7233  Packaging related description code        C      an..3

    060    C213 NUMBER AND TYPE OF PACKAGES                C    1
           7224  Package quantity                          C      n..8
           7065  Package type description code             C      an..17
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           7064  Type of packages                          C      an..35
           7233  Packaging related description code        C      an..3
    """
    def __init__(self, *a):
        Segment.__init__(self, 'GID', *a)
        self(
            'item',
            ('package1', ('quantity', 'code', 'code_list', 'agency', 'type', 'packaging_code')),
            ('package2', ('quantity', 'code', 'code_list', 'agency', 'type', 'packaging_code')),
            ('package3', ('quantity', 'code', 'code_list', 'agency', 'type', 'packaging_code')),
            ('package4', ('quantity', 'code', 'code_list', 'agency', 'type', 'packaging_code')),
            ('package5', ('quantity', 'code', 'code_list', 'agency', 'type', 'packaging_code')),
        )


# LOC ===================================================================={{{1
class LOC(Segment):
    """
    Segment: LOC, Place/Location Identification

    Function: To identify a place or a location and/or related locations.

    010    3227 LOCATION FUNCTION CODE QUALIFIER           M    1 an..3

    020    C517 LOCATION IDENTIFICATION                    C    1
           3225  Location name code                        C      an..35
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           3224  Location name                             C      an..256

    030    C519 RELATED LOCATION ONE IDENTIFICATION        C    1
           3223  First related location name code          C      an..25
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           3222  First related location name               C      an..70

    040    C553 RELATED LOCATION TWO IDENTIFICATION        C    1
           3233  Second related location name code         C      an..25
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           3232  Second related location name              C      an..70

    050    5479 RELATION CODE                              C    1 an..3
    """
    def __init__(self, *a):
        Segment.__init__(self, 'LOC', *a)
        self(
            'qual',
            ('id', ('code', 'code_list', 'agency', 'name')),
            ('related1', ('code', 'code_list', 'agency', 'name')),
            ('related2', ('code', 'code_list', 'agency', 'name')),
            'relation',
        )


# MEA ===================================================================={{{1
class MEA(Segment):
    """
    Segment: MEA,  MEASUREMENTS

    Function: To specify physical measurements, including dimension tolerances,
    weights and counts.

    010    6311 MEASUREMENT PURPOSE CODE QUALIFIER         M    1 an..3

    020    C502 MEASUREMENT DETAILS                        C    1
           6313  Measured attribute code                   C      an..3
           6321  Measurement significance code             C      an..3
           6155  Non-discrete measurement name code        C      an..17
           6154  Non-discrete measurement name             C      an..70

    030    C174 VALUE/RANGE                                C    1
           6411  Measurement unit code                     M      an..8
           6314  Measure                                   C      an..18
           6162  Range minimum quantity                    C      n..18
           6152  Range maximum quantity                    C      n..18
           6432  Significant digits quantity               C      n..2

    040    7383 SURFACE OR LAYER CODE                      C    1 an..3
    """
    def __init__(self, *a):
        Segment.__init__(self, 'MEA', *a)
        self(
            'purpose'
            ('details', ('attribute', 'significance', 'name_code', 'name')),
            ('value', ('unit', 'measure', 'min', 'max', 'digits')),
            'surface'
        )


# NAD ===================================================================={{{1
class NAD(Segment):
    """
    Segment: NAD, Name and Address

    Function: To specify the name/address and their related function, either by
    C082 only and/or unstructured by C058 or structured by C080 thru 3207.

    010    3035 PARTY FUNCTION CODE QUALIFIER              M    1 an..3

    020    C082 PARTY IDENTIFICATION DETAILS               C    1
           3039  Party identifier                          M      an..35
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3

    030    C058 NAME AND ADDRESS                           C    1
           3124  Name and address description              M      an..35
           3124  Name and address description              C      an..35
           3124  Name and address description              C      an..35
           3124  Name and address description              C      an..35
           3124  Name and address description              C      an..35

    040    C080 PARTY NAME                                 C    1
           3036  Party name                                M      an..35
           3036  Party name                                C      an..35
           3036  Party name                                C      an..35
           3036  Party name                                C      an..35
           3036  Party name                                C      an..35
           3045  Party name format code                    C      an..3

    050    C059 STREET                                     C    1
           3042  Street and number or post office box
                 identifier                                M      an..35
           3042  Street and number or post office box
                 identifier                                C      an..35
           3042  Street and number or post office box
                 identifier                                C      an..35
           3042  Street and number or post office box
                 identifier                                C      an..35

    060    3164 CITY NAME                                  C    1 an..35

    070    C819 COUNTRY SUB-ENTITY DETAILS                 C    1
           3229  Country sub-entity name code              C      an..9
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           3228  Country sub-entity name                   C      an..70

    080    3251 POSTAL IDENTIFICATION CODE                 C    1 an..17

    090    3207 COUNTRY NAME CODE                          C    1 an..3
    """
    def __init__(self, *a):
        Segment.__init__(self, 'NAD', *a)
        self(
            'qual',
            ('id', ('id', 'code', 'agency')),
            ('name_adress', ('description1', 'description2',
                'description3', 'description4', 'description5')),
            ('name', ('name1', 'name2', 'name3', 'name4', 'name5', 'format')),
            ('street', ('street1', 'street2', 'street3', 'street4')),
            'city',
            ('state', ('code', 'code_list', 'agency', 'name')),
            'postal_id',
            'country'
        )


# NAT ===================================================================={{{1
class NAT(Segment):
    """
    Segment: NAT, Nationality

    Function: To specify a nationality.

    010    3493 NATIONALITY CODE QUALIFIER                 M    1 an..3

    020    C042 NATIONALITY DETAILS                        C    1
           3293  Nationality name code                     C      an..3
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           3292  Nationality name                          C      a..35
    """
    def __init__(self, *a):
        Segment.__init__(self, 'NAT', *a)
        self(
            'qual',
            ('nationality', ('code', 'code_list', 'agency', 'name')),
        )


# QTY ===================================================================={{{1
class QTY(Segment):
    """
    Segment: QTY,  QUANTITY

    Function: To specify a pertinent quantity.

    010    C186 QUANTITY DETAILS                           M    1
           6063  Quantity type code qualifier              M      an..3
           6060  Quantity                                  M      an..35
           6411  Measurement unit code                     C      an..8
    """
    def __init__(self, *a):
        Segment.__init__(self, 'QTY', *a)
        self(
            ('details', ('code', 'quantity', 'unit'))
        )


# RFF ===================================================================={{{1
class RFF(Segment):
    """
    Segment: RFF, Reference

    Function: To specify a reference.

    010    C506 REFERENCE                                  M    1
           1153  Reference code qualifier                  M      an..3
           1154  Reference identifier                      C      an..70
           1156  Document line identifier                  C      an..6
           4000  Reference version identifier              C      an..35
           1060  Revision identifier                       C      an..6
    """
    def __init__(self, *a):
        Segment.__init__(self, 'RFF', *a)
        self(
            ('reference', ('qual', 'id', 'line', 'version', 'revision'))
        )


# TDT ===================================================================={{{1
class TDT(Segment):
    """
    Segment: TDT, Transport Information

    Function: To specify information regarding the transport such as mode
    of transport, means of transport, its conveyance reference number and
    the identification of the means of transport.

    010    8051 TRANSPORT STAGE CODE QUALIFIER             M    1 an..3

    020    8028 MEANS OF TRANSPORT JOURNEY IDENTIFIER      C    1 an..17

    030    C220 MODE OF TRANSPORT                          C    1
           8067  Transport mode name code                  C      an..3
           8066  Transport mode name                       C      an..17

    040    C001 TRANSPORT MEANS                            C    1
           8179  Transport means description code          C      an..8
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           8178  Transport means description               C      an..17

    050    C040 CARRIER                                    C    1
           3127  Carrier identifier                        C      an..17
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           3128  Carrier name                              C      an..35

    060    8101 TRANSIT DIRECTION INDICATOR CODE           C    1 an..3

    070    C401 EXCESS TRANSPORTATION INFORMATION          C    1
           8457  Excess transportation reason code         M      an..3
           8459  Excess transportation responsibility code M      an..3
           7130  Customer shipment authorisation
                 identifier                                C      an..17

    080    C222 TRANSPORT IDENTIFICATION                   C    1
           8213  Transport means identification name
                 identifier                                C      an..35
           1131  Code list identification code             C      an..17
           3055  Code list responsible agency code         C      an..3
           8212  Transport means identification name       C      an..70
           8453  Transport means nationality code          C      an..3

    090    8281 TRANSPORT MEANS OWNERSHIP INDICATOR CODE   C    1 an..3

           Dependency note:
           040  D5(040,030) If first, then all
    """
    def __init__(self, *a):
        Segment.__init__(self, 'TDT', *a)
        self(
            'qual',
            'id',
            ('mode', ('code', 'name')),
            ('means', ('code', 'code_list', 'agency', 'description')),
            ('carrier', ('id', 'code_list', 'agency', 'name')),
            'direction',
            ('excess', ('reason', 'responsibility', 'id')),
            ('transport', ('id', 'code', 'agency', 'id', 'nationality')),
            'owner'
        )


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=0:
# eof

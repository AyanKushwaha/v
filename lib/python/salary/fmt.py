
# -*- coding: latin-1
"""
Common formats.
"""

# imports ================================================================{{{1
import math
import salary.api as api
import salary.conf as conf
import utils.fmt as fmt
from RelTime import RelTime


# BasicRecord ============================================================{{{1
class BasicRecord(dict):
    """
    Produce "flat file" records for the mainframe.
    The record is a dict, but with attribute access.
    Accessing the map value will get the raw data, the attribute access will
    return a converted value.  Each record type has to specify which conversion
    functions are to be used.
    Values that are not set are treated as 'None'.
    """
    def __init__(self, spec, *a, **k):
        """The spec is a tuple of tuples.
        spec = (
            ('fieldname1', 'conversion_function1'),
            ('fieldname2', 'conversion_function2'),
        )
        The fields will be printed out in order after the conversion function
        has been applied.
        """
        dict.__init__(self, k)
        self._fields = (n for n, c in spec)
        self._convmap = dict(spec)

    def record(self):
        """Return the record as a string."""
        return ''.join([getattr(self, name) for name in self._fields])

    def __getattr__(self, name):
        """Return converted value of field 'name'."""
        if name in self._convmap:
            return self._convmap[name](self.get(name, None))
        else:
            raise AttributeError("Attribute %s does not exist for %s" % 
                    (name, self.__class__.__name__))

    def __setattr__(self, name, value):
        """Enter value into dict."""
        if name.startswith('_'):
            # To avoid recursion.
            object.__setattr__(self, name, value)
        else:
            self[name] = value

    def __delattr__(self, name):
        """Remove value from dict."""
        if name in self:
            del self[name]

    def __str__(self):
        """Return string representation (= self.record)"""
        return self.record()


# conv ==================================================================={{{1
class conv:
    """
    This class is a collection of conversion routines commonly used when
    creating "flat files" for the mainframe.
    The class creates records of different types (default is BasicRecord).
    """
    def __init__(self, spec=(), rec=BasicRecord):
        self.spec = spec
        self.rec = rec

    def __call__(self, *a, **k):
        return self.rec(self.spec, *a, **k)

    class POSITIVE_INT:
        """Convert to right adjusted string with leading zeros.  Note: does not
        work well with negative values."""
        def __init__(self, pos):
            """'pos' is number of positions."""
            self.pos = pos
        def __call__(self, num):
            return fmt.INT(self.pos, num)

    class CHR:
        """Convert to left adjusted string with tailing spaces."""
        def __init__(self, pos):
            """'pos' is number of positions."""
            self.pos = pos
        def __call__(self, txt):
            return fmt.CHR(self.pos, txt)

    class Constant:
        """Some constant value (a string)."""
        def __init__(self, value):
            self.value = value
        def __call__(self, *a, **k):
            """Just a dummy."""
            return self.value

    def DateDDMMYYYY(self, atime):
        """Convert AbsTime to date in format DDMMYYYY."""
        if atime is None:
            return 8 * ' '
        (y, m, d, H, M) = atime.split()[:5]
        return "%02d%02d%04d" % (d, m, y)

    def DateYYMMDD(self, atime):
        """Convert AbsTime to date in format YYMMDD."""
        if atime is None:
            return 6 * ' '
        return ("%04d%02d%02d" % atime.split()[:3])[2:]

    class ANUM:
        """Convert to number with mainframe spec 9(n),mm-, fraction with
        tailing sign."""
        def __init__(self, i, f):
            """i is number of digits in front of the decimal separator, f
            is the number of digits after."""
            self.i = i
            self.f = f
            self.maxlen = i + f + 1

        def __call__(self, num):
            if num is None:
                num = 0.0
            if num < 0:
                num = -num
                sign = '-'
            else:
                sign = ' '
            if(isinstance(num, list)): # Fix it !
                return ""

            x = "%0*.*f" % (self.maxlen, self.f, num / 100.0)
            if len(x) > (self.maxlen):
                raise fmt.CellOverFlowError("Value '%s' too large to fit in cell of width '%s'." % (x, self.maxlen))
            return ','.join(x.split('.')) + sign

    class VNUM1:
        """Convert to number with mainframe spec 9(n)Vmm with no sign and no
        decimal point, and where an empty field will be replaced by filler."""
        def __init__(self, i, f, filler=' '):
            """i is number of digits in front of the decimal separator, f
            is the number of digits after."""
            self.i = i
            self.f = f
            self.maxlen = i + f
            self.filler = filler

        def __call__(self, num):
            if num is None:
                # Fill with filler
                return self.maxlen * self.filler
            if num < 0:
                num = -num
                sign = '-'
            else:
                sign = ' '
            x = "%0*.*f" % (self.maxlen + 1, self.f, num / 100.0)
            x = ''.join(x.split('.'))
            if len(x) > (self.maxlen):
                raise fmt.CellOverFlowError("Value '%s' too large to fit in cell of width '%s'." % (x, self.maxlen))
            return x

    def TimeHHMM(self, atime):
        """Convert AbsTime to time in format HHMM."""
        if atime is None:
            return 4 * ' '
        return "%02d%02d" % atime.split()[3:5]


# CSVFormatter ==========================================================={{{1
class CSVFormatter:
    """
    As a convenience for creating CSV files for different systems.

    To use this class create a file (e.g. Record_SE_CSV.py) which contains
    the following:

    from salary.fmt import CSVFormatter

    class Record_SE_CSV(CSVFormatter):
        pass
    """

    def __init__(self, runfiles):
        pass

    def pre(self):
        return "Extperkey,Type,Amount"

    def record(self, extperkey, extartid, amount):
        return '%s,%s,%.2f' % (extperkey, extartid, amount / 100.0)


# HTMLFormatter =========================================================={{{1
class HTMLFormatter:
    class Headings:
        admcode   = 'admcode'
        amount    = 'amount'
        extartid  = 'extartid'
        extperkey = 'extperkey'
        extsys    = 'extsys'
        firstdate = 'firstdate'
        lastdate  = 'lastdate'
        note      = 'note'
        runid     = 'runid'
        starttime = 'starttime'
        selector  = 'selector'
        total     = 'total'

    def __init__(self, runfiles):
        self.total = 0
        self.runfiles = runfiles
        self.headings = self.Headings()

    def pre(self):
        h = self.headings
        rf = self.runfiles
        rd = rf.rundata
        return """<html>
<head>
  <title>%s</title>
  <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1" />
  <style type="text/css">
<!--
    table { width: 40%%; }
    h1 { font-size: 105%%; }
    body { font-family: sans-serif; }
    dd { font-style: italic; }
    td { font-family: monospace; }
    td.amount { text-align: right }
    th { text-align: left; border-bottom: solid; }
    th.amount { text-align: right }
    tr.total { font-weight: bold; border-top: solid; border-bottom: solid; }
    .total .extperkey { font-family: sans-serif; }
-->
  </style>
</head>
<body>
<h1>%s</h1>
<dl>
  <dt>%s</dt><dd>%s</dd>
  <dt>%s</dt><dd>%s</dd>
  <dt>%s</dt><dd>%s</dd>
  <dt>%s</dt><dd>%s</dd>
  <dt>%s</dt><dd>%s</dd>
  <dt>%s</dt><dd>%s</dd>
  <dt>%s</dt><dd>%s</dd>
  <dt>%s</dt><dd>%s</dd>
</dl>
<hr>
<table>
  <tr>
    <th class="extperkey">%s</th>
    <th class="extartid">%s</th>
    <th class="amount">%s</th>
  </tr>
""" % (
        rf.name,
        rf.name,
        h.extsys, rd.extsys,
        h.runid, rd.runid,
        h.starttime, rd.starttime,
        h.admcode, rd.admcode,
        h.firstdate, rd.firstdate,
        h.lastdate, rd.lastdate,
        h.selector, rd.selector,
        h.note, rd.note,
        h.extperkey,
        h.extartid,
        h.amount,
      )

    def post(self):
        return """
  <tr class="total">
    <td class="total">%s</td>
    <td></td>
    <td class="amount">%.2f</td>
  </tr>
</table>
</body>
</html>
""" % (self.headings.total, self.total)

    def record(self, extperkey, extartid, amount):
        self.total = self.total + amount / 100.0
        return """  <tr>
    <td class="extperkey">%s</td>
    <td class="type">%s</td>
    <td class="amount">%.2f</td>
  </tr>""" % (extperkey, extartid, amount / 100.0)


# PALSRecordMaker ========================================================{{{1
class PALSRecordMaker(conv):
    def __init__(self, runtype=''):
        if runtype == 'VACATION_Y':
            conv.__init__(self, (
                ('TYP', self.Constant('4')),
                ('FILLER1', self.CHR(6)),
                ('FILLER2', self.POSITIVE_INT(5)),
                ('EMPNO', self.POSITIVE_INT(5)),
                ('FILLER3', self.Constant('51')),
                ('LONEART', self.CHR(3)),
                ('FILLER4', self.CHR(17)),
                ('ANTAL_TIM', self.VNUM1(3, 2)),
                ('ANTAL_DGR', self.VNUM1(3, 2)),
                ('A_PRIS', self.VNUM1(5, 2)),
                ('BELOPP', self.VNUM1(7, 2)),
                ('TECKEN', self.CHR(1)),
                ('FILLER6', self.CHR(1)),
                ('DATUMFROM', self.Constant(6*' ')),
                ('DATUMTOM', self.Constant(6*' ')),
                ('FILLER7', self.CHR(1)),
                ('BUNTID', self.CHR(4)),
                ('IDENT', self.Constant('IIVAR')),
                ('FILLER8', self.CHR(61)),
            ))
        else:
            conv.__init__(self, (
                ('TYP', self.Constant('4')),
                ('FILLER1', self.CHR(6)),
                ('FILLER2', self.POSITIVE_INT(5)),
                ('EMPNO', self.POSITIVE_INT(5)),
                ('FILLER3', self.Constant('51')),
                ('LONEART', self.CHR(3)),
                ('FILLER4', self.CHR(10)),
                ('ANTAL_TIM', self.VNUM1(5, 2)),
                ('ANTAL_DGR', self.VNUM1(3, 2)),
                ('A_PRIS', self.VNUM1(5, 2)),
                ('BELOPP', self.VNUM1(7, 2)),
                ('TECKEN', self.CHR(1)),
                ('FILLER6', self.CHR(1)),
                ('DATUMFROM', self.DateYYMMDD),
                ('DATUMTOM', self.DateYYMMDD),
                ('FILLER7', self.CHR(6)),
                ('BUNTID', self.CHR(4)),
                ('IDENT', self.Constant('IIVAR')),
                ('FILLER8', self.CHR(61)),
            ))


# PALS ==================================================================={{{1
class PALS:
    def __init__(self, rf):
        self.firstdate = rf.rundata.firstdate
        self.lastdate = utils.last_date(rf.rundata.lastdate)
        self.runtype = rf.rundata.runtype
        if self.runtype == 'SUPERVIS':
            self.buntid = '9096'
        elif self.runtype == 'VACATION_Y':
            self.buntid = '9074'
        elif self.runtype == 'PERDIEM':
            self.buntid = '9022'
        elif self.runtype == 'COMPDAYS':
            self.buntid = '9162'
        elif self.runtype == 'TEMP_CREW':
            self.buntid = '9025'
        else:
            self.buntid = '9023'
        self._rec = PALSRecordMaker(self.runtype)

    def record(self, extperkey, type, amount):
        rec = self._rec(
            DATUMFROM=self.firstdate,
            DATUMTOM=self.lastdate,
            EMPNO=extperkey,
            LONEART=type,
            TECKEN=('-', ' ')[amount >= 0],
            BUNTID=self.buntid)
        if self.runtype == 'PERDIEM':
            rec['BELOPP'] = abs(amount)
        elif self.runtype in ('COMPDAYS'):
            rec['ANTAL_DGR'] = abs(amount)
        else:
            rec['ANTAL_TIM'] = abs(amount)
        return str(rec)


# PALS2 =================================================================={{{1
class PALS2:
    """ PALS record (Vacation) """
    def __str__(self):
        return ''.join(
            (
                '4',
                6 * ' ',
                '00000',
                fmt.INT(5, self.empno),
                '51',
                fmt.CHR(3, self.type),
                40 * ' ',
                ("%04d%02d%02d" % self.startdate.split()[:3])[2:],
                ("%04d%02d%02d" % utils.last_date(self.enddate).split()[:3])[2:],
                6 * ' ',
                self.buntid,
                'IIVAR',
                61 * ' ',
            ))


# PALS Format description ================================================={{{1

# [acosta:09/302@15:30] Updated ANTAL-DGR from 9(5) to 9(3)V99
# Field  PALS1    PALS2    Name           Value              Comment
# ------ -------- -------- -------------- ------------------ -----------------------------------
# F01:   X        X        TYP            4                  Constant
# F02:   X(6)     X(6)     FILLER1        6 * ' '            Constant
# F03:   9(5)     9(5)     FILLER2        00000              Constant
# F04:   9(5)     9(5)     EMPNO                             extperkey
# F05:   XX       XX       FILLER3        51                 Constant
# F06:   X(3)     X(3)     LÖNEART                           type
# F07:   X(10)    X(10)    FILLER4        10 * ' '           Constant
# F08:   9(5)V99  X(7)     ANTAL-TIM      amount * 100       amount
# F09:   9(3)V99  X(5)     ANTAL-DGR      00000              Constant
# F10:   9(5)V99  X(7)     A-PRIS         7 * ' '            Constant
# F11:   9(7)V99  X(9)     BELOPP         9 * ' '            Constant
# F12:   X        X        TECKEN         ' ' or '-'         Sign of amount
# F13:   X        X        FILLER6        ' '                Constant
# F14:   X(6)     X(6)     DATUM.FR.O.M.                     YYMMDD, First day of salary period
# F15:   X(6)     X(6)     DATUM.T.O.M.                      YYMMDD, Last day of salary period
# F16:   X(6)     X(6)     FILLER7        6 * ' '            Constant
# F17:   X(4)     X(4)     BUNTID         9023               Constant (ident delivering system)
# F18:   X(5)     X(5)     IDENT          IIVAR              Constant
# F19:   X(61)    X(61)    FILLER8        61 * ' '           Constant


# Bluegarden ============================================================={{{1

# BGARecordMaker ========================================================{{{1

# Bluegarden deviation transaction: format description ===================={{{1
#
# Field name	  Field no	Picture	  Form	Length	Position  Remark
# TRANS TYPE	    1	    X	      A/N	1	    1	      Constant: A
# COMPANY	        2	    X(4)	  A/N	4	    2	      4 characters, eg sesk
# ORG UNIT	        3	    XX	      A/N	2	    6	      2 characters (Constant: 01)
# EMPLOYEE ID	    4	    X(10)	  A/N	10	    8	      Employment no SAP (12345     )
# EMPLOYMENT NO	    5	    X(10)	  A/N	10	    18	      SPACE
# PAYROLL CODE	    6	    X(3)	  A/N	3	    28	      Payroll code in HR plus (NOT 000)
# COST CENTER 1	    7	    X(24)	  A/N	24	    31	      SPACE
# COST CENTER 2	    8	    X(20)	  A/N	20	    55	      SPACE
# TEXT 1	        9	    X(10)	  A/N	10	    75	      SPACE
# TEXT 2	       10	    X(10)	  A/N	10	    85	      SPACE
# TRANS NO	       11	    XX	      A/N	2	    95	      01
# START DATE	   12	    X(6)	  A/N	6	    97	      Start date for the  reporting period,  eg 140801 (the
#                                                             first of August 2014)
# PERIOD LENGTH	   13	    99	      N	    2	    103	      Number of days in the period (eg 31, number of days in
#                                                             August)
# DAYS1-35				                    140	    105	      ZEROS
# - TIM	           14	    99V99
# FILLER	       15	    99V99	  N	    4	    245	      ZEROS
# VACATION FACTOR  16	    9V9(4)	  N	    5	    249
# NUMBER	       17	    9(4)V99	  N	    6	    254	      Eg  10.5 hours is entered as 001050
# NUMBER NEG.	   18	    X	      A/N	1	    260	      - if number is negative
# PRICE EACH	   19	    9(5)V99	  N	    7	    261	      Eg 250 SEK is entered as 0025000
# AMOUNT	       20	    9(7)V99	  N	    9	    268	      Eg 1500 SEK is entered as 000150000
# AMOUNT NEG.	   21	    X	      A/N	1	    277	      - if amount is negative
# BUNDLE NO	       22	    X(10)	  A/N	10	    278	      Any no can be entered to identify the transaction
# START DATE	   23	    X(6)	  A/N	6	    288	      Eg 140801 (the first of August 2014)
# END DATE	       24	    X(6)	  A/N	6	    294	      Eg 140801 (the first of August 2014). Same as START DATE,
#                                                             when NUMBER, PRICE EACH or AMOUNT is entered.
# ABSENCE EXTENT   25	    999V9(4)  N	    7	    300 	  Absence extent, eg 50% is entered as 0500000
# FILLER	       26	    999V99	  N	    5	    307	      ZEROS
# SALARY DEGREE    27		          N	    2	    312	      ZEROS
# SHIFT FORM	   28		          N	    1	    314	      ZEROS
# ID / CHILD	   29		          A/N	10	    315	      If the function ?parental leave per child? is used, enter
#                                                             unique value on posts regarding parental leave.

class BGARecordMaker(conv):
    def __init__(self, runtype=''):
        conv.__init__(self, (
                ('TRANS_TYPE', self.Constant('A')),
                ('COMPANY', self.Constant('sesk')),
                ('ORG_UNIT', self.Constant('01')),
                ('EMPLOYEE_ID', self.CHR(10)),
                ('EMPLOYMENT_NO', self.Constant(' ' * 10)),
                ('PAYROLL_CODE', self.CHR(3)),
                ('COST_CENTER_1', self.Constant(' ' * 24)),
                ('COST_CENTER_2', self.Constant(' ' * 20)),
                ('TEXT_1', self.Constant(' ' * 10)),
                ('TEXT_2', self.Constant(' ' * 10)),
                ('TRANS_NO', self.Constant('01')),
                ('PERIOD_START_DATE', self.DateYYMMDD),
                ('PERIOD_LENGTH', self.POSITIVE_INT(2)),
                ('DAY_1', self.POSITIVE_INT(4)),
                ('DAY_2', self.POSITIVE_INT(4)),
                ('DAY_3', self.POSITIVE_INT(4)),
                ('DAY_4', self.POSITIVE_INT(4)),
                ('DAY_5', self.POSITIVE_INT(4)),
                ('DAY_6', self.POSITIVE_INT(4)),
                ('DAY_7', self.POSITIVE_INT(4)),
                ('DAY_8', self.POSITIVE_INT(4)),
                ('DAY_9', self.POSITIVE_INT(4)),
                ('DAY_10', self.POSITIVE_INT(4)),
                ('DAY_11', self.POSITIVE_INT(4)),
                ('DAY_12', self.POSITIVE_INT(4)),
                ('DAY_13', self.POSITIVE_INT(4)),
                ('DAY_14', self.POSITIVE_INT(4)),
                ('DAY_15', self.POSITIVE_INT(4)),
                ('DAY_16', self.POSITIVE_INT(4)),
                ('DAY_17', self.POSITIVE_INT(4)),
                ('DAY_18', self.POSITIVE_INT(4)),
                ('DAY_19', self.POSITIVE_INT(4)),
                ('DAY_20', self.POSITIVE_INT(4)),
                ('DAY_21', self.POSITIVE_INT(4)),
                ('DAY_22', self.POSITIVE_INT(4)),
                ('DAY_23', self.POSITIVE_INT(4)),
                ('DAY_24', self.POSITIVE_INT(4)),
                ('DAY_25', self.POSITIVE_INT(4)),
                ('DAY_26', self.POSITIVE_INT(4)),
                ('DAY_27', self.POSITIVE_INT(4)),
                ('DAY_28', self.POSITIVE_INT(4)),
                ('DAY_29', self.POSITIVE_INT(4)),
                ('DAY_30', self.POSITIVE_INT(4)),
                ('DAY_31', self.POSITIVE_INT(4)),
                ('DAY_32', self.POSITIVE_INT(4)),
                ('DAY_33', self.POSITIVE_INT(4)),
                ('DAY_34', self.POSITIVE_INT(4)),
                ('DAY_35', self.POSITIVE_INT(4)),
                ('FILLER_1', self.Constant('0' * 4)),
                ('VACATION_FACTOR', self.Constant(' ' * 5)),
                ('NUMBER', self.POSITIVE_INT(6)),
                ('NUMBER_NEG', self.CHR(1)),
                ('PRICE_EACH', self.POSITIVE_INT(7)),
                ('AMOUNT', self.POSITIVE_INT(9)),
                ('AMOUNT_NEG', self.CHR(1)),
                ('BUNDLE_NO', self.POSITIVE_INT(10)),
                ('START_DATE', self.DateYYMMDD),
                ('END_DATE', self.DateYYMMDD),
                ('ABSENCE_EXTENT', self.POSITIVE_INT(7)),
                ('FILLER_2', self.Constant('0' * 5)),
                ('SALARY_DEGREE', self.Constant('0' * 2)),
                ('SHIFT_FORM', self.Constant('0')),
                ('ID_CHILD', self.POSITIVE_INT(10))
                ))

class BGBRecordMaker(conv):
    def __init__(self, runtype=''):
        conv.__init__(self, (
                ('TRANS_TYPE', self.Constant('B')),
                ('COMPANY', self.Constant('sesk')),
                ('ORG_UNIT', self.Constant('01')),
                ('EMPLOYEE_ID', self.CHR(10)),
                ('EMPLOYMENT_NO', self.Constant(' ' * 10)),
                ('PAYROLL_CODE', self.CHR(3)),
                ('COST_CENTER_1', self.Constant(' ' * 24)),
                ('COST_CENTER_2', self.Constant(' ' * 20)),
                ('TEXT_1', self.Constant(' ' * 10)),
                ('TEXT_2', self.Constant(' ' * 10)),
                ('TRANS_NO', self.Constant('01')),
                ('PERIOD_START_DATE', self.DateYYMMDD),
                ('PERIOD_LENGTH', self.POSITIVE_INT(2)),
                ('DAY_1', self.POSITIVE_INT(4)),
                ('DAY_2', self.POSITIVE_INT(4)),
                ('DAY_3', self.POSITIVE_INT(4)),
                ('DAY_4', self.POSITIVE_INT(4)),
                ('DAY_5', self.POSITIVE_INT(4)),
                ('DAY_6', self.POSITIVE_INT(4)),
                ('DAY_7', self.POSITIVE_INT(4)),
                ('DAY_8', self.POSITIVE_INT(4)),
                ('DAY_9', self.POSITIVE_INT(4)),
                ('DAY_10', self.POSITIVE_INT(4)),
                ('DAY_11', self.POSITIVE_INT(4)),
                ('DAY_12', self.POSITIVE_INT(4)),
                ('DAY_13', self.POSITIVE_INT(4)),
                ('DAY_14', self.POSITIVE_INT(4)),
                ('DAY_15', self.POSITIVE_INT(4)),
                ('DAY_16', self.POSITIVE_INT(4)),
                ('DAY_17', self.POSITIVE_INT(4)),
                ('DAY_18', self.POSITIVE_INT(4)),
                ('DAY_19', self.POSITIVE_INT(4)),
                ('DAY_20', self.POSITIVE_INT(4)),
                ('DAY_21', self.POSITIVE_INT(4)),
                ('DAY_22', self.POSITIVE_INT(4)),
                ('DAY_23', self.POSITIVE_INT(4)),
                ('DAY_24', self.POSITIVE_INT(4)),
                ('DAY_25', self.POSITIVE_INT(4)),
                ('DAY_26', self.POSITIVE_INT(4)),
                ('DAY_27', self.POSITIVE_INT(4)),
                ('DAY_28', self.POSITIVE_INT(4)),
                ('DAY_29', self.POSITIVE_INT(4)),
                ('DAY_30', self.POSITIVE_INT(4)),
                ('DAY_31', self.POSITIVE_INT(4)),
                ('DAY_32', self.POSITIVE_INT(4)),
                ('DAY_33', self.POSITIVE_INT(4)),
                ('DAY_34', self.POSITIVE_INT(4)),
                ('DAY_35', self.POSITIVE_INT(4)),
                ('FILLER_1', self.Constant('0' * 4)),
                ('VACATION_FACTOR', self.Constant('0' * 5)),
                ('OFF_DUTY_FACTOR', self.Constant('0' * 6)),
                ('FILLER_2', self.Constant(' ')),
                ('FILLER_3', self.Constant('0' * 7)),
                ('FILLER_4', self.Constant('0' * 9)),
                ('FILLER_5', self.Constant(' ' * 1)),
                ('FILLER_6', self.Constant(' ' * 10)),
                ('FILLER_7', self.Constant(' ' * 6)),
                ('FILLER_8', self.Constant(' ' * 6)),
                ('FILLER_9', self.Constant('0' * 7)),
                ('WEEKLY_WORKING_HOURS', self.Constant('0' * 5)),
                ('FILLER_10', self.Constant('0' * 2)),
                ('FILLER_11', self.Constant('0' * 1)),
                ('FILLER_12', self.Constant('0' * 10))
                ))

class BG:
    def __init__(self, rf):
        self.firstdate = rf.rundata.firstdate
        self.lastdate = utils.last_date(rf.rundata.lastdate)
        self.runtype = rf.rundata.runtype
        self.bundle_no = rf.rundata.runid
        if self.runtype == 'BUDGETED':  # Only budgeted time / schedule uses type B records
            self._rec = BGBRecordMaker(self.runtype)
        else:                           # All other reports use type A records
            self._rec = BGARecordMaker(self.runtype)

    def record(self, extperkey, extartid, amounts):
        extartid_list = extartid.split(':')
        if len(extartid_list) == 2:   # extartid:amount_type
            amount_type = extartid_list[1]
        elif len(extartid_list) == 1: # extartid
            amount_type = 'number'
        else:
            raise AttributeError("Unknown extartid format: %s" % extartid)
        extartid = extartid_list[0]

        params = {}
        params['PERIOD_START_DATE'] = self.firstdate
        params['PERIOD_LENGTH'] = int(self.lastdate - self.firstdate) / (60 * 24) + 1
        params['EMPLOYEE_ID'] = str(extperkey)
        params['PAYROLL_CODE'] = extartid
        params['BUNDLE_NO'] = self.bundle_no

        if (self.runtype == 'BUDGETED') or (self.runtype == 'ABSENCE'):
            # Report amounts for several days in each record
            for (offset, amount) in amounts:
                params["DAY_%d" % (offset+1)] = amount
        else:
            # Report amount for one day per record
            (offset, amount) = amounts
            transaction_date = self.firstdate.adddays(offset)
            params['START_DATE'] = transaction_date
            params['END_DATE'] = transaction_date
            if amount_type == 'amount':
                params['AMOUNT'] = abs(amount)
                params['AMOUNT_NEG'] = ('-', ' ')[amount >= 0]
            elif amount_type == 'number':
                params['NUMBER'] = abs(amount)
                params['NUMBER_NEG'] = ('-', ' ')[amount >= 0]
            else:
                raise AttributeError("Unknown amount type: %s" % amount_type)
        return str(self._rec(**params))


# SAPStartRecordMaker ===================================================={{{1
class SAPStartRecordMaker(conv):
    def __init__(self):
        #  1: PIC X(2)  RECTP       Record type, value 00
        #  2: PIC X(8)  DELIV       Delivery ID, id of delivering system.
        #  3: PIC X(4)  VERNO       File format version
        #  4: PIC X(8)  CRDAT       File creation date, DDMMCCYY (UTC)
        #  5: PIC X(4)  CRTIM       File creation time, HHMM (UTC)
        #  6: PIC 9(5)  SEQNO       File sequence number. Unique number.
        #  7: PIC X(6)  PAYPR       Payroll period, YYYYMM, normally this is one
        #                           month later than the transaction period
        #                           BEGDA-ENDDA
        #  8: PIC 9(8)  BEGDA       First day of salary month (DDMMYYYY)
        #  9: PIC 9(8)  ENDDA       Last day of salary month (DDMMYYYY)
        # 10: PIC X(60) FILLER      Empty

        conv.__init__(self, (
            ('RECTP', self.POSITIVE_INT(2)),
            ('DELIV', self.CHR(8)),
            ('VERNO', self.CHR(4)),
            ('CRDAT', self.DateDDMMYYYY),
            ('CRTIM', self.TimeHHMM),
            ('SEQNO', self.POSITIVE_INT(5)),
            ('PAYPR', self.Month),
            ('BEGDA', self.DateDDMMYYYY),
            ('ENDDA', self.DateDDMMYYYY),
            ('FILLER', self.CHR(60)),
        ))

    def Month(self, atime):
        y, m, d = atime.split()[:3]
        if m == 12:
            sm = 1
            sy = y + 1
        else:
            sm = m + 1
            sy = y
        return "%04d%02d" % (y, m)

    def __call__(self, *a, **k):
        k['RECTP'] = k.get('RECTP', 0)
        k['VERNO'] = k.get('VERNO', '1.0')
        return conv.__call__(self, *a, **k)


# SAPEndRecordMaker ======================================================{{{1
class SAPEndRecordMaker(conv):
    """ SAP Format, end record """
    def __init__(self):
        #  1: RECTP    PIC X(2)              Record type, value 99
        #  2: TRNNO    PIC 9(9)              Number of data records.
        #  3: FILLER   PIC X(102)            Filler.

        conv.__init__(self, (
            ('RECTP', self.POSITIVE_INT(2)),
            ('TRNNO', self.POSITIVE_INT(9)),
            ('FILLER', self.CHR(102)),
        ))

    def __call__(self, *a, **k):
        k['RECTP'] = k.get('RECTP', 99)
        return conv.__call__(self, *a, **k)


# SAPRecordMaker ========================================================={{{1
class SAPRecordMaker(conv):
    def __init__(self):
        #  1: PIC X(2)  RECTP       Record Type, value 01
        #  2: PIC X(8)  BEGDA       Start date (DDMMYYYY), 1st day last month
        #  3: PIC X(8)  ENDDA       End date (DDMMYYYY), last day last month
        #  4: PIC X(3)  Filler      3 * '0'
        #  5: PIC 9(5)  PERNR       External empno
        #  6: PIC 9(4)  LGART       Article id
        #  7: PIC 9(7),99- BETRG    Amount (Betrag)
        #  8: PIC X(3)  WAERS       Always 'NOK' (Währung)
        #  9: PIC 9(5),99-  ANZHL   Number (Anzahl) Space ??? (should be 000000000)
        # 10: PIC X(8)  EITXT       8 * ' ' Unit text
        # 11: PIC XX    PREAS       2 * ' '  Reason code
        # 12: PIC X(10) KOSTL       10 * ' ' Cost center
        # 13: PIC X(20) ZUORD       20 * ' ' Assignment number
        # 14: PIC X(20) Filler      20 * ' ' Future use

        conv.__init__(self, (
            ('RECTP', self.POSITIVE_INT(2)),
            ('BEGDA', self.DateDDMMYYYY),
            ('ENDDA', self.DateDDMMYYYY),
            #('FILLER1', self.POSITIVE_INT(3)),
            ('PERNR', self.POSITIVE_INT(8)),
            ('LGART', self.POSITIVE_INT(4)),
            ('BETRG', self.ANUM(7, 2)),
            ('WAERS', self.CHR(3)),
            ('ANZHL', self.ANUM(5, 2)),
            ('EITXT', self.CHR(8)),
            ('PREAS', self.CHR(2)),
            ('KOSTL', self.CHR(10)),
            ('ZUORD', self.CHR(20)),
            ('FILLER2', self.CHR(20)),
        ))

    def __call__(self, *a, **k):
        k['RECTP'] = k.get('RECTP', 1)
        return conv.__call__(self, *a, **k)


# SAPVacationRecordMaker ================================================={{{1
class SAPVacationRecordMaker(conv):
    def __init__(self):
        # This format was specified in CR 169

        #  1: PIC X(2)  RECTP       Record Type, value 01
        #  2: PIC X(8)  BEGDA       Start date VA-period (DDMMYYYY)
        #  3: PIC X(8)  ENDDA       End date VA-period (DDMMYYYY)
        #  4: PIC 9(8)  PERNR       External empno
        #  5: PIC X(4)  LGART       Article id '1511'
        #  6: PIC X(11) BETRG       Always spaces
        #  7: PIC X(3)  WAERS       Always spaces (VALUTA-CODE)
        #  8: PIC 9(8)  ANZHL       Number of vacation days
        #  9: PIC X(1)  SIGN        Sign, '-' or space (+=)
        # 10: PIC X(8)  EITXT       Always spaces
        # 11: PIC X(2)  PREAS       Always spaces
        # 12: PIC X(10) KOSTL       COST-CENTER
        # 13: PIC X(20) ZUORD       Always spaces
        # 14: PIC X(20) Filler      Always spaces

        conv.__init__(self, (
            ('RECTP', self.POSITIVE_INT(2)),
            ('BEGDA', self.DateDDMMYYYY),
            ('ENDDA', self.DateDDMMYYYY),
            ('PERNR', self.POSITIVE_INT(8)),
            ('LGART', self.POSITIVE_INT(4)),
            ('BETRG', self.CHR(11)),
            ('WAERS', self.CHR(3)),
            ('ANZHL', self.POSITIVE_INT(8)),
            ('SIGN',  self.CHR(1)),
            ('EITXT', self.CHR(8)),
            ('PREAS', self.CHR(2)),
            ('KOSTL', self.CHR(10)),
            ('ZUORD', self.CHR(20)),
            ('FILLER', self.CHR(20)),
        ))


# SAPAbsenceRecordMaker ================================================={{{1
class SAPAbsenceRecordMaker(conv):
    def __init__(self):
        #  1: PIC X(2)  RECTP       Record Type, value 01
        #  2: PIC X(8)  BEGDA       Start date VA-period (DDMMYYYY)
        #  3: PIC X(8)  ENDDA       End date VA-period (DDMMYYYY)
        #  4: PIC 9(8)  PERNR       External empno
        #  5: PIC X(4)  LGART       Article id '1511'
        #  6: PIC X(11) BETRG       Always spaces
        #  7: PIC X(3)  WAERS       Always spaces (VALUTA-CODE)
        #  8: PIC 9(8)  ZEROS       8 zeros

        conv.__init__(self, (
            ('RECTP', self.POSITIVE_INT(2)),
            ('BEGDA', self.DateDDMMYYYY),
            ('ENDDA', self.DateDDMMYYYY),
            ('PERNR', self.POSITIVE_INT(8)),
            ('LGART', self.POSITIVE_INT(4)),
            ('BETRG', self.CHR(11)),
            ('WAERS', self.CHR(3)),
            ('ZEROS', self.Constant('00000000')),
            ('FILLER', self.CHR(61)),
        ))

# SAPScheduleRecordMaker ================================================={{{1
class SAPScheduleRecordMaker(conv):
    def __init__(self):
        #  1: PIC 9(8)  PERNR       External empno
        #  2: PIC X(8)  DATE        Date of check
        #  3: PIC X(1)  DOF         Day off flag
        #  6: PIC X(24) ZEROS       Always zeros

        conv.__init__(self, (
            ('PERNR', self.POSITIVE_INT(8)),
            ('DATE',  self.DateDDMMYYYY),
            ('DOF',   self.Constant('Y')),
            ('ZEROS', self.Constant('00000000000000000000000')),
            ('FILLER', self.CHR(73)),
        ))

# SAPTcScheduleRecordMaker ================================================={{{1
class SAPTcScheduleRecordMaker(conv):
    def __init__(self):
        #  1: PIC 9(8)  PERNR       External empno
        #  2: PIC X(8)  DATE        Date of check
        #  3: PIC X(1)  DOF         Day off flag
        #  6: PIC X(24) ZEROS       Always zeros

        conv.__init__(self, (
            ('PERNR',   self.POSITIVE_INT(8)),
            ('DATE',    self.DateDDMMYYYY),
            ('DOF',     self.Constant('N')),
            ('ENDTIME', self.POSITIVE_INT(8)),
            ('ZEROS',   self.Constant('0000000000000000')),
        ))

# SAPTcScheduleRecordMaker ================================================={{{1
class SAPAllScheduleRecordMaker(conv):
    def __init__(self):
        #  1: PIC 9(8)  PERNR       External empno
        #  2: PIC X(8)  DATE        Date of check
        #  3: PIC X(1)  DOF         Day off flag
        #  6: PIC X(24) ZEROS       Always zeros

        conv.__init__(self, (
            ('PERNR',   self.POSITIVE_INT(8)),
            ('DATE',    self.DateDDMMYYYY),
            ('DOF',     self.Constant('N')),
            ('ENDTIME', self.POSITIVE_INT(8)),
            ('ZEROS',   self.Constant('0000000000000000')),
        ))


# SAP ===================================================================={{{1
class SAP(object):

    def __init__(self, rf):
        self.rd = rf.rundata
        self.numberOfRecords = 0
        self.kostl = api.getCostCenter(self.rd)
        if self.rd.runtype in conf.need_currencies:
            self.waers = conf.currencies.get(self.rd.extsys, '')
        else:
            self.waers = None
        self.deliv = self.get_deliveryid(self.rd.extsys, self.rd.runtype)
        if self.rd.runtype == 'COMPDAYS' and self.rd.extsys not in ('DK','NO'):
            self.deliv = 'CMSXXX'

        self._start_rec = SAPStartRecordMaker()
        self._rec = SAPRecordMaker()
        self._end_rec = SAPEndRecordMaker()

    def get_deliveryid(self, extsys, runtype):
        if extsys in ('DK', 'NO'):
            # SAP delivery IDs for Denmark and Norway
            delivery_ids = {
                'AMBI': 'CMSAMBI',
                'COMPDAYS': 'CMSFDAY',
                'OVERTIME': 'CMSOTIME',
                'PERDIEM': 'CMSPDIEM',
                'SUPERVIS': 'CMSSUPER',
                'TEMP_CREW': 'CMSTEMP',
                'VACATION_P': 'CMSVAPDA',
                'VACATION_R': 'CMSVARDA',
                'VACATIONYF': 'CMSVAFDY',
                'VACATIONYC': 'CMSVAADY',
            }
            return delivery_ids.get(runtype, 'CMSXXX')
        elif extsys == 'S3':
            # SAP delivery IDs for Sweden
            delivery_ids = {
                'PERDIEM':    'PDIMSTO',
                'ALLOWNCE_M': 'ALLMSTO',
                'ALLOWNCE_D': 'ALLDSTO',
                'VACATION_Y': 'VACSTO',
                'ABSENCE':    'ABSSTO 1.0',
                'SCHEDULE':   'SCHESTO 1.0',
                'TCSCHEDULE': 'TEMPSTO 1.0',
                'SCHED_CCSE': 'CCSESTO 1.0',
            }
            return delivery_ids.get(runtype, 'CMSXXX')
        else:
            return 'CMSXXX'

    def pre(self):
        """ Header info """
        return str(self._start_rec(
            DELIV=self.deliv,
            CRDAT=self.rd.starttime,
            CRTIM=self.rd.starttime,
            SEQNO=self.rd.runid,
            PAYPR=self.rd.starttime,
            BEGDA=self.rd.firstdate,
            ENDDA=utils.last_date(self.rd.lastdate)))

    def record(self, extperkey, type, amount):
        self.numberOfRecords += 1
        rec = self._rec(
            BEGDA=self.rd.firstdate,
            ENDDA=utils.last_date(self.rd.lastdate),
            PERNR=extperkey,
            LGART=type,
            WAERS=self.waers,
            KOSTL=self.kostl)
        if self.rd.runtype == 'PERDIEM':
            rec['BETRG'] = amount
        else:
            rec['ANZHL'] = amount
        return str(rec)
    
    def post(self):
        """ end-record """
        return str(self._end_rec(
            TRNNO=self.numberOfRecords))


# utils =================================================================={{{1
class utils:
    """A couple of date/time utilities, using static methods of a class to make
    it easier to import both."""

    @staticmethod
    def last_date(et):
        """Return a date from a time, if both hours and minutes are '0' (0:00)
        return one day less (the time as 24:00)."""
        if et.split()[3:5] == (0, 0):
            return et - RelTime(1, 0, 0)
        return et

    @staticmethod
    def days(st, et):
        """Return number of days between two dates."""
        return int(math.ceil(abs((int(et) - int(st)) / 1440.0)))
        

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

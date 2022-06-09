#! /usr/bin/env python

import sys

# Run with carmpython ===================================================={{{1
try:
    from carmensystems.dig.framework.dave import DaveSearch, createOp, DaveConnector, DaveStorer
except:
    # Probably not running with carmpython
    if sys.executable.startswith('/opt/Carmen'):
        raise Exception("Cannot even start with 'carmpython', check your installation!")
    try:
        os.environ['CARMUSR']
    except:
        raise Exception("Environment CARMUSR must be set.")

from dateutil.parser import parse as duparse
from subprocess import Popen, PIPE, STDOUT
import time, os, logging, signal, json
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from AbsTime import AbsTime
from RelTime import RelTime
from operator import itemgetter

import traceback


# get_program ------------------------------------------------------------{{{2
def get_program():
    return os.path.basename(sys.argv[0])


def to_abstime(str_value):
    if len(str_value) == 8:
        return AbsTime(int(str_value[4:8]), int(str_value[2:4]), int(str_value[0:2]), 0 , 0)
    elif len(str_value) == 12:
        return AbsTime(int(str_value[4:8]), int(str_value[2:4]), int(str_value[0:2]), int(str_value[8:10]) , int(str_value[10:12]))
    else:
        raise

def strtosec(strtime):
    """ Simple string to time parser.

    This function get time string and parse it to seconds.

    Args: 
        strtime (str): unix like time stamp

    Returns:
        t (int): seconds of time passed
    
    Raises:
        ValueError: if strtime is not possible to parse; then kill the process with signal 1.
    """
    try:
        t = duparse(strtime)
        return time.mktime(t.timetuple())
    except ValueError:
        logging.error("Can not parse '%s' to date. You may have to set carmen version by --r20 ", strtime )
        exit(1)


class pstr(str):
    def format_type(self, length):
        if len(self) != length:
            logging.error("Wrong length for string" )
        return self

class pint(int):
    def format_type(self, length):
        format_str = "%%0%dd" % length
        return format_str % self

class pamount():
    def __init__(self, value):
        if isinstance(value, int):
            self.value = value
        elif isinstance(value, float) and False:
            self.value = int(value * 100)
        else:
            sign = value[-1]
            if not sign in [' ', '-']:
                logging.error("Invalid sign: %s" % sign )
            decimals = int(value[-3:-1])
            comma = value[-4:-3]
            if comma not in [',', '.']:
                logging.error("Expected comma, or dot.  got %s" % comma )
            integer = int(value[:-4])
            self.value = integer * 100 + decimals
            if sign == '-':
                self.value = -self.value

    def __add__(self, another):
        return pamount(self.value + another.value)

    def __eq__(self, another):
        return self.value == another.value

    def __ne__(self, another):
        return self.value != another.value

    def __mul__(self, another):
        return pamount(self.value * another)

    def __trunc__(self):
        return self.value / 100

    def __str__(self):
        if self.value < 0:
            sign = '-'
        else:
            sign = ''
        integer = abs(self.value) / 100
        decimals = abs(self.value) % 100
        
        return "%s%d.%02d" % (sign, integer, decimals)
    
    def format_type(self, length):
        format_str = "%%0%dd,%%02d%%s" % (length - 4)
        if self.value < 0:
            sign = '-'
        else:
            sign = ' '
        integer = abs(self.value) / 100
        decimals = abs(self.value) % 100
        return format_str % (integer, decimals, sign)

def parse(specifier, string, headervars):
    result = {}
    trail = string
    for name, length, ftype, expected in specifier:
        result[name] = ftype(trail[:length])
        if expected != None:
            if expected.startswith('{') and expected.endswith('}'):
                expected = headervars[expected[1:-1]]
            if expected != result[name]:
                logging.error("Expected value '%s' for field %s, got '%s'" % (expected, name, result[name]) )
                return None
        trail = trail[length:]

    if len(trail) > 0:
        logging.error("Trailing string not handled" )

    return result


def parse_file(specifiers, filename):
    header_specifier, record_specifier, trailer_specifier, _ = specifiers

    infile = open(filename)
    lines = [line for line in infile]

    header = parse(header_specifier, lines[0], {})
    if header == None:
        return None
    records = []
    for line in lines[1: -1]:
        records.append(parse(record_specifier, line, header))

    trailer = parse(trailer_specifier, lines[-1], header)

    status = {'additions' : 0,
              'modifications' : 0,
              'deletes' : 0}

    return (header, records, trailer, status)


def convert_value(vstr):
    if len(vstr) == 0:
        logging.error("Trying to convert empty value" )
        return None

    if ',' in vstr:
        parts = vstr.split(',')
    elif '.' in vstr:
        parts = vstr.split('.')
    else:
        parts = [vstr, '00']

    if len(parts[1]) < 2:
        parts[1] = parts[1] + '0' * (2 - len(parts[1]))
    elif len(parts[1]) > 2:
        logging.warn("Truncating to two decimals: %s" % vstr )
        parts[1] = parts[1][:2]
    return ','.join(parts)



ALLOWANCE_D_SPECIFIER = ([("number1", 2, pstr, '00'),
                         ("title", 12, pstr, 'ALLDSTO 1.0 '),
                         ("rundate", 8, pstr, None),
                         ("runtime", 4, pstr, None), # FIXME: Check what this number is
                         ("runid", 5, pstr, None),
                         ("salaryperiod", 6, pstr, None),
                         ("periodstart", 8, pstr, None),
                         ("periodend", 8, pstr, None),
                         ("trail", 60, pstr, ' ' * 60),
                         ("newline", 1, pstr, '\n')],

                        [("number1", 2, pstr, '01'),
                         ("periodstart", 8, pstr, None),
                         ("periodend", 8, pstr, None),
                         ("number2", 3, pstr, '000'),
                         ("empno", 5, pstr, None),
                         ("account", 4, pstr, None),
                         ("amount", 11, pstr, '0000000,00 '),
                         ("currency", 3, pstr, ' ' * 3),
                         ("value", 9, pamount, None),
                         ("trail", 60, pstr, ' ' * 60),
                         ("newline", 1, pstr, '\n')],

                        [("number1", 6, pstr, '990000'),
                         ("numrecords", 5, pint, None),
                         ("trail", 102, pstr, ' ' * 102),
                         ("newline", 1, pstr, '\n')],

                        {'correct': 'value'})



ALLOWANCE_M_SPECIFIER = ([("number1", 2, pstr, '00'),
                         ("title", 12, pstr, 'ALLMSTO 1.0 '),
                         ("rundate", 8, pstr, None),
                         ("runtime", 4, pstr, None), # FIXME: Check what this number is
                         ("runid", 5, pstr, None),
                         ("salaryperiod", 6, pstr, None),
                         ("periodstart", 8, pstr, None),
                         ("periodend", 8, pstr, None),
                         ("trail", 60, pstr, ' ' * 60),
                         ("newline", 1, pstr, '\n')],

                        [("number1", 2, pstr, '01'),
                         ("periodstart", 8, pstr, "{periodstart}"),
                         ("periodend", 8, pstr, "{periodend}"),
                         ("number2", 3, pstr, '000'),
                         ("empno", 5, pstr, None),
                         ("account", 4, pstr, None),
                         ("amount", 11, pstr, '0000000,00 '),
                         ("currency", 3, pstr, ' ' * 3),
                         ("value", 9, pamount, None),
                         ("trail", 60, pstr, ' ' * 60),
                         ("newline", 1, pstr, '\n')],

                        [("number1", 6, pstr, '990000'),
                         ("numrecords", 5, pint, None),
                         ("trail", 102, pstr, ' ' * 102),
                         ("newline", 1, pstr, '\n')],

                        {'correct': 'value'})


COMPDAYS_SPECIFIER = ([("number1", 2, pstr, '00'),
                       ("title", 12, pstr, 'CMSFDAY 1.0 '),
                       ("rundate", 8, pstr, None),
                       ("runtime", 4, pstr, None), # FIXME: Check what this number is
                       ("runid", 5, pstr, None),
                       ("salaryperiod", 6, pstr, None),
                       ("periodstart", 8, pstr, None),
                       ("periodend", 8, pstr, None),
                       ("trail", 60, pstr, ' ' * 60),
                       ("newline", 1, pstr, '\n')],

                      [("number1", 2, pstr, '01'),
                       ("periodstart", 8, pstr, "{periodstart}"),
                       ("periodend", 8, pstr, "{periodend}"),
                       ("number2", 3, pstr, '000'),
                       ("empno", 5, pstr, None),
                       ("account", 4, pstr, None),
                       ("amount", 11, pstr, '0000000,00 '),
                       ("currency", 3, pstr, ' ' * 3),
                       ("value", 9, pamount, None),
                       ("trail", 60, pstr, ' ' * 60),
                       ("newline", 1, pstr, '\n')],

                      [("number1", 6, pstr, '990000'),
                       ("numrecords", 5, pint, None),
                       ("trail", 102, pstr, ' ' * 102),
                       ("newline", 1, pstr, '\n')],

                      {'correct': 'value'})


OVERTIME_SPECIFIER = ([("number1", 2, pstr, '00'),
                       ("title", 12, pstr, 'CMSOTIME1.0 '),
                       ("rundate", 8, pstr, None),
                       ("runtime", 4, pstr, None), # FIXME: What is this?
                       ("runid", 5, pstr, None),
                       ("salaryperiod", 6, pstr, None),
                       ("periodstart", 8, pstr, None),
                       ("periodend", 8, pstr, None),
                       ("trail", 60, pstr, ' ' * 60),
                       ("newline", 1, pstr, '\n')],

                      [("number1", 2, pstr, '01'),
                       ("periodstart", 8, pstr, "{periodstart}"),
                       ("periodend", 8, pstr, "{periodend}"),
                       ("number2", 3, pstr, '000'),
                       ("empno", 5, pstr, None),
                       ("account", 4, pstr, None),
                       ("amount", 11, pstr, '0000000,00 '),
                       ("currency", 3, pstr, '   '),
                       ("value", 9, pamount, None),
                       ("trail", 60, pstr, ' ' * 60),
                       ("newline", 1, pstr, '\n')],

                      [("number1", 6, pstr, '990000'),
                       ("numrecords", 5, pint, None),
                       ("trail", 102, pstr, ' ' * 102),
                       ("newline", 1, pstr, '\n')],

                      {'correct': 'value'})

ALLOWNCE_SPECIFIER = ([("number1", 2, pstr, '00'),
                       ("title", 12, pstr, 'CMSSUPER1.0 '),
                       ("rundate", 8, pstr, None),
                       ("runtime", 4, pstr, None), # FIXME: What is this?
                       ("runid", 5, pstr, None),
                       ("salaryperiod", 6, pstr, None),
                       ("periodstart", 8, pstr, None),
                       ("periodend", 8, pstr, None),
                       ("trail", 60, pstr, ' ' * 60),
                       ("newline", 1, pstr, '\n')],

                      [("number1", 2, pstr, '01'),
                       ("periodstart", 8, pstr, "{periodstart}"),
                       ("periodend", 8, pstr, "{periodend}"),
                       ("number2", 3, pstr, '000'),
                       ("empno", 5, pstr, None),
                       ("account", 4, pstr, None),
                       ("amount", 11, pstr, '0000000,00 '),
                       ("currency", 3, pstr, '   '),
                       ("value", 9, pamount, None),
                       ("trail", 60, pstr, ' ' * 60),
                       ("newline", 1, pstr, '\n')],

                      [("number1", 6, pstr, '990000'),
                       ("numrecords", 5, pint, None),
                       ("trail", 102, pstr, ' ' * 102),
                       ("newline", 1, pstr, '\n')],

                      {'correct': 'value'})


PERDIEM_SPECIFIER_SE = ([("number1", 2, pstr, '00'),
                      ("title", 12, pstr, 'PDIMSTO 1.0 '),
                      ("rundate", 8, pstr, None),
                      #  ("runtime", 4, pstr, '0553'),
                      ("runtime", 4, pstr, '0832'),
                      ("runid", 5, pstr, None),
                      ("salaryperiod", 6, pstr, None),
                      ("periodstart", 8, pstr, None),
                      ("periodend", 8, pstr, None),
                      ("trail", 60, pstr, ' ' * 60),
                      ("newline", 1, pstr, '\n')],

                     [("number1", 2, pstr, '01'),
                      ("periodstart", 8, pstr, "{periodstart}"),
                      ("periodend", 8, pstr, "{periodend}"),
                      ("number2", 3, pstr, '000'),
                      ("empno", 5, pstr, None),
                      ("account", 4, pstr, None),
                      ("amount", 11, pamount, None),
                      ("currency", 3, pstr, 'SEK'),
                      ("value", 9, pstr, '00000,00 '),
                      ("trail", 60, pstr, ' ' * 60),
                      ("newline", 1, pstr, '\n')],

                     [("number1", 6, pstr, '990000'),
                      ("numrecords", 5, pint, None),
                      ("trail", 102, pstr, ' ' * 102),
                      ("newline", 1, pstr, '\n')],

                     {'correct': 'amount'})


PERDIEM_SPECIFIER_NO = ([("number1", 2, pstr, '00'),
                         ("title", 12, pstr, 'CMSPDIEM1.0 '),
                         ("rundate", 8, pstr, None),
                         ("runtime", 4, pstr, None),
                         ("runid", 5, pstr, None),
                         ("salaryperiod", 6, pstr, None),
                         ("periodstart", 8, pstr, None),
                         ("periodend", 8, pstr, None),
                         ("trail", 60, pstr, ' ' * 60),
                         ("newline", 1, pstr, '\n')],

                        [("number1", 2, pstr, '01'),
                         ("periodstart", 8, pstr, "{periodstart}"),
                         ("periodend", 8, pstr, "{periodend}"),
                         ("number2", 3, pstr, '000'),
                         ("empno", 5, pstr, None),
                         ("account", 4, pstr, None),
                         ("amount", 11, pamount, None),
                         ("currency", 3, pstr, 'NOK'),
                         ("value", 9, pstr, '00000,00 '),
                         ("trail", 60, pstr, ' ' * 60),
                         ("newline", 1, pstr, '\n')],
                        
                        [("number1", 6, pstr, '990000'),
                         ("numrecords", 5, pint, None),
                         ("trail", 102, pstr, ' ' * 102),
                         ("newline", 1, pstr, '\n')],
                        
                        {'correct': 'amount'})

PERDIEM_SPECIFIER_DK = ([("number1", 2, pstr, '00'),
                      ("title", 12, pstr, 'CMSPDIEM1.0 '),
                      ("rundate", 8, pstr, None),
                      #  ("runtime", 4, pstr, '0553'),
                      ("runtime", 4, pstr, '0506'),
                      ("runid", 5, pstr, None),
                      ("salaryperiod", 6, pstr, None),
                      ("periodstart", 8, pstr, None),
                      ("periodend", 8, pstr, None),
                      ("trail", 60, pstr, ' ' * 60),
                      ("newline", 1, pstr, '\n')],

                     [("number1", 2, pstr, '01'),
                      ("periodstart", 8, pstr, "{periodstart}"),
                      ("periodend", 8, pstr, "{periodend}"),
                      ("number2", 3, pstr, '000'),
                      ("empno", 5, pstr, None),
                      ("account", 4, pstr, None),
                      ("amount", 11, pamount, None),
                      ("currency", 3, pstr, 'DKK'),
                      ("value", 9, pstr, '00000,00 '),
                      ("trail", 60, pstr, ' ' * 60),
                      ("newline", 1, pstr, '\n')],

                     [("number1", 6, pstr, '990000'),
                      ("numrecords", 5, pint, None),
                      ("trail", 102, pstr, ' ' * 102),
                      ("newline", 1, pstr, '\n')],

                     {'correct': 'amount'})

PERDIEMTAX_SPECIFIER_NO = ([("number1", 2, pstr, '00'),
                            ("title", 12, pstr, 'CMSXXX  1.0 '),
                            ("rundate", 8, pstr, None),
                            ("runtime", 4, pstr, None),
                            ("runid", 5, pstr, None),
                            ("salaryperiod", 6, pstr, None),
                            ("periodstart", 8, pstr, None),
                            ("periodend", 8, pstr, None),
                            ("trail", 60, pstr, ' ' * 60),
                            ("newline", 1, pstr, '\n')],

                           [("number1", 2, pstr, '01'),
                            ("periodstart", 8, pstr, "{periodstart}"),
                            ("periodend", 8, pstr, "{periodend}"),
                            ("number2", 3, pstr, '000'),
                            ("empno", 5, pstr, None),
                            ("account", 4, pstr, None),
                            ("amount", 11, pstr, '0000000,00 '),
                            ("currency", 3, pstr, ' ' * 3),
                            ("value", 9, pamount, None),
                            ("trail", 60, pstr, ' ' * 60),
                            ("newline", 1, pstr, '\n')],
                        
                           [("number1", 6, pstr, '990000'),
                            ("numrecords", 5, pint, None),
                            ("trail", 102, pstr, ' ' * 102),
                            ("newline", 1, pstr, '\n')],

                           {'correct': 'value'})


TEMP_CREW_SPECIFIER = ([("number1", 2, pstr, '00'),
                        ("title", 12, pstr, 'CMSTEMP 1.0 '),
                        ("rundate", 8, pstr, None),
                        ("runtime", 4, pstr, None), # FIXME: Check what number this is
                        ("runid", 5, pstr, None),
                        ("salaryperiod", 6, pstr, None),
                        ("periodstart", 8, pstr, None),
                        ("periodend", 8, pstr, None),
                        ("trail", 60, pstr, ' ' * 60),
                        ("newline", 1, pstr, '\n')],

                       [("number1", 2, pstr, '01'),
                        ("periodstart", 8, pstr, "{periodstart}"),
                        ("periodend", 8, pstr, "{periodend}"),
                        ("number2", 3, pstr, '000'),
                        ("empno", 5, pstr, None),
                        ("account", 4, pstr, None),
                        ("amount", 11, pstr, '0000000,00 '),
                        ("currency", 3, pstr, ' ' * 3),
                        ("value", 9, pamount, None),
                        ("trail", 60, pstr, ' ' * 60),
                        ("newline", 1, pstr, '\n')],

                       [("number1", 6, pstr, '990000'),
                        ("numrecords", 5, pint, None),
                        ("trail", 102, pstr, ' ' * 102),
                        ("newline", 1, pstr, '\n')],

                       {'correct': 'value'})

VACATIONYC_SPECIFIER = ([("number1", 2, pstr, '00'),
                         ("title", 12, pstr, 'CMSVAADY1.0 '),
                         ("rundate", 8, pstr, None),
                         ("runtime", 4, pstr, None), # FIXME: Check what number this is
                         ("runid", 5, pstr, None),
                         ("salaryperiod", 6, pstr, None),
                         ("periodstart", 8, pstr, None),
                         ("periodend", 8, pstr, None),
                         ("trail", 60, pstr, ' ' * 60),
                         ("newline", 1, pstr, '\n')],

                        [("number1", 2, pstr, '01'),
                         ("periodstart", 8, pstr, "{periodstart}"),
                         ("periodend", 8, pstr, "{periodend}"),
                         ("number2", 3, pstr, '000'),
                         ("empno", 5, pstr, None),
                         ("account", 4, pstr, None),
                         ("amount", 11, pstr, '0000000,00 '),
                         ("currency", 3, pstr, ' ' * 3),
                         ("value", 9, pamount, None),
                         ("trail", 60, pstr, ' ' * 60),
                         ("newline", 1, pstr, '\n')],

                        [("number1", 6, pstr, '990000'),
                         ("numrecords", 5, pint, None),
                         ("trail", 102, pstr, ' ' * 102),
                         ("newline", 1, pstr, '\n')],

                        {'correct': 'value'})

VACATIONYF_SPECIFIER = ([("number1", 2, pstr, '00'),
                         ("title", 12, pstr, 'CMSVAFDY1.0 '),
                         ("rundate", 8, pstr, None),
                         ("runtime", 4, pstr, None), # FIXME: Check what number this is
                         ("runid", 5, pstr, None),
                         ("salaryperiod", 6, pstr, None),
                         ("periodstart", 8, pstr, None),
                         ("periodend", 8, pstr, None),
                         ("trail", 60, pstr, ' ' * 60),
                         ("newline", 1, pstr, '\n')],

                        [("number1", 2, pstr, '01'),
                         ("periodstart", 8, pstr, "{periodstart}"),
                         ("periodend", 8, pstr, "{periodend}"),
                         ("number2", 3, pstr, '000'),
                         ("empno", 5, pstr, None),
                         ("account", 4, pstr, None),
                         ("amount", 11, pstr, '0000000,00 '),
                         ("currency", 3, pstr, ' ' * 3),
                         ("value", 9, pamount, None),
                         ("trail", 60, pstr, ' ' * 60),
                         ("newline", 1, pstr, '\n')],

                        [("number1", 6, pstr, '990000'),
                         ("numrecords", 5, pint, None),
                         ("trail", 102, pstr, ' ' * 102),
                         ("newline", 1, pstr, '\n')],

                        {'correct': 'value'})

SPECIFIERS = {'ALLOWANCE_D': {'S3': ALLOWANCE_D_SPECIFIER},
              'ALLOWANCE_M': {'S3': ALLOWANCE_M_SPECIFIER},
              'COMPDAYS' : {'DK': COMPDAYS_SPECIFIER,
                            'NO': COMPDAYS_SPECIFIER},
              'OVERTIME' : {'DK' : OVERTIME_SPECIFIER,
                            'NO': OVERTIME_SPECIFIER},
              'ALLOWANCE' : {'DK' : ALLOWNCE_SPECIFIER,
                            'NO': ALLOWNCE_SPECIFIER},
              'PERDIEM': {'NO': PERDIEM_SPECIFIER_NO,
                          'DK': PERDIEM_SPECIFIER_DK,
                          'S3': PERDIEM_SPECIFIER_SE},
              'PERDIEMTAX': {'NO': PERDIEMTAX_SPECIFIER_NO},
              'TEMP_CREW': {'DK': TEMP_CREW_SPECIFIER,
                            'NO': TEMP_CREW_SPECIFIER},
              'VACATIONYC' : {'NO': VACATIONYC_SPECIFIER},
              'VACATIONYF' : {'NO': VACATIONYF_SPECIFIER}}

SPECIFIERS_FILE = { 'ussalcph.dat': {'report':'OVERTIME', 'region':'DK'},
                    'ussalosl.dat': {'report':'OVERTIME', 'region':'NO'},
                    'svcph.dat': {'report':'ALLOWANCE', 'region':'DK'},
                    'svosl.dat': {'report':'ALLOWANCE', 'region':'NO'},
                    'tempcdk.sal': {'report':'TEMP_CREW', 'region':'DK'},
                    'tempcno.sal': {'report':'TEMP_CREW', 'region':'NO'},

                    'fdaycph.dat': {'report':'COMPDAYS', 'region':'DK'},
                    'fdayosl.dat': {'report':'COMPDAYS', 'region':'NO'},

                    'allowances1_cms_se_YYYYMMDD_i.dat': {'report':'ALLOWANCE_M', 'region':'S3'},
                    'allowances2_cms_se_YYYYMMDD_i.dat': {'report':'ALLOWANCE_D', 'region':'S3'},

                    'pdiemcph.dat': {'report':'PERDIEM', 'region':'DK'},
                    'pdiem_cms_se_YYYYMMDD_i.dat': {'report':'PERDIEM', 'region':'S3'},
                    'fdaycph.dat': {'report':'COMPDAYS', 'region':'DK'},
                    'fdayosl.dat': {'report':'COMPDAYS', 'region':'NO'},
                    'vaosla.dat': {'report':'VACATIONYC', 'region':'NO'},
                    'vaperosl.dat': {'report':'VACATIONYC', 'region':'NO'},
                    'vaoslf.dat': {'report':'VACATIONYF', 'region':'NO'}}

        
def handle(filename, region, report, retro_run_id, cancel_run_id, commit, included_ranks, ignored_ranks):
    specifier = SPECIFIERS[report][region]

    header, records, trailer, statistics = parse_file(specifier, filename)
    _, _, _, config = specifier

    ops = []

    print "# salary_run_id:"
    print "runid", int(header['runid'])
    print "starttime", to_abstime(header["rundate"] + header["runtime"])
    print "runtype", report
    print "admcode", "N"
    print "selector"
    print "extsys", region
    firstdate = to_abstime(header['periodstart'])
    print "firstdate", firstdate
    lastdate = to_abstime(header['periodend']) + RelTime(24, 0)
    print "lastdate", lastdate
    print "releasedate"
    print "note"
    print

    if retro_run_id != None:
        admcode = 'R'
        note = 'Retro of %s.' % retro_run_id
        selector = retro_run_id
    elif cancel_run_id != None:
        admcode = 'C'
        note = 'Cancellation of %s.' % cancel_run_id
        selector = None
    else:
        admcode = 'N'
        note = 'Imported by import_salary_file_to_db.py'
        selector = None

    connstr = os.environ['DB_URL']
    schemastr = os.environ['DB_SCHEMA']

    dc = DaveConnector(connstr, schemastr)
    l1 = dc.getL1Connection()
    max_run_id = l1.intRQuery("select max(runid) from salary_run_id", None)
    print "Got max runid %s" % max_run_id
    next_run_id = l1.intRQuery("select seq_salary_run.nextval from dual", None)
    while(next_run_id <= max_run_id):
        next_run_id = l1.intRQuery("select seq_salary_run.nextval from dual", None)

    run_id = next_run_id
    print "Using runid %s" % run_id

    ops.append(createOp('salary_run_id', 'N', {"runid" : run_id,
                                               "starttime" : int(to_abstime(header["rundate"] + header["runtime"])),
                                               "runtype" : report,
                                               "admcode" : admcode,
                                               "selector" : selector,
                                               "extsys" : region,
                                               "firstdate" : int(firstdate) / 24 / 60,
                                               "lastdate" : int(lastdate) / 24 / 60,
                                               "releasedate" : None,
                                               "note" : note}))

    crewids = {}
    ranks = {}

    for record in records:
        empno = record['empno']
        # print record
        if not empno in crewids.keys():
            s = sorted(dc.runSearch(DaveSearch("crew_employment", ["extperkey = '%s' AND validfrom <= %s" % (empno, int(firstdate))], False)), key=itemgetter('validto'), reverse=True)
            # print "# crew_employment"
            # print s
            # print
            crewids[empno] = s[0]['crew']
            ranks[empno] = s[0]['crewrank']
            validfrom = AbsTime(s[0]['validfrom'])
            validto = AbsTime(s[0]['validto'])
            if validto <= firstdate:
                print("WARNING: Using crewid %s for extperkey %s even though employment is not active (%s not in %s - %s)" %
                      (crewids[empno], empno, firstdate, validfrom, validto))
            # if crewids[empno] != empno:
            #     print "# Crew extperkey and crewid differs"
            #     print "%s -> %s" % (empno, crewids[empno])
            #     print
        # print "# salary_basic_data"
        # print "runid", int(header['runid'])
        # print "extperkey", empno
        # print "extartid", record['account']
        # print "crewid", crewids[empno]
        # print "amount", int(record['amount'] * 100)
        # print

        if ranks[empno] in included_ranks:
            ops.append(createOp('salary_basic_data', 'N', {"runid" : run_id,
                                                           "extperkey" : empno,
                                                           "extartid" : record['account'],
                                                           "crewid" : crewids[empno],
                                                           "amount" : int(record[config['correct']] * 100)}))
        elif ranks[empno] in ignored_ranks:
            pass
        else:
            print "Ignoring crew %s with rank %s" % (empno, ranks[empno])

    program = get_program()
    dc.getConnection().setProgram(program)

    remark = "Test of salary import"
    # print "# DB operations"
    # print ops
    # print
    if commit:
        commitid = DaveStorer(dc, reason=remark).store(ops, returnCommitId=True) 
        print "%s operations committed to db with id %s" % (len(ops), commitid)
    else:
        print "%s operations not committed to db" % len(ops)



# TODO: Add desired argument and check them if it necessary
def run():
    """ This function parse and check or set all variables to execute the module execution function.

    This function first set all argparser variables and then try to parse them. There are some values that need to be
    set with default values. It also initialize logging object class according to argparser values which are set by user.
    And finally, it calls the execution function with proper values.

    """
    ap = ArgumentParser(description=__doc__, formatter_class=RawDescriptionHelpFormatter)
    ap.add_argument('-r', '--region', help='set to DK, SE, NO')
    ap.add_argument('-t', '--type', help='set salary report type to: ALLOWNCE, ALLOWNCE_C, ALLOWNCE_D, COMPDAYS, OVERTIME, PERDIEM, TEMP_CREW, VACATIONYC, VACATIONYF')
    ap.add_argument('-f', '--file', help='set salary file name like ussalcph.dat')
    ap.add_argument('-R', '--retro', help='set retro run id')
    ap.add_argument('-C', '--cancel', help='set cancel run id')
    ap.add_argument('-c', '--commit', help='commit to db')
    ap.add_argument('-m', '--maincat', help='include crew with main category C/F')

    args = ap.parse_args()

    if not args.file:
        print("You need to specify a file name")
        return
    if not args.region:
        print("You need to specify a region")
        return
    if not args.type:
        print("You need to specify a run type")
        return

    ranks_c = ['AA', 'AH', 'AP', 'AS']
    ranks_f = ['FC', 'FP', 'FS']
    if args.maincat == 'C':
        included_ranks = ranks_c
        ignored_ranks = ranks_f
    elif args.maincat == 'F':
        included_ranks = ranks_f
        ignored_ranks = ranks_c
    elif args.maincat == None:
        included_ranks = ranks_f + ranks_c
        ignored_ranks = []
    else:
        raise Exception("Unknown main category %s" % args.maincat)

    handle(args.file, args.region, args.type, args.retro, args.cancel, args.commit, included_ranks, ignored_ranks)


if __name__ == '__main__':
    """ Main function to report start and end time and run the main function run()
        Signal handler is registered here as well.
    """
    run()



from behave import *

import os
import re
import shutil
from datetime import date as dt

import Cui
import util_custom as custom

from AbsTime import AbsTime
from RelTime import RelTime

# There are different ways to match steps with python code, e.g. parse and re
# Given the trip has another "leg"

# behave.use_step_matcher('parse') is default
# @given(u'the trip has {a_another} "{activity}"
# def create_activity_on_trip(activity, a_another='unused'):

# behave.use_step_matcher('re')
# @given(u'the trip has (?P<a_another>a|another) "(?P<activity>[a-z]*")
# def create_activity_on_trip(activity, a_another='unused'):

# a_another, activity and others are used in many places and are replaced with mathching_patterns
# that uses string formatting with dictionaries: '%(key)s' % {key:value} => 'value'
# @given(u'the trip has %(a_another)s "%(activity)s") % {'a_another':'(?P<a_another>a|another)', 'activity':'(?P<activity>[a-z]*)'}

# The dictionary is then replaced with the constant matching_patterns:
# @given(u'the trip has %(a_another)s "%(activity)s") % util.matching_patterns

# Accepted arguments are then verified using the verify_XXX functions below
# to make sure that the tester has entered proper values.
# It is generally better to be a little bit more forgiving when accepting values, and then print proper assert messages
# instead of not accepting a step at all, which will just turn yellow as a 'no match'.

# Common data input matching strings
matching_patterns = {'a_another':'(?P<a_another>a|another)',
                     'activity':'(?P<activity>[a-z]*)',
                     'arr_apt':'(?P<arr_apt>[A-Z]*)',
                     'attribute':'(?P<attribute>[\-A-Z0-9]*)',
                     'attr_val':'(?P<attr_val>\"[\-A-Z0-9 /]*\")',
                     'contract':'(?P<contract>[\-A-Z0-9_]*)',
                     'crew_roster':'(?P<crew_roster>crew|roster)',
                     'date':'(?P<date>[A-Za-z0-9 ]*)',
                     'date2':'(?P<date2>[A-Za-z0-9]*)',
                     'dep_apt':'(?P<dep_apt>[A-Z]*)',
                     'doc':'(?P<doc>[A-Z0-9+,]*)',
                     'docno':'(?P<docno>[A-Z0-9+,]*)',
                     'flight_id':'(?P<flight_id>[0-9]+)',
                     'homebase':'(?P<homebase>[A-Z]*)',
                     'hour':'(?P<hour>[0-9]*)',
                     'leg_ix':'(?P<leg_ix>\d*)',
                     'leg_ix_1':'(?P<leg_ix_1>\d*)',
                     'leg_ix_2':'(?P<leg_ix_2>\d*)',
                     'maindocno':'(?P<maindocno>[A-Z0-9+,]*)',
                     'month':'(?P<month>[A-Z]*)',
                     'on_off':'(?P<on_off>on|off)',
                     'pass_fail':'(?P<pass_fail>pass|fail)',
                     'personal_activity':'(?P<personal_activity>[A-Z0-9]*)',
                     'pos':'(?P<pos>[A-Z0-9 ]+)',
                     'qualification':'(?P<qualification>[\-A-Z0-9\+_]*)',
                     'rave_name':'(?P<rave_name>.*)',
                     'rave_value':'(?P<rave_value>.*)',
                     'restriction':'(?P<restriction>[\-A-Z0-9\+]*)',
                     'roster_ix':'(?P<roster_ix>#?\d+)',
                     'rule_set':'(?P<rule_set>[A-Za-z_0-9]*)',
                     'stn':'(?P<stn>[A-Z]*)',
                     'table_name':'(?P<table_name>[a-z_]*)',
                     'time':'(?P<time>[0-9:]*)',
                     'time2':'(?P<time2>[0-9:]*)',
                     'total':'(?P<total>\d*)',
                     'trip_ix':'(?P<trip_ix>#?\d+)',
                     'un_locked':'(?P<un_locked>locked|unlocked)',
                     'year':'(?P<year>[0-9:]*)',
                     'window_ix':'(?P<window_ix>[1234])',
                     'window_mode':'(?P<window_mode>[A-Za-z ]*)'
                     }

@given(u'Pairing_CC')
def set_up_for_pairing(context):
    context.application = 'Pairing_CC'

@given(u'JCP')
def set_up_for_pairing(context):
    context.application = 'Pairing_CC'

@given(u'Pairing_FC')
def set_up_for_pairing(context):
    context.application = 'Pairing_FC'

@given(u'JCR')
def set_up_for_rostering(context):
    context.application = 'Rostering_CC'

@given(u'Rostering_CC')
def set_up_for_rostering(context):
    context.application = 'Rostering_CC'

@given(u'Rostering_FC')
def set_up_for_rostering(context):
    context.application = 'Rostering_FC'

@given(u'Tracking')
def set_up_for_tracking(context):
    context.application = 'Tracking'

@step(u'prettyprint')
def pretty_print(context):
    """
    prettyprint
     Helps Behave avoiding overwriting important lines (this one will be overwritten instead).
     Possibly related to:
     https://github.com/behave/behave/issues/167
    """
    pass

# 
# Verify input variables in test definitions
#
def verify_ac_type(ac_type):
    """
    MD80, or none
    """
    ac_type = ac_type.encode().upper()
    regexp = '^[A-Z0-9]*$'
    if ac_type:
        assert re.match(regexp, ac_type), 'Cannot handle ac type %s, use MD80' % ac_type
    return ac_type

def verify_activity(activity):
    """
    leg, dh, ground
    """

    handled_activities = ('leg', 'dh', 'ground', '')
    activity = activity.encode().lower()
    assert activity in handled_activities, 'Cannot handle activity "%s", only %s' % (activity, ", ".join(handled_activities))
    return activity


def verify_attr_val(attr_val):
    attr_str = None
    attr_int = None
    attr_abs = None
    attr_rel = None

    if attr_val != '':
        if attr_val.startswith('"') and attr_val.endswith('"'):
            attr_str = attr_val[1:-1]
        else:
            try:
                attr_int = int(attr_val)
            except:
                try:
                    attr_abs = AbsTime(str(attr_val))
                except:
                    try:
                        attr_rel = RelTime(attr_val)
                    except:
                        attr_str = attr_val # Fallback to string
    return attr_str, attr_int, attr_abs, attr_rel


def verify_attributes(attr1, attr2):
    for key in attr1:
        assert not (key in attr2 and key != 'validfrom' and key != 'validto'), 'Overlapping attribute "%s"' % key


def verify_in_list(value, value_list, value_name):
    """
    Verify that value is in list
    """

    value = value.encode().lower()
    assert value in value_list, 'Cannot handle %s "%s", only %s' % (value_name, value, ", ".join(value_list))
    return value


def verify_carrier(carrier):
    """
    JA
    """
    handled_carriers = custom.handled_carriers
    handled_carriers.append('')
    carrier = carrier.encode().upper()
    assert carrier in handled_carriers, 'Cannot handled carrier "%s", only %s' % (carrier, ", ".join(handled_carriers))
    return carrier


def verify_carrier(code):
    """
    Z2
    """
    code = code.encode().upper()
    return code


def verify_date(date):
    """
    6Jun2016, 06JUN2016, 6JUNTHIS, 06JUNTHIS, 6THIS, 06THIS
    """
    if not date:
        return
    date = date.encode().upper()

    if 'THIS' in date:
        today = dt.today()
        if len(date) > 7:
            current_year = today.strftime('%Y')
            date = date[:-4] + current_year
        elif len(date) < 7:
            current_month_year = today.strftime("%b").upper() + today.strftime("%Y")
            date = date[:-4] + current_month_year

    p = re.compile('(?P<day>[0-9]{1,2})(?P<mon>[A-Z]{3})(?P<year>[0-9]{2,4})')
    m = p.match(date)
    assert m, 'Cannot handle date %s' % date

    day = int(m.group('day'))
    assert 1 <= day and day <= 31, 'Date day out of range: %d, %s' % (day, date)

    mon = m.group('mon')
    assert mon in custom.handled_months, 'Date month unhandled: %s, %s' \
        % (mon, date)

    year = m.group('year')
    _year = int(year)
    if len(year) == 2:
        if _year >= 86:
            _year += 1900
        else:
            _year += 2000
    assert 1900 <= _year and _year <= 2100, 'Date year out of range: %d, %s' % (_year, date)

    ret = '%02d%s%d' % (day, mon, _year)
    return ret

def verify_deps_arrs(deps_arrs):
    """
    departs or arrives
    """
    deps_arrs = deps_arrs.encode().lower()
    if deps_arrs in ('departs', 'arrives'):
        return deps_arrs
    assert False, 'Cannot handle "%s", use "departs|arrives"' % deps_arrs

def verify_int(i):
    """
    1, or none
    """
    if i == '':
        return None
    try:
        i = int(i)
    except ValueError:
        assert False, 'Cannot handle %s, use 3' % i
    return i


def verify_int_list(i):
    """
    List of integers
    """
    if i == '':
        return None

    int_list = []
    try:
        for part in i.split(','):
            maybe_range = part.split('-')
            if len(maybe_range) == 2:
                int_list = int_list + range(int(maybe_range[0]), int(maybe_range[1]) + 1)
            elif len(maybe_range) == 1:
                int_list = int_list + [int(maybe_range[0])]
            else:
                raise ValueError
    except ValueError:
        assert False, 'Cannot handle %s, use 3 or 3,4 or 3-4 or 3,4,5-6' % i
    return int_list


def verify_boolean(b):
    """
    1, or none
    """
    if b == '':
        return None
    try:
        b = bool(b)
    except ValueError:
        assert False, 'Cannot handle %s, use True or False' % b
    return b


def verify_str(text):
    """
    "content", or none
    """
    if text == '':
        return None
    try:
        text = str(text)
    except ValueError:
        assert False, 'Cannot handle %s, use Bah' % text
    return text


def verify_pos(pos):
    """
    Position as number or string
    """
    if pos == '':
        return None

    pos_map = {'1'  : '1/0/0/0//0/0/0/0//0/0',
               'FC' : '1/0/0/0//0/0/0/0//0/0',
               '2'  : '0/1/0/0//0/0/0/0//0/0',
               'FP' : '0/1/0/0//0/0/0/0//0/0',
               '3'  : '0/0/1/0//0/0/0/0//0/0',
               'FR' : '0/0/1/0//0/0/0/0//0/0',
               '4'  : '0/0/0/1//0/0/0/0//0/0',
               'FU' : '0/0/0/1//0/0/0/0//0/0',
               '5'  : '0/0/0/0//1/0/0/0//0/0',
               'AP' : '0/0/0/0//1/0/0/0//0/0',
               '6'  : '0/0/0/0//0/1/0/0//0/0',
               'AS' : '0/0/0/0//0/1/0/0//0/0',
               '7'  : '0/0/0/0//0/0/1/0//0/0',
               'AH' : '0/0/0/0//0/0/1/0//0/0',
               '8'  : '0/0/0/0//0/0/0/1//0/0',
               'TU' : '0/0/0/0//0/0/0/1//0/0',
               '9'  : '0/0/0/0//0/0/0/0//1/0',
               'TL' : '0/0/0/0//0/0/0/0//1/0',
               '10' : '0/0/0/0//0/0/0/0//0/1',
               'TR' : '0/0/0/0//0/0/0/0//0/1'}

    try:
        pos = pos_map[pos]
    except ValueError:
        assert False, 'Cannot handle position %s, use 1 or FC' % pos
    return pos


def verify_complement(complement):
    """
    Complement in the format 0/0/0/0//0/0/0/0//0/0
    """

    pattern = '0/0/0/0//0/0/0/0//0/0'
    error_string = 'Invalid complement %s, use this format %s' % (complement, pattern)

    assert len(pattern.split('/')) == len(complement.split('/')), error_string

    for p, c in zip(pattern.split('/'), complement.split('/')):
        if p == '':
            assert p == c, error_string
        else:
            try:
                assert int(c) >= 0, error_string
            except:
                assert False, error_string
    return '/'.join([c for c in complement.split('/') if c != ''])


def verify_file_name(file_name):
    """
    /some/absolute/file/name
    some/relative/file/name
    name
    """
    file_name = file_name.encode()
    p = re.compile('[a-zA-Z0-9_/]*')
    assert p.match(file_name), 'Cannot handle all characters in %s' % file_name
    return file_name

def verify_plan_path(plan_path):
    """
    plan/version/local_plan
    plan/version/local_plan/sub_plan
    plan/version/local_plan/sub_plan/solution
    """

    plan_path = plan_path.encode()
    p = re.compile('[a-zA-Z0-9_/]*')
    assert p.match(plan_path), 'Cannot handle all charcters in %s' % plan_path
    num_dir = plan_path.count('/')
    assert num_dir in (3,4,5), 'Cannot handle %d dirs in plan path' % num_dir

    return plan_path

def verify_rave_name(rave_name):
    """
    module.%variable%, True
    module.rule, False
    keyword, False

    Assume: No numbers in module names
    """

    # Clean escaped characters
    rave_name = '"'.join(rave_name.split('\\"'))

    if rave_name.find('.') > 0:
        if rave_name.find('%') > 0:
            # module.%variable%
            p = re.compile('^[a-zA-Z_0-9]*\.%[a-zA-Z0-9_%\(\),\.\s"]*$')
            assert p.match(rave_name), 'Cannot handle variable "%s", use "module.%%variable%%"' % rave_name
        elif rave_name.startswith("rule_on(") and rave_name.endswith(")"):
            # rule_on(module.rule)
            p = re.compile('^[a-zA-Z_0-9]*\.[a-zA-Z0-9_]*$')
            assert p.match(rave_name[8:-1]), 'Cannot handle expression "%s", use "rule_on(module.rule)"' % rave_name
        else:
            # module.rule
            p = re.compile('^[a-zA-Z_0-9]*\.[a-zA-Z0-9_]*$')
            assert p.match(rave_name), 'Cannot handle rule "%s", use "module.rule"' % rave_name
    else:
        # keyword
        p = re.compile('^[a-z_0-9]*$')
        assert p.match(rave_name), 'Cannot handle keyword "%s", use "keyword"' % rave_name
            
    return rave_name

def verify_rave_value(rave_value):
    """
    0:45
    06JUL2003 09:00
    or any string?!
    """
    rave_value = rave_value.encode()
    return rave_value

def verify_stn(stn):
    """
    GOT
    Assume 3 letter IATA codes or empty string
    """
    p = re.compile('^[A-Z][A-Z][A-Z]$')
    if stn:
        stn = stn.encode().upper()
        assert p.match(stn), 'Cannot handle station "%s", use "GOT"' % stn
    return stn

def verify_time(time):
    """
    12:45, or none
    """
    regexp = '^[0-2]?[0-9]:[0-5][0-9]$'
    if time:
        time = time.encode()
        assert re.match(regexp, time), 'Cannot handle time %s, use 12:45' % time
    return time


def verify_abstime(time):
    """
    01FEB2018, 01FEB2018 12:45 or none
    """
    if time:
        try:
            time = AbsTime(str(time))
        except:
            assert False, 'Cannot handle abstime %s, use 01FEB2018 or 01FEB2018 12:45' % time
    else:
        time = None
    return time


def verify_reltime(time):
    """
    12:45 or none
    """
    if time:
        try:
            time = RelTime(str(time))
        except:
            assert False, 'Cannot handle reltime %s, use 12:45' % time
    return time


def verify_time_or_datetime(time):
    """
    12:45, 01FEB2018 12:45 or none
    """
    if time:
        time = time.encode()
        try:
            time = str(RelTime(time))
        except:
            try:
                time = str(AbsTime(time))
            except:
                assert False, 'Cannot handle time or datetime %s, use 12:45 or 01FEB2018 12:45' % time
    return time


def verify_window_ix_to_area(window_ix):
    """
    Verify that window_ix is a proper number, ie 1..4
    and return the corresponding window_area
    1 -> Cui.CuiArea0
    """
    window_ix = verify_int(window_ix)

    if window_ix < 5:
        window_area = (Cui.CuiArea0, Cui.CuiArea1, Cui.CuiArea2, Cui.CuiArea3)[window_ix - 1]
    else:
        assert False, 'Cannot handle window %i, only  1,2,3 or 4' % window_ix
    return window_area

def verify_window_mode(mode):
    """
    Verify that mode is a proper window mode
    return lowercase mode and Cui window mode
    """
    all_window_modes = {'leg sets':Cui.LegSetMode,
                        'legs':Cui.LegMode,
                        'duties':Cui.RtdMode,
                        'trips':Cui.CrrMode,
                        'crew':Cui.CrewMode,
                        'rosters':Cui.CrewMode,
                        'rotations':Cui.AcRotMode}
    mode = mode.encode().lower()
    if not mode in all_window_modes.keys():
        # mode may be singular form, ie trip instead of trips
        mode = mode + 's'
        if not mode in all_window_modes.keys():
            assert False, 'Cannot handle window mode %s, use e.g. trips or rosters' % mode

    return (mode, all_window_modes[mode])

def copy_dirs(from_dirs, to_dirs):
    rel_path = ''
    orig_root = ''
    orig_root_len = 0
    os.chdir(to_dirs)

    for dirPath, subdirList, fileList in os.walk(from_dirs):
        if orig_root:
            rel_path = dirPath[orig_root_len+1:]
            os.chdir(to_dirs)

            create_dir(rel_path)
            os.chdir(rel_path)
        else:
            orig_root = dirPath
            orig_root_len = len(orig_root)

        for fname in fileList:
            if not (fname.endswith('~') or fname.endswith('.pyc')):
                from_file = os.path.join(orig_root, rel_path, fname)
                to_file = fname
                copy_file(from_file, to_file)

def create_dir(needed_dir):
    if not os.path.isdir(needed_dir):
        try:
            os.mkdir(needed_dir)
        except:
            assert False, 'Could not create dir: %s' % needed_dir

def copy_file(from_file, to_file):
    bkp_file = to_file +'.behave_bkp'
    try:
        shutil.move(to_file, bkp_file)
    except IOError as exc:
        if exc.errno in (2,):
            # No such file or directory, ignore
            pass
        else:
            assert False, 'Could not move to bakup: %s' % to_file
    try:
        shutil.copy(from_file, to_file)
    except IOError as exc:
        raise

def default(value, default):
    return default if value == None else value

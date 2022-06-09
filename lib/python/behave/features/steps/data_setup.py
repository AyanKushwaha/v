from behave import use_step_matcher
from AbsTime import AbsTime

import util
import util_custom
import random


use_step_matcher('re')


CREW_ATTRIBUTE_COLUMNS = ('attribute', 'value', 'valid from', 'valid to')

#
# Set up personal activity data
#
@given(u'crew member %(roster_ix)s has a personal activity "%(personal_activity)s" at station "%(stn)s" that starts at %(date)s %(time)s and ends at %(date2)s %(time2)s' % util.matching_patterns)
def create_personal_activity(context, roster_ix, personal_activity, stn, date, time, date2, time2, a_another='unused'):
    """
    Given crew member 1 has a personal activity "F7" at station "OSL" that starts at 1Aug2018 00:00 and ends at 2Aug2018 01:00
    """
    _create_personal_activity(context, roster_ix=roster_ix, personal_activity=personal_activity, stn=stn, start_date=date, start_time=time, end_date=date2, end_time=time2)


def _create_personal_activity(context, roster_ix, personal_activity, start_date=None, start_time=None, end_date=None, end_time=None, stn=None):
    roster_ix = util.verify_int(roster_ix)
    start_date = util.verify_date(start_date)
    start_time = util.verify_time(start_time)
    end_date = util.verify_date(end_date)
    end_time = util.verify_time(end_time)
    stn = util.verify_stn(stn)
    context.ctf.create_personal_activity(crew_ix=roster_ix, personal_activity=personal_activity, start_date=start_date, start_time=start_time, end_date=end_date, end_time=end_time, stn=stn)


activity_columns = ('act', 'car', 'num', 'dep stn', 'arr stn', 'dep', 'arr', 'ac_typ', 'code', 'date')

#
# Set up activity data
#
@given(u'%(a_another)s "%(activity)s"' % util.matching_patterns)
def create_activity(context, activity, a_another='unused'):
    """
    Given a "leg"
    """
    _create_activity(context, activity=activity)

@given(u'%(a_another)s "%(activity)s" that departs at %(time)s' % util.matching_patterns)
def create_activity_dep_time(context, time, activity, a_another='unused'):
    """
    Given a "leg" that departs at 10:00
    """
    _create_activity(context, dep=time, activity=activity)

@given(u'%(a_another)s "%(activity)s" that departs at %(date)s' \
           % util.matching_patterns)
def create_activity_dep_date(context, date, activity, a_another='unused'):
    """
    Given a "leg" that departs at 9Jul2003
    """
    _create_activity(context, date=date, activity=activity)

@given(u'%(a_another)s "%(activity)s" that departs at %(date)s %(time)s' \
           % util.matching_patterns)
def create_activity_dep_date_time(context, date, time, activity, a_another='unused'):
    """
    Given a "leg" that departs at 9Jul2003 12:00
    """
    print(date)
    print(time)
    _create_activity(context, date=date, dep=time, activity=activity)


@given(u'%(a_another)s "%(activity)s" that arrives at %(time)s' % util.matching_patterns)
def create_activity_arr_time(context, time, activity, a_another='unused'):
    """
    Given a "leg" that arrives at 12:00
    """
    _create_activity(context, arr=time, activity=activity)

@given(u'%(a_another)s "%(activity)s" that arrives at %(date)s' % util.matching_patterns)
def create_activity_arr_date(context, date, activity, a_another='unused'):
    """
    Given a "leg" that arrives at 11Jul2003
    """
    _create_activity(context, date=date, activity=activity)

@given(u'%(a_another)s "%(activity)s" that arrives at %(date)s %(time)s' % util.matching_patterns)
def create_activity_arr_date(context, date, time, activity, a_another='unused'):
    """
    Given a "leg" that arrives at 11Jul2003 14:00
    """
    _create_activity(context, date=date, arr=time, activity=activity)

@given(u'%(a_another)s "%(activity)s" that departs at %(time)s and arrives at %(time2)s' % util.matching_patterns)
def create_activity_dep_arr_time(context, activity, time, time2, a_another='unused'):
    """
    Given a "leg" that departs at 10:00 and arrives at 12:00
    """
    _create_activity(context, dep=time, arr=time2, activity=activity)


@given(u'%(a_another)s "%(activity)s" that departs from "%(stn)s"' % util.matching_patterns)
def create_activity_dep_stn(context, activity, stn, a_another='unused'):
    """
    Given a "leg" that departs from "DEP"
    """
    _create_activity(context, dep_stn=stn)

@given(u'%(a_another)s "%(activity)s" that arrives at "%(stn)s"' % util.matching_patterns)
def create_activity_arr_stn(context, activity, stn, a_another='unused'):
    """
    Given a "leg" that arrives at "ARR"
    """
    _create_activity(context, arr_stn=stn)

@given(u'%(a_another)s "%(activity)s" that departs from "%(stn)s" at %(time)s' % util.matching_patterns)
def create_activity_dep_stn_dep(context, activity, stn, time, a_another='unused'):
    """
    Given a "leg" that departs from "DEP" at 14:00
    """
    _create_activity(context, dep_stn=stn, dep=time)

@given(u'%(a_another)s "%(activity)s" that arrives at "%(stn)s" at %(time)s' % util.matching_patterns)
def create_activity_arr_stn_arr(context, activity, stn, time, a_another='unused'):
    """
    Given a "leg" that arrives at "ARR" at 16:00
    """
    _create_activity(context, activity=activity, arr_stn=stn, arr=time)

def _create_activity(context, date=None, dep=None, arr=None, dep_stn=None, arr_stn=None, activity='leg'):
    date = util.verify_date(date)
    dep = util.verify_time(dep)
    arr = util.verify_time(arr)
    dep_stn = util.verify_stn(dep_stn)
    arr_stn = util.verify_stn(arr_stn)
    activity = util.verify_activity(activity)
    context.ctf.create_activity(activity=activity, date=date, dep=dep, arr=arr, dep_stn=dep_stn, arr_stn=arr_stn)


@given(u'the following activities')
def create_activities_from_table(context):
    """
    Given the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   |
    | leg | 7511 |         | ARR     | 01FEB2018 | 10:25 | 11:35 |
    | leg |      |         |         | 01FEB2018 | 12:25 |       |
    | leg |      |         |         | 01FEB2018 | 12:25 |       |
    | leg |      |         |         | 01FEB2018 |       | 17:00 |

Available columns:
Colums prepended with # are not yet implemented.

#        label:            A label to assign to the activity, used to reference it (example: long flight)
        act:              Any one of: leg, dh, oag, ground, transport (example: leg)
        car:              Flight carrier code (example: JA)
        num:              Flight number (example: 7511)
#        suf:              Flight suffix (example: P)
        dep stn:          Departure airport code (example: ORY)
        arr stn:          Arrival airport code (example: ARR)
        dep:              Departure time (example: 01NOV2016 10:25)
        arr:              Arrival time (example: 01NOV2016 12:25)
        ac_typ:           Aircraft type (example: 74H)
#        srv_typ:          Service type (example: C)
        code:             Only applicable for ground duties, ground duty code (example: SBY)
#        duty type:        Type of duty, used mainly for augmentation (example: REL)
#        cockpit employer: The carrier code of the cockpit employer (example: JA)
#        cabin employer:   The carrier code of the cabin employer (example: JA)
#        ac owner:         The carrier code of the aircraft owner (example: JA)
#        user tags:        User tags defined in the system (example: PRE_BOOKED)
#        ac change         Whether the current and the next leg are the same aircraft or not (example: False)
    """
    # Add all needed columns, default value to ''
    for column in activity_columns:
        context.table.ensure_column_exists(column)

    # Verify that all columns can be handled
    for column in context.table.headings:
        assert column in activity_columns, 'Cannot handle column %s, use: %s' % (column, ", ".join(activity_columns))
    
    # Add all activities from table
    for row in context.table:
        activity = util.verify_activity(row[context.table.get_column_index('act')])
        assert not activity == 'dh', 'Cannot create free dh legs, only as part of trips'
        carrier = util.verify_carrier(row[context.table.get_column_index('car')])
        code = util.verify_str(row[context.table.get_column_index('code')])
        flight_num = util.verify_int(row[context.table.get_column_index('num')])
        dep_stn = util.verify_stn(row[context.table.get_column_index('dep stn')])
        arr_stn = util.verify_stn(row[context.table.get_column_index('arr stn')])
        date = util.verify_date(row[context.table.get_column_index('date')])
        dep = util.verify_time(row[context.table.get_column_index('dep')])
        arr = util.verify_time(row[context.table.get_column_index('arr')])
        ac_typ = util.verify_ac_type(row[context.table.get_column_index('ac_typ')])

        context.ctf.create_activity(activity=activity, car=carrier, code=code, num=flight_num, date=date, dep=dep, arr=arr, dep_stn=dep_stn, arr_stn=arr_stn, ac_typ=ac_typ)


@given(u'leg %(leg_ix_1)s has onward flight leg %(leg_ix_2)s' % util.matching_patterns)
def connect_onward_flight_ref(context, leg_ix_1, leg_ix_2):
    """
    Given leg 5 has onward flight leg 6
    """
    leg_ix_1 = util.verify_int(leg_ix_1)
    leg_ix_2 = util.verify_int(leg_ix_2)
    context.ctf.connect_onward_flight_ref(leg_ix_1, leg_ix_2)

#
# Set up trip data
#

@given(u'%(a_another)s trip' % util.matching_patterns)
def create_trip(context, a_another='unused'):
    """
    Given a trip
    """
    context.ctf.create_trip()

@given(u'%(a_another)s trip with homebase "%(stn)s"' % util.matching_patterns)
def create_trip_with_homebase(context, stn, a_another='unused'):
    """
    Given a trip with homebase "GOT"
    """
    stn = util.verify_stn(stn)
    context.ctf.create_trip(homebase=stn)

@given(u'the trip has %(a_another)s "%(activity)s"' % util.matching_patterns)
def create_activity_on_trip(context, activity, a_another='unused'):
    """
    Given the trip has a "dh"
    """
    _create_activity_on_trip(context, activity)

@given(u'the trip has %(a_another)s "%(activity)s" that departs from "%(stn)s"' % util.matching_patterns)
def create_activity_on_trip_dep_stn(context, activity, stn, a_another='unused'):
    """
    Given the trip has a "dh" that departs from "GOT"
    """    
    _create_activity_on_trip(context, activity=activity, dep_stn=stn)

@given(u'the trip has %(a_another)s "%(activity)s" that departs at %(time)s' % util.matching_patterns)
def create_activity_on_trip_dep_time(context, activity, time, a_another='unused'):
    """
    Given the trip has a "leg" that departs at 10:00
    """        
    _create_activity_on_trip(context, activity=activity, dep=time)

@given(u'the trip has %(a_another)s "%(activity)s" that departs at %(date)s' % util.matching_patterns)
def create_activity_on_trip_dep_date(context, activity, date, a_another='unused'):
    """
    Given the trip has a "leg" that departs at 9Jul2003
    """        
    _create_activity_on_trip(context, activity=activity, date=date)

@given(u'the trip has %(a_another)s "%(activity)s" that departs at %(date)s %(time)s' % util.matching_patterns)
def create_activity_on_trip_dep_date_time(context, activity, date, time, a_another='unused'):
    """
    Given the trip has a "leg" that departs at 9Jul2003 10:00
    """        
    _create_activity_on_trip(context, activity=activity, date=date, dep=time)

@given(u'the trip has %(a_another)s "%(activity)s" that arrives at "%(stn)s"' % util.matching_patterns)
def create_activity_on_trip_arr_stn(context, activity, stn, a_another='unused'):
    """
    Given the trip has a "leg" that arrives at "ARR"
    """    
    _create_activity_on_trip(context, activity=activity, arr_stn=stn)

@given(u'the trip has %(a_another)s "%(activity)s" that arrives at %(time)s' % util.matching_patterns)
def create_activity_on_trip_arr_time(context, activity, time, a_another='unused'):
    """
    Given the trip has a "leg" that arrives at 14:00
    """        
    _create_activity_on_trip(context, activity=activity, arr=time)

@given(u'the trip has %(a_another)s "%(activity)s" that arrives at %(date)s' % util.matching_patterns)
def create_activity_on_trip_arr_date(context, activity, date, a_another='unused'):
    """
    Given the trip has a "leg" that arrives at 11Jul2003
    """        
    _create_activity_on_trip(context, activity=activity, date=date)

@given(u'the trip has %(a_another)s "%(activity)s" that arrives at %(date)s %(time)s' % util.matching_patterns)
def create_activity_on_trip_arr(context, activity, date, time, a_another='unused'):
    """
    Given the trip has a "leg" that arrives at 11Jul2003 16:30
    """        
    _create_activity_on_trip(context, activity=activity, date=date, arr=time)

@given(u'the trip has %(a_another)s "%(activity)s" that departs from "%(stn)s" at %(time)s' % util.matching_patterns)
def create_activity_on_trip_dep_stn_dep(context, activity, stn, time, a_another='unused'):
    """
    Given the trip has a "leg" that departs from "ARN" at 10:00
    """        
    _create_activity_on_trip(context, activity=activity, dep_stn=stn, dep=time)

@given(u'the trip has %(a_another)s "%(activity)s" that arrives at "%(stn)s" at %(time)s' % util.matching_patterns)
def create_activity_on_trip_arr_stn_arr(context, activity, stn, time, a_another='unused'):
    """
    Given the trip has a "leg" that arrives at "ARR" at 16:00
    """        
    _create_activity_on_trip(context, activity=activity, arr_stn=stn, arr=time)

def _create_activity_on_trip(context, activity='', date='', dep='', arr='', dep_stn='', arr_stn=''):
    activity = util.verify_activity(activity)
    date = util.verify_date(date)
    dep = util.verify_time(dep)
    arr = util.verify_time(arr)
    dep_stn = util.verify_stn(dep_stn)
    arr_stn = util.verify_stn(arr_stn)
    context.ctf.create_activity_on_trip(activity=activity, date=date, dep=dep, arr=arr, dep_stn=dep_stn, arr_stn=arr_stn)
    

@given(u'%(a_another)s trip with the following activities' % util.matching_patterns)
def create_trip_from_table(context, a_another='unused', homebase=''):
    """
    Given a trip with the following activities
    | act | num  | dep stn | arr stn | dep   | arr   |
    | leg | 7511 |         | ARR     | 10:25 | 11:35 |
    | leg |      |         |         | 12:25 |       |

Available columns:
Colums prepended with # are not yet implemented.

#        label:            A label to assign to the activity, used to reference it (example: long flight)
        act:              Any one of: leg, dh, oag, ground, transport (example: leg)
        car:              Flight carrier code (example: JA)
        num:              Flight number (example: 7511)
#        suf:              Flight suffix (example: P)
        dep stn:          Departure airport code (example: ORY)
        arr stn:          Arrival airport code (example: ARR)
        dep:              Departure time (example: 01NOV2016 10:25)
        arr:              Arrival time (example: 01NOV2016 12:25)
        ac_typ:           Aircraft type (example: 74H)
#        srv_typ:          Service type (example: C)
        code:             Only applicable for ground duties, ground duty code (example: SBY)
#        duty type:        Type of duty, used mainly for augmentation (example: REL)
#        cockpit employer: The carrier code of the cockpit employer (example: JA)
#        cabin employer:   The carrier code of the cabin employer (example: JA)
#        ac owner:         The carrier code of the aircraft owner (example: JA)
#        user tags:        User tags defined in the system (example: PRE_BOOKED)
#        ac change         Whether the current and the next leg are the same aircraft or not (example: False)
    """

    # Add all needed columns, default value to ''
    for column in activity_columns:
        context.table.ensure_column_exists(column)

    # Verify that all columns can be handled
    for column in context.table.headings:
        assert column in activity_columns, 'Cannot handle column %s, use: %s' % (column, ", ".join(activity_columns))

    # First create an empty trip
    context.ctf.create_trip(homebase=homebase)

    # Then add all activities from table
    for row in context.table:
        activity = util.verify_activity(row['act'])
        carrier = util.verify_carrier(row['car'])
        code = util.verify_carrier(row['code'])
        flight_num = util.verify_int(row['num'])
        dep_stn = util.verify_stn(row['dep stn'])
        arr_stn = util.verify_stn(row['arr stn'])
        date = util.verify_date(row['date'])
        dep = util.verify_time_or_datetime(row['dep'])
        arr = util.verify_time_or_datetime(row['arr'])
        ac_typ = util.verify_ac_type(row['ac_typ'])

        context.ctf.create_activity_on_trip(activity=activity, car=carrier, code=code, num=flight_num, date=date, dep=dep, arr=arr, dep_stn=dep_stn, arr_stn=arr_stn, ac_typ=ac_typ)

@given(u'%(a_another)s trip with homebase "%(stn)s" with the following activities' % util.matching_patterns)
def create_trip_with_homebase_from_table(context, stn, a_another='unused'):
    """
    Given a trip with homebase "GOT" with the following activities
    | act | num  | dep stn | arr stn | dep   | arr   |
    | leg | 7511 |         | ARR     | 10:25 | 11:35 |
    | leg |      |         |         | 12:25 |       |

Available columns:
Colums prepended with # are not yet implemented.

#        label:            A label to assign to the activity, used to reference it (example: long flight)
        act:              Any one of: leg, dh, oag, ground, transport (example: leg)
        car:              Flight carrier code (example: JA)
        num:              Flight number (example: 7511)
#        suf:              Flight suffix (example: P)
        dep stn:          Departure airport code (example: ORY)
        arr stn:          Arrival airport code (example: ARR)
        dep:              Departure time (example: 01NOV2016 10:25)
        arr:              Arrival time (example: 01NOV2016 12:25)
        ac_typ:           Aircraft type (example: 74H)
#        srv_typ:          Service type (example: C)
        code:             Only applicable for ground duties, ground duty code (example: SBY)
#        duty type:        Type of duty, used mainly for augmentation (example: REL)
#        cockpit employer: The carrier code of the cockpit employer (example: JA)
#        cabin employer:   The carrier code of the cabin employer (example: JA)
#        ac owner:         The carrier code of the aircraft owner (example: JA)
#        user tags:        User tags defined in the system (example: PRE_BOOKED)
#        ac change         Whether the current and the next leg are the same aircraft or not (example: False)
    """
    homebase = util.verify_stn(stn)
    create_trip_from_table(context, homebase=homebase)
    

@given(u'crew member %(roster_ix)s with homebase "%(stn)s" has duty time that exceeds %(hour)s hours in month %(month)s in %(year)s' % util.matching_patterns)
def generate_roster_with_duties(context, roster_ix, stn, hour, month, year):
    """
    Given crew member 1 with homebase "OSL" has duty time that exceeds 160 hours in month JAN in 2019
    """
    months = {'JAN' : 31,
              'FEB' : 28,
              'MAR' : 31,
              'APR' : 30,
              'MAY' : 31,
              'JUN' : 30,
              'JUL' : 31,
              'AUG' : 31,
              'SEP' : 30,
              'OCT' : 31,
              'NOV' : 30,
              'DEC' : 31
              }
    
    valid_target_stns = filter(lambda homebase: homebase.upper() != stn, util_custom.homebases)  
    avg_duty_length = 8
    avg_trips = int(hour) / avg_duty_length
    num_trips_to_generate = avg_trips if (int(hour) % avg_duty_length == 0) else avg_trips + 1
    print('Generating {0} trips for crew member {1}'.format(num_trips_to_generate, roster_ix)) # Used to define rule checks in tests
    spread = months[month] / num_trips_to_generate

    # Create multiple trips during month exceeding nr hours defined in 'hour'
    for trip_nr in range(0, num_trips_to_generate):
        context.ctf.create_trip(homebase=stn)
        target_stn = random.choice(valid_target_stns)
        for leg_nr in range(0, 2):
            activity = util.verify_activity('leg')
            carrier = util.verify_carrier('')
            code = util.verify_carrier('')
            flight_num = util.verify_int((trip_nr + 1) * 10 + leg_nr)
            dep_stn = util.verify_stn(stn if leg_nr == 0 else target_stn)
            arr_stn = util.verify_stn(target_stn if leg_nr == 0 else stn)
            date = util.verify_date('{0}{1}{2}'.format(ensure_correct_spread(trip_nr, spread), month, year))
            dep = util.verify_time('10:00' if leg_nr == 0 else '13:30')
            arr = util.verify_time('12:30' if leg_nr == 0 else '17:00')
            ac_typ = util.verify_ac_type('33A')
            context.ctf.create_activity_on_trip(activity=activity, car=carrier, code=code, num=flight_num, date=date, dep=dep, arr=arr, dep_stn=dep_stn, arr_stn=arr_stn, ac_typ=ac_typ)
        trip_ix = util.verify_int(trip_nr + 1)
        roster_ix = util.verify_int(roster_ix)
        context.ctf.assign_trip_to_crew(trip_ix, roster_ix)    
         
def ensure_correct_spread(trip_nr, spread):
    if trip_nr == 0:
        return 1
    elif spread == 1:
        return (spread * trip_nr) + 1
    else:
        return spread * trip_nr
    
#
# Set up crew data
#

@given(u'%(a_another)s crew member' % util.matching_patterns)
def add_crew_member(context, a_another='unused'):
    """
    Given a crew member
    """
    context.ctf.add_crew()
@given(u'%(a_another)s crew member with homebase "%(stn)s"' % util.matching_patterns)
def add_crew_member_homebase(context, stn, a_another='unused'):
    """
    Given another crew member with homebase "GOT"
    """
    homebase = util.verify_stn(stn)
    crew_ix = context.ctf.add_crew()
    context.ctf.set_crew_homebase(crew_ix, homebase)


@given(u'%(a_another)s crew member with' % util.matching_patterns)
def add_crew_member_with_attributes(context, a_another='unused'):
    """
    Given a crew member with
       | attribute       | value     | valid from | valid to  |
       .#### values for crew table ####
       | employee number | 12345     | ---------- | --------- |
       | sex             | F         | ---------- | --------- |
       | main function   | F         | ---------- | --------- |
#       | birthdate     | 01JAN1990 | ---------- | --------- |
#       | name          | Ben Jones | ---------- | --------- |
#       | signature     | bjones    | ---------- | --------- |
#       | seniority     | 1         | ---------- | --------- |
       | contract      | V301      | 01JAN1996  | 31Dec2075 |
       | employment    | --------- | 01JAN1996  | 31Dec2075 |
#       | main function | PU        |            |           |
#       .#### values for  crew_qualifications table ####
#       | aircraft      | B747      | 01JAN1996  | 31Dec2075 |
#       | airport       | CDG       | 01JAN1996  | 31Dec2075 |
#       | language      | A         | 01JAN1996  | 31Dec2075 |
#       | etops         | YES       | 01JAN1996  | 31Dec2075 |
#       | instructor    | AUDIT     | 01JAN1996  | 31Dec2075 |
#       | misc          | SAFETY    | 01JAN1996  | 31Dec2075 |
#       | passport      | DE        | 01JAN1996  | 31Dec2075 |
#       | visa          | US        | 01JAN1996  | 31Dec2075 |
       .#### values for crew_employment table ####
       | base            | ARN       | 01JAN1996  | 31Dec2075 |
       | crew rank       | FC        | 01JAN1996  | 31DEC2075 |
       | title rank      | FC        | 01JAN1996  | 31DEC2075 |
#       | rank          | PU        | 01JAN1996  | 31Dec2075 |
#       | workrate      | PT1       | 01JAN1996  | 31Dec2075 |
#       .#### values for crew_restrictions tables ####
#       .# see definitions.crew_restrictions for available fields, can be e.g.
#       | medical restriction | ------ | 31Aug2016  | 31Dec2016 |
       .#### values for crew_attr table ####
       | published       | 01JUL2018 | 01JAN1996  | 31Dec2075 |
       | region       | SKI | ------  | --------|

    Note:
    * A ---------- means the field is ignored for this attribute. Leave it empty
    * Validfrom/validto are always defaulted if not given.
    
    # the '.' is to not have the row filtered out by steps-catalog
    """

    # Add all needed columns, default value to ''
    for column in CREW_ATTRIBUTE_COLUMNS:
        context.table.ensure_column_exists(column)

    # Verify that all columns can be handled
    for column in context.table.headings:
        assert column in CREW_ATTRIBUTE_COLUMNS, 'Cannot handle column %s, use: %s' % (column, ", ".join(CREW_ATTRIBUTE_COLUMNS))

    # Add all crew attributes from table
    crew_attributes = {}
    crew_attr_attributes = []
    crew_employment_attributes = []
    crew_contract_attributes = []
    attribute_map = {'employee number' : ('crew', 'empno'),
                     'sex' : ('crew', 'sex'),
                     'main function' : ('crew', 'maincat'),
                     'employment' : ('crew', (None, 'employmentdate', 'retirementdate')),
                     'published' : ('crew_attr', 'PUBLISHED'),
                     'base' : ('crew_employment', 'base'),
                     'contract' : ('crew_contract', 'contract'),
                     'crew rank' : ('crew_employment', 'crewrank'),
                     'title rank' : ('crew_employment', 'titlerank'),
                     'region': ('crew_employment', 'region')}
    for row in context.table:
        attribute = util.verify_in_list(row['attribute'], attribute_map.keys(), 'attribute')
        value = row['value']
        valid_from = util.verify_date(row['valid from'])
        valid_to = util.verify_date(row['valid to'])

        table, attribute_name = attribute_map[attribute]
        if table == 'crew':
            if isinstance(attribute_name, tuple):
                if not attribute_name[0] is None:
                    crew_attributes[attribute_name[0]] = value
                crew_attributes[attribute_name[1]] = valid_from
                crew_attributes[attribute_name[2]] = valid_to
            else:
                crew_attributes[attribute_name] = value
        elif table == 'crew_attr':
            (attr_str, attr_int, attr_abs, attr_rel) = util.verify_attr_val(value)
            crew_attr_attributes.append({'attr' : attribute_name,
                                         'value_str' : attr_str,
                                         'value_int' : attr_int,
                                         'value_abs' : attr_abs,
                                         'value_rel' : attr_rel})
        elif table == 'crew_employment':
            crew_employment_attributes = merge_attribute(crew_employment_attributes, attribute_name, value, valid_from, valid_to)
        elif table == 'crew_contract':
            crew_contract_entry = {'contract' : value}
            if valid_from != None:
                crew_contract_entry['validfrom'] = valid_from
            if valid_to != None:
                crew_contract_entry['validto'] = valid_to
            crew_contract_attributes.append(crew_contract_entry)
        else:
            raise Exception("Unhandled attribute '%s'" % attribute)

    crew_ix = context.ctf.add_crew(**crew_attributes)
    for crew_attr_attribute in crew_attr_attributes:
        context.ctf.set_crew_attr(crew_ix, **crew_attr_attribute)
    for crew_employment_attribute in crew_employment_attributes:
        context.ctf.set_crew_employment(crew_ix, **crew_employment_attribute)
    for crew_contract_attribute in crew_contract_attributes:
        context.ctf.set_crew_contract(crew_ix, **crew_contract_attribute)


def merge_attribute(attributes, attribute_name, value, valid_from, valid_to):
    attributes_out = []

    to_merge = [{attribute_name : value,
                 'validfrom': valid_from,
                 'validto' : valid_to}]

    for old_attribute in attributes:
        if len(to_merge) == 0:
            attributes_out.append(old_attribute)
        else:
            to_merge.append(old_attribute)
            while len(to_merge) > 1:
                to_merge = sorted(to_merge, key=attribute_sorter)
                if attribute_valid_from(to_merge[0]) < attribute_valid_from(to_merge[1]):
                    if attribute_valid_to(to_merge[0]) <= attribute_valid_from(to_merge[1]):
                        attributes_out.append(to_merge.pop(0))
                    else:
                        start = to_merge[0].copy()
                        start['validto'] = to_merge[1]['validfrom']
                        attributes_out.append(start)
                        to_merge[0]['validfrom'] = to_merge[1]['validfrom']
                else: # Same validfrom
                    util.verify_attributes(to_merge[0], to_merge[1])
                    if attribute_valid_to(to_merge[0]) < attribute_valid_to(to_merge[1]):
                        start = to_merge[1].copy()
                        to_merge[1]['validfrom'] = to_merge[0]['validto']
                        start.update(to_merge.pop(0))
                    else: # Same validto
                        start = to_merge.pop(0)
                        start.update(to_merge.pop(0))
                    attributes_out.append(start)
    attributes_out = attributes_out + to_merge
    return attributes_out


def attribute_valid_from(attribute):
    if attribute['validfrom'] != None:
        valid_from = AbsTime(attribute['validfrom'])
    else:
        valid_from = AbsTime("1JAN1900")
    return valid_from


def attribute_valid_to(attribute):
    if attribute['validto'] != None:
        valid_to = AbsTime(attribute['validto'])
    else:
        valid_to = AbsTime("31DEC2099")
    return valid_to


def attribute_sorter(attribute):

    return attribute_valid_from(attribute), attribute_valid_to(attribute)


@given(u'trip %(trip_ix)s is assigned to crew member %(roster_ix)s' % util.matching_patterns)
def assign_trip_to_crew(context, trip_ix, roster_ix):
    """
    Given trip 1 is assigned to crew member 1
    """
    trip_ix = util.verify_int(trip_ix)
    roster_ix = util.verify_int(roster_ix)
    context.ctf.assign_trip_to_crew(trip_ix, roster_ix)


@given(u'trip %(trip_ix)s is assigned to crew member %(roster_ix)s in position %(pos)s' % util.matching_patterns)
def assign_trip_to_crew_in_position(context, trip_ix, roster_ix, pos):
    """
    Given trip 1 is assigned to crew member 1 in position 1
    """
    trip_ix = util.verify_int(trip_ix)
    roster_ix = util.verify_int(roster_ix)
    pos = util.verify_pos(pos)
    context.ctf.assign_trip_to_crew(trip_ix, roster_ix, pos)


@given(u'trip %(trip_ix)s is assigned to crew member %(roster_ix)s in position %(pos)s with attribute %(attribute)s=%(attr_val)s' % util.matching_patterns)
def assign_trip_to_crew_in_position_with_attribute(context, trip_ix, roster_ix, pos, attribute, attr_val):
    """
    Given trip 1 is assigned to crew member 1 in position 1 with attribute TRAINING="LIFUS"
    """
    (attr_str, attr_int, attr_abs, attr_rel) = util.verify_attr_val(attr_val)
    trip_ix = util.verify_int(trip_ix)
    roster_ix = util.verify_int(roster_ix)
    pos = util.verify_pos(pos)
    context.ctf.assign_trip_to_crew(trip_ix, roster_ix, pos, [{'name' : attribute,
                                                               'value_rel' : attr_rel,
                                                               'value_abs' : attr_abs,
                                                               'value_int' : attr_int,
                                                               'value_str' : attr_str}])


ASSIGNMENT_COLUMNS = ('leg', 'type', 'name', 'value')
@given(u'trip %(trip_ix)s is assigned to crew member %(roster_ix)s in position %(pos)s with' % util.matching_patterns)
def assign_trip_to_crew_with(context, trip_ix, roster_ix, pos):
    """
    Given trip 1 is assigned to crew member 1 in position AH with
      | type      | leg | name       | value |
      | attribute | 3,7 | MEAL_BREAK | X     |
    """
    trip_ix = util.verify_int(trip_ix)
    roster_ix = util.verify_int(roster_ix)
    pos = util.verify_pos(pos)

        # Add all needed columns, default value to ''
    for column in ASSIGNMENT_COLUMNS:
        context.table.ensure_column_exists(column)

    # Verify that all columns can be handled
    for column in context.table.headings:
        assert column in ASSIGNMENT_COLUMNS, 'Cannot handle column %s, use: %s' % (column, ", ".join(ASSIGNMENT_COLUMNS))

    attributes = []
    # Add all activities from table
    for row in context.table:
        legs = util.verify_int_list(row['leg'])
        typ = util.verify_str(row['type'])
        assert typ in ['attribute'], 'Type must be attribute, not "%s"' % typ
        name = util.verify_str(row['name'])
        (attr_str, attr_int, attr_abs, attr_rel) = util.verify_attr_val(row['value'])
        attributes.append({'legs' : legs,
                           'name' : name,
                           'value_rel' : attr_rel,
                           'value_abs' : attr_abs,
                           'value_int' : attr_int,
                           'value_str' : attr_str})
    context.ctf.assign_trip_to_crew(trip_ix, roster_ix, pos, attributes)


@given(u'planning period from %(date)s to %(date2)s' % util.matching_patterns)
def new_planning_period(context, date, date2):
    """
    Given planning period from 1JAN2018 to 31JAN2018
    """
    context.ctf.set_planning_period(AbsTime(str(date)), AbsTime(str(date2)))


use_step_matcher('parse')

@given(u'following trips have the complement {complement}')
def set_trip_complement(context, complement):
    """
    Given following trips have the complement 1/1/0//0/0/0/0//0
    """
    complement = util.verify_complement(complement)
    context.ctf.set_trip_complement(complement)

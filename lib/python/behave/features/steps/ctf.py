import os

from subprocess import call
from tempfile import NamedTemporaryFile

import Cui
from AbsTime import AbsTime
from RelTime import RelTime
import BSIRAP
#TODO: remove OTS dependancy
from carmusr.planning import set_planning_period
from Variable import Variable

import util
import util_custom as custom
import carmensystems.rave.api as rave

ACTIVITY_DATE = AbsTime(custom.activity_date_str)

def offset_time(time, offset=0):
    """
    (20030706) 08:00, -1 -> (20030706 07:00
    """
    if type(offset) == int:
        offset = '%d:00' % offset
    return time + RelTime(offset)

def make_reltime(time):
    ret = None
    if not time:
        return ret
    elif type(time) == BSIRAP.RelTime:
        return time
    elif type(time) == BSIRAP.AbsTime:
        return time.time_of_day()
    elif type(time) == str:
        try:
            ret = RelTime(time)
        except:
            assert False, 'Cannot handle time: %s use hh:mm' % time
        return ret
    else:
        assert False, 'Cannot handle unknown type of time: %s(%s)' % (time, type(time))

def make_abstime(date, time):
    ret_date = date and AbsTime(date) or ACTIVITY_DATE
    if not time:
        return ret_date
    elif type(time) == str:
        try:
            # If the the string can be decoded as an absolute time: use it!
            return AbsTime(time)
        except:
            pass

        time_len = len(time)
        if time_len == 14 or time_len == 8:
            if date:
                assert False, 'Cannot work with both date and time: %s/%s' \
                    % (date, time)
            else:
                return AbsTime(time)
        elif time_len == 5 or time_len == 4:
            return ret_date + RelTime(time)
        else:
            assert False, 'Cannot handle (string) time %s' % time
    elif type(time) == BSIRAP.RelTime:
        return ret_date + time
    elif type(time) == BSIRAP.AbsTime:
        return time
    else:
        assert False, 'Cannot handle date %s(%s) and time %s(%s)' \
            % (date, type(date), time, type(time))

def make_dep(last_arr=None, date=None, dep=None, arr=None):
    """
    Create a departure time, returns a AbsTime
    """
    one_hour = RelTime('1:00')
    date_abs = date and make_abstime(date, None) or ''
    last_arr_date = last_arr.day_floor()

    ret_date = ''
    ret_dep = ''

    ### WIP: handle all combinations of input....

    if date:
        if dep:
            ret_dep = make_abstime(date, dep)
        elif arr:
            ret_dep = make_abstime(date, arr) - one_hour
        ret_date = date
    elif last_arr:
        if dep:
            ret_dep = make_abstime(last_arr_date, dep)
        elif arr:
            print('### arr: %s' % arr)
            print('### last_arr_date: %s' % last_arr_date)
            ret_dep = make_abstime(last_arr_date, arr) - one_hour
            print('### make ret_dep: %s' % ret_dep)
        else:
            ret_dep = last_arr + one_hour

    if last_arr and ret_dep:
        assert last_arr < ret_dep, 'Too early departure %s (%s)' % (ret_dep, last_arr)

    return (ret_date, ret_dep)

def ctf_yyyymmdd(time):
    return time.yyyymmdd()[:8]

def ctf_hhmm(time):
    return str(time)[-5:-3] + str(time)[-2:]


def create_new_activity(last_activity=None, activity='leg', car='', code='', num='', date='', dep='', arr='', dep_stn='', arr_stn='', ac_typ='', cockpit_employer='', cabin_employer='', ac_owner='', trip_num=0, num_activities=0):
    if last_activity:
        last_flno, last_arr, last_arr_stn = last_activity.get_activity_info()
        flno = num and int(num) or last_flno+1
        (date, dep) = make_dep(last_arr, date, dep, arr)

        if dep_stn:
            assert dep_stn == last_arr_stn, 'Implausible cxn %s-%s' % (last_arr_stn, dep_stn)
        else:
            dep_stn = last_arr_stn
        the_activity = Activity(activity=activity, car=car, code=code, flno=flno, date=date, dep=dep, arr=arr, dep_stn=dep_stn, arr_stn=arr_stn, ac_typ=ac_typ, cockpit_employer=cockpit_employer, cabin_employer=cabin_employer, ac_owner=ac_owner, num_activities=num_activities)
    else:
        flno = num and int(num) or ''
        the_activity = Activity(activity=activity, car=car, code=code, flno=flno, date=date, dep=dep, arr=arr, dep_stn=dep_stn, arr_stn=arr_stn, ac_typ=ac_typ, cockpit_employer=cockpit_employer, cabin_employer=cabin_employer, ac_owner=ac_owner, trip_num=trip_num, num_activities=num_activities)
    return the_activity


def create_new_personal_activity(personal_activity, start_date='', start_time='', end_date='', end_time='', stn=''):
    the_personal_activity = PersonalActivity(code=personal_activity, station=stn, startDate=start_date, startTime=start_time, endDate=end_date, endTime=end_time, onDutyCode="N")
    return the_personal_activity


class CTF(object):
    def __init__(self, directory=None, prefix='ctf_', lp='', sp='', display=False):
        self.plan = NamedTemporaryFile(dir=directory, prefix=prefix, delete=False)
        self.localplan = lp
        self.subplan = sp
        self.is_dated = True
        self.activities = []
        self.trips = []
        self.crew = {}
        self.sp_etables = {}
        self.has_onward_flights = False
        self.set_planning_period(AbsTime(custom.pp_start_str), AbsTime(custom.pp_end_str))
        self.complement = '1/1/0/0/1/0/2/0/0/0'

    def set_planning_period(self, pp_start, pp_end):
        self.pp_start = pp_start
        self.pp_end = pp_end
        global ACTIVITY_DATE
        ACTIVITY_DATE = self.pp_start + RelTime(24, 0) * 5


    def set_trip_complement(self, complement):
        self.complement = complement


    # Personal activity methods
    def create_personal_activity(self, crew_ix, personal_activity, start_date='', start_time='', end_date='', end_time='', stn=''):
        if start_date:
            # Create full start/end including date
            start = make_abstime(start_date, start_time)
            end = end_date and make_abstime(end_date, end_time) or offset_time(start, 1)
        elif end:
            # Create full start/end including date
            end = make_abstime(end_date, end_time)
            start = offset_time(end, -1)

        the_personal_activity = create_new_personal_activity(personal_activity=personal_activity, start_date=ctf_yyyymmdd(start), start_time=ctf_hhmm(start), end_date=ctf_yyyymmdd(end), end_time=ctf_hhmm(end), stn=stn)
        crew_id = self.make_crew_id(crew_ix)
        self.crew[crew_id].assign_personal_activity(the_personal_activity)


    # Leg methods
    def num_activities(self):
        return len(self.activities)
    def get_last_activity(self):
        return self.activities and self.activities[-1] or None

    def create_activity(self, activity='leg', car='', code='', num='', date='', dep='', arr='', dep_stn='', arr_stn='', ac_typ='', cockpit_employer='', cabin_employer='', ac_owner=''):
        if dep:
            # Create full dep/arr including date
            dep = make_abstime(date, dep)
            arr = arr and make_abstime(date, arr) or offset_time(dep, 1)
            date = ''
        elif arr:
            # Create full arr/dep including date
            arr = make_abstime(date, arr)
            dep = offset_time(arr, -1)
            date = ''

        the_activity = create_new_activity(activity=activity, car=car, code=code, num=num, date=date, dep=dep, arr=arr, dep_stn=dep_stn, arr_stn=arr_stn, ac_typ=ac_typ, cockpit_employer=cockpit_employer, cabin_employer=cabin_employer, ac_owner=ac_owner, num_activities=self.num_activities())
        self.add_activity(the_activity)
        return

    def add_activity(self, the_activity):
        self.activities.append(the_activity) # TODO: make sure not duplicate
        planning_start = str(self.pp_start)[2:-5].strip()
        activity_date = the_activity.get_date()[2:].strip()
        if (planning_start != activity_date):
            self.add_to_accumulators(the_activity, self.crew)

    def connect_onward_flight_ref(self, leg_ix_1, leg_ix_2):
        self.has_onward_flights = True
        leg_1 = self.activities[leg_ix_1-1]
        leg_2 = self.activities[leg_ix_2-1]
        leg_1.connect_onward_flight_ref(leg_2)

    # Trip methods
    def num_trips(self):
        return len(self.trips)
    def get_last_trip(self):
        if self.trips:
            return self.trips[-1]
        return None
    def create_trip(self, homebase=None, name=None, the_activity=None):
        num = self.num_trips()+1
        homebase = homebase or custom.trip_homebase
        name = name or self.make_trip_name(num)
        activities_in_trip = []
        if the_activity:
            activities_in_trip.append(the_activity)
        self.trips.append(Trip(num, name, homebase, activities_in_trip, self.complement))

    def make_trip_name(self, num):
        return '%s%03d' % (custom.trip_name, num)

    def create_activity_on_trip(self, activity='leg', car='', code='', num='', date='', dep='', arr='', dep_stn='', arr_stn='', ac_typ='', cockpit_employer='', cabin_employer='', ac_owner=''):
        the_activity = self.get_last_trip().add_activity(activity=activity,
                                                         car=car, code=code, num=num,
                                                         date=date, dep=dep, arr=arr,
                                                         dep_stn=dep_stn, arr_stn=arr_stn, ac_typ=ac_typ,
                                                         cockpit_employer=cockpit_employer,
                                                         cabin_employer=cabin_employer,
                                                         ac_owner=ac_owner)
        self.add_activity(the_activity)

    # Crew methods
    def make_crew_id(self, crew_ix):
        crew_id = '%s%03d' % (custom.crew_id, crew_ix)
        return crew_id

    def add_crew(self, empno=None, sex='F', maincat='F', employmentdate="01JAN1901", retirementdate=None):
        crew_ix = len(self.crew)+1
        crew_id = self.make_crew_id(crew_ix)
        self.crew[crew_id] = Crew(crew_id)

        row_dict = {"id": crew_id,
                    "empno": util.default(empno, crew_id),
                    "sex": sex,
                    "birthday": "24DEC1977",
                    "title": None,
                    "name": "%s %s" % (crew_id, crew_id),
                    "forenames": crew_id,
                    "logname": "TestUser",
                    "si": None,
                    "maincat": maincat,
                    "bcity": "Ankeborg",
                    "bstate": None,
                    "bcountry": "SE",
                    "alias": None,
                    "employmentdate": employmentdate,
                    "retirementdate": retirementdate}
        self.add_row_dict("crew", row_dict) #defined in ctf_custom

        return crew_ix

    def assign_trip_to_crew(self, trip_ix, crew_ix, position='1/0', attributes=[]):
        crew_id = self.make_crew_id(crew_ix)
        the_trip = self.trips[trip_ix-1]
        self.crew[crew_id].assign_trip(the_trip, position)
        leg_nr = 1
        for activity in the_trip.activities:
            udor = str(activity.departure.day_floor())
            uuid = '%s %s' % (activity.code, activity.dep_stn)
            fd = '%s %06d ' % (activity.car, activity.flight_num)
            dep_stn = '%s' % activity.dep_stn
            si = None
            for attribute in attributes:
                # Skip legs not the the 'legs' attribute.
                # If the 'legs' attribute does not exist, skip no legs
                if 'legs' in attribute:
                    if not leg_nr in attribute['legs']:
                        continue
                row_dict = {"attr": attribute['name'],
                            "value_rel": attribute.get('value_rel', None),
                            "value_abs": attribute.get('value_abs', None),
                            "value_int": attribute.get('value_int', None),
                            "value_str": attribute.get('value_str', None),
                            "si": si}
                if activity.is_ground_duty():
                    row_dict.update({"cgd_task_udor": udor,
                                     "cgd_task_id": uuid,
                                     "cgd_crew": crew_id})
                    self.add_row_dict("crew_ground_duty_attr", row_dict)  #defined in ctf_custom
                else:
                    row_dict.update({"cfd_leg_udor": udor,
                                     "cfd_leg_fd": fd,
                                     "cfd_leg_adep": dep_stn,
                                     "cfd_crew": crew_id})
                    self.add_row_dict("crew_flight_duty_attr", row_dict)  #defined in ctf_custom
            leg_nr = leg_nr + 1

    def init_sp_table(self, table_name):
        if not self.sp_etables.has_key(table_name):
            self.sp_etables[table_name] = Etable(table_name)
        return self.sp_etables[table_name]

    # Turn this CTF object into an rrl-file (plan)
    def create_and_load_plan(self, application):

        ctf_lines = self.get_ctf_lines()

        if ctf_lines:
            self.plan.writelines([ctf_line.encode("iso-8859-1") for ctf_line in ctf_lines])
            self.plan.flush()

            self.create_rrl(self.localplan, self.subplan)
            self.copy_baseline_etables(self.localplan, self.subplan)

            if application in ('Pairing_CC', ''):
                rule_set = custom.rule_set_pairing_cc
            elif application == 'Pairing_FC':
                rule_set = custom.rule_set_pairing_fc
            elif application == 'Rostering_CC':
                rule_set = custom.rule_set_rostering_cc
            elif application == 'Rostering_FC':
                rule_set = custom.rule_set_rostering_fc
            elif application == 'Tracking':
                rule_set = custom.rule_set_tracking
            else:
                assert False, 'Cannot handle application: %s' % application

            Cui.CuiOpenSubPlan(Cui.gpc_info, self.localplan, self.subplan, Cui.CUI_SILENT)
            Cui.CuiCrcLoadRuleset(Cui.gpc_info, rule_set)
            if application != "Tracking":
                try:
                    set_planning_period(self.pp_start,
                                        self.pp_end)
                except:
                    print("WARNING: Could not set planning period with parameter")
                    
            self.build_rotations()
        else:
            # No ctf data needed for this test
            pass


    def get_ctf_lines(self):
        ctf_lines = []
        ctf_lines += self.get_header()
        ctf_lines += self.get_etables()
        ctf_activities = self.get_activities()
        ctf_trips = self.get_trips()
        ctf_crew = self.get_crew()
        if not (ctf_activities or ctf_trips or ctf_crew):
            return [] # without data there is no proper CTF, no data/plan needed for test
        ctf_lines += ctf_activities
        ctf_lines += ctf_trips
        ctf_lines += ctf_crew

        #print('ctf_lines: ', ctf_lines)
        return ctf_lines

    def create_rrl(self, localplan, subplan):
        exit_code = call([
                "Ctf2Rrl",
                "-i" + self.plan.name,
                "-t" + localplan,
                "-o" + subplan,
                "-c" + "crew_info.etab",
                ])
        if exit_code != 0:
            assert False, 'Error with Ctf2Rrl: %s' % self.plan.name

    def copy_baseline_etables(self, localplan, subplan):
        current_lp_etable = os.path.expandvars('$CARMDATA/LOCAL_PLAN/%s/etable' % localplan)
        current_sp_etable = os.path.expandvars('$CARMDATA/LOCAL_PLAN/%s/etable' % subplan)
        baseline_lp_etable = os.path.expandvars('$CARMDATA/LOCAL_PLAN/Jeppesen/Baseline/Baseline/etable')
        baseline_sp_etable = os.path.expandvars('$CARMDATA/LOCAL_PLAN/Jeppesen/Baseline/Baseline/Baseline_JCP/etable')

        util.copy_dirs(baseline_lp_etable, current_lp_etable)
        util.copy_dirs(baseline_sp_etable, current_sp_etable)


    def get_header(self):
        ret = ['PERIOD: %s - %s\n' % (ctf_yyyymmdd(self.pp_start), ctf_yyyymmdd(self.pp_end))]
        ret.append('PLAN TYPE: %s\n\n' % (self.is_dated and 'DATED' or 'STANDARD'))
        ret.append('TIME MODE: UTC\n\n')
        return ret

    def get_etables(self):
        ret = []
        if self.sp_etables:
            ret.append('SP ETAB:\n')
            for etab in self.sp_etables.values():
                ret += etab.get_ctf_lines()
                ret.append('EOTABLE\n\n')
            ret.append('EOETAB\n\n')
        return ret

    def get_activities(self):
        ret = []
        if self.activities:
            ret.append('SECTION: LEG\n')
            custom_keys = [] # FIXME: assign somewhere
            if len(custom_keys) > 0:
                ret.append("CUSTOM HEADER: " + ' '.join(['"%s"' % key for key in custom_keys]) + "\n")
            for activity in self.activities:
                if not activity.is_ground_duty():
                    ret.append(activity.get_ctf_line(custom_keys=custom_keys))
            ret.append('EOSECTION\n\n')
            ret.append('SECTION: GROUND DUTY\n')
            for activity in self.activities:
                if activity.is_ground_duty():
                    ret.append(activity.get_ctf_line())
            ret.append('EOSECTION\n\n')
        return ret

    def get_trips(self):
        ret = []
        if self.trips:
            ret.append('SECTION: PAIRING\n')
            for trip in self.trips:
                ret += trip.get_ctf_lines()
            ret.append('EOSECTION\n\n')
        return ret

    def get_crew(self):
        ret = []
        if self.crew:
            ret.append('SECTION: CREW\n')
            for key in sorted(self.crew):
                ret += self.crew[key].get_ctf_lines()
            ret.append('EOSECTION\n\n')
        return ret
     
    # If there is ownward cxn info, build rotations
    def build_rotations(self):
        if self.has_onward_flights:
            # Make sure the proper rule set is loaded
            Cui.CuiCrcLoadRuleset(Cui.gpc_info, custom.rule_set_rotations)
            build_ac_rotations()

class Activity(object):

    def __init__(self, activity='leg', car='', code='', flno=0, date='', dep='', arr='', dep_stn='', arr_stn='', ac_typ='', cockpit_employer='', cabin_employer='', ac_owner='', trip_num=0, num_activities=0):
        # Values may be decoded if the come diectly from Gherkin step
        self.activity=activity
        self.set_car(car)
        self.set_code(code)
        self.set_flight_num(flno, trip_num, num_activities)
        self.set_departure_arrival(date, dep, arr, num_activities)
        self.set_dep_arr_stn(activity, dep_stn, arr_stn, num_activities)
        self.set_ac_typ(ac_typ)
        self.set_date(date)
        self.set_employer(cockpit_employer, cabin_employer, ac_owner)

        self.activity_num = 1
        self.freq = '1234567'
        self.activity_type = 'F'      # F, G, O, T
        # activity_sub_code, only intersting if assigned to trip # L, D, E, *
        if self.activity == 'leg':
            self.activity_sub_code = 'L'  
        elif self.activity == 'dh':
            self.activity_sub_code = 'D'
        else:
            # E is for extra seat
            self.activity_sub_code = '*'

        self.activity_suffix = '*'    # Flight suffix for flights,activity suffix for ground duties
        self.lock = '*'               # N, F, L, X, * ... actually per segment in trip

        self.onw_flight_ref = None
        self.custom_attributes = { } # FIXME: Assign somewhere

    def set_car(self, car):
        self.car = car and car.encode() or custom.activity_carrier

    def set_code(self, code):
        self.code = code and code.encode() or ''

    def set_flight_num(self, flight_num, trip_num, num_activities):
        self.flight_num = flight_num or custom.activity_flight_num + trip_num + num_activities

    def set_ac_typ(self, ac_typ):
        self.ac_typ = ac_typ or '737'

    def set_departure_arrival(self, date, dep, arr, num_activities):
        if dep:
            this_dep = make_abstime(date, dep)
            if arr:
                this_arr = make_abstime(date, arr)
            else:
                this_arr = offset_time(this_dep, 1)
        else:
            if arr:
                this_arr = make_abstime(date, arr)
                this_dep = offset_time(this_arr, -1)
            else:
                this_dep = self.get_new_dep_arr(date=date, num_activities=num_activities)
                this_arr = offset_time(this_dep, 1)

        self.departure = this_dep
        self.arrival = this_arr

    def set_dep_arr_stn(self, activity, dep_stn, arr_stn, num_activities):
        self.dep_stn = dep_stn and dep_stn.encode() \
            or self.new_dep_stn(num_activities=num_activities)
        self.arr_stn = arr_stn and arr_stn.encode() \
            or self.new_arr_stn(num_activities=num_activities)

        if activity == 'ground':
            assert self.dep_stn == self.arr_stn, 'Implausible ground duty, non equal stn names: %s %s' % (self.dep_stn, self.arr_stn)
        else:
            assert not self.dep_stn == self.arr_stn, 'Implausible leg, equal stn names: %s %s' % (self.dep_stn, self.arr_stn)

    def set_date(self, date):
        if date:
            self.date = date
        else:
            self.date = str(self.arrival)[:-5]

    def set_employer(self, cockpit_employer, cabin_employer, ac_owner):
        self.cockpit_employer = cockpit_employer or self.car
        self.cabin_employer = cabin_employer or self.car
        self.ac_owner = ac_owner or self.car

    def get_activity_info(self):
        return(self.flight_num, self.arrival, self.arr_stn)

    def get_new_date(self, date=None):
        """
        20030706
        """
        if date:
            return make_abstime(date, None)
        return ACTIVITY_DATE

    def get_date(self):
        return self.date
            
    def get_new_dep_arr(self, date=None, time=None, offset=0, num_activities=0, dep=True):
        """ 
        20030706 06:00
        """
        ret_date = self.get_new_date(date=date)
        if not time:
            if dep:
                time = 6 + 2*num_activities
            else:
                time = 7 + 2*num_activities
            ret = ret_date + RelTime('%02d:00' % time)
        elif len(time)==5:
            ret = ret_date + offset_time(RelTime(time), offset)
        elif len(time)==14:
            ret = offset_time(AbsTime(time), offset)
        else:
            assert False, 'Cannot handle new dep/arr: %s' % time
        return ret


    def new_dep_stn(self, dep_stn=None, num_activities=0):
        """
        GOT
        """
        if not dep_stn:
            return (custom.activity_stn1, custom.activity_stn2)[num_activities % 2]
        return dep_stn

    def new_arr_stn(self, arr_stn=None, num_activities=0):
        """
        ARN
        """
        if not arr_stn:
            return (custom.activity_stn2, custom.activity_stn1)[num_activities % 2]
        return arr_stn

    def connect_onward_flight_ref(self, leg_2):
        self.onw_flight_ref = leg_2

    def is_ground_duty(self):
        return self.activity == 'ground'

    def get_ctf_line(self, custom_keys=[]):
        """
        Leg:
        JA 4711 * 1 GOT CDG 0800 1000 0 12345 20030706 20030805 737 [JA 4712 * 1] /SKN/SKN/SK
        Ground duty:
        AB12 * MAD 0800 0100 12345 20030706 20030805 * *
        """
        if self.activity == 'ground':
            dep_date = ctf_yyyymmdd(self.departure)
            dep = ctf_hhmm(self.departure)
            arr_date = ctf_yyyymmdd(self.arrival)
            duration = ctf_hhmm(self.arrival)
            ret = '%s * %s %s %s %s %s %s * *\n' % \
                  (self.code,
                   self.dep_stn,
                   dep,
                   duration,
                   self.freq,
                   dep_date,
                   arr_date,
                  )
        else:
            dep_date = ctf_yyyymmdd(self.departure)
            dep = ctf_hhmm(self.departure)
            arr_date = ctf_yyyymmdd(self.arrival)
            arr = ctf_hhmm(self.arrival)
            day_diff = int((self.arrival.day_floor() - self.departure.day_floor()) / RelTime(24, 0))

            ret = '%s %s * 1 %s %s %s %s %s %s %s %s %s %s /%s/%s/%s\n' % \
                  (self.car, self.flight_num,
                   self.dep_stn, self.arr_stn, dep, arr, day_diff,
                   self.freq, dep_date, arr_date,
                   self.ac_typ,
                   self.get_ctf_onward_flight(),
                   self.cockpit_employer, self.cabin_employer, self.ac_owner,
                  )
            if len(custom_keys) > 0:
                custom_attributes = ['"%s"' % self.custom_attributes.get(key, '') for key in custom_keys]
                custom_attributes_str = 'CUSTOM: ' + ' '.join(custom_attributes) + '\n'
                ret = ret + custom_attributes_str

        return ret

    def get_ctf_onward_flight(self):
        ret = ''
        if self.onw_flight_ref:
            ret = self.onw_flight_ref.get_ctf_onward_info()
        return ret

    def get_ctf_onward_info(self):
        return '%s %s %s %s' % (self.car, self.flight_num, self.activity_suffix, self.activity_num)

    def get_ctf_line_trip(self):
        """
        Leg:
        F L * 20030707 GOT 0800 JA 4711 * 1 1000 CDG 20030707
        Ground duty:
        G * * 20030707 GOT 0800 OL1 * * 1 0400 GOT 20030707
        """
        dep_date = ctf_yyyymmdd(self.departure)
        dep = ctf_hhmm(self.departure)
        arr_date = ctf_yyyymmdd(self.arrival)
        arr = ctf_hhmm(self.arrival)

        if self.activity == 'ground':
            ret = 'G * %s %s %s %s %s * * %s %s %s %s\n' % \
                  (self.lock,
                   dep_date, self.dep_stn, dep, self.code,
                   self.activity_num,
                   arr, self.arr_stn, arr_date)
        else:
            ret = '%s %s %s  %s %s %s %s %s  %s %s  %s %s %s\n' % \
                  (self.activity_type, self.activity_sub_code, self.lock,
                   dep_date, self.dep_stn, dep, self.car, self.flight_num,
                   self.activity_suffix, self.activity_num,
                   arr, self.arr_stn, arr_date)
        return ret


class PersonalActivity:
    nextFlightNumber = 1

    def __init__(self, code, station, startDate, startTime, endDate, endTime, environmentCode="0", onDutyCode="F", subCode="*", lock="L"):
        self.code = code
        self.station = station
        self.startDate = startDate
        self.startTime = startTime
        self.endDate = endDate
        self.endTime = endTime
        self.environmentCode = environmentCode
        self.onDutyCode = onDutyCode
        self.subCode = subCode
        self.lock = lock

    def __str__(self):
        l = [ self.lock,
              self.onDutyCode,
              self.environmentCode,
              self.startDate,
              self.station,
              self.startTime,
              self.code,
              "*",
              self.subCode,
              self.endTime,
              self.station,
              self.endDate]
        return ' '.join(l)


class Trip(object):
    def __init__(self, num, name, homebase=None, activities_in_trip=None, complement=None):
        self.num = 1000 + num*100
        self.homebase = homebase or custom.trip_homebase
        self.name = name
        self.on_duty = 'N' # F for off-duty
        self.is_env = '0' # 1 if environment
        self.comp = complement
        self.activities = activities_in_trip

    def get_num_activities(self):
        return len(self.activities)

    def add_activity(self, the_activity=None, activity='', car='', code='', num='', date='', dep='', arr='', dep_stn='', arr_stn='', ac_typ='', cockpit_employer='', cabin_employer='', ac_owner=''):
        if not the_activity:
            last_activity = self.activities and self.activities[-1] or None
            the_activity = create_new_activity(last_activity=last_activity,
                                               activity=activity, car=car, code=code, num=num,
                                               date=date, dep=dep, arr=arr,
                                               dep_stn=dep_stn, arr_stn=arr_stn,
                                               ac_typ=ac_typ,
                                               cockpit_employer=cockpit_employer,
                                               cabin_employer=cabin_employer,
                                               ac_owner=ac_owner,
                                               trip_num=self.num,
                                               num_activities=self.get_num_activities())

        self.activities.append(the_activity)
        return the_activity

    def get_last_activity_info(self):
        assert self.activities, 'get_last_activity_info was called on empty activities list'
        return selfactivities[-1].get_activity_info()

    def get_ctf_lines(self):
        """
        PAIRING: 2 1001 "PairingName" 1/1 GOT
        F L * 20030707 GOT 0800 JA 4711 * 1 1000 CDG 20030707
        F L * 20030707 CDG 1200 JA 4712 * 1 1400 GOT 20030707
        EOPAIRING
        """
        ret = ['PAIRING: %d %d "%s" %s %s\n' % (len(self.activities), self.num, self.name, self.comp, self.homebase)]
        for activity in self.activities:
            ret.append(activity.get_ctf_line_trip())

        ret.append('EOPAIRING\n\n')
        return ret

    def get_ctf_lines_crew(self, pos):
        """
        1001 * 0 1/0
        """
        ret = '%d * %s %s\n' % (self.num, self.is_env, pos)
        return ret


class Crew(object):
    def __init__(self, crew_id, homebase=None):
        self.crew_id = crew_id
        self.homebase = homebase or custom.crew_homebase
        self.assignments = [] # (trip, pos)
        self.personal_activities = []
        #rave.set_crew_homebase(self.crew_id, self.homebase)
        
    def assign_trip(self, the_trip, position='1/0'):
        self.assignments.append((the_trip, position))

    def assign_personal_activity(self, personal_activity):
        self.personal_activities.append(personal_activity)
        
    def get_ctf_lines(self):
        """
        CREW: 2 "Crew1"
        1001 * 0 1/0
        EOCREW
        """

        ret = ['CREW: %d "%s"\n' % (len(self.assignments) + len(self.personal_activities), self.crew_id)]
        for activity in self.personal_activities:
            ret.append("%s\n" % activity)
        for (trip, pos) in self.assignments:
            ret.append(trip.get_ctf_lines_crew(pos))
        ret.append('EOCREW\n\n')
        return ret


class Etable(object):
    suffix = '.etab'

    def __init__(self, etab_name=''):
        etab_name = etab_name or 'dummy'
        if len(etab_name)>5 and etab_name[-5:] == self.suffix:
                self.etab_name = etab_name
        else:
            self.etab_name = etab_name + self.suffix

        self.header = etab_name and self.get_header(etab_name) or ''
        self.lines = []
        return etab_name

    def get_header(self, etab_name):
        if etab_name == 'dummy':
            return
        else:
            assert False, 'Etab name %s should be handled by EtableCustom class' % etab_name

    def add_line(self, line):
        self.lines.append(line)

    def get_ctf_lines(self):
        ret = '%s\n' % self.etab_name
        ret += self.header
        for line in self.lines:
            if isinstance(line, list):
                ret += ', '.join([str(part) for part in line]) + ';\n'
            else:
                ret += '%s\n' % line
        return ret


# Helper for building lines in an etable file
def etab_str(value):
    if value == None:
        return 'VOID'
    elif isinstance(value, str):
        return '"%s"' % value
    elif isinstance(value, bool):
        return str(value).upper()
    else:
        return str(value)


# Simple version ot OTS:ac_rotations.build_ac_rotations()
def build_ac_rotations():
    ROTATION_RULES_MODULE = 'ac_rotation_rules'
    rule_settings = dict()
    for rule in rave.rules():
        rule_settings[rule.name()] = rule.on()

    # Turning off all rules not in ac_rotation_rules
    for rule in rave.rules():
        if not rule.name().startswith(ROTATION_RULES_MODULE + '.'):
            rule.setswitch(False)

    try:
        Cui.CuiBuildAcRotations(Cui.gpc_info, 0)
    finally:
       for rule in rave.rules():
        if rule.name() in rule_settings:
            rule.setswitch(rule_settings[rule.name()])


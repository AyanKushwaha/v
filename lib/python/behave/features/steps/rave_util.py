import os

from behave import *
import util_custom as custom
import Cui
import carmensystems.rave.api as rave
import carmensystems.studio.cpmbuffer as cpmb
import carmensystems.studio.cuibuffer as cuib
import BSIRAP
from RelTime import RelTime
from AbsTime import AbsTime


import util_custom as custom
import util

use_step_matcher('re')

RAVE_VALUE_COLUMNS = ('leg', 'trip', 'roster', 'value')
RAVE_LEGALITY_COLUMNS = ('leg', 'trip', 'roster', 'value')

from enum import Enum
class EVAL_TYPE(Enum):
    Rule = 1
    Rave = 2
    Constraint = 3

iterators_trip, trip_set = custom.map_trip_set_iterator.split('.')

#@when(u'I load (rule set|ruleset) "%(my_rule_set)s"' % util.matching_patterns)
@when(u'I load (rule set|ruleset) "%(rule_set)s"' % util.matching_patterns)
def load_rule_set(context, unused_rule_set, rule_set):
    """
    When I load rule set "rule_set_jcp"
    """
    rule_set = rule_set.encode()
    if rule_set == 'rule_set_jcp':
        rule_set = custom.rule_set_pairing_cc
    elif rule_set == 'rule_set_jcr':
        rule_set = custom.rule_set_rostering_cc
    elif rule_set == 'rule_set_jcr_fc':
        rule_set = custom.rule_set_rostering_fc
    elif rule_set == 'rule_set_jct':
        rule_set = custom.rule_set_tracking
    Cui.CuiCrcLoadRuleset(Cui.gpc_info, rule_set)

@when(u'I set parameter "%(rave_name)s" to "%(rave_value)s"' % util.matching_patterns)
def set_rule_parameter(context, rave_name, rave_value):
    """
    When I set parameter "trip_rules_exp.%min_connection_time_when_on_duty_p%" to "0:45"
    """
    param_name = util.verify_rave_name(rave_name)
    param_value = util.verify_rave_value(rave_value)
    rule_param = rave.param(param_name)
    rule_param_data_type = get_rule_data_type(rule_param)
    param_value_dt = set_rule_data_type(param_value, rule_param_data_type)
    rule_param.setvalue(param_value_dt)

def get_rule_data_type(rule_param):
    return type(rule_param.value())

def set_rule_data_type(param_value, data_type):
    if data_type == BSIRAP.RelTime:
        return RelTime(param_value)
    elif data_type == BSIRAP.AbsTime:
        return AbsTime(param_value)
    elif param_value == "TRUE":
        return True
    elif param_value == "FALSE":
        return False
    elif data_type == int:
        return int(param_value)
    elif data_type == rave.enumval:
        # Enum values are local to their rave module, and should go by the form "planning_area.ANY_QUAL" 
        # where ANY_QUAL is the enum value and planning_area is the module name. The enum name itself is not needed.
        return rave.enumval(param_value)
    assert False, 'Cannot handle data type %s' % data_type

#
# eval rave variables
#

@then(u'rave "%(rave_name)s" shall be "%(rave_value)s"' % util.matching_patterns)
def eval_rave_on_default(context, rave_name, rave_value):
    """
    Then rave "leg.%start_utc%" shall be "06JUL2003 09:00"
    """
    _eval_rave_on_leg_trip_roster(rave_name, rave_value, 1, 1, 0)

@then(u'rave "%(rave_name)s" shall be "%(rave_value)s" on leg %(leg_ix)s' % util.matching_patterns)
def eval_rave_on_leg(context, rave_name, rave_value, leg_ix):
    """
    Then rave "leg.%start_utc%" shall be "06JUL2003 10:46" on leg 2
    """
    _eval_rave_on_leg_trip_roster(rave_name, rave_value, leg_ix, 1, 0)

@then(u'rave "%(rave_name)s" shall be "%(rave_value)s" on leg %(leg_ix)s on trip %(trip_ix)s' % util.matching_patterns)
def eval_rave_on_leg_on_trip(context, rave_name, rave_value, leg_ix, trip_ix):
    """
    Then rave "leg.%start_utc%" shall be "06JUL2003 11:47" on leg 2 on trip 2
    """
    _eval_rave_on_leg_trip_roster(rave_name, rave_value, leg_ix, trip_ix, 0)

@then(u'rave "%(rave_name)s" shall be "%(rave_value)s" on %(crew_roster)s %(roster_ix)s' % util.matching_patterns)
def eval_rave_on_trip_on_roster(context, rave_name, rave_value, roster_ix, crew_roster='unused'):
    """
    Then rave "leg.%start_utc%" shall be "06JUL2003 20:00" on roster 2
    """
    _eval_rave_on_leg_trip_roster(rave_name, rave_value, 0, 0, roster_ix)

@then(u'rave "%(rave_name)s" shall be "%(rave_value)s" on trip %(trip_ix)s on %(crew_roster)s %(roster_ix)s' % util.matching_patterns)
def eval_rave_on_trip_on_roster(context, rave_name, rave_value, trip_ix, roster_ix, crew_roster='unused'):
    """
    Then rave "leg.%start_utc%" shall be "06JUL2003 20:00" on trip 1 on roster 2
    """
    _eval_rave_on_leg_trip_roster(rave_name, rave_value, 1, trip_ix, roster_ix)

@then(u'rave "%(rave_name)s" shall be "%(rave_value)s" on leg %(leg_ix)s on trip %(trip_ix)s on %(crew_roster)s %(roster_ix)s' % util.matching_patterns)
def eval_rave_on_leg_on_trip_on_roster(context, rave_name, rave_value, leg_ix, trip_ix, roster_ix, crew_roster='unused'):
    """
    Then rave "leg.%start_utc%" shall be "06JUL2003 20:00" on leg 2 on trip 1 on roster 2
    """
    _eval_rave_on_leg_trip_roster(rave_name, rave_value, leg_ix, trip_ix, roster_ix)
    

@then(u'rave "%(rave_name)s" values shall be' % util.matching_patterns)
def eval_rave_values(context, rave_name):
    """
    Then rave "trip.%start_hb%" values shall be
     | trip | roster | value           |
     | 1    | 1      | 01NOV2016 00:00 |
     | 2    | 1      | 02NOV2016 00:00 |
     | 1    | 2      | 03NOV2016 00:00 |
     | 2    | 2      | 04NOV2016 00:00 |
     | 1    | 3      | 01NOV2016 00:00 |
     | 2    | 3      | 02NOV2016 00:00 |
     | 3    | 3      | 03NOV2016 00:00 |
     | 4    | 3      | 04NOV2016 00:00 |

         If leg is not specified, the trip level will be used.
         If trip is not specified, the roster level will be used.
         If roster is not specified, a trip chain will be used.
    """

    # Add all needed columns, default value to ''
    for column in RAVE_VALUE_COLUMNS:
        context.table.ensure_column_exists(column)

    # Verify that all columns can be handled
    for column in context.table.headings:
        assert column in RAVE_VALUE_COLUMNS, 'Cannot handle column %s, use: %s' % (column, ", ".join(RAVE_VALUE_COLUMNS))

    for row in context.table:
        rave_value = row[context.table.get_column_index('value')]
        # Interpret empty string as voiding value
        if rave_value == '':
            rave_value = 'None'
        elif rave_value.startswith('"') and rave_value.endswith('"') and len(rave_value) >= 2:
            rave_value = rave_value[1:-1]
        legs = util.verify_int_list(row['leg'])
        if legs == None:
            legs = [0]
        trips = util.verify_int_list(row['trip'])
        if trips == None:
            trips = [0]
        rosters = util.verify_int_list(row['roster'])
        if rosters == None:
            rosters = [0]

        for roster in rosters:
            for trip in trips:
                for leg in legs:
                    _eval_rave_on_leg_trip_roster(rave_name, rave_value, leg, trip, roster)


#
# eval rules
#

@then(u'the rule "%(rave_name)s" shall %(pass_fail)s on leg %(leg_ix)s' % util.matching_patterns)
def eval_rule_on_leg(context, rave_name, pass_fail, leg_ix):
    """
    Then the rule "trip_rules_exp.min_connection_time" shall pass on leg 1
    """
    _eval_rave_on_leg_trip_roster(rave_name, pass_fail, leg_ix,1,0, EVAL_TYPE.Rule)

@then(u'the rule "%(rave_name)s" shall %(pass_fail)s on trip %(trip_ix)s' % util.matching_patterns)
def eval_rule_on_trip(context, rave_name, pass_fail, trip_ix):
    """
    Then the rule "trip_rules_exp.max_no_of_consecutive_night_duties_per_trip" shall pass on trip 1
    """
    _eval_rave_on_leg_trip_roster(rave_name, pass_fail, 1, trip_ix, 0, EVAL_TYPE.Rule)

@then(u'the rule "%(rave_name)s" shall %(pass_fail)s on trip %(trip_ix)s on %(crew_roster)s %(roster_ix)s' % util.matching_patterns)
def eval_rule_on_trip_on_roster(context, rave_name, pass_fail, trip_ix, roster_ix, crew_roster='unused'):
    """
    Then the rule "trip_rules_exp.max_no_of_consecutive_night_duties_per_trip" shall pass on trip 1 on roster 2
    """
    _eval_rave_on_leg_trip_roster(rave_name, pass_fail, 1, trip_ix, roster_ix, EVAL_TYPE.Rule)

@then(u'the rule "%(rave_name)s" shall %(pass_fail)s on leg %(leg_ix)s on trip %(trip_ix)s' % util.matching_patterns)
def eval_rule_on_leg_on_trip(context, rave_name, pass_fail, leg_ix, trip_ix):
    """
    Then the rule "trip_rules_exp.min_connection_time" shall pass on leg 1 on trip 2
    """
    _eval_rave_on_leg_trip_roster(rave_name, pass_fail, leg_ix,trip_ix,0, EVAL_TYPE.Rule)

@then(u'the rule "%(rave_name)s" shall %(pass_fail)s on leg %(leg_ix)s on trip %(trip_ix)s on %(crew_roster)s %(roster_ix)s' % util.matching_patterns)
def eval_rule_on_leg_on_trip_on_roster(context, rave_name, pass_fail, leg_ix, trip_ix, roster_ix, crew_roster='unused'):
    """
    Then the rule "eu_ops.minimum_rest" shall pass on leg 2 on trip 1 on roster 2
    """
    _eval_rave_on_leg_trip_roster(rave_name, pass_fail, leg_ix,trip_ix,roster_ix, EVAL_TYPE.Rule)

@then(u'the rule "%(rave_name)s" legality shall be' % util.matching_patterns)
def eval_rule_legality(context, rave_name):
    """
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_ctr_flight" legality shall be
     | trip | roster | value |
     | 1    | 1      | pass  |
     | 2    | 1      | fail  |
     | 1    | 2      | pass  |
     | 2    | 2      | pass  |
     | 1    | 3      | fail  |
     | 2    | 3      | pass  |
     | 3    | 3      | pass  |
     | 4    | 3      | pass  |

         If leg is not specified, the trip level will be used.
         If trip is not specified, the roster level will be used.
         If roster is not specified, a trip chain will be used.
    """

    # Add all needed columns, default value to ''
    for column in RAVE_LEGALITY_COLUMNS:
        context.table.ensure_column_exists(column)

    # Verify that all columns can be handled
    for column in context.table.headings:
        assert column in RAVE_LEGALITY_COLUMNS, 'Cannot handle column %s, use: %s' % (column, ", ".join(RAVE_LEGALITY_COLUMNS))

    for row in context.table:
        rave_value = row[context.table.get_column_index('value')]
        # Interpret empty string as voiding value
        if rave_value == '':
            rave_value = 'None'
        elif rave_value.startswith('"') and rave_value.endswith('"') and len(rave_value) >= 2:
            rave_value = rave_value[1:-1]
        legs = util.verify_int_list(row['leg'])
        if legs == None:
            legs = [0]
        trips = util.verify_int_list(row['trip'])
        if trips == None:
            trips = [0]
        rosters = util.verify_int_list(row['roster'])
        if rosters == None:
            rosters = [0]

        for roster in rosters:
            for trip in trips:
                for leg in legs:
                    _eval_rave_on_leg_trip_roster(rave_name, rave_value, leg, trip, roster, EVAL_TYPE.Rule)


#
# eval constraints
# Todo: I'm not sure this is really working yet.
#       When testing one constraint it always returned "0".
#       I'm not sure what needs to be fixed, or how it should be used.
#
@then(u'the constraint "%(rave_name)s" shall be "%(rave_value)s" on leg %(leg_ix)s on trip %(trip_ix)s on %(crew_roster)s %(roster_ix)s' % util.matching_patterns)
def eval_constraint_on_leg_on_trip_on_roster(context, rave_name, rave_value, leg_ix, trip_ix, roster_ix, crew_roster='unused'):
    """
    Then the constraint "roster_constraints.temp_crew_skd_sks_cc" shall be "0" on leg 1 on trip 1 on roster 2
    """
    _eval_rave_on_leg_trip_roster(rave_name, rave_value, leg_ix, trip_ix, roster_ix, EVAL_TYPE.Constraint)

#
# Evaluate rave variable/rule/constraint
#
def _eval_rave_on_leg_trip_roster(rave_name, rave_value, leg_ix,trip_ix,roster_ix, eval_type=EVAL_TYPE.Rave):
    leg_ix = util.verify_int(leg_ix)
    trip_ix = util.verify_int(trip_ix)
    roster_ix = util.verify_int(roster_ix)
    
    rave_name = util.verify_rave_name(rave_name)
    if eval_type == EVAL_TYPE.Rule:
        if rave_value.encode().lower()=='pass':
            exp_results = ['True', 'None'] # Void-ing rules pass
        else:
            exp_results = ['False']
    else:
        exp_results = [util.verify_rave_value(rave_value)]

    rave_result = str(eval_rave(rave_name, leg_ix, trip_ix, roster_ix, eval_type))

    extra_info = " on roster %s trip %s leg %s" % (roster_ix, trip_ix, leg_ix)
    assert rave_result in exp_results, '%s %s evaluated to "%s" ("%s")%s\nNote: exact string matching is used' % \
        (eval_type.name, rave_name, rave_result, ' or '.join(exp_results), extra_info)


def eval_rave(rave_name, leg_ix=1, trip_ix=1, roster_ix=0, eval_type=EVAL_TYPE.Rave):
    ret = None
    win_chains = WindowChains()
    current_roster = 0
    if roster_ix > 0:
        for roster_bag in win_chains.bag.chain_set(sort_by="crew.%id%"):
            current_roster += 1
            if current_roster==roster_ix:
                # Need to do this within for loop for the bag to still exist
                ret = eval_rave_on_trip_bag(roster_bag, eval_type, rave_name, leg_ix, trip_ix)
                break
        assert ret, 'Could not find roster %s' % (roster_ix)
    else:
        ret = eval_rave_on_trip_bag(win_chains.bag, eval_type, rave_name, leg_ix, trip_ix)
    return ret[0]


def eval_rave_on_trip_bag(trips_bag, eval_type, rave_name, leg_ix=1, trip_ix=1):
    if trip_ix == 0:
        return eval_rave_on_leg_bag(trips_bag, eval_type, rave_name, leg_ix)
    else:
        current_trip = 0
        for trip_bag in getattr(getattr(trips_bag, iterators_trip), trip_set)():
            current_trip+=1
            if current_trip==trip_ix:
                return eval_rave_on_leg_bag(trip_bag, eval_type, rave_name, leg_ix)
        assert False, 'Could not find trip %s' % (trip_ix)
    

def eval_rave_on_leg_bag(legs_bag, eval_type, rave_name, leg_ix=1):
    if leg_ix == 0:
        return eval_rave_on_bag(legs_bag, eval_type, rave_name)
    else:
        current_leg = 0
        for leg_bag in legs_bag.atom_set():
            current_leg+=1
            if current_leg==leg_ix:
                return eval_rave_on_bag(leg_bag, eval_type, rave_name)
        assert False, 'Could not find leg %s' % (leg_ix)


def eval_rave_on_bag(bag, eval_type, rave_name):
    # Assume module.variable 
    try:
        if eval_type == EVAL_TYPE.Rule:
            rave_eval = rave.eval(bag, rave.rule(rave_name))
        elif eval_type == EVAL_TYPE.Constraint:
            rave_eval = rave.eval(bag, rave.constraint(rave_name))
        else:
            rave_eval = rave.eval(bag, rave.expr(rave_name))
    except rave.UsageError as e:
        assert False, 'Can not handle rave expression %s, use module.%%rave_name%%, module.rule or keyword\n.%s'\
                                      % (rave_name, e)

    return rave_eval


def num_selected_trips():
    win_chains = WindowChains()
    rave_eval = rave.eval(win_chains.bag, rave.var(custom.map_num_marked_trips))
    return rave_eval[0]

def num_selected_legs():
    win_chains = WindowChains()
    rave_eval = rave.eval(win_chains.bag, rave.var(custom.map_num_marked_legs))
    return rave_eval[0]

# Simple version of the OTS class
class WindowChains():
    def __init__(self):
        self.area = Cui.CuiWhichArea
        self.win_buf = cuib.CuiBuffer(self.area, cuib.WindowScope)
        self._buf = cpmb.CpmBuffer(self.win_buf, 'true')
        self.bag = rave.buffer2context(self._buf).bag()
        

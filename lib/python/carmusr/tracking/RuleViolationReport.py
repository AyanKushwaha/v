import os
import re
import tempfile

import Cui
import carmensystems.rave.api as r
from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime
from Variable import Variable

from utils.rave import RaveIterator
from utils.selctx import SingleCrewFilter
from tm import TM

"""
To run the RuleViolationReport job from the command-line:
$CARMUSR/bin/testing/submitDigJob.sh --job subq_violation --name Test --st 06Nov2009 ...
   --rerun True --report "report_sources.report_server.rs_subq_violation" --delta "1"

"""

class RuleHandler(object):
    """
    Looks for a specific set of rules defined in the current ruleset, and
    provides means to turn these rules on or off, turning all other rules off.
    
    The rules to look for is given by a set of name expressions in
    'rave_string_paramset' (given by a ravevar and valid-date).
    
    Example:
      If 'rave_string_paramset' contains these definitions:
        subq_violation_report_rules rule*.*subq*       01Jan1986 01Jan2035
        subq_violation_report_rules !*max_duty_in_fdp* 01Jan1986 01Jan2035
      then a RuleHandler with:
          validdate:     AbsTime("1jan2010")
          paramset_key:  TM.rave_paramset_set["subq_violation_report_rules"]
      can be used to temporarily turn on all subpart-Q rules, except the one
      for "max_duty_in_fdp", while all other rules are turned off.
    """
    def __init__(self, validdate, paramset_key):
        onoffrules = {}
        
        # Find rules specified in rave_string_paramset 'paramset_key' that are
        # valid on the given date. Store in local 'onoffrules' as
        # Key (string): Expression
        # Value (tuple): [0] (bool):  If matching rules are to be on or off.
        #                [1] (regex): Compiled re.
        #                [2] (list):  names of matching rules (initially empty)
        # The name list is only for reference, when validating the expressions.
        
        print 'Checking "%s" rule expressions valid %s...' \
              % (paramset_key.id, AbsDate(validdate))
        rule_name_expression = [expr.val.replace(' ', '')
            for expr in paramset_key.referers("rave_string_paramset", "ravevar")
            if expr.validfrom <= validdate <= expr.validto]
        for expr in rule_name_expression:
            off = expr.startswith("!")
            regex_str = expr[off:].replace('.', "\.") \
                                  .replace('*', ".*?") \
                                  .replace('?', ".")
            try:
                regex = re.compile("(?i)^" + regex_str + "$")
                onoffrules[expr] = [not off, regex, []]
            except Exception,e:
                print '  Expression "%s" *** Cannot evaluate: %s' % (expr, e)
                
        # Create the list 'self._all_rules' withe an item for each of the rules
        # in the currently loaded ruleset:
        # [0] (string): Rule name
        # [1] (bool):   If the rule is initially on or off
        # [2] (bool):   If the rule is to be on or off during report generation
        #               as defined by "subq_violation_report_rules" expressions
        #               (see onoffrules above). Default is off (False).

        self._all_rules = []
        parset_fd, parset_name = tempfile.mkstemp()
        os.close(parset_fd)
        try:
            Cui.CuiCrcSaveParameterSet(Cui.gpc_info, 0, parset_name, 0, 14)
            parset_file = open(parset_name, "r")
            try:
                # Create a 'self._all_rules' item for each rule in the ruleset.
                # Check if the rule matches an 'onoffrules' expression. 
                
                section = "RULES"
                for row in [row.strip() for row in parset_file.readlines()]:
                    m = re.match(r"^<(.+)>", row)
                    if m: 
                        section =  m.group(1)
                    elif section == "RULES":
                        m = re.match(r"^([^_].+?)\s+(on|off)\b", row)
                        if m:
                            try:
                                rule = r.rule(m.group(1))
                                orig = rule.on()
                                for onoff, regex, names in sorted(onoffrules.values()):
                                    if regex.match(rule.name()):
                                        want = onoff
                                        names.append(rule.name())
                                        break
                                else:
                                    want = False
                                self._all_rules.append((rule, orig, want))
                            except r.UsageError, e:
                                print "Warning:", e
                                
                # Log expressions + corresponding rules
                         
                for expr, (on, regex, names) in sorted(onoffrules.items()):
                    print '  Expression "%s" - rule(%s) -' % (expr, ("OFF","ON")[on]),
                    if not names:
                        print "NO MATCHING RULES"
                    else:
                        print "matching rules:"
                        for name in sorted(names):
                            print "   ",name
            finally:
                parset_file.close()                    
        finally:
            os.remove(parset_name)
    
    def turn_on_specified_rules_and_turn_off_all_other(self):
        print "Switching to temporary rule settings"
        for rule, orig, want in self._all_rules:
            if orig != want:
                rule.setswitch(want)
        
    def reset_to_original_rule_onoff_settings(self):
        print "Returning to original rule settings"
        for rule, orig, want in self._all_rules:
            if orig != want:
                rule.setswitch(orig)
    
"""
import  carmusr.tracking.RuleViolationReport as RuleViolationReport
reload(RuleViolationReport)
RuleViolationReport.subq_violation_report("1dec2009", "31dec2009", True)
"""

def subq_violation_report(st=None, en=None, rerun=False):
    """
    Implements CR476 - Sub Q Violation Reports.
    
    For the given date range (default is yesterday) search the plan for
    Subpart-Q rule failures.
    
    Rules to look for is given by name expressions in 'rave_string_paramset',
    using 'rave_paramset_set' item "subq_violation_report_rules" as ravevar key.
    
    Store failure info in the 'rule_violation_log' table, using 
    'rave_paramset_set' item "subq_violation_report_rules" as logtype key.
    
    If rerun=True, any existing 'rule_violation_log' entries with logtype
    "subq_violation_report_rules" for the given date range are removed prior
    to the run.
    """
    
    today, = r.eval("round_down(fundamental.%now%, 24:00)")
    yesterday = today - RelTime(24,0)
    starttime = AbsTime(st or yesterday).day_floor()
    endtime = (AbsTime(en or starttime).day_floor() + RelTime(0,1)).day_ceil()
    print starttime,endtime,yesterday
    
    assert endtime <= today, "Cannot store future rule failures"
    assert starttime < endtime, "Invalid date range: start > end"
    
    msg = "RUNNING SUB Q VIOLATION REPORT FOR PERIOD [%s .. %s[" % (
          AbsDate(starttime), AbsDate(endtime))
    print (len(msg)+8) * "-"
    print "---",msg,"---"
    print (len(msg)+8) * "-"
    
    logtype = TM.rave_paramset_set["subq_violation_report_rules"]
    rulehandler = RuleHandler(starttime, logtype)
    
    remove_count = 0
    exist_ldap = ("(&(logtype=%s)(failtime>=%s)(failtime<%s))"  
                  % (logtype.id, starttime, endtime))
    for row in TM.rule_violation_log.search(exist_ldap):
        assert rerun, "There is already a logged rule violation for %s" % row.failtime
        row.remove()
        remove_count += 1
        
    if remove_count:
        print "REMOVED %d EXISTING ROWS" % remove_count
    
    try:
        # Do not consider rule exceptions when checking SubQ rule violations (SASCMS-4461)
        r.param('rule_exceptions.%include_rule_exceptions_p%').setvalue(False)
        rulehandler.turn_on_specified_rules_and_turn_off_all_other()
        
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiNoArea, 'PLAN')
        context = 'sp_crew'
        crew_failures = {}
        rule_stats = {}
        rule_errors = {}
        
        print "SEARCHING FOR RULE VIOLATIONS"
        
        RE_ABSDATE = re.compile(
            r"\d\d(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\d\d\d\d")

        for ix,crew,failures in r.eval(context, r.foreach('iterators.roster_set',
                'crew.%id%', r.foreach(r.rulefailure())))[0]:
            failure_list = []
            for failure in [f[0] for f in failures]:
                try:
                    # Extract the scheduled start time according to the
                    # '+'-separated items in the failobject.
                    # Note that the time component items are in different
                    # positions within the list depending on the type of object.
                    fo_items = failure.failobject.split("+")
                    for dat in fo_items:
                       if RE_ABSDATE.match(dat):
                           break
                    tim = fo_items[-3]
                    failtime = AbsTime("%s %s:%s" % (dat, tim[:2], tim[2:]))
                    # Now check if the failure occurred in our interval.
                    if starttime <= failtime < endtime:
                        failure_list.append((failure, failtime))
                        rule = failure.rule.name()
                        rule_stats[rule] = rule_stats.get(rule, 0) + 1
                except Exception,x:
                    k = "Rule: %s / Error: %s" % (failure.rule, x)
                    rule_errors[k] = rule_errors.get(k, 0) + 1
            if failure_list:
                crew_failures[crew] = failure_list
   
        print "%s RULE VIOLATIONS FOR %s OF %s CREW" % (
            sum(len(fl) for fl in crew_failures.values()), len(crew_failures), ix)
          
        if crew_failures:
            for crewid in crew_failures.keys():
                crew = TM.crew[crewid]
                ctx = SingleCrewFilter(crewid)
                legs = RaveIterator(r.iter('iterators.leg_set'), {
                        'empno':  'crew.%extperkey_at_date%(leg.%start_hb%)',
                        'sobt':   'leg.%activity_scheduled_start_time_utc%',
                        'flid':   'leg.%flight_id%',
                        'adep':   'leg.%start_station%',
                        'ades':   'leg.%end_station%',
                        'rank':   'crew_pos.%current_function%',
                        'func':   'crew_pos.%assigned_function%',
                        'base':   'leg.%homebase%',
                        'region': 'leg.%region%',
                        'quals':  'report_rule_violation.%crew_ac_quals_at_leg_start%',
                    }).eval(ctx.context())
                for (failure,failtime) in crew_failures[crewid]:
                    key = (logtype, crew, failure.rule.name(), failtime)
                    try:
                        # There may be cases when the same error results in
                        # several violations to the same rule, with the same
                        # failobject. In that case, just ignore the duplicates.
                        row = TM.rule_violation_log[key]
                        si = (row.si or "")
                        if si: si += ","
                        if len(str(si)) > 192:
                            continue
                        else:
                            row.si = si + "dup=True"
                            continue
                    except:
                        pass
                    row = TM.rule_violation_log.create(key)
                    row.activitykey = failure.failobject
                    row.starttime = failure.startdate
                    row.ruleremark = failure.failtext
                    if failure.limitvalue:
                        row.limitval = str(failure.limitvalue) 
                    if failure.actualvalue:
                        row.actualval = str(failure.actualvalue)
                    try:
                        row.overshoot = int(failure.overshoot)
                    except:
                        pass
                    for leg in legs:
                        if leg.sobt == failtime:
                            row.si = ",".join([
                                "empno=%s"  % leg.empno,
                                "region=%s" % leg.region,
                                "base=%s"   % leg.base,
                                ",".join("qual=%s" % q
                                         for q in leg.quals.split(":")),
                                "adep=%s"   % leg.adep,
                                "ades=%s"   % leg.ades,
                                "rank=%s"   % leg.rank,
                                "func=%s"   % (leg.func or "--"),
                                ])
                            break
                    else:
                        row.si = "**No activity corresponding to activitykey**"
                        
            print "-----------------------"
            print "--- VIOLATIONS/RULE ---"
            print "-----------------------"
            for rule, count in sorted(rule_stats.items()):
                print "%5d * %s" % (count ,rule)
            print "%5d total" % sum(count for count in rule_stats.values())
        
        if rule_errors:
            print "*******************"
            print "*** RULE ERRORS ***"
            print "*******************"
            for rule_err, count in sorted(rule_errors.items()):
                print "%4d %s" % (count,rule_err) 
                
    finally:    
        r.param('rule_exceptions.%include_rule_exceptions_p%').setvalue(True)
        rulehandler.reset_to_original_rule_onoff_settings()
        print "SUB Q VIOLATION REPORT DONE"
        

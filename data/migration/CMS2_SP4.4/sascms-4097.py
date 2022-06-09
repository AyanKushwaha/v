#!/bin/env python


"""
SASCMS-4097 
 - The startdate is changed for the rule rules_indust_ccr.ind_max_duty_time_in_7x24_hrs_all
   so rule exceptions must be created to avoid new warnings for already excepted rulebreaks. 

"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    rule_exception_list = {}

    # Only create new rule exception for alerts after this date
    from_time = int(AbsTime('01Sep2012'))

    # Find all rule exception entries
    for r in list(fixrunner.level_1_query(dc, " ".join((
        "SELECT",
            "re.crew, re.ruleid, re.starttime, ta.alerttime, ta.exceptionstarttime, re.activitykey, re.ruleremark, "
            "re.limitval, re.actualval , re.overrel, re.overint, re.ctime, re.reason, re.si",
        "FROM",
            "track_alert ta,",
            "rule_exception re",
        "WHERE",
            "re.ruleid = 'rules_indust_ccr.ind_max_duty_time_in_7x24_hrs_all'",
            "AND",
            "re.deleted = 'N'",
            "AND",
            "re.next_revid = 0",   
            "AND",
            "ta.rule = 'rules_indust_ccr.ind_max_duty_time_in_7x24_hrs_all'",
            "AND",
            "ta.next_revid = 0",
            "AND",
            "re.activitykey = ta.activity_atype || '+' || ta.activity_id",
            "AND",
            "re.starttime <> ta.alerttime",
            "AND",
            "ta.alerttime > %u" % (from_time),
        )), ['re_crew', 're_ruleid', 're_startime', 'ta_alerttime', 'ta_exceptionstarttime',
             're_activitykey', 're_ruleremark', 're_limitval', 're_actualval', 're_overrel', 
             're_overint', 're_ctime', 're_reason', 're_si'])):

        key = (r['re_crew'], r['re_ruleid'], r['ta_alerttime'])
        rule_exception_list[key] =  {'crew' : r['re_crew'],
                                     'ruleid' : r['re_ruleid'],
                                     'starttime' : r['ta_alerttime'],
                                     'activitykey' : r['re_activitykey'],
                                     'ruleremark' : r['re_ruleremark'],
                                     'limitval' : r['re_limitval'],
                                     'actualval' :r['re_actualval'],
                                     'overrel' : r['re_overrel'],
                                     'overint' : r['re_overint'],
                                     'username' : 'sascms-4097',
                                     'ctime' : r['re_ctime'],
                                     'reason' : r['re_reason'],
                                     'si' : r['re_si']} 

        
    added_rows = []
    
    # Create new rule exceptions to avoid new alerts to be generated when the new rule
    # is deployed. 
    for key, entry in rule_exception_list.iteritems():
        if len(fixrunner.dbsearch(dc, "rule_exception", "crew = '%s'  and ruleid='%s' and starttime='%s'" % (key[0], key[1], key[2]))) == 0 and \
            not key in added_rows:
            added_rows.append(key)
            ops.append(fixrunner.createop("rule_exception", 'N', entry))

    return ops


fixit.program = 'sascms-4097.py (%s)' % __version__


if __name__ == '__main__':
    fixit()

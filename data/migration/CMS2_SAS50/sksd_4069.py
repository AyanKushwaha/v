#!/bin/env python


"""
SKSD-4069 Split MISMATCH into MISMATCH_C and MISMATCH_F
"""


import adhoc.fixrunner as fixrunner


__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    #Modify relevant entity filters
    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"mppcategory", "id":"mppcategory_crew_user_filter", "where_condition":"($.validfrom < %:3*1440 and $.validto >= %:4*1440-367*1440) AND (($.val='MISMATCH_C' AND %:1='C') OR ($.val='MISMATCH_F' AND %:1='F') OR ($.filt='EMPLOYMENT' and %:1='F' and $.val like 'F|%%') OR ($.filt='EMPLOYMENT' and %:1='C' and $.val like 'C|%%'))"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"mppcategory", "id":"mppcategory_crew_user_filter", "where_condition":"($.validfrom < %:3*1440 and $.validto >= %:4*1440-367*1440) AND ($.val='MISMATCH' OR ($.filt='EMPLOYMENT' and %:1='F' and $.val like 'F|%%') OR ($.filt='EMPLOYMENT' and %:1='C' and $.val like 'C|%%'))"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"mppcategory", "id":"mppcategory_crew_user_filter_1", "where_condition":"($.validfrom < %:3*1440 and $.validto >= %:4*1440-367*1440) AND (($.val='MISMATCH_C' AND %:1='C') OR ($.val='MISMATCH_F' AND %:1='F') OR ($.filt='EMPLOYMENT' and %:1='F' and $.val like 'F|%%') OR ($.filt='EMPLOYMENT' and %:1='C' and $.val like 'C|%%'))"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"mppcategory", "id":"mppcategory_crew_user_filter_1", "where_condition":"($.validfrom < %:3*1440 and $.validto >= %:4*1440-367*1440) AND ($.val='MISMATCH' OR ($.filt='EMPLOYMENT' and %:1='F' and $.val like 'F|%%') OR ($.filt='EMPLOYMENT' and %:1='C' and $.val like 'C|%%'))"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"mppcategory", "id":"mppcategory_crew_user_filter_2", "where_condition":"($.validfrom < %:3*1440 and $.validto >= %:4*1440-367*1440) AND (($.val='MISMATCH_C' AND %:1='C') OR ($.val='MISMATCH_F' AND %:1='F') OR ($.filt='EMPLOYMENT' and %:1='F' and $.val like 'F|%%') OR ($.filt='EMPLOYMENT' and %:1='C' and $.val like 'C|%%'))"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"mppcategory", "id":"mppcategory_crew_user_filter_2", "where_condition":"($.validfrom < %:3*1440 and $.validto >= %:4*1440-367*1440) AND ($.val='MISMATCH' OR ($.filt='EMPLOYMENT' and %:1='F' and $.val like 'F|%%') OR ($.filt='EMPLOYMENT' and %:1='C' and $.val like 'C|%%'))"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"mppcategory", "id":"mppcategory_crew_user_filter_3", "where_condition":"($.validfrom < %:3*1440 and $.validto >= %:4*1440-367*1440) AND (($.val='MISMATCH_C' AND %:1='C') OR ($.val='MISMATCH_F' AND %:1='F') OR ($.filt='EMPLOYMENT' and %:1='F' and $.val like 'F|%%') OR ($.filt='EMPLOYMENT' and %:1='C' and $.val like 'C|%%'))"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"mppcategory", "id":"mppcategory_crew_user_filter_3", "where_condition":"($.validfrom < %:3*1440 and $.validto >= %:4*1440-367*1440) AND ($.val='MISMATCH' OR ($.filt='EMPLOYMENT' and %:1='F' and $.val like 'F|%%') OR ($.filt='EMPLOYMENT' and %:1='C' and $.val like 'C|%%'))"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"mppcategory", "id":"mppcategory_crew_user_filter_4", "where_condition":"($.validfrom < %:3*1440 and $.validto >= %:4*1440-367*1440) AND (($.val='MISMATCH_C' AND %:1='C') OR ($.val='MISMATCH_F' AND %:1='F') OR ($.filt='EMPLOYMENT' and %:1='F' and $.val like 'F|%%') OR ($.filt='EMPLOYMENT' and %:1='C' and $.val like 'C|%%'))"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"mppcategory", "id":"mppcategory_crew_user_filter_4", "where_condition":"($.validfrom < %:3*1440 and $.validto >= %:4*1440-367*1440) AND ($.val='MISMATCH' OR ($.filt='EMPLOYMENT' and %:1='F' and $.val like 'F|%%') OR ($.filt='EMPLOYMENT' and %:1='C' and $.val like 'C|%%'))"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"mppcategory", "id":"mppcategory_crew_user_filter_5", "where_condition":"($.validfrom < %:3*1440 and $.validto >= %:4*1440-367*1440*2) AND (($.val='MISMATCH_C' AND %:1='C') OR ($.val='MISMATCH_F' AND %:1='F') OR ($.filt='EMPLOYMENT' and %:1='F' and $.val like 'F|%%') OR ($.filt='EMPLOYMENT' and %:1='C' and $.val like 'C|%%'))"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"mppcategory", "id":"mppcategory_crew_user_filter_5", "where_condition":"($.validfrom < %:3*1440 and $.validto >= %:4*1440-367*1440*2) AND ($.val='MISMATCH' OR ($.filt='EMPLOYMENT' and %:1='F' and $.val like 'F|%%') OR ($.filt='EMPLOYMENT' and %:1='C' and $.val like 'C|%%'))"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"mppcategory", "id":"mppcategory_crew_user_filter_7", "where_condition":"($.validfrom < %:3*1440 and $.validto >= %:4*1440-367*1440) AND (($.val='MISMATCH_C' AND %:1='C') OR ($.val='MISMATCH_F' AND %:1='F') OR ($.filt='EMPLOYMENT' and %:1='F' and $.val like 'F|%%') OR ($.filt='EMPLOYMENT' and %:1='C' and $.val like 'C|%%'))"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"mppcategory", "id":"mppcategory_crew_user_filter_7", "where_condition":"($.validfrom < %:3*1440 and $.validto >= %:4*1440-367*1440) AND ($.val='MISMATCH' OR ($.filt='EMPLOYMENT' and %:1='F' and $.val like 'F|%%') OR ($.filt='EMPLOYMENT' and %:1='C' and $.val like 'C|%%'))"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"mppcategory", "id":"mppcategory_crew_user_filter_8", "where_condition":"($.validfrom < %:3*1440 and $.validto >= %:4*1440-367*1440) AND (($.val='MISMATCH_C' AND %:1='C') OR ($.val='MISMATCH_F' AND %:1='F') OR ($.filt='EMPLOYMENT' and %:1='F' and $.val like 'F|%%') OR ($.filt='EMPLOYMENT' and %:1='C' and $.val like 'C|%%'))"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"mppcategory", "id":"mppcategory_crew_user_filter_8", "where_condition":"($.validfrom < %:3*1440 and $.validto >= %:4*1440-367*1440) AND ($.val='MISMATCH' OR ($.filt='EMPLOYMENT' and %:1='F' and $.val like 'F|%%') OR ($.filt='EMPLOYMENT' and %:1='C' and $.val like 'C|%%'))"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"mppcategory", "id":"mppcategory_crew_user_filter_9", "where_condition":"($.validfrom < %:3*1440 and $.validto >= %:4*1440-367*1440) AND (($.val='MISMATCH_C' AND %:1='C') OR ($.val='MISMATCH_F' AND %:1='F') OR ($.filt='EMPLOYMENT' and %:1='F' and $.val like 'F|%%') OR ($.filt='EMPLOYMENT' and %:1='C' and $.val like 'C|%%'))"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"mppcategory", "id":"mppcategory_crew_user_filter_9", "where_condition":"($.validfrom < %:3*1440 and $.validto >= %:4*1440-367*1440) AND ($.val='MISMATCH' OR ($.filt='EMPLOYMENT' and %:1='F' and $.val like 'F|%%') OR ($.filt='EMPLOYMENT' and %:1='C' and $.val like 'C|%%'))"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_active", "id":"crew_user_filter_active_crew_user_filter", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.filt='CONTRACT' AND $.val in ('ACTIVE','MISMATCH_C','MISMATCH_F'))"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_active", "id":"crew_user_filter_active_crew_user_filter", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.filt='CONTRACT' AND $.val in ('ACTIVE','MISMATCH'))"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_active", "id":"crew_user_filter_active_crew_user_filter_1", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.filt='CONTRACT' AND $.val in ('ACTIVE','MISMATCH_C','MISMATCH_F'))"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_active", "id":"crew_user_filter_active_crew_user_filter_1", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.filt='CONTRACT' AND $.val in ('ACTIVE','MISMATCH'))"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_active", "id":"crew_user_filter_active_crew_user_filter_2", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.filt='CONTRACT' AND $.val in ('ACTIVE','MISMATCH_C','MISMATCH_F'))"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_active", "id":"crew_user_filter_active_crew_user_filter_2", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.filt='CONTRACT' AND $.val in ('ACTIVE','MISMATCH'))"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_cct", "id":"crew_user_filter_cct_crew_user_filter", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.val like %:3 OR $.val like %:4 OR $.val like %:3||'_CCT' OR $.val like %:4||'_CCT' OR length(REGEXP_SUBSTR($.val,%:5))>0 OR $.val='MISMATCH_C' OR $.val='MISMATCH_F')"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_cct", "id":"crew_user_filter_cct_crew_user_filter", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.val like %:3 OR $.val like %:4 OR $.val like %:3||'_CCT' OR $.val like %:4||'_CCT' OR length(REGEXP_SUBSTR($.val,%:5))>0 OR  $.val='MISMATCH')"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_cct", "id":"crew_user_filter_cct_crew_user_filter_1", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.val like %:3 OR $.val like %:4 OR $.val like %:3||'_CCT' OR $.val like %:4||'_CCT' OR length(REGEXP_SUBSTR($.val,%:5))>0 OR $.val='MISMATCH_C' OR $.val='MISMATCH_F')"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_cct", "id":"crew_user_filter_cct_crew_user_filter_1", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.val like %:3 OR $.val like %:4 OR $.val like %:3||'_CCT' OR $.val like %:4||'_CCT' OR length(REGEXP_SUBSTR($.val,%:5))>0 OR  $.val='MISMATCH')"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_cct", "id":"crew_user_filter_cct_crew_user_filter_2", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.val like %:3 OR $.val like %:4 OR $.val like %:3||'_CCT' OR $.val like %:4||'_CCT' OR length(REGEXP_SUBSTR($.val,%:5))>0 OR $.val='MISMATCH_C' OR $.val='MISMATCH_F')"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_cct", "id":"crew_user_filter_cct_crew_user_filter_2", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.val like %:3 OR $.val like %:4 OR $.val like %:3||'_CCT' OR $.val like %:4||'_CCT' OR length(REGEXP_SUBSTR($.val,%:5))>0 OR  $.val='MISMATCH')"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_quals", "id":"crew_user_filter_quals_crew_user_filter", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.val='MISMATCH_C' OR $.val='MISMATCH_F' OR  ($.filt='ACQUAL' AND ($.val=%:3 or length(REGEXP_SUBSTR($.val,%:3))>0)))"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_quals", "id":"crew_user_filter_quals_crew_user_filter", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.val='MISMATCH' OR  ($.filt='ACQUAL' AND ($.val=%:3 or length(REGEXP_SUBSTR($.val,%:3))>0)))"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_quals", "id":"crew_user_filter_quals_crew_user_filter_1", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.val='MISMATCH_C' OR $.val='MISMATCH_F' OR  ($.filt='ACQUAL' AND ($.val=%:3 or length(REGEXP_SUBSTR($.val,%:3))>0)))"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_quals", "id":"crew_user_filter_quals_crew_user_filter_1", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.val='MISMATCH' OR  ($.filt='ACQUAL' AND ($.val=%:3 or length(REGEXP_SUBSTR($.val,%:3))>0)))"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_quals", "id":"crew_user_filter_quals_crew_user_filter_2", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.val='MISMATCH_C' OR $.val='MISMATCH_F' OR  ($.filt='ACQUAL' AND ($.val=%:3 or length(REGEXP_SUBSTR($.val,%:3))>0)))"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_quals", "id":"crew_user_filter_quals_crew_user_filter_2", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.val='MISMATCH' OR  ($.filt='ACQUAL' AND ($.val=%:3 or length(REGEXP_SUBSTR($.val,%:3))>0)))"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_employment", "id":"crew_user_filter_employment_crew_user_filter", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.val='MISMATCH_C' OR $.val='MISMATCH_F' OR ($.filt='EMPLOYMENT' AND ($.val = %:3 or $.val like %:3)))"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_employment", "id":"crew_user_filter_employment_crew_user_filter", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.val='MISMATCH' OR ($.filt='EMPLOYMENT' AND ($.val = %:3 or $.val like %:3)))"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_employment", "id":"crew_user_filter_employment_crew_user_filter_1", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.val='MISMATCH_C' OR $.val='MISMATCH_F' OR ($.filt='EMPLOYMENT' AND ($.val = %:3 or $.val like %:3)))"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_employment", "id":"crew_user_filter_employment_crew_user_filter_1", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.val='MISMATCH' OR ($.filt='EMPLOYMENT' AND ($.val = %:3 or $.val like %:3)))"}))

    ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_employment", "id":"crew_user_filter_employment_crew_user_filter_2", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.val='MISMATCH_C' OR $.val='MISMATCH_F' OR ($.filt='EMPLOYMENT' AND ($.val = %:3 or $.val like %:3)))"}))
    # ops.append(fixrunner.createop("dave_entity_filter", "U", {"selection":"crew_user_filter_employment", "id":"crew_user_filter_employment_crew_user_filter_2", "where_condition":"($.validfrom<=%:2 and $.validto>%:1) AND ($.val='MISMATCH' OR ($.filt='EMPLOYMENT' AND ($.val = %:3 or $.val like %:3)))"}))

    return ops


fixit.program = 'sksd_4069.py (%s)' % __version__
if __name__ == '__main__':
    fixit()

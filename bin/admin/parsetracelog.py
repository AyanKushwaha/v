#!/usr/bin/env python
"""
Transforms a piece from the trace log (see 'x' below) into an executable SQL statement.
"""

x = """
TRACE: dave_oracle::OCI::vstmt pre_sql="SELECT /* Tracking TrackingStudio */ crew_activity_0.* FROM cms_test.crew_activity crew_activity_0 WHERE EXISTS (SELECT 1 FROM cms_test.crew_user_filter crew_user_filter_1 WHERE (crew_user_filter_
1.next_revid = 0) AND (crew_user_filter_1.deleted = 'N') AND (crew_user_filter_1.branchid = %:5) AND (crew_activity_0.crew = crew_user_filter_1.crew) AND (crew_activity_0.branchid = crew_user_filter_1.branchid) AND (((crew_user_filter_1
.validfrom<=%:18 and crew_user_filter_1.validto>%:17) AND (crew_user_filter_1.filt='CONTRACT' AND crew_user_filter_1.val in ('ACTIVE','MISMATCH'))))) AND (crew_activity_0.next_revid = 0) AND (crew_activity_0.deleted = 'N') AND (crew_act
ivity_0.branchid = %:5) AND ((crew_activity_0.st<=%:22 and crew_activity_0.et>=%:21))"
TRACE: dave_oracle::Reader::vstmt start
SQL: dave_oracle::Reader::vstmt Parameter values: 50779027, 50779027, 0, 0, 1, NULL, 0, 0, 13576320, 13638239, 13049280, 12522240, 9887040, 13533120, 11790720, 13638239, 13576320, 13638239, 9428, 9470, 13576320, 13638239, 13049280, 1344
6720, 13767839, 0
TRACE: dave_oracle::Reader::vfmt start
"""

import sys
stmt = []
params = []
mode = 0
try:
    for line in sys.stdin:
        line = line.strip()
        if mode >= 1 and not line.startswith("TRACE:") and not line.startswith("SQL:"):
            if mode == 1:
                stmt.append(line)
            else:
                params.append(line)
    	elif line.startswith("TRACE: dave_oracle::OCI::vstmt pre_sql"):
        	stmt.append(line[40:])
        	mode = 1
    	elif line.startswith("SQL: dave_oracle::Reader::vstmt Parameter values:"):
        	params.append(line[50:])
       	 	mode = 2
        
	stmt = ''.join(stmt)[:-1]
	params = map(str.strip, (''.join(params)).split(','))

    for i in range(len(params), 0, -1):
        stmt = stmt.replace("%%:%d" % i, params[i-1])
except Exception, message:
    print message
    exit(1)
except KeyboardInterrupt, message:
    print "Program interrupted!"
    exit(2)
print stmt

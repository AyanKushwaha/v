"""
SKCMS-2881: Update link crew data
"""
import csv
import datetime
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-02-04_e'

filepath = os.path.expandvars('$CARMUSR')
file = filepath+'/data/migration/saslink/link_crew'

def val_date(date_str):
    return int(AbsTime(date_str))/24/60

valid_from = int(AbsTime("01Mar2022"))
valid_to = int(AbsTime("31Dec2035"))

crewList = []

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()

    crewList = open(file).read().splitlines()
    for crew in crewList:
        print("Looking for %s crew to modify" % crew)
        for ce_entry in fixrunner.dbsearch(dc, 'crew_employment', "crew='%s' and validfrom<%i" % (crew, valid_from)):
            print("Updating validto in crew_employment for %s", crew)
            ce_entry['validto'] = valid_from
            ops.append(fixrunner.createop('crew_employment', 'U', ce_entry))

        for cc_entry in fixrunner.dbsearch(dc, 'crew_contract', "crew='%s' and validfrom<%i" % (crew, valid_from)):
            print("Updating validto in crew_contract for %s", crew)
            cc_entry['validto'] = valid_from
            ops.append(fixrunner.createop('crew_contract', 'U', cc_entry))

        for ce_entry in fixrunner.dbsearch(dc, 'crew_employment', "crew='%s' and validfrom>=%i" % (crew, valid_from)):
            print("Updating crew_employment for %s", crew)
            ce_entry['carrier'] = 'SVS'
            ce_entry['company'] = 'SVS'
            ce_entry['region'] = 'SVS'
            ce_entry['planning_group'] = 'SVS'
            ops.append(fixrunner.createop('crew_employment', 'U', ce_entry))

        for cc_entry in fixrunner.dbsearch(dc, 'crew_contract', "crew='%s' and validfrom>=%i and contract='%s'" % (crew, valid_from, 'V300')):
            print("Updating contract in crew_contract for CC %s", crew)
            cc_entry['contract'] = 'VSVS-101'
            ops.append(fixrunner.createop('crew_contract', 'U', cc_entry))

        for cc_entry in fixrunner.dbsearch(dc, 'crew_contract', "crew='%s' and validfrom>=%i and contract='%s'" % (crew, valid_from, 'VSA-001')):
            print("Updating contract in crew contract for CC %s", crew)
            cc_entry['contract'] = 'VSVS-001'
            ops.append(fixrunner.createop('crew_contract', 'U', cc_entry))
            
    return ops

fixit.program = 'update_link_crew.py (%s)' % __version__
if __name__ == '__main__':
    fixit()

"""
SKCMS-2881: Add new contracts for link crew
"""
import csv
import datetime
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2022-02-04_e'

filepath = os.path.expandvars('$CARMUSR')
file_fd = filepath+'/data/migration/saslink/Link_FD'
file_cc = filepath+'/data/migration/saslink/Link_CC'

def val_date(date_str):
    return int(AbsTime(date_str))/24/60

valid_from = int(AbsTime("01Mar2022"))
valid_to = int(AbsTime("31Dec2035"))

crewList_FD = []
crewList_CC = []

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()

    crewList_FD = open(file_fd).read().splitlines()
    for crew in crewList_FD:
        print("Looking for FD crew %s to modify" % crew)
        if len(fixrunner.dbsearch(dc, 'crew_contract', "crew='%s' and contract='%s'" % (crew, 'VSVS-001'))) == 0:
            print("Adding new contract for FD crew %s " % crew)
            ops.append(fixrunner.createOp("crew_contract", "N",
                            {
                                'crew': crew,
                                'validfrom': valid_from,
                                'validto': valid_to,
                                'contract': 'VSVS-001',
                                'si': '',
                                'endreason': '',
                                'patternstart': 0,
                                'cyclestart': 0,
                            }))
	
        if len(fixrunner.dbsearch(dc, 'crew_employment', "crew='%s' and company='%s'" % (crew, 'SVS'))) == 0:    
            print("Adding new employment for FD crew %s " % crew)
            ops.append(fixrunner.createOp("crew_employment","N",
                            {
                                'crew': crew,
                                'validfrom': valid_from,
                                'validto': valid_to,
                                'carrier': 'SVS',
                                'company': 'SVS',
                                'base': 'CPH',
                                'crewrank': 'FC',
                                'titlerank': 'FC',
                                'si': '',
                                'region': 'SVS',
                                'civicstation': 'CPH',
                                'station':'CPH',
                                'country': 'DK',
                                'extperkey': crew,
                                'planning_group': 'SVS',
                            }))

    crewList_CC = open(file_cc).read().splitlines()
    for crew in crewList_CC:
        print("Looking for CC crew %s to modify" % crew)
        if len(fixrunner.dbsearch(dc, 'crew_contract', "crew='%s' and contract='%s'" % (crew, 'VSVS-101'))) == 0:
            print("Adding new contract for CC crew %s " % crew)
            ops.append(fixrunner.createOp("crew_contract", "N",
                            {
                                'crew': crew,
                                'validfrom': valid_from,
                                'validto': valid_to,
                                'contract': 'VSVS-101',
                                'si': '',
                                'endreason': '',
                                'patternstart': 0,
                                'cyclestart': 0,
                            }))
	
        if len(fixrunner.dbsearch(dc, 'crew_employment', "crew='%s' and company='%s'" % (crew, 'SVS'))) == 0:    
            print("Adding new employment for CC crew %s " % crew)
            ops.append(fixrunner.createOp("crew_employment","N",
                            {
                                'crew': crew,
                                'validfrom': valid_from,
                                'validto': valid_to,
                                'carrier': 'SVS',
                                'company': 'SVS',
                                'base': 'CPH',
                                'crewrank': 'AA',
                                'titlerank': 'AA',
                                'si': '',
                                'region': 'SVS',
                                'civicstation': 'CPH',
                                'station':'CPH',
                                'country': 'DK',
                                'extperkey': crew,
                                'planning_group': 'SVS',
                            }))
            
    return ops

fixit.program = 'add_link_contract_employment.py (%s)' % __version__
if __name__ == '__main__':
    fixit()

import csv
from datetime import datetime

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from carmensystems.basics.uuid import uuid
import utils.Names

'''
Usage:
    1. Read from csv file (reference SASINC0244695)
    2. Change open statements to target correct files, change dates
    3. Update __version__
    4. Run using
        $ python crew_qual.py
'''
 
crewList = []
def main():
    update_crew_qual()
    fixit()
 
def update_crew_qual():
    with open('./crew_seniority_update.csv') as csvFile:
        data = csv.reader(csvFile, delimiter=';', quotechar='|')
        for row in data:
            crewList.append(dict({'id': row[0],'grp': row[1],'validfrom': row[2],'seniority': row[3]}))         
    

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):

    format = "%d%b%Y %H:%M:%S:%f"
    ae_tim = datetime(2023, 2, 1).strftime(format)
    tim = AbsTime(ae_tim[:15])
    print(tim)
 
    ops = list()
    for crew in crewList:
        print (crew['id'],crew['grp'],crew['validfrom'],crew['seniority'],int(tim))

    for crew in crewList:
        ops.append(fixrunner.createOp('crew_seniority', 'U', {'crew': crew['id'],
                                                            'grp': crew['grp'],
                                                            'validfrom': int(crew['validfrom']),
                                                            'seniority': int(crew['seniority']),
                                                            'validto': int(tim)}))
    return ops
 
__version__ = 'SASINC0244695'
fixit.program = 'update_crew_seniority.py (%s)' % __version__
 
main()

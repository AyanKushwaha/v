import csv
from datetime import datetime

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from carmensystems.basics.uuid import uuid
import utils.Names

'''
Usage:
    1. Read from csv file (reference SASINC0252819)
    2. Change open statements to target correct files, insert crew seniority number
    3. Update __version__
    4. Run using
        $ python insert_crew_seniority_no.py
'''
 
CrewSeniority = []
def main():
    insert_crew_seniority_no()
    fixit()
 
def insert_crew_seniority_no():
    with open('./seniority_no.csv') as csvFile:
        data = csv.reader(csvFile, delimiter=';', quotechar='|')
        for row in data:
            CrewSeniority.append(dict({'crew': row[0],'grp': row[1],'validfrom': row[2],'validto': row[3],'seniority': row[4]}))         
    

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()
    for crew in CrewSeniority:
        ops.append(fixrunner.createOp('crew_seniority', 'N', {'crew': crew['crew'],
                                                            'grp': crew['grp'],
                                                            'validfrom': int(crew['validfrom']),
                                                            'validto': int(crew['validto']),
                                                            'seniority': int(crew['seniority'])}))
    return ops
 
__version__ = 'SASINC0252819_1'
fixit.program = 'insert_crew_seniority.py (%s)' % __version__
 
main()

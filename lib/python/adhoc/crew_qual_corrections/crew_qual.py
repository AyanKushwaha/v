import csv
from datetime import datetime

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from carmensystems.basics.uuid import uuid
import utils.Names

'''
Usage:
    1. Read from csv file (reference SASINC0155169)
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
    with open('/opt/Carmen/CARMUSR/LIVEFEED/lib/python/adhoc/crew_qual_corrections/crew_qualification_corrections.csv') as csvFile:
        data = csv.reader(csvFile, delimiter=';', quotechar='|')
        for row in data:
            crewList.append(dict({'id': row[0],'qual_typ': row[1],'qual_subtype': row[2],'validfrom': row[3]}))         
    

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    date = str(datetime.now()).replace('-', '')    
    time = AbsTime(date[:14])
    print(time)
    # rate = -100

    format = "%d%b%Y %H:%M:%S:%f"
    ae_tim = datetime(2021, 1, 1).strftime(format)
    tim = AbsTime(ae_tim[:15])
    print(tim)
 
    ops = list()
    for crew in crewList:
        print crew['id'],crew['qual_typ'],crew['qual_subtype'],int(tim)

    for crew in crewList:
        ops.append(fixrunner.createOp('crew_qualification', 'U', {'crew': crew['id'],
                                                            'qual_typ': crew['qual_typ'],
                                                            'qual_subtype': crew['qual_subtype'],
                                                            'validfrom': int(crew['validfrom']),
                                                            'validto': int(tim)}))
    return ops
 
__version__ = 'SASINC0155169'
fixit.program = 'crew_qual.py (%s)' % __version__
 
main()

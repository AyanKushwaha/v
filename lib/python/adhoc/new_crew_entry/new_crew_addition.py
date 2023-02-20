import csv
from datetime import datetime

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from AbsDate import AbsDate
from carmensystems.basics.uuid import uuid
import utils.Names

newCrew = []

def main():
    fetch_crew_data()
    fixit()
 
def fetch_crew_data():
    with open('/users/tcskuyadm/repo/CARMUSR/SAS-Tracking/lib/python/adhoc/new_crew_entry/newCrewData.csv') as csvFile:
        data = csv.reader(csvFile, delimiter=';', quotechar='|')
        for row in data:
            newCrew.append(dict({'Crewid': row[0],'EmplNo': row[1],'Extperkey': row[2],'BirthCity': row[3],'BirthCountry': row[4],'EmplDate': row[5],'Base': row[6],'Rank': row[7],'PlanningGroup': row[8],'Contract': row[9],'AircraftQualification': row[10],'Name': row[11],'Forenames': row[12]}))


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    for crew in newCrew:
        temp=fixrunner.dbsearch(dc, 'crew', "id='%s'" % crew['Crewid'])
        if(temp!=[]):
            print("CREW ID ALREADY EXITS FOR CREW -->{0}".format(crew))
            continue
        else:
            if(crew['EmplDate']!=''):
                empd=crew['EmplDate']
                format = "%d%b%Y"
                strtodate =  datetime.strptime(empd, '%Y/%m/%d')
                datechg=strtodate.strftime("%d%b%Y %H:%M:%S:%f")
                employmentDate = AbsTime(datechg[:15])
                bDay = datetime(2019, 1, 1).strftime(format) 
                birthday = AbsTime(bDay[:9])
                EvalidTo = datetime(2035, 12, 31).strftime(format)
                EmploymentValidTo = AbsTime(EvalidTo[:15])
            
                if(crew['PlanningGroup']=='SVS'):
                    carrier='SVS'
                    company='SVS'
                elif(crew['PlanningGroup']=='SKN' or crew['PlanningGroup']=='SKS' or crew['PlanningGroup']=='SKD'):
                    carrier='SK'
                    company='SK'
                else:
                    print("PLANNING GROUP IS NOT CORRECT, PLEASE CHECK CREW ID-->{0}".format(crew['Crewid']))
                    continue
                
                if(crew['PlanningGroup']=='SKS' or crew['Base']=='STO'):
                    country = 'SE'
                elif(crew['PlanningGroup']=='SKD' or crew['Base']=='CPH'):
                    country = 'DK'
                elif(crew['PlanningGroup']=='SKN' or crew['Base']=='BGO' or crew['Base']=='OSL' ):
                    country = 'NO'
                else:
                    print("BASE IS MISSING, PLEASE CHECK CREW ID-->{0}".format(crew['Crewid']))
                    continue
                ops.append(fixrunner.createOp('crew', 'N', {'id': crew['Crewid'],
                                                            'empno': crew['EmplNo'],
                                                            'sex': 'F',
                                                            'birthday': int(birthday)/1440,
                                                            'name': crew['Name'],
                                                        'forenames': crew['Forenames'],
                                                        'logname': crew['Name'] +' '+ crew['Forenames'],
                                                            'bcity': crew['BirthCity'],
                                                            'bcountry': crew['BirthCountry'],
                                                            'employmentdate': int(employmentDate)/1440}))
                
                ops.append(fixrunner.createOp('crew_employment','N',{'crew':crew['Crewid'],
                                                                    'validfrom':int(employmentDate),
                                                                    'validto':int(EmploymentValidTo),
                                                                    'carrier': carrier ,
                                                                    'company': company,
                                                                    'base': crew['Base'],
                                                                    'crewrank': crew['Rank'],
                                                                    'titlerank': crew['Rank'],
                                                                    'region': crew['PlanningGroup'],
                                                                    'civicstation': crew['Base'],
                                                                    'station':crew['Base'],
                                                                    'country': country,
                                                                    'extperkey': crew['EmplNo'],
                                                                    'planning_group': crew['PlanningGroup']}))
                
                ops.append(fixrunner.createOp('crew_contract','N',{'crew':crew['Crewid'],
                                                                'validfrom': int(employmentDate),
                                                                'validto': int(EmploymentValidTo),
                                                                'contract': crew['Contract'],
                                                                'cyclestart': 0}))
                
                ops.append(fixrunner.createOp('crew_qualification','N',{'crew':crew['Crewid'],
                                                                        'qual_typ': 'ACQUAL',
                                                                        'qual_subtype': crew['AircraftQualification'],
                                                                        'validfrom': int(employmentDate),
                                                                        'validto': int(EmploymentValidTo)}))
            else:
                print("EMPLOYMENT DATE IS NOT PRESENT, PLEASE CHECK CREW ID-->{0}".format(crew['Crewid']))
                continue    
            

    return ops

__version__ = 'Run22'
fixit.program = 'new_crew_addition.py (%s)' % __version__
 
main()
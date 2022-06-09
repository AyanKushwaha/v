"""
SKCMS-2778: Add fake SAS Link Crew for testing
Note you need to update crew_user_filter for these crew to show up
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime


__version__ = '2022-01-21'


filepath = os.path.expandvars('$CARMUSR')
directory = filepath+'/data/migration/saslink/'

def val_date(date_str):
    return int(AbsTime(date_str))/24/60

birthday = val_date("23Feb1985")
employment = val_date("01Dec2021")
valid_from = int(AbsTime("01Dec2021"))
valid_to = int(AbsTime("31Dec2035"))


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()

    # Fake captain

    ops.append(fixrunner.createOp('crew', 'N', {'id': '200000',
        'empno': '200000',
        'sex': 'F',
        'birthday': birthday,
        'name': 'McCaptain',
        'forenames': 'Carla',
        'logname': 'Carla McCaptain',
        'si': 'Fake crew for Link testing',
        'bcity': 'CARACAS',
        'bcountry': 'VE',
        'employmentdate': employment}))

    ops.append(fixrunner.createOp('crew_employment', 'N', {'crew': '200000',
        'validfrom': valid_from,
        'validto': valid_to,
        'carrier': 'SVS',
        'company': 'SVS',
        'base': 'CPH',
        'crewrank': 'FC',
        'titlerank': 'FC',
        'region': 'SVS',
        'civicstation': 'CPH',
        'station': 'CPH',
        'country': 'DK',
        'extperkey': '200000',
        'planning_group': 'SVS'}))

    ops.append(fixrunner.createOp('crew_contract', 'N', {'crew': '200000',
        'validfrom': valid_from,
        'validto': valid_to,
        'contract': 'V0001',
        'cyclestart': 0}))

    ops.append(fixrunner.createOp('crew_qualification', 'N', {'crew': '200000',
        'qual_typ': 'ACQUAL',
        'qual_subtype': 'EJ',
        'validfrom': valid_from,
        'validto': valid_to}))


    # Fake first officer

    ops.append(fixrunner.createOp('crew', 'N', {'id': '200001',
        'empno': '200001',
        'sex': 'M',
        'birthday': birthday,
        'name': 'McOfficer',
        'forenames': 'Otto',
        'logname': 'Otto McOfficer',
        'si': 'Fake crew for Link testing',
        'bcity': 'NAUMBURG',
        'bcountry': 'DE',
        'employmentdate': employment}))

    ops.append(fixrunner.createOp('crew_employment', 'N', {'crew': '200001',
        'validfrom': employment,
        'validto': valid_to,
        'carrier': 'SVS',
        'company': 'SVS',
        'base': 'CPH',
        'crewrank': 'FP',
        'titlerank': 'FP',
        'region': 'SVS',
        'civicstation': 'CPH',
        'station': 'CPH',
        'country': 'DK',
        'extperkey': '200001',
        'planning_group': 'SVS'}))

    ops.append(fixrunner.createOp('crew_contract', 'N', {'crew': '200001',
        'validfrom': employment,
        'validto': valid_to,
        'contract': 'V0001',
        'cyclestart': 0}))

    ops.append(fixrunner.createOp('crew_qualification', 'N', {'crew': '200001',
        'qual_typ': 'ACQUAL',
        'qual_subtype': 'EJ',
        'validfrom': employment,
        'validto': valid_to}))


    # Fake purser

    ops.append(fixrunner.createOp('crew', 'N', {'id': '200002',
        'empno': '200002',
        'sex': 'F',
        'birthday': birthday,
        'name': 'McPurser',
        'forenames': 'Petronella',
        'logname': 'Petronella McPurser',
        'si': 'Fake crew for Link testing',
        'bcity': 'PARTILLE',
        'bcountry': 'SE',
        'employmentdate': employment}))

    ops.append(fixrunner.createOp('crew_employment', 'N', {'crew': '200002',
        'validfrom': employment,
        'validto': valid_to,
        'carrier': 'SVS',
        'company': 'SVS',
        'base': 'CPH',
        'crewrank': 'AP',
        'titlerank': 'AP',
        'region': 'SVS',
        'civicstation': 'CPH',
        'station': 'CPH',
        'country': 'DK',
        'extperkey': '200002',
        'planning_group': 'SVS'}))
    
    ops.append(fixrunner.createOp('crew_contract', 'N', {'crew': '200002',
        'validfrom': employment,
        'validto': valid_to,
        'contract': 'V0001',
        'cyclestart': 0}))

    ops.append(fixrunner.createOp('crew_qualification', 'N', {'crew': '200002',
        'qual_typ': 'ACQUAL',
        'qual_subtype': 'EJ',
        'validfrom': employment,
        'validto': valid_to}))


    # Fake cabin crew

    ops.append(fixrunner.createOp('crew', 'N', {'id': '200003',
        'empno': '200003',
        'sex': 'M',
        'birthday': birthday,
        'name': 'McHost',
        'forenames': 'Hans',
        'logname': 'Hans McHost',
        'si': 'Fake crew for Link testing',
        'bcity': 'ODENSE',
        'bcountry': 'DK',
        'employmentdate': employment}))

    ops.append(fixrunner.createOp('crew_employment', 'N', {'crew': '200003',
        'validfrom': employment,
        'validto': valid_to,
        'carrier': 'SVS',
        'company': 'SVS',
        'base': 'CPH',
        'crewrank': 'AH',
        'titlerank': 'AH',
        'region': 'SVS',
        'civicstation': 'CPH',
        'station': 'CPH',
        'country': 'DK',
        'extperkey': '200003',
        'planning_group': 'SVS'}))

    ops.append(fixrunner.createOp('crew_contract', 'N', {'crew': '200003',
        'validfrom': employment,
        'validto': valid_to,
        'contract': 'V0001',
        'cyclestart': 0}))

    ops.append(fixrunner.createOp('crew_qualification', 'N', {'crew': '200003',
        'qual_typ': 'ACQUAL',
        'qual_subtype': 'EJ',
        'validfrom': employment,
        'validto': valid_to}))
    
    return ops



fixit.program = 'add_fake_sl_Crew.py (%s)' % __version__
if __name__ == '__main__':
    fixit()

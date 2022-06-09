#!/bin/env python


"""
SKCMS-1779 Airport qualification needs to be depending on aircraft qual
Sprint: SAS68
"""


import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
from operator import itemgetter
from AbsTime import AbsTime

__version__ = '2018-05-28'

START_TIME = AbsTime("1JUN2018")

@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    crew_qualification = migrate_table.MigrateTable(dc, fixrunner, 'crew_qualification', ['crew', 'qual_typ', 'qual_subtype', 'validfrom', 'validto', 'lvl', 'si', 'acstring'], 4)
    crew_qualification.load(None)

    crew_t = migrate_table.MigrateTable(dc, fixrunner, 'crew', ['id', 'empno', 'sex', 'birthday', 'title', 'name', 'forenames', 'logname', 'si', 'maincat', 'bcity', 'bstate', 'bcountry', 'alias', 'employmentdate', 'retirementdate'], 1)
    crew_t.load(None)

    big_data = {}
    crew_qual_acquals = []
    crew_qualifications = []

    get_apt_quals(big_data, crew_qualification)

    ignore_retired_crew(big_data, crew_t)

    get_ac_quals(big_data, crew_qualification)

    for crew in big_data:
#        print crew
        crew_data = big_data[crew]

        get_ac_apt_matches(crew_data)

        cqa, cq = get_ac_apt_qual_ops(crew_data)
        crew_qual_acquals = crew_qual_acquals + cqa
        crew_qualifications = crew_qualifications + cq
#        print_ac_quals(crew_data)

#        print "==========================="


    for crew_qual_acqual in crew_qual_acquals:
        ops.append(fixrunner.createOp('crew_qual_acqual', 'N', crew_qual_acqual))
    for crew_qualification in crew_qualifications:
        ops.append(fixrunner.createOp('crew_qualification', 'D', crew_qualification))
    return ops


def get_apt_quals(big_data, crew_qualification):
    """Get current airport qualifications from the crew_qualification table"""
    apt_quals = crew_qualification.get_matching_rows({'qual_typ' : 'AIRPORT'})
    for apt_qual in sorted(apt_quals, key=itemgetter('validfrom')):
        if AbsTime(apt_qual['validto']) > START_TIME:
            crew = apt_qual['crew']
            if not crew in big_data:
                big_data[crew] = {'acs' : [],
                                  'apts' : [],
                                  'info' : None}
            big_data[crew]['apts'].append(apt_qual)
#        else:
#            print "Ignoring apt qual: %s %s %s - %s" % (apt_qual['crew'], apt_qual['qual_subtype'], AbsTime(apt_qual['validfrom']), AbsTime(apt_qual['validto']))


def ignore_retired_crew(big_data, crew_t):
    """Remove retired crew from qualification data"""
    for crew_item in crew_t.get_matching_rows({}):
        crew = crew_item['id']
        if crew in big_data:
            if crew_item['retirementdate'] == None or AbsTime(crew_item['retirementdate'] * 60 * 24) > START_TIME:
                big_data[crew]['info'] = crew_item
            else:
                del big_data[crew] # Ignore retired crew


def get_ac_quals(big_data, crew_qualification):
    """Get all aircrew qualifications for crew with current airport qualifications from the crew_qualification table"""
    ac_quals = crew_qualification.get_matching_rows({'qual_typ' : 'ACQUAL'})
    for ac_qual in sorted(ac_quals, key=itemgetter('validfrom')):
        crew = ac_qual['crew']
        if crew in big_data:
            big_data[crew]['acs'].append(ac_qual)


def map_ac_name(ac_name):
    """Map A3 and A4 qualifications to a common A3A4 qualification"""
    if ac_name in ['A3', 'A4']:
        new_ac_name = 'A3A4'
    else:
        new_ac_name = ac_name
    return new_ac_name


def get_ac_apt_matches(crew_data):
    """Calculate which aircraft quals match which airport qualifications"""
    for apt_qual in crew_data['apts']:
        crew = apt_qual['crew']
        apt_name = apt_qual['qual_subtype']
        apt_validfrom = apt_qual['validfrom']
        apt_validto = apt_qual['validto']
        match = set()
        potential_match = set()
        for ac_qual in crew_data['acs']:
            ac_name = ac_qual['qual_subtype']
            new_ac_name = map_ac_name(ac_name)
            ac_validfrom = ac_qual['validfrom']
            ac_validto = ac_qual['validto']
            if apt_validfrom >= ac_validfrom and apt_validfrom < ac_validto:
                if AbsTime(ac_validto) > START_TIME:
                    match.add(new_ac_name)
                else:
                    potential_match.add(new_ac_name)
            elif ac_validfrom > apt_validfrom and ac_validfrom < apt_validto and AbsTime(ac_validto) > START_TIME:
                if new_ac_name in potential_match:
                    match.add(new_ac_name)
                    potential_match.remove(new_ac_name)
                elif new_ac_name not in match:
                    print "ERROR: AC qual begins within apt qual: %s %s %s - %s vs %s %s - %s" % (crew, ac_name, AbsTime(ac_validfrom), AbsTime(ac_validto), apt_name, AbsTime(apt_validfrom), AbsTime(apt_validto))
        apt_qual['match'] = match


def get_ac_apt_qual_ops(crew_data):
    """Calculate db operations to create / delete apt qualifications"""
    apt_qual_list = crew_data['apts']
    crew_qual_acqual = []
    crew_qualification = []
    for qual in apt_qual_list:
        crew = qual['crew']
        match = qual['match']
#        print 'old qual ', '  ', qual['qual_subtype'], AbsTime(qual['validfrom']), AbsTime(qual['validto'])
        if len(match) > 1:
            print "ERROR: multiple AC quals for airport: %s" % (match)
        elif len(match) == 0:
            print "ERROR: no current AC qual for airport qual: %s %s %s - %s" % (crew, qual['qual_subtype'], AbsTime(qual['validfrom']), AbsTime(qual['validto']))
        for ac_type in match:
            new_qual = {'crew' : qual['crew'],
                        'qual_typ' : 'ACQUAL',
                        'qual_subtype' : ac_type,
                        'acqqual_typ' : qual['qual_typ'],
                        'acqqual_subtype' : qual['qual_subtype'],
                        'validfrom' : qual['validfrom'],
                        'validto' : qual['validto'],
                        'lvl' : qual['lvl'],
                        'si' : qual['si']}
#            print ' new qual', ac_type, qual['qual_subtype'], AbsTime(qual['validfrom']), AbsTime(qual['validto'])
            crew_qual_acqual.append(new_qual)
            old_qual = {'crew' : qual['crew'],
                        'qual_typ' : qual['qual_typ'],
                        'qual_subtype' : qual['qual_subtype'],
                        'validfrom' : qual['validfrom']}

            crew_qualification.append(old_qual)

#    print '--------------------------'
    return (crew_qual_acqual, crew_qualification)


def print_ac_quals(crew_data):
    """Print aircraft qualifications for one crew"""
    ac_qual_list = crew_data['acs']
    for qual in ac_qual_list:
        print qual['qual_subtype'], AbsTime(qual['validfrom']), AbsTime(qual['validto'])

    print '--------------------------'


fixit.program = 'migrate_apt_quals.py (%s)' % __version__
if __name__ == '__main__':
    fixit()

#!/bin/env python


"""
SASCMS-3997 CCR TR FC New functionality for legality check on Course content

- New Course Types in section Training Type in Training need
- New course subtypes
- New set of rank types for course content
- New set of ac types for course content

"""

import adhoc.fixrunner as fixrunner


__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    # Add new course types to table course_type
    coursetypes = ['REFRESH 3-6',
                   'REFRESH 6-12',
                   'REFRESH 12-18',
                   'REFRESH 18-36',
                   'REFRESH 36-60',
                   'REFRESH 5 years plus',
                   'CONV TYPERATING',
                   'UPGRADE Type Rating',
                   'UPGRADE right to left',
                   'CCQ-A3A4',
                   'OCC',
                   'Commander Course seminar']

    for type in coursetypes:
        if len(type)<=25:
            if len(fixrunner.dbsearch(dc, 'course_type', "id='%s'" % type)) == 0:
                ops.append(fixrunner.createop('course_type', 'N', {'id': type}))
            else:
                print "Row %s already exists" % type
        else:
            print "Row type: " + type + " contains >25 characters."


    # Add default course subtype to (new) table course_subtype
    if len(fixrunner.dbsearch(dc, 'course_subtype', "id='NONE'")) == 0:
        ops.append(fixrunner.createop('course_subtype', 'N', {'id': 'NONE'}))
    else:
        print "Row NONE already exists"


    # Add elements to course_rank_set
    ranks = ['ALL',
             'FC',
             'FP']

    for rank in ranks:
        if len(fixrunner.dbsearch(dc, 'course_rank_set', "id='%s'" % rank)) == 0:
            ops.append(fixrunner.createop('course_rank_set', 'N', {'id': rank}))
        else:
            print "Row %s already exists" % rank


    # Add element to agreement_validity table
    validfrom = 9740 #to_dave_date(datetime.datetime(2012, 9, 1))
    validto = 18261 #to_dave_date(datetime.datetime(2035, 12, 31))
    
    agreement_validity = {'id' : 'trng_course_activity_checks',
                          'validfrom' : validfrom,
                          'validto' : validto,
                          'si' : 'FC legality on course content'}

    if len(fixrunner.dbsearch(dc, 'agreement_validity', "id='%s'" % agreement_validity['id'])) == 0:
        ops.append(fixrunner.createop('agreement_validity', 'N', agreement_validity))
    else:
        print "Row %s already exists" % agreement_validity['id']


    # Add elements to course_ac_qual_set
    acquals = ['ALL','36', '37', '38', 'A2', 'A3', 'A4', 'CJ', 'M8']

    for type in acquals:
        if len(fixrunner.dbsearch(dc, 'course_ac_qual_set', "id='%s'" % type)) == 0:
            ops.append(fixrunner.createop('course_ac_qual_set', 'N', {'id': type}))
        else:
            print "Row %s already exists" % type


    # Add elements to course_actype_set 
#   actypes = ['ALL',
#               '100', '141', '142', '143', '146', '14W', '310', '318', '319', '320', '321', '322', '32B', '32F', '330',
#               '332', '333', '33S', '340', '343', '34K', '34S', '380', '717', '733', '734', '735', '736', '737', '738',
#               '739','73A', '73B', '73C', '73D', '73E', '73F', '73G', '73H', '73I', '73J', '73K', '73L', '73M', '73N',
#               '73O', '73P','73R', '73S', '73T', '73U', '73V', '73W', '73Z', '752', '753', '75A', '75W', '763', '76W',
#               'A32', 'A33', 'A81','AR1', 'AR7', 'AR8', 'AR9', 'ARB', 'ARC', 'AT3', 'AT4', 'AT5', 'AT7', 'AT8', 'ATL',
#               'ATP', 'ATR', 'BEC', 'BEH','CNJ', 'CR2', 'CR9', 'CRJ', 'D28', 'D38', 'DH1', 'DH3', 'DH4', 'DH8', 'DHQ',
#               'DHS', 'E75', 'E90', 'E95', 'ER3','ER4', 'F50', 'F5H', 'F5N', 'F5V', 'F70', 'FFF', 'J31', 'J32', 'LCH',
#               'M80', 'M81', 'M82', 'M83', 'M87', 'M8A','M8C', 'M8D', 'M8E', 'M8M', 'M8S', 'M8T', 'M8Y', 'M90', 'M93',
#               'M9T', 'RFS', 'S20', 'S92', 'SF3', 'SU1', 'SU7','SU9', 'T20']
#
#    for type in actypes:
#        if len(fixrunner.dbsearch(dc, 'course_actype_set', "id='%s'" % type)) == 0:
#            ops.append(fixrunner.createop('course_actype_set', 'N', {'id': type}))
#        else:
#            print "Row %s already exists" % type

    return ops


fixit.program = 'sascms-3997.py (%s)' % __version__


if __name__ == '__main__':
    fixit()

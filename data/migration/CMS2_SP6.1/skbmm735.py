#!/bin/env python


"""
InterbidsMigration. Populate bid_award_type_bid_type table with data.

"""

import adhoc.fixrunner as fixrunner


__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []


    bid_award_type_bid_types = [('TRANSITION', 'CAREER','C', 'CCAC'),
                                ('TRANSITION', 'CAREER','F', 'ATPL_CONFIRMATION'), 
                                ('TRANSITION', 'CAREER','F', 'BASE'),
                                ('TRANSITION', 'CAREER','F', 'FCAC'),
                                ('TRANSITION', 'CAREER','F', 'NORTHNORWAY'),
                                ('TRANSITION', 'CAREER','F', 'FOAC'),
                                ('ANNUAL_LEAVE', 'LEAVE', 'C', 'EXTRAVACATION'),
                                ('ANNUAL_LEAVE', 'LEAVE', 'C', 'INROTATION'),
                                ('ANNUAL_LEAVE', 'LEAVE', 'C', 'JOIN'),
                                ('ANNUAL_LEAVE', 'LEAVE', 'C', 'JOINVACATION'),
                                ('ANNUAL_LEAVE', 'LEAVE', 'C', 'NOVACATION'),
                                ('ANNUAL_LEAVE', 'LEAVE', 'C', 'POSTPONE'),
                                ('ANNUAL_LEAVE', 'LEAVE', 'C', 'TRANSFER'),
                                ('ANNUAL_LEAVE', 'LEAVE', 'C', 'VACATION'),
                                ('ANNUAL_LEAVE', 'LEAVE', 'F', 'EXTRAVACATION'),
                                ('ANNUAL_LEAVE', 'LEAVE', 'F', 'INROTATION'),
                                ('ANNUAL_LEAVE', 'LEAVE', 'F', 'JOIN'),
                                ('ANNUAL_LEAVE', 'LEAVE', 'F', 'JOINVACATION'),
                                ('ANNUAL_LEAVE', 'LEAVE', 'F', 'NOVACATION'),
                                ('ANNUAL_LEAVE', 'LEAVE', 'F', 'POSTPONE'),
                                ('ANNUAL_LEAVE', 'LEAVE', 'F', 'TRANSFER'),
                                ('ANNUAL_LEAVE', 'LEAVE', 'F', 'VACATION')]
                                

    for awardingtype_id, awardingtype_bid_cat, awardingtype_crew_cat, bidtype in bid_award_type_bid_types:
        if len(fixrunner.dbsearch(dc, 'bid_award_type_bid_type', "awardingtype_id='%s' AND awardingtype_cat_id='%s' AND awardingtype_cat_cat='%s' AND bidtype='%s'" % (awardingtype_id, awardingtype_bid_cat, awardingtype_crew_cat, bidtype))) == 0:
            ops.append(fixrunner.createop('bid_award_type_bid_type', 'N', {'awardingtype_id' : awardingtype_id, 
                                                                            'awardingtype_cat_id' : awardingtype_bid_cat, 
                                                                            'awardingtype_cat_cat' : awardingtype_crew_cat, 
                                                                            'bidtype' : bidtype}))
        else:
            print "%s %s %s %s already exists in bid_award_type_bid_type" % (awardingtype_id, awardingtype_bid_cat, awardingtype_crew_cat, bidtype)

    return ops


fixit.program = 'skbmm735.py (%s)' % __version__


if __name__ == '__main__':
    fixit()

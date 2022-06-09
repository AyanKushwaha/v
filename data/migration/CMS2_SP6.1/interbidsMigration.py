#!/bin/env python


"""
InterbidsMigration. Populate new SP6 leave and TRANSITION bidding tables with data.


"""

import adhoc.fixrunner as fixrunner


__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    bid_actions = ['UPDATE', 'CREATE', 'DELETE']

    bid_awarding_cats = [('LEAVE', 'F'),
                         ('CAREER', 'F'),
                         ('LEAVE', 'C'),
                         ('CAREER', 'C')]

    bid_statuses = [('AWARDED','NULL'),
                  ('PENDING','NULL'),
                  ('REJECTED','NULL')]

    bid_groups = [('TRANSITION_FOAC','true'),
                  ('TRANSITION_FCAC','true'),
                  ('TRANSITION_CCAC','true'),
                  ('TRANSITION_NN','true'),
                  ('TRANSITION_BASE','true'),
                  ('TRANSITION_ATPL','true'),
                  ('VACATION','true')]

    crew_qualification_set_data = [('BIDS_FOAC_QUAL', 'FC CJ'),
                                   ('BIDS_FOAC_QUAL','FP A340/330'),
                                   ('BIDS_FOAC_QUAL','FP A321'),
                                   ('BIDS_FOAC_QUAL','FP 737'),
                                   ('BIDS_FCAC_QUAL','A321'),
                                   ('BIDS_FCAC_QUAL','737'),
                                   ('BIDS_FCAC_QUAL','A340/330'),
                                   ('BIDS_CCAC_QUAL','CJ'),
                                   ('BIDS_CCAC_QUAL','AL'),
                                   ('BIDS_CCAC_QUAL','A2')]

    bid_group_bid_types = [('TRANSITION_FCAC','FCAC'),
                           ('TRANSITION_ATPL','ATPL_CONFIRMATION'),
                           ('TRANSITION_FOAC','FOAC'),
                           ('TRANSITION_CCAC','CCAC'),
                           ('TRANSITION_NN','NORTHNORWAY'),
                           ('TRANSITION_BASE','BASE'),
                           ('VACATION','POSTPONE'),
                           ('VACATION','JOINVACATION'),
                           ('VACATION','VACATION'),
                           ('VACATION','TRANSFER'),
                           ('VACATION','NOVACATION'),
                           ('VACATION','EXTRAVACATION'),
                           ('VACATION','JOIN')] 

    bid_awarding_types = [('ANNUAL_LEAVE','LEAVE', 'C','NULL'),
                          ('ANNUAL_LEAVE','LEAVE', 'F','NULL'),
                          ('TRANSITION','CAREER', 'C','NULL'),
                          ('TRANSITION','CAREER', 'F', 'NULL')]

    bid_types = [('ATPL_CONFIRMATION'),
                 ('BASE'),
                 ('CCAC'),
                 ('FCAC'),
                 ('FOAC'),
                 ('NORTHNORWAY'),
                 ('EXTRAVACATION'),
                 ('INROTATION'),
                 ('JOIN'),
                 ('JOINVACATION'),
                 ('NOVACATION'),
                 ('POSTPONE'),
                 ('TRANSFER'),
                 ('VACATION')]


    for typ, subtyp in crew_qualification_set_data:
        if len(fixrunner.dbsearch(dc, 'crew_qualification_set', "typ='%s' AND subtype='%s'" % (typ, subtyp))) == 0:
            ops.append(fixrunner.createop('crew_qualification_set', 'N', {'typ' : typ, 'subtype': subtyp}))
        else:
            print "Crew qualification %s %s already exists" % (typ, subtyp)

    for bid_aw_cat, crew_cat in bid_awarding_cats:
        if len(fixrunner.dbsearch(dc, 'bid_awarding_cat', "id='%s' AND cat='%s'" % (bid_aw_cat, crew_cat))) == 0:
            ops.append(fixrunner.createop('bid_awarding_cat', 'N', {'id' : bid_aw_cat, 'cat': crew_cat, 'descr': ""}))
        else:
            print "Bid awarding cat  %s already exists" % bid_aw_cat

    for bid_st, descr in bid_statuses:
        if len(fixrunner.dbsearch(dc, 'bid_status', "id='%s'" % bid_st)) == 0:
            ops.append(fixrunner.createop('bid_status', 'N', {'id' : bid_st, 'descr' : descr}))
        else:
            print "Bid status  %s already exists" % bid_st

    for bid_grp, b in bid_groups:
        if len(fixrunner.dbsearch(dc, 'bid_group', "id='%s'" % bid_grp)) == 0:
            ops.append(fixrunner.createop('bid_group', 'N', {'id' : bid_grp, 'issorted' : b}))
        else:
            print "Bid group  %s already exists" % bid_grp

    for bid_grp, bid_typ in bid_group_bid_types:
        if len(fixrunner.dbsearch(dc, 'bid_group_bid_type', "bidgroup='%s' AND bidtype='%s'" % (bid_grp,bid_typ))) == 0:
            ops.append(fixrunner.createop('bid_group_bid_type', 'N', {'bidgroup' : bid_grp, 'bidtype' : bid_typ}))
        else:
            print "Bid type %s already exists for bid group %s" % (bid_typ, bid_grp)

    for id, bid_cat, crew_cat, descr in bid_awarding_types:
        if len(fixrunner.dbsearch(dc, 'bid_awarding_type', "id='%s' AND cat_id='%s' AND cat_cat='%s'" % (id, bid_cat, crew_cat))) == 0:
            ops.append(fixrunner.createop('bid_awarding_type', 'N', {'id' : id, 'cat_id' : bid_cat, 'cat_cat' : crew_cat, 'descr' : descr}))
        else:
            print "Bid awarding %s already exists for category %s %s" % (id, bid_cat, crew_cat)

    for id in bid_types:
        if len(fixrunner.dbsearch(dc, 'bid_type', "id='%s'" % id)) == 0:
            ops.append(fixrunner.createop('bid_type', 'N', {'id' : id}))
        else:
            print "%s already exists" % id

    for bid_ac in bid_actions:
        if len(fixrunner.dbsearch(dc, 'bid_action', "id='%s'" % bid_ac)) == 0:
            ops.append(fixrunner.createop('bid_action', 'N', {'id' : bid_ac}))
        else:
            print "%s already exists" % bid_ac

    return ops


fixit.program = 'interbidsMigration.py (%s)' % __version__


if __name__ == '__main__':
    fixit()

#!/bin/env python


"""
SASCMS-5966 - removing old bid entries, removing old bid groups and adding a new bid group.


"""

import adhoc.fixrunner as fixrunner


__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    
    ops = []

    #removing old bid entries
    for bid_general_entry in fixrunner.dbsearch(dc, 'bid_general', "bidtype='BASE' or bidtype='FCAC' or bidtype='FOAC' or bidtype='NORTHNORWAY'"):
        for bid_transition_entry in fixrunner.dbsearch(dc, 'bid_transition', "general_id='%s' AND general_crew='%s'" % (bid_general_entry['id'], bid_general_entry['crew'])):
            ops.append(fixrunner.createop('bid_transition', 'D', bid_transition_entry))
        ops.append(fixrunner.createop('bid_general', 'D', bid_general_entry))
        
       
    #removing old bid groups
    for crew_qualification_set_entry in fixrunner.dbsearch(dc, 'crew_qualification_set', "typ='BIDS_FCAC_QUAL' or typ='BIDS_FOAC_QUAL'"):
        ops.append(fixrunner.createop('crew_qualification_set', 'D', crew_qualification_set_entry))
        
    for bid_group_bid_awarding_entry in fixrunner.dbsearch(dc, 'bid_group_bid_awarding', "bidgroup='TRANSITION_BASE' or bidgroup='TRANSITION_FCAC' or bidgroup='TRANSITION_FOAC' or bidgroup='TRANSITION_NN'"):
        ops.append(fixrunner.createop('bid_group_bid_awarding', 'D', bid_group_bid_awarding_entry))
    
    for bid_award_type_bid_type_entry in fixrunner.dbsearch(dc, 'bid_award_type_bid_type', "bidtype='BASE' or bidtype='FCAC' or bidtype='FOAC' or bidtype='NORTHNORWAY'"):
        ops.append(fixrunner.createop('bid_award_type_bid_type', 'D', bid_award_type_bid_type_entry)) 
           
    for bid_group_bid_type_entry in fixrunner.dbsearch(dc, 'bid_group_bid_type', "bidgroup='TRANSITION_BASE' or bidgroup='TRANSITION_FCAC' or bidgroup='TRANSITION_FOAC' or bidgroup='TRANSITION_NN'"):
        ops.append(fixrunner.createop('bid_group_bid_type', 'D', bid_group_bid_type_entry)) 
         
    for bid_type_entry in fixrunner.dbsearch(dc, 'bid_type', "id='BASE' or id='FCAC' or id='FOAC' or id='NORTHNORWAY'"):
        ops.append(fixrunner.createop('bid_type', 'D', bid_type_entry))    
        
    for bid_group_entry in fixrunner.dbsearch(dc, 'bid_group', "id='TRANSITION_BASE' or id='TRANSITION_FCAC' or id='TRANSITION_FOAC' or id='TRANSITION_NN'"):
        ops.append(fixrunner.createop('bid_group', 'D', bid_group_entry))
        
    
        
    #adding new bid_groups
    bid_groups = [('TRANSITION_FBID','true'),]
    
    bid_types = [('FBID'),]
    
    bid_group_bid_types = [('TRANSITION_FBID','FBID'),]
    
    bid_award_type_bid_types = [('TRANSITION', 'CAREER','F', 'FBID'),]
    
    crew_qualification_set_data = [('BIDS_FBID_QUAL', 'FC LH'),
                                   ('BIDS_FBID_QUAL', 'FC Main CPH'),
                                   ('BIDS_FBID_QUAL', 'FC Main OSL'),
                                   ('BIDS_FBID_QUAL', 'FC Main STO'),
                                   ('BIDS_FBID_QUAL', 'FC RC CPH'),
                                   ('BIDS_FBID_QUAL', 'FO LH'),
                                   ('BIDS_FBID_QUAL', 'FO Main CPH'),
                                   ('BIDS_FBID_QUAL', 'FO Main OSL'),
                                   ('BIDS_FBID_QUAL', 'FO Main STO')]
                  
    for bid_grp, b in bid_groups:
        if len(fixrunner.dbsearch(dc, 'bid_group', "id='%s'" % bid_grp)) == 0:
            ops.append(fixrunner.createop('bid_group', 'N', {'id' : bid_grp, 'issorted' : b}))
        else:
            print "Bid group  %s already exists" % bid_grp
    
    
    for id in bid_types:
        if len(fixrunner.dbsearch(dc, 'bid_type', "id='%s'" % id)) == 0:
            ops.append(fixrunner.createop('bid_type', 'N', {'id' : id}))
        else:
            print "%s already exists" % id
            
            
    for bid_grp, bid_typ in bid_group_bid_types:
        if len(fixrunner.dbsearch(dc, 'bid_group_bid_type', "bidgroup='%s' AND bidtype='%s'" % (bid_grp,bid_typ))) == 0:
            ops.append(fixrunner.createop('bid_group_bid_type', 'N', {'bidgroup' : bid_grp, 'bidtype' : bid_typ}))
        else:
            print "Bid type %s already exists for bid group %s" % (bid_typ, bid_grp)
            
            
    for awardingtype_id, awardingtype_bid_cat, awardingtype_crew_cat, bidtype in bid_award_type_bid_types:
        if len(fixrunner.dbsearch(dc, 'bid_award_type_bid_type', "awardingtype_id='%s' AND awardingtype_cat_id='%s' AND awardingtype_cat_cat='%s' AND bidtype='%s'" % (awardingtype_id, awardingtype_bid_cat, awardingtype_crew_cat, bidtype))) == 0:
            ops.append(fixrunner.createop('bid_award_type_bid_type', 'N', {'awardingtype_id' : awardingtype_id, 
                                                                            'awardingtype_cat_id' : awardingtype_bid_cat, 
                                                                            'awardingtype_cat_cat' : awardingtype_crew_cat, 
                                                                            'bidtype' : bidtype}))
        else:
            print "%s %s %s %s already exists in bid_award_type_bid_type" % (awardingtype_id, awardingtype_bid_cat, awardingtype_crew_cat, bidtype)
            
            
    for typ, subtyp in crew_qualification_set_data:
        if len(fixrunner.dbsearch(dc, 'crew_qualification_set', "typ='%s' AND subtype='%s'" % (typ, subtyp))) == 0:
            ops.append(fixrunner.createop('crew_qualification_set', 'N', {'typ' : typ, 'subtype': subtyp}))
        else:
            print "Crew qualification %s %s already exists" % (typ, subtyp)


    return ops


fixit.program = 'sascms-5966.py (%s)' % __version__


if __name__ == '__main__':
    fixit()

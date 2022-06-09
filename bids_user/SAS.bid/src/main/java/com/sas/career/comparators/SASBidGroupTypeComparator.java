package com.sas.career.comparators;

import java.util.Comparator;
import java.util.HashMap;

import com.jeppesen.carmen.crewweb.backendfacade.customization.api.BidGroupType;

public class SASBidGroupTypeComparator implements Comparator<BidGroupType> {
	
	private static final HashMap<String, Integer> bidGroupOrder = new HashMap<String, Integer>();
	
	public SASBidGroupTypeComparator() {
		bidGroupOrder.put("transition_fbid", 	0);
		bidGroupOrder.put("transition_fcac", 	1);
		bidGroupOrder.put("transition_foac", 	2);
		bidGroupOrder.put("transition_ccac", 	3);
		bidGroupOrder.put("transition_base", 	4);
		bidGroupOrder.put("transition_atpl", 	5);
		bidGroupOrder.put("transition_nn", 		6);
	}

    @Override
    public int compare(BidGroupType o1, BidGroupType o2) {
    	if (hasValueForBidGroupId(o1) && hasValueForBidGroupId(o2)) {
    		return getValueForBidGroupId(o1).compareTo(getValueForBidGroupId(o2));
    	} else {
    		return o1.getId().compareTo(o2.getId());
    	}
    }
    
    private Integer getValueForBidGroupId(BidGroupType bgt) {
    	return bidGroupOrder.get(bgt.getId().toLowerCase());
    }
    
    private boolean hasValueForBidGroupId(BidGroupType bgt) {
    	return bidGroupOrder.containsKey(bgt.getId().toLowerCase());
    }
}

package com.sas.vacation.comparators;

import java.util.Comparator;
import java.util.HashMap;

import com.jeppesen.carmen.crewweb.backendfacade.customization.api.BidGroupType;

public class SASBidGroupTypeComparator implements Comparator<BidGroupType> {
	
	private static final HashMap<String, Integer> bidGroupOrder = new HashMap<String, Integer>();
	
	public SASBidGroupTypeComparator() {
		bidGroupOrder.put("vacation", 		1);
		bidGroupOrder.put("joinvacation", 	2);
		bidGroupOrder.put("transfer", 		3);
		bidGroupOrder.put("novacation", 	4);
		bidGroupOrder.put("postpone", 		5);
		bidGroupOrder.put("extravacation", 	6);
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

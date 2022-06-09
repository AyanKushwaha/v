package com.sas.interbids.exporter;

import java.util.ArrayList;
import java.util.List;

import com.jeppesen.carmen.crewweb.framework.bo.User;
import com.jeppesen.carmen.crewweb.interbids.bo.Bid;
import com.jeppesen.carmen.crewweb.interbids.bo.BidGroup;
import com.jeppesen.carmen.crewweb.interbids.bo.impl.BidGroupImpl;
import com.jeppesen.carmen.crewweb.interbids.business.export.BidGroupExportFilter;
import com.sas.interbids.base.SasConstants;

/**
 * Class for bid group export that merges both flights and preferences bid groups 
 * into one bid group to avoid multiple "NrOfBids" lines in the export file. 
 * 
 */

public class BidGroupExportMerger implements BidGroupExportFilter {
	/**
	 * {@inheritDoc}
	 */
	@Override
	public List<BidGroup> filter(User user, List<BidGroup> bidGroups) {
		List<BidGroup> result = new ArrayList<BidGroup>();
		List<Bid> bids = new ArrayList<Bid>();
		BidGroup lastBidGroup = new BidGroupImpl();


		for (BidGroup bidGroup : bidGroups) {
			 String category = bidGroup.getCategory();

			if (SasConstants.BID_CATEGORY_CURRENT.equals(category) || SasConstants.BID_CATEGORY_PREFERENCE.equals(category)) {
				lastBidGroup = bidGroup;

				for (Bid bid : bidGroup.getAllBids()) {
					bids.add(bid);
				}
			}
		}
		lastBidGroup.setBids(bids);
		result.add(lastBidGroup);
		return result;
	}
}

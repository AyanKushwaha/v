package com.sas.interbids.formatter;

import static com.jeppesen.carmen.crewweb.interbids.customization.api.BidData.BID_PROPERTY_PREFIX;
import static com.jeppesen.carmen.crewweb.interbids.customization.api.BidData.BID_TRANSIENT_PREFIX;

import com.jeppesen.carmen.crewweb.framework.business.DataSourceLookupHelper;
import com.jeppesen.carmen.crewweb.framework.context.aware.DataSourceLookupHelperAware;
import com.jeppesen.carmen.crewweb.interbids.customization.api.MutableBidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.TransientBidDataInterface;
import com.sas.interbids.formatter.helper.PriorityStringLookupHelper;

/**
 * Converts bid data to readable form for use in transient column fields.
 */
public class DynamicBidDataHandler implements TransientBidDataInterface,
		DataSourceLookupHelperAware {

	private DataSourceLookupHelper dataSourceLookupHelper;

	@Override
	public void applyTransientPropertyToBidData(MutableBidData bidData) {
		String priorityValue = bidData.get(BID_PROPERTY_PREFIX
				+ "priority.priority");

		PriorityStringLookupHelper priorityStringLookupHelper = new PriorityStringLookupHelper(
				dataSourceLookupHelper);

		String priorityName = priorityStringLookupHelper
				.getPriorityString(priorityValue);

		bidData.set(BID_TRANSIENT_PREFIX + "priorityName", priorityName);
	}

	@Override
	public void setDataSourceLookupHelper(
			DataSourceLookupHelper dataSourceLookupHelper) {
		this.dataSourceLookupHelper = dataSourceLookupHelper;
	}
}

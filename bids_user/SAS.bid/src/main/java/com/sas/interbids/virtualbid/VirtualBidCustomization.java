package com.sas.interbids.virtualbid;

import com.jeppesen.carmen.crewweb.backendfacade.bo.ImmutableTrip;
import com.jeppesen.carmen.crewweb.framework.business.DataSourceLookupHelper;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserCustomizationAPI;
import com.jeppesen.carmen.crewweb.framework.context.aware.DataSourceLookupHelperAware;
import com.jeppesen.carmen.crewweb.framework.context.aware.UserCustomizationAPIAware;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.MutableBidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.VirtualBidCustomizationInterface;
import com.jeppesen.carmen.crewweb.interbids.customization.api.VirtualBidUpstreamContext;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;
import com.jeppesen.jcms.crewweb.common.util.CWLog;
import com.sas.interbids.base.SasConstants;
import com.sas.interbids.formatter.helper.PriorityStringLookupHelper;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import org.joda.time.format.DateTimeFormatter;
import static com.jeppesen.carmen.crewweb.interbids.customization.api.BidData.BID_PROPERTY_PREFIX;
import static com.jeppesen.carmen.crewweb.interbids.customization.api.BidData.BID_TRANSIENT_PREFIX;
import static com.sas.interbids.base.SasConstants.LEG_DURATION_BID_POINTS;
import static com.sas.interbids.base.SasConstants.PRIORITY;
import static java.lang.String.format;


public class VirtualBidCustomization implements VirtualBidCustomizationInterface, UserCustomizationAPIAware, DataSourceLookupHelperAware {

    private static final CWLog LOG = CWLog.getLogger(VirtualBidCustomization.class);
    private UserCustomizationAPI userCustomizationAPI;
    Map<String, Collection<? extends ImmutableTrip>> preassignmentLists = new HashMap<String, Collection<? extends ImmutableTrip>>();

    @Override
    public void prepareForUpstreamProcessing(MutableBidData baseBid, CWDateTime periodStart,
					     VirtualBidUpstreamContext context) {


	if (baseBid.getType().equalsIgnoreCase("days_for_production")) {
	    handleDaysForProductionBid(baseBid, context);
	} else {
	    applyTransientPropertyToBidData(baseBid);
	}
    }


    @Override
    public void setUserCustomizationAPI(UserCustomizationAPI arg0) {
	this.userCustomizationAPI = arg0;
    }


    private void handleDaysForProductionBid(MutableBidData baseBid, VirtualBidUpstreamContext context) {
	CWDateTime bidStart = baseBid.getStartDate();
	CWDateTime bidEnd = baseBid.getEndDate();

	for (ImmutableTrip trip : getPreassignments()) {
	    if (tripIsFlt(trip)) {
		CWDateTime lockedStart = CWDateTime.create(trip.getStart().getMilliSeconds());
		CWDateTime lockedEnd = CWDateTime.create(trip.getEnd().getMilliSeconds() - 60000);

		if((!bidStart.isBefore(lockedStart)) && (!bidEnd.isAfter(lockedEnd))) {
		    // Bid is totally within locked period: just lock bid.
		    baseBid.setLocked(true);
		} else if ((bidStart.isBefore(lockedStart)) && (bidEnd.isAfter(lockedEnd))) {
		    // Bid needs to be split in three parts. Original bid is part before locked part.
		    CWDateTime part1End = CWDateTime.create(lockedStart.getMilliSeconds() - 60000);
		    setBidDates(baseBid, bidStart, part1End);
		
		    MutableBidData part2 = context.createNewVirtualBid();
		    setBidDates(part2, lockedStart, lockedEnd);
		    part2.setLocked(true);
		
		    MutableBidData part3 = context.createNewVirtualBid();
		    CWDateTime part3Start = CWDateTime.create(lockedEnd.getMilliSeconds() + 60000);
		    setBidDates(part3, part3Start, bidEnd);
		} else if ((!bidStart.isAfter(lockedEnd)) && bidEnd.isAfter(lockedEnd)) {
		    // Bid needs to be split in two parts. Original bid is part after locked part.
		    MutableBidData part1 = context.createNewVirtualBid();
		    setBidDates(part1, bidStart, lockedEnd);
		    part1.setLocked(true);
		
		    CWDateTime part2Start = CWDateTime.create(lockedEnd.getMilliSeconds() + 60000);
		    setBidDates(baseBid, part2Start, bidEnd);
		} else if (bidStart.isBefore(lockedStart) && (!bidEnd.isBefore(lockedStart))) {
		    // Bid needs to be split in two parts. Original bid is part before locked part.
		    CWDateTime part1End = CWDateTime.create(lockedStart.getMilliSeconds() - 60000);
		    setBidDates(baseBid, bidStart, part1End);

		    MutableBidData part2 = context.createNewVirtualBid();
		    setBidDates(part2, lockedStart, bidEnd);
		    part2.setLocked(true);		
		}
		break;
	    }
	}
    }

    
    private void setBidDates(MutableBidData bid, CWDateTime start, CWDateTime end) {
	bid.setStartDate(start);
	bid.setEndDate(end);
	SasConstants.setValidityPeriodFieldValue(bid, SasConstants.START, CWDateTime.formatISODateTime(start));
	SasConstants.setValidityPeriodFieldValue(bid, SasConstants.END, CWDateTime.formatISODateTime(end));
	SasConstants.setValidityPeriodFieldValue(bid, SasConstants.START_DATE, CWDateTime.formatISODate(start));
	SasConstants.setValidityPeriodFieldValue(bid, SasConstants.END_DATE, CWDateTime.formatISODate(end));
    }


    private boolean tripIsFlt(ImmutableTrip trip) {
	return trip.getCrrId().equals("FLT");
    }


    private Collection<? extends ImmutableTrip> getPreassignments() {
	Collection<? extends ImmutableTrip> preassignments;
	String userId = this.userCustomizationAPI.getUserId();
	
	if (preassignmentLists.containsKey(userId)) {
	    preassignments = preassignmentLists.get(userId);
	} else {
	    preassignments = this.userCustomizationAPI.getPreassignments();
	    preassignmentLists.put(userId, preassignments);
	}
	return preassignments;
    }


    // Originally from DynamicBidDataHandler.java
    private DataSourceLookupHelper dataSourceLookupHelper;

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

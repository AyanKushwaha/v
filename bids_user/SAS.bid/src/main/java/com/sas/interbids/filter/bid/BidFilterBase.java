package com.sas.interbids.filter.bid;

import static com.jeppesen.carmen.crewweb.interbids.customization.api.BidData.BID_PROPERTY_PREFIX;
import static com.sas.interbids.base.SasConstants.getValidityPeriodFieldValue;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;

import com.jeppesen.carmen.crewweb.backendfacade.bo.Activity;
import com.jeppesen.carmen.crewweb.backendfacade.bo.ImmutableTrip;
import com.jeppesen.carmen.crewweb.backendfacade.bo.Trip;
import com.jeppesen.carmen.crewweb.framework.bo.Period;
import com.jeppesen.carmen.crewweb.interbids.business.impl.FilterBidResult;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidTypeFilterContext;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidTypeFilterInterface;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;
import com.sas.interbids.filter.FilterBase;

public class BidFilterBase extends FilterBase implements BidTypeFilterInterface {

	protected static final String TIME_INTERVAL_START_PROPERTY = BID_PROPERTY_PREFIX
			+ "time_interval.start_time";
	protected static final String TIME_INTERVAL_END_PROPERTY = BID_PROPERTY_PREFIX
			+ "time_interval.end_time";		
	
	@Override
	public void filter(BidData bidData, FilterBidResult result,
			BidTypeFilterContext context) {

		List<Trip> matchingTrips = new ArrayList<Trip>();

		for (Trip trip : result.getBaselineTrips()) {
			if (isMatch(trip, bidData, context)) {
				matchingTrips.add(trip);
			}
		}
		result.setTripList("availableTrips", result.getBaselineTrips());
		result.setMatchTripList(matchingTrips);
	}

	@Override
	public Collection<CWDateTime> getDaysOff(BidData bidData, Period period,
			BidTypeFilterContext context) {
		return Collections.emptyList();
	}

	@Override
	public boolean isMatch(ImmutableTrip trip, BidData bidData,
			BidTypeFilterContext context) {
		
		//Disregard everything that is not a flight
		String tripType = trip.getAttribute(ATTR_TRIP_TYPE);
		if (!ATTR_TRIP_TYPE_FLIGHT.equals(tripType)) {
			return false;
		}
		
		return isMatch(trip, bidData);
	}

	protected CWDateTime getActivityStart(Activity activity) {
		return getDateTime(activity, ATTR_START_DATE, ATTR_START_TIME);
	}	
	
	private CWDateTime getDateTime(Activity activity, String attrDate, String attrTime) {
		String date = activity.getAttribute(attrDate);
		String time = activity.getAttribute(attrTime);
		return CWDateTime.parseDateTime(date + " " + time);
	}	
	
	protected CWDateTime getTripStart(ImmutableTrip trip) {
		return getDateTime(trip, ATTR_START_DATE, ATTR_START_TIME);
	}	
	
	private CWDateTime getDateTime(ImmutableTrip trip, String attrDate, String attrTime) {
		String date = trip.getAttribute(attrDate);
		String time = trip.getAttribute(attrTime);
		return CWDateTime.parseDateTime(date + " " + time);
	}		
	
	protected boolean isWithinValidity(CWDateTime date, Validity v) {
		boolean withinPeriod = dateTimeUtil.isDateTimeWithinRange(v.getStart(), v.getEnd(), date);
		boolean touchesWeekdays = !v.hasWeekdays() || dateTimeUtil.tripTouchesWeekdays(v.getWeekdays(), date, date);
		return withinPeriod && touchesWeekdays;
	}	
	
	/**
	 * Override this i subclasses
	 * @param trip
	 * @param bidData
	 * @return
	 */
	protected boolean isMatch(ImmutableTrip trip, BidData bidData) {
		return false;
	}
	
	protected static class Validity {

		private CWDateTime start;
		private CWDateTime end;
		private String[] weekdays;

		private Validity(BidData bidData, boolean ufnAllowed) {
			String startValue = getValidityPeriodFieldValue(bidData, "start");
			this.start = CWDateTime.parseISODateTime(startValue);

			String endValue = getValidityPeriodFieldValue(bidData, "end");
			CWDateTime end = CWDateTime.parseISODateTime(endValue);
			if (end == null && ufnAllowed) {
				end = CWDateTime.create(2035, 12, 31, 23, 59, 0);
			}
			this.end = end;

			String weekdaysValue = getValidityPeriodFieldValue(bidData, "weekdays");
			if (weekdaysValue != null) {
				this.weekdays = split(weekdaysValue);
			}
		}

		public static Validity ufnAllowed(BidData bidData) {
			return new Validity(bidData, true);
		}

		public static Validity ufnNotAllowed(BidData bidData) {
			return new Validity(bidData, false);
		}

		public CWDateTime getStart() {
			return start;
		}

		public CWDateTime getEnd() {
			return end;
		}

		public String[] getWeekdays() {
			return weekdays;
		}

		public boolean hasWeekdays() {
			return weekdays != null;
		}
	}
}

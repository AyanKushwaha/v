package com.sas.interbids.filter.bid;

import java.util.List;

import com.sas.interbids.base.SasConstants;

import static com.jeppesen.carmen.crewweb.interbids.customization.api.BidData.BID_PROPERTY_PREFIX;

import com.jeppesen.carmen.crewweb.backendfacade.bo.ImmutableTrip;
import com.jeppesen.carmen.crewweb.backendfacade.bo.Trip;
import com.jeppesen.carmen.crewweb.backendfacade.bo.Activity;
import com.jeppesen.carmen.crewweb.backendfacade.bo.Duty;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;

public class StopBidFilter extends BidFilterBase {

        protected static final String STOP_DESTINATION = BID_PROPERTY_PREFIX
			+ "stop_destination.stop_destination";
	protected static final String STOP_TYPE = BID_PROPERTY_PREFIX
			+ "stop_type.stop_type";
	protected static final String STOP_LENGTH_SELECTION = BID_PROPERTY_PREFIX
			+ "stop_length.selection";
	protected static final String STOP_LENGTH_START_VALUE = BID_PROPERTY_PREFIX
			+ "stop_length.startValue";
	protected static final String STOP_LENGTH_END_VALUE = BID_PROPERTY_PREFIX
			+ "stop_length.endValue";

	@Override
	protected boolean isMatch(ImmutableTrip trip, BidData bidData) {

		return isStopMatchValid((Trip)trip, Validity.ufnAllowed(bidData), bidData);
	}

  private boolean isStopMatchValid(Trip trip, Validity validity, BidData bidData){
    String destination = bidData.get(STOP_DESTINATION) == null ? "any" : bidData.get(STOP_DESTINATION); 
    
    String stopLengthMin = bidData.get(SasConstants.STOP_LENGTH_MIN);
		// Should never be NULL, but we put on both suspenders and belt
		if (stopLengthMin.isEmpty() || stopLengthMin == null) {
			stopLengthMin = SasConstants.DEFAULT_STOP_LENGTH_MIN;
		}
		String stopLengthMax = bidData.get(SasConstants.STOP_LENGTH_MAX);
		if (stopLengthMax.isEmpty() || stopLengthMax == null) {
			stopLengthMax = SasConstants.DEFAULT_STOP_LENGTH_MAX;
		} 
    
    for (Duty duty : trip.getDuties()) {
      String endStation = dutyEndStation(duty);
      
      if (destination.equalsIgnoreCase("any") || destination.equals(endStation)) {
        return matchAtDestinationWithinInterval(duty.getAttribute(ATTR_RESTTIME), stopLengthMin, stopLengthMax) && matchWithinValidityPeriod(duty.getAttribute(ATTR_ACTIVITY_ENDDATE), validity);
      }
    }
    return false;
  }

  private boolean matchAtDestinationWithinInterval(String dutyRestTime, String minTime, String maxTime) {
    int minTimeInMinutes = stringTimeToMinutes(minTime);
    int maxTimeInMinutes = stringTimeToMinutes(maxTime);
    int restTimeInMinutes = stringTimeToMinutes(dutyRestTime);
    if (restTimeInMinutes <= maxTimeInMinutes && restTimeInMinutes >= minTimeInMinutes) {
      return true;
    }
    return false;
  }
  
  private boolean matchWithinValidityPeriod(String stopStartTime, Validity validity){
    CWDateTime stopDate = parseAbsdateToCWDateTime(stopStartTime);
    return isWithinValidity(stopDate, validity);
  }
  
  
  private String dutyEndStation(Duty duty) {
    List<Activity> activityList = duty.getActivities();
    Activity lastActivityinDuty = activityList.get(activityList.size() - 1);
    return lastActivityinDuty.getAttribute(ATTR_END_STATION);
  }
}



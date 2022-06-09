package com.sas.interbids.filter;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.regex.Pattern;
import java.util.ArrayList;

import org.joda.time.DateTime;

import org.apache.commons.lang.StringUtils;

import com.jeppesen.carmen.crewweb.backendfacade.bo.Activity;
import com.jeppesen.carmen.crewweb.backendfacade.bo.Duty;
import com.jeppesen.carmen.crewweb.backendfacade.bo.Trip;
import com.jeppesen.carmen.crewweb.framework.context.aware.DateTimeUtilAware;
import com.jeppesen.carmen.crewweb.framework.util.DateTimeUtil;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;
import com.jeppesen.jcms.crewweb.common.util.CWLog;


public class FilterBase implements DateTimeUtilAware {
	
	private static final CWLog LOG = CWLog.getLogger(FilterBase.class);

	protected static final Pattern regex_comma_whitespace = Pattern
			.compile(",\\s*");
	
	protected static final String MAXIMUM = "maximum";
	protected static final String MINIMUM = "minimum";
	protected static final String BETWEEN = "between";
	protected static final String EXACTLY = "exactly";
	
	/* Bid properties */
	protected static final String START_TIME_PROPERTY = "start_time";
	protected static final String END_TIME_PROPERTY = "end_time";
	protected static final String START_VALUE_PROPERTY = "startValue";
	protected static final String END_VALUE_PROPERTY = "endValue";
	protected static final String DESTINATION = "destination";
	protected static final String SELECTION = "selection";
	protected static final String STOP_TYPE = "stop_type";
	protected static final String FLIGHT_NUMBER_PROPERTY = "flight_number";
	
	protected static final String TYPE_ANY_STOP = "any_stop";
	protected static final String TYPE_GROUND_STOP = "ground_stop";
	protected static final String TYPE_NIGHT_STOP = "night_stop";
	
	/* Trip attributes */
	protected static final String TYPE_NIGHTSTOP_TRUE = "True";
	protected static final String TYPE_NIGHTSTOP_NONE = "None";
	
	protected static final String ATTR_TRIP_TYPE = "type";
	protected static final String ATTR_TRIP_TYPE_FLIGHT = "flight";
	protected static final String ATTR_START_TIME = "starttime";	
	protected static final String ATTR_END_TIME = "endtime";	
	protected static final String ATTR_FLIGHT_NUMBER = "number";
	protected static final String ATTR_LENGTH = "length";
	
	protected static final String ATTR_START_DATE = "startdate";
	protected static final String ATTR_NIGHT_STOP = "nightstop";
	protected static final String ATTR_RESTTIME = "resttime";	
	protected static final String ATTR_LAYOVERS = "layovers";
	protected static final String ATTR_CNXTIME = "cnxtime";
	
	protected static final String ATTR_ACTIVITY_STARTDATE = "startdate";
	protected static final String ATTR_ACTIVITY_STARTTIME = "starttime";
	protected static final String ATTR_ACTIVITY_ENDDATE = "enddate";
	protected static final String ATTR_ACTIVITY_ENDTIME = "endtime";
	protected static final String ATTR_ACTIVITY_CHARTER = "charter";
	
	protected static final String ATTR_START_STATION = "startstation";
	protected static final String ATTR_END_STATION = "endstation";
	
	protected DateTimeUtil dateTimeUtil;
	
	private static final String[] EMPTY_ARRAY = new String[0];
	
	protected static final Map<String, Integer> weekday = new HashMap<String, Integer>();
	protected static final Map<String, Integer> monthNr = new HashMap<String, Integer>();
	static {
		weekday.put("monday", 1);
		weekday.put("tuesday", 2);
		weekday.put("wednesday", 3);
		weekday.put("thursday", 4);
		weekday.put("friday", 5);
		weekday.put("saturday", 6);
		weekday.put("sunday", 7);
		
		monthNr.put("jan", 1);
		monthNr.put("feb", 2);
		monthNr.put("mar", 3);
		monthNr.put("apr", 4);
		monthNr.put("may", 5);
		monthNr.put("jun", 6);
		monthNr.put("jul", 7);
		monthNr.put("aug", 8);
		monthNr.put("sep", 9);
		monthNr.put("oct", 10);
		monthNr.put("nov", 11);
		monthNr.put("dec", 12);
	}
	
	
	@Override
	public void setDateTimeUtil(DateTimeUtil dateTimeUtil) {
		this.dateTimeUtil = dateTimeUtil;
	}

	protected CWDateTime parseTime(String time) {
		return dateTimeUtil.parseDurationToCWDateTime(time);
	}
	
	/**
	* Expects input like Abstime string e.g 01Jan2019
	**/
	protected CWDateTime parseAbsdateToCWDateTime(String absDate)	{
		int day = Integer.parseInt(absDate.substring(0, 2));
		int month = monthNr.get(absDate.substring(2, 5).toLowerCase());
		int year = Integer.parseInt(absDate.substring(5, 9)); 
		
		return dateTimeUtil.parseToCWDateTime(new DateTime(year, month, day, 0, 1, 1, 1));
	}
	

	
	// Retrieves the number of hours from the rest duration (format 54:40)
	public int parseHours(String duration) {
		// Split the String into hours and minutes
		String[] fromValues = duration.split(":");
		return Integer.parseInt(fromValues[0]);
	}
	
	// Retrieves the number of hours from the rest duration (format 54:40)
	public int parseMinutes(String duration) {
		// Split the String into hours and minutes
		String[] fromValues = duration.split(":");
		return Integer.parseInt(fromValues[1]);
	}	

	public int stringTimeToMinutes(String duration) {
		return parseHours(duration) * 60 + parseMinutes(duration);
	}
	
	protected static String[] split(String s) {
		if (StringUtils.isEmpty(s)) {
			return EMPTY_ARRAY;
		}

		if (s.startsWith(",")) {
			s = s.substring(1);
		}
		return regex_comma_whitespace.split(s);
	}
	
	protected boolean isWeekdayMatch(BidData bidData, CWDateTime date) {
		
		String weekday = bidData.get(BidData.BID_PROPERTY_PREFIX + "weekday_option.weekday_option");
		if (weekday != null) {
			try {
				int w = Integer.parseInt(weekday);
				return w == date.getDayOfWeek();
			} catch (Exception e) {
				LOG.warn("Not able to parse weekday: " + weekday);
				return false;
			}
		} else {
			return true;
		}
	}

	protected boolean isWithinTimeInterval(CWDateTime time, CWDateTime start, CWDateTime end) {

		// Allow missing values when filtering
		if (start == null && end == null) {
			return true;
		}
		else if (start == null) {
			return !time.isAfter(end);
		}
		else if (end == null) {
			return !time.isBefore(start);
		}

		if (start.isAfter(end)) {
			return time.isAfter(start) || time.isEqual(start)
					|| time.isBefore(end) || time.isEqual(end);
		}
		
		return dateTimeUtil.isDateTimeWithinRange(start, end, time);
	}		
	
	/**
	 * Check if stop minutes is within interval
	 * 
	 * @param stopTime on format hh:mm
	 * @param startTime on format hh:mm
	 * @param endTime on format hh:mm
	 * @return
	 */
	protected boolean isInTimeInterval(String stopTime, String startTime, String endTime) {

		int startMinutes = (parseHours(startTime) * 60) + parseMinutes(startTime);
		int endMinutes = (parseHours(endTime) * 60) + parseMinutes(endTime);
		int stopMinutes = (parseHours(stopTime) * 60) + parseMinutes(stopTime);

		return (stopMinutes >= startMinutes && stopMinutes <= endMinutes);
	}		
	
	/**
	 * Check if stop minutes is minimum startTime
	 * @param stopTime
	 * @param startTime
	 * @return
	 */
	protected boolean isInMinimumTime(String stopTime, String startTime) {

		int startMinutes = (parseHours(startTime) * 60) + parseMinutes(startTime);
		int stopMinutes = (parseHours(stopTime) * 60) + parseMinutes(stopTime);

		return (stopMinutes >= startMinutes);
	}
	
	/**
	 * Check if stop minutes is less than endTime
	 * @param stopTime
	 * @param endTime
	 * @return
	 */
	protected boolean isInMaximumTime(String stopTime, String endTime) {

		int endMinutes = (parseHours(endTime) * 60) + parseMinutes(endTime);
		int stopMinutes = (parseHours(stopTime) * 60) + parseMinutes(stopTime);

		return (stopMinutes <= endMinutes);
	}

	/**
	 * Check if a matching ground stop exists in the trip
	 * 
	 * @param trip
	 * @param destination 
	 * @param startTime on format hh:mm
	 * @param endTime on format hh:mm
	 * @param type MINIMUM (startTime), MAXIMUM (endTime), BETWEEN (startTime - endTime) 
	 * @return
	 */
	protected boolean isGroundStopMatch(Trip trip, String destination) {
		
		Iterator<Duty> duties = trip.getDuties().iterator();
		while(duties.hasNext()) {
			Duty duty = duties.next();

			Iterator<Activity> activities = duty.getActivities().iterator();
			while(activities.hasNext()) {
				Activity activity = activities.next();
					
				//last leg in a trip cannot grant a stop
				if (!duties.hasNext() && !activities.hasNext()) {
					return false;
				}
				
				String activityEndStation = activity.getAttribute(ATTR_END_STATION);
				if (destination.equalsIgnoreCase("any") || destination.equals(activityEndStation)) {
					
					String activityStopTime = activity.getAttribute(ATTR_CNXTIME);
					
					if (!(activityStopTime == null || activityStopTime.length() == 0)) {
					    String startTime = "10:00";
					    
					    if (isInMinimumTime(activityStopTime, startTime)) {
						return true;
					    }
					}
				}
			}
		}
		
		return false;
	}
	
	/**
	 * Check if a trip contains a matching nightstop at a destination
	 * 
	 * @param trip
	 * @param destination
	 * @param startTime on format hh:mm
	 * @param endTime on format hh:mm
	 * @param type MINIMUM (startTime), MAXIMUM (endTime), BETWEEN (startTime - endTime) 
	 * @return
	 */
	protected boolean isNightStopMatch(Trip trip, String destination) {
		String layovers = trip.getAttribute(ATTR_LAYOVERS);
		

		//if no layover destination match
		if (layovers == null || (!destination.equalsIgnoreCase("any") && !layovers.contains(destination))) {
			return false;
		}
		
		for (Duty duty : trip.getDuties()) {
			String dutyNightStop = duty.getAttribute(ATTR_NIGHT_STOP);
			if (TYPE_NIGHTSTOP_TRUE.equals(dutyNightStop)) {
				
				String dutyRestTime = duty.getAttribute(ATTR_RESTTIME);
				String startTime = "10:00";
				
				if(isInMinimumTime(dutyRestTime, startTime)) {
					if (duty.getActivities().size() != 0) {
						Activity activity = duty.getActivities().get(duty.getActivities().size() - 1);
						String activityEndStation = activity.getAttribute(ATTR_END_STATION);
	
						if (destination.equalsIgnoreCase("any") || destination.equals(activityEndStation)) {
							return true;
						}
					}
				}
			}
		}

		return false;
	}	
}

package com.sas.interbids.base;

import static com.jeppesen.carmen.crewweb.interbids.customization.api.BidData.BID_PROPERTY_PREFIX;

import java.util.HashMap;
import java.util.Map;

import com.jeppesen.carmen.crewweb.framework.context.aware.DateTimeUtilAware;
import com.jeppesen.carmen.crewweb.framework.util.DateTimeUtil;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.MutableBidData;

public final class SasConstants implements DateTimeUtilAware {

	public static final String PBS_PERIOD = "standard";

	public static final String dateFormat = "ddMMMyy";
	public static final String dateTimeFormat = "ddMMMyy HH:mm";

	// Validity period
	public static final String START = "start";
	public static final String END = "end";
	public static final String START_DATE = "startDate";
	public static final String END_DATE = "endDate";
	public static final String ORIGINAL_START_DATE = "originalStartDate";
	public static final String ORIGINAL_END_DATE = "originalEndDate";
	public static final String START_TIME = "start_time";
	public static final String END_TIME = "end_time";

	public static final String BETWEEN = "between";
	public static final String EXACTLY = "exactly";
	public static final String MAXIMUM = "maximum";
	public static final String MINIMUM = "minimum";

	// Number of days
	public static final String NUMBER_OF_DAYS = "number_of_days";

	// Destination
	public static final String DESTINATION = "airport_code";

	// Others
	public static final String CHECKIN_OPTIONS = prop("checkin_options");
	public static final String CHECKOUT_OPTIONS = prop("checkout_options");
	public static final String TIMES_PER_ROSTER = prop("time_per_roster", "times_per_roster");
//	public static final String MOST_IMPORTANT = prop("most_important", "consec_days");
	public static final String MOST_IMPORTANT = prop("string_days_off", "most_important");
	public static final String TYPE_OF_COMP_DAY_FD = prop("type_of_comp_day_fd", "type_of_comp_day");
	public static final String TYPE_OF_COMP_DAY_CC = prop("type_of_comp_day_cc", "type_of_comp_day");
	public static final String PRIORITY = prop("priority");
	public static final String COMP_DAY_PERIOD = prop("comp_day_period", "day_period");
	public static final String CHECK_IN_START = prop("check_in", "startTime");
	public static final String CHECK_IN_END = prop("check_in", "endTime");
	public static final String CHECK_OUT_START = prop("check_out", "startTime");
	public static final String CHECK_OUT_END = prop("check_out", "endTime");
	public static final String CONSEC_DAYS_AT_WORK = prop("num_consec_days_at_work", "consec_days_at_work");
	public static final String CONSEC_DAYS_OFF = prop("num_consec_days_off", "consec_days_off");
	public static final String STOP_DESTINATION = prop("stop_destination");
	public static final String FLIGHT_DEP_STATION = prop("flight_departing_station");
	public static final String STOP_TYPE = prop("stop_type");
	public static final String FLIGHT_NUMBER = prop("flight_number");
	public static final String CHARTER_FLIGHT = prop("flight_number", "charter");
	public static final String ETAB_TYPE_PREFERENCE = "Preference";
	public static final String CHECK_IN_TIME = prop("check_in_type", "checkInTime");
	public static final String CHECK_OUT_TIME = prop("check_out_type", "checkOutTime");

	//BidGroup details
	public static final String BID_CATEGORY_CURRENT = "current";
	public static final String BID_CATEGORY_PREFERENCE = "preference";
	public static final String BID_GROUP_TYPE_FLIGHT = "flight";
	public static final String BID_GROUP_TYPE_PREFERENCE = "preference-bids";
	public static final String BID_GROUP_NAME_CURRENT = "Current Bids";
	public static final String BID_GROUP_NAME_PREFERENCES = "Current Lifestyle";

	//Combination
	public static final String COMBINATION_CHECKIN_STARTTIME = prop("combination_checkin", "start_time");
	public static final String COMBINATION_CHECKIN_ENDTIME = prop("combination_checkin", "end_time");
	public static final String COMBINATION_CHECKIN_OPTIONS = prop("combination_checkin", "checkin_options");
	public static final String COMBINATION_CHECKOUT_STARTTIME = prop("combination_checkout", "start_time");
	public static final String COMBINATION_CHECKOUT_ENDTIME = prop("combination_checkout", "end_time");
	public static final String COMBINATION_CHECKOUT_OPTIONS = prop("combination_checkout", "checkout_options");

	public static final String COMBINATION_PAIRING_START = prop("combination_pairing_length", "startValue");
	public static final String COMBINATION_PAIRING_END = prop("combination_pairing_length", "endValue");
	public static final String COMBINATION_PAIRING_SELECTION = prop("combination_pairing_length", "selection");	

	public static final String COMBINATION_STOP_START = prop("combination_stop", "startValue");
	public static final String COMBINATION_STOP_END = prop("combination_stop", "endValue");
	public static final String COMBINATION_STOP_TYPE = prop("combination_stop", "stop_type");
	public static final String COMBINATION_STOP_SELECTION = prop("combination_stop", "selection");
	public static final String COMBINATION_STOP_DESTINATION = prop("combination_stop", "destination");

	//WeekdayAndTime
	public static final String WEEKDAY_STARTTIME = prop("weekday_and_time", "startTime");
	public static final String WEEKDAY_TO_WEEKDAY = prop("weekday_and_time", "to_weekday");
	public static final String WEEKDAY_ENDTIME = prop("weekday_and_time", "endTime");
	public static final String WEEKDAY_FROM_WEEKDAY = prop("weekday_and_time", "from_weekday");

	//PairingLength
	public static final String PAIRING_START = prop("days_per_pairing", "startValue");
	public static final String PAIRING_END = prop("days_per_pairing", "endValue");
	public static final String PAIRING_SELECTION = prop("days_per_pairing", "selection");

	public static final String LEG_DURATION_START = prop("leg_duration", "startValue");
	public static final String LEG_DURATION_END = prop("leg_duration", "endValue");
	public static final String LEG_DURATION_SELECTION = prop("leg_duration", "selection");
	public static final String LEG_DURATION_BID_POINTS = prop("leg_duration_points", "priority");

	public static final String STOP_LENGTH_MIN = prop("stop_length_min");
	public static final String STOP_LENGTH_MAX = prop("stop_length_max");

	public static final String DEFAULT_STOP_LENGTH_MIN = "5:00";
	public static final String DEFAULT_STOP_LENGTH_MAX = "300:00";

	public static Map<String, Integer> stop_type_translation = new HashMap<String, Integer>();

	protected static Map<String, String> validityPeriodPropertyNames = new HashMap<String, String>();
	protected static Map<String, String> timeIntervalPropertyNames = new HashMap<String, String>();
	protected static Map<String, String> numberOfDaysPropertyNames = new HashMap<String, String>();	
	protected static Map<String, String> destinationPropertyNames = new HashMap<String, String>();

	public static Map<String, String> compensationDaysTypeOfCompDay = new HashMap<String, String>();


	static {
		validityPeriodPropertyNames.put("check_in", "validity_period");
		validityPeriodPropertyNames.put("check_out", "validity_period");
		validityPeriodPropertyNames.put("string_of_days_off", "string_days_off");
		validityPeriodPropertyNames.put("compensation_days_fd", "single_validity_period");
		validityPeriodPropertyNames.put("compensation_days_cc", "single_validity_period");
		validityPeriodPropertyNames.put("consecutive_days_at_work", "validity_period");
		validityPeriodPropertyNames.put("consecutive_days_off", "validity_period");
		validityPeriodPropertyNames.put("time_off", "date_time_end");
		validityPeriodPropertyNames.put("last_minute_LOA", "validity_period_no_ufn");
		validityPeriodPropertyNames.put("days_for_production", "validity_period_days_for_prod");
		validityPeriodPropertyNames.put("pairing_length", "validity_period");
		validityPeriodPropertyNames.put("leg_duration", "validity_period");
		validityPeriodPropertyNames.put("stop", "validity_period");
		validityPeriodPropertyNames.put("f4_weekend_off_cc", "f4_weekend_off_period_cc");
		validityPeriodPropertyNames.put("f4_weekend_off_fd_crj", "f4_weekend_off_period_fd_crj");
		validityPeriodPropertyNames.put("f4_weekend_off_fd", "f4_weekend_off_period_fd");
		validityPeriodPropertyNames.put("combination", "validity_period");
		validityPeriodPropertyNames.put("flight", "single_date");

		timeIntervalPropertyNames.put("check_in", "time_interval");
		timeIntervalPropertyNames.put("check_out", "time_interval");
		timeIntervalPropertyNames.put("compensation_days_fd", "static_time_interval");
		timeIntervalPropertyNames.put("compensation_days_cc", "static_time_interval");

		destinationPropertyNames.put("FlightNumber", "airport_code_optional");
		destinationPropertyNames.put("FlyWithCrew", "airport_code_optional");
		destinationPropertyNames.put("RestPeriodAtStation", "airport_code");

		stop_type_translation.put("any_stop", 0);
		stop_type_translation.put("ground_stop", 1);
		stop_type_translation.put("night_stop", 2);

		compensationDaysTypeOfCompDay.put("compensation_days_fd", TYPE_OF_COMP_DAY_FD);
		compensationDaysTypeOfCompDay.put("compensation_days_cc", TYPE_OF_COMP_DAY_CC);
	}

	private static String prop(String typeAndName) {
		return prop(typeAndName, typeAndName);
	}

	private static String prop(String type, String name) {
		return BID_PROPERTY_PREFIX + type + "." + name;
	}

	private static String getFieldValue(BidData bidData, String fieldName,
			Map<String, String> propertyNames) {

		String bidType = bidData.getType();
		String propertyName = propertyNames.get(bidType);
		String propertyKey = BID_PROPERTY_PREFIX + propertyName + "." + fieldName;
		String fieldValue = bidData.get(propertyKey);

		return fieldValue;
	}

	public static String getValidityPeriodFieldValue(BidData bidData,
			String fieldName) {
		return getFieldValue(bidData, fieldName, validityPeriodPropertyNames);
	}

        private static void setFieldValue(MutableBidData bidData, String fieldName, String fieldValue,
					  Map<String, String> propertyNames) {

		String bidType = bidData.getType();
		String propertyName = propertyNames.get(bidType);
		String propertyKey = BID_PROPERTY_PREFIX + propertyName + "." + fieldName;
		bidData.set(propertyKey, fieldValue);
	}

	public static void setValidityPeriodFieldValue(MutableBidData bidData,
						       String fieldName,
						       String fieldValue) {
	    setFieldValue(bidData, fieldName, fieldValue, validityPeriodPropertyNames);
	}

	public static String getTimeIntervalFieldValue(BidData bidData, String fieldName) {
		String fieldValue = getFieldValue(bidData, fieldName, timeIntervalPropertyNames);
		return fieldValue;
	}

	public static Integer getNumberOfDays(BidData bidData) {
		String nrOfDays = getFieldValue(bidData, NUMBER_OF_DAYS, numberOfDaysPropertyNames);
		try {
			return new Integer(nrOfDays);
		}
		catch (RuntimeException e) {
			return null;
		}
	}

	@Override
	public void setDateTimeUtil(DateTimeUtil dateTimeUtil) {
		// TODO Auto-generated method stub

	}

}

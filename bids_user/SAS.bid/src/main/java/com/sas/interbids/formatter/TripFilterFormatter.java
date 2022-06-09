package com.sas.interbids.formatter;

import java.util.List;

import com.jeppesen.carmen.crewweb.interbids.bo.BidProperty;
import com.jeppesen.carmen.crewweb.interbids.bo.TripSearch;
import com.jeppesen.carmen.crewweb.interbids.customization.TripSearchFormatter;
import com.jeppesen.jcms.crewweb.common.context.aware.LocalizationAware;
import com.jeppesen.jcms.crewweb.common.localization.Localization;

/**
 * This class is used to make the filters in the trip tab readable.
 * The following property need to be set in interbids.properties in order for this to work
 * interbids.trip-search-formatter-class=com.jeppesen.klm.formatter.TripFilterFormatter 
 */


public class TripFilterFormatter extends Formatter implements TripSearchFormatter, LocalizationAware{

	private Localization localization;
	
	private static final String CHECKIN_PROPERTY = "check_in";
	private static final String CHECKOUT_PROPERTY = "check_out";
	private static final String FLIGHT_NUMBER_PROPERTY = "flight_number";
	private static final String PAIRING_LENGTH_PROPERTY = "days_per_pairing_interval";
	private static final String LEG_DURATION_PROPERTY = "leg_duration_interval";
	private static final String STOP_PROPERTY = "stop_interval";
	
	//TEMP PROPERTIES. SHOULD BE REMOVED WHEN JIRA UIIB-1650
	
	private static final String COMBINATION_CHECKIN_PROPERTY = "combination_checkin";
	private static final String COMBINATION_CHECKOUT_PROPERTY = "combination_checkout";
	private static final String COMBINATION_PAIRING_LENGTH_PROPERTY = "combination_pairing_length";
	private static final String COMBINATION_STOP_PROPERTY = "combination_stop";

	public String format(TripSearch tripSearch) {
		StringBuilder result = new StringBuilder();
		List<BidProperty> bidProperties = tripSearch.getBidProperties();
		for(BidProperty bidProperty : bidProperties){
			
			appendPropertyFilterString(result, bidProperty);
			result.append(", ");	
		}
		return result.toString();
	}

	private void appendPropertyFilterString(StringBuilder result, BidProperty bidProperty) {
		if (bidProperty.getType().equalsIgnoreCase(CHECKIN_PROPERTY)) {
			
			getCheckIn(result, bidProperty);
			
		} else if (bidProperty.getType().equalsIgnoreCase(CHECKOUT_PROPERTY)) {
			
			getCheckOut(result, bidProperty);
			
		} else if (bidProperty.getType().equalsIgnoreCase(FLIGHT_NUMBER_PROPERTY)) {
			
			getFlightNumber(result, bidProperty);
			
		} else if (bidProperty.getType().equalsIgnoreCase(PAIRING_LENGTH_PROPERTY)) {
			
			getPairingLength(result, bidProperty);
			
		} else if (bidProperty.getType().equalsIgnoreCase(LEG_DURATION_PROPERTY)) {
			
			getLegDuration(result, bidProperty);
			
		} else if (bidProperty.getType().equalsIgnoreCase(STOP_PROPERTY)) {
			
			getStop(result, bidProperty);
			
		} else if (bidProperty.getType().equalsIgnoreCase(COMBINATION_CHECKIN_PROPERTY)) {
			
			getCheckIn(result, bidProperty);
			
		} else if (bidProperty.getType().equalsIgnoreCase(COMBINATION_CHECKOUT_PROPERTY)) {
			
			getCheckIn(result, bidProperty);
			
		} else if (bidProperty.getType().equalsIgnoreCase(COMBINATION_PAIRING_LENGTH_PROPERTY)) {
			
			getCombinationPairingLength(result, bidProperty);
			
		} else if (bidProperty.getType().equalsIgnoreCase(COMBINATION_STOP_PROPERTY)) {
			
			getCombinationStop(result, bidProperty);
			
		}
	}

	private void getCombinationStop(StringBuilder result, BidProperty bidProperty) {
		String stopDestination = bidProperty.getBidPropertyEntryValue("destination");
		String stopType = bidProperty.getBidPropertyEntryValue("stop_type");
		String selection = bidProperty.getBidPropertyEntryValue("selection");

		result.append(setBoldText(localization.MSGR("combination_stop_formatter")));
		
		result.append(" ");
		result.append(localization.MSGR("combination_stop_destination_formatter"));
		result.append(" ");
		result.append(stopDestination);
		result.append(" ");
		
		result.append(" ");
		result.append(setBoldText(localization.MSGR("combination_stop_type_formatter")));
		result.append(" ");
		result.append(localization.MSGR(stopType));
		result.append(" ");
		
		if (selection.equalsIgnoreCase("minimum")) {
			String start = bidProperty.getBidPropertyEntryValue("startValue");
			result.append(localization.MSGR("combination_stop_minimum_formatter"));
			result.append(" ");
			result.append(start);
			result.append(" ");
		} else if (selection.equalsIgnoreCase("maximum")) {
			String end = bidProperty.getBidPropertyEntryValue("endValue");
			result.append(localization.MSGR("combination_stop_maximum_formatter"));
			result.append(" ");
			result.append(end);
			result.append(" ");
		} else if (selection.equalsIgnoreCase("between")) {
			String start = bidProperty.getBidPropertyEntryValue("startValue");
			String end = bidProperty.getBidPropertyEntryValue("endValue");
			result.append(localization.MSGR("combination_stop_between_start_formatter"));
			result.append(" ");
			result.append(start);
			result.append(" ");
			result.append(localization.MSGR("time_interval_between_end_formatter"));
			result.append(" ");
			result.append(end);
			result.append(" ");
			result.append(localization.MSGR("leg_duration_hours"));
		}
		
		result.append("     ");
	}

	private void getCombinationPairingLength(StringBuilder result, BidProperty bidProperty) {
		String selection = bidProperty.getBidPropertyEntryValue("selection");
		String start = bidProperty.getBidPropertyEntryValue("startValue");
		String end = bidProperty.getBidPropertyEntryValue("endValue");
		
		result.append("<b>");
		result.append(localization.MSGR("pairing_length_formatter"));
		result.append("</b>");
		result.append(" ");
		
		if (selection.equalsIgnoreCase("minimum")) {
			
			result.append(localization.MSGR("pairing_length_minimum_formatter"));
			result.append(" ");
			result.append(start);
			
		} else if (selection.equalsIgnoreCase("maximum")) {
			
			result.append(localization.MSGR("pairing_length_maximum_formatter"));
			result.append(" ");
			result.append(end);
			
		} else if (selection.equalsIgnoreCase("exactly")) {
			
			result.append(localization.MSGR("pairing_length_exactly_formatter"));
			result.append(" ");
			result.append(start);
			
		} else if (selection.equalsIgnoreCase("between")) {
			
			result.append(localization.MSGR("pairing_length_between_start_formatter"));
			result.append(" ");
			result.append(start);
			result.append(" ");
			result.append(localization.MSGR("pairing_length_between_end_formatter"));
			result.append(" ");
			result.append(end);
			result.append(" ");
			result.append(localization.MSGR("pairing_length_days"));
			result.append("     ");
			
		}
		result.append("     ");
	}

	private void getStop(StringBuilder result, BidProperty bidProperty) {
		String stopDestination = bidProperty.getBidPropertyEntryValue("destination");
		String stopType = bidProperty.getBidPropertyEntryValue("stop_type");
		
		String start = bidProperty.getBidPropertyEntryValue("startValue");
		String end = bidProperty.getBidPropertyEntryValue("endValue");
		
		result.append(setBoldText(localization.MSGR("combination_stop_formatter")));
		
		result.append(" ");
		result.append(setBoldText(localization.MSGR("combination_stop_destination_formatter")));
		result.append(" ");
		result.append(stopDestination);
		result.append(" ");
		
		result.append(" ");
		result.append(setBoldText(localization.MSGR("combination_stop_type_formatter")));
		result.append(" ");
		result.append(localization.MSGR(stopType));
		result.append(" ");
		
		result.append(localization.MSGR("stop_duration_start_formatter"));
		result.append(" ");
		result.append(start);
		result.append(" ");
		result.append(localization.MSGR("stop_duration_end_formatter"));
		result.append(" ");
		result.append(end);
		result.append(" ");
		result.append(localization.MSGR("stop_duration_hours"));
		result.append("     ");
	}

	private void getLegDuration(StringBuilder result, BidProperty bidProperty) {
		String start = bidProperty.getBidPropertyEntryValue("startValue");
		String end = bidProperty.getBidPropertyEntryValue("endValue");
		result.append("<b>");
		result.append(localization.MSGR("leg_duration_formatter"));
		result.append("</b>");
		result.append(" ");
		result.append(localization.MSGR("leg_duration_start_formatter"));
		result.append(" ");
		result.append(start);
		result.append(" ");
		result.append(localization.MSGR("leg_duration_end_formatter"));
		result.append(" ");
		result.append(end);
		result.append(" ");
		result.append(localization.MSGR("leg_duration_hours"));
		result.append("     ");
	}

	private void getPairingLength(StringBuilder result, BidProperty bidProperty) {
		String start = bidProperty.getBidPropertyEntryValue("startValue");
		String end = bidProperty.getBidPropertyEntryValue("endValue");
		result.append("<b>");
		result.append(localization.MSGR("pairing_length_formatter"));
		result.append("</b>");
		result.append(" ");
		result.append(localization.MSGR("pairing_length_start_formatter"));
		result.append(" ");
		result.append(start);
		result.append(" ");
		result.append(localization.MSGR("pairing_length_end_formatter"));
		result.append(" ");
		result.append(end);
		result.append(" ");
		result.append(localization.MSGR("pairing_length_days"));
		result.append("     ");
	}

	private void getFlightNumber(StringBuilder result, BidProperty bidProperty) {
		String flightNumber = bidProperty.getBidPropertyEntryValue("flight_number");
		
		Boolean charter = false;
		try {
			charter = Boolean.parseBoolean(bidProperty.getBidPropertyEntryValue("charter"));
		} catch (Exception e) {
			charter = false;
		}
		
		if (flightNumber != null) {
			result.append("<b>");
			result.append(localization.MSGR("flight_number_formatter"));
			result.append("</b>");
			result.append(" ");
			result.append(flightNumber);
			
			if (charter) {
			result.append(" ");
			result.append("<b>");
			result.append(localization.MSGR("charter"));
			result.append("</b>");
			result.append(" ");
			if (charter) {
				result.append("yes");
			} else {
				result.append("yes");
			}
			result.append("     ");
			}
		} else {
			result.append("<b>");
			result.append(localization.MSGR("charter"));
			result.append("</b>");
			result.append(" ");
			if (charter) {
				result.append("yes");
			} else {
				result.append("no");
			}
			result.append("     ");
		}
	}

	private void getCheckOut(StringBuilder result, BidProperty bidProperty) {
		String start = bidProperty.getBidPropertyEntryValue("start_time");
		String end = bidProperty.getBidPropertyEntryValue("end_time");
		result.append("<b>");
		result.append(localization.MSGR("check_out_formatter"));
		result.append("</b>");
		result.append(" ");
		result.append(localization.MSGR("time_interval_start_formatter"));
		result.append(" ");
		result.append(start);
		result.append(" ");
		result.append(localization.MSGR("time_interval_end_formatter"));
		result.append(" ");
		result.append(end);
		result.append("     ");
	}

	private void getCheckIn(StringBuilder result, BidProperty bidProperty) {
		String start = bidProperty.getBidPropertyEntryValue("start_time");
		String end = bidProperty.getBidPropertyEntryValue("end_time");
		result.append("<b>");
		result.append(localization.MSGR("check_in_formatter"));
		result.append("</b>");
		result.append(" ");
		result.append(localization.MSGR("time_interval_start_formatter"));
		result.append(" ");
		result.append(start);
		result.append(" ");
		result.append(localization.MSGR("time_interval_end_formatter"));
		result.append(" ");
		result.append(end);
		result.append("     ");
	}
	
	private String setBoldText(String text) {
		return "<b>" + text + "</b>";
	}

	public String formatAsReport(TripSearch tripSearch) {
		StringBuilder result = new StringBuilder();
		
		result.append("<b>Filter name:</b> " + tripSearch.getName() + "<br>");
		
		List<BidProperty> bidProperties = tripSearch.getBidProperties();
		for(BidProperty bidProperty : bidProperties){
			result.append("<ul><li>");
			appendPropertyFilterString(result, bidProperty);
			result.append("</li></ul>");
		}
		return result.toString();
	}

    public void setLocalization(Localization localization) {
    	this.localization = localization;
    }
}
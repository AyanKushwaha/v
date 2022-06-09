package com.sas.vacation.formatter;

import java.util.Locale;

import org.joda.time.format.DateTimeFormatter;

import com.jeppesen.carmen.crewweb.backendfacade.bo.ImmutableTrip;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.VacationTripDetailsFormatterInterface;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;

public class VacationTripDetailsFormatter implements VacationTripDetailsFormatterInterface {
	
	private static final String TRIP_CSS_PREFIX = "trip-item-";

    @Override
    public String getDetails(ImmutableTrip trip) {
    	String type = trip.getAttribute("type");
    	//Do not show "UNDEFINED" as type in trip details
    	if (type != null && type.length() > 0 && !type.equalsIgnoreCase("undefined")) {
    		type = Character.toUpperCase(type.charAt(0)) + type.substring(1);
    		type = " " + type;
    	} else {
    		type = "";
    	}
    	
        return //"<table>" + 
                addRow("Type:" + type + " " + trip.getAttribute("code")) +
                addRow("Start:&nbsp" + formatDateTime(trip.getStart(), "ddMMMyy HH:mm")) +
                addRow("End:&nbsp&nbsp&nbsp" + formatDateTime(trip.getEnd(), "ddMMMyy HH:mm"));
               //"</table>";
    }

    private String addRow(String text) {
        return text + "</br>";
    }

    @Override
    public String getStyleClassSuffix(ImmutableTrip trip) {
    	
    	
    	String type = trip.getAttribute("type");
        type = type + " " + TRIP_CSS_PREFIX + trip.getAttribute("type") + "-" + trip.getAttribute("code");
        type = type + " " + TRIP_CSS_PREFIX + trip.getAttribute("code");
        return type;
    }

	@Override
	public String getTitle(ImmutableTrip trip) {
		return trip.getAttribute("code");
//		String crrId = trip.getCrrId();
//		return crrId;
	}
	
	private String formatDateTime(String dateTimeString, String format) {
        if (dateTimeString != null) {
            CWDateTime date = CWDateTime.parseISODateTime(dateTimeString);
            DateTimeFormatter fmt = CWDateTime.getDateTimeFormatter(format, Locale.ENGLISH);
            return fmt.print(date.getDateTime());
        } else {
            return dateTimeString;
        }
    }
	
	private String formatDateTime(CWDateTime dateTime, String format) {
		if (dateTime != null) {
            DateTimeFormatter fmt = CWDateTime.getDateTimeFormatter(format, Locale.ENGLISH);
            return fmt.print(dateTime.getDateTime());
        } else {
            return "";
        }
    }
}
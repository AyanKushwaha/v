package com.sas.interbids.formatter.helper;


/**
 * A helper class that formats weekdays nicely.
 * 
 * @author henrik.oscarsson
 *
 */
public class WeekdayFormatterHelper {

	/**
	 * Formats the weekdays in the form " days: Mon, Tue, Thu"
	 * 
	 * @param weekdays, a comma separated string of weekdays,usually the value stored in the database.
	 * @return
	 */
	public String formatWeekdays(String weekdays) {
	
		// Do some initial checking that we really have something to work with
		if (weekdays == null || "".equals(weekdays))
			return "";
	
		weekdays = weekdays.trim();
		if ("".equals(weekdays))
			return "";
	
		// The weekday names that we are using
		String[] dayName = { "", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" };
	
		// The resulting string
		StringBuilder result = new StringBuilder();
	
		// If the string starts with a "," we remove that first
		if (weekdays.startsWith(",", 0))
			weekdays = weekdays.substring(1);
	
		// Put all the weekday values in an array
		String[] days = weekdays.split(",");
	
		// Get the last weekday value
		int endDay = Integer.parseInt(days[days.length - 1]);
		if (endDay > 7 || endDay < 0)
			return "";
	
		// Get the first weekday value
		int startDay = Integer.parseInt(days[0]);
		if (startDay < 1 || startDay > 7)
			return "";
	
		// If the bid is for only one day, just output that day
		if (startDay == endDay) {
			result.append(dayName[startDay]);
			result.append(", ");
		}
		// If the distance between the first and the last is the same as the
		// length
		// then the days in that range are consecutive
		else if (endDay - startDay == days.length - 1) {
			result.append(dayName[startDay]);
			result.append(" - ");
			result.append(dayName[endDay]);
			result.append(", ");
		}
		// Or just output a comma separated list of days
		else {
			for (int i = 0; i < days.length; i++) {
				result.append(dayName[Integer.parseInt(days[i])]);
				result.append(", ");
			}
		}

		// Remove the last ", " and return
		return result.substring(0, result.length() - 2);
	}
}
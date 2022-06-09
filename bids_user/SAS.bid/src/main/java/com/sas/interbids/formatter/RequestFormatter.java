package com.sas.interbids.formatter;

import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

import com.jeppesen.carmen.crewweb.interbids.bo.RequestLogEntry;
import com.jeppesen.carmen.crewweb.interbids.customization.api.RequestFormatterInterface;

public class RequestFormatter extends Formatter implements
		RequestFormatterInterface {

	@Override
	public String formatDetails(RequestLogEntry requestLogEntry) {
		StringBuilder s = new StringBuilder();
//		String requestType = requestLogEntry.getType();
//		append(s, localize(requestType), " - ");

		String startDate = requestLogEntry.getPropertyValue("startDate");

		requestLogEntry.hasProperty("nr_of_days");
		
		int nrOfDays = Integer.parseInt(requestLogEntry
				.getPropertyValue("nr_of_days"));
		
		try {
			String endDate = calculateEndDate(startDate, nrOfDays);
			appendRequestPeriod(s, startDate, endDate);

		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		return s.toString();
	}

	private String calculateEndDate(String startDate, int nrOfDays)
			throws ParseException {

		DateFormat df = new SimpleDateFormat("yyyy-MM-dd");
		Date start;
		start = df.parse(startDate);

		// Date start = startDate.getDate();
		Calendar c = Calendar.getInstance();
		c.setTime(start);
		c.add(Calendar.DATE, nrOfDays);
		c.add(Calendar.MINUTE, -1);
		
		String end = null;
		
		if(c!= null){
			end = df.format(c.getTime());
		}
		
		return end;
	}
}

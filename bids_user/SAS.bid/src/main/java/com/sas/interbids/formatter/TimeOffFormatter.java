package com.sas.interbids.formatter;

import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.FormatterContext;
import com.jeppesen.carmen.crewweb.interbids.customization.api.FormatterInterface;
import com.sas.interbids.base.SasConstants;

public class TimeOffFormatter extends Formatter implements FormatterInterface {

	@Override
	public String format(BidData bidData, FormatterContext arg1) {
		StringBuilder s = super.format(bidData);
		String startDateWithTime = bidData.getAllByPropertyType("date_time_start").get(0).get("start");
		String endDateWithTime = bidData.getAllByPropertyType("date_time_end").get(0).get("end");
		String from = formatDateTime(startDateWithTime, SasConstants.dateTimeFormat);
		String to = formatDateTime(endDateWithTime, SasConstants.dateTimeFormat);

		appendPeriod(s, from, to);
		return s.toString();
	}
}
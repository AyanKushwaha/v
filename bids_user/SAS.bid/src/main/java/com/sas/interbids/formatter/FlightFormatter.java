package com.sas.interbids.formatter;

import static com.sas.interbids.base.SasConstants.START_DATE;
import static com.sas.interbids.base.SasConstants.getValidityPeriodFieldValue;

import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.FormatterContext;
import com.jeppesen.carmen.crewweb.interbids.customization.api.FormatterInterface;
import com.sas.interbids.base.SasConstants;

public class FlightFormatter extends Formatter implements FormatterInterface {

	@Override
	public String format(BidData bidData, FormatterContext arg1) {
		StringBuilder s = super.format(bidData);

		String flightNumber = localize("bidFormat.flight.number", bidData.get(SasConstants.FLIGHT_NUMBER));
		String startDate =  localize("bidFormat.departure.date",formatDate(getValidityPeriodFieldValue(bidData, START_DATE), SasConstants.dateFormat));
		append(s, flightNumber);
		appendSeparator(s);
		append(s, startDate);

		return s.toString();
	}
}

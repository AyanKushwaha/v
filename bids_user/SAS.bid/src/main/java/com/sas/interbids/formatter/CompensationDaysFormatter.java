package com.sas.interbids.formatter;

import static com.sas.interbids.base.SasConstants.COMP_DAY_PERIOD;
import static com.sas.interbids.base.SasConstants.compensationDaysTypeOfCompDay;

import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.FormatterContext;
import com.jeppesen.carmen.crewweb.interbids.customization.api.FormatterInterface;

public class CompensationDaysFormatter extends Formatter implements FormatterInterface {

	@Override
	public String format(BidData bidData, FormatterContext arg1) {
        StringBuilder s = super.format(bidData);
        appendFrom(s);
        appendDate(s, bidData);
        appendTimeInterval(s, bidData);
        appendCompDayPeriod(s, bidData);
        appendSpace(s);
        appendTypeOfCompDay(s, bidData);
        return s.toString();
	}
	
	private void appendCompDayPeriod(StringBuilder s, BidData bidData) {
		String compDayPeriod = bidData.get(COMP_DAY_PERIOD);
		if (compDayPeriod != null) {
			String message = localize("bidFormat.compDayPeriod", compDayPeriod);
			appendSeparator(s);
			append(s, message);
		} 
	}

	private void appendTypeOfCompDay(StringBuilder s, BidData bidData) {
		String typeOfCompDay = bidData.get(compensationDaysTypeOfCompDay.get(bidData.getType()));
		if (typeOfCompDay != null) {
			String message = localize("bidFormat.typeOfCompDay", typeOfCompDay);
			append(s, message);
		}
	}

}

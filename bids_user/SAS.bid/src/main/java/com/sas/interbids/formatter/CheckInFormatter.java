package com.sas.interbids.formatter;

import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.FormatterContext;
import com.jeppesen.carmen.crewweb.interbids.customization.api.FormatterInterface;

public class CheckInFormatter extends Formatter implements FormatterInterface  {

	@Override
	public String format(BidData bidData, FormatterContext arg1) {
        StringBuilder s = super.format(bidData);
        appendCheckInTime(s, bidData);
		appendPeriod(s, bidData);
        return s.toString();
	}

}

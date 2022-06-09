package com.sas.interbids.formatter;

import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.FormatterContext;
import com.jeppesen.carmen.crewweb.interbids.customization.api.FormatterInterface;

public class PreferencesFormatter extends Formatter implements FormatterInterface {

	@Override
	public String format(BidData bidData, FormatterContext arg1) {
		StringBuilder s = new StringBuilder();
		append(s, localize(bidData.getType()));
		return s.toString();
	}
}


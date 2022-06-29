package com.sas.career.formatter;

import com.jeppesen.carmen.crewweb.jmpframework.customization.api.Bid;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.BidDetailsFormatter;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.FormatterContext;
import com.jeppesen.jcms.crewweb.common.util.CWLog;

public class BaseTypeFormatter extends Formatter implements BidDetailsFormatter {
	
	private static final CWLog LOG = CWLog.getLogger(BaseTypeFormatter.class);
	
	public static final String KEY = "base";
	public static final String BASE_TRANSLATION_KEY = "base_translation_formatter";

	@Override
	public String formatDetails(Bid bid, FormatterContext arg1) {
		StringBuffer buff = new StringBuffer();

		try {
			buff.append(format(BASE_TRANSLATION_KEY, formatValuesetValue(getValueEntry(bid, KEY))));
		} catch (Exception e) {
			LOG.error(e.getMessage());

			buff.append(format(BID_VALUE_NOT_FOUND));
		}

		return buff.toString();
	}
}

package com.sas.career.formatter;

import com.jeppesen.carmen.crewweb.jmpframework.customization.api.Bid;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.BidDetailsFormatter;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.FormatterContext;
import com.jeppesen.jcms.crewweb.common.util.CWLog;

public class ATPLConfirmationTypeFormatter extends Formatter implements BidDetailsFormatter {
	
	private static final CWLog LOG = CWLog.getLogger(ATPLConfirmationTypeFormatter.class);
	
//	private static final String KEY = "types";
//	private static final String BASE_TRANSLATION_KEY = "base_translation_formatter";

    @Override
    public String formatDetails(Bid arg0, FormatterContext arg1) {
        StringBuffer buff = new StringBuffer();
        
//        try {
//			buff.append(format(BASE_TRANSLATION_KEY, getValueEntry(bid, KEY)));
//		} catch (Exception e) {
//			LOG.error(e.getMessage());
//			
//			buff.append(format(BID_VALUE_NOT_FOUND));
//		}
        
        return buff.toString();
    }
}

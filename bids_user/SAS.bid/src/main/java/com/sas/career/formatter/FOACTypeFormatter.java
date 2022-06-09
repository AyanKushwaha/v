package com.sas.career.formatter;

import com.jeppesen.carmen.crewweb.jmpframework.customization.api.Bid;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.BidDetailsFormatter;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.FormatterContext;
import com.jeppesen.jcms.crewweb.common.util.CWLog;

public class FOACTypeFormatter extends Formatter implements BidDetailsFormatter {
	
	private static final CWLog LOG = CWLog.getLogger(FOACTypeFormatter.class);
	
	public static final String KEY = "foac_qual";
	public static final String QUAL_TRANSLATION_KEY = "fo_ac_translation_formatter";

    @Override
    public String formatDetails(Bid bid, FormatterContext formatterContext) {
        StringBuffer buff = new StringBuffer();
        
        try {
        	// Removed until UICMP-3047 is fixed
//        	buff.append(format(PRIORITY_TRANSLATION_KEY, bid.getPrio()));
			buff.append(format(QUAL_TRANSLATION_KEY, formatValuesetValue(getValueEntry(bid, KEY))));
		} catch (Exception e) {
			LOG.error(e.getMessage());
			
			buff.append(format(BID_VALUE_NOT_FOUND));
		}
        
        return buff.toString();
    }
}

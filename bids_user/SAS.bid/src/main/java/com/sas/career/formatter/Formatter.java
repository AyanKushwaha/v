package com.sas.career.formatter;

import java.text.Format;
import java.text.MessageFormat;
import java.text.SimpleDateFormat;

import com.jeppesen.carmen.crewweb.jmpframework.customization.api.Bid;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.BidProperty;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.PropertyEntry;
import com.jeppesen.jcms.crewweb.common.context.aware.LocalizationAware;
import com.jeppesen.jcms.crewweb.common.exception.CWInvalidDateException;
import com.jeppesen.jcms.crewweb.common.exception.CWRuntimeException;
import com.jeppesen.jcms.crewweb.common.localization.Localization;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;
import com.jeppesen.jcms.crewweb.common.util.CWLog;

public class Formatter implements LocalizationAware{
	
	protected Localization localization;
	private static final CWLog LOG = CWLog.getLogger(Formatter.class);
	
	protected static final String BID_VALUE_NOT_FOUND = "bid_no_value_found";
	protected static final String PRIORITY_TRANSLATION_KEY = "priority_translation_formatter";
    
	@Override
	public void setLocalization(Localization localization) {
		this.localization = localization;
	}
	
    protected String getValueEntry(Bid bid, String key) throws CWRuntimeException {
    	for (BidProperty property : bid.getProperties()) {
    		for (PropertyEntry entry : property.getPropertyEntries()) {
    			if (entry.getName().equalsIgnoreCase(key)) {
    				return entry.getValue();
    			}
    		}
    	}
    	
    	throw new CWRuntimeException("Value for key: " + key + " not found");
    }
    
    
	public String format(String key, Object... arguments) {
		String s = localization.MSGR(key);
		return MessageFormat.format(s, arguments);
	}
	
	protected String formatValuesetValue(String value) {
    	int index = value.lastIndexOf("+");
    	if (index >= 0) {
    		return value.substring(index+1);
    	} else {
    		return value;
    	}
    }
	
	protected String getDateTimeWithFormat(String dateString, String format) {
		Format formatter = new SimpleDateFormat(format);

		if (dateString != null) {
			CWDateTime date = null;
			try {
				date = CWDateTime.parseISODateTime(dateString);
				return formatter.format(date.getDate());
			} catch (CWInvalidDateException e) {
				LOG.error("Not able to parse date. Invalid date format: " + dateString);
				LOG.error(e.getMessage());
				return dateString;
			}
		} else {
			return dateString;
		}
	}
    
}

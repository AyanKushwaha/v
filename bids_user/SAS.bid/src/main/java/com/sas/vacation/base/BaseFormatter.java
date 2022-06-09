package com.sas.vacation.base;

import java.text.Format;
import java.text.SimpleDateFormat;
import java.util.List;

import com.jeppesen.carmen.backendfacade.xmlschema.jmp.v2.JaxbEntry;
import com.jeppesen.carmen.backendfacade.xmlschema.jmp.v2.JaxbResultingBid;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.Bid;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.BidProperty;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.PropertyEntry;
import com.jeppesen.jcms.crewweb.common.context.aware.LocalizationAware;
import com.jeppesen.jcms.crewweb.common.exception.CWInvalidDateException;
import com.jeppesen.jcms.crewweb.common.localization.Localization;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;
import com.jeppesen.jcms.crewweb.common.util.CWLog;

public class BaseFormatter implements LocalizationAware {

	protected LocalizationHelper LOC;
	private static final CWLog LOG = CWLog.getLogger(BaseFormatter.class);

	protected static final String dateFormat = "ddMMMyy";

	@Override
	public void setLocalization(Localization loc) {
		this.LOC = new LocalizationHelper(loc);
	}

	protected String makeBold(String string) {
		return "<b>" + string + "</b>";
	}


	protected void appendAlternative(List<BidProperty> properties, StringBuffer s, int alternative) {

		BidProperty bidProperty = properties.get(alternative);

		String start = "";
		String end = "";
		String vacationDays = "";
		for (PropertyEntry entry : bidProperty.getPropertyEntries()) {
			if (entry.getName().equalsIgnoreCase("start")) {
				start = entry.getValue();
			} else if (entry.getName().equalsIgnoreCase("end")) {
				end = entry.getValue();
			} else if (entry.getName().equalsIgnoreCase("actual_number_of_days")) {
				vacationDays = entry.getValue();
			}
		}
		if (!start.equalsIgnoreCase("")) {
			s.append(LOC.format("vacation_alt_format", LOC.format("validity_period_alt" + alternative), getDateTimeWithFormat(start, dateFormat), getDateTimeWithFormat(end, dateFormat)));
			if (!vacationDays.equalsIgnoreCase("")) {
				s.append(LOC.format("vacation_days_format", vacationDays));
			}
			s.append("<br>");
		} else {
			return;
		}
	}

	protected void appendNumberOfDays(StringBuffer s, Bid bid, String entryKey) {

		for (BidProperty properties : bid.getProperties()) {
		for (PropertyEntry entry : properties.getPropertyEntries()) {
			if (entry.getName().equalsIgnoreCase(entryKey)) {
				String value = entry.getValue();
				if (value != null && !value.isEmpty()) {
					s.append(LOC.format("num_days_format", LOC.format("num_days"), value));
				}
			}
		}
		}
	}

	protected String getDateTimeWithFormat(String dateString, String format) {
		Format formatter = new SimpleDateFormat(format);

		if (dateString != null) {
			CWDateTime date = null;
			try {
				date = CWDateTime.parseISODate(dateString);
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

	protected void appendComment(StringBuffer s, Bid bid) {

		for (BidProperty property : bid.getProperties()) {
			for (PropertyEntry entry : property.getPropertyEntries()) {
				if (entry.getName().equalsIgnoreCase("vacation_comment")) {
					if (!entry.getValue().equalsIgnoreCase("\"\"")) {
						s.append(LOC.format("vacation_comment_format", LOC.format("vacation_comment"), trimStringFromQuotes(entry.getValue())));
					}
				}
			}
		}
	}
	
	private String trimStringFromQuotes(String str) {
		if (!str.isEmpty() && str.charAt(0) == '"' && str.charAt(str.length()-1) == '"') {
			return str.substring(1, str.length()-1);
		} else {
			return str;
		}
	}
}


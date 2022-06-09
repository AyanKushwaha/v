package com.sas.interbids.formatter;

import static com.sas.interbids.base.SasConstants.CHECKIN_OPTIONS;
import static com.sas.interbids.base.SasConstants.CHECKOUT_OPTIONS;
import static com.sas.interbids.base.SasConstants.END_DATE;
import static com.sas.interbids.base.SasConstants.END_TIME;
import static com.sas.interbids.base.SasConstants.START_DATE;
import static com.sas.interbids.base.SasConstants.START_TIME;
import static com.sas.interbids.base.SasConstants.TIMES_PER_ROSTER;
import static com.sas.interbids.base.SasConstants.CHECK_IN_TIME;
import static com.sas.interbids.base.SasConstants.CHECK_OUT_TIME;
import static com.sas.interbids.base.SasConstants.getTimeIntervalFieldValue;
import static com.sas.interbids.base.SasConstants.getValidityPeriodFieldValue;

import java.util.Locale;

import org.joda.time.format.DateTimeFormatter;

import com.jeppesen.carmen.crewweb.framework.context.aware.DateTimeUtilAware;
import com.jeppesen.carmen.crewweb.framework.util.DateTimeUtil;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.jcms.crewweb.common.context.aware.LocalizationAware;
import com.jeppesen.jcms.crewweb.common.localization.Localization;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;
import com.sas.interbids.base.SasConstants;
import com.sas.interbids.formatter.helper.LocalizationHelper;
import com.sas.interbids.formatter.helper.WeekdayFormatterHelper;

public class Formatter implements LocalizationAware, DateTimeUtilAware {

    protected LocalizationHelper localization;
    protected DateTimeUtil dateTimeUtil;

    protected WeekdayFormatterHelper weekdayFormatter;

    public Formatter() {
        weekdayFormatter = new WeekdayFormatterHelper();
    }

    @Override
    public void setLocalization(Localization localization) {
        this.localization = new LocalizationHelper(localization);
    }

    protected String localize(String key, Object... arguments) {
        String locale = localization.format(key, arguments);
        return locale;
    }

    protected StringBuilder format(BidData bidData) {
        StringBuilder s = new StringBuilder();
        appendBidType(s, bidData);
        return s;
    }

    protected void append(StringBuilder s, Object... values) {
        for (Object value : values) {
            s.append(value);
        }
    }

    protected void appendSpace(StringBuilder s) {
        s.append(" ");
    }

    protected void appendSeparator(StringBuilder s) {
        s.append(", ");
    }

    protected void appendFrom(StringBuilder s) {
        append(s, localize("from"), " ");
    }

    protected void appendTo(StringBuilder s) {
        append(s, localize("to"), " ");
    }

    private void appendBidType(StringBuilder s, BidData bidData) {
        append(s, localize(bidData.getType()), " - ");
    }

    protected void appendPeriod(StringBuilder s, BidData bidData) {
        String from = formatDate(getValidityPeriodFieldValue(bidData, START_DATE), SasConstants.dateFormat);
        String to = formatDate(getValidityPeriodFieldValue(bidData, END_DATE), SasConstants.dateFormat);
        appendPeriod(s, from, to);
    }

    protected void appendPeriodWithTime(StringBuilder s, BidData bidData) {
//        String format = "ddMMyy";
        String from = formatDate(getValidityPeriodFieldValue(bidData, START_DATE), SasConstants.dateFormat);
        String startTime = getValidityPeriodFieldValue(bidData, START_TIME);
        String to = formatDate(getValidityPeriodFieldValue(bidData, END_DATE), SasConstants.dateFormat);
        String endTime = getValidityPeriodFieldValue(bidData, END_TIME);
        appendPeriodWithTime(s, from, startTime, to, endTime);
    }

    protected void appendDate(StringBuilder s, BidData bidData) {
        String date = formatDate(getValidityPeriodFieldValue(bidData, START_DATE), SasConstants.dateFormat);
        append(s, date);
    }

    protected void appendRequestPeriod(StringBuilder s, String startDate, String endDate) {
        String from = formatDate(startDate, SasConstants.dateFormat);
        String to = formatDate(endDate, SasConstants.dateFormat);
        append(s, localize("request_period", from, to));
    }
    
    protected void appendRequestPeriodDateAndTime(StringBuilder s, String startDateTime, String endDateTime) {
        String from = formatDateTime(startDateTime, SasConstants.dateTimeFormat);
        String to = formatDateTime(endDateTime, SasConstants.dateTimeFormat);
        appendPeriod(s, from, to);
    }
    
    protected static String formatDateTime(String dateTimeString, String format) {
        if (dateTimeString != null) {
            CWDateTime date = CWDateTime.parseISODateTime(dateTimeString);
            DateTimeFormatter fmt = CWDateTime.getDateTimeFormatter(format, Locale.ENGLISH);
            return fmt.print(date.getDateTime());
        } else {
            return dateTimeString;
        }
    }


    protected static String formatDate(String dateString, String format) {
        if (dateString != null) {
            CWDateTime date = CWDateTime.parseISODate(dateString);
            DateTimeFormatter fmt = CWDateTime.getDateTimeFormatter(format, Locale.ENGLISH);
            return fmt.print(date.getDateTime());
        } else {
            return dateString;
        }
    }

    protected void appendPeriod(StringBuilder s, Object from, Object to) {
        append(s, localize("from"), " ", from);
        if (to != null) {
            appendSpace(s);
            append(s, localize("to"), " ", to);
        } else {
            appendSpace(s);
            append(s, localize("to"), " ", localize("UFN"));
        }
    }

    protected void appendPeriodWithTime(StringBuilder s, Object from, Object startTime, Object to, Object endTime) {
        append(s, localize("from"), " ", from, " ", startTime);
        if (to != null) {
            appendSpace(s);
            append(s, localize("to"), " ", to, " ", endTime);
        } else {
            appendSpace(s);
            append(s, localize("to"), " ", localize("UFN"));
        }
    }

    protected void appendTimeInterval(StringBuilder s, BidData bidData) {
        String from = getTimeIntervalFieldValue(bidData, START_TIME);
        String to = getTimeIntervalFieldValue(bidData, END_TIME);
        appendSeparator(s);
        append(s, from, " - ", to);
    }

    protected void appendCheckinOption(StringBuilder s, BidData bidData) {
        String option = bidData.get(CHECKIN_OPTIONS);
        s.append(localize("bidFormat.checkin_option." + option));
        appendSpace(s);
    }
    
    protected void appendCheckoutOption(StringBuilder s, BidData bidData) {
        String option = bidData.get(CHECKOUT_OPTIONS);
        s.append(localize("bidFormat.checkout_option." + option));
        appendSpace(s);
    }

    protected void appendTimePerRoster(StringBuilder s, BidData bidData) {
        String timePerRoster = bidData.get(TIMES_PER_ROSTER);
        if (timePerRoster != null) {
            String message = localize("bidFormat.timePerRoster", timePerRoster);
            appendSeparator(s);
            append(s, message);
        }
    }
    
    protected void appendDayOfWeek(StringBuilder s, BidData bidData) {
    	String dayOfWeek = bidData.get(BidData.BID_PROPERTY_PREFIX + "weekday_option.weekday_option");
    	if (dayOfWeek != null) {
    		String day = intToWeekDay(Integer.parseInt(dayOfWeek));
    		s.append(localization.format("for_day_of_week", day));
    		appendSeparator(s);
    	} 
    }

    protected void appendCheckInTime(StringBuilder s, BidData bidData) {
        String IOTime = bidData.get(CHECK_IN_TIME);
        if (IOTime != null) {
            String message = localize("bidFormat.checkintime", IOTime);
            appendSpace(s);
            append(s, message);
        }
    }

    protected void appendCheckOutTime(StringBuilder s, BidData bidData) {
        String IOTime = bidData.get(CHECK_OUT_TIME);
        if (IOTime != null) {
            String message = localize("bidFormat.checkouttime", IOTime);
            appendSpace(s);
            append(s, message);
        }
    }
    
    protected void appendStopLengths(StringBuilder s, BidData bidData) {
        String stopLengthMin = bidData.get(SasConstants.STOP_LENGTH_MIN);
        if (stopLengthMin == null) {
           stopLengthMin = SasConstants.DEFAULT_STOP_LENGTH_MIN;
        }
        String stopLengthMax = bidData.get(SasConstants.STOP_LENGTH_MAX);
        if (stopLengthMax == null) {
           stopLengthMax = SasConstants.DEFAULT_STOP_LENGTH_MAX;
        }
        String message = String.format(" - Min: %s Max: %s - ", stopLengthMin, stopLengthMax);
        append(s, message);
    }
    
    protected String intToWeekDay(int weekday) {
        switch (weekday) {
        case 1:
            return "Mon";
        case 2:
            return "Tue";
        case 3:
            return "Wed";
        case 4:
            return "Thu";
        case 5:
            return "Fri";
        case 6:
            return "Sat";
        case 7:
            return "Sun";
        default:
            break;
        }
        return null;

    }

	@Override
	public void setDateTimeUtil(DateTimeUtil arg0) {
		this.dateTimeUtil = arg0;
	}
}

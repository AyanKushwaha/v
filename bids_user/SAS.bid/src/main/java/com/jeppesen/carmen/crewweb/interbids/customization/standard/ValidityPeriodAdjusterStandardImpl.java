package com.jeppesen.carmen.crewweb.interbids.customization.standard;

import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import com.jeppesen.carmen.crewweb.framework.bo.Period;
import com.jeppesen.carmen.crewweb.interbids.bo.Bid;
import com.jeppesen.carmen.crewweb.interbids.bo.BidGroup;
import com.jeppesen.carmen.crewweb.interbids.bo.BidProperty;
import com.jeppesen.carmen.crewweb.interbids.customization.ValidityPeriodAdjuster;
import com.jeppesen.carmen.crewweb.interbids.customization.api.MutableBidData;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;
import com.sas.interbids.base.SasConstants;

/**
 * Standard bid copier.
 */
public class ValidityPeriodAdjusterStandardImpl implements
ValidityPeriodAdjuster {

	private static final List<String> validity_properties = Arrays.asList(
			"validity_period", "validity_period_with_time",
			"f4_weekend_off_period_cc", "f4_weekend_off_period_fd",
			"f4_weekend_off_period_fd_crj", "string_days_off",
			"single_validity_period", "validity_period_no_ufn", 
			"date_time_start", "date_time_end", "single_date",
			"validity_period_days_for_prod");
	private static final Set<String> compensation_days_bid = new HashSet<String>();

	static {
		compensation_days_bid.add("compensation_days_fd");
		compensation_days_bid.add("compensation_days_cc");
	}

	/**
	 * {@inheritDoc}
	 */
	public void adjustPeriod(BidGroup bidGroup, Bid bid, Period period) {
		String category = bidGroup.getCategory();
		if ("current".equals(category)) {
			CWDateTime bidStart = period.getStart();
			CWDateTime bidEnd = period.getEnd();
			List<BidProperty> bidProperties = bid.getBidProperties();
			for (BidProperty bidProperty : bidProperties) {
				if ("flight".equals(bid.getType()) && validity_properties.contains(bidProperty.getType())) {
					String start = bidProperty.getBidPropertyEntryValue("startDate");
					bidStart = CWDateTime.parseISODate(start);
					String end = start + " 23:59";
					bidEnd = CWDateTime.parseISODateTime(end);
				} else if ("time_off".equals(bid.getType()) && validity_properties.contains(bidProperty.getType())) {
					String start = bidProperty.getBidPropertyEntryValue("start");
					if (start != null) {
						bidStart = CWDateTime.parseISODateTime(start);
					}
					String end = bidProperty.getBidPropertyEntryValue("end");
					if (end != null) {
						bidEnd = CWDateTime.parseISODateTime(end);
					}
				} else if (validity_properties.contains(bidProperty.getType())) {
					String start = bidProperty.getBidPropertyEntryValue("start");
					bidStart = CWDateTime.parseISODateTime(start);
					String end = bidProperty.getBidPropertyEntryValue("end");
					if (compensation_days_bid.contains(bid.getType())) {
						end = getCompEndDate(bid, bidStart);
					}
					if (end != null) {
						bidEnd = CWDateTime.parseISODateTime(end);
					} else {
						bidEnd = null;
					}

				}
			}
			bid.setStartDate(bidStart);
			bid.setEndDate(bidEnd);
		}
		if ("standing".equals(category)) {
			bid.setStartDate(period.getStart());
			bid.setEndDate(null);
		}
		if ("template".equals(category)) {
			bid.setStartDate(null);
			bid.setEndDate(null);
		}
	}

	private String getCompEndDate(Bid bid, CWDateTime startDay) {
		String days = "";
		for (BidProperty bp : bid.getBidProperties()) {
			if (bp.getType().equalsIgnoreCase("comp_day_period")) {
				days = bp.getBidPropertyEntryValue("day_period");
			}
		}
		try {
			int d = Integer.parseInt(days);
			CWDateTime end = CWDateTime.create(startDay.getMilliSeconds());
			end.addDays(d);
			end.removeMinutes(1);
			return CWDateTime.formatISODateTime(end);
		} catch (Exception e) {
			return "";
		}
	}
}

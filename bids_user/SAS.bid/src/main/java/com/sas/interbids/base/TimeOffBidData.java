package com.sas.interbids.base;

import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;



public class TimeOffBidData extends BidDataExt {
	
	public TimeOffBidData(BidData bidData) {
		super(bidData);
	}
	
	private String WEEKDAY_PROPERTY = "weekday_and_time.";
	
	public String getWeekdayFromDate() {
		return super.getPropertyValue(WEEKDAY_PROPERTY + "from_weekday");
	}
	
	public String getWeekdayToDate() {
		return super.getPropertyValue(WEEKDAY_PROPERTY + "to_weekday");
	}
	
	public String getWeekdayFromTime() {
		return super.getPropertyValue(WEEKDAY_PROPERTY + "startTime");
	}
	
	public String getWeekdayToTime() {
		return super.getPropertyValue(WEEKDAY_PROPERTY + "endTime");
	}
	
}
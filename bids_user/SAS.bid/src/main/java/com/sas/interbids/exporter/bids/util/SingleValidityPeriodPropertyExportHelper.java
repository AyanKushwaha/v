package com.sas.interbids.exporter.bids.util;

import static com.sas.interbids.base.SasConstants.COMP_DAY_PERIOD;
import static com.sas.interbids.base.SasConstants.START;
import static com.sas.interbids.base.SasConstants.getValidityPeriodFieldValue;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

import com.jeppesen.carmen.crewweb.framework.util.DateTimeUtil;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRow;
import com.sas.interbids.exporter.SasExportConstants;

public class SingleValidityPeriodPropertyExportHelper {
	
	private SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm");

	private DateTimeUtil dateTimeUtil;

	/**
	 * Constructor, initialize the corehelper
	 */
	public SingleValidityPeriodPropertyExportHelper() {
		this.dateTimeUtil = new DateTimeUtil();
	}

	// @Override
	public void setDateTimeUtil(DateTimeUtil dateTimeUtil) {
		this.dateTimeUtil = dateTimeUtil;
	}

	public void populate(ExportRow row, BidData bidData) {
		
		String compDayPeriod = bidData.get(COMP_DAY_PERIOD);

		String startDate = getValidityPeriodFieldValue(bidData, START);
		Date parsedStartDate;
		try {
			parsedStartDate = sdf.parse(startDate);
			
			Calendar c = Calendar.getInstance();
			c.setTime(parsedStartDate);
			c.add(Calendar.DATE, Integer.parseInt(compDayPeriod)-1);
			int year = c.get(Calendar.YEAR);
			int month = c.get(Calendar.MONTH);
			int day = c.get(Calendar.DATE);
			c.set(year, month, day, 23, 59);
			String endDate = sdf.format(c.getTime());
			
			//  We need to convert the dates from "2010-01-01 00:00" to "01JAN2010 00:00"
			String startAbsTime = dateTimeUtil.convertISODateTimeStringToAbstimeString(startDate);
			String endAbsTime = dateTimeUtil.convertISODateTimeStringToAbstimeString(endDate);

			
			row.set(SasExportConstants.ABS1, startAbsTime);
			row.set(SasExportConstants.ABS2, endAbsTime);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

}

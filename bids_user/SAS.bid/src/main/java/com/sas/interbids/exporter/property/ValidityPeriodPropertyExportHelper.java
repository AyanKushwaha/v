package com.sas.interbids.exporter.property;


import static com.sas.interbids.base.SasConstants.END;
import static com.sas.interbids.base.SasConstants.START;
import static com.sas.interbids.base.SasConstants.getValidityPeriodFieldValue;

import com.jeppesen.carmen.crewweb.framework.util.DateTimeUtil;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRow;
import com.sas.interbids.exporter.SasExportConstants;

public class ValidityPeriodPropertyExportHelper {

	
	private DateTimeUtil dateTimeUtil;

	/**
	 * Constructor, initialize the corehelper
	 */
	public ValidityPeriodPropertyExportHelper() {
		this.dateTimeUtil = new DateTimeUtil();
	}


//	@Override
	public void setDateTimeUtil(DateTimeUtil dateTimeUtil) {
		this.dateTimeUtil = dateTimeUtil;
	}
	
	/**
	 * This method handles all validity_period properties containing two dates.
	 * It retrieves the start and end dates and sets the corresponding columns in the export row
	 *
	 * @param row,	 the export row to populate
	 * @param bidData, the bid data for the current bid
	 */
	public void populate(ExportRow row, BidData bidData) {
		String startDate = getValidityPeriodFieldValue(bidData, START);

		String endDate = getValidityPeriodFieldValue(bidData, END);
		if (endDate == null) {
			endDate = "2035-12-31 23:59";
		}

		//  We need to convert the dates from "2010-01-01 00:00" to "01JAN2010 00:00"
		String startAbsTime = dateTimeUtil.convertISODateTimeStringToAbstimeString(startDate);
		String endAbsTime = dateTimeUtil.convertISODateTimeStringToAbstimeString(endDate);

		row.set(SasExportConstants.ABS1, startAbsTime);
		row.set(SasExportConstants.ABS2, endAbsTime);
	}


}


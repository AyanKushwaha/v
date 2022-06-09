package com.sas.interbids.exporter.bids.util;

import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRow;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;
import com.sas.interbids.exporter.SasExportConstants;

/**
 * Helper to add Period data to export format.
 */
public class PeriodExportHelper {

	public static void populate(ExportRow row, BidData bidData) {
		
		String ufn_date = "2035-12-31 23:59";
		
		CWDateTime startDate = bidData.getStartDate();
		CWDateTime endDate = bidData.getEndDate();
		
		if (endDate == null) {
			endDate = CWDateTime.parseISODateTime(ufn_date);
		}
		row.set(SasExportConstants.ABS1, getAbstime(startDate, true));
		row.set(SasExportConstants.ABS2, getAbstime(endDate, true));
	}

	/**
	 * This method is to convert the date to DDMMMYY.
	 * 
	 * @param date
	 *            The default date to use for conversion
	 * @param withTime
	 *            True if time is presented
	 * @return The DDMMMYY or DDMMMYY HH:MM format
	 */
	private static String getAbstime(CWDateTime date, boolean withTime) {
		String result = "";
		if (withTime) {
			result = CWDateTime.formatDateTime(date);
		} else {
			String[] dateTime = CWDateTime.formatDateTime(date).split(" ");
			result = dateTime[0];
		}
		return result.toUpperCase();
	}

}

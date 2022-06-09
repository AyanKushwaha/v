/**
 * 
 */
package com.sas.interbids.exporter.bids;

import com.jeppesen.carmen.crewweb.framework.util.DateTimeUtil;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidExporter;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportContext;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRow;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRowCreator;
import com.sas.interbids.exporter.SasExportConstants;
import com.sas.interbids.exporter.bids.util.PointsPropertyExportHelper;

public class TimeOffExporter implements BidExporter {

	private DateTimeUtil dateTimeUtil;

	public TimeOffExporter() {
		super();
		dateTimeUtil = new DateTimeUtil();
	}

	@Override
	public void setContext(ExportContext exportContext) {}

	@Override
	public void processBidData(BidData bidData, ExportRowCreator exportRowCreator) {
		ExportRow row = exportRowCreator.createRow();
		System.out.println("bid created by " + bidData.getCreatedBy());
		row.set(SasExportConstants.TYPE, "TimeOff");
		String startDateWithTime = bidData.getAllByPropertyType("date_time_start").get(0).get("start");
		String endDateWithTime = bidData.getAllByPropertyType("date_time_end").get(0).get("end");
		setDateTime(row, startDateWithTime, SasExportConstants.ABS1);
		setDateTime(row, endDateWithTime, SasExportConstants.ABS2);

		PointsPropertyExportHelper.populate(row, bidData);
	}

	private void setDateTime(ExportRow row, String dateTime, String exportColumn) {
		if (dateTime != null) {
			String absValue = dateTimeUtil.convertISODateTimeStringToAbstimeString(dateTime);
			row.set(exportColumn, absValue);
		}
	}

}

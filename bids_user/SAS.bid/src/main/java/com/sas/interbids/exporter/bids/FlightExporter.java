/**
 * 
 */
package com.sas.interbids.exporter.bids;

import static com.sas.interbids.base.SasConstants.getValidityPeriodFieldValue;

import com.jeppesen.carmen.crewweb.framework.util.DateTimeUtil;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidExporter;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportContext;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRow;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRowCreator;
import com.sas.interbids.base.SasConstants;
import com.sas.interbids.exporter.SasExportConstants;
import com.sas.interbids.exporter.bids.util.PointsPropertyExportHelper;

public class FlightExporter implements BidExporter {

	private DateTimeUtil dateTimeUtil;

	public FlightExporter() {
		super();
		dateTimeUtil = new DateTimeUtil();
	}

	@Override
	public void processBidData(BidData bidData, ExportRowCreator rowCreator) {

		/*
		Example:
		"10286",0,0,0,"NrOfBids",1,0,0:00,0:00,01Jan1986 00:00,01Jan1986 00:00,"",false,
		"10286",1,0,3,"Flight",0,0,0:00,0:00,09DEC2017 00:00,09DEC2017 23:59,"SK99999",false,
		 */

		String startDate = getValidityPeriodFieldValue(bidData, SasConstants.START_DATE);
		String startDateWithTime = startDate + " 00:00";
		String endDateWithTime= startDate + " 23:59";

		ExportRow row = rowCreator.createRow();
		row.set(SasExportConstants.TYPE, "Flight");
		row.set(SasExportConstants.STR1, bidData.get(SasConstants.FLIGHT_NUMBER));
		setDateTime(row, SasExportConstants.ABS1, startDateWithTime);
		setDateTime(row, SasExportConstants.ABS2, endDateWithTime);

		PointsPropertyExportHelper.populate(row, bidData);
	}

	private void setDateTime(ExportRow row, String exportColumn, String dateTime) {
		if (dateTime != null) {
			String absValue = dateTimeUtil.convertISODateTimeStringToAbstimeString(dateTime);
			row.set(exportColumn, absValue);
		}
	}

	@Override
	public void setContext(ExportContext arg0) {}
}

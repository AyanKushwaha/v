package com.sas.interbids.exporter.bids.util;

import static com.sas.interbids.base.SasConstants.compensationDaysTypeOfCompDay;

import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRow;
import com.sas.interbids.exporter.SasExportConstants;

public class CompensationDayCodePropertyExportHelper {
	
	public void populate(ExportRow row, BidData bidData) {
		String type = bidData.get(compensationDaysTypeOfCompDay.get(bidData.getType()));
		row.set(SasExportConstants.STR1, type);
	}

}

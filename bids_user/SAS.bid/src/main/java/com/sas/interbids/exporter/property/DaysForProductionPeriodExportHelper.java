package com.sas.interbids.exporter.property;

import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRow;
import com.sas.interbids.base.SasConstants;
import com.sas.interbids.exporter.SasExportConstants;

public class DaysForProductionPeriodExportHelper {
	
	public void populate(ExportRow row, BidData bidData) {
		String start = bidData.get(SasConstants.LEG_DURATION_START);
		String end = bidData.get(SasConstants.LEG_DURATION_END);
		row.set(SasExportConstants.ABS1, start);
		row.set(SasExportConstants.ABS2, end);
	}

}

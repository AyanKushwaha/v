package com.sas.interbids.exporter.bids.util;

import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRow;
import com.sas.interbids.base.SasConstants;
import com.sas.interbids.exporter.SasExportConstants;

public class PointsPropertyExportHelper {

	public static void populate(ExportRow row, BidData bidData) {
		String priority = bidData.get(SasConstants.PRIORITY);
		row.set(SasExportConstants.POINTS, priority);
	}
}

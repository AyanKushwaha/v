package com.sas.interbids.exporter.bids;

import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidExporter;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportContext;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRow;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRowCreator;
import com.sas.interbids.exporter.SasExportConstants;
import com.sas.interbids.exporter.bids.util.PointsPropertyExportHelper;
import com.sas.interbids.exporter.property.ValidityPeriodPropertyExportHelper;

public class LastMinuteLOAExporter  implements BidExporter {

	@Override
	public void processBidData(BidData bidData, ExportRowCreator rowCreator) {
		
		ExportRow row = rowCreator.createRow();
		row.set(SasExportConstants.TYPE, "TimeOff");
		PointsPropertyExportHelper.populate(row, bidData);
		new ValidityPeriodPropertyExportHelper().populate(row, bidData);
		row.set(SasExportConstants.INT2, 99);
		row.set(SasExportConstants.STR1, "LA42");
	}
	

	@Override
	public void setContext(ExportContext exportContext) {
	}
}

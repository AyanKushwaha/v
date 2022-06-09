package com.sas.interbids.exporter.bids;

import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidExporter;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportContext;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRow;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRowCreator;
import com.sas.interbids.base.SasConstants;
import com.sas.interbids.exporter.SasExportConstants;
import com.sas.interbids.exporter.bids.util.PeriodExportHelper;
import com.sas.interbids.exporter.bids.util.PointsPropertyExportHelper;

public class CheckOutExporter implements BidExporter {

	public CheckOutExporter() {
		super();
	}

	@Override
	public void processBidData(BidData bidData, ExportRowCreator rowCreator) {
		ExportRow row = rowCreator.createRow();

		//Bidtyp and bid data
		row.set(SasExportConstants.TYPE, "CheckOut");
		row.set(SasExportConstants.REL1, "00:00");
		row.set(SasExportConstants.REL2, bidData.get(SasConstants.CHECK_OUT_TIME));

		//Validity period handling
		PeriodExportHelper.populate(row, bidData);

		//Priority handling
		PointsPropertyExportHelper.populate(row, bidData);
	}

	@Override
	public void setContext(ExportContext exportContext) {
	}


}

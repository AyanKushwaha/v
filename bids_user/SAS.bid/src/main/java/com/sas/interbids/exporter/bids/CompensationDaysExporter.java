package com.sas.interbids.exporter.bids;

import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidExporter;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportContext;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRow;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRowCreator;
import com.sas.interbids.exporter.SasExportConstants;
import com.sas.interbids.exporter.bids.util.CompensationDayCodePropertyExportHelper;
import com.sas.interbids.exporter.bids.util.SingleValidityPeriodPropertyExportHelper;

public class CompensationDaysExporter  implements BidExporter {

	private final static String BIDTYPE = "TimeOff";

	@Override
	public void processBidData(BidData bidData, ExportRowCreator rowCreator) {
		
		ExportRow row = rowCreator.createRow();
		row.set(SasExportConstants.TYPE, BIDTYPE);
		row.set(SasExportConstants.INT2, 99);
		new SingleValidityPeriodPropertyExportHelper().populate(row, bidData);
		new CompensationDayCodePropertyExportHelper().populate(row, bidData);
	}
	
	@Override
	public void setContext(ExportContext exportContext) {
	}
}

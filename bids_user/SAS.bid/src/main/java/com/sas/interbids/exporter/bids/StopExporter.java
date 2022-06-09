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

public class StopExporter implements BidExporter {

	public StopExporter() {
		super();
	}

	@Override
	public void processBidData(BidData bidData, ExportRowCreator rowCreator) {
		ExportRow row = rowCreator.createRow();
		row.set(SasExportConstants.TYPE, "Stop");
		row.set(SasExportConstants.STR1, bidData.get(SasConstants.STOP_DESTINATION));
		row.set(SasExportConstants.ABS1, bidData.get(SasConstants.STOP_DESTINATION));

		/*
		* NOTE: Since comboboxes doesn't support default values, we show
		* the default value in the UI in 'emptyText' and set the default
		* value here instead.
		*/
		String stopLengthMin = bidData.get(SasConstants.STOP_LENGTH_MIN);
		if (stopLengthMin == null) {
			stopLengthMin = SasConstants.DEFAULT_STOP_LENGTH_MIN;
		}
		String stopLengthMax = bidData.get(SasConstants.STOP_LENGTH_MAX);
		if (stopLengthMax == null) {
			stopLengthMax = SasConstants.DEFAULT_STOP_LENGTH_MAX;
		}

		row.set(SasExportConstants.REL1, stopLengthMin);
		row.set(SasExportConstants.REL2, stopLengthMax);

		PeriodExportHelper.populate(row, bidData);
		PointsPropertyExportHelper.populate(row, bidData);
	}

	@Override
	public void setContext(ExportContext arg0) {
		// TODO Auto-generated method stub

	}
}

package com.sas.interbids.exporter.bids;


import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidExporter;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportContext;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRow;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRowCreator;
import com.sas.interbids.base.SasConstants;
import com.sas.interbids.exporter.SasExportConstants;
import com.sas.interbids.exporter.bids.util.PeriodExportHelper;

public class PreferencesExporter implements BidExporter {

	@Override
	public void processBidData(BidData bidData, ExportRowCreator rowCreator) {

		/*
		Example:
		"11294",0,0,0,"NrOfBids",1,0,0:00,0:00,01Jan1986 00:00,01Jan1986 00:00,"",false,
		"11294",1,0,0,"Preference",0,0,0:00,0:00,01DEC2017 00:00,31DEC2035 23:59,"early_ends_pref",false,
		 */


		ExportRow row = rowCreator.createRow();
		row.set(SasExportConstants.TYPE, SasConstants.ETAB_TYPE_PREFERENCE);
		String preferenceType = bidData.getType();
		row.set(SasExportConstants.STR1, preferenceType);
		PeriodExportHelper.populate(row, bidData);
	}

	@Override
	public void setContext(ExportContext exportContext) {
	}
}
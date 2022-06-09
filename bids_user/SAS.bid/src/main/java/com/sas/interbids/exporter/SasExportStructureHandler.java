package com.sas.interbids.exporter;

import java.util.List;

import com.jeppesen.carmen.crewweb.interbids.customization.api.ETableExportStructureHandler;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ETableStructure;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportDataContainer;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRow;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRowCreator;

public class SasExportStructureHandler implements ETableExportStructureHandler{

	@Override
	public void registerETableStructure(ETableStructure etableStructure) {
		etableStructure.addColumn(SasExportConstants.EMPNO, ETableStructure.DataTypes.STRING, null);
		etableStructure.addColumn(SasExportConstants.SEQNO, ETableStructure.DataTypes.INTEGER, null);
		etableStructure.addColumn(SasExportConstants.SUBSEQNO, ETableStructure.DataTypes.INTEGER, 0);
		etableStructure.addColumn(SasExportConstants.POINTS, ETableStructure.DataTypes.INTEGER, 0);
		etableStructure.addColumn(SasExportConstants.TYPE, ETableStructure.DataTypes.STRING, null);
		etableStructure.addColumn(SasExportConstants.INT1, ETableStructure.DataTypes.INTEGER, 0);
		etableStructure.addColumn(SasExportConstants.INT2, ETableStructure.DataTypes.INTEGER, 0);
		etableStructure.addColumn(SasExportConstants.REL1, ETableStructure.DataTypes.RELTIME, "0:00");
		etableStructure.addColumn(SasExportConstants.REL2, ETableStructure.DataTypes.RELTIME, "0:00");
		etableStructure.addColumn(SasExportConstants.ABS1, ETableStructure.DataTypes.ABSTIME, "01Jan1986 00:00");
		etableStructure.addColumn(SasExportConstants.ABS2, ETableStructure.DataTypes.ABSTIME, "01Jan1986 00:00");
		etableStructure.addColumn(SasExportConstants.STR1, ETableStructure.DataTypes.STRING, "");
		etableStructure.addColumn(SasExportConstants.BOOL1, ETableStructure.DataTypes.BOOLEAN, "false");
	}

	/**
	 * Add all common values to the bid row(s) just created
	 * In this case we add the user id and the sequence number of each bid
	 */
	@Override
	public void postProcessBidLinesForOneBid(ExportDataContainer dataContainer, List<ExportRow> rows) {
		String userId = dataContainer.get(ExportDataContainer.USERID);
		int bidIndex = dataContainer.getAsInteger(ExportDataContainer.BID_INDEX) + 1;

		for (ExportRow row : rows) {
			row.set(SasExportConstants.EMPNO, userId);
			row.set(SasExportConstants.SEQNO, bidIndex);
		}
	}

	/**
	 * When a new bidgroup is being selected we want to print a row
	 * that contains the number of bids for this bidgroup.
	 * <p/>
	 * In the Sas case each user only has one bidgroup so it
	 * is kind of a workaround to print the number of bids per user...
	 */
	@Override
	public void handleNewBidGroupSection(ExportDataContainer dataContainer, ExportRowCreator rowStore) {
		String userId = dataContainer.get(ExportDataContainer.USERID);
		String noOfBids = dataContainer.get(ExportDataContainer.NUMBER_OF_BIDS);

		// Create the export: 
		// "001091", 0, 0, 0, "NrOfBids", 5, 0, 00:00, 00:00, 01Jan1986 00:00, 01Jan1986 00:00, "", false,
		ExportRow row = rowStore.createRow();
		row.set(SasExportConstants.EMPNO, userId);
		row.set(SasExportConstants.SEQNO, 0);
		row.set(SasExportConstants.SUBSEQNO, 0);
		row.set(SasExportConstants.POINTS, 0);
		row.set(SasExportConstants.TYPE, "NrOfBids");
		row.set(SasExportConstants.INT1, noOfBids);
	}

	@Override
	public void handleNewBidSection(ExportDataContainer dataContainer, ExportRowCreator rowStore) {
	}

	@Override
	public void handleNewUserSection(ExportDataContainer dataContainer, ExportRowCreator rowStore) {
	}

	@Override
	public void postProcessBidGroupLines(ExportDataContainer arg0,
			List<ExportRow> arg1) {
		// TODO Auto-generated method stub
		
	}

}

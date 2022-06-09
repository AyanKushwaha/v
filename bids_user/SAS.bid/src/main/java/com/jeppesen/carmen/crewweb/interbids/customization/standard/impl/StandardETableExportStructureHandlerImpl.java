package com.jeppesen.carmen.crewweb.interbids.customization.standard.impl;

import java.util.List;

import com.jeppesen.carmen.crewweb.interbids.customization.api.ETableExportStructureHandler;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ETableStructure;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportDataContainer;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRow;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ExportRowCreator;
import com.jeppesen.carmen.crewweb.interbids.customization.standard.ETableExportConstants;

public class StandardETableExportStructureHandlerImpl implements ETableExportStructureHandler {

    /**
     * {@inheritDoc}
     */
    public void registerETableStructure(ETableStructure etableStructure) {
        etableStructure.addColumn(ETableExportConstants.CREWID, ETableStructure.DataTypes.STRING, null);

        etableStructure.addColumn(ETableExportConstants.STATUS, ETableStructure.DataTypes.STRING, null);
        etableStructure.addColumn(ETableExportConstants.TYPE, ETableStructure.DataTypes.STRING, null);

        etableStructure.addColumn(ETableExportConstants.BIDGROUPIDX, ETableStructure.DataTypes.INTEGER, null);
        etableStructure.addColumn(ETableExportConstants.LINEIDX, ETableStructure.DataTypes.INTEGER, null);
        etableStructure.addColumn(ETableExportConstants.SUBLINEIDX, ETableStructure.DataTypes.INTEGER, null);

        etableStructure.addColumn(ETableExportConstants.INT1, ETableStructure.DataTypes.INTEGER, 0);
        etableStructure.addColumn(ETableExportConstants.INT2, ETableStructure.DataTypes.INTEGER, 0);

        etableStructure.addColumn(ETableExportConstants.STR1, ETableStructure.DataTypes.STRING, null);
        etableStructure.addColumn(ETableExportConstants.STR2, ETableStructure.DataTypes.STRING, null);

        etableStructure.addColumn(ETableExportConstants.REL1, ETableStructure.DataTypes.RELTIME, "0:00");
        etableStructure.addColumn(ETableExportConstants.REL2, ETableStructure.DataTypes.RELTIME, "0:00");

        etableStructure.addColumn(ETableExportConstants.ABS1, ETableStructure.DataTypes.ABSTIME, "01JAN1986");
        etableStructure.addColumn(ETableExportConstants.ABS2, ETableStructure.DataTypes.ABSTIME, "01JAN1986");

        etableStructure.addColumn(ETableExportConstants.LIMIT, ETableStructure.DataTypes.INTEGER, 0);
    }

    public void handleNewUserSection(ExportDataContainer dataContainer, ExportRowCreator rowStore) {
        // CO Example:
        // "YF01003","","CrewNGroups",0,0,1,1,0,"","",0.0,0.0,1986-01-01T00:00:00.000+01:00,1986-01-01T00:00:00.000+01:00,0,

        ExportRow row = rowStore.createRow();
        row.set(ETableExportConstants.CREWID, dataContainer.get("userId"));
        row.set(ETableExportConstants.TYPE, "CrewNGroups");
        
        row.set(ETableExportConstants.BIDGROUPIDX, 0);
        row.set(ETableExportConstants.LINEIDX, 0);
        row.set(ETableExportConstants.SUBLINEIDX, 0);

        row.set(ETableExportConstants.INT1, dataContainer.getAsInteger("numberOfBidGroups"));
    }

    public void handleNewBidGroupSection(ExportDataContainer dataContainer, ExportRowCreator rowStore) {
        // CO Example:
        // "YF01003","","GroupNLines",0,0,0,1,1,"SUBMITTED","FLIGHT",0.0,0.0,1986-01-01T00:00:00.000+01:00,1986-01-01T00:00:00.000+01:00,0,

        ExportRow row = rowStore.createRow();
        row.set(ETableExportConstants.CREWID, dataContainer.get("userId"));
        row.set(ETableExportConstants.TYPE, "GroupNLines");
        row.set(ETableExportConstants.INT1, dataContainer.getAsInteger("numberOfBids"));
        
        row.set(ETableExportConstants.BIDGROUPIDX, dataContainer.getAsInteger("bidGroup.index"));
        row.set(ETableExportConstants.LINEIDX, 0);
        row.set(ETableExportConstants.SUBLINEIDX, 0);
        
        row.set(ETableExportConstants.STR1, dataContainer.get("bidGroup.submitted") != null ? "SUBMITTED" : "");
        row.set(ETableExportConstants.STR2, dataContainer.get("bidGroup.type"));
    }

    public void handleNewBidSection(ExportDataContainer dataContainer, ExportRowCreator rowStore) {
    }

    public void postProcessBidLinesForOneBid(ExportDataContainer dataContainer, List<ExportRow> rows) {
        String userId = dataContainer.get("userId");
        int bidGroupIndex = dataContainer.getAsInteger("bidGroup.index");
        int bidIndex = dataContainer.getAsInteger("bid.index");

        int subLineIndex = 0;
        for (ExportRow row : rows) {
            row.set(ETableExportConstants.CREWID, userId);
            row.set(ETableExportConstants.BIDGROUPIDX, bidGroupIndex);
            row.set(ETableExportConstants.LINEIDX, bidIndex);
            row.set(ETableExportConstants.SUBLINEIDX, subLineIndex);
        }
    }

	@Override
	public void postProcessBidGroupLines(ExportDataContainer arg0,
			List<ExportRow> arg1) {
		// TODO Auto-generated method stub
		
	}
}

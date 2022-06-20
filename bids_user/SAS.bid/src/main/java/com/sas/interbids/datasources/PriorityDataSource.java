package com.sas.interbids.datasources;

import static com.jeppesen.carmen.crewweb.backendfacade.customization.datasource.DataSourceContainerFieldFactory.createContainer;
import static com.jeppesen.carmen.crewweb.backendfacade.customization.datasource.DataSourceContainerFieldFactory.createField;
import static com.jeppesen.carmen.crewweb.backendfacade.customization.datasource.DataSourceContainerFieldFactory.createRecord;

import java.util.Map;

import com.jeppesen.carmen.crewweb.backendfacade.bo.DataSourceContainer;
import com.jeppesen.carmen.crewweb.backendfacade.bo.DataSourceDescriptor;
import com.jeppesen.carmen.crewweb.backendfacade.customization.api.DataSourceProcessorInterface;
import com.jeppesen.carmen.crewweb.backendfacade.customization.datasource.DataSourceContainerRecord;
import com.jeppesen.carmen.crewweb.backendfacade.customization.datasource.MutableDataSourceContainer;
import com.jeppesen.jcms.crewweb.common.context.aware.LocalizationManagerAware;
import com.jeppesen.jcms.crewweb.common.localization.Localization;
import com.jeppesen.jcms.crewweb.common.localization.LocalizationManager;

/**
 * Custom datasource defining priority 
 */

public class PriorityDataSource implements DataSourceProcessorInterface, LocalizationManagerAware{

	private Localization localization;

	@Override
    public DataSourceContainer process(DataSourceDescriptor descriptor, Map<String, String> requestParams) {
        final MutableDataSourceContainer container = createContainer();
                
        container.addField(createField("name"));
        container.addField(createField("value"));
        
        container.addRecord(newRecord(localization.MSGR("priority_3"), "3"));
        container.addRecord(newRecord(localization.MSGR("priority_2"), "2"));
        container.addRecord(newRecord(localization.MSGR("priority_1"), "1"));
        
        return container;
    }

	private DataSourceContainerRecord newRecord(String name, String value) {
		DataSourceContainerRecord dataRecord = createRecord();
		dataRecord.setField("name", name);
		dataRecord.setField("value", value);
		return dataRecord;
	}

	@Override
	public void setLocalizationManager(LocalizationManager localizationManager) {
		localization = localizationManager.getServerLocalization();
	}
}

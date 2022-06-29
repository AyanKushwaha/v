package com.sas.career.valuesets;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.jeppesen.carmen.crewweb.backendfacade.bo.DataSourceContainer;
import com.jeppesen.carmen.crewweb.backendfacade.bo.DataSourceDescriptor;
import com.jeppesen.carmen.crewweb.backendfacade.customization.api.DataSourceProcessorInterface;
import com.jeppesen.carmen.crewweb.backendfacade.customization.datasource.DataSourceContainerField;
import com.jeppesen.carmen.crewweb.backendfacade.customization.datasource.DataSourceContainerFieldFactory;
import com.jeppesen.carmen.crewweb.backendfacade.customization.datasource.DataSourceContainerRecord;
import com.jeppesen.carmen.crewweb.backendfacade.customization.datasource.MutableDataSourceContainer;
import com.jeppesen.carmen.crewweb.framework.business.DataSourceLookupHelper;
import com.jeppesen.carmen.crewweb.framework.context.aware.DataSourceLookupHelperAware;


public class FBIDTypeValuesetProcessorClass implements DataSourceProcessorInterface, DataSourceLookupHelperAware {
	
	private DataSourceLookupHelper dataSourceLookupHelper;
	
	private static final String fbid_datasource = "valueset.fbid_qual";
	private static final String value_key = "value";
	
	private static final String entry_name = "name";
	private static final String entry_value = "value";

	@Override
	public DataSourceContainer process(DataSourceDescriptor arg0,
			Map<String, String> arg1) {
		
		MutableDataSourceContainer result = DataSourceContainerFieldFactory.createContainer();
		DataSourceContainerField nameField = DataSourceContainerFieldFactory.createField(entry_name);
		DataSourceContainerField valueField = DataSourceContainerFieldFactory.createField(entry_value);
		
		result.addField(nameField);
		result.addField(valueField);
		
		DataSourceContainer dataSource = dataSourceLookupHelper.getDataSource(fbid_datasource);
		List<HashMap<String,Object>> data = dataSource.getData();
		
		for (HashMap<String,Object> d : data) {
			if (d.containsKey(value_key)) {
				DataSourceContainerRecord dataRecord = DataSourceContainerFieldFactory.createRecord();
				Object object = d.get(value_key);
				dataRecord.setField(nameField, trimValue(object));
				dataRecord.setField(valueField, object);
				result.addRecord(dataRecord);
				
			}
		}
		
		return result;
		
	}
	
	private void consumeDataSource() {
//		dataSourceLookupHelper.
	}
	
	private String trimValue(Object obj) {
		if (obj instanceof String) {
			String value = (String)obj;
			int index = value.lastIndexOf("+");
	    	if (index >= 0) {
	    		return value.substring(index+1);
	    	} else {
	    		return value;
	    	}
			
		} else {
			return obj.toString();
		}
	}

	@Override
	public void setDataSourceLookupHelper(DataSourceLookupHelper arg0) {
		this.dataSourceLookupHelper = arg0;
	}

}
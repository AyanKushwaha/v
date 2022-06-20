package com.sas.career.valuesets;

import java.util.Map;

import com.jeppesen.carmen.crewweb.backendfacade.bo.DataSourceContainer;
import com.jeppesen.carmen.crewweb.backendfacade.bo.DataSourceDescriptor;
import com.jeppesen.carmen.crewweb.backendfacade.customization.api.DataSourceProcessorInterface;
import com.jeppesen.carmen.crewweb.framework.business.DataSourceLookupHelper;
import com.jeppesen.carmen.crewweb.framework.context.aware.DataSourceLookupHelperAware;



public class FOACTypeValueSetProcessorClass implements DataSourceProcessorInterface, DataSourceLookupHelperAware {
	
	private DataSourceLookupHelper dataSourceLookupHelper;

	@Override
	public DataSourceContainer process(DataSourceDescriptor arg0,
			Map<String, String> arg1) {
		
		DataSourceContainer dataSource = dataSourceLookupHelper.getDataSource("valueset.foac_qual");
		return dataSource;
	}
	
	@Override
	public void setDataSourceLookupHelper(
			DataSourceLookupHelper dataSourceLookupHelper) {
		this.dataSourceLookupHelper = dataSourceLookupHelper;
		
	}
}
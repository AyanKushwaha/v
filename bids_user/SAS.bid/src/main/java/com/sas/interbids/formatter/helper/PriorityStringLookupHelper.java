package com.sas.interbids.formatter.helper;

import java.util.HashMap;
import java.util.List;

import com.jeppesen.carmen.crewweb.backendfacade.bo.DataSourceContainer;
import com.jeppesen.carmen.crewweb.framework.business.DataSourceLookupHelper;

public class PriorityStringLookupHelper {

	private DataSourceLookupHelper dataSourceLookupHelper;
	
	public PriorityStringLookupHelper(DataSourceLookupHelper dataSourceLookupHelper){
		this.dataSourceLookupHelper = dataSourceLookupHelper;
	}


	public String getPriorityString(String priority) {

		DataSourceContainer dataSource = dataSourceLookupHelper.getDataSource("custom.priority");

		String priorityName = "";

		List<HashMap<String, Object>> data = dataSource.getData();
		for (HashMap<String, Object> hashMap : data) {
			if (hashMap.get("value").equals(priority)) {
				priorityName = (String) hashMap.get("name");

				break;
			}
		}

		return priorityName;

	}

}

package com.jeppesen.carmen.crewweb.vacation.customization.standard;

import java.util.HashMap;
import java.util.Map;

import com.jeppesen.carmen.crewweb.framework.business.facade.UserCustomizationAPI;
import com.jeppesen.carmen.crewweb.framework.context.aware.UserCustomizationAPIAware;
import com.jeppesen.carmen.crewweb.backendfacade.customization.api.DataSourceParametersHandler;

public class DisabledDaysParameterHandlerClass implements
		DataSourceParametersHandler, UserCustomizationAPIAware {
	private UserCustomizationAPI userCustomizationApi;
	
	@Override
	public Map<String, String> getParameters(Map<String, String> arg0) {
		Map<String, String> result = new HashMap<String, String>();
		result.put("crewId", userCustomizationApi.getUserId());
		return result;
	}

	@Override
	public void setUserCustomizationAPI(UserCustomizationAPI userCustomizationApi) {
		this.userCustomizationApi = userCustomizationApi;
		
	}

}

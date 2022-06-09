package com.sas.career.valuesets;

import java.util.HashMap;
import java.util.Map;

import com.jeppesen.carmen.crewweb.backendfacade.customization.api.DataSourceValueSetParametersHandler;
import com.jeppesen.carmen.crewweb.backendfacade.service.ValueSetParameters;


public class CCACQualificationParameterHandlerClass implements DataSourceValueSetParametersHandler {


    public CCACQualificationParameterHandlerClass() {
    }

    @Override
    public Map<String, String> getParameters(Map<String, String> requestParams) {
        Map<String, String> result = new HashMap<String, String>();
        result.put(ValueSetParameters.ENTRY_NAME, "ccac_qual");
        result.put(ValueSetParameters.BIDDING_CREW_ID, requestParams.get(ValueSetParameters.BIDDING_CREW_ID));
        result.put(ValueSetParameters.AUTHENTICATED_CREW_ID, requestParams.get(ValueSetParameters.AUTHENTICATED_CREW_ID));
        result.put(ValueSetParameters.AWARDING_CATEGORY, requestParams.get(ValueSetParameters.AWARDING_CATEGORY));
        result.put(ValueSetParameters.AWARDING_TYPE, requestParams.get(ValueSetParameters.AWARDING_TYPE));
        result.put(ValueSetParameters.BID_TYPE, requestParams.get(ValueSetParameters.BID_TYPE));
        result.put(ValueSetParameters.BID_GROUP_ID, requestParams.get(ValueSetParameters.BID_GROUP_ID));
        return result;
    }

}

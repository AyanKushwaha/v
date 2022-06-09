package com.sas.interbids.formatter;

import java.util.HashMap;
import java.util.List;

import com.jeppesen.carmen.crewweb.backendfacade.bo.DataSourceContainer;
import com.jeppesen.carmen.crewweb.framework.business.DataSourceLookupHelper;
import com.jeppesen.carmen.crewweb.framework.context.aware.DataSourceLookupHelperAware;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.FormatterContext;
import com.jeppesen.carmen.crewweb.interbids.customization.api.FormatterInterface;
import com.jeppesen.jcms.crewweb.common.context.aware.Initializable;
import com.sas.interbids.base.SasConstants;

public class StopFormatter extends Formatter implements FormatterInterface, DataSourceLookupHelperAware, Initializable {

	private HashMap<String, String> destinationValueToNameMap = null;

	private DataSourceLookupHelper dataSourceLookupHelper;

	@Override
	public String format(BidData bidData, FormatterContext arg1) {
		StringBuilder s = super.format(bidData);
		String destinationValue = bidData.get(SasConstants.STOP_DESTINATION);

		String destinationName = destinationValue;
		if (destinationValueToNameMap.containsKey(destinationValue)) {
			destinationName = destinationValueToNameMap.get(destinationValue);
		}

		append(s, destinationName);
		appendStopLengths(s, bidData);
		appendPeriod(s, bidData);
		return s.toString();
	}

	@Override
	public void setDataSourceLookupHelper(DataSourceLookupHelper dataSourceLookupHelper) {
		this.dataSourceLookupHelper = dataSourceLookupHelper;

	}

	@Override
	public void initialize() {
		destinationValueToNameMap = new HashMap<>();
		DataSourceContainer dataSource = dataSourceLookupHelper.getDataSource("etab.stop_destination");
		List<HashMap<String, Object>> data = dataSource.getData();
		for (HashMap<String, Object> hashMap : data) {
			String value = (String) hashMap.get("value");
			String name = (String) hashMap.get("name");
			destinationValueToNameMap.put(value, name);
		}
	}
}

/**
 * 
 */
package com.sas.interbids.datasources;

import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.SortedMap;
import java.util.TreeMap;

import com.jeppesen.carmen.crewweb.backendfacade.bo.Activity;
import com.jeppesen.carmen.crewweb.backendfacade.bo.DataSourceContainer;
import com.jeppesen.carmen.crewweb.backendfacade.bo.DataSourceDescriptor;
import com.jeppesen.carmen.crewweb.backendfacade.bo.Duty;
import com.jeppesen.carmen.crewweb.backendfacade.bo.ImmutableTrip;
import com.jeppesen.carmen.crewweb.backendfacade.customization.api.DataSourceProcessorInterface;
import com.jeppesen.carmen.crewweb.backendfacade.customization.datasource.DataSourceContainerField;
import com.jeppesen.carmen.crewweb.backendfacade.customization.datasource.DataSourceContainerFieldFactory;
import com.jeppesen.carmen.crewweb.backendfacade.customization.datasource.DataSourceContainerRecord;
import com.jeppesen.carmen.crewweb.backendfacade.customization.datasource.MutableDataSourceContainer;
import com.jeppesen.carmen.crewweb.framework.bo.Period;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserCustomizationAPI;
import com.jeppesen.carmen.crewweb.framework.context.aware.UserCustomizationAPIAware;
import com.jeppesen.carmen.crewweb.interbids.business.facade.ImmutableTripAPI;
import com.jeppesen.carmen.crewweb.interbids.context.aware.ImmutableTripAPIAware;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;

/**
 * Feed flight number and date(s)
 *
 */

public class FlightNumberDataSource implements UserCustomizationAPIAware,
DataSourceProcessorInterface, ImmutableTripAPIAware {

	private ImmutableTripAPI trips;
	private UserCustomizationAPI userCustomizationAPI;


	@Override
	public DataSourceContainer process(DataSourceDescriptor descriptor,
			Map<String, String> requestParams) {

		MutableDataSourceContainer container = DataSourceContainerFieldFactory.createContainer();
		Collection<? extends ImmutableTrip> allTrips = trips.getAllTrips();

		SortedMap<String, String> hset = new TreeMap<>();

		DataSourceContainerField flightDisplayNameField = DataSourceContainerFieldFactory.createField("displayName");
		DataSourceContainerField flightNumberField = DataSourceContainerFieldFactory.createField("flightnumber");

		container.addField(flightDisplayNameField);
		container.addField(flightNumberField);

		for (ImmutableTrip t : allTrips) {
			if ("flight".equals(t.getAttribute("type"))) {
				List<Duty> duties = t.getDuties();
				for (Duty d : duties) {
					for (Activity a : d.getActivities()) {
						if ("flight".equals(a.getAttribute("type")) && flightStartDateWithinBiddingPeriod(a.getAttribute("startdate_utc"))) {
							String flightNumber = a.getAttribute("number");
							String startStation = a.getAttribute("startstation");
							String endStation = a.getAttribute("endstation");
							hset.put("SK" + flightNumber, "SK" + flightNumber + " (" + startStation + " - " + endStation + ")");
						}
					}
				}
			}
		}
		Iterator<Entry<String, String>> setIterator = hset.entrySet().iterator();
		while(setIterator.hasNext()){
			Entry<String, String> entry = setIterator.next();
			DataSourceContainerRecord dataRecord = DataSourceContainerFieldFactory.createRecord();
			dataRecord.setField(flightNumberField, entry.getKey());
			dataRecord.setField(flightDisplayNameField, entry.getValue());
			container.addRecord(dataRecord);
		}
		return container;
	}

	@Override
	public void setUserCustomizationAPI(
			UserCustomizationAPI userCustomizationAPI) {
		this.userCustomizationAPI = userCustomizationAPI;
	}

	//Only display flights for the actual bidding period
	private boolean flightStartDateWithinBiddingPeriod(String flightStartDate) {
		String userId = userCustomizationAPI.getUserId();
		String periodType = "standard";
		Period period = userCustomizationAPI.getCurrentPeriodForUser(userId, periodType);
		CWDateTime bidPeriodStart = period.getStart();
		CWDateTime bidPeriodEnd = period.getEnd();
		CWDateTime parsedFlightStartDate = CWDateTime.parseDate(flightStartDate);
		return parsedFlightStartDate.isInIntervall(bidPeriodStart, bidPeriodEnd);
	}

	@Override
	public void setImmutableTripAPI(ImmutableTripAPI trips) {
		this.trips = trips;
	}
}

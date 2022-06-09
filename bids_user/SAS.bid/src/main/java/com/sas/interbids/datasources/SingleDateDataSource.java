/**
 * 
 */
package com.sas.interbids.datasources;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Map;

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

public class SingleDateDataSource implements UserCustomizationAPIAware,
DataSourceProcessorInterface, ImmutableTripAPIAware {

	private ImmutableTripAPI trips;
	private UserCustomizationAPI userCustomizationAPI;

	@Override
	public DataSourceContainer process(DataSourceDescriptor descriptor,
			Map<String, String> requestParams) {

		MutableDataSourceContainer container = DataSourceContainerFieldFactory.createContainer();
		Collection<? extends ImmutableTrip> allTrips = trips.getAllTrips();

		DataSourceContainerField startStationField = DataSourceContainerFieldFactory.createField("startstation");
		DataSourceContainerField endStationField = DataSourceContainerFieldFactory.createField("endstation");
		DataSourceContainerField flightNumberField = DataSourceContainerFieldFactory.createField("flightnumber");
		DataSourceContainerField departureDateField = DataSourceContainerFieldFactory.createField("departuredate");

		container.addField(startStationField);
		container.addField(endStationField);
		container.addField(flightNumberField);
		container.addField(departureDateField);

		List<Activity> activities = new ArrayList<>();
		List<String> activitiesunique = new ArrayList<>();

		for (ImmutableTrip t : allTrips) {
			if ("flight".equals(t.getAttribute("type"))) {
				List<Duty> duties = t.getDuties();
				for (Duty d : duties) {
					for (Activity a : d.getActivities()) {
						if ("flight".equals(a.getAttribute("type")) && flightStartDateWithinBiddingPeriod(a.getAttribute("startdate_utc"))) {
							String flightNumber = a.getAttribute("number");
							String start = a.getAttribute("startdate_local");
							if (!activitiesunique.contains(flightNumber + ", " + start)){
								activitiesunique.add(flightNumber + ", " + start);
								activities.add(a);
							}
						}
					}
				}
			}
		} Collections.sort(activities, new ActivityComparator());

		for (Activity a: activities){
			String startStation = a.getAttribute("startstation");
			String endStation = a.getAttribute("endstation");
			String flightNumber = a.getAttribute("number");
			String start = a.getAttribute("startdate_local");
			DataSourceContainerRecord dataRecord = DataSourceContainerFieldFactory.createRecord();
			dataRecord.setField(startStationField, startStation);
			dataRecord.setField(endStationField, endStation);

			CWDateTime parsedStartDate = CWDateTime.parseDate(start);
			SimpleDateFormat simpleDateFormatOut = new SimpleDateFormat("yyyy-MM-dd");
			String startDate = simpleDateFormatOut.format(parsedStartDate.getDate());

			dataRecord.setField(departureDateField, startDate);
			dataRecord.setField(flightNumberField, "SK" + flightNumber);
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

	private static class ActivityComparator implements Comparator<Activity> {
		@Override
		public int compare(Activity a, Activity b) {
			return a.getAttribute("startdate_local").compareTo(b.getAttribute("startdate_local"));
		}
	}
}

package com.sas.interbids.filter.prefiltering;

import java.util.Map;

import com.jeppesen.carmen.crewweb.backendfacade.bo.ImmutableTrip;
import com.jeppesen.carmen.crewweb.framework.bo.Period;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserCustomizationAPI;
import com.jeppesen.carmen.crewweb.framework.context.aware.UserCustomizationAPIAware;
import com.jeppesen.carmen.crewweb.interbids.customization.api.TripFilterInterface;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;

public class TripInsideBidPeriodPreFiltering implements TripFilterInterface,
		UserCustomizationAPIAware {

	/**
	 * Trip attribute key.
	 */
	static final String TRIP_ATTRIBUTE_KEY = "tripAttribute";

	/**
	 * API used to access user qualifications.
	 */
	private UserCustomizationAPI userCustomizationAPI;

	/**
	 * Map containing configuration parameters for this filter. For this filter
	 * the map is expected to contain the key "tripAttribute".
	 */
	private Map<String, String> parameters;

	/**
	 * {@inheritDoc}
	 */
	@Override
	public boolean isTripAvailable(ImmutableTrip trip) {
		
		Period currentPeriodForUser = userCustomizationAPI.getCurrentPeriodForUser(userCustomizationAPI.getUserId(), "standard");
		CWDateTime periodStart = currentPeriodForUser.getStart();
		return !trip.getStart().isBefore(periodStart);
	}

	@Override
	public void setParameters(Map<String, String> parameters) {
		this.parameters = parameters;
	}

	@Override
	public void setUserCustomizationAPI(
			UserCustomizationAPI userCustomizationAPI) {
		this.userCustomizationAPI = userCustomizationAPI;
	}

}

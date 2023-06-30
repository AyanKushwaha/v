package com.sas.interbids.filter.prefiltering;

import java.util.Collection;
import java.util.HashMap;
import java.util.Map;

import com.jeppesen.carmen.crewweb.backendfacade.bo.ImmutableTrip;
import com.jeppesen.carmen.crewweb.framework.bo.UserAttribute;
import com.jeppesen.carmen.crewweb.framework.bo.UserGroup;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserAPI;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserCustomizationAPI;
import com.jeppesen.carmen.crewweb.framework.context.aware.UserCustomizationAPIAware;
import com.jeppesen.carmen.crewweb.interbids.customization.api.TripFilterInterface;
import com.jeppesen.jcms.crewweb.common.exception.CWRuntimeException;

public class HomebasePrefiltering implements TripFilterInterface,
		UserCustomizationAPIAware {

	/**
	 * Trip attribute key.
	 */
	static final String TRIP_ATTRIBUTE_KEY = "tripAttribute";
	private static final String USER_ATTRIBUTE_KEY_STATION = "station";
	private static final String USER_ATTRIBUTE_KEY_REGION ="region";

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
		String tripAttribute = parameters.get(TRIP_ATTRIBUTE_KEY);
		String station ="";
		String region ="";
		Map<String, String> stationandregion = new HashMap<String, String>();
		stationandregion.put("CPH","SKD");
		stationandregion.put("OSL","SKN");
		stationandregion.put("SVG","SKN");
		stationandregion.put("TRD","SKN");
		stationandregion.put("STO","SKS");
		stationandregion.put("BGO","SKN");


		if (tripAttribute == null) {
			throw new CWRuntimeException(
					"No tripAttribute parameter defined for the qualification trip filter.");
		}
		String tripHomebase = trip.getAttribute(tripAttribute);
		if (tripHomebase == null) {
			return true;
		}

		// Get the user attributes
		String userId = userCustomizationAPI.getUserId();
		UserAPI userAPI = userCustomizationAPI.getUserAPI(userId);
		Collection<UserAttribute> userAttributes = userAPI.getUserAttributes();
		Collection<UserGroup> userGroups = userAPI.getUserGroups();
		for (UserGroup userGroup : userGroups){
			if(userGroup.getGroupName().equals("FD LH")){
				return true;
			}
		}
		

		for (UserAttribute userAttribute : userAttributes) {
			//Find the user attribute Homebase
			String userAttributeName = userAttribute.getName();
			String userAttributeValue = userAttribute.getValue();
			//If the value of the homebase user attribute matches the trip homebase attribute it's a match
			if(userAttributeName.equals(USER_ATTRIBUTE_KEY_STATION)){
				station = userAttributeValue;
			}
			if(userAttributeName.equals(USER_ATTRIBUTE_KEY_REGION)){
				region = userAttributeValue;
			}
		}
		//Check if station is matching with region and if the crew is lent to another region
		if (!stationandregion.get(station).equalsIgnoreCase(region)){
			if (region.equalsIgnoreCase("SKS")){
				station = "STO";
			} else if (region.equalsIgnoreCase("SKN")) {
				station ="OSL";
			} else if (region.equalsIgnoreCase("SKD")) {
				station ="CPH";
			}
		}
		return canFlyFromStation(station, tripHomebase);
	}
        
        public boolean canFlyFromStation(String station, String tripHomebase) {
		return (station.equals(tripHomebase) || (tripHomebase.equals("OSL") && (station.equals("SVG") || station.equals("TRD"))));
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

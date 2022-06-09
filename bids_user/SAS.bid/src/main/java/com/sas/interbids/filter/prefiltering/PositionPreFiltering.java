package com.sas.interbids.filter.prefiltering;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Map;
import java.util.regex.Pattern;

import com.jeppesen.carmen.crewweb.backendfacade.bo.ImmutableTrip;
import com.jeppesen.carmen.crewweb.framework.bo.UserAttribute;
import com.jeppesen.carmen.crewweb.framework.bo.UserQualification;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserAPI;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserCustomizationAPI;
import com.jeppesen.carmen.crewweb.framework.context.aware.UserCustomizationAPIAware;
import com.jeppesen.carmen.crewweb.interbids.customization.api.TripFilterInterface;
import com.jeppesen.jcms.crewweb.common.exception.CWRuntimeException;

public class PositionPreFiltering implements TripFilterInterface,
		UserCustomizationAPIAware {

	/**
	 * Trip attribute key.
	 */
	static final String TRIP_ATTRIBUTE_KEY = "tripAttribute";
	static final String USER_ATTRIBUTE_KEY = "crewrank";
	static final String TRIP_LH_ATTRIBUTE_KEY = "longhaulAttribute";
	
	private static final String CONTRACT_QUAL = "contractvg";

	static final HashSet<String> LONG_HAUL_QUAL = new HashSet<String>();
	
	static {
		LONG_HAUL_QUAL.add("AL");
		LONG_HAUL_QUAL.add("A3");
		LONG_HAUL_QUAL.add("A4");
		LONG_HAUL_QUAL.add("A5");
	}
	

	/**
	 * API used to access user qualifications.
	 */
	private UserCustomizationAPI userCustomizationAPI;

	/**
	 * Map containing configuration parameters for this filter. For this filter
	 * the map is expected to contain the key "tripAttribute".
	 */
	private Map<String, String> parameters;
	
	protected static final Pattern regex_whitespace_comma_whitespace = Pattern.compile("\\s*,\\s*");
	protected static final Pattern regex_comma_whitespace = Pattern.compile(",\\s*");
	protected static final Pattern regex_whitespace = Pattern.compile("\\s");

	/**
	 * {@inheritDoc}
	 */
	@Override
	public boolean isTripAvailable(ImmutableTrip trip) {

		String tripAttribute = parameters.get(TRIP_ATTRIBUTE_KEY);
		if (tripAttribute == null) {
			throw new CWRuntimeException(
					"No tripAttribute parameter defined for the qualification trip filter.");
		}
		String position = trip.getAttribute(tripAttribute);
		if (position == null || position.equalsIgnoreCase("None")) {
			return true;
		}
		
		String[] positions = getListFromString(position);
		if (positions.length == 0) {
			return true;
		}

		String userId = userCustomizationAPI.getUserId();
		UserAPI userAPI = userCustomizationAPI.getUserAPI(userId);
		
		for (UserAttribute userAttribute : userAPI.getUserAttributes()) {
			String userAttributeName = userAttribute.getName();
			if (userAttributeName.equalsIgnoreCase(USER_ATTRIBUTE_KEY)) {
				String userAttributeValue = userAttribute.getValue();
				if (userAttributeValue.equalsIgnoreCase("AS") && isSHQual(userAPI)){
					if (!isTripSH(trip)){
						return false;
					}
				}
				ArrayList<String> crewPositions = getCrewPositions(userAttributeValue, userAPI);
				for (String crewPos : crewPositions) {
					for (String pos : positions) {
						String[] p = regex_whitespace.split(pos);

						int num_pos = Integer.parseInt(p[0]);

						if (num_pos > 0 && crewPos.equalsIgnoreCase(p[p.length-1])) {
							return true;
						}
					}
				}
			}
		}
		return false;
	}
	
	private ArrayList<String> getCrewPositions(String crewPosition, UserAPI userAPI) {
		ArrayList<String> crewPositions = new ArrayList<String>();
		crewPositions.add(crewPosition);
		if (crewPosition.equalsIgnoreCase("AS") && isQualForLongHaulAndShortHaul(userAPI)) {
			crewPositions.add("AH");
		} else if (crewPosition.equalsIgnoreCase("AS") && isSHQual(userAPI)){
			crewPositions.add("AH");
		}
		
		return crewPositions;
	}
	
	private boolean isQualForLongHaulAndShortHaul(UserAPI userAPI) {
		boolean isLongHaul = false;
		boolean isShortHaul = false;
		
		for (UserQualification qual : userAPI.getUserQualifications()) {
			String qualName = qual.getQualificationName();
			if (LONG_HAUL_QUAL.contains(qualName)) {
				isLongHaul = true;
			} else if (!CONTRACT_QUAL.equalsIgnoreCase(qualName) && !LONG_HAUL_QUAL.contains(qualName)) {
				isShortHaul = true;
			}
		}
		
		return isLongHaul && isShortHaul;
	}
	private boolean isTripSH(ImmutableTrip trip){
		String lhAttribute = parameters.get(TRIP_LH_ATTRIBUTE_KEY);
		if (lhAttribute == null) {
			throw new CWRuntimeException(
					"No tripAttribute parameter defined for the qualification trip filter.");
		}

		if (trip.getAttribute(lhAttribute).equalsIgnoreCase("true")){
			return false;
		}
		return true;
	}
	private boolean isSHQual(UserAPI userAPI) {
		boolean isShortHaul = true;
		for (UserQualification qual : userAPI.getUserQualifications()) {
			String qualName= qual.getQualificationName();
			if (LONG_HAUL_QUAL.contains(qualName)){
				isShortHaul = false;
			}
		}		
		return isShortHaul;
	}
	
	public String[] getListFromString(String string) {

		// Remove the extra "," at the beginning of the string in order not the get an empty field at the beginning
		if (string.charAt(0) == ',') {
			string = string.substring(1, string.length());
		}

		// Get a list of all selected weekdays
		String[] list = {}; 
		try {
			list = regex_comma_whitespace.split(string);
			
		} catch (Exception e) {
//			LOG.debug("No weekdays selected");
		}

		return list;
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

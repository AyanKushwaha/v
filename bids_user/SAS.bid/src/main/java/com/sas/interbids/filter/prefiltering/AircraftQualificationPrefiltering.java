package com.sas.interbids.filter.prefiltering;

import java.util.Collection;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import com.jeppesen.carmen.crewweb.backendfacade.bo.ImmutableTrip;
import com.jeppesen.carmen.crewweb.framework.bo.Period;
import com.jeppesen.carmen.crewweb.framework.bo.UserGroup;
import com.jeppesen.carmen.crewweb.framework.bo.UserQualification;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserAPI;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserCustomizationAPI;
import com.jeppesen.carmen.crewweb.framework.context.aware.UserCustomizationAPIAware;
import com.jeppesen.carmen.crewweb.interbids.customization.api.TripFilterInterface;
import com.jeppesen.jcms.crewweb.common.exception.CWRuntimeException;

public class AircraftQualificationPrefiltering implements TripFilterInterface,
		UserCustomizationAPIAware {

	/**
	 * Trip attribute key.
	 */
	static final String TRIP_ATTRIBUTE_KEY_FD = "tripAttribute_fd";
	static final String TRIP_ATTRIBUTE_KEY_CC = "tripAttribute_cc";
	
	static final Set<String> fd_groups = new HashSet<String>();
	static final Set<String> cc_groups = new HashSet<String>();
	
	static {
		fd_groups.add("FD LH");
		fd_groups.add("FD SH FG");
		fd_groups.add("FD SH SKD FG");
		fd_groups.add("FD SH SKN FG");
		fd_groups.add("FD SH SKS FG");
		fd_groups.add("FD SH VG");
		fd_groups.add("FD SH SKD VG");
		fd_groups.add("FD SH SKN VG");
		fd_groups.add("FD SH SKS VG");
		
		cc_groups.add("CC SKD FG");
		cc_groups.add("CC SKD VG");
		cc_groups.add("CC SKN FG");
		cc_groups.add("CC SKN VG");
		cc_groups.add("CC SKS FG");
		cc_groups.add("CC SKS VG");
		cc_groups.add("CC RP");
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

	/**
	 * {@inheritDoc}
	 */
	@Override
	public boolean isTripAvailable(ImmutableTrip trip) {

		String tripAttribute_fd = parameters.get(TRIP_ATTRIBUTE_KEY_FD);
		String tripAttribute_cc = parameters.get(TRIP_ATTRIBUTE_KEY_CC);
		
		if (tripAttribute_fd == null || tripAttribute_cc == null) {
			throw new CWRuntimeException(
					"No tripAttribute parameter defined for the qualification trip filter.");
		}
		String tripAircraftQualification_fd = trip.getAttribute(tripAttribute_fd);
		String tripAircraftQualification_cc = trip.getAttribute(tripAttribute_cc);
		if (tripAircraftQualification_fd == null || tripAircraftQualification_cc == null) {
			return true;
		}

		// Get the user qualifications
		String userId = userCustomizationAPI.getUserId();
		UserAPI userAPI = userCustomizationAPI.getUserAPI(userId);
		Collection<UserQualification> userQualifications = userAPI
				.getUserQualifications();
		
		String trip_qual = getTripQualForUser(userAPI, tripAircraftQualification_fd, tripAircraftQualification_cc);
		
		for (UserQualification userQualification : userQualifications) {

			if (isQualMatch(userQualification, trip_qual) && isTripInQualificationPeriod(userQualification, trip)) {
				return true;
			}
		}
		return false;
	}
	
	private String getTripQualForUser(UserAPI userAPI, String fd_qual, String cc_qual) {
		Period currentPeriodForUser = userCustomizationAPI.getCurrentPeriodForUser(userAPI.getUserId(), "standard");
		for (UserGroup group : userAPI.getUserGroups()) {
			if (group.getStartTime().isBefore(currentPeriodForUser.getStart()) && group.getEndTime().isAfter(currentPeriodForUser.getEnd())) {
				return fd_groups.contains(group.getGroupName()) ? fd_qual : cc_qual;
			}
			
		}
		return "";
	}
	
	private boolean isQualMatch(UserQualification qualification, String tripQualification) {
		if (tripQualification.equalsIgnoreCase(qualification.getQualificationName())) {
			return true;
		} else {
			return false;
		}
	}
	
	private boolean isTripInQualificationPeriod(UserQualification qualification, ImmutableTrip trip) {
		return !qualification.getStartTime().isAfter(trip.getStart()) && !qualification.getEndTime().isBefore(trip.getEnd());
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

package com.sas.interbids.validator.requests;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;


import com.jeppesen.carmen.crewweb.backendfacade.bo.ImmutableTrip;
import java.util.Collection;
import java.util.HashMap;
import java.util.Arrays;

import com.jeppesen.carmen.crewweb.framework.bo.UserAttribute;
import com.jeppesen.carmen.crewweb.framework.bo.UserQualification;
import com.jeppesen.carmen.crewweb.framework.bo.UserGroup;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserAPI;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserCustomizationAPI;
import com.jeppesen.carmen.crewweb.framework.context.aware.DateTimeUtilAware;
import com.jeppesen.carmen.crewweb.framework.context.aware.UserCustomizationAPIAware;
import com.jeppesen.carmen.crewweb.framework.util.DateTimeUtil;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidTypeValidatorInterface;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ValidationContext;
import com.jeppesen.carmen.crewweb.interbids.validation.RequestValidatorSupport;
import com.jeppesen.jcms.crewweb.common.exception.CWInvalidDateException;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;

import com.jeppesen.jcms.crewweb.common.util.CWLog;
import org.apache.tomcat.util.json.JSONException;
import org.apache.tomcat.util.json.JSONObject;


/**
 * An implementation of a bid validator that uses
 * {@link BidTypeValidatorInterface} and {@link UserCustomizationAPIAware} to
 * validate days off.
 * 
 * Checks so that user is on variable contract when bid starts
 */

public class RequestFSRequestIsAllowedValidator extends
		RequestValidatorSupport implements UserCustomizationAPIAware,
		DateTimeUtilAware {

	private static final CWLog LOG = CWLog.getLogger(RequestFSRequestIsAllowedValidator.class);
	
	/**
	 * Access user related information, such as id, pre-assignments, or current
	 * period.
	 */
	private Map<String, String> requestData;
	private List<String> violations;

	private UserCustomizationAPI userCustomizationAPI;
	private DateTimeUtil dateTimeUtil;
	
	private static final String VARIABLE_CONTRACT_NAME = "CONTRACTVG";
	private static final Set<String> VARIABLE_CONTRACT = new HashSet<String>();
	static {
		VARIABLE_CONTRACT.add("FD LH");
		VARIABLE_CONTRACT.add("FD SH SKN VG");
		VARIABLE_CONTRACT.add("FD SH SKS VG");
		VARIABLE_CONTRACT.add("FD SH SKD VG");
		VARIABLE_CONTRACT.add("CC SKD VG");
		VARIABLE_CONTRACT.add("CC SKN VG");
		VARIABLE_CONTRACT.add("CC SKS VG");
	}

    private static final List<String> agreementGroupsFS = Arrays.asList("FD SH SKN VG", "CC SKD VG");

    Map<String, Collection<? extends ImmutableTrip>> preassignmentLists = new HashMap<String, Collection<? extends ImmutableTrip>>();

	private boolean tripIsFS(ImmutableTrip trip) {
		return trip.getCrrId().equals("FS");
	}

	private Collection<? extends ImmutableTrip> getPreassignments() {
		Collection<? extends ImmutableTrip> preassignments;
		String userId = this.userCustomizationAPI.getUserId();

		if (preassignmentLists.containsKey(userId)) {
			preassignments = preassignmentLists.get(userId);
		} else {
			preassignments = this.userCustomizationAPI.getPreassignments();
			preassignmentLists.put(userId, preassignments);
		}
		return preassignments;
	}

	// TODO: can be removed after SKAM-84 will be fixed
	static class FSRequestLog {
		static String create(CWDateTime startDate, int nrOfDays, UserCustomizationAPI userCustomizationAPI) {
			JSONObject logInfo = new JSONObject();
			String printedLog = "";
			try {
				UserAPI userAPI = userCustomizationAPI.getCurrentUserAPI();
				logInfo.put("User id", userCustomizationAPI.getUserId());
				for (UserAttribute attribute : userAPI.getUserAttributes()) {
					if ("contracttype".equals(attribute.getName())) {
						logInfo.put("Contract type", attribute.getValue());
						break;
					}
				}
				logInfo.put("Requested start date", startDate);
				logInfo.put("NrOfDays", nrOfDays);
				List<String> qualifications = new ArrayList<>();
				for (UserQualification qualification: userAPI.getUserQualifications()) {
					qualifications.add(new StringBuilder(qualification.getQualificationName())
																 .append(": ")
																 .append(qualification.getStartTime())
																 .append(" - ")
																 .append(qualification.getEndTime()).toString());
				}
				logInfo.put("Qualifications", qualifications);
				printedLog = "\nSKAM-84: DEBUGING\n" + logInfo.toString(2);
			} catch (JSONException e) {
				LOG.error("FS request log is corrupted." + e.getMessage());
			}
			return printedLog;
		}
	}

	@Override
	public void validate(List<String> violations,
			Map<String, String> requestData, ValidationContext context) {

		this.violations = violations;
		this.requestData = requestData;

		CWDateTime startDate = getAndValidateDateFormat("start",
				"Start date is not a valid date");
		int nrOfDays = Integer.parseInt(requestData.get("nr_of_days"));

		boolean isAllowed = true;
		isAllowed = isFSRequestValid(startDate, nrOfDays);
		if (!isAllowed) {
				LOG.warn(FSRequestLog.create(startDate, nrOfDays, userCustomizationAPI));
		    violations.add("Your contract type (FG) on the selected date does not allow you to place FS requests.");
		}
		UserAPI userAPI = userCustomizationAPI.getUserAPI(userCustomizationAPI.getUserId());
		for ( UserGroup userGroup : userAPI.getUserGroups() ) {
			if ( agreementGroupsFS.contains(userGroup.getGroupName()) ) {
				if ( dateTimeUtil.isDateTimeWithinRange(userGroup.getStartTime(), userGroup.getEndTime(), startDate) ) {
                    String violationType = getFsViolationType(startDate, nrOfDays, userGroup.getGroupName());
                    if( violationType != null) {
                        LOG.debug(String.format("### FS BID ### Violation string was: " + violationType));
                        violations.add(violationType);
                    }
                }
			}
		}
	}

	private String getFsViolationType(CWDateTime startDateNewBid, int nrOfDaysNewBid, String userGroupName) {

        // Get first day of current and next month
		CWDateTime firstDayOfCurrentMonth = getFirstDayOfCurrentMonth(startDateNewBid);
        CWDateTime firstDayOfNextMonth = getFirstDayOfNextMonth(startDateNewBid);

        // Get end day of new bid
        CWDateTime endDateNewBid = CWDateTime.create(startDateNewBid.getMilliSeconds());
        endDateNewBid.addDays(nrOfDaysNewBid);

        int fsTripsInSameMonthCounter = 0;
        int fsDaysInSameMonthCounter = 0;
        String violationType = null;

		try {
			// Go through all pre-assignment
			for (ImmutableTrip trip : getPreassignments()) {

				CWDateTime tripStart = trip.getStart();
				CWDateTime tripEnd = trip.getEnd();

				if (tripIsFS(trip)) {
                    // Check if preassigned FS trip overlaps the month of the new bid
                    if (dateTimeUtil.isOverlap(tripStart, tripEnd, firstDayOfCurrentMonth, firstDayOfNextMonth)) {
                        // Count number of FS trips in period.
                        fsTripsInSameMonthCounter++;
                        // When FS trip count number of used FS days in period.
                        if ( tripIsTwoDays(trip)) {
                            fsDaysInSameMonthCounter += 2;
                         }
                        else {
                            fsDaysInSameMonthCounter++;
                        }

		                // Illegal if new bid overlaps the preassigned FS trip
                        if ( dateTimeUtil.isOverlap(startDateNewBid, endDateNewBid, tripStart, tripEnd) ) {
                            violationType = "New FS bid cannot overlap existing FS bids.";
                        }
                        // Illegal if the preassigned FS trip is 2 days long
                        else if ( !tripIsOneDay(trip) && !"CC SKD VG".equals(userGroupName)) {
                            violationType = "The maximum number of FS days in this calender month is already reached.";
                        }
                        // Illegal if the new FS bid is 2 days long and there is a preassigned FS trip
                        else if ( nrOfDaysNewBid > 1 &&  !"CC SKD VG".equals(userGroupName)) {
                            violationType = "Cannot add a 2-day FS when there already are FS days in the calendar month.";
                        }

                        // Illegal if the preassigned FS trip and the new FS bid are not consecutive
                        else if ( !datesAreConsecutive(startDateNewBid, tripStart) &&  !"CC SKD VG".equals(userGroupName)) {
                            violationType = "FS days within the same calendar month must be consecutive.";
                        }
                        // CC SKD has right to 3 FS days under certain circumstances.
                        else if ( "CC SKD VG".equals(userGroupName) && fsDaysInSameMonthCounter >= 2 && nrOfDaysNewBid >= 2) {
                            violationType = "The maximum number of FS days will be exceeded with that bid.";
                        }
                        // CC SKD has right to 3 FS days under certain circumstances.
                        else if ( "CC SKD VG".equals(userGroupName) && fsDaysInSameMonthCounter >= 3 && nrOfDaysNewBid >= 1) {
                            violationType = "The maximum number of FS days will be exceeded with that bid.";
                        }
                    }
                }
			}
		} catch (Exception e) {
            // Not possible to fetch pre-assignments
            e.printStackTrace();
            return null;
        }

		// We do this check to always return the violation message below when there are two preassigned FS trips in the month of the new FS bid.
		// Exception for CC SKD VG which are allowed to have separate FS bids.
        if (fsTripsInSameMonthCounter > 1 && !"CC SKD VG".equals(userGroupName)) {
            violationType = "The maximum number of FS days in this calender month is already reached.";
        }

        return violationType;
	}

	private boolean tripIsOneDay(ImmutableTrip trip) {
	    CWDateTime startDate = trip.getStart();
	    CWDateTime dateAfterStartDate = CWDateTime.create(startDate.getMilliSeconds());
		dateAfterStartDate.addDays(1);
		CWDateTime endDate = trip.getEnd();

		return endDate.isEqual(dateAfterStartDate);
	}

    private boolean tripIsTwoDays(ImmutableTrip trip) {
	    CWDateTime startDate = trip.getStart();
	    CWDateTime dateAfterStartDate = CWDateTime.create(startDate.getMilliSeconds());
		dateAfterStartDate.addDays(2);
		CWDateTime endDate = trip.getEnd();

		return endDate.isEqual(dateAfterStartDate);
	}

	private CWDateTime getFirstDayOfCurrentMonth(CWDateTime date) {
	    CWDateTime tempNextDay = CWDateTime.create(date.getMilliSeconds());
		tempNextDay.addDays(1);
		long oneDayMilliSeconds = tempNextDay.getMilliSeconds() - date.getMilliSeconds();
		return CWDateTime.create(date.getMilliSeconds() - ((date.getDay() - 1) * oneDayMilliSeconds ));
	}

	private CWDateTime getFirstDayOfNextMonth(CWDateTime date) {
	    CWDateTime tempNextDay = CWDateTime.create(date.getMilliSeconds());
		tempNextDay.addDays(1);
		long oneDayMilliSeconds = tempNextDay.getMilliSeconds() - date.getMilliSeconds();
		CWDateTime firstDayOfMonth = CWDateTime.create(date.getMilliSeconds() - ((date.getDay() - 1) * oneDayMilliSeconds ));
		CWDateTime tempDayOfNextMonth = CWDateTime.create(firstDayOfMonth.getMilliSeconds() + ( 32 * oneDayMilliSeconds));
		return CWDateTime.create(tempDayOfNextMonth.getMilliSeconds() - ((tempDayOfNextMonth.getDay() - 1) * oneDayMilliSeconds ));
	}

	private boolean datesAreConsecutive(CWDateTime date1, CWDateTime date2) {
	    CWDateTime dateBeforeDate1 = CWDateTime.create(date1.getMilliSeconds());
	    dateBeforeDate1.addDays(-1);

	    CWDateTime dateAfterDate1 = CWDateTime.create(date1.getMilliSeconds());
	    dateAfterDate1.addDays(1);

	    return date2.isEqual(dateBeforeDate1) || date2.isEqual(dateAfterDate1);
	}

	private boolean isFSRequestValid(CWDateTime startDate, int nrOfDays) {
		UserAPI userAPI = userCustomizationAPI.getUserAPI(userCustomizationAPI.getUserId());
		// Split request into list of FS days
		ArrayList<CWDateTime> FSDayList = getFSRequestDays(startDate, nrOfDays);

		boolean isAllowed = true;
		for (CWDateTime date : FSDayList) {
			// verify that all requested days are within VG contract period
			if (!isRequestDayValid(userAPI, date)) {
				isAllowed = false;
			}
			
		}
		return isAllowed;
	}

	private ArrayList<CWDateTime> getFSRequestDays(CWDateTime startDate, int nrOfDays) {
		ArrayList<CWDateTime> FSDayList = new ArrayList<CWDateTime>();
		for (int i = 0; i < nrOfDays; i++) {
			CWDateTime date = CWDateTime.create(startDate.getMilliSeconds());
			date.addDays(i);
			FSDayList.add(date);
		}
		return FSDayList;
	}

	private boolean isRequestDayValid(UserAPI userAPI, CWDateTime date) {
		Boolean isValid = false;
		for (UserQualification userQual :userAPI.getUserQualifications()) {
			if (userQual.getQualificationName().equalsIgnoreCase(VARIABLE_CONTRACT_NAME)) {
				if (dateTimeUtil.isDateTimeWithinRange(userQual.getStartTime(), userQual.getEndTime(), date)) {
					isValid = true;
				}
			}
		}
		return isValid;
	}

	private CWDateTime getAndValidateDateFormat(String dateDataKey,
			String errorMessage) {
		String value = requestData.get(dateDataKey);
		if (value == null) {
			violations.add(errorMessage);
		}

		CWDateTime parsedDate = null;
		try {
			parsedDate = CWDateTime.parseISODateTime(value);
		} catch (CWInvalidDateException e) {
			violations.add(errorMessage);
		}
		return parsedDate;
	}

	@Override
	public void setUserCustomizationAPI(
			UserCustomizationAPI userCustomizationAPI) {
		this.userCustomizationAPI = userCustomizationAPI;

	}

	@Override
	public void setDateTimeUtil(DateTimeUtil dateTimeUtil) {
		this.dateTimeUtil = dateTimeUtil;
	}

}

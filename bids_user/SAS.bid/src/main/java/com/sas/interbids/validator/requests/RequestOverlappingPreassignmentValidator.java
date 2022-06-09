package com.sas.interbids.validator.requests;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.Collection;
import java.util.Date;
import java.util.List;
import java.util.Map;

import com.jeppesen.carmen.crewweb.backendfacade.bo.ImmutableTrip;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserCustomizationAPI;
import com.jeppesen.carmen.crewweb.framework.context.aware.DateTimeUtilAware;
import com.jeppesen.carmen.crewweb.framework.context.aware.UserCustomizationAPIAware;
import com.jeppesen.carmen.crewweb.framework.util.DateTimeUtil;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidTypeValidatorInterface;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ValidationContext;
import com.jeppesen.carmen.crewweb.interbids.validation.RequestValidatorSupport;
import com.jeppesen.jcms.crewweb.common.exception.CWInvalidDateException;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;

/**
 * An implementation of a bid validator that uses
 * {@link BidTypeValidatorInterface} and {@link UserCustomizationAPIAware} to
 * validate days off.
 * 
 * Checks that the request doesn't overlap any existing pre-assignment
 */

public class RequestOverlappingPreassignmentValidator extends
		RequestValidatorSupport implements UserCustomizationAPIAware,
		DateTimeUtilAware {

	/**
	 * Access user related information, such as id, pre-assignments, or current
	 * period.
	 */
	private Map<String, String> requestData;
	private List<String> violations;
	private String type;

	private UserCustomizationAPI userCustomizationAPI;
	private DateTimeUtil dateTimeUtil;

	@Override
	public void validate(List<String> violations,
			Map<String, String> requestData, ValidationContext context) {

		this.violations = violations;
		this.requestData = requestData;

		CWDateTime startDate = getAndValidateDateFormat("start",
				"Start date is not a valid date");
		
		int nrOfDays = Integer.parseInt(requestData.get("nr_of_days"));
		
		CWDateTime endDate = calculateEndDate(startDate, nrOfDays);

		// Check so that the bid doesn't overlap any of the pre-assignmets
		if (overlapsPreassignments(startDate, endDate)) {
			violations.add("Request is overlapping preassignment");
			return;
		}
	}

	private boolean overlapsPreassignments(CWDateTime start, CWDateTime end) {

		// Get all pre-assignments
		Collection<? extends ImmutableTrip> preassignmentList = new ArrayList<ImmutableTrip>();

		try {
			preassignmentList = userCustomizationAPI.getPreassignments();

			// Go through all pre-assignment
			for (ImmutableTrip trip : preassignmentList) {

				CWDateTime tripStart = trip.getStart();
				CWDateTime tripEnd = trip.getEnd();

				if (dateTimeUtil.isOverlap(tripStart, tripEnd, start, end)) {
					return true;
				}

			}
		} catch (Exception e) {
			// Not possible to fetch pre-assignments
			e.printStackTrace();
			return false;
		}

		return false;
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

	private CWDateTime calculateEndDate(CWDateTime startDate,  int nrOfDays) {
		Date start = startDate.getDate();
		Calendar c = Calendar.getInstance();
		c.setTime(start);
		c.add(Calendar.DATE, nrOfDays);
		c.add(Calendar.MINUTE, -1);
		CWDateTime end = CWDateTime.create(c.getTimeInMillis());
		return end;
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
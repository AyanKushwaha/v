package com.sas.interbids.validator.requests;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import com.jeppesen.carmen.crewweb.framework.bo.UserQualification;
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

/**
 * An implementation of a bid validator that uses
 * {@link BidTypeValidatorInterface} and {@link UserCustomizationAPIAware} to
 * validate days off.
 *
 * Checks so that user is on variable contract when bid starts
 */

public class RequestFWRequestIsAllowedValidator extends
		RequestValidatorSupport implements UserCustomizationAPIAware,
		DateTimeUtilAware {

    private static final CWLog LOG = CWLog.getLogger(RequestFWRequestIsAllowedValidator.class);

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
		VARIABLE_CONTRACT.add("FD SH SKN FG");
		VARIABLE_CONTRACT.add("FD SH SKD FG");
		VARIABLE_CONTRACT.add("FD SH SKS FG");
		VARIABLE_CONTRACT.add("CC SKD VG");
		VARIABLE_CONTRACT.add("CC SKN VG");
		VARIABLE_CONTRACT.add("CC SKS VG");
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
		isAllowed = isFWRequestValid(startDate, nrOfDays);

		if (!isAllowed) {
			LOG.warn(RequestFSRequestIsAllowedValidator.FSRequestLog.create(startDate, nrOfDays, userCustomizationAPI));
			violations.add("Your contract type (FG) on the selected date does not allow you to place FW requests.");
		}
	}

	private boolean isFWRequestValid(CWDateTime startDate, int nrOfDays) {
		UserAPI userAPI = userCustomizationAPI.getUserAPI(userCustomizationAPI.getUserId());

		// Split request into list of FW days
		ArrayList<CWDateTime> FWDayList = getFWRequestDays(startDate, nrOfDays);

		boolean isAllowed = true;
		for (CWDateTime date : FWDayList) {
			// verify that all requested days are within VG contract period
			if (!isRequestDayValid(userAPI, date)) {
				isAllowed = false;
			}
		}
		return isAllowed;
	}

	private ArrayList<CWDateTime> getFWRequestDays(CWDateTime startDate, int nrOfDays) {
		ArrayList<CWDateTime> FWDayList = new ArrayList<CWDateTime>();
		for (int i = 0; i < nrOfDays; i++) {
			CWDateTime date = CWDateTime.create(startDate.getMilliSeconds());
			date.addDays(i);
			FWDayList.add(date);
		}
		return FWDayList;
	}

	private boolean isRequestDayValid(UserAPI userAPI, CWDateTime date) {
		Boolean isValid = false;
		for (UserQualification userQual : userAPI.getUserQualifications()) {
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

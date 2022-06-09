package com.sas.interbids.validator.requests;

import java.util.List;
import java.util.Map;

import com.jeppesen.carmen.crewweb.framework.bo.Period;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserCustomizationAPI;
import com.jeppesen.carmen.crewweb.framework.context.aware.DateTimeUtilAware;
import com.jeppesen.carmen.crewweb.framework.context.aware.UserCustomizationAPIAware;
import com.jeppesen.carmen.crewweb.framework.util.DateTimeUtil;
import com.jeppesen.carmen.crewweb.interbids.customization.api.ValidationContext;
import com.jeppesen.carmen.crewweb.interbids.validation.RequestValidatorSupport;
import com.jeppesen.jcms.crewweb.common.exception.CWInvalidDateException;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;

/**
 * A class that checks that the request starts within the request period
 * 
 * @param violations
 * @param requestData
 * @return sets a violation error if the start date of the request is not within the request period
 */

public class RequestStartDateValidator extends RequestValidatorSupport implements UserCustomizationAPIAware,
        DateTimeUtilAware {

    /**
     * Access user related information, such as id, pre-assignments, or current period.
     */
    private Map<String, String> requestData;
    private List<String> violations;
    private UserCustomizationAPI userCustomizationAPI;
    private DateTimeUtil dateTimeUtil;

    @Override
    public void setUserCustomizationAPI(UserCustomizationAPI userCustomizationAPI) {
        this.userCustomizationAPI = userCustomizationAPI;
    }

    @Override
    public void setDateTimeUtil(DateTimeUtil dateTimeUtil) {
        this.dateTimeUtil = dateTimeUtil;

    }

    @Override
    public void validate(List<String> violations, Map<String, String> requestData, ValidationContext context) {
        this.violations = violations;
        this.requestData = requestData;
        String requestType = requestTypeConfiguration.getType();

        String userId = userCustomizationAPI.getUserId();
        String periodCategory = requestTypeConfiguration.getCategory();
        if (!userCustomizationAPI.userHasCurrentPeriod(userId, periodCategory)) {
            violations.add("There's no " + periodCategory + " period open -  requests are currently not accepted.");
        }

        Period requestPeriod = userCustomizationAPI.getCurrentPeriodForUser(userId, periodCategory);
        CWDateTime startDate = getAndValidateDateFormat("start", "Start date is not a valid date");

        validateDateIsWithinPeriod(startDate, requestPeriod, "Start date must be within the requesting period");
        // TODO should use translatable string, core bug UIIB-1558
        // validateDateIsWithinPeriod(startDate, requestPeriod, "request_start_date_not_in_period");
    }

    private void validateDateIsWithinPeriod(CWDateTime date, Period period, String errorMessage) {
        if (dateTimeUtil.isDateTimeWithinRange(period.getStart(), period.getEnd(), date)) {
            return;
        }
        violations.add(errorMessage);
    }

    private CWDateTime getAndValidateDateFormat(String dateDataKey, String errorMessage) {
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
}

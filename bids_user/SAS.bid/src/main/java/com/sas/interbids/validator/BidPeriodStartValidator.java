package com.sas.interbids.validator;

import static com.sas.interbids.base.SasConstants.START;
import static com.sas.interbids.base.SasConstants.getValidityPeriodFieldValue;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import com.jeppesen.carmen.crewweb.framework.bo.Period;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserCustomizationAPI;
import com.jeppesen.carmen.crewweb.framework.context.aware.UserCustomizationAPIAware;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidTypeValidatorContext;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidTypeValidatorInterface;
import com.jeppesen.carmen.crewweb.interbids.validation.IValidatorResult;
import com.jeppesen.carmen.crewweb.interbids.validation.ValidationDataSet;
import com.jeppesen.carmen.crewweb.interbids.validation.ValidatorResult;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;

public class BidPeriodStartValidator implements BidTypeValidatorInterface, UserCustomizationAPIAware {

	protected UserCustomizationAPI userCustomizationAPI;

	@Override
	public void setAttributes(Map<String, String> arg0) {

	}

	@Override
	public void validate(BidData arg0, IValidatorResult arg1,
			ValidationDataSet arg2, BidTypeValidatorContext arg3) {

	}

	@Override
	public void validateOnSystemContinouosValidation(BidData arg0,
			ValidatorResult arg1, ValidationDataSet arg2,
			BidTypeValidatorContext arg3) {

	}

	@Override
	public void validateOnSystemImport(BidData arg0, ValidatorResult arg1,
			ValidationDataSet arg2, BidTypeValidatorContext arg3) {

	}

	@Override
	public void validateOnUserCreate(BidData arg0, ValidatorResult arg1,
			ValidationDataSet arg2, BidTypeValidatorContext arg3) {
		localValidate(arg0, arg1, arg2, arg3);
	}

	@Override
	public void validateOnUserUpdate(BidData arg0, ValidatorResult arg1,
			ValidationDataSet arg2, BidTypeValidatorContext arg3) {
		localValidate(arg0, arg1, arg2, arg3);
	}

	@Override
	public void validateAfterTripCacheFlush(BidData arg0, ValidatorResult arg1,
			ValidationDataSet arg2, BidTypeValidatorContext arg3) {

	}

	public void localValidate(BidData bidData, IValidatorResult iValidatorResult, ValidationDataSet validationDataSet, BidTypeValidatorContext bidTypeValidatorContext) {

		Period currentPeriodForUser = userCustomizationAPI.getCurrentPeriodForUser(userCustomizationAPI.getUserId(), Period.STANDARD_BID_PERIOD);
		CWDateTime bidWindowOpenDate = currentPeriodForUser.getOpen();
		CWDateTime bidStart;


		//		CWDateTime bidCreatedOrUpdatedDate = bidData.getUpdated() != null ? bidData.getUpdated() : bidData.getCreated();

		if (bidWindowOpenDate.isAfter(bidData.getCreated())) {
			return;
		}
		CWDateTime bidPeriodStartDate = currentPeriodForUser.getStart();

		if ("time_off".equals(bidData.getType())) {
			bidStart = CWDateTime.parseISODateTime(bidData.getAllByPropertyType("date_time_start").get(0).get("start"));
			List<String> paramList = new ArrayList<String>();
			if (!bidStart.isInIntervall(currentPeriodForUser.getStart(), currentPeriodForUser.getEnd())) {
				paramList.add(bidStart.toString());
				iValidatorResult.addValidationError("bid_start_date_not_in_period", paramList);
			}
		} else {
			bidStart = CWDateTime.parseISODateTime(getValidityPeriodFieldValue(bidData, START));
			List<String> paramList = new ArrayList<String>();
			if (bidStart.isBefore(bidPeriodStartDate)) {
				paramList.add(bidStart.toString());
				iValidatorResult.addValidationError("bid_start_date_not_in_period", paramList);
			}
		}
	}

	@Override
	public void setUserCustomizationAPI(
			UserCustomizationAPI userCustomizationAPI) {
		this.userCustomizationAPI = userCustomizationAPI;
	}
}

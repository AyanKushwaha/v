package com.sas.interbids.validator;

import static com.sas.interbids.base.SasConstants.START;
import static com.sas.interbids.base.SasConstants.END;
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
import com.sas.interbids.base.SasConstants;

public class LastMinuteLOAEndValidator implements BidTypeValidatorInterface,
		UserCustomizationAPIAware {

	private void localValidate(BidData bidData, IValidatorResult result,
			ValidationDataSet validationDataSet, BidTypeValidatorContext context) {
		CWDateTime validity_start = CWDateTime.parseISODateTime(SasConstants
				.getValidityPeriodFieldValue(bidData, SasConstants.START));
		CWDateTime validity_end = CWDateTime.parseISODateTime(SasConstants
				.getValidityPeriodFieldValue(bidData, SasConstants.END));
		if (validity_end != null) {
			CWDateTime validity_start_plus_thirty = CWDateTime
					.parseISODateTime(SasConstants.getValidityPeriodFieldValue(
							bidData, SasConstants.START));
			validity_start_plus_thirty.addDays(30);
			validity_start_plus_thirty.removeMinutes(1);

			if (!validity_end.isInIntervall(validity_start,
					validity_start_plus_thirty)) {
				List<String> paramList = new ArrayList<String>();
				result.addValidationError(
						"The end date of this bid must be less than 30 days from start date",
						paramList);
			}
		} else {
			List<String> paramList = new ArrayList<String>();
			result.addValidationError("This bid must have an end date",
					paramList);
		}
	}

	@Override
	public void setUserCustomizationAPI(UserCustomizationAPI arg0) {
		// TODO Auto-generated method stub

	}

	@Override
	public void validate(BidData bidData, IValidatorResult result,
			ValidationDataSet validationDataSet, BidTypeValidatorContext context) {
		localValidate(bidData, result, validationDataSet, context);

	}

	@Override
	public void setAttributes(Map<String, String> attributes) {
		// TODO Auto-generated method stub

	}

	@Override
	public void validateOnUserUpdate(BidData bidData, ValidatorResult result,
			ValidationDataSet validationDataSet, BidTypeValidatorContext context) {
		localValidate(bidData, result, validationDataSet, context);

	}

	@Override
	public void validateOnUserCreate(BidData bidData, ValidatorResult result,
			ValidationDataSet validationDataSet, BidTypeValidatorContext context) {
		localValidate(bidData, result, validationDataSet, context);

	}

	@Override
	public void validateOnSystemImport(BidData bidData, ValidatorResult result,
			ValidationDataSet validationDataSet, BidTypeValidatorContext context) {
		// TODO Auto-generated method stub

	}

	@Override
	public void validateOnSystemContinouosValidation(BidData bidData,
			ValidatorResult result, ValidationDataSet validationDataSet,
			BidTypeValidatorContext context) {
		localValidate(bidData, result, validationDataSet, context);

	}

	@Override
	public void validateAfterTripCacheFlush(BidData bid,
			ValidatorResult partialResult, ValidationDataSet validationDataSet,
			BidTypeValidatorContext context) {
		// TODO Auto-generated method stub

	}

}

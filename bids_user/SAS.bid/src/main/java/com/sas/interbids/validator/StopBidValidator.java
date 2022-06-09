package com.sas.interbids.validator;


import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import com.jeppesen.carmen.crewweb.framework.business.facade.UserCustomizationAPI;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidTypeValidatorContext;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidTypeValidatorInterface;
import com.jeppesen.carmen.crewweb.interbids.validation.IValidatorResult;
import com.jeppesen.carmen.crewweb.interbids.validation.ValidationDataSet;
import com.jeppesen.carmen.crewweb.interbids.validation.ValidatorResult;
import com.sas.interbids.base.SasConstants;

public class StopBidValidator implements BidTypeValidatorInterface {

	private void localValidate(BidData bidData, IValidatorResult result,
			ValidationDataSet validationDataSet, BidTypeValidatorContext context) {

		String stopLengthMin = bidData.get(SasConstants.STOP_LENGTH_MIN);
		if (stopLengthMin == null) {
			stopLengthMin = SasConstants.DEFAULT_STOP_LENGTH_MIN;
		}
		String stopLengthMax = bidData.get(SasConstants.STOP_LENGTH_MAX);
		if (stopLengthMax == null) {
			stopLengthMax = SasConstants.DEFAULT_STOP_LENGTH_MAX;
        }

        // stopLength{Min,Max} is in the form HH:SS
        String[] minParts = stopLengthMin.split(":");
        String[] maxParts = stopLengthMax.split(":");
        
        int minMinutes = Integer.parseInt(minParts[0]) * 60 + Integer.parseInt(minParts[1]);
        int maxMinutes = Integer.parseInt(maxParts[0]) * 60 + Integer.parseInt(maxParts[1]);

        List<String> paramList = new ArrayList<String>();

        if (minMinutes > maxMinutes) {
            result.addValidationError("min_over_max", paramList);
        }
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

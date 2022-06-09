package com.sas.interbids.validator;

import static com.sas.interbids.base.SasConstants.START;
import static com.sas.interbids.base.SasConstants.END;
import static com.sas.interbids.base.SasConstants.getValidityPeriodFieldValue;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

import com.jeppesen.carmen.crewweb.backendfacade.bo.Activity;
import com.jeppesen.carmen.crewweb.backendfacade.bo.ImmutableTrip;
import com.jeppesen.carmen.crewweb.backendfacade.bo.Duty;
import com.jeppesen.carmen.crewweb.framework.bo.Period;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserCustomizationAPI;
import com.jeppesen.carmen.crewweb.framework.context.aware.DateTimeUtilAware;
import com.jeppesen.carmen.crewweb.framework.context.aware.UserCustomizationAPIAware;
import com.jeppesen.carmen.crewweb.framework.util.DateTimeUtil;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidTypeValidatorContext;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidTypeValidatorInterface;
import com.jeppesen.carmen.crewweb.interbids.validation.IValidatorResult;
import com.jeppesen.carmen.crewweb.interbids.validation.ValidationDataSet;
import com.jeppesen.carmen.crewweb.interbids.validation.ValidatorResult;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;
import com.sas.interbids.base.SasConstants;
import com.jeppesen.jcms.crewweb.common.util.CWLog;
import static java.lang.String.format;

public class DaysForProductionOverlapValidator implements BidTypeValidatorInterface,
							  UserCustomizationAPIAware,
							  DateTimeUtilAware {

    private UserCustomizationAPI userCustomizationAPI;
    private DateTimeUtil dateTimeUtil;
    private static final CWLog LOG = CWLog.getLogger(DaysForProductionOverlapValidator.class);
    Map<String, Collection<? extends ImmutableTrip>> preassignmentLists = new HashMap<String, Collection<? extends ImmutableTrip>>();




    private boolean tripIsFn(ImmutableTrip trip) {
	return trip.getCrrId().equals("FN");
    }

    private boolean tripIsFlt(ImmutableTrip trip) {
	return trip.getCrrId().equals("FLT");
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
    
	private boolean overlapsPreassignments(CWDateTime start, CWDateTime end) {

		try {
			// Go through all pre-assignment
		        for (ImmutableTrip trip : getPreassignments()) {

				CWDateTime tripStart = trip.getStart();
				CWDateTime tripEnd = trip.getEnd();

				if (!(tripIsFn(trip) || tripIsFlt(trip))) {
				    if (dateTimeUtil.isOverlap(tripStart, tripEnd, start, end)) {
					return true;
				    }
				}

			}
		} catch (Exception e) {
			// Not possible to fetch pre-assignments
			e.printStackTrace();
			return false;
		}

		return false;
	}


    private boolean overlapsOtherBid(ValidationDataSet validationDataSet, BidData bidData, CWDateTime start, CWDateTime end) {

	Collection<? extends BidData> bidList = validationDataSet.getOtherBidsInSameBidGroupAs(bidData);

	// Go through all bids
	for (BidData bid : bidList) {
	    if (bid.getType().equals(bidData.getType())) {
		CWDateTime bidStart = bid.getStartDate();
		CWDateTime bidEnd = bid.getEndDate();

		if (dateTimeUtil.isOverlap(bidStart, bidEnd, start, end)) {
		    return true;
		}
	    }
	}

	return false;
    }


    private CWDateTime max(CWDateTime a, CWDateTime b) {
	if (a.compareTo(b) > 0) {
	    return a;
	} else {
	    return b;
	}
    }
    
    private CWDateTime min(CWDateTime a, CWDateTime b) {
	if (a.compareTo(b) > 0) {
	    return b;
	} else {
	    return a;
	}
    }
    
    private boolean fltIsNoLongerOverlapped(CWDateTime start, CWDateTime end, CWDateTime originalStart, CWDateTime originalEnd) {

	try {
	    // Go through all pre-assignment
	    for (ImmutableTrip trip : getPreassignments()) {
		CWDateTime tripStart = trip.getStart();
		CWDateTime tripEnd = trip.getEnd();

		if (tripIsFlt(trip)) {
		    if (dateTimeUtil.isOverlap(tripStart, tripEnd, originalStart, originalEnd)) {
			if ((!max(tripStart, start).equals(max(tripStart, originalStart))) ||
			    (!min(tripEnd, end).equals(min(tripEnd, originalEnd)))) {
			    return true;
			}
		    }
		}
	    }
	} catch (Exception e) {
	    // Not possible to fetch pre-assignments
	    e.printStackTrace();
	    return false;
	}

	return false;
    }

    
        private void localValidate(BidData bidData, IValidatorResult result,
			ValidationDataSet validationDataSet, BidTypeValidatorContext context) {

		CWDateTime validity_start = CWDateTime.parseISODateTime(SasConstants
				.getValidityPeriodFieldValue(bidData, SasConstants.START));
		CWDateTime validity_end = CWDateTime.parseISODateTime(SasConstants
				.getValidityPeriodFieldValue(bidData, SasConstants.END));
		String original_start_date_str = SasConstants.getValidityPeriodFieldValue(bidData, SasConstants.ORIGINAL_START_DATE);
		String original_end_date_str = SasConstants.getValidityPeriodFieldValue(bidData, SasConstants.ORIGINAL_END_DATE);

		if (overlapsOtherBid(validationDataSet, bidData, validity_start, validity_end)) {
		    List<String> paramList = new ArrayList<String>();
		    result.addValidationError("The bid overlaps an existing bid.",
					      paramList);
		} else if (overlapsPreassignments(validity_start, validity_end)) {
		    List<String> paramList = new ArrayList<String>();
		    result.addValidationError("The bid overlaps a preassigned activity.",
					      paramList);
		} else if ((original_start_date_str != null) && (original_end_date_str != null)) {
			CWDateTime original_start_date = CWDateTime.parseISODateTime(original_start_date_str+" 00:00");
			CWDateTime original_end_date = CWDateTime.parseISODateTime(original_end_date_str+" 23:59");

			if (fltIsNoLongerOverlapped(validity_start, validity_end, original_start_date, original_end_date)) {
			    List<String> paramList = new ArrayList<String>();
			    result.addValidationError("Cannot change part of bid that has planned activity.",
						      paramList);
			}
		}
	}

	@Override
	public void setUserCustomizationAPI(UserCustomizationAPI arg0) {
		this.userCustomizationAPI = arg0;
	}

	@Override
	public void setDateTimeUtil(DateTimeUtil dateTimeUtil) {
		this.dateTimeUtil = dateTimeUtil;
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
	    // Clear preassignments cache
	    LOG.debug("############# Clearing preassignments");
	    preassignmentLists = new HashMap<String, Collection<? extends ImmutableTrip>>();
	}

}

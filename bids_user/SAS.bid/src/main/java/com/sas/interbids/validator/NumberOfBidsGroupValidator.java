package com.sas.interbids.validator;

import com.jeppesen.carmen.crewweb.interbids.bo.Bid;
import com.jeppesen.carmen.crewweb.interbids.bo.BidGroup;
import com.jeppesen.carmen.crewweb.interbids.bo.BidProperty;
import com.jeppesen.carmen.crewweb.interbids.customization.BidGroupValidator;
import com.jeppesen.carmen.crewweb.interbids.validation.ValidatorResult;
import com.sas.interbids.base.BidsPerPriority;

import java.util.ArrayList;
import java.util.List;

import static com.sas.interbids.base.BidsPerPriority.*;

/**
 * Bid group validator for bid groups of category current (type flight). Returns an error if bid group contains
 * number of bids higher than number specified in {@link BidsPerPriority BidsPerPriority.class} per particular priority.
 */

public class NumberOfBidsGroupValidator implements BidGroupValidator {

	/**
	 * {@inheritDoc}
	 */
	public ValidatorResult validate(BidGroup bidGroup) {

		ValidatorResult result = new ValidatorResult(true, null, bidGroup, bidGroup.getId() + "");

		// Exclude Compensation Days bids and Last Minute LOA Bids from list as they should not be counted.
		int countForPriorityHigh = 0, countForPriorityMedium = 0, countForPriorityLow = 0;
		for (Bid bid : bidGroup.getAllBids()){
			if (!excludedBidTypes(bid)) {
				String priorityValue = getPriorityValueFrom(bid);
				switch (BidsPerPriority.fromPriorityValue(priorityValue)) {
					case HIGH:
						countForPriorityHigh++;
						if (countForPriorityHigh > HIGH.getAllowedBidsAmount()) {
							return buildValidationResult(result, HIGH);
						}
						break;
					case MEDIUM:
						countForPriorityMedium++;
						if (countForPriorityMedium > MEDIUM.getAllowedBidsAmount()) {
							return buildValidationResult(result, MEDIUM);
						}
						break;
					case LOW:
						countForPriorityLow++;
						if (countForPriorityLow > LOW.getAllowedBidsAmount()) {
							return buildValidationResult(result, LOW);
						}
						break;
					default:
						break;
				}
			}
		}
		return result;
	}

	private boolean excludedBidTypes(Bid bid) {
		return bid.getType().equalsIgnoreCase("compensation_days_cc") 
				|| bid.getType().equalsIgnoreCase("compensation_days_fd") 
				|| bid.getType().equalsIgnoreCase("days_for_production") 
				|| bid.getType().equalsIgnoreCase("last_minute_LOA");
	}

	private ValidatorResult buildValidationResult(ValidatorResult result, BidsPerPriority rule) {
		List<String> paramList = new ArrayList<>();
		paramList.add(String.valueOf(rule.getAllowedBidsAmount()));
		paramList.add(rule.name());
		result.addValidationError("max_bidchainno_bidgroup_error", paramList);
		result.setValid(false);
		return result;
	}

	private String getPriorityValueFrom(Bid bid) {
		for (BidProperty property : bid.getBidProperties()) {
			if ("priority".equals(property.getType())) {
				return property.getBidPropertyEntryValue("priority");
			}
		}
		return "";
	}

}

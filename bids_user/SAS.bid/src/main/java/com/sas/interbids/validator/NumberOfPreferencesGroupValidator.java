package com.sas.interbids.validator;

import java.util.ArrayList;
import java.util.List;

import com.jeppesen.carmen.crewweb.interbids.bo.BidGroup;
import com.jeppesen.carmen.crewweb.interbids.customization.BidGroupValidator;
import com.jeppesen.carmen.crewweb.interbids.validation.ValidatorResult;

/**
 * Bid group validator for bid groups of category preference (type preference-bids). Returns an error if bid group contains more than 1 preference.
 */

public class NumberOfPreferencesGroupValidator implements BidGroupValidator {

    /**
     * Max number of bid chains in a preference-bids bid group.
     */
    private static final int MAX_NO_PREFERENCES = 1;

    /**
     * {@inheritDoc}
     */
    public ValidatorResult validate(BidGroup bidGroup) {
        ValidatorResult result = new ValidatorResult(true, null, bidGroup, bidGroup.getId() + "");
        int actualSize = bidGroup.getAllBids().size();
        if (actualSize > MAX_NO_PREFERENCES) {
            List<String> paramList = new ArrayList<String>();
            paramList.add(actualSize + "");
            paramList.add(MAX_NO_PREFERENCES + "");
            result.addValidationError("max_preferencechainno_bidgroup_error", paramList);
            result.setValid(false);
        }
        return result;
    }

}

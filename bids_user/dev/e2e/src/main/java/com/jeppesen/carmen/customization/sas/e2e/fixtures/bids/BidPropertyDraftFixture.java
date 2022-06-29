package com.jeppesen.carmen.customization.sas.e2e.fixtures.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidProperty;
import org.springframework.stereotype.Service;

@Service
public class BidPropertyDraftFixture {

    public BidProperty initDraft(final String identifier) {
        return new BidProperty().setSortOrder(0L)
                .setBidPropertyType("bidPropertyType" + identifier);
    }
}

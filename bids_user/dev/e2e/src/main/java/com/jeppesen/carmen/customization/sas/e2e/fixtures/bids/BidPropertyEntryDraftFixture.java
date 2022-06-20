package com.jeppesen.carmen.customization.sas.e2e.fixtures.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidPropertyEntry;
import org.springframework.stereotype.Service;

@Service
public class BidPropertyEntryDraftFixture {

    public BidPropertyEntry initDraft(final String identifier) {
        return new BidPropertyEntry().setEntryKey("entryKey" + identifier)
                .setEntryValue("entryValue" + identifier);
    }
}

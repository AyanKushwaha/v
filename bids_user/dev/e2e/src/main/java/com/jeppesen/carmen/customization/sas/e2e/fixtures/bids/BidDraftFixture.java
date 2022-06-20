package com.jeppesen.carmen.customization.sas.e2e.fixtures.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.Bid;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

import static java.lang.String.format;
import static java.time.LocalDateTime.now;

@Service
public class BidDraftFixture {

    public Bid initDraft(final long identifier) {
        final LocalDateTime now = now();
        return new Bid().setBidId(identifier)
                .setBidGroupId(identifier)
                .setName(format("name%d", identifier))
                .setBidType(format("bidType%d", identifier))
                .setCreatedBy(format("createdBy%d", identifier))
                .setUpdatedBy(format("updatedBy%d", identifier))
                .setStartDate(now)
                .setEndDate(now.plusDays(1))
                .setInvalid(null)
                .setCreated(now)
                .setUpdated(now)
                .setRevisionDate(now);
    }
}

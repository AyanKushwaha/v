package com.jeppesen.carmen.customization.sas.e2e.fixtures.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidGroup;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
public class BidGroupDraftFixture {

    public BidGroup initDraft(final String identifier) {
        final LocalDateTime now = LocalDateTime.now();
        return new BidGroup().setBidGroupId(0L)
                .setName("name" + identifier)
                .setDescription("description" + identifier)
                .setUserId("userId" + identifier)
                .setCreatedBy("createdBy" + identifier)
                .setUpdatedBy("updatedBy" + identifier)
                .setType("type" + identifier)
                .setCreated(now)
                .setUpdated(now)
                .setStartDate(now)
                .setEndDate(now.plusDays(1))
                .setSubmitted(now)
                .setInvalid(now)
                .setRevisionDate(now)
                .setCategory(BidGroup.Category.current);
    }
}

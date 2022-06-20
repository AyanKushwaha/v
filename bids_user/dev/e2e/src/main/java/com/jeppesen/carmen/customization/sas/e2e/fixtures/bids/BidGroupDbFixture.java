package com.jeppesen.carmen.customization.sas.e2e.fixtures.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.api.Fixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidGroup;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidGroupRepository;
import lombok.RequiredArgsConstructor;
import lombok.val;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class BidGroupDbFixture implements Fixture<BidGroup> {

    final BidGroupRepository bidGroupRepository;
    final BidGroupDraftFixture bidGroupDraftFixture;
    final BidGroupOrderDbFixture bidGroupOrderDbFixture;

    @Override
    @Transactional
    public BidGroup create(BidGroup obj) {
        val bidGroup = bidGroupRepository.save(obj);
        bidGroupOrderDbFixture.create(bgo -> bgo.setBidGroupId(bidGroup.getBidGroupId()));
        return bidGroup;
    }

    @Override
    public BidGroup initDraft() {
        final String identifier = generateString(5);
        return bidGroupDraftFixture.initDraft(identifier);
    }
}

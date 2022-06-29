package com.jeppesen.carmen.customization.sas.e2e.fixtures.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.api.Fixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidPropertyEntry;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidPropertyEntryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class BidPropertyEntryDbFixture implements Fixture<BidPropertyEntry> {

    final BidPropertyEntryRepository bidPropertyEntryRepository;
    final BidPropertyEntryDraftFixture bidPropertyEntryDraftFixture;

    @Override
    @Transactional
    public BidPropertyEntry create(BidPropertyEntry obj) {
        return bidPropertyEntryRepository.save(obj);
    }

    @Override
    public BidPropertyEntry initDraft() {
        final String identifier = generateString(5);
        return bidPropertyEntryDraftFixture.initDraft(identifier);
    }
}

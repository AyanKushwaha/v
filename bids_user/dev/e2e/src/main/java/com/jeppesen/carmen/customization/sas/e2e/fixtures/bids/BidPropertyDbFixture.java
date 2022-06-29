package com.jeppesen.carmen.customization.sas.e2e.fixtures.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.api.Fixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidProperty;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidPropertyRepository;
import lombok.RequiredArgsConstructor;
import lombok.val;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;
import java.util.function.UnaryOperator;

@Service
@RequiredArgsConstructor
public class BidPropertyDbFixture implements Fixture<BidProperty> {

    final BidPropertyRepository bidPropertyRepository;
    final BidPropertyDraftFixture bidPropertyDraftFixture;
    final BidPropertyEntryDbFixture bidPropertyEntryDbFixture;

    @Override
    @Transactional
    public BidProperty create(BidProperty obj) {
        val bidProperty = bidPropertyRepository.save(obj);
        bidPropertyEntryDbFixture.create(bpe -> bpe.setBidProperty(bidProperty));
        return bidProperty;
    }

    @Transactional
    public BidProperty create(UnaryOperator<BidProperty> patchedBidProperty, Map<String, String> properties) {
        val bidProperty = bidPropertyRepository.save(patchedBidProperty.apply(initDraft()));
        properties.forEach((k, v) -> bidPropertyEntryDbFixture.create(bpe -> bpe.setBidProperty(bidProperty)
                .setEntryKey(k)
                .setEntryValue(v)));
        return bidProperty;
    }

    @Override
    public BidProperty initDraft() {
        final String identifier = generateString(5);
        return bidPropertyDraftFixture.initDraft(identifier);
    }
}

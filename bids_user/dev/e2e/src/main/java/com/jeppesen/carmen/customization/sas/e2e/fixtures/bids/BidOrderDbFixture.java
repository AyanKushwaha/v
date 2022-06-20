package com.jeppesen.carmen.customization.sas.e2e.fixtures.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.api.Fixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidOrder;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidOrderRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class BidOrderDbFixture implements Fixture<BidOrder> {

    final BidOrderRepository bidOrderRepository;
    final BidOrderDraftFixture bidOrderDraftFixture;

    @Override
    @Transactional
    public BidOrder create(BidOrder obj) {
        return bidOrderRepository.save(obj);
    }

    @Override
    public BidOrder initDraft() {
        return bidOrderDraftFixture.initDraft();
    }
}

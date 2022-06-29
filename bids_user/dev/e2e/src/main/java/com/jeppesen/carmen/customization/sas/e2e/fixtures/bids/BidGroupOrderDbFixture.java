package com.jeppesen.carmen.customization.sas.e2e.fixtures.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.api.Fixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidGroupOrder;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidGroupOrderRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class BidGroupOrderDbFixture implements Fixture<BidGroupOrder> {

    final BidGroupOrderRepository bidGroupOrderRepository;
    final BidGroupOrderDraftFixture bidGroupOrderDraftFixture;

    @Override
    @Transactional
    public BidGroupOrder create(BidGroupOrder obj) {
        return bidGroupOrderRepository.save(obj);
    }

    @Override
    public BidGroupOrder initDraft() {
        return bidGroupOrderDraftFixture.initDraft();
    }
}

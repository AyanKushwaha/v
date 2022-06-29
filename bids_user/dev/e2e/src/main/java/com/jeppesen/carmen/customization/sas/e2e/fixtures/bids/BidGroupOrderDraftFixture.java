package com.jeppesen.carmen.customization.sas.e2e.fixtures.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidGroupOrder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
public class BidGroupOrderDraftFixture {

    public BidGroupOrder initDraft() {
        return new BidGroupOrder().setRevisionDate(LocalDateTime.now())
                .setRowIndex(1L);
    }
}

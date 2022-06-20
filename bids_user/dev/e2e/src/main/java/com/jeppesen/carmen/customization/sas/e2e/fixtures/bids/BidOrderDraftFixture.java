package com.jeppesen.carmen.customization.sas.e2e.fixtures.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidOrder;
import org.springframework.stereotype.Service;

import static java.time.LocalDateTime.now;

@Service
public class BidOrderDraftFixture {

    public BidOrder initDraft() {
        return new BidOrder().setRevisionDate(now())
                .setRowIndex(1L);
    }
}

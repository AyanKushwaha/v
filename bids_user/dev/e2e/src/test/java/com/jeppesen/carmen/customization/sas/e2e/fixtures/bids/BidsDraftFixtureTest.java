package com.jeppesen.carmen.customization.sas.e2e.fixtures.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.AbstractDbFixtureTest;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.Bid;
import lombok.RequiredArgsConstructor;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import static java.time.LocalDateTime.now;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertFalse;

@DisplayName("Testing bid draft fixture tests")
@RequiredArgsConstructor(onConstructor_ = @Autowired)
class BidsDraftFixtureTest extends AbstractDbFixtureTest {

    final BidDraftFixture bidDraftFixture;

    @Test
    void test() {
        long identifier = 1L;

        final Bid bid = bidDraftFixture.initDraft(identifier);

        assertAll(() -> {
            assertThat(bid.getBidId()).isEqualTo(identifier);
            assertThat(bid.getBidGroupId()).isEqualTo(identifier);
            assertThat(bid.getName()).isEqualTo("name" + identifier);
            assertThat(bid.getBidType()).isEqualTo("bidType" + identifier);
            assertThat(bid.getCreatedBy()).isEqualTo("createdBy" + identifier);
            assertThat(bid.getUpdatedBy()).isEqualTo("updatedBy" + identifier);
            assertFalse(bid.getStartDate().isAfter(now()));
            assertFalse(bid.getEndDate().isAfter(now().plusDays(1)));
            assertThat(bid.getInvalid()).isNull();
            assertFalse(bid.getCreated().isAfter(now()));
            assertFalse(bid.getUpdated().isAfter(now()));
            assertFalse(bid.getRevisionDate().isAfter(now()));
        });
    }
}

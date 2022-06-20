package com.jeppesen.carmen.customization.sas.e2e.fixtures.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.AbstractDbFixtureTest;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidGroup;
import lombok.RequiredArgsConstructor;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import static java.time.LocalDateTime.now;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertFalse;

@DisplayName("Testing bid group draft fixture tests")
@RequiredArgsConstructor(onConstructor_ = @Autowired)
class BidGroupsDraftFixtureTest extends AbstractDbFixtureTest {

    final BidGroupDraftFixture bidGroupDraftFixture;

    @Test
    void test() {
        String identifier = "1";
        final BidGroup bidGroup = bidGroupDraftFixture.initDraft(identifier);

        assertAll(() -> {
            assertThat(bidGroup.getBidGroupId()).isEqualTo(0L);
            assertThat(bidGroup.getName()).isEqualTo("name" + identifier);
            assertThat(bidGroup.getDescription()).isEqualTo("description" + identifier);
            assertThat(bidGroup.getCreatedBy()).isEqualTo("createdBy" + identifier);
            assertThat(bidGroup.getUpdatedBy()).isEqualTo("updatedBy" + identifier);
            assertThat(bidGroup.getType()).isEqualTo("type" + identifier);
            assertThat(bidGroup.getCategory()).isEqualTo(BidGroup.Category.current);
            assertFalse(bidGroup.getCreated().isAfter(now()));
            assertFalse(bidGroup.getUpdated().isAfter(now()));
            assertFalse(bidGroup.getStartDate().isAfter(now()));
            assertFalse(bidGroup.getEndDate().isAfter(now().plusDays(1)));
            assertFalse(bidGroup.getInvalid().isAfter(now()));
            assertFalse(bidGroup.getSubmitted().isAfter(now()));
            assertFalse(bidGroup.getRevisionDate().isAfter(now()));
        });
    }
}

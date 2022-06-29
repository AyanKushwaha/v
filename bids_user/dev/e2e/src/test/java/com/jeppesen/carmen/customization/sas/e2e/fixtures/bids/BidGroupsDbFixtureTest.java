package com.jeppesen.carmen.customization.sas.e2e.fixtures.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.AbstractDbFixtureTest;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidGroup;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidGroupOrder;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidGroupOrderRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidGroupRepository;
import lombok.RequiredArgsConstructor;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertAll;

@DisplayName("Testing bid groups DB fixture tests")
@RequiredArgsConstructor(onConstructor_ = @Autowired)
class BidGroupsDbFixtureTest extends AbstractDbFixtureTest {

    final BidGroupDbFixture bidGroupDbFixture;
    final BidGroupRepository bidGroupRepository;
    final BidGroupOrderRepository bidGroupOrderRepository;

    @AfterEach
    void cleanUpDb() {
        bidGroupOrderRepository.deleteAll();
        assertThat(bidGroupOrderRepository.findAll()).isEmpty();

        bidGroupRepository.deleteAll();
        assertThat(bidGroupRepository.findAll()).isEmpty();
    }

    @Test
    @DisplayName("should create specific drafted bid group with bid group order entry")
    void test() {
        String userId = "TestUser";

        final BidGroup created = bidGroupDbFixture.create(bg -> bg.setUserId(userId).setName("TestBidGroup"));
        final BidGroup dbBidGroup = bidGroupRepository.findAllByUserId(userId).get(0);
        final List<BidGroupOrder> bidGroupOrders = bidGroupOrderRepository.finaAllUserBidGroupOrders(userId);

        assertAll(() -> {
            assertThat(dbBidGroup.getUserId()).isEqualTo(userId);
            assertThat(dbBidGroup.getName()).isEqualTo(created.getName());
            bidGroupOrders.forEach(bgo -> assertThat(dbBidGroup.getBidGroupId()).isEqualTo(bgo.getBidGroupId()));
        });
    }
}

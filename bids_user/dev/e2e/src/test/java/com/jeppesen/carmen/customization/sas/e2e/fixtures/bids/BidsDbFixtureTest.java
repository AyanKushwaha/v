package com.jeppesen.carmen.customization.sas.e2e.fixtures.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.AbstractDbFixtureTest;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.Bid;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidOrder;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidProperty;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidPropertyEntry;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.*;
import com.jeppesen.carmen.customization.sas.e2e.po.AdministrationPage;
import lombok.RequiredArgsConstructor;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertAll;

@DisplayName("Testing bids DB fixture tests")
@RequiredArgsConstructor(onConstructor_ = @Autowired)
class BidsDbFixtureTest extends AbstractDbFixtureTest {

    final BidDbFixture bidDbFixture;
    final BidRepository bidRepository;
    final BidGroupRepository bidGroupRepository;
    final BidOrderRepository bidOrderRepository;
    final BidPropertyRepository bidPropertyRepository;
    final BidGroupOrderRepository bidGroupOrderRepository;
    final BidPropertyEntryRepository bidPropertyEntryRepository;
    final AdministrationPage administrationPage;

    @AfterEach
    void cleanUpDb() {
        bidOrderRepository.deleteAll();
        assertThat(bidOrderRepository.findAll()).isEmpty();

        bidPropertyEntryRepository.deleteAll();
        assertThat(bidPropertyEntryRepository.findAll()).isEmpty();

        bidPropertyRepository.deleteAll();
        assertThat(bidPropertyRepository.findAll()).isEmpty();

        bidGroupOrderRepository.deleteAll();
        assertThat(bidGroupOrderRepository.findAll()).isEmpty();

        bidGroupRepository.deleteAll();
        assertThat(bidGroupRepository.findAll()).isEmpty();

        bidRepository.deleteAll();
        assertThat(bidRepository.findAll()).isEmpty();
    }

    @Test
    @DisplayName("should create specific drafted bid with generated bid property and bid property entry")
    void testCreateBidWithGeneratedProperties() {
        LocalDateTime startTime = LocalDateTime.now();
        LocalDateTime endTime = startTime.plusDays(3);
        String userId = "TestUser";
        String bidName = "Test";

        final Bid created = bidDbFixture.create(b -> b.setCreatedBy(userId)
                .setName(bidName)
                .setStartDate(startTime)
                .setEndDate(endTime));
        final Bid dbBid = bidRepository.findById(created.getBidId())
                .orElseThrow(() -> new RuntimeException("bid " + created.getBidId() + " not found"));
        final List<BidProperty> bidProperties = bidPropertyRepository.findAllByBidCreatedBy(userId);
        final List<BidPropertyEntry> bidPropertyEntries = bidPropertyEntryRepository.findAllUserBidPropertyEntries(userId);
        final List<BidOrder> bidOrders = bidOrderRepository.findAllUserBidOrders(userId);

        assertAll(() -> {
            assertThat(dbBid.getCreatedBy()).isEqualTo(userId);
            assertThat(dbBid.getName()).isEqualTo(bidName);
            assertThat(dbBid.getStartDate()).isEqualTo(startTime);
            assertThat(dbBid.getEndDate()).isEqualTo(endTime);
            assertThat(dbBid.getBidId()).isEqualTo(dbBid.getBidSequenceId());
            bidProperties.forEach(bp -> {
                assertThat(dbBid).isEqualTo(bp.getBid());
                bidPropertyEntries.forEach(bpe -> assertThat(bp).isEqualTo(bpe.getBidProperty()));
            });
            bidOrders.forEach(bo -> assertThat(dbBid.getBidId()).isEqualTo(bo.getBidId()));
        });
    }

    @Test
    @DisplayName("should create drafted bid with specific properties")
    void testCreateBidWithSpecificProperties() {
        String userId = "TestUser";
        Map<String, String> propertyEntries = new HashMap<>();
        propertyEntries.put("days", "4");
        propertyEntries.put("points", "70");
        Map<String, Map<String, String>> properties = new HashMap<>();
        properties.put("number_of_days", propertyEntries);

        final Bid created = bidDbFixture.create(b -> b.setCreatedBy(userId), properties);

        final Bid dbBid = bidRepository.findById(created.getBidId())
                .orElseThrow(() -> new RuntimeException("bid " + created.getBidId() + " not found"));
        final List<BidProperty> dbBidProperties = bidPropertyRepository.findAllByBidCreatedBy(userId);
        final List<BidPropertyEntry> dbBidPropertyEntries = bidPropertyEntryRepository.findAllUserBidPropertyEntries(userId);

        assertAll(() -> {
            assertThat(dbBid.getCreatedBy()).isEqualTo(userId);
            dbBidProperties.forEach(bp -> {
                assertThat(dbBid).isEqualTo(bp.getBid());
                properties.forEach((key, value) -> assertThat(key).isEqualTo(bp.getBidPropertyType()));
                assertThat(dbBidPropertyEntries.size()).isEqualTo(propertyEntries.size());

                dbBidPropertyEntries.forEach(bpe -> {
                    assertThat(bp).isEqualTo(bpe.getBidProperty());
                    assertThat(bpe.getEntryValue()).isEqualTo(propertyEntries.get(bpe.getEntryKey()));
                });
            });
        });
    }
}

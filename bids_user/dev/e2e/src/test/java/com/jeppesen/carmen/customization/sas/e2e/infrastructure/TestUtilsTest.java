package com.jeppesen.carmen.customization.sas.e2e.infrastructure;

import com.jeppesen.carmen.customization.sas.e2e.AbstractSelenideTest;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.bids.BidDbFixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.Bid;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidProperty;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidPropertyEntry;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.User;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.UserAttribute;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidPropertyEntryRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidPropertyRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.users.UserAttributeRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.users.UserRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.users.UserAttributeDbFixture;
import com.jeppesen.carmen.customization.sas.e2e.po.AdministrationPage;
import lombok.AllArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.TestUtils.addAttributeToUser;
import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.TestUtils.deleteBid;
import static java.lang.String.format;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertAll;

@Log4j2
@Tag("PO")
@DisplayName("Utility tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
class TestUtilsTest extends AbstractSelenideTest {

    final CrewPortalProps props;
    final BidDbFixture bidDbFixture;
    final BidRepository bidRepository;
    final BidPropertyRepository bidPropertyRepository;
    final BidPropertyEntryRepository bidPropertyEntryRepository;
    final AdministrationPage administrationPage;
    final UserRepository userRepository;
    final UserAttributeRepository userAttributeRepository;
    final UserAttributeDbFixture userAttributeDbFixture;

    @Test
    @DisplayName("should delete bids and flush cache")
    void should_delete_bids_and_flush_cache() {

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
            assertThat(dbBid).isNotNull();
            assertThat(dbBidProperties.size()).isEqualTo(properties.size());
            assertThat(dbBidPropertyEntries.size()).isEqualTo(propertyEntries.size());
        });

        deleteBid(dbBid, bidRepository, bidPropertyRepository, bidPropertyEntryRepository, administrationPage);

        assertAll(() -> {
            assertThat(bidRepository.findById(dbBid.getBidId())).isEqualTo(Optional.empty());
            assertThat(bidPropertyRepository.findAllByBidCreatedBy(userId)).isEmpty();
            assertThat(bidPropertyEntryRepository.findAllUserBidPropertyEntries(userId)).isEmpty();
        });
    }

    @Test
    @DisplayName("should update existing user attribute")
    void should_update_existing_user_attribute() {
        final String testAttributeName = "testAttributeName";
        final String previousValue = "test_attribute_value";
        final String newValue = "test_attribute_value2";

        String userId = props.getLogin().getCrew().getUsername();
        // add new user attribute
        addAttributeToUser(userId, testAttributeName, previousValue, userRepository, userAttributeDbFixture);
        // update attribute added in previous step to new value
        addAttributeToUser(userId, testAttributeName, newValue, userRepository, userAttributeDbFixture);

        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException(format("user with id=%s not found", userId)));

        UserAttribute ua = userAttributeRepository.findByUserAndAttributeName(user, testAttributeName)
                .orElseThrow(() -> new RuntimeException(format("attribute with name=%s not found", testAttributeName)));
        assertThat(ua.getAttributeValue().equals(newValue)).isTrue();
    }
}

package com.jeppesen.carmen.customization.sas.e2e.userstories.fda;

import com.jeppesen.carmen.customization.sas.e2e.AbstractSelenideTest;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidPropertyEntryRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidPropertyRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidRepository;
import com.jeppesen.carmen.customization.sas.e2e.po.AdministrationPage;
import lombok.AllArgsConstructor;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;

import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.TestUtils.flushCache;

@Tags({
        @Tag("E2E"), @Tag("F")
})
@DisplayName("FDA position E2E tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
public class FDAPositionBidTest extends AbstractSelenideTest {

    AdministrationPage administrationPage;
    BidRepository bidRepository;
    BidPropertyRepository bidPropertyRepository;
    BidPropertyEntryRepository bidPropertyEntryRepository;

    @Test
    @DisplayName("should create FDA Vacation bid if data is well formed")
    void should_create_FDA_Vacation_bid_if_data_is_well() {

        administrationPage.open()
                .home().fdaTab().careerWindow()
                .clickPlaceBid()
                .createFdaPositionBid()
                .verifyBidVisibilityOfNrExactOnFDATab("FDA Position", 5)
                .close();
    }

    @AfterAll
    void cleanUp() {
        flushCache(administrationPage);
    }
}

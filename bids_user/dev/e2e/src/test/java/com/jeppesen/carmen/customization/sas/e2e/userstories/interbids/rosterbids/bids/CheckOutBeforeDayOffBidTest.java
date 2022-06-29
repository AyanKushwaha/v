package com.jeppesen.carmen.customization.sas.e2e.userstories.interbids.rosterbids.bids;


import com.jeppesen.carmen.customization.sas.e2e.AbstractSelenideTest;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.PeriodsDbFixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.PeriodRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidPropertyEntryRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidPropertyRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidRepository;
import com.jeppesen.carmen.customization.sas.e2e.po.AdministrationPage;
import lombok.AllArgsConstructor;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;

import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.TestUtils.*;

@Tags({
        @Tag("E2E"), @Tag("C")
})
@DisplayName("Check Out Before Day Off Bid E2E tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
public class CheckOutBeforeDayOffBidTest extends AbstractSelenideTest {

    PeriodsDbFixture periodsDbFixture;
    PeriodRepository periodRepository;
    BidRepository bidRepository;
    BidPropertyRepository bidPropertyRepository;
    BidPropertyEntryRepository bidPropertyEntryRepository;
    AdministrationPage administrationPage;

    @BeforeEach
    void setUp() {
        preparePeriodForGroup("CC SKD VG", periodRepository, periodsDbFixture, administrationPage);
    }

    @Test
    @DisplayName("should create Check Out Before Day Off bid if data is well formed")
    void should_create_Check_Out_Before_Day_Off_bid_if_data_is_well() {

        String criteria = "Check out before day off - before 00:00 bid placed from 15Mar20 to 16Mar20";
        String firstDate = "15Mar20";
        String secondDate = "16Mar20";

        administrationPage
                .proxyUserById("testCrew")
                .home().interbidsTab().bidWindow().bidTab().currentBid()
                .clickPlaceBid()
                .createCheckOutBeforeDayOffBid(firstDate, secondDate)
                .verifyBidVisibilityOfNrExact(criteria, 1)
                .close();
    }

    @AfterEach
    void tearDown() {
        deleteLastBid(bidRepository, bidPropertyRepository, bidPropertyEntryRepository, administrationPage);
    }

    @AfterAll
    void cleanUp() {
        deletePeriodsAndFlushCache(periodRepository, administrationPage);
    }
}

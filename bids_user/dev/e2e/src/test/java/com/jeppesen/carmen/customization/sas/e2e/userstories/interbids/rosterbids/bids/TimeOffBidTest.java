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
        @Tag("E2E"), @Tag("T")
})
@DisplayName("TimeOff E2E tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
class TimeOffBidTest extends AbstractSelenideTest {

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
    @DisplayName("should create and validate is not duplicated Time Off bid if data is well formed")
    void should_create_and_validate_is_not_duplicated_Time_Off_bid_if_data_is_well() {

        String criteria = "Time off - from 15Mar20 00:00 to 16Mar20 00:00";
        String firstDate = "15Mar20";
        String secondDate = "16Mar20";

        administrationPage.open()
                .proxyUserById("testCrew")
                .home().interbidsTab().bidWindow().bidTab().currentBid()
                .clickPlaceBid()
                .createTimeOffBid(firstDate, secondDate)
                .verifyBidVisibilityOfNrExact(criteria, 1)
                .clickPlaceBid()
                .validateTimeOffBidNotDuplicated(firstDate, secondDate)
                .close();
    }

    @Test
    @DisplayName("should not create Time Off bid if period is large")
    void should_not_create_Time_Off_bid_if_period_is_large() {

        String firstDate = "15Mar20";
        String secondDate = "15Apr20";

        administrationPage
                .proxyUserById("testCrew")
                .home().interbidsTab().bidWindow().bidTab().currentBid()
                .clickPlaceBid()
                .createTimeOffBid(firstDate, secondDate)
                .verityTextPresentOnPage("\"TimeOff bid period duration is exceeded. Maximum allowed duration: 72 hours.\"")
                .clickButtonOk()
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

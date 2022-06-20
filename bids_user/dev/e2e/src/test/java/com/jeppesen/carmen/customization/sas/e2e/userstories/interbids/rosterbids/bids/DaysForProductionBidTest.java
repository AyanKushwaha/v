package com.jeppesen.carmen.customization.sas.e2e.userstories.interbids.rosterbids.bids;

import com.jeppesen.carmen.customization.sas.e2e.AbstractSelenideTest;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.PeriodsDbFixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.PeriodRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidPropertyEntryRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidPropertyRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidRepository;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.CrewPortalProps;
import com.jeppesen.carmen.customization.sas.e2e.po.AdministrationPage;
import lombok.AllArgsConstructor;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;

import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.TestUtils.*;

@Tags({
        @Tag("E2E"), @Tag("D")
})
@DisplayName("Days For Production E2E tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
public class DaysForProductionBidTest extends AbstractSelenideTest {

    CrewPortalProps props;
    PeriodsDbFixture periodsDbFixture;
    PeriodRepository periodRepository;
    BidRepository bidRepository;
    BidPropertyRepository bidPropertyRepository;
    BidPropertyEntryRepository bidPropertyEntryRepository;
    AdministrationPage administrationPage;

    @BeforeEach
    void setUp() {
        preparePeriodForFirstGroup(props, periodRepository, periodsDbFixture, administrationPage);
    }

    @Test
    @DisplayName("should create and validate is not duplicated Days For Production bid if data is well formed")
    void should_create_and_validate_is_not_duplicated_Days_For_Production_bid_if_data_is_well() {

        String criteria = "Days for production - from 01Apr20 to 01Apr20";
        String firstDate = "01Apr20";
        String secondDate = "01Apr20";

        administrationPage
                .proxyUserById("testCrew1")
                .home().interbidsTab().bidWindow().bidTab().currentBid()
                .clickPlaceBid()
                .createDaysForProductionBid(firstDate, secondDate)
                .verifyBidVisibilityOfNrExact(criteria, 1)
                .clickPlaceBid()
                .validateDaysForProductionBid(firstDate, secondDate)
                .close();
    }

    @Test
    @DisplayName("should not create Days For Production bid if period is overlap")
    void should_not_create_Days_For_Production_bid_if_period_is_overlap() {

        String firstDate = "31Mar20";
        String secondDate = "31Mar20";

        administrationPage
                .proxyUserById("testCrew1")
                .home().interbidsTab().bidWindow().bidTab().currentBid()
                .clickPlaceBid()
                .createDaysForProductionBid(firstDate, secondDate)
                .verityTextPresentOnPage("The bid overlaps a preassigned activity.")
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

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
@DisplayName("Compensation Day E2E tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
public class CompensationDayBidTest extends AbstractSelenideTest {

    PeriodsDbFixture periodsDbFixture;
    PeriodRepository periodRepository;
    BidRepository bidRepository;
    BidPropertyRepository bidPropertyRepository;
    BidPropertyEntryRepository bidPropertyEntryRepository;
    AdministrationPage administrationPage;

    @BeforeAll
    void setUp() {
        preparePeriodForGroup("CC SKD VG", periodRepository, periodsDbFixture, administrationPage);
    }

    @Test
    @DisplayName("should create Compensation Days bid if data is well formed")
    void should_create_Compensation_Days_bid_if_data_is_well() {

        String criteria = "Compensation days - from 14Mar20, 00:00 - 23:59, 1 days of type F3";

        administrationPage
                .proxyUserById("testCrew")
                .home().interbidsTab().bidWindow().bidTab().currentBid()
                .clickPlaceBid()
                .createCompensationDaysBid()
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

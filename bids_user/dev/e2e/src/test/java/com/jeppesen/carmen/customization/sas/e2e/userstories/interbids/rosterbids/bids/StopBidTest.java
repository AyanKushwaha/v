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
        @Tag("E2E"), @Tag("S")
})
@DisplayName("Stop E2E tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
public class StopBidTest extends AbstractSelenideTest {

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
    @DisplayName("should create Stop bid if data is well formed")
    void should_create_Stop_bid_if_data_is_well() {

        String criteria = "Stop - ABV - Min: 5:00 Max: 300:00 - from 14Mar20 to UFN";

        administrationPage
                .proxyUserById("testCrew")
                .home().interbidsTab().bidWindow().bidTab().currentBid()
                .clickPlaceBid()
                .createStopBid()
                .verifyBidVisibilityOfNrExact(criteria, 1)
                .clickPlaceBid()
                .validateStopBidNotDuplicated()
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

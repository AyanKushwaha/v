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
        @Tag("E2E"), @Tag("F")
})
@DisplayName("Flight E2E tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
public class FlightBidTest extends AbstractSelenideTest {

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
    @DisplayName("should create Flight bid if data is well formed")
    void should_create_Flight_bid_if_data_is_well() {

        String criteria = "Flight - Flight number SK0101, Departure date 16Apr20";

        administrationPage
                .proxyUserById("testCrew")
                .home().interbidsTab().bidWindow().bidTab().currentBid()
                .clickPlaceBid()
                .createFlightBid()
                .verifyBidVisibilityOfNrExact(criteria, 1)
                .clickPlaceBid()
                .validateFlightBidNotDuplicated()
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

package com.jeppesen.carmen.customization.sas.e2e.userstories.interbids.rosterbids.lifestyle;

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
        @Tag("E2E"), @Tag("L")
})
@DisplayName("Lifestyle Bid E2E tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
public class LifestyleBidTest extends AbstractSelenideTest {

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
    @DisplayName("should create and validate is not duplicated Morning person")
    void should_create_and_validate_is_not_duplicated_morning_person() {
        String nameLifestyle = "Morning person";

        administrationPage
                .proxyUserById("testCrew")
                .home().interbidsTab().bidWindow().clickLifestyleTab()
                .currentLifestyle()
                .clickPlaceBid()
                .createLifestyle(nameLifestyle)
                .verifyBidVisibilityOfNrExact("Morning Person", 1)
                .clickPlaceBid()
                .validateLifestyleNotDuplicated(nameLifestyle)
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

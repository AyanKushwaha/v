package com.jeppesen.carmen.customization.sas.e2e.userstories.interbids.requests;

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
@DisplayName("FS tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
public class FSRequestTest extends AbstractSelenideTest {

    PeriodsDbFixture periodsDbFixture;
    PeriodRepository periodRepository;
    BidRepository bidRepository;
    BidPropertyRepository bidPropertyRepository;
    BidPropertyEntryRepository bidPropertyEntryRepository;
    AdministrationPage administrationPage;

    @BeforeEach
    void setUp() {
        preparePeriodByTypeForGroup("CC SKD VG", "A_FS", periodRepository, periodsDbFixture, administrationPage);
    }

    @Test
    @DisplayName("should create FS request if data is well formed")
    void should_create_FS_request_if_data_is_well() {

        String date = "01Apr20";

        administrationPage
                .proxyUserById("testCrew")
                .home().interbidsTab().bidWindow().requestTab().currentRequest()
                .clickPlaceRequest()
                .createFSRequest(date)
                .close();
    }

    @Test
    @DisplayName("should not create FS request if data is overlapping")
    void should_not_create_FS_request_if_date_is_overlapping() {

        String date = "18Mar20";

        administrationPage
                .proxyUserById("testCrew")
                .home().interbidsTab().bidWindow().requestTab().currentRequest()
                .clickPlaceRequest()
                .createFSRequest(date)
                .verityTextPresentOnPage("Request is overlapping preassignment")
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

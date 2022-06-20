package com.jeppesen.carmen.customization.sas.e2e.userstories;

import com.jeppesen.carmen.customization.sas.e2e.AbstractSelenideTest;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.PeriodsDbFixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.PeriodRepository;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.CrewPortalProps;
import com.jeppesen.carmen.customization.sas.e2e.po.AdministrationPage;
import com.jeppesen.carmen.customization.sas.e2e.po.BiddingPage;
import lombok.AllArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;

import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.TestUtils.deletePeriodsAndFlushCache;
import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.TestUtils.preparePeriodForFirstGroup;

@Log4j2
@Tags({
        @Tag("E2E"), @Tag("B")
})
@DisplayName("Bidding E2E tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
class BiddingTest extends AbstractSelenideTest {

    BiddingPage biddingPage;
    CrewPortalProps props;
    PeriodsDbFixture periodsDbFixture;
    PeriodRepository periodRepository;
    AdministrationPage administrationPage;

    @BeforeAll
    void init() {
        preparePeriodForFirstGroup(props, periodRepository, periodsDbFixture, administrationPage);
    }

    @Test
    @DisplayName("should delete all bids")
    void should_delete_all_bids() {

        biddingPage.open().bidWindow().bidTab().currentBid()
                .deleteAllBids()
                .close();
    }

    @AfterAll
    void cleanUp() {
        deletePeriodsAndFlushCache(periodRepository, administrationPage);
    }
}

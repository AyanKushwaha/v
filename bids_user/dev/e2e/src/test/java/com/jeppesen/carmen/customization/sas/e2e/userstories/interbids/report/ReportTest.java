package com.jeppesen.carmen.customization.sas.e2e.userstories.interbids.report;

import com.jeppesen.carmen.customization.sas.e2e.AbstractSelenideTest;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.PeriodsDbFixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.PeriodRepository;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.CrewPortalProps;
import com.jeppesen.carmen.customization.sas.e2e.po.AdministrationPage;
import com.jeppesen.carmen.customization.sas.e2e.po.BiddingPage;
import lombok.AllArgsConstructor;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;

import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.TestUtils.deletePeriodsAndFlushCache;
import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.TestUtils.preparePeriodForFirstGroup;

@Tags({
        @Tag("E2E"), @Tag("R")
})
@DisplayName("Report E2E tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
class ReportTest extends AbstractSelenideTest {

    BiddingPage biddingPage;
    CrewPortalProps props;
    PeriodsDbFixture periodsDbFixture;
    PeriodRepository periodRepository;
    AdministrationPage administrationPage;

    @BeforeEach
    void setUp() {
        preparePeriodForFirstGroup(props, periodRepository, periodsDbFixture, administrationPage);
    }

    @Test
    @DisplayName("should check general report is visible")
    void should_check_general_report_is_visible() {

        biddingPage.open()
                .bidWindow().reportSubTab()
                .validateFieldIsVisible("All-crew-report.pdf")
                .close();
    }

    @Test
    @DisplayName("should check private report is visible")
    void should_check_private_report_is_visible() {

        biddingPage.open()
                .bidWindow().reportSubTab()
                .validateFieldIsVisible("crew-report.pdf")
                .close();
    }

    @AfterAll
    void cleanUp() {
        deletePeriodsAndFlushCache(periodRepository, administrationPage);
    }
}

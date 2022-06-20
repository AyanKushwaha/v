package com.jeppesen.carmen.customization.sas.e2e.userstories;

import com.jeppesen.carmen.customization.sas.e2e.AbstractSelenideTest;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.PeriodsDbFixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.PeriodRepository;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.CrewPortalProps;
import com.jeppesen.carmen.customization.sas.e2e.po.AdministrationPage;
import lombok.AllArgsConstructor;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;

import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.TestUtils.deletePeriodsAndFlushCache;
import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.TestUtils.preparePeriodForFirstGroup;

@Tags({
        @Tag("E2E"), @Tag("P")
})
@DisplayName("Proxy User E2E tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
public class ProxyUserTest extends AbstractSelenideTest {

    CrewPortalProps props;
    AdministrationPage administrationPage;
    PeriodRepository periodRepository;
    PeriodsDbFixture periodDbFixture;

    @BeforeAll
    void init() {
        preparePeriodForFirstGroup(props, periodRepository, periodDbFixture, administrationPage);
    }

    @Test
    @DisplayName("should show correct bid period in Calendar for proxy user")
    public void should_show_correct_bid_period_in_Calendar_for_proxy_user() {

        administrationPage.open().home()
                .clickUsersMenu()
                .fillField("User Id:", "testCrew1")
                .clickSearchButton()
                .shouldFindUser("testCrew1")
                .clickButtonProxy();

        administrationPage.home().interbidsTab()
                .bidWindow()
                .bidTab()
                .currentBid()
                .clickCurrentWeek()
                .close();

    }

    @AfterAll
    void cleanUp() {
        deletePeriodsAndFlushCache(periodRepository, administrationPage);
    }
}

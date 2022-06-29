package com.jeppesen.carmen.customization.sas.e2e.po;

import com.jeppesen.carmen.customization.sas.e2e.AbstractSelenideTest;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.PeriodsDbFixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.PeriodRepository;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.CrewPortalProps;
import lombok.AllArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import static com.codeborne.selenide.Condition.exactText;
import static com.codeborne.selenide.Selectors.byText;
import static com.codeborne.selenide.Selenide.$;
import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.PageObjects.existAndVisible;

@Log4j2
@Tag("PO")
@DisplayName("User PO tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
class UserHomePageTest extends AbstractSelenideTest {

    CrewPortalProps props;
    BiddingPage homePage;
    PeriodsDbFixture periodsDbFixture;
    PeriodRepository periodRepository;
    AdministrationPage administrationPage;

    @Test
    @DisplayName("should not open PBS page after period deleted and flushed by admin")
    void should_not_open_PBS_page_after_period_deleted_and_flushed_by_admin() {
        when_period_deleted_and_cache_flushed_by_admin();
        then_user_should_not_see_PBS_page();
    }

    private void when_period_deleted_and_cache_flushed_by_admin() {
        periodRepository.deleteAll();
        administrationPage.open().home().clickServersMenu().flushCacheRequest()//.flushCache()
                .close();
    }

    private void then_user_should_not_see_PBS_page() {
        homePage.open().bidWindow();
        $(".noperiod").shouldBe(existAndVisible)
                .find(byText("No current or future bid period defined, please contact Administrator."));
        homePage.close();
    }
}

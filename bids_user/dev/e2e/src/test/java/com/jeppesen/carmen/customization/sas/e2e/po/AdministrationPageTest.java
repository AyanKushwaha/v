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
@DisplayName("Administration PO tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
class AdministrationPageTest extends AbstractSelenideTest {

    BiddingPage biddingPage;
    CrewPortalProps props;
    PeriodsDbFixture periodsDbFixture;
    PeriodRepository periodRepository;
    AdministrationPage administrationPage;

    @Test
    @DisplayName("should flush server cache")
    void should_flush_server_cache() {
        administrationPage.open()
                .clickServersMenu()
                .flushCache()
                .close();
    }

    @Test
    @Tag("REST")
    @DisplayName("should flush server cache using REST API")
    void should_flush_server_cache_using_REST_API() {

        when_period_created();
        administrationPage.open().clickServersMenu().flushCacheRequest()
                .close();

        then_open_PBS_page();
        then_period_deleted();

        administrationPage.open().clickServersMenu().flushCacheRequest()
                .close();

        then_open_PBS_page_and_see_no_period_error_message();
    }

    private void when_period_created() {
        periodRepository.deleteAll();
        String groupName = props.getAdministrationPage().getGroups().iterator().next();
        periodsDbFixture.createForGroup(groupName);
    }

    private void then_period_deleted() {
        periodRepository.deleteAll();
    }

    private void then_open_PBS_page() {
        biddingPage.open().bidWindow().bidTab();
        log.info("should see Current Bids");
        $("#MainView_bidsTab").shouldBe(existAndVisible)
                .find(byText("Current Bids"))
                .shouldBe(existAndVisible);
        biddingPage.close();
    }

    private void then_open_PBS_page_and_see_no_period_error_message() {
        biddingPage.open().bidWindow();
        log.info("should not see Bid Window");
        $(".noperiod").shouldBe(existAndVisible)
                .shouldHave(exactText("No current or future bid period defined, please contact Administrator."));
        biddingPage.close();
    }
}

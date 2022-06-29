package com.jeppesen.carmen.customization.sas.e2e.po;

import com.jeppesen.carmen.customization.sas.e2e.AbstractSelenideTest;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.PeriodsDbFixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.PeriodRepository;
import lombok.AllArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import static com.codeborne.selenide.Condition.exactText;
import static com.codeborne.selenide.Selectors.byText;
import static com.codeborne.selenide.Selenide.$;
import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.PageObjects.existAndVisible;
import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.TestUtils.deletePeriodsAndFlushCache;
import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.TestUtils.preparePeriodForGroup;

@Log4j2
@Tag("PO")
@DisplayName("Interbids PO tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
class InterbidsPageTest extends AbstractSelenideTest {

    BiddingPage biddingPage;
    PeriodsDbFixture periodsDbFixture;
    PeriodRepository periodRepository;
    AdministrationPage administrationPage;

    @Test
    @DisplayName("should login, open Interbids page successfully if proper period exists")
    void should_open_Interbids_page() {

        preparePeriodForGroup("CC RP", periodRepository, periodsDbFixture, administrationPage);

        biddingPage.open().bidWindow().bidTab();
        log.info("should see Bid Window");
        $("#MainView_bidsTab").shouldBe(existAndVisible)
                .find(byText("Current Bids"))
                .shouldBe(existAndVisible);
        biddingPage.close();
    }

    @Test
    @DisplayName("should open Interbids page and see 'no period' error message if proper period doesn't exist")
    void should_open_Interbids_page_and_see_no_period_error_message_if_proper_period_does_not_exist() {

        deletePeriodsAndFlushCache(periodRepository, administrationPage);

        biddingPage.open().bidWindow();
        log.info("should not see Bid Window");
        $(".noperiod").shouldBe(existAndVisible)
                .shouldHave(exactText("No current or future bid period defined, please contact Administrator."));
        biddingPage.close();
    }

    @AfterAll
    void cleanUp() {
        deletePeriodsAndFlushCache(periodRepository, administrationPage);
    }
}

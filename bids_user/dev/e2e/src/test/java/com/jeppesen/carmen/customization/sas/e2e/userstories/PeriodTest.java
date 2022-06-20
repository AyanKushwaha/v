package com.jeppesen.carmen.customization.sas.e2e.userstories;

import com.jeppesen.carmen.customization.sas.e2e.AbstractSelenideTest;
import com.jeppesen.carmen.customization.sas.e2e.po.AdministrationPage;
import lombok.AllArgsConstructor;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Tags;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

@Tags({
        @Tag("E2E"), @Tag("P")
})
@DisplayName("Period E2E tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
class PeriodTest extends AbstractSelenideTest {

    AdministrationPage administrationPage;

    @Test
    @DisplayName("should create update and delete periods")
    void should_create_update_and_delete_periods() {
        administrationPage.open().clickPeriodsMenu().deleteAllPeriods()
                .home().clickServersMenu().flushCacheRequest()
                .home().clickPeriodsMenu().createStandardPeriod("CC SKD VG")
                .editPeriod("CC SKD VG", "CC RP")
                .deletePeriod("CC RP")
                .home().clickServersMenu().flushCacheRequest()
                .close();
    }

    @Test
    @DisplayName("should delete all periods, create a new one flush cache and delete all periods again")
    void should_delete_all_periods_create_new_one_flush_cache_and_delete_all_periods_again() {
        administrationPage.open().clickPeriodsMenu().deleteAllPeriods();
        administrationPage.home().clickPeriodsMenu().createStandardPeriod();
        administrationPage.home().clickServersMenu().flushCacheRequest();
        administrationPage.home().clickPeriodsMenu().deleteAllPeriods();
        administrationPage.close();
    }
}

package com.jeppesen.carmen.customization.sas.e2e.userstories.vacation;

import com.jeppesen.carmen.customization.sas.e2e.AbstractSelenideTest;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidPropertyEntryRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidPropertyRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidRepository;
import com.jeppesen.carmen.customization.sas.e2e.po.AdministrationPage;
import lombok.AllArgsConstructor;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;

import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.TestUtils.flushCache;

@Tags({
        @Tag("E2E"), @Tag("P")
})
@DisplayName("Postpone vacation E2E tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
public class PostponeVacationBidTest extends AbstractSelenideTest {

    AdministrationPage administrationPage;
    BidRepository bidRepository;
    BidPropertyRepository bidPropertyRepository;
    BidPropertyEntryRepository bidPropertyEntryRepository;

    @Test
    @DisplayName("should create Postpone Vacation bid if data is well formed")
    void should_create_Postpone_Vacation_bid_if_data_is_well() {

        String days = "5";

        administrationPage.open()
                .home().vacationTab().vacationWindow()
                .clickPlaceBid()
                .createPostponeVacationBid(days)
                .verifyBidVisibilityOfNrExactOnVacationTab("Postpone Vacation", 2)
                .close();
    }

    @Test
    @DisplayName("should not create Postpone Vacation bid if data of days is wrong")
    void should_not_create_Postpone_Vacation_bid_if_data_of_days_is_wrong() {

        administrationPage.open()
                .home().vacationTab().vacationWindow()
                .clickPlaceBid()
                .createPostponeVacationBid(null)
                .verityTextPresentOnPage("The bid dialog contains invalid data.")
                .close();
    }

    @AfterAll
    void cleanUp() {
        flushCache(administrationPage);
    }
}

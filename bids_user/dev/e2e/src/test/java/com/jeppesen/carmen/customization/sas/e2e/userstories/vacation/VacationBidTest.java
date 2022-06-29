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
        @Tag("E2E"), @Tag("V")
})
@DisplayName("Vacation E2E tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
public class VacationBidTest extends AbstractSelenideTest {
    AdministrationPage administrationPage;
    BidRepository bidRepository;
    BidPropertyRepository bidPropertyRepository;
    BidPropertyEntryRepository bidPropertyEntryRepository;

    @Test
    @DisplayName("should create Vacation bid if data is well formed")
    void should_create_Vacation_bid_if_data_is_well() {

        String firstDayNumber = "2";
        String secondDayNumber = "3";
        String comment = "Test comment";

        administrationPage.open()
                .home().vacationTab().vacationWindow()
                .clickPlaceBid()
                .createVacationBid(firstDayNumber, secondDayNumber, comment)
                .verifyBidVisibilityOfNrExactOnVacationTab("Vacation", 3)
                .close();
    }

    @AfterAll
    void cleanUp() {
        flushCache(administrationPage);
    }
}

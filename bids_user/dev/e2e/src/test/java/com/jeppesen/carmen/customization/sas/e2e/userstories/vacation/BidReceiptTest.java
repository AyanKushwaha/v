package com.jeppesen.carmen.customization.sas.e2e.userstories.vacation;

import com.jeppesen.carmen.customization.sas.e2e.AbstractSelenideTest;
import com.jeppesen.carmen.customization.sas.e2e.po.AdministrationPage;
import lombok.AllArgsConstructor;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Tags;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

@Tags({
        @Tag("E2E"), @Tag("B")
})
@DisplayName("Bid Receipt E2E tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
public class BidReceiptTest extends AbstractSelenideTest {
    AdministrationPage administrationPage;

    @Test
    @DisplayName("should create Vacation bid if data is well formed")
    void should_create_Vacation_bid_if_data_is_well() {

        administrationPage.open()
                .home().vacationTab().vacationWindow()
                .clickBidReceipt()
                .clickClose()
                .close();
    }
}

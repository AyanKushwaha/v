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
        @Tag("E2E"), @Tag("G")
})
@DisplayName("Group E2E tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
class GroupsTest extends AbstractSelenideTest {

    AdministrationPage administrationPage;

    @Test
    @DisplayName("should create verify and delete group")
    void should_create_verify_and_delete_group() {

        administrationPage.open()
                .clickGroupsMenu()
                .createGroup("TestGroup")
                .verifyGroupIsNotDuplicated("TestGroup")
                .deleteGroup("TestGroup")
                .close();
    }
}

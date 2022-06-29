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
        @Tag("E2E"), @Tag("U")
})
@DisplayName("Users Search E2E tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
public class UserSearchTest extends AbstractSelenideTest {

    AdministrationPage administrationPage;

    @Test
    @DisplayName("should search all users")
    void should_search_all_users() {
        administrationPage.open().home()
                .clickUsersMenu()
                .clickSearchButton()
                .shouldFindUsers(3)
                .shouldFindUser("admin")
                .shouldFindUser("testCrew");
    }

    @Test
    @DisplayName("should search user by first name")
    void should_search_user_by_FirstName() {
        administrationPage.open().home()
                .clickUsersMenu()
                .fillField("First Name:", "Admin")
                .clickSearchButton()
                .shouldFindUser("admin");
    }

    @Test
    @DisplayName("should search users by group")
    void should_search_users_by_Group() {
        administrationPage.open().home()
                .clickUsersMenu()
                .fillField("Group:", "TG2")
                .clickSearchButton()
                .shouldFindUsers(3)
                .shouldFindUser("testCrew");
    }

    @Test
    @DisplayName("should search user by not valid first name with error message")
    void should_search_users_by_not_valid_FirstName_with_ErrorMessage() {
        administrationPage.open().home()
                .clickUsersMenu()
                .fillField("First Name:", "xxx")
                .clickSearchButton()
                .clickButtonOk();
    }
}

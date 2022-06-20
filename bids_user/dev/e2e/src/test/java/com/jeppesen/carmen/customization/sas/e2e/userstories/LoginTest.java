package com.jeppesen.carmen.customization.sas.e2e.userstories;

import com.jeppesen.carmen.customization.sas.e2e.AbstractSelenideTest;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.PeriodRepository;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.CrewPortalProps;
import com.jeppesen.carmen.customization.sas.e2e.po.AdministrationPage;
import com.jeppesen.carmen.customization.sas.e2e.po.BiddingPage;
import lombok.AllArgsConstructor;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;

import static com.codeborne.selenide.Condition.exist;
import static com.codeborne.selenide.Condition.visible;
import static com.codeborne.selenide.Selectors.byText;
import static com.codeborne.selenide.Selectors.byValue;
import static com.codeborne.selenide.Selenide.*;
import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.CrewPortalProps.Login.Crew;
import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.PageObjects.existAndVisible;
import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.PageObjects.switchFrame;
import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.SeleniumGridAdapter.open;
import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.TestUtils.deletePeriodsAndFlushCache;

/**
 * NOTE: Page objects shouldn't be used in this test.
 * At least not for testing login functionality
 */
@Tags({
        @Tag("E2E"), @Tag("L")
})
@DisplayName("Login E2E tests")
@AllArgsConstructor(onConstructor_ = @Autowired)
class LoginTest extends AbstractSelenideTest {

    CrewPortalProps props;
    PeriodRepository periodRepository;
    AdministrationPage administrationPage;
    BiddingPage biddingPage;

    @BeforeEach
    void should_open_url() {
        open(props.getServer().getBaseUrl());
    }

    @Test
    @DisplayName("admin should login")
    void admin_should_login() {
        $("#c_username").setValue(props.getLogin().getAdmin().getUsername());
        $("#c_password").setValue(props.getLogin().getAdmin().getPassword());
        $(byValue("Sign In")).click();
        $(byText(props.getTabs().getAdministration())).shouldBe(existAndVisible);
    }

    @Test
    @DisplayName("admin should not login with wrong credentials")
    void admin_should_not_login_with_wrong_credentials() {
        $("#c_username").setValue("wrong admin login");
        $("#c_password").setValue(props.getLogin().getAdmin().getPassword());
        $(byValue("Sign In")).click();
        $(byText("Wrong username or password")).shouldBe(existAndVisible);

        refresh();
        $(byText("Wrong username or password"))
                .shouldNotBe(visible)
                .shouldNotBe(exist);
    }

    @Test
    @DisplayName("user should login")
    void user_should_login() {
        Crew crew = props.getLogin().getCrew();
        $("#c_username").setValue(crew.getUsername());
        $("#c_password").setValue(crew.getPassword());
        $(byValue("Sign In")).click();
        switchFrame("interbidsContentFrame");
        $(byText("No current or future bid period defined, please contact Administrator.")).shouldBe(existAndVisible);
    }

    @Test
    @DisplayName("user should not login with wrong credentials")
    void user_should_not_login_with_wrong_credentials() {
        $("#c_username").setValue("wrong user login");
        $("#c_password").setValue(props.getLogin().getCrew().getPassword());
        $(byValue("Sign In")).click();
        $(byText("Wrong username or password")).shouldBe(existAndVisible);

        refresh();
        $(byText("Wrong username or password"))
                .shouldNotBe(visible)
                .shouldNotBe(exist);
    }

    @AfterEach
    void afterEach() {
        close();
    }

    @AfterAll
    void tearDownAll() {
        deletePeriodsAndFlushCache(periodRepository, administrationPage);
    }
}

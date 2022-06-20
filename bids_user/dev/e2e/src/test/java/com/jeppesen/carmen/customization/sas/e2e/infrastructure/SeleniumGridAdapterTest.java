package com.jeppesen.carmen.customization.sas.e2e.infrastructure;

import com.jeppesen.carmen.customization.sas.e2e.AbstractSelenideTest;
import lombok.AllArgsConstructor;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.By;
import org.springframework.beans.factory.annotation.Autowired;

import static com.codeborne.selenide.Selenide.$;
import static com.codeborne.selenide.WebDriverRunner.closeWebDriver;
import static org.junit.jupiter.api.Assertions.assertTrue;

@Tag("PO")
@DisplayName("Connection adapter to Selenium grid")
@AllArgsConstructor(onConstructor_ = @Autowired)
class SeleniumGridAdapterTest extends AbstractSelenideTest {

    private final CrewPortalProps props;

    @AfterEach
    void tearDown() {
        closeWebDriver();
    }

    @Test
    void should_open_connection_by_url_only() {
        String validLoginUrl = props.getServer().getBaseUrl();
        SeleniumGridAdapter.open(validLoginUrl);
        String page = $(By.tagName("body")).innerHtml();
        assertTrue(page.contains("c_username"));
    }
}

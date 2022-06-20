package com.jeppesen.carmen.customization.sas.e2e;

import com.codeborne.selenide.Configuration;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.CrewPortalProps;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.SeleniumGridAdapter;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.TestInstance;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.springframework.boot.test.context.SpringBootTest.WebEnvironment.NONE;

@SpringBootTest(classes = E2eApplication.class, webEnvironment = NONE)
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public abstract class AbstractSelenideTest {

    @Autowired
    CrewPortalProps props;

    @BeforeAll
    void setup() {
        Configuration.timeout = Long.parseLong(System.getProperty("selenide.timeout", System
                .getenv().getOrDefault("SELENIDE_TIMEOUT", "30000")));
    }

    @AfterEach
    void afterEach() {
        SeleniumGridAdapter.close();
    }
}

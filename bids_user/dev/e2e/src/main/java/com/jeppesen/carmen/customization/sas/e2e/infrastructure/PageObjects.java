package com.jeppesen.carmen.customization.sas.e2e.infrastructure;

import com.codeborne.selenide.Condition;
import lombok.NoArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.openqa.selenium.WebDriver;

import static com.codeborne.selenide.Condition.*;
import static com.codeborne.selenide.Selenide.switchTo;
import static java.util.Arrays.asList;
import static lombok.AccessLevel.PRIVATE;

@Log4j2
@NoArgsConstructor(access = PRIVATE)
public class PageObjects {

    public static final Condition existAndVisible = and("exist and visible", exist, visible);

    public static WebDriver switchToDefault() {
        log.info("should open root");
        return switchTo().defaultContent();
    }

    public static WebDriver switchFrame(String frame) {
        log.info("should switch to {}", frame);
        return switchTo().frame(frame);
    }

    public static WebDriver switchInnerFrame(String... frames) {
        log.info("should switch to inner {}", asList(frames));
        return switchTo().innerFrame(frames);
    }
}

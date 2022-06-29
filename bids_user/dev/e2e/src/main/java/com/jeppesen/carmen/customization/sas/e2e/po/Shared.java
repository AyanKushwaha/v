package com.jeppesen.carmen.customization.sas.e2e.po;

import com.codeborne.selenide.SelenideElement;
import lombok.AccessLevel;
import lombok.NoArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.openqa.selenium.By;

import java.util.function.BiConsumer;
import java.util.function.Consumer;
import java.util.function.Supplier;

import static com.codeborne.selenide.CollectionCondition.size;
import static com.codeborne.selenide.CollectionCondition.sizeGreaterThanOrEqual;
import static com.codeborne.selenide.Condition.exactText;
import static com.codeborne.selenide.Selectors.*;
import static com.codeborne.selenide.Selenide.$;
import static com.codeborne.selenide.Selenide.$$;
import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.PageObjects.existAndVisible;
import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.PageObjects.switchFrame;

@Log4j2
@SuppressWarnings("java:S1192")
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public class Shared {

    private static final String ARROW_TRIGGER_SELECTOR = "x-form-arrow-trigger";

    public static final Consumer<String> shouldDisplayThisBidWindow =
            bidName -> $$(By.className("x-window-header-text")).filterBy(exactText(bidName))
                    .filterBy(existAndVisible)
                    .first()
                    .shouldBe(existAndVisible)
                    .click();

    public static final Consumer<String> selectValue = number ->
            $$(By.className("x-combo-list-item")).filterBy(exactText(number))
                    .filterBy(existAndVisible)
                    .first()
                    .shouldBe(existAndVisible)
                    .click();

    public static final BiConsumer<Integer, String> setFormTextValueByIndex = (index, value) ->
            $$(By.className("x-form-text")).get(index).setValue(value).click();

    public static final Consumer<String> selectOption = option ->
            $$(byText(option)).filterBy(existAndVisible).last().click();

    public static final BiConsumer<Integer, String> selectDayNumberFromCalendar = (integer, s) -> {
        $$(By.className("x-form-date-trigger")).get(integer).click();
        $$(By.className("x-date-date")).filterBy(exactText(s)).filterBy(existAndVisible).first().click();
    };

    public static final Supplier<SelenideElement> rootArea = () -> $(byId("BidWorkArea"));

    public static void bidWindow() {
        switchFrame("interbidsContentFrame");
    }

    public static void vacationWindow() {
        switchFrame("vacationContentFrame");
    }

    public static void careerWindow() {
        switchFrame("careerContentFrame");
    }

    public static void bidTab() {
        log.info("should find Bid tab by css: #MainView_tabs__MainView_bidsTabTab");
        $(byId("MainView_tabs__MainView_bidsTabTab")).shouldBe(existAndVisible).click();
    }

    public static void requestTab() {
        log.info("should find Bid tab by css: #MainView_tabs__MainView_requestsTabTab");
        $(byId("MainView_tabs__MainView_requestsTabTab")).shouldBe(existAndVisible).click();
    }

    public static void currentBid() {
        log.info("should find Current Bid element by css: #bidGroupTitleView_toolbar");
        $(byId("bidGroupTitleView_toolbar")).shouldBe(existAndVisible).click();
    }

    public static void currentRequest() {
        log.info("should find Current Bid element by css: #request_log_title_label");
        $(byId("request_log_title_label")).shouldBe(existAndVisible).click();
    }

    public static void currentLifestyle() {
        log.info("should find Current Lifestyle element by css: #bidgroup_title_label");
        $$(byId("bidgroup_title_label")).filterBy(exactText("Current Lifestyle"))
                .filterBy(existAndVisible)
                .first()
                .shouldBe(existAndVisible);
    }

    public static void clickCurrentWeek() {
        log.info("should find current date");
        $(byClassName("ux-calendar-week")).shouldBe(existAndVisible).click();
    }

    public static void clickBidsTab() {
        log.info("should find Lifestyle tab");
        $(byId("MainView_bidsTab_currentAccordionHeader")).shouldBe(existAndVisible).click();
    }

    public static void clickLifestyleTab() {
        log.info("should find Lifestyle tab");
        $(byId("MainView_bidsTab_preferenceAccordionHeader")).shouldBe(existAndVisible).click();
    }

    public static void clickPlaceBid() {
        log.info("should find Place Bid button");
        $$("button").filterBy(exactText("Place Bid"))
                .filterBy(existAndVisible)
                .first()
                .shouldBe(existAndVisible)
                .click();
    }

    public static void clickPlaceRequest() {
        log.info("should find Place Request button");
        $$("button").filterBy(exactText("Place Request"))
                .filterBy(existAndVisible)
                .first()
                .shouldBe(existAndVisible)
                .click();
    }

    public static void validateTimeOffBidNotDuplicated(String firstDate, String secondDate) {
        log.info("should validate Time Off Bid not duplicated");
        createTimeOffBid(firstDate, secondDate);
        $(withText("You are entitled to 1 PBS bid(s) for priority HIGH per calendar month. This bid will violate the limit.")).shouldBe(existAndVisible);
    }

    public static void validateStopBidNotDuplicated() {
        log.info("should validate Stop Bid not duplicated");
        createStopBid();
        $(withText("You are entitled to 1 PBS bid(s) for priority HIGH per calendar month. This bid will violate the limit.")).shouldBe(existAndVisible);
    }

    public static void validateFlightBidNotDuplicated() {
        log.info("should validate Flight Bid not duplicated");
        createFlightBid();
        $(withText("You are entitled to 1 PBS bid(s) for priority HIGH per calendar month. This bid will violate the limit.")).shouldBe(existAndVisible);
    }

    public static void createTimeOffBid(String firstDate, String secondDate) {
        log.info("should create Time Off Bid");
        selectOption.accept("Time Off");
        shouldDisplayThisBidWindow.accept("New Time Off Bid");
        setFormTextValueByIndex.accept(0, firstDate);
        setFormTextValueByIndex.accept(2, secondDate);
        $$(byClassName(ARROW_TRIGGER_SELECTOR)).first().click();
        selectValue.accept("High");
        selectOption.accept("OK");
    }

    public static void createCompensationDaysBid() {
        log.info("should create Compensation Days Bid");
        selectOption.accept("Compensation Days");
        shouldDisplayThisBidWindow.accept("New Compensation Days Bid");
        selectOption.accept("OK");
    }

    public static void createCheckInAfterDayOffBid(String firstDate, String secondDate) {
        log.info("should create Check in after day off Bid");
        selectOption.accept("Check in after day off");
        shouldDisplayThisBidWindow.accept("New Check in after day off");
        setFormTextValueByIndex.accept(1, firstDate);
        setFormTextValueByIndex.accept(2, secondDate);
        $$(byClassName(ARROW_TRIGGER_SELECTOR)).get(1).click();
        selectValue.accept("Medium");
        selectOption.accept("OK");
    }

    public static void createCheckOutBeforeDayOffBid(String firstDate, String secondDate) {
        log.info("should create Check out before day off Bid");
        selectOption.accept("Check out before day off");
        shouldDisplayThisBidWindow.accept("New Check out before day off");
        setFormTextValueByIndex.accept(1, firstDate);
        setFormTextValueByIndex.accept(2, secondDate);
        $$(byClassName(ARROW_TRIGGER_SELECTOR)).get(1).click();
        selectValue.accept("Medium");
        selectOption.accept("OK");
    }

    public static void createLastMinuteLOABid(String firstDate, String secondDate) {
        log.info("should create Last Minute LOA Bid");
        selectOption.accept("Last Minute LOA");
        shouldDisplayThisBidWindow.accept("New Last Minute LOA bid");
        setFormTextValueByIndex.accept(0, firstDate);
        setFormTextValueByIndex.accept(1, secondDate);
        selectOption.accept("OK");
    }

    public static void createFlightBid() {
        log.info("should create Flight Bid");
        selectOption.accept("Flight");
        shouldDisplayThisBidWindow.accept("New Flight Bid");
        $$(byClassName(ARROW_TRIGGER_SELECTOR)).first().click();
        selectValue.accept("SK0101 (DXB - DUB)");
        $$(byClassName(ARROW_TRIGGER_SELECTOR)).get(1).click();
        selectValue.accept("2020-04-16");
        $$(byClassName(ARROW_TRIGGER_SELECTOR)).get(2).click();
        selectValue.accept("High");
        selectOption.accept("OK");
    }

    public static void createStopBid() {
        log.info("should create Stop Bid");
        selectOption.accept("Stop");
        shouldDisplayThisBidWindow.accept("New Stop Bid");
        setFormTextValueByIndex.accept(0, "ABV");
        $$(byClassName(ARROW_TRIGGER_SELECTOR)).get(3).click();
        selectValue.accept("High");
        selectOption.accept("OK");
    }

    public static void createFSRequest(String date) {
        log.info("should create FS request");
        selectOption.accept("FS");
        shouldDisplayThisBidWindow.accept("New FS request");
        setFormTextValueByIndex.accept(0, date);
        $$(byClassName(ARROW_TRIGGER_SELECTOR)).first().click();
        selectValue.accept("1");
        selectOption.accept("OK");
        selectOption.accept("Yes");
    }

    public static void createVacationBid(String firstDayNumber, String secondDayNumber, String comment) {
        log.info("should create Vacation Bid");
        $(byClassName("VACATION")).shouldBe(existAndVisible).click();
        log.info("should check Vacation Bid window");
        shouldDisplayThisBidWindow.accept("New Vacation bid");
        selectDayNumberFromCalendar.accept(0, firstDayNumber);
        selectDayNumberFromCalendar.accept(1, secondDayNumber);
        $$(By.className("x-form-field")).get(6).setValue(comment);
        log.info("should click OK on Vacation Bid window");
        selectOption.accept("OK");
    }

    public static void createPostponeVacationBid(String days) {
        log.info("should create Postpone Vacation Bid");
        $(byClassName("POSTPONE")).shouldBe(existAndVisible).click();
        log.info("should check Postpone Vacation Bid window");
        shouldDisplayThisBidWindow.accept("New Postpone vacation bid");
        log.info("should enter first date on Postpone vacation bid window");
        setFormTextValueByIndex.accept(0, days);
        selectOption.accept("OK");
    }

    public static void createDaysForProductionBid(String firstDate, String secondDate) {
        log.info("should create Days for production Bid");
        selectOption.accept("Days for production");
        shouldDisplayThisBidWindow.accept("New days for production bid");
        setFormTextValueByIndex.accept(0, firstDate);
        setFormTextValueByIndex.accept(1, secondDate);
        selectOption.accept("OK");
    }

    public static void validateDaysForProductionBidNotDuplicated(String firstDate, String secondDate) {
        log.info("should validate Days For Production Bid not duplicated");
        createDaysForProductionBid(firstDate, secondDate);
        $(withText("The bid overlaps an existing bid.")).shouldBe(existAndVisible);
    }

    public static void createFdaPositionBid() {
        log.info("should create FDA Position Bid");
        $(By.className("FBID")).shouldBe(existAndVisible).click();
        shouldDisplayThisBidWindow.accept("New FDA Position");
        $$(byClassName(ARROW_TRIGGER_SELECTOR)).first().click();
        setFormTextValueByIndex.accept(0, "FO LH");
        selectOption.accept("OK");
    }

    public static void createLifestyle(String name) {
        log.info("should create Lifestyle by name");
        selectOption.accept(name);
        shouldDisplayThisBidWindow.accept("New Morning person Lifestyle");
        selectOption.accept("OK");
    }

    public static void validateLifestyleBidNotDuplicated(String name) {
        log.info("should validate Lifestyle Bid not duplicated");
        createLifestyle(name);
        $(withText("You may only choose one lifestyle bid per calendar month. If you wish to change your Lifestyle, please delete your current choice first.")).shouldBe(existAndVisible);
    }

    public static void verifyBidVisibilityOfNrExact(String bidName, int size) {
        log.info("should check Bid on Interbids tab");
        rootArea.get().$$(withText(bidName)).filterBy(existAndVisible).shouldBe(size(size));
    }

    public static void verifyBidVisibilityOfNrExactOnFDATab(String name, int size) {
        log.info("should check Bid on FDA tab");
        $(byId("bidListGrid_TRANSITION")).$$(withText(name)).filterBy(exactText(name)).shouldBe(size(size));
    }

    public static void verifyBidVisibilityOfNrExactOnVacationTab(String name, int size) {
        log.info("should check Bid on Vacation tab");
        $$(withText(name)).shouldBe(sizeGreaterThanOrEqual(size));
    }
}

package com.jeppesen.carmen.customization.sas.e2e.po;

import com.codeborne.selenide.Condition;
import com.codeborne.selenide.ElementsCollection;
import com.codeborne.selenide.SelenideElement;
import com.codeborne.selenide.WebDriverRunner;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.BidGroupsConfigurationException;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.CrewPortalProps;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.SeleniumGridAdapter;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.Strings;
import io.vavr.control.Try;
import lombok.Cleanup;
import lombok.RequiredArgsConstructor;
import lombok.SneakyThrows;
import lombok.extern.log4j.Log4j2;
import lombok.val;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.BasicCookieStore;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.impl.cookie.BasicClientCookie;
import org.apache.http.message.BasicNameValuePair;
import org.openqa.selenium.By;
import org.openqa.selenium.Cookie;
import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;

import javax.annotation.PreDestroy;
import java.util.Collections;
import java.util.function.BiFunction;
import java.util.function.Function;

import static com.codeborne.selenide.CollectionCondition.texts;
import static com.codeborne.selenide.Condition.*;
import static com.codeborne.selenide.Selectors.*;
import static com.codeborne.selenide.Selenide.$;
import static com.codeborne.selenide.Selenide.$$;
import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.PageObjects.*;
import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.Strings.trimmed;
import static java.lang.String.format;
import static java.nio.charset.StandardCharsets.UTF_8;
import static org.springframework.beans.factory.config.ConfigurableBeanFactory.SCOPE_PROTOTYPE;

@Log4j2
@Component
@Scope(SCOPE_PROTOTYPE)
@RequiredArgsConstructor
@SuppressWarnings("java:S1192")
public class AdministrationPage {

    private static final String IFRAME_BODY = "iframeBody";
    private static final String PORTAL_TAB_NAME = "Portal";
    private static final String ROW_IN_TABLE_SELECTOR = ".x-grid3-row";
    private static final String X_PATH_INPUT_IN_FORM_SELECTOR = "div > div > input";
    private static final String ITEM_IN_COMBO_LIST_SELECTOR = ".x-combo-list-item";
    private static final String ADMINISTRATION_FRAME = "administrationContentFrame";

    final CrewPortalProps props;

    public AdministrationPage login() {
        CrewPortalProps.Login.Admin admin = props.getLogin().getAdmin();
        log.info("should enter admin credentials: {}/{}", admin.getUsername(), admin.getPassword());
        $("#c_username").shouldBe(existAndVisible).setValue(admin.getUsername());
        $("#c_password").shouldBe(existAndVisible).setValue(admin.getPassword());
        log.info("should click Sign In");
        $(byValue("Sign In")).should(exist).click();
        return this;
    }

    public AdministrationPage open() {
        log.info("should open portal");
        SeleniumGridAdapter.open(props.getServer().getBaseUrl());
        return login().home();
    }

    public AdministrationPage home() {
        switchToDefault();
        log.info("should have {} tab visible", props.getTabs().getAdministration());
        $(byText(props.getTabs().getAdministration())).shouldBe(existAndVisible).click();
        return this;
    }

    public AdministrationPage interbidsTab() {
        checkProxyMode();
        openTab(props.getTabs().getInterbids());
        return this;
    }

    public AdministrationPage vacationTab() {
        openTab(props.getTabs().getVacation());
        return this;
    }

    public AdministrationPage fdaTab() {
        openTab(props.getTabs().getFda());
        return this;
    }

    private void openTab(String tabName) {
        log.info("should click {} tab", tabName);
        $(withText(tabName)).shouldBe(existAndVisible).click();
    }

    public AdministrationPage bidWindow() {
        Shared.bidWindow();
        return this;
    }

    public AdministrationPage vacationWindow() {
        Shared.vacationWindow();
        return this;
    }

    public AdministrationPage careerWindow() {
        Shared.careerWindow();
        return this;
    }

    public AdministrationPage bidTab() {
        Shared.bidTab();
        return this;
    }

    public AdministrationPage requestTab() {
        Shared.requestTab();
        return this;
    }

    public AdministrationPage currentBid() {
        Shared.currentBid();
        return this;
    }

    public AdministrationPage currentRequest() {
        Shared.currentRequest();
        return this;
    }

    public AdministrationPage currentLifestyle() {
        Shared.currentLifestyle();
        return this;
    }

    public AdministrationPage clickCurrentWeek() {
        Shared.clickCurrentWeek();
        return this;
    }

    public AdministrationPage clickBidsTab() {
        Shared.clickBidsTab();
        return this;
    }

    public AdministrationPage clickLifestyleTab() {
        Shared.clickLifestyleTab();
        return this;
    }

    public AdministrationPage clickPlaceBid() {
        Shared.clickPlaceBid();
        return this;
    }

    public AdministrationPage clickPlaceRequest() {
        Shared.clickPlaceRequest();
        return this;
    }

    public AdministrationPage clickBidReceipt() {
        clickButton("Bid Receipt");
        return this;
    }

    public AdministrationPage clickClose() {
        clickButton("Close");
        return this;
    }

    public AdministrationPage createTimeOffBid(String firstDate, String secondDate) {
        Shared.createTimeOffBid(firstDate, secondDate);
        return this;
    }

    public AdministrationPage createCompensationDaysBid() {
        Shared.createCompensationDaysBid();
        return this;
    }

    public AdministrationPage createCheckInAfterDayOffBid(String firstDate, String secondDate) {
        Shared.createCheckInAfterDayOffBid(firstDate, secondDate);
        return this;
    }

    public AdministrationPage createCheckOutBeforeDayOffBid(String firstDate, String secondDate) {
        Shared.createCheckOutBeforeDayOffBid(firstDate, secondDate);
        return this;
    }

    public AdministrationPage createLastMinuteLOABid(String firstDate, String secondDate) {
        Shared.createLastMinuteLOABid(firstDate, secondDate);
        return this;
    }

    public AdministrationPage createFlightBid() {
        Shared.createFlightBid();
        return this;
    }

    public AdministrationPage createStopBid() {
        Shared.createStopBid();
        return this;
    }

    public AdministrationPage createFSRequest(String date) {
        Shared.createFSRequest(date);
        return this;
    }

    public AdministrationPage createVacationBid(String firstDayNumber, String secondDayNumber, String comment) {
        Shared.createVacationBid(firstDayNumber, secondDayNumber, comment);
        return this;
    }

    public AdministrationPage createPostponeVacationBid(String days) {
        Shared.createPostponeVacationBid(days);
        return this;
    }

    public AdministrationPage createDaysForProductionBid(String firstDate, String secondDate) {
        Shared.createDaysForProductionBid(firstDate, secondDate);
        return this;
    }

    public AdministrationPage validateDaysForProductionBid(String firstDate, String secondDate) {
        Shared.validateDaysForProductionBidNotDuplicated(firstDate, secondDate);
        clickButtonOk();
        return this;
    }

    public AdministrationPage createLifestyle(String name) {
        Shared.createLifestyle(name);
        return this;
    }

    public AdministrationPage validateLifestyleNotDuplicated(String name) {
        Shared.validateLifestyleBidNotDuplicated(name);
        clickButtonOk();
        return this;
    }

    public AdministrationPage createFdaPositionBid() {
        Shared.createFdaPositionBid();
        return this;
    }

    public AdministrationPage validateTimeOffBidNotDuplicated(String firstDate, String secondDate) {
        Shared.validateTimeOffBidNotDuplicated(firstDate, secondDate);
        clickButtonOk();
        return this;
    }

    public AdministrationPage validateStopBidNotDuplicated() {
        Shared.validateStopBidNotDuplicated();
        clickButtonOk();
        return this;
    }

    public AdministrationPage validateFlightBidNotDuplicated() {
        Shared.validateFlightBidNotDuplicated();
        clickButtonOk();
        return this;
    }

    public AdministrationPage verifyBidVisibilityOfNrExact(String bidName, int size) {
        Shared.verifyBidVisibilityOfNrExact(bidName, size);
        return this;
    }

    public AdministrationPage verifyBidVisibilityOfNrExactOnFDATab(String bidName, int size) {
        Shared.verifyBidVisibilityOfNrExactOnFDATab(bidName, size);
        return this;
    }

    public AdministrationPage verifyBidVisibilityOfNrExactOnVacationTab(String bidName, int size) {
        Shared.verifyBidVisibilityOfNrExactOnVacationTab(bidName, size);
        return this;
    }

    public AdministrationPage verityTextPresentOnPage(String text) {
        $(byText(text)).shouldBe(existAndVisible);
        return this;
    }

    public AdministrationPage clickServersMenu() {
        switchFrame(ADMINISTRATION_FRAME);
        waitFor("Servers");
        switchInnerFrame(ADMINISTRATION_FRAME, IFRAME_BODY);
        return this;
    }

    public AdministrationPage clickUsersMenu() {
        switchFrame(ADMINISTRATION_FRAME);
        $(byText(PORTAL_TAB_NAME)).shouldBe(existAndVisible).click();
        waitFor("Users");
        switchInnerFrame(ADMINISTRATION_FRAME, IFRAME_BODY);
        return this;
    }

    public AdministrationPage flushCache() {
        log.info("should flush cache");
        $(byText("Tools")).shouldBe(existAndVisible).click();
        $(byText("Flush Cache")).shouldBe(existAndVisible).click();
        return this;
    }

    public AdministrationPage proxyUserById(String userId) {
        log.info("should proxy by userId: {}", userId);
        open().home()
                .clickUsersMenu()
                .fillField("User Id:", userId)
                .clickSearchButton()
                .shouldFindUser(userId)
                .clickButtonProxy();
        return this;
    }

    @SneakyThrows
    public AdministrationPage flushCacheRequest() {
        log.info("should flush cache by using REST API");

        String jBossNonDockerLocalhost = "127.0.0.1";
        String flushCacheEndpoint = format("http://%s:8080/sas/interbids/flushClusterCache.action",
                jBossNonDockerLocalhost);
        val params = Collections.singletonList(new BasicNameValuePair("flushTrips", "false"));
        HttpPost flushCacheRequest = new HttpPost(flushCacheEndpoint);
        flushCacheRequest.setEntity(new UrlEncodedFormEntity(params, UTF_8));

        Function<Cookie, BasicClientCookie> toBasicClientCookie = cookie -> {
            BasicClientCookie result = new BasicClientCookie(cookie.getName(), cookie.getValue());
            result.setDomain(jBossNonDockerLocalhost);
            result.setPath(cookie.getPath());
            return result;
        };
        BasicCookieStore cookieStore = new BasicCookieStore();
        cookieStore.addCookies(WebDriverRunner.getWebDriver().manage().getCookies().stream()
                .map(toBasicClientCookie)
                .toArray(BasicClientCookie[]::new));

        @Cleanup CloseableHttpClient client = HttpClientBuilder.create().setDefaultCookieStore(cookieStore).build();
        Try.run(() -> client.execute(flushCacheRequest))
                .getOrElseThrow(e -> new RuntimeException(format("flush cache failed: %s", e.getLocalizedMessage())));

        return this;
    }

    public AdministrationPage clickPeriodsMenu() {
        switchFrame(ADMINISTRATION_FRAME);
        waitFor("Periods");
        switchInnerFrame(ADMINISTRATION_FRAME, IFRAME_BODY);
        return this;
    }

    public AdministrationPage clickGroupsMenu() {
        switchFrame(ADMINISTRATION_FRAME);

        $(byText(PORTAL_TAB_NAME)).shouldBe(existAndVisible)
                .click();

        waitForGroupsElement();
        switchInnerFrame(ADMINISTRATION_FRAME, IFRAME_BODY);
        return this;
    }

    public AdministrationPage deleteAllPeriods() {

        log.info("should delete all periods");

        Condition bidGroups = props.getAdministrationPage().getGroups()
                .stream()
                .map(Condition::exactText)
                .reduce((c1, c2) -> or("Bid Groups exactText OR-conditions", c1, c2))
                .orElseThrow(() -> new RuntimeException(format("Cannot create condition Groups: %s",
                        props.getAdministrationPage().getGroups())));

        ElementsCollection elements = $$("div > table > tbody > tr > td > div");

        elements.filterBy(existAndVisible)
                .filterBy(bidGroups)
                .forEach(this::confirmDeletion);

        return this;
    }

    public AdministrationPage deleteGroup(String bidGroupName) {

        log.info("should delete Group: {}", bidGroupName);

        SelenideElement groupsArea = $("div.x-grid3-scroller").shouldBe(visible);
        ElementsCollection groupsRows = groupsArea.$$("table.x-grid3-row-table").filterBy(existAndVisible);

        SelenideElement groupElement = groupsRows.filter(exactText(bidGroupName))
                .filterBy(existAndVisible)
                .first();
        confirmGroupDeletion(groupElement);
        return this;
    }

    public AdministrationPage createStandardPeriod() {
        createStandardPeriod(props.getAdministrationPage().getGroups().stream().findFirst()
                .orElseThrow(BidGroupsConfigurationException::new));
        return this;
    }

    public AdministrationPage createStandardPeriod(String bidGroup) {
        createPeriod(bidGroup, "standard");
        return this;
    }

    public AdministrationPage createPeriod(String bidGroup, String typePeriod) {
        log.info("should create period for group: {}", bidGroup);

        String bidGroupTrimmed = trimmed(bidGroup, "bidGroup");

        $(byText("New")).shouldBe(existAndVisible).click();
        $(byText("Manage Period")).shouldBe(existAndVisible);
        $(byText("Period type:")).shouldBe(existAndVisible).parent()
                .find("div > div > input").shouldBe(existAndVisible)
                .click();

        $$(".x-combo-list-item").findBy(exactText(typePeriod))
                .click();

        findGroupDropDown().click();
        chooseComboListItem(bidGroupTrimmed);
        clickButtonOk();
        return this;
    }

    public AdministrationPage createGroup(String bidGroupName) {

        log.info("should create group: {}", bidGroupName);
        $(byText("New"))
                .shouldBe(existAndVisible)
                .click();

        findGroupTextBox().sendKeys(bidGroupName);
        clickButtonOk();
        $(byText(bidGroupName)).shouldBe(existAndVisible);
        return this;
    }

    public AdministrationPage verifyGroupIsNotDuplicated(String bidGroupName) {
        log.info("verify cannot create group: {}", bidGroupName);
        createGroup(bidGroupName);
        $(byText("Could not create group."))
                .shouldBe(existAndVisible);
        clickButtonOk();
        clickButtonCancel();
        return this;
    }

    private AdministrationPage clickButton(String name) {
        log.info("should find and click button: {}", name);
        $$("button")
                .filterBy(exactTextCaseSensitive(name))
                .filterBy(existAndVisible).last()
                .click();
        return this;
    }

    public AdministrationPage clickButtonProxy() {
        return clickButton("Proxy");
    }

    public AdministrationPage clickButtonOk() {
        return clickButton("OK");
    }

    public AdministrationPage clickButtonOkInLowerCase() {
        return clickButton("ok");
    }

    public AdministrationPage clickButtonCancel() {
        return clickButton("Cancel");
    }

    static final Function<String, ElementsCollection> xPanelBwraps =
            criteria -> $$(".x-panel-bwrap").filterBy(existAndVisible)
                    .filterBy(textCaseSensitive("New"))
                    .filterBy(textCaseSensitive("Edit"))
                    .filterBy(textCaseSensitive("Export"))
                    .filterBy(textCaseSensitive(criteria));

    static final BiFunction<SelenideElement, String, ElementsCollection> xGrid3Rows =
            (rootElement, criteria) -> rootElement.findAll("div.x-grid3-row")
                    .shouldHave(texts(criteria));

    public AdministrationPage editPeriod(String fromGroup, String toGroup) {

        log.info("should edit period from: {} to: {}", fromGroup, toGroup);

        String fromGroupTrimmed = trimmed(fromGroup, "fromGroup");
        String toGroupTrimmed = trimmed(toGroup, "toGroup");
        SelenideElement root = xPanelBwraps.apply(fromGroupTrimmed).first();
        ElementsCollection elements = xGrid3Rows.apply(root, fromGroupTrimmed);

        elements.forEach(element -> {
            element.shouldBe(existAndVisible).click();
            root.$(byText("Edit")).click();
            $(byText("Modify")).click();
            findGroupDropDown().click();
            chooseComboListItem(toGroupTrimmed);
            clickButtonOk();
        });

        return this;
    }

    public AdministrationPage deletePeriod(String bidGroup) {

        log.info("should delete period for: {}", bidGroup);

        String bidGroupTrimmed = trimmed(bidGroup, "fromGroup");
        SelenideElement root = xPanelBwraps.apply(bidGroupTrimmed).first();
        ElementsCollection elements = xGrid3Rows.apply(root, bidGroupTrimmed);

        elements.forEach(this::confirmDeletion);
        return this;
    }

    public void close() {
        SeleniumGridAdapter.close();
    }

    /* Private API */

    private void waitFor(String elementName) {
        log.info("should click {} menu", elementName);
        $(byText(elementName)).shouldBe(existAndVisible).click();
    }

    private void waitForGroupsElement() {
        log.info("should click Groups menu");
        $(byText("Groups")).shouldBe(existAndVisible).click();
    }

    private SelenideElement findGroupDropDown() {
        log.info("should find group drop-down");
        return $(byText("Group:"))
                .shouldBe(existAndVisible).parent()
                .find(X_PATH_INPUT_IN_FORM_SELECTOR)
                .shouldBe(existAndVisible);
    }

    public AdministrationPage fillField(String label, String inputValue) {
        log.info("should fill field with '{}' value", inputValue);
        $(byText(label)).parent()
                .find(By.className("x-form-field"))
                .shouldBe(existAndVisible)
                .setValue(inputValue)
                .pressEnter();
        return this;
    }

    private SelenideElement findGroupTextBox() {
        log.info("should find group textbox");
        return $(byText("Name:"))
                .shouldBe(existAndVisible).parent()
                .find(X_PATH_INPUT_IN_FORM_SELECTOR)
                .shouldBe(existAndVisible);
    }

    private void chooseComboListItem(String item) {
        log.info("should choose combo-list-item {}", item);
        $$(ITEM_IN_COMBO_LIST_SELECTOR).findBy(exactText(item))
                .click();
    }

    private SelenideElement findEditorOkButton() {
        log.info("should find button OK");
        return $$("table > tbody > tr > td > em > button").findBy(exactText("OK"));
    }

    public AdministrationPage clickSearchButton() {
        log.info("should click button Search");
        $$("button").filterBy(exactTextCaseSensitive("Search")).first()
                .shouldBe(existAndVisible).click();
        return this;
    }

    public AdministrationPage shouldFindUsers(int userCount) {
        log.info("should find {} users in User table", userCount);

        $$(ROW_IN_TABLE_SELECTOR)
                .shouldHaveSize(userCount)
                .filterBy(existAndVisible)
                .last().shouldBe(existAndVisible);

        return this;
    }

    public AdministrationPage shouldFindUser(String userId) {
        log.info("should find User {}", userId);

        SelenideElement userRow = findUserRow(userId);

        userRow.find(By.className("x-grid3-col-loginId"))
                .shouldBe(existAndVisible)
                .shouldNotBe(empty);

        userRow.find(By.className("x-grid3-col-3"))
                .shouldBe(existAndVisible)
                .shouldNotBe(empty);

        userRow.find(By.className("x-grid3-col-4"))
                .shouldBe(existAndVisible)
                .shouldNotBe(empty);

        return this;
    }

    private void checkProxyMode() {
        log.info("should find .header-proxy");
        $(byClassName("header-proxy")).shouldBe(visible);
    }

    private SelenideElement findUserRow(String userId) {
        log.info("should find a row for User {}", userId);

        SelenideElement userIdColumn = $$(By.className("x-grid3-col-userId"))
                .filter(textCaseSensitive(userId))
                .first()
                .shouldBe(existAndVisible)
                .shouldBe(exactTextCaseSensitive(userId));

        SelenideElement row = userIdColumn.parent()
                .parent()
                .shouldBe(existAndVisible);
        row.parent()
                .parent()
                .click();

        return row;
    }

    private void confirmDeletion(SelenideElement element) {
        element.shouldBe(existAndVisible).click();
        log.info("should delete period: {}", Strings.trimLine(element.text()));
        $(byText("Edit")).shouldBe(existAndVisible).click();
        $(byText("Delete")).shouldBe(existAndVisible).click();
        $(byText("Do you want to delete period?")).shouldBe(existAndVisible);
        $(byText("Yes")).shouldBe(existAndVisible).click();
        element.shouldNotBe(existAndVisible);
    }

    private void confirmGroupDeletion(SelenideElement element) {
        element.shouldBe(existAndVisible).click();
        log.info("should delete Group: {}", Strings.trimLine(element.text()));
        $(byText("Edit")).shouldBe(existAndVisible).click();
        $(byText("Delete")).shouldBe(existAndVisible).click();
        $(withText("Do you want to delete group")).shouldBe(existAndVisible);
        $(byText("Yes")).shouldBe(existAndVisible).click();
        element.shouldNotBe(existAndVisible);
    }

    /* Debug API */

    @PreDestroy
    public void preDestroy() {
        log.debug("should clean resources and close page object instance: {}", this);
        SeleniumGridAdapter.close();
    }
}

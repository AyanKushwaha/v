package com.jeppesen.carmen.customization.sas.e2e.po;

import com.codeborne.selenide.ElementsCollection;
import com.codeborne.selenide.SelenideElement;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.CrewPortalProps;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.SeleniumGridAdapter;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.Strings;
import lombok.RequiredArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;

import javax.annotation.PreDestroy;
import java.util.ListIterator;
import java.util.function.Supplier;

import static com.codeborne.selenide.Condition.exist;
import static com.codeborne.selenide.Condition.textCaseSensitive;
import static com.codeborne.selenide.Selectors.byText;
import static com.codeborne.selenide.Selectors.byValue;
import static com.codeborne.selenide.Selenide.$;
import static com.codeborne.selenide.Selenide.$$;
import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.PageObjects.existAndVisible;
import static com.jeppesen.carmen.customization.sas.e2e.infrastructure.PageObjects.switchToDefault;
import static org.springframework.beans.factory.config.ConfigurableBeanFactory.SCOPE_PROTOTYPE;

@Log4j2
@Component
@Scope(SCOPE_PROTOTYPE)
@RequiredArgsConstructor
@SuppressWarnings("java:S1192")
public class BiddingPage {

    final CrewPortalProps props;
    final AdministrationPage administrationPage;

    public BiddingPage open() {
        SeleniumGridAdapter.open(props.getServer().getBaseUrl());
        return login().home();
    }

    public BiddingPage home() {
        switchToDefault();
        log.info("should have Interbids tab visible in PBS home page");
        $(byText(props.getTabs().getInterbids())).shouldBe(existAndVisible).click();
        return this;
    }

    public BiddingPage reportSubTab() {
        log.info("Should switch to report sub-tab");
        $(byText("Report")).shouldBe(existAndVisible).click();
        return this;
    }

    public BiddingPage bidWindow() {
        Shared.bidWindow();
        return this;
    }

    public BiddingPage bidTab() {
        Shared.bidTab();
        return this;
    }

    public BiddingPage currentBid() {
        Shared.currentBid();
        return this;
    }

    public BiddingPage clickPlaceBid() {
        Shared.clickPlaceBid();
        return this;
    }

    public BiddingPage deleteAllBids() {
        log.info("should delete all bids... please take some patience, it's very long running operation");

        Supplier<SelenideElement> root = () -> $$(".x-panel-bwrap").filterBy(textCaseSensitive("Bid Details"))
                .filterBy(existAndVisible)
                .last()
                .shouldBe(existAndVisible); // should be is important!
        Supplier<ElementsCollection> children = () -> root.get().findAll("div.x-grid3-row");
        Supplier<ListIterator<SelenideElement>> elements = () -> children.get().listIterator(children.get().size());

        if (children.get().isEmpty()) return this;
        while (elements.get().hasPrevious())
            confirmDeletion(elements.get().previous());

        return this;
    }

    public BiddingPage validateFieldIsVisible(String field) {
        log.info("should be visible: {}", field);
        $(byText(field)).shouldBe(existAndVisible);
        return this;
    }

    public void close() {
        SeleniumGridAdapter.close();
    }

    private void confirmDeletion(SelenideElement element) {
        element.shouldBe(existAndVisible).click();
        log.info("should delete bid: {}", Strings.trimLine(element.text()));
        $(byText("Edit")).shouldBe(existAndVisible).click();
        $(byText("Delete")).shouldBe(existAndVisible).click();
        $(byText("Delete 1 bid(s)?")).shouldBe(existAndVisible);
        $(byText("Yes")).shouldBe(existAndVisible).click();
        element.shouldNotBe(existAndVisible);
    }

    public BiddingPage login() {
        CrewPortalProps.Login.Crew crew = props.getLogin().getCrew();
        log.info("should enter user credentials: {}/{}", crew.getUsername(), crew.getPassword());
        $("#c_username").shouldBe(existAndVisible).setValue(crew.getUsername());
        $("#c_password").shouldBe(existAndVisible).setValue(crew.getPassword());
        log.info("should click Sign In");
        $(byValue("Sign In")).shouldBe(exist).click();
        return this;
    }

    /* Debug API */

    @PreDestroy
    public void preDestroy() {
        log.debug("should clean resources and close page object instance: {}", this);
        SeleniumGridAdapter.close();
    }
}

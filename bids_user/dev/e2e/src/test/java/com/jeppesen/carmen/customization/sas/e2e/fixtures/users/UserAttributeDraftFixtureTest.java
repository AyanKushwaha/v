package com.jeppesen.carmen.customization.sas.e2e.fixtures.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.AbstractDbFixtureTest;
import lombok.RequiredArgsConstructor;
import lombok.val;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import static java.time.LocalDateTime.now;
import static java.time.temporal.ChronoUnit.MINUTES;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.junit.jupiter.api.Assertions.assertAll;

@DisplayName("Testing user attributes draft fixture")
@RequiredArgsConstructor(onConstructor_ = @Autowired)
class UserAttributeDraftFixtureTest extends AbstractDbFixtureTest {

    final UserAttributeDraftFixture userAttributeDraftFixture;

    @Test
    @DisplayName("should create drafted user attribute")
    void test() {
        val userAttribute = userAttributeDraftFixture.initDraft("Test");
        val startDate = now().truncatedTo(MINUTES);
        val endDate = startDate.plusMonths(1);

        assertAll("assert user attribute draft was properly created",
                () -> assertThat(startDate, equalTo(userAttribute.getStartDate())),
                () -> assertThat(endDate, equalTo(userAttribute.getEndDate()))
        );
    }
}

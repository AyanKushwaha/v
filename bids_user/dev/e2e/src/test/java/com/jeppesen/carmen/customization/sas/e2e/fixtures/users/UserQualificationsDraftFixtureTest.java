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

@DisplayName("Testing user qualification draft fixture")
@RequiredArgsConstructor(onConstructor_ = @Autowired)
class UserQualificationsDraftFixtureTest extends AbstractDbFixtureTest {

    final UserQualificationsDraftFixture userQualificationsDraftFixture;

    @Test
    @DisplayName("should create drafted user qualification")
    void test() {
        val userQualification = userQualificationsDraftFixture.initDraft();
        val startDate = now().truncatedTo(MINUTES);
        val endDate = startDate.plusYears(1);

        assertAll("assert user qualification draft was properly created",
                () -> assertThat(startDate, equalTo(userQualification.getStartDate())),
                () -> assertThat(endDate, equalTo(userQualification.getEndDate()))
        );
    }
}

package com.jeppesen.carmen.customization.sas.e2e.fixtures.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.AbstractDbFixtureTest;
import lombok.RequiredArgsConstructor;
import lombok.val;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import static java.time.LocalDateTime.now;
import static java.time.temporal.ChronoUnit.MINUTES;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertAll;

@DisplayName("Testing user messages DB fixture tests")
@RequiredArgsConstructor(onConstructor_ = @Autowired)
class UserMessageDraftFixtureTest extends AbstractDbFixtureTest {

    final UserMessageDraftFixture userMessageDraftFixture;

    @Test
    @DisplayName("should create drafted user message")
    void test() {
        val userMessage = userMessageDraftFixture.initDraft();
        val expected = now().truncatedTo(MINUTES);

        assertAll("assert user message draft was properly created",
                () -> assertThat(userMessage.getCreated()).isEqualTo(expected),
                () -> assertThat(userMessage.getUpdated()).isEqualTo(expected)
        );
    }
}

package com.jeppesen.carmen.customization.sas.e2e.fixtures.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.AbstractDbFixtureTest;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.users.UserMessageRepository;
import lombok.RequiredArgsConstructor;
import lombok.val;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import static java.time.LocalDateTime.now;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertAll;

@DisplayName("Testing user messages DB fixture tests")
@RequiredArgsConstructor(onConstructor_ = @Autowired)
class UserMessageDbFixtureTest extends AbstractDbFixtureTest {

    final UserMessageDBFixture userMessageDBFixture;
    final UserMessageRepository userMessageRepository;

    @Test
    @DisplayName("should create specific user message")
    void test() {

        val startTime = now().plusDays(1);
        val endTime = startTime.plusDays(1);
        val messageCreated = userMessageDBFixture.create(um -> um.setStartTime(startTime)
                .setEndTime(endTime)
                .setGroupId(1L)
                .setMessageText("Test message"));

        val messageInDB = userMessageRepository.findById(messageCreated.getMessageId())
                .orElseThrow(() -> new RuntimeException(
                        "message " + messageCreated.getMessageId() + " not found"));

        assertAll("assert message was properly created",
                () -> assertThat(messageInDB.getMessageText()).isEqualTo("Test message"),
                () -> assertThat(messageInDB.getGroupId()).isEqualTo(1L),
                () -> assertThat(messageInDB.getCreated()).isBefore(startTime),
                () -> assertThat(messageInDB.getUpdated()).isBefore(startTime),
                () -> assertThat(messageInDB.getStartTime()).isBefore(endTime),
                () -> assertThat(messageInDB.getEndTime()).isAfter(startTime)
        );
    }

    @AfterEach
    void cleanUpDb() {
        userMessageRepository.deleteAll();
        assertThat(userMessageRepository.findAll()).isEmpty();
    }
}

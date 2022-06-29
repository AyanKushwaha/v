package com.jeppesen.carmen.customization.sas.e2e.fixtures.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.AbstractDbFixtureTest;
import lombok.RequiredArgsConstructor;
import lombok.val;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import static java.time.LocalDateTime.now;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertAll;

@DisplayName("Testing user draft fixture")
@RequiredArgsConstructor(onConstructor_ = @Autowired)
class UsersDraftFixtureTest extends AbstractDbFixtureTest {

    final UserDraftFixture usersDraftFixture;

    @Test
    void test() {

        val user = usersDraftFixture.initDraft("1");

        assertAll("assert user draft was properly created",
                () -> assertThat(user.getUserId()).isEqualTo("userId1"),
                () -> assertThat(user.getLoginId()).isEqualTo("loginId1"),
                () -> assertThat(user.getFirstName()).isEqualTo("firstName1"),
                () -> assertThat(user.getLastName()).isEqualTo("lastName1"),
                () -> assertThat(user.getPassword()).isEqualTo("password1"),
                () -> assertThat(user.getMessagesLastRead()).isBeforeOrEqualTo(now()),
                () -> assertThat(user.getInactive()).isBeforeOrEqualTo(now())
        );
    }
}

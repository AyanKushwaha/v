package com.jeppesen.carmen.customization.sas.e2e.fixtures.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.User;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

import static java.lang.String.format;
import static java.time.LocalDateTime.now;

@Service
public class UserDraftFixture {

    public User initDraft(final String suffix) {
        final LocalDateTime now = now();
        return new User(format("userId%s", suffix)).setLoginId(format("loginId%s", suffix))
                .setPassword(format("password%s", suffix))
                .setFirstName(format("firstName%s", suffix))
                .setLastName(format("lastName%s", suffix))
                .setMessagesLastRead(now)
                .setInactive(now);
    }
}

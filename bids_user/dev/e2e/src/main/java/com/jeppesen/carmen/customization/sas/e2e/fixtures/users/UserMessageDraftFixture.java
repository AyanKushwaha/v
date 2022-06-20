package com.jeppesen.carmen.customization.sas.e2e.fixtures.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.UserMessage;
import lombok.val;
import org.springframework.stereotype.Service;

import static java.time.LocalDateTime.now;
import static java.time.temporal.ChronoUnit.MINUTES;

@Service
public class UserMessageDraftFixture {

    public UserMessage initDraft() {
        val now = now().truncatedTo(MINUTES);
        return new UserMessage().setCreated(now)
                .setUpdated(now);
    }
}

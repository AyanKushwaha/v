package com.jeppesen.carmen.customization.sas.e2e.fixtures.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.UserGroup;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
public class UserGroupDraftFixture {

    public UserGroup initDraft() {
        final LocalDateTime now = LocalDateTime.now();
        return new UserGroup().setStartDate(now.minusDays(2))
                .setEndDate(now.plusMonths(1));
    }
}

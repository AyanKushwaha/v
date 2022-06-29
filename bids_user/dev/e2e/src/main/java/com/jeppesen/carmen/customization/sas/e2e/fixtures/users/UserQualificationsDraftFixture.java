package com.jeppesen.carmen.customization.sas.e2e.fixtures.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.UserQualification;
import lombok.val;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

import static java.time.temporal.ChronoUnit.MINUTES;

@Service
public class UserQualificationsDraftFixture {

    public UserQualification initDraft() {
        val now = LocalDateTime.now().truncatedTo(MINUTES);
        return new UserQualification().setStartDate(now)
                .setEndDate(now.plusYears(1));
    }
}

package com.jeppesen.carmen.customization.sas.e2e.fixtures.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.UserAttribute;
import lombok.val;
import org.springframework.stereotype.Service;

import static java.time.LocalDateTime.now;
import static java.time.temporal.ChronoUnit.MINUTES;

@Service
public class UserAttributeDraftFixture {

    public UserAttribute initDraft(final String identifier) {
        val now = now().truncatedTo(MINUTES);
        return new UserAttribute().setAttributeName("attributeName" + identifier)
                .setAttributeValue("attributeValue" + identifier)
                .setStartDate(now)
                .setEndDate(now.plusMonths(1));
    }
}

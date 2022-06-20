package com.jeppesen.carmen.customization.sas.e2e.fixtures;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Group;
import org.springframework.stereotype.Service;

@Service
public class GroupsDraftFixture {

    public Group initDraft(final String identifier) {
        return new Group().setGroupName("groupName" + identifier)
                .setDescription("groupDescription" + identifier);
    }
}

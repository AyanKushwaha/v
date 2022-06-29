package com.jeppesen.carmen.customization.sas.e2e.fixtures;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Group;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertAll;

@DisplayName("Testing group draft fixture tests")
class GroupsDraftFixtureTest extends AbstractDbFixtureTest {

    @Autowired
    GroupsDraftFixture groupsDraftFixture;

    @Test
    void test() {
        String identifier = "1";
        final Group group = groupsDraftFixture.initDraft(identifier);
        assertAll("assert group draft was properly created",
                () -> assertThat(group.getGroupName()).isEqualTo("groupName" + identifier),
                () -> assertThat(group.getDescription()).isEqualTo("groupDescription" + identifier));
    }
}

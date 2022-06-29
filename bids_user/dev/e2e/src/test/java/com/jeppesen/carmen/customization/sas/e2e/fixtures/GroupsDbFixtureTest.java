package com.jeppesen.carmen.customization.sas.e2e.fixtures;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Group;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.GroupRepository;
import lombok.RequiredArgsConstructor;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertAll;

@DisplayName("Testing groups DB fixture tests")
@RequiredArgsConstructor(onConstructor_ = @Autowired)
class GroupsDbFixtureTest extends AbstractDbFixtureTest {

    final GroupRepository groupRepository;
    final GroupsDbFixture groupsDbFixture;

    @AfterEach
    void cleanUpDb() {
        groupRepository.deleteAll();
        assertThat(groupRepository.findAll()).isEmpty();
    }

    @Test
    @DisplayName("should create specific drafted group")
    void test() {

        final Group created = groupsDbFixture.create(g -> g.setGroupName("Test").setDescription("TestDesc"));

        final Group dbGroup = groupRepository.findById(created.getGroupId())
                .orElseThrow(() -> new RuntimeException("group " + created.getGroupId() + " not found"));

        assertAll("assert group was properly created",
                () -> assertThat(dbGroup.getGroupName()).isEqualTo("Test"),
                () -> assertThat(dbGroup.getDescription()).isEqualTo("TestDesc")
        );
    }
}

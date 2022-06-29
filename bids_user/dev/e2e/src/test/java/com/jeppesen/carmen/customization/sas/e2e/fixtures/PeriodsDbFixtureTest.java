package com.jeppesen.carmen.customization.sas.e2e.fixtures;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Group;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Period;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.GroupRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.PeriodRepository;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.BidGroupsConfigurationException;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.CrewPortalProps;
import lombok.RequiredArgsConstructor;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertAll;

@DisplayName("Testing periods DB fixture tests")
@RequiredArgsConstructor(onConstructor_ = @Autowired)
class PeriodsDbFixtureTest extends AbstractDbFixtureTest {

    final GroupRepository groupRepository;
    final CrewPortalProps crewPortalProps;
    final PeriodRepository periodRepository;
    final PeriodsDbFixture periodsDbFixture;

    @AfterEach
    void cleanUpDb() {
        periodRepository.deleteAll();
        assertThat(periodRepository.findAll()).isEmpty();

        groupRepository.deleteAll();
        assertThat(groupRepository.findAll()).isEmpty();
    }

    @Test
    @DisplayName("should create specific drafted period for default group")
    void createForDefaultGroup() {
        final Period created = periodsDbFixture.create(p -> p);

        final Period dbPeriod = periodRepository.findById(created.getPeriodId())
                .orElseThrow(() -> new RuntimeException("period " + created.getPeriodId() + " not found"));

        final String groupName = crewPortalProps.getAdministrationPage().getGroups().stream()
                .findFirst()
                .orElseThrow(BidGroupsConfigurationException::new);

        final Group dbGroup = groupRepository.findByGroupName(groupName).orElse(new Group());

        assertAll("assert period and group was properly created",
                () -> assertThat(dbGroup.getGroupName()).isEqualTo(groupName),
                () -> assertThat(dbGroup.getGroupId()).isEqualTo(dbPeriod.getGroupId())
        );
    }

    @Test
    @DisplayName("should create specific drafted period for existing group")
    void createForExistingGroup() {
        final String groupName = "Test";
        final Period created = periodsDbFixture.createForGroup(groupName);

        final Period dbPeriod = periodRepository.findById(created.getPeriodId())
                .orElseThrow(() -> new RuntimeException("period " + created.getPeriodId() + " not found"));

        final Group dbGroup = groupRepository.findByGroupName(groupName)
                .orElseThrow(() -> new RuntimeException("group with name " + groupName + " not found"));

        assertAll("assert period and group was properly created",
                () -> assertThat(dbGroup.getGroupName()).isEqualTo(groupName),
                () -> assertThat(dbGroup.getGroupId()).isEqualTo(dbPeriod.getGroupId())
        );
    }
}

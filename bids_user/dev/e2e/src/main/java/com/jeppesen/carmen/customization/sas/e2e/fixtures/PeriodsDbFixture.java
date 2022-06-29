package com.jeppesen.carmen.customization.sas.e2e.fixtures;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.api.Fixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Group;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Period;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.PeriodRepository;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.BidGroupsConfigurationException;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.CrewPortalProps;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import static java.util.Objects.isNull;

@Service
@RequiredArgsConstructor
public class PeriodsDbFixture implements Fixture<Period> {

    final CrewPortalProps props;
    final GroupsDbFixture groupsDbFixture;
    final PeriodRepository periodRepository;
    final PeriodsDraftFixture periodsDraftFixture;

    @Override
    @Transactional
    public Period create(Period obj) {

        if (isNull(obj.getGroupId())) {
            Group group = groupsDbFixture.create(g -> g.setGroupName(props.getAdministrationPage().getGroups().stream().findFirst()
                    .orElseThrow(BidGroupsConfigurationException::new)));
            obj.setGroupId(group.getGroupId());
        }

        return periodRepository.save(obj);
    }

    @Transactional
    public Period createForGroup(String groupName) {
        Group group = groupsDbFixture.create(g -> g.setGroupName(groupName));
        return create(p -> p.setGroupId(group.getGroupId()));
    }

    @Transactional
    public Period createPeriodByTypeForGroup(String groupName, String periodType) {
        Group group = groupsDbFixture.create(g -> g.setGroupName(groupName));
        return create(p -> {
            p.setGroupId(group.getGroupId());
            p.setType(periodType);
            return p;
        });
    }

    @Override
    public Period initDraft() {
        return periodsDraftFixture.initDraft();
    }
}

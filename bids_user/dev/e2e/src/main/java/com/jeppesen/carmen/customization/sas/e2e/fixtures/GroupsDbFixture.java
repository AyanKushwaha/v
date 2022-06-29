package com.jeppesen.carmen.customization.sas.e2e.fixtures;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.api.Fixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Group;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.GroupRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class GroupsDbFixture implements Fixture<Group> {

    final GroupRepository groupRepository;
    final GroupsDraftFixture groupsDraftFixture;

    @Override
    @Transactional
    public Group create(Group obj) {
        return groupRepository.findByGroupName(obj.getGroupName())
                .orElseGet(() -> groupRepository.save(obj));
    }

    @Override
    public Group initDraft() {
        final String identifier = generateString(5);
        return groupsDraftFixture.initDraft(identifier);
    }
}

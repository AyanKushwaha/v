package com.jeppesen.carmen.customization.sas.e2e.fixtures.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.api.Fixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.UserGroup;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.users.UserGroupRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor(onConstructor_ = @Autowired)
public class UserGroupDbFixture implements Fixture<UserGroup> {

    final UserGroupRepository userGroupRepository;
    final UserGroupDraftFixture userGroupsDraftFixture;

    @Override
    @Transactional
    public UserGroup create(final UserGroup obj) {
        return userGroupRepository.findByUserAndGroup(obj.getUser(), obj.getGroup())
                .orElseGet(() -> userGroupRepository.save(obj));
    }

    @Override
    public UserGroup initDraft() {
        return userGroupsDraftFixture.initDraft();
    }
}

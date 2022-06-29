package com.jeppesen.carmen.customization.sas.e2e.fixtures.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.api.Fixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Qualification;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.User;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.UserQualification;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.users.UserQualificationRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class UserQualificationsDbFixture implements Fixture<UserQualification> {

    final UserQualificationRepository userQualificationRepository;
    final UserQualificationsDraftFixture userQualificationsDraftFixture;

    @Override
    @Transactional
    public UserQualification create(UserQualification obj) {
        return userQualificationRepository.saveAndFlush(obj);
    }

    @Transactional
    public UserQualification addQualificationToUser(User user, Qualification qualification) {
        return create(ug -> ug.setUser(user).setQualification(qualification));
    }

    @Override
    public UserQualification initDraft() {
        return userQualificationsDraftFixture.initDraft();
    }
}

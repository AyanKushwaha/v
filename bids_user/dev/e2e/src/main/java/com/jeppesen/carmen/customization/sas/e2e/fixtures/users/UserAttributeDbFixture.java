package com.jeppesen.carmen.customization.sas.e2e.fixtures.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.api.Fixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.UserAttribute;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.users.UserAttributeRepository;
import lombok.RequiredArgsConstructor;
import lombok.val;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor(onConstructor_ = @Autowired)
public class UserAttributeDbFixture implements Fixture<UserAttribute> {

    final UserAttributeRepository userAttributeRepository;
    final UserAttributeDraftFixture userAttributesDraftFixture;

    @Override
    @Transactional
    public UserAttribute create(final UserAttribute obj) {
        return userAttributeRepository
                .findByUserAndAttributeName(obj.getUser(), obj.getAttributeName())
                .map(a -> userAttributeRepository.saveAndFlush(obj.setUserAttributeId(a.getUserAttributeId()))).orElseGet(() -> userAttributeRepository.save(obj));
    }

    @Override
    public UserAttribute initDraft() {
        val identifier = generateString(5);
        return userAttributesDraftFixture.initDraft(identifier);
    }
}

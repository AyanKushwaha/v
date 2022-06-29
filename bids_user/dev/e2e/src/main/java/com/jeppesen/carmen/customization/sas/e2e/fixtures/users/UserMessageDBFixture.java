package com.jeppesen.carmen.customization.sas.e2e.fixtures.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.GroupsDbFixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.api.Fixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Group;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.UserMessage;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.users.UserMessageRepository;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.BidGroupsConfigurationException;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.CrewPortalProps;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import javax.transaction.Transactional;

import static java.util.Objects.isNull;

@Service
@RequiredArgsConstructor(onConstructor_ = @Autowired)
public class UserMessageDBFixture implements Fixture<UserMessage> {

    final CrewPortalProps props;
    final UserMessageRepository userMessageRepository;
    final UserMessageDraftFixture userMessageDraftFixture;
    final GroupsDbFixture groupsDbFixture;

    @Override
    @Transactional
    public UserMessage create(UserMessage obj) {
        if (isNull(obj.getGroupId())) {
            Group group = groupsDbFixture.create(g -> g.setGroupName(props.getAdministrationPage().getGroups().stream().findFirst()
                    .orElseThrow(BidGroupsConfigurationException::new)));
            obj.setGroupId(group.getGroupId());
        }
        return userMessageRepository.save(obj);
    }

    @Transactional
    public UserMessage createForGroup(String groupName) {
        Group group = groupsDbFixture.create(g -> g.setGroupName(groupName));
        return create(p -> p.setGroupId(group.getGroupId()));
    }

    @Override
    public UserMessage initDraft() {
        return userMessageDraftFixture.initDraft();
    }
}

package com.jeppesen.carmen.customization.sas.e2e.fixtures.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.AbstractDbFixtureTest;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Qualification;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.User;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.UserGroup;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.UserMessage;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.GroupRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.users.*;
import io.vavr.collection.HashMap;
import lombok.RequiredArgsConstructor;
import lombok.val;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import static com.jeppesen.carmen.customization.sas.e2e.fixtures.users.UserDbFixture.Param.*;
import static java.time.LocalDateTime.now;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertAll;

@DisplayName("Testing users DB fixture")
@RequiredArgsConstructor(onConstructor_ = @Autowired)
class UsersDbFixtureTest extends AbstractDbFixtureTest {

    final UserDbFixture usersDbFixture;
    final UserRepository userRepository;
    final GroupRepository groupRepository;
    final UserGroupRepository userGroupRepository;
    final UserAttributeRepository userAttributeRepository;
    final UserQualificationRepository userQualificationRepository;
    final UserMessageRepository userMessageRepository;

    @Test
    @DisplayName("should create specific drafted user")
    void create() {

        val created = usersDbFixture.create(u -> u.setLoginId("test")
                .setFirstName("Test")
                .setLastName("Test")
                .setPassword("test")
                .setMessagesLastRead(now()));

        userAttributeRepository.findAllAttributesByUser(created)
                .forEach(ua -> assertThat(created.getUserId()).isEqualTo(ua.getUser().getUserId()));

        val dbUser = userRepository.findById(created.getUserId())
                .orElseThrow(() -> new RuntimeException("user " + created.getUserId() + " not found"));

        assertAll("assert user and it's attributes.",
                () -> assertThat(dbUser.getLoginId()).isEqualTo("test"),
                () -> assertThat(dbUser.getLoginId().length()).isLessThanOrEqualTo(32),
                () -> assertThat(dbUser.getFirstName()).isEqualTo(created.getFirstName()),
                () -> assertThat(dbUser.getLastName()).isEqualTo(created.getLastName()),
                () -> assertThat(dbUser.getMessagesLastRead()).isEqualTo(created.getMessagesLastRead())
        );
    }

    @Test
    @DisplayName("should create specific user with params")
    void createWithParams() {

        // given:
        AttributesParam attributes = () -> HashMap.of("attr1", "value1",
                        "attr2", "value2")
                .toJavaMap();
        // and:
        QualificationParam qualification = () -> "cp1";
        // and:
        GroupParam group = () -> "test_group";
        // and:
        MessageParam message = () -> "test_message";

        val created = usersDbFixture.createWithParams(() -> new User("777").setLoginId("Id")
                        .setFirstName("testFirstName")
                        .setLastName("testLastName")
                        .setPassword("password")
                        .setMessagesLastRead(now()),
                qualification,
                group,
                message,
                attributes);
        // when:
        val dbUser = userRepository.findById(created.getUserId())
                .orElseThrow(() -> new RuntimeException("user " + created.getUserId() + " not found"));
        // and:
        userAttributeRepository.findAllAttributesByUser(created)
                .forEach(ua -> assertThat(created.getUserId()).isEqualTo(ua.getUser().getUserId()));
        // and:
        groupRepository.findByGroupName("test_group")
                .orElseThrow(() -> new RuntimeException("test_group not found"));
        // and:
        Qualification userQualification = userQualificationRepository.findAllQualificationsByUser(created)
                .get(0)
                .getQualification();
        // and:
        UserGroup userGroup = userGroupRepository.findByUser(created)
                .orElseThrow(() -> new RuntimeException("group test_group not found"));
        // and:
        UserMessage userMessage = userMessageRepository.findByMessageText("test_message")
                .orElseThrow(() -> new RuntimeException("message not found"));
        // and:
        val firstUserAttribute = userAttributeRepository.findAllAttributesByUser(created)
                .stream()
                .filter(a -> a.getAttributeName().equals("attr1"))
                .findAny()
                .orElseThrow(() -> new RuntimeException("attribute attr1 not found"));
        // and:
        val secondUserAttribute = userAttributeRepository.findAllAttributesByUser(created)
                .stream()
                .filter(a -> a.getAttributeName().equals("attr2"))
                .findAny()
                .orElseThrow(() -> new RuntimeException("attribute attr2 not found"));

        // then:
        assertAll("assert user and it's attributes, qualification and group.",
                () -> assertThat(dbUser.getLoginId()).isEqualTo("Id"),
                () -> assertThat(dbUser.getFirstName()).isEqualTo(created.getFirstName()),
                () -> assertThat(dbUser.getLastName()).isEqualTo(created.getLastName()),
                () -> assertThat(dbUser.getMessagesLastRead()).isEqualTo(created.getMessagesLastRead()),
                () -> assertThat(userQualification.getQualName()).isEqualTo("cp1"),
                () -> assertThat(userGroup.getGroup().getGroupName()).isEqualTo("test_group"),
                () -> assertThat(firstUserAttribute.getAttributeName()).isEqualTo("attr1"),
                () -> assertThat(secondUserAttribute.getAttributeName()).isEqualTo("attr2"),
                () -> assertThat(userMessage.getMessageText()).isEqualTo("test_message")
        );
    }

    @AfterEach
    void cleanUpDb() {
        userAttributeRepository.deleteAll();
        userQualificationRepository.deleteAll();
        userGroupRepository.deleteAll();
        userRepository.deleteAll();
        groupRepository.deleteAll();
    }
}

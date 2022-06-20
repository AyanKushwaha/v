package com.jeppesen.carmen.customization.sas.e2e.fixtures.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.GroupsDbFixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.QualificationDbFixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.api.Fixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.User;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.users.UserRepository;
import io.vavr.API;
import lombok.RequiredArgsConstructor;
import lombok.extern.log4j.Log4j2;
import lombok.val;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Map;
import java.util.Objects;
import java.util.function.BiFunction;
import java.util.function.Supplier;

import static com.jeppesen.carmen.customization.sas.e2e.fixtures.users.UserDbFixture.Param.*;
import static io.vavr.API.$;
import static io.vavr.API.Case;
import static io.vavr.Predicates.instanceOf;

@Log4j2
@Service
@RequiredArgsConstructor(onConstructor_ = @Autowired)
public class UserDbFixture implements Fixture<User>, BiFunction<User, UserDbFixture.Param[], User> {

    final UserRepository userRepository;
    final GroupsDbFixture groupsDbFixture;
    final UserDraftFixture usersDraftFixture;
    final UserGroupDbFixture userGroupDbFixture;
    final UserMessageDBFixture userMessageDBFixture;
    final QualificationDbFixture qualificationDbFixture;
    final UserAttributeDbFixture userAttributesDbFixture;
    final UserQualificationsDbFixture userQualificationsDbFixture;

    @Override
    public User initDraft() {
        val identifier = generateString(5);
        return usersDraftFixture.initDraft(identifier);
    }

    @Override
    @Transactional
    public User create(final User userObj) {
        return userRepository.save(userObj);
    }

    @Transactional
    public User createWithParams(final Supplier<User> holder, Param... params) {
        Objects.requireNonNull(holder, "holder may not be null.");
        Objects.requireNonNull(params, "params may not be null.");
        return apply(userRepository.save(holder.get()), params);
    }

    public interface Param<T> extends Supplier<T> {
        interface GroupParam extends Param<String> {
        }

        interface MessageParam extends Param<String> {
        }

        interface QualificationParam extends Param<String> {
        }

        interface AttributesParam extends Param<Map<String, String>> {
        }
    }

    @Override
    @Transactional
    public User apply(User user, Param... params) {
        Objects.requireNonNull(user, "user may not be null.");
        Objects.requireNonNull(params, "params may not be null.");
        Arrays.stream(params).forEach(param -> API.Match(param).of(
                Case($(instanceOf(GroupParam.class)), p -> handleGroup(user, p)),
                Case($(instanceOf(AttributesParam.class)), p -> handleAttributes(user, p)),
                Case($(instanceOf(QualificationParam.class)), p -> handleQualification(user, p)),
                Case($(instanceOf(MessageParam.class)), p -> handleMessage(user, p)),
                Case($(), p -> handleUnexpected(user, p))
        ));
        return user;
    }

    private <T> User handleUnexpected(User user, T other) {
        Objects.requireNonNull(other, "other param may not be null.");
        log.warn("No suitable parameter: {} of type: {}! please use valid Param sub-type.", other, other.getClass());
        return user;
    }

    private User handleMessage(User user, MessageParam message) {
        Objects.requireNonNull(message, "message param may not be null.");
        userMessageDBFixture.create(um -> um.setMessageText(message.get())
                .setStartTime(LocalDateTime.now())
                .setEndTime(LocalDateTime.now().plusDays(1)));
        return user;
    }

    private User handleQualification(User user, QualificationParam qualification) {
        Objects.requireNonNull(qualification, "qualification param may not be null.");
        val created = qualificationDbFixture.create(q -> q.setQualName(qualification.get()));
        userQualificationsDbFixture.addQualificationToUser(user, created);
        return user;
    }

    private User handleAttributes(User user, AttributesParam attributes) {
        Objects.requireNonNull(attributes, "attributes param may not be null.")
                .get()
                .forEach((n, v) -> userAttributesDbFixture.create(ua -> ua.setUser(user)
                        .setAttributeName(n)
                        .setAttributeValue(v)));
        return user;
    }

    private User handleGroup(User user, GroupParam group) {
        return userGroupDbFixture.create(ug -> ug.setUser(user)
                        .setGroup(groupsDbFixture.create(g -> g.setGroupName(group.get()))))
                .getUser();
    }
}

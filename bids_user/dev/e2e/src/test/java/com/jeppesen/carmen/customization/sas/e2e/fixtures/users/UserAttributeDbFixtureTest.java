package com.jeppesen.carmen.customization.sas.e2e.fixtures.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.AbstractDbFixtureTest;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.users.UserAttributeRepository;
import lombok.RequiredArgsConstructor;
import lombok.val;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.junit.jupiter.api.Assertions.assertAll;

@DisplayName("Testing user attributes DB fixture tests")
@RequiredArgsConstructor(onConstructor_ = @Autowired)
class UserAttributeDbFixtureTest extends AbstractDbFixtureTest {

    final UserDbFixture userDbFixture;
    final UserAttributeDbFixture userAttributeDbFixture;
    final UserAttributeRepository userAttributeRepository;

    @Test
    @DisplayName("should add Attribute to User")
    void test() {

        val user = userDbFixture.create(u -> u);
        val attribute = userAttributeDbFixture.create(ua -> ua.setAttributeName("AttributeName")
                .setAttributeValue("AttributeValue")
                .setUser(user));
        val userAttributes = userAttributeRepository.findAllAttributesByUser(user);

        assertAll("assert user attribute created",
                () -> assertThat(userAttributes.size(), equalTo(1)),
                () -> assertThat(attribute.getAttributeName(), equalTo(userAttributes.get(0).getAttributeName())),
                () -> assertThat(attribute.getAttributeValue(), equalTo(userAttributes.get(0).getAttributeValue()))
        );
    }
}

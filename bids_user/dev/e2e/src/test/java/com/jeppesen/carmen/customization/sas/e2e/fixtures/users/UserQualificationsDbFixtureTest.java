package com.jeppesen.carmen.customization.sas.e2e.fixtures.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.AbstractDbFixtureTest;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.QualificationDbFixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.QualificationRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.users.UserQualificationRepository;
import lombok.RequiredArgsConstructor;
import lombok.val;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.junit.jupiter.api.Assertions.assertAll;

@ExtendWith(SpringExtension.class)
@DisplayName("Testing User Qualifications DB fixture")
@RequiredArgsConstructor(onConstructor_ = @Autowired)
class UserQualificationsDbFixtureTest extends AbstractDbFixtureTest {

    final UserDbFixture userDbFixture;
    final QualificationDbFixture qualificationsDbFixture;
    final QualificationRepository qualificationRepository;
    final UserQualificationsDbFixture userQualificationsDbFixture;
    final UserQualificationRepository userQualificationRepository;

    @Test
    @DisplayName("should add Qualification to User")
    void test() {

        val user = userDbFixture.create(u -> u);
        val qualification = qualificationsDbFixture.create(q -> q.setQualName("TestQualification"));
        userQualificationsDbFixture.addQualificationToUser(user, qualification);
        val userQualifications = userQualificationRepository.findAllQualificationsByUser(user);

        assertAll("assert user qualification created",
                () -> assertThat(userQualifications.size(), equalTo(1)),
                () -> assertThat(qualification.getQualName(), equalTo(userQualifications.get(0).getQualification().getQualName())),
                () -> assertThat(qualification.getDescription(), equalTo(userQualifications.get(0).getQualification().getDescription()))
        );
    }

    @AfterEach
    void cleanUpDb() {
        userQualificationRepository.deleteAll();
        qualificationRepository.deleteAll();
    }
}

package com.jeppesen.carmen.customization.sas.e2e.fixtures;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.QualificationRepository;
import lombok.RequiredArgsConstructor;
import lombok.val;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertAll;

@DisplayName("Testing qualification DB fixture test")
@RequiredArgsConstructor(onConstructor_ = @Autowired)
class QualificationsDbFixtureTest extends AbstractDbFixtureTest {

    final QualificationDbFixture qualificationDbFixture;
    final QualificationRepository qualificationRepository;

    @AfterEach
    void cleanUpDb() {
        qualificationRepository.deleteAll();
        assertThat(qualificationRepository.findAll()).isEmpty();
    }

    @Test
    @DisplayName("should create specific drafted qualification")
    void test() {

        val created = qualificationDbFixture.create(q -> q.setQualName("Test").setDescription("TestDesc"));

        val dbQualification = qualificationRepository.findById(created.getQualId())
                .orElseThrow(() -> new RuntimeException("qualification " + created.getQualName() + " not found"));
        assertAll("assert qualification was properly created",
                () -> assertThat(dbQualification.getQualName()).isEqualTo("Test"),
                () -> assertThat(dbQualification.getDescription()).isEqualTo("TestDesc")
        );
    }
}

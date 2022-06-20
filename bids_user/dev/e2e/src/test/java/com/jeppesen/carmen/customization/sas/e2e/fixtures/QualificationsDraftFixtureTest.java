package com.jeppesen.carmen.customization.sas.e2e.fixtures;

import lombok.RequiredArgsConstructor;
import lombok.val;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.junit.jupiter.api.Assertions.assertAll;

@DisplayName("Testing qualification draft fixture")
@RequiredArgsConstructor(onConstructor_ = @Autowired)
class QualificationsDraftFixtureTest extends AbstractDbFixtureTest {

    final QualificationsDraftFixture qualificationsDraftFixture;

    @Test
    void test() {
        val qualification = qualificationsDraftFixture.initDraft("1");
        assertAll("assert qualification draft was properly created",
                () -> assertThat("qualificationName1", equalTo(qualification.getQualName())),
                () -> assertThat("description1", equalTo(qualification.getDescription()))
        );
    }
}

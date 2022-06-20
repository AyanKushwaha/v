package com.jeppesen.carmen.customization.sas.e2e.fixtures;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Period;
import lombok.RequiredArgsConstructor;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import static org.assertj.core.api.Assertions.assertThat;

@DisplayName("Testing period draft fixture tests")
@RequiredArgsConstructor(onConstructor_ = @Autowired)
class PeriodsDraftFixtureTest extends AbstractDbFixtureTest {

    final PeriodsDraftFixture periodDraftFixture;

    @Test
    void test() {
        final Period period = periodDraftFixture.initDraft();
        assertThat(period.getType()).isEqualTo("standard");
    }
}

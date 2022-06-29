package com.jeppesen.carmen.customization.sas.e2e.fixtures;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.api.Fixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Qualification;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.QualificationRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class QualificationDbFixture implements Fixture<Qualification> {

    final QualificationRepository qualificationRepository;
    final QualificationsDraftFixture qualificationsDraftFixture;

    @Override
    @Transactional
    public Qualification create(Qualification obj) {
        return qualificationRepository.findByQualName(obj.getQualName())
                .orElseGet(() -> qualificationRepository.save(obj));
    }

    @Override
    public Qualification initDraft() {
        final String identifier = generateString(5);
        return qualificationsDraftFixture.initDraft(identifier);
    }
}

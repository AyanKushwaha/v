package com.jeppesen.carmen.customization.sas.e2e.fixtures;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Qualification;
import org.springframework.stereotype.Service;

@Service
public class QualificationsDraftFixture {

    public Qualification initDraft(final String identifier) {
        return new Qualification().setQualName("qualificationName" + identifier)
                .setDescription("description" + identifier);
    }
}

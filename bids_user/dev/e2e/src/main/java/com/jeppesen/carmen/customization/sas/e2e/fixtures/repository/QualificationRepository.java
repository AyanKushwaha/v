package com.jeppesen.carmen.customization.sas.e2e.fixtures.repository;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Qualification;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface QualificationRepository extends JpaRepository<Qualification, Long> {
    Optional<Qualification> findByQualName(String qualName);
}

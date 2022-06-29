package com.jeppesen.carmen.customization.sas.e2e.fixtures.repository;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Period;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PeriodRepository extends JpaRepository<Period, Long> {
}

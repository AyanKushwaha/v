package com.jeppesen.carmen.customization.sas.e2e.fixtures.repository;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Group;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface GroupRepository extends JpaRepository<Group, Long> {

    Optional<Group> findByGroupName(String groupName);
}

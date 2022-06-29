package com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.User;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.UserQualification;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface UserQualificationRepository extends JpaRepository<UserQualification, Long> {
    List<UserQualification> findAllQualificationsByUser(User user);
}

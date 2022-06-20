package com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Group;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.User;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.UserGroup;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface UserGroupRepository extends JpaRepository<UserGroup, String> {
    Optional<UserGroup> findByUserAndGroup(User user, Group group);

    Optional<UserGroup> findByUser(User user);
}

package com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.User;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.UserAttribute;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface UserAttributeRepository extends JpaRepository<UserAttribute, String> {
    List<UserAttribute> findAllAttributesByUser(User user);

    Optional<UserAttribute> findByUserAndAttributeName(User user, String attributeName);
}

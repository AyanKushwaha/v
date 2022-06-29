package com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.User;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<User, String> {
}

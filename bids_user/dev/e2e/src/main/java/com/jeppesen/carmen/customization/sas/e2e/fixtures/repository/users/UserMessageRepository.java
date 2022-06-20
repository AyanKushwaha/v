package com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.users;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.UserMessage;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface UserMessageRepository extends JpaRepository<UserMessage, Long> {
    Optional<UserMessage> findByMessageText(String messageText);
}

package com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import com.fasterxml.jackson.datatype.jsr310.deser.LocalDateTimeDeserializer;
import com.fasterxml.jackson.datatype.jsr310.ser.LocalDateTimeSerializer;
import lombok.*;
import lombok.experimental.Accessors;
import org.springframework.format.annotation.DateTimeFormat;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;
import java.io.Serializable;
import java.time.LocalDateTime;

import static lombok.AccessLevel.NONE;
import static org.springframework.format.annotation.DateTimeFormat.ISO.DATE_TIME;

@Data
@Entity
@Table(name = "USERS")
@NoArgsConstructor
@RequiredArgsConstructor
@Accessors(chain = true)
@EqualsAndHashCode(exclude = "userId")
@JsonIgnoreProperties(ignoreUnknown = true)
public class User implements Serializable {

    private static final long serialVersionUID = 635573837099652760L;

    @Id
    @NonNull
    @Setter(NONE)
    @Column(name = "USERID", nullable = false, length = 32)
    String userId;

    @Column(name = "LOGINID", nullable = false, length = 32)
    String loginId;

    @Column(name = "PASSWORD", length = 128)
    String password;

    @Column(name = "FIRSTNAME", length = 64)
    String firstName;

    @Column(name = "LASTNAME", length = 64)
    String lastName;

    @DateTimeFormat(iso = DATE_TIME)
    @Column(name = "MESSAGESLASTREAD")
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime messagesLastRead;

    @Column(name = "INACTIVE")
    @DateTimeFormat(iso = DATE_TIME)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime inactive;
}

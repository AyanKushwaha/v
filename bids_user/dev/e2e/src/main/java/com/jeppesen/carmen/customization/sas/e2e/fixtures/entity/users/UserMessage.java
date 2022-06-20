package com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import com.fasterxml.jackson.datatype.jsr310.deser.LocalDateTimeDeserializer;
import com.fasterxml.jackson.datatype.jsr310.ser.LocalDateTimeSerializer;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.Accessors;
import org.springframework.format.annotation.DateTimeFormat;

import javax.persistence.*;
import java.io.Serializable;
import java.time.LocalDateTime;

import static javax.persistence.GenerationType.SEQUENCE;
import static lombok.AccessLevel.NONE;
import static org.springframework.format.annotation.DateTimeFormat.ISO.DATE_TIME;

@Data
@Entity
@NoArgsConstructor
@Accessors(chain = true)
@Table(name = "USERMESSAGES")
@EqualsAndHashCode(exclude = "messageId")
@JsonIgnoreProperties(ignoreUnknown = true)
public class UserMessage implements Serializable {

    private static final long serialVersionUID = -7373399622823449730L;

    @Id
    @Setter(NONE)
    @Column(name = "MESSAGEID", nullable = false)
    @GeneratedValue(strategy = SEQUENCE, generator = "userMessagesSeq")
    @SequenceGenerator(name = "userMessagesSeq", sequenceName = "USERMESSAGESSEQUENCE", allocationSize = 1)
    Long messageId;

    @Column(name = "MESSAGETEXT", columnDefinition = "CLOB NOT NULL", nullable = false)
    String messageText;

    @DateTimeFormat(iso = DATE_TIME)
    @Column(name = "STARTTIME", nullable = false)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime startTime;

    @DateTimeFormat(iso = DATE_TIME)
    @Column(name = "ENDTIME", nullable = false)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime endTime;

    @DateTimeFormat(iso = DATE_TIME)
    @Column(name = "CREATED", nullable = false)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime created;

    @DateTimeFormat(iso = DATE_TIME)
    @Column(name = "UPDATED", nullable = false)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime updated;

    @Column(name = "GROUPID", nullable = false)
    Long groupId;
}

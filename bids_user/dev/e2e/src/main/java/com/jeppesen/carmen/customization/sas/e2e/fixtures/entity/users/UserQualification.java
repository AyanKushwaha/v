package com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import com.fasterxml.jackson.datatype.jsr310.deser.LocalDateTimeDeserializer;
import com.fasterxml.jackson.datatype.jsr310.ser.LocalDateTimeSerializer;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Qualification;
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
@Table(name = "USERQUALIFICATIONS")
@EqualsAndHashCode(exclude = "userQualId")
@JsonIgnoreProperties(ignoreUnknown = true)
public class UserQualification implements Serializable {

    private static final long serialVersionUID = 8316394252962337225L;

    @Id
    @Setter(NONE)
    @Column(name = "USERQUALID", nullable = false)
    @GeneratedValue(strategy = SEQUENCE, generator = "userQualificationsSeq")
    @SequenceGenerator(name = "userQualificationsSeq", sequenceName = "USERQUALIFICATIONSSEQUENCE", allocationSize = 1)
    Long userQualId;

    @DateTimeFormat(iso = DATE_TIME)
    @Column(name = "STARTDATE", nullable = false)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime startDate;

    @DateTimeFormat(iso = DATE_TIME)
    @Column(name = "ENDDATE", nullable = false)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime endDate;

    @ManyToOne
    @JoinColumn(name = "QUALID", referencedColumnName = "QUALID", nullable = false)
    Qualification qualification;

    @ManyToOne
    @JoinColumn(name = "USERID", referencedColumnName = "USERID", nullable = false)
    User user;
}

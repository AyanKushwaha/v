package com.jeppesen.carmen.customization.sas.e2e.fixtures.entity;

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
@Table(name = "PERIODS")
@Accessors(chain = true)
@EqualsAndHashCode(exclude = "periodId")
@JsonIgnoreProperties(ignoreUnknown = true)
public class Period implements Serializable {

    private static final long serialVersionUID = -6412189015731509435L;

    @Id
    @Setter(NONE)
    @Column(name = "PERIODID", nullable = false)
    @GeneratedValue(strategy = SEQUENCE, generator = "periodsSeq")
    @SequenceGenerator(name = "periodsSeq", sequenceName = "PERIODSSEQUENCE", allocationSize = 1)
    Long periodId;

    @Column(name = "GROUPID", nullable = false)
    Long groupId;

    @DateTimeFormat(iso = DATE_TIME)
    @Column(name = "OPENDATE", nullable = false)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime openDate;

    @DateTimeFormat(iso = DATE_TIME)
    @Column(name = "CLOSEDATE", nullable = false)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime closeDate;

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

    @Column(name = "TYPE", nullable = false, length = 32)
    String type;
}

package com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids;

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
@Table(name = "BIDS")
@Accessors(chain = true)
@JsonIgnoreProperties(ignoreUnknown = true)
@EqualsAndHashCode(exclude = "bidSequenceId")
public class Bid implements Serializable {

    private static final long serialVersionUID = 2596271169467306664L;

    @Id
    @Setter(NONE)
    @Column(name = "BIDSEQUENCEID", nullable = false, insertable = false)
    @GeneratedValue(strategy = SEQUENCE, generator = "bidsSeq")
    @SequenceGenerator(name = "bidsSeq", sequenceName = "BIDSSEQUENCE", allocationSize = 1)
    Long bidSequenceId;

    @Column(name = "REVISIONDATE", nullable = false)
    @DateTimeFormat(iso = DATE_TIME)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime revisionDate;

    @Column(name = "BIDID", nullable = false)
    Long bidId;

    @Column(name = "BIDTYPE", nullable = false, length = 32)
    String bidType;

    @Column(name = "NAME", length = 256)
    String name;

    @Column(name = "BIDGROUPID", nullable = false)
    Long bidGroupId;

    @Column(name = "STARTDATE")
    @DateTimeFormat(iso = DATE_TIME)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime startDate;

    @Column(name = "ENDDATE")
    @DateTimeFormat(iso = DATE_TIME)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime endDate;

    @Column(name = "CREATEDBY", nullable = false, length = 32)
    String createdBy;

    @Column(name = "CREATED", nullable = false)
    @DateTimeFormat(iso = DATE_TIME)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime created;

    @Column(name = "UPDATEDBY", length = 32)
    String updatedBy;

    @Column(name = "UPDATED")
    @DateTimeFormat(iso = DATE_TIME)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime updated;

    @Column(name = "INVALID")
    @DateTimeFormat(iso = DATE_TIME)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime invalid;
}

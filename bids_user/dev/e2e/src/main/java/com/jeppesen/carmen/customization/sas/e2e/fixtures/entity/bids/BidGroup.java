package com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import com.fasterxml.jackson.datatype.jsr310.deser.LocalDateTimeDeserializer;
import com.fasterxml.jackson.datatype.jsr310.ser.LocalDateTimeSerializer;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.Accessors;
import org.springframework.format.annotation.DateTimeFormat;

import javax.persistence.*;
import java.io.Serializable;
import java.time.LocalDateTime;

import static javax.persistence.EnumType.STRING;
import static org.springframework.format.annotation.DateTimeFormat.ISO.DATE_TIME;

@Data
@Entity
@NoArgsConstructor
@Accessors(chain = true)
@Table(name = "BIDGROUPS")
@IdClass(BidGroupPK.class)
@JsonIgnoreProperties(ignoreUnknown = true)
public class BidGroup implements Serializable {

    private static final long serialVersionUID = -1110867377331019898L;

    @SuppressWarnings("squid:S00115")
    public enum Category {
        current,
        preference,
        category_bid,
        standing_bid,
        global,
    }

    @Id
    @DateTimeFormat(iso = DATE_TIME)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JoinColumn(name = "REVISIONDATE", nullable = false)
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime revisionDate;

    @Id
    @JoinColumn(name = "BIDGROUPID", nullable = false)
    Long bidGroupId;

    @Column(name = "USERID", nullable = false, length = 32)
    String userId;

    @Column(name = "NAME", nullable = false, length = 256)
    String name;

    @Column(name = "DESCRIPTION", length = 256)
    String description;

    @Enumerated(STRING)
    @Column(name = "CATEGORY", nullable = false, length = 16)
    Category category;

    @Column(name = "TYPE", nullable = false, length = 32)
    String type;

    @Column(name = "SUBMITTED")
    @DateTimeFormat(iso = DATE_TIME)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime submitted;

    @DateTimeFormat(iso = DATE_TIME)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    @Column(name = "STARTDATE", nullable = false)
    LocalDateTime startDate;

    @Column(name = "ENDDATE")
    @DateTimeFormat(iso = DATE_TIME)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime endDate;

    @Column(name = "CREATEDBY", nullable = false, length = 32)
    String createdBy;

    @DateTimeFormat(iso = DATE_TIME)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    @Column(name = "CREATED", nullable = false)
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

    @Column(name = "CACHEMARK")
    Long cacheMark;
}

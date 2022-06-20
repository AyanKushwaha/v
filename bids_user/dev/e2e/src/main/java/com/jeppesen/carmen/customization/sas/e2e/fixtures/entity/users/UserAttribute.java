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
import lombok.experimental.Accessors;
import org.springframework.format.annotation.DateTimeFormat;

import javax.persistence.*;
import java.io.Serializable;
import java.time.LocalDateTime;

import static javax.persistence.GenerationType.SEQUENCE;
import static org.springframework.format.annotation.DateTimeFormat.ISO.DATE_TIME;

@Data
@Entity
@NoArgsConstructor
@Accessors(chain = true)
@Table(name = "USERATTRIBUTES")
@JsonIgnoreProperties(ignoreUnknown = true)
@EqualsAndHashCode(exclude = "userAttributeId")
public class UserAttribute implements Serializable {

    private static final long serialVersionUID = -7609997409230394058L;

    @Id
    @Column(name = "USERATTRIBUTEID", nullable = false)
    @GeneratedValue(strategy = SEQUENCE, generator = "userAttributesSeq")
    @SequenceGenerator(name = "userAttributesSeq", sequenceName = "USERATTRIBUTESSEQUENCE", allocationSize = 1)
    Long userAttributeId;

    @Column(name = "ATTRIBUTENAME", nullable = false, length = 32)
    String attributeName;

    @Column(name = "ATTRIBUTEVALUE", length = 256)
    String attributeValue;

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

    @ManyToOne
    @JoinColumn(name = "USERID", referencedColumnName = "USERID", nullable = false)
    User user;
}

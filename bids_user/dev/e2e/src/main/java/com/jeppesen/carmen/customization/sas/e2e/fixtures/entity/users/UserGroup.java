package com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import com.fasterxml.jackson.datatype.jsr310.deser.LocalDateTimeDeserializer;
import com.fasterxml.jackson.datatype.jsr310.ser.LocalDateTimeSerializer;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Group;
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
@Table(name = "USERGROUPS")
@EqualsAndHashCode(exclude = "userGroupId")
@JsonIgnoreProperties(ignoreUnknown = true)
public class UserGroup implements Serializable {

    private static final long serialVersionUID = 7468565957765207810L;

    @Id
    @Setter(NONE)
    @Column(name = "USERGROUPID", nullable = false)
    @GeneratedValue(strategy = SEQUENCE, generator = "userGroupsSeq")
    @SequenceGenerator(name = "userGroupsSeq", sequenceName = "USERGROUPSSEQUENCE", allocationSize = 1)
    Long userGroupId;

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
    @JoinColumn(name = "GROUPID", referencedColumnName = "GROUPID", nullable = false)
    Group group;

    @ManyToOne
    @JoinColumn(name = "USERID", referencedColumnName = "USERID", nullable = false)
    User user;
}

package com.jeppesen.carmen.customization.sas.e2e.fixtures.entity;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.Accessors;

import javax.persistence.*;
import java.io.Serializable;

import static javax.persistence.GenerationType.SEQUENCE;
import static lombok.AccessLevel.NONE;

@Data
@Entity
@NoArgsConstructor
@Table(name = "GROUPS")
@Accessors(chain = true)
@EqualsAndHashCode(exclude = "groupId")
@JsonIgnoreProperties(ignoreUnknown = true)
public class Group implements Serializable {

    private static final long serialVersionUID = 818628035387907461L;

    @Id
    @Setter(NONE)
    @Column(name = "GROUPID", nullable = false)
    @GeneratedValue(strategy = SEQUENCE, generator = "groupsSeq")
    @SequenceGenerator(name = "groupsSeq", sequenceName = "GROUPSSEQUENCE", allocationSize = 1)
    Long groupId;

    @Column(name = "GROUPNAME", nullable = false, length = 32)
    String groupName;

    @Column(name = "DESCRIPTION", length = 128)
    String description;
}

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
@Accessors(chain = true)
@Table(name = "QUALIFICATIONS")
@EqualsAndHashCode(exclude = "qualId")
@JsonIgnoreProperties(ignoreUnknown = true)
public class Qualification implements Serializable {

    private static final long serialVersionUID = -4601041670338946923L;

    @Id
    @Setter(NONE)
    @Column(name = "QUALID", nullable = false)
    @GeneratedValue(strategy = SEQUENCE, generator = "qualificationsSeq")
    @SequenceGenerator(name = "qualificationsSeq", sequenceName = "QUALIFICATIONSSEQUENCE", allocationSize = 1)
    Long qualId;

    @Column(name = "QUALNAME", nullable = false, length = 32)
    String qualName;

    @Column(name = "DESCRIPTION", length = 128)
    String description;
}

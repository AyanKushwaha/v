package com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids;

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
@Table(name = "BIDPROPERTYENTRIES")
@JsonIgnoreProperties(ignoreUnknown = true)
@EqualsAndHashCode(exclude = "bidPropertyEntryId")
public class BidPropertyEntry implements Serializable {

    private static final long serialVersionUID = -1678425285804917896L;

    @Id
    @Setter(NONE)
    @Column(name = "BIDPROPERTYENTRYID", nullable = false)
    @GeneratedValue(strategy = SEQUENCE, generator = "bidPropertyEntriesSeq")
    @SequenceGenerator(name = "bidPropertyEntriesSeq", sequenceName = "BIDPROPERTYENTRIESSEQUENCE", allocationSize = 1)
    Long bidPropertyEntryId;

    @Column(name = "ENTRYKEY", nullable = false, length = 32)
    String entryKey;

    @Column(name = "ENTRYVALUE", length = 1024)
    String entryValue;

    @ManyToOne
    @JoinColumn(name = "BIDPROPERTYID", referencedColumnName = "BIDPROPERTYID")
    BidProperty bidProperty;
}

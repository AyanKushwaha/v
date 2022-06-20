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
@Table(name = "BIDPROPERTIES")
@JsonIgnoreProperties(ignoreUnknown = true)
@EqualsAndHashCode(exclude = "bidPropertyId")
public class BidProperty implements Serializable {

    private static final long serialVersionUID = 7384335921457528546L;

    @Id
    @Setter(NONE)
    @Column(name = "BIDPROPERTYID", nullable = false)
    @GeneratedValue(strategy = SEQUENCE, generator = "bidPropertiesSeq")
    @SequenceGenerator(name = "bidPropertiesSeq", sequenceName = "BIDPROPERTIESSEQUENCE", allocationSize = 1)
    Long bidPropertyId;

    @Column(name = "SORTORDER", nullable = false)
    Long sortOrder;

    @Column(name = "BIDPROPERTYTYPE", nullable = false, length = 32)
    String bidPropertyType;

    @ManyToOne
    @JoinColumn(name = "BIDSEQUENCEID", referencedColumnName = "BIDSEQUENCEID", nullable = false)
    Bid bid;
}

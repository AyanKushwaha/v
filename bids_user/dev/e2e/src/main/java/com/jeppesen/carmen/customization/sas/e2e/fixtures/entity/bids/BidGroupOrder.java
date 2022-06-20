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

import static org.springframework.format.annotation.DateTimeFormat.ISO.DATE_TIME;

@Data
@Entity
@NoArgsConstructor
@Accessors(chain = true)
@Table(name = "BIDGROUPORDER")
@IdClass(BidGroupOrderPK.class)
@JsonIgnoreProperties(ignoreUnknown = true)
public class BidGroupOrder implements Serializable {

    private static final long serialVersionUID = 5583551862490599170L;

    @Id
    @JoinColumn(name = "BIDGROUPID", nullable = false)
    Long bidGroupId;

    @Id
    @DateTimeFormat(iso = DATE_TIME)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JoinColumn(name = "REVISIONDATE", nullable = false)
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime revisionDate;

    @Column(name = "ROWINDEX", nullable = false)
    Long rowIndex;
}

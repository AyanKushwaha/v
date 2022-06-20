package com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import com.fasterxml.jackson.datatype.jsr310.deser.LocalDateTimeDeserializer;
import com.fasterxml.jackson.datatype.jsr310.ser.LocalDateTimeSerializer;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;
import lombok.experimental.Accessors;
import org.springframework.format.annotation.DateTimeFormat;

import javax.persistence.Column;
import javax.persistence.Embeddable;
import javax.persistence.Id;
import java.io.Serializable;
import java.time.LocalDateTime;

import static org.springframework.format.annotation.DateTimeFormat.ISO.DATE_TIME;

@Data
@Embeddable
@NoArgsConstructor
@EqualsAndHashCode
@Accessors(chain = true)
public class BidGroupOrderPK implements Serializable {

    private static final long serialVersionUID = -7362672682332731146L;

    @Id
    @Column(name = "BIDGROUPID", nullable = false, precision = 0)
    Long bidGroupId;

    @Id
    @DateTimeFormat(iso = DATE_TIME)
    @Column(name = "REVISIONDATE", nullable = false)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss.SSS")
    @JsonSerialize(using = LocalDateTimeSerializer.class)
    @JsonDeserialize(using = LocalDateTimeDeserializer.class)
    LocalDateTime revisionDate;
}

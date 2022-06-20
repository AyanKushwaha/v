package com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidProperty;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

public interface BidPropertyRepository extends JpaRepository<BidProperty, Long> {

    List<BidProperty> findAllByBidCreatedBy(@Param("createdBy") String userId);

    List<BidProperty> findAllByBidBidId(long bidId);

    List<BidProperty> findAllByBidBidIdIn(List<Long> bidIds);

    @Modifying(flushAutomatically = true)
    @Transactional
    @Query("DELETE FROM #{#entityName} bp WHERE bp.bidPropertyId IN :ids")
    void deleteByIds(@Param("ids") List<Long> ids);
}

package com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.Bid;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

public interface BidRepository extends JpaRepository<Bid, Long> {

    @Modifying(flushAutomatically = true)
    @Transactional
    @Query("DELETE FROM #{#entityName} b WHERE b.bidId IN :ids")
    void deleteByIds(@Param("ids") List<Long> ids);

    Bid findTopByOrderByBidIdDesc();
}

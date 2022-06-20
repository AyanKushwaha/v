package com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidPropertyEntry;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

public interface BidPropertyEntryRepository extends JpaRepository<BidPropertyEntry, Long> {

    @Query(
            " SELECT bpe FROM #{#entityName} bpe              " +
                    " WHERE bpe.bidProperty.bidPropertyId IN (        " +
                    "     SELECT pb.bidPropertyId FROM BidProperty pb " +
                    "     WHERE pb.bid.createdBy = :userId )          ")
    List<BidPropertyEntry> findAllUserBidPropertyEntries(@Param("userId") String userId);

    List<BidPropertyEntry> findAllByBidPropertyBidPropertyId(Long bidPropertyId);

    List<BidPropertyEntry> findAllByBidPropertyBidPropertyIdIn(List<Long> bidPropertyIds);

    @Modifying(flushAutomatically = true)
    @Transactional
    @Query("DELETE FROM #{#entityName} bpe WHERE bpe.bidProperty.bidPropertyId IN :bidPropertyIds")
    void deleteByBidPropertyIds(@Param("bidPropertyIds") List<Long> bidPropertyIds);
}

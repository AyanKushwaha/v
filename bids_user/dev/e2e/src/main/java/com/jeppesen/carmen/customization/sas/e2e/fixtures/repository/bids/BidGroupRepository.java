package com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidGroup;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidGroupPK;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.repository.query.Param;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

public interface BidGroupRepository extends JpaRepository<BidGroup, BidGroupPK> {

    List<BidGroup> findAllByUserId(@Param("userId") String userId);

    @Modifying(flushAutomatically = true)
    @Transactional
    void deleteAllByUserIdAndName(@Param("userId") String userId, @Param("name") String name);
}

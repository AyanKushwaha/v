package com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidGroupOrder;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidGroupOrderPK;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface BidGroupOrderRepository extends JpaRepository<BidGroupOrder, BidGroupOrderPK> {

    @Query(
            " SELECT bgo FROM #{#entityName} bgo        " +
                    " WHERE bgo.bidGroupId in (                 " +
                    "     SELECT bg.bidGroupId FROM BidGroup bg " +
                    "     WHERE bg.userId = :userId )           ")
    List<BidGroupOrder> finaAllUserBidGroupOrders(@Param("userId") String userId);
}

package com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidOrder;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidOrderPK;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface BidOrderRepository extends JpaRepository<BidOrder, BidOrderPK> {

    @Query(
            " SELECT bo FROM #{#entityName} bo  " +
                    " WHERE bo.bidId IN (               " +
                    "     SELECT b.bidId FROM Bid b     " +
                    "     WHERE b.createdBy = :userId ) ")
    List<BidOrder> findAllUserBidOrders(@Param("userId") String userId);
}

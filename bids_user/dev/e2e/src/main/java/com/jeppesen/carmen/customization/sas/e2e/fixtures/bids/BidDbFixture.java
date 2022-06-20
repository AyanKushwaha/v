package com.jeppesen.carmen.customization.sas.e2e.fixtures.bids;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.api.Fixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.Bid;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.User;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidRepository;
import lombok.RequiredArgsConstructor;
import lombok.val;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.security.SecureRandom;
import java.util.Map;
import java.util.function.UnaryOperator;

@Service
@RequiredArgsConstructor
public class BidDbFixture implements Fixture<Bid> {

    final BidRepository bidRepository;
    final BidDraftFixture bidDraftFixture;
    final BidGroupDbFixture bidGroupDbFixture;
    final BidOrderDbFixture bidOrderDbFixture;
    final BidPropertyDbFixture bidPropertyDbFixture;

    @Transactional
    public Bid create(UnaryOperator<Bid> patchedBid, Map<String, Map<String, String>> properties) {
        val savedBid = bidRepository.save(patchedBid.apply(initDraft()));
        val bid = bidRepository.save(savedBid.setBidId(savedBid.getBidSequenceId()));

        val iterator = properties.entrySet().iterator();
        for (long i = 1L; iterator.hasNext(); i++) {
            val sortOrder = i;
            val e = iterator.next();
            bidPropertyDbFixture.create(bp -> bp.setBid(bid)
                            .setBidPropertyType(e.getKey())
                            .setSortOrder(sortOrder),
                    e.getValue());
        }
        return bid;
    }

    @Transactional
    public Bid create(UnaryOperator<Bid> patchedBid, User user) {
        val savedBid = bidRepository.save(patchedBid.apply(initDraft()).setCreatedBy(user.getUserId()));
        val bid = bidRepository.save(savedBid.setBidId(savedBid.getBidSequenceId()));
        bidPropertyDbFixture.create(bp -> bp.setBid(bid));
        bidGroupDbFixture.create(bg -> bg.setBidGroupId(bid.getBidGroupId()).setUserId(user.getUserId()));
        bidOrderDbFixture.create(bo -> bo.setBidId(bid.getBidId()));
        return bid;
    }

    @Override
    @Transactional
    public Bid create(Bid obj) {
        val savedBid = bidRepository.save(obj);
        val bid = bidRepository.save(savedBid.setBidId(savedBid.getBidSequenceId()));
        bidPropertyDbFixture.create(bp -> bp.setBid(bid));
        return bid;
    }

    @Override
    public Bid initDraft() {
        final long identifier = new SecureRandom().nextLong();
        return bidDraftFixture.initDraft(identifier);
    }
}

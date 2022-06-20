package com.jeppesen.carmen.customization.sas.e2e.infrastructure;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.GroupsDbFixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.PeriodsDbFixture;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Group;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.Bid;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.bids.BidProperty;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.users.User;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.PeriodRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidGroupRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidPropertyEntryRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidPropertyRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.bids.BidRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.repository.users.UserRepository;
import com.jeppesen.carmen.customization.sas.e2e.fixtures.users.UserAttributeDbFixture;
import com.jeppesen.carmen.customization.sas.e2e.po.AdministrationPage;
import lombok.NoArgsConstructor;
import lombok.extern.log4j.Log4j2;
import lombok.val;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

import static java.lang.String.format;
import static java.time.LocalTime.MIDNIGHT;
import static lombok.AccessLevel.PRIVATE;

/**
 * Purpose of this class is basically DRY code.
 */
@Log4j2
@NoArgsConstructor(access = PRIVATE)
public class TestUtils {

    public static void addAttributeToUser(String userId,
                                          String attributeName,
                                          String attributeValue,
                                          UserRepository userRepository,
                                          UserAttributeDbFixture userAttributeDbFixture) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException(format("user with id=%s not found", userId)));
        userAttributeDbFixture.create(ua -> ua.setUser(user).setAttributeName(attributeName).setAttributeValue(attributeValue));
    }

    public static void preparePeriodForFirstGroup(CrewPortalProps props,
                                                  PeriodRepository periodRepository,
                                                  PeriodsDbFixture periodsDbFixture,
                                                  AdministrationPage administrationPage) {
        periodRepository.deleteAll();
        String groupName = props.getAdministrationPage().getGroups().iterator().next();
        periodsDbFixture.createForGroup(groupName);
        flushCache(administrationPage);
    }

    public static void preparePeriodForGroup(String groupName,
                                             PeriodRepository periodRepository,
                                             PeriodsDbFixture periodsDbFixture,
                                             AdministrationPage administrationPage) {
        periodRepository.deleteAll();
        periodsDbFixture.createForGroup(groupName);
        flushCache(administrationPage);
    }

    public static void preparePeriodByTypeForGroup(String groupName, String periodType,
                                                   PeriodRepository periodRepository,
                                                   PeriodsDbFixture periodsDbFixture,
                                                   AdministrationPage administrationPage) {
        periodRepository.deleteAll();
        periodsDbFixture.createForGroup(groupName);
        periodsDbFixture.createPeriodByTypeForGroup(groupName, periodType);
        flushCache(administrationPage);
    }

    public static void prepareOneDayPeriodAndFlushCache(String groupName,
                                                        PeriodRepository periodRepository,
                                                        PeriodsDbFixture periodsDbFixture,
                                                        GroupsDbFixture groupsDbFixture,
                                                        AdministrationPage administrationPage) {

        final LocalDateTime todayMidnight = LocalDateTime.of(java.time.LocalDate.now(), MIDNIGHT);
        final Group group = groupsDbFixture.create(g -> g.setGroupName(groupName));

        periodRepository.deleteAll();
        periodsDbFixture.create(p -> p.setGroupId(group.getGroupId())
                .setStartDate(todayMidnight)
                .setEndDate(todayMidnight.plusHours(23).minusMinutes(59))
                .setOpenDate(todayMidnight)
                .setCloseDate(todayMidnight.plusHours(23).minusMinutes(59)));

        flushCache(administrationPage);
    }

    public static void deletePeriodsAndFlushCache(PeriodRepository periodRepository,
                                                  AdministrationPage administrationPage) {
        periodRepository.deleteAll();
        flushCache(administrationPage);
    }

    public static void deleteAllBids(BidRepository bidRepository,
                                     BidPropertyRepository bidPropertyRepository,
                                     BidPropertyEntryRepository bidPropertyEntryRepository,
                                     AdministrationPage administrationPage) {
        bidPropertyEntryRepository.deleteAll();
        bidPropertyRepository.deleteAll();
        bidRepository.deleteAll();
        flushCache(administrationPage);
    }

    public static void deleteCurrentUserBidGroups(String bidGroup,
                                                  CrewPortalProps props,
                                                  BidGroupRepository bidGroupRepository) {
        bidGroupRepository.deleteAllByUserIdAndName(props.getLogin().getCrew().getUsername(), bidGroup);
    }

    public static void deleteBid(Bid bid,
                                 BidRepository bidRepository,
                                 BidPropertyRepository bidPropertyRepository,
                                 BidPropertyEntryRepository bidPropertyEntryRepository,
                                 AdministrationPage administrationPage) {

        val bidId = bid.getBidId();
        val bps = bidPropertyRepository.findAllByBidBidId(bidId);
        val bpIds = bps.stream().map(BidProperty::getBidPropertyId).collect(Collectors.toList());

        bidPropertyEntryRepository.deleteByBidPropertyIds(bpIds);
        bidPropertyRepository.deleteByIds(bpIds);
        bidRepository.deleteById(bidId);

        flushCache(administrationPage);
    }

    public static void deleteLastBid(BidRepository bidRepository,
                                     BidPropertyRepository bidPropertyRepository,
                                     BidPropertyEntryRepository bidPropertyEntryRepository,
                                     AdministrationPage administrationPage) {

        val bid = bidRepository.findTopByOrderByBidIdDesc();
        deleteBid(bid, bidRepository, bidPropertyRepository, bidPropertyEntryRepository, administrationPage);
    }

    public static void deleteBids(List<Bid> bids,
                                  BidRepository bidRepository,
                                  BidPropertyRepository bidPropertyRepository,
                                  BidPropertyEntryRepository bidPropertyEntryRepository,
                                  AdministrationPage administrationPage) {

        val bidIds = bids.stream().map(Bid::getBidId).collect(Collectors.toList());
        deleteBidsByIds(bidIds, bidRepository, bidPropertyRepository, bidPropertyEntryRepository, administrationPage);
    }

    public static void deleteBidsByIds(List<Long> bidIds,
                                       BidRepository bidRepository,
                                       BidPropertyRepository bidPropertyRepository,
                                       BidPropertyEntryRepository bidPropertyEntryRepository,
                                       AdministrationPage administrationPage) {

        val bps = bidPropertyRepository.findAllByBidBidIdIn(bidIds);
        val bpIds = bps.stream().map(BidProperty::getBidPropertyId).collect(Collectors.toList());

        bidPropertyEntryRepository.deleteByBidPropertyIds(bpIds);
        bidPropertyRepository.deleteByIds(bpIds);
        bidRepository.deleteByIds(bidIds);

        flushCache(administrationPage);
    }

    public static void flushCache(AdministrationPage administrationPage) {
        administrationPage.open().home()
                .clickServersMenu().flushCacheRequest()
                .close();
    }
}

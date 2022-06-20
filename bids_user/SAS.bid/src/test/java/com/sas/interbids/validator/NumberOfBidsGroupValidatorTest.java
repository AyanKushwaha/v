package com.sas.interbids.validator;

import com.jeppesen.carmen.crewweb.interbids.bo.Bid;
import com.jeppesen.carmen.crewweb.interbids.bo.BidGroup;
import com.jeppesen.carmen.crewweb.interbids.bo.BidProperty;
import com.jeppesen.carmen.crewweb.interbids.validation.ValidatorResult;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.runners.MockitoJUnitRunner;

import java.util.Arrays;
import java.util.List;

import static com.jeppesen.jcms.crewweb.common.util.CWTimeRange.DAYS;
import static com.sas.interbids.base.BidsPerPriority.HIGH;
import static com.sas.interbids.base.BidsPerPriority.LOW;
import static com.sas.interbids.base.BidsPerPriority.MEDIUM;
import static java.util.Collections.singletonList;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.*;

@RunWith(MockitoJUnitRunner.class)
public class NumberOfBidsGroupValidatorTest {

    private final CWDateTime startDateTime = CWDateTime.create(2018, 11, 1, 2, 0, 0);
    private NumberOfBidsGroupValidator validator;
    @Mock
    private BidGroup bidGroup;

    @Before
    public void dependencyInjection() {
        validator = new NumberOfBidsGroupValidator();
    }

    @After
    public void resetMocks() {
        reset(bidGroup);
    }


    @Test
    public void different_priority_ok() {

        // Given
        Bid newBid = mockBid("time_off", MEDIUM.getPriorityValue(), startDateTime, startDateTime.plus(2, DAYS));
        Bid existingBid1 = mockBid("flight", MEDIUM.getPriorityValue(), startDateTime, startDateTime.plus(3, DAYS));
        Bid existingBid2 = mockBid("stop", LOW.getPriorityValue(), startDateTime, startDateTime.plus(3, DAYS));
        Bid existingBid3 = mockBid("flight", HIGH.getPriorityValue(), startDateTime, startDateTime.plus(3, DAYS));

        When(Arrays.asList(newBid, existingBid1, existingBid2, existingBid3));

        ValidatorResult result = validator.validate(bidGroup);

        //Then
        assertEquals(result.getResultObject(), bidGroup);
        assertTrue(result.isEmpty());
        assertTrue(result.isValid());
        assertEquals(result.getValidationFailureList().size(), 0);
    }

    @Test
    public void same_priority_ok() {

        // Given
        Bid newBid = mockBid("time_off", MEDIUM.getPriorityValue(), startDateTime, startDateTime.plus(2, DAYS));
        Bid existingBid1 = mockBid("flight", MEDIUM.getPriorityValue(), startDateTime, startDateTime.plus(3, DAYS));

        When(Arrays.asList(newBid, existingBid1));

        ValidatorResult result = validator.validate(bidGroup);

        //Then
        assertEquals(result.getResultObject(), bidGroup);
        assertTrue(result.isEmpty());
        assertTrue(result.isValid());
        assertEquals(result.getValidationFailureList().size(), 0);
    }

    @Test
    public void same_priority_amount_exceeded() {

        // Given
        Bid newBid = mockBid("time_off", HIGH.getPriorityValue(), startDateTime, startDateTime.plus(2, DAYS));
        Bid existingBid1 = mockBid("flight", HIGH.getPriorityValue(), startDateTime, startDateTime.plus(3, DAYS));
        List<String> expectedParams = Arrays.asList(String.valueOf(HIGH.getAllowedBidsAmount()), HIGH.name());

        When(Arrays.asList(newBid, existingBid1));

        ValidatorResult result = validator.validate(bidGroup);

        //Then
        assertEquals(result.getResultObject(), bidGroup);
        assertFalse(result.isEmpty());
        assertFalse(result.isValid());
        assertEquals(result.getValidationFailureList().size(), 1);
        assertEquals(result.getValidationFailureList().get(0).getMessage(), "max_bidchainno_bidgroup_error");
        assertEquals(result.getValidationFailureList().get(0).getMessageParameters(), expectedParams);
    }

    private Bid mockBid(final String bidType,
                        final String bidPriority,
                        final CWDateTime startDateTime,
                        final CWDateTime endDateTime) {

        Bid mockedBid = mock(Bid.class);
        BidProperty property = mock(BidProperty.class);

        given(mockedBid.getType()).willReturn(bidType);
        given(mockedBid.getStartDate()).willReturn(startDateTime);
        given(mockedBid.getEndDate()).willReturn(endDateTime);
        given(mockedBid.getBidProperties()).willReturn(singletonList(property));
        given(property.getType()).willReturn("priority");
        given(property.getBidPropertyEntryValue("priority")).willReturn(bidPriority);

        return mockedBid;
    }

    private void When(List<Bid> existingBids) {
        when(bidGroup.getAllBids()).thenReturn(existingBids);
    }
}

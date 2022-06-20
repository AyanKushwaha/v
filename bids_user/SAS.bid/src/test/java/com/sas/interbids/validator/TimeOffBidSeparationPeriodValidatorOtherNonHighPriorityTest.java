package com.sas.interbids.validator;

import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.validation.ValidationDataSet;
import com.jeppesen.carmen.crewweb.interbids.validation.ValidatorResult;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.runners.MockitoJUnitRunner;

import static com.jeppesen.jcms.crewweb.common.util.CWTimeRange.DAYS;
import static java.util.Collections.singletonList;
import static org.mockito.Matchers.any;
import static org.mockito.Matchers.anyListOf;
import static org.mockito.Matchers.anyString;
import static org.mockito.Mockito.*;

@RunWith(MockitoJUnitRunner.class)
public class TimeOffBidSeparationPeriodValidatorOtherNonHighPriorityTest {

    TimeOffBidSeparationPeriodValidator validator = new TimeOffBidSeparationPeriodValidator();

    @Mock BidData bidData, otherBidData;
    @Mock ValidatorResult result;
    @Mock ValidationDataSet validationDataSet;

    @Test
    public void validateOnUserCreateTest() {

        final CWDateTime start = CWDateTime.create(2017, 11, 1);
        final CWDateTime end = start.plus(2, DAYS);

        when(bidData.getType())
                .thenReturn("time_off");
        when(bidData.getStartDate())
                .thenReturn(start);
        when(bidData.getEndDate())
                .thenReturn(end);
        when(bidData.get("bid.property.priority.priority"))
                .thenReturn("high");

        when(otherBidData.getType())
                .thenReturn("time_off");
        when(otherBidData.getStartDate())
                .thenReturn(start.plus(3, DAYS));
        when(otherBidData.getEndDate())
                .thenReturn(end.plus(3, DAYS));
        when(otherBidData.get("bid.property.priority.priority"))
                .thenReturn("medium");

        when(validationDataSet.getOtherBidsInSameBidGroupAs(any(BidData.class)))
                .thenReturn(singletonList(otherBidData));

        validator.validateOnUserCreate(bidData, result, validationDataSet, null);

        verify(result, times(0))
                .addValidationError(anyString(), anyListOf(String.class));
    }
}

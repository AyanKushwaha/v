package com.sas.interbids.validator;

import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.validation.ValidationDataSet;
import com.jeppesen.carmen.crewweb.interbids.validation.ValidatorResult;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.runners.MockitoJUnitRunner;

import static java.util.Collections.singletonList;
import static org.mockito.Matchers.any;
import static org.mockito.Matchers.anyListOf;
import static org.mockito.Matchers.anyString;
import static org.mockito.Mockito.*;

@RunWith(MockitoJUnitRunner.class)
public class TimeOffBidSeparationPeriodValidatorSeparationPeriodIsTooShortTest {

    TimeOffBidSeparationPeriodValidator validator = new TimeOffBidSeparationPeriodValidator();

    @Mock BidData bidData, otherBidData;
    @Mock ValidatorResult result;
    @Mock ValidationDataSet validationDataSet;

    @Test
    public void validateOnUserCreateTest() {

        when(otherBidData.getType())
                .thenReturn("time_off");
        when(otherBidData.getStartDate())
                .thenReturn(CWDateTime.create(2017, 10, 31));
        when(otherBidData.getEndDate())
                .thenReturn(CWDateTime.create(2017, 11, 2));
        when(otherBidData.get("bid.property.priority.priority"))
                .thenReturn("high");

        when(bidData.getType())
                .thenReturn("time_off");
        when(bidData.getStartDate())
                .thenReturn(CWDateTime.create(2017, 11, 3));
        when(bidData.getEndDate())
                .thenReturn(CWDateTime.create(2017, 11, 4));
        when(bidData.get("bid.property.priority.priority"))
                .thenReturn("high");

        when(validationDataSet.getOtherBidsInSameBidGroupAs(any(BidData.class)))
                .thenReturn(singletonList(otherBidData));

        validator.validateOnUserCreate(bidData, result, validationDataSet, null);

        verify(result, times(1))
                .addValidationError(anyString(), anyListOf(String.class));
    }
}

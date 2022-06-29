package com.sas.interbids.validator;

import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.validation.ValidatorResult;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.runners.MockitoJUnitRunner;

import static org.mockito.Matchers.anyListOf;
import static org.mockito.Matchers.anyString;
import static org.mockito.Mockito.*;

@RunWith(MockitoJUnitRunner.class)
public class TimeOffBidSeparationPeriodValidatorNonTimeOffBidTypeTest {

    TimeOffBidSeparationPeriodValidator validator = new TimeOffBidSeparationPeriodValidator();

    @Mock BidData bidData;
    @Mock ValidatorResult result;

    @Test
    public void validateOnUserCreateTest() {

        when(bidData.getType())
                .thenReturn("non time_off");

        validator.validateOnUserCreate(bidData, result, null, null);

        verify(result, times(0))
                .addValidationError(anyString(), anyListOf(String.class));
    }
}

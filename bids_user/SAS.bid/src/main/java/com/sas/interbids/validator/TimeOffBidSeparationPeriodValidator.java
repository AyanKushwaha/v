package com.sas.interbids.validator;

import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidTypeValidatorContext;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidTypeValidatorInterface;
import com.jeppesen.carmen.crewweb.interbids.validation.IValidatorResult;
import com.jeppesen.carmen.crewweb.interbids.validation.ValidationDataSet;
import com.jeppesen.carmen.crewweb.interbids.validation.ValidatorResult;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;
import org.joda.time.Duration;

import java.util.List;
import java.util.Map;

import static java.lang.String.valueOf;
import static java.util.Collections.singletonList;
import static org.joda.time.Duration.standardHours;

public class TimeOffBidSeparationPeriodValidator implements BidTypeValidatorInterface {

    public static final int MAXIMUM_ALLOWED_BID_DURATION_IN_HOURS = 72;
    public static final int MINIMUM_REQUIRED_SEPARATION_PERIOD_IN_HOURS = 48;
    public static final Duration MAXIMUM_ALLOWED_BID_DURATION = standardHours(MAXIMUM_ALLOWED_BID_DURATION_IN_HOURS);
    public static final Duration MINIMUM_REQUIRED_SEPARATION_PERIOD = standardHours(MINIMUM_REQUIRED_SEPARATION_PERIOD_IN_HOURS);

    // helpers

    private void validateBidPeriod(final BidData bidData,
                                   final IValidatorResult result,
                                   final ValidationDataSet validationDataSet) {

        if (!"time_off".equals(bidData.getType())) return;

        if (durationIsExceeded(bidData))
            result.addValidationError("time_off.bid_duration_is_exceeded",
                                      singletonList(valueOf(MAXIMUM_ALLOWED_BID_DURATION_IN_HOURS)));

        if (priorityIsNotHigh(bidData)) return;

        final List<BidData> otherBids = validationDataSet.getOtherBidsInSameBidGroupAs(bidData);
        if (null == otherBids || otherBids.isEmpty()) return;

        for (final BidData otherBidData : otherBids) {

            if (priorityIsNotHigh(otherBidData)) continue;

            if (separationPeriodIsValid(bidData, otherBidData)) continue;

            result.addValidationError("time_off.high_bid_separation_period_is_too_short",
                                      singletonList(valueOf(MINIMUM_REQUIRED_SEPARATION_PERIOD_IN_HOURS)));
        }
    }

    /**
     * @return true if bid duration is longer than MAXIMUM_ALLOWED_BID_DURATION_IN_HOURS.
     */
    private boolean durationIsExceeded(final BidData bidData) {

        final Duration bidDuration = new Duration(bidData.getStartDate().getDateTime(),
                                                  bidData.getEndDate().getDateTime());

        return bidDuration.compareTo(MAXIMUM_ALLOWED_BID_DURATION) > 0;
    }

    private boolean priorityIsNotHigh(final BidData bidData) {
        final String priority = bidData.get("bid.property.priority.priority");
        return null != priority && !"high".equals(priority.toLowerCase());
    }

    /**
     * @return true if separation bids period is valid.
     */
    private boolean separationPeriodIsValid(final BidData d1, final BidData d2) {

        final CWDateTime end1 = d1.getEndDate();
        final CWDateTime start2 = d2.getStartDate();

        if (!end1.isAfter(start2)) {
            final Duration currentSeparationPeriod = new Duration(end1.getDateTime(), start2.getDateTime());
            return currentSeparationPeriod.compareTo(MINIMUM_REQUIRED_SEPARATION_PERIOD) >= 0;
        }

        final CWDateTime end2 = d2.getEndDate();
        final CWDateTime start1 = d1.getStartDate();

        if (!end2.isAfter(start1)) {
            final Duration currentSeparationPeriod = new Duration(end2.getDateTime(), start1.getDateTime());
            return currentSeparationPeriod.compareTo(MINIMUM_REQUIRED_SEPARATION_PERIOD) >= 0;
        }

        return false;
    }

    // lifecycle hooks

    @Override
    public void validateOnUserUpdate(final BidData bidData,
                                     final ValidatorResult result,
                                     final ValidationDataSet validationDataSet,
                                     final BidTypeValidatorContext context) {

        validateBidPeriod(bidData, result, validationDataSet);
    }

    @Override
    public void validateOnUserCreate(final BidData bidData,
                                     final ValidatorResult result,
                                     final ValidationDataSet validationDataSet,
                                     final BidTypeValidatorContext context) {

        validateBidPeriod(bidData, result, validationDataSet);
    }

    // necessary empty overrides

    @Override
    public void validateOnSystemImport(final BidData bidData,
                                       final ValidatorResult result,
                                       final ValidationDataSet validationDataSet,
                                       final BidTypeValidatorContext context) { }
    @Override
    public void validateOnSystemContinouosValidation(final BidData bidData,
                                                     final ValidatorResult result,
                                                     final ValidationDataSet validationDataSet,
                                                     final BidTypeValidatorContext context) { }
    @Override
    public void validateAfterTripCacheFlush(final BidData bid,
                                            final ValidatorResult partialResult,
                                            final ValidationDataSet validationDataSet,
                                            final BidTypeValidatorContext context) { }
    @Override
    public void validate(final BidData bidData,
                         final IValidatorResult result,
                         final ValidationDataSet validationDataSet,
                         final BidTypeValidatorContext context) { }
    @Override
    public void setAttributes(final Map<String, String> attributes) { }
}

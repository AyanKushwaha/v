package com.jeppesen.carmen.crewweb.interbids.customization.standard;

import java.util.List;

import com.jeppesen.carmen.crewweb.framework.bo.Period;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserCustomizationAPI;
import com.jeppesen.carmen.crewweb.framework.context.aware.UserCustomizationAPIAware;
import com.jeppesen.carmen.crewweb.framework.customization.LogoutValidationHandler;
import com.jeppesen.carmen.crewweb.framework.exception.CWNoCurrentPeriodException;
import com.jeppesen.carmen.crewweb.framework.exception.UnauthorizedException;
import com.jeppesen.carmen.crewweb.interbids.bo.BidGroup;
import com.jeppesen.carmen.crewweb.interbids.business.facade.BidManagerCustomizationAPI;
import com.jeppesen.carmen.crewweb.interbids.context.aware.BidManagerCustomizationAPIAware;
import com.jeppesen.jcms.crewweb.common.context.aware.LocalizationAware;
import com.jeppesen.jcms.crewweb.common.localization.Localization;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;
import com.jeppesen.jcms.crewweb.common.util.CWLog;

public class LogoutValidationHandlerImpl implements LogoutValidationHandler, UserCustomizationAPIAware,
        BidManagerCustomizationAPIAware, LocalizationAware {

    private static final CWLog LOG = CWLog.getLogger(LogoutValidationHandlerImpl.class);

    /**
     * A UserCustomizationAPI to get current user information
     */
    private UserCustomizationAPI userCustomizationAPI;

    /**
     * A BidManagerCustomizationAPI to get bid and group information for user
     */
    private BidManagerCustomizationAPI bidManagerCustomizationAPI;

    /**
     * A LocalizationManager to get localized messages.
     */
    private Localization localization;

    /**
     * Method is called when a LogoutValidation message is received in the MessageBrooker. Return a warning if no
     * BidGroups are found for current user.
     * 
     * @return warning if no bid groups found otherwise empty string.
     */
    public String performLogoutValidation() {
        String logoutValidationMessage = "";
        String userId = userCustomizationAPI.getUserId();
        Period period = null;
        try {
            period = userCustomizationAPI.getCurrentPeriodForUser(userId, "standard");
        } catch (CWNoCurrentPeriodException exception) {
            // Users that have no period defined should still be able to log out.
            return logoutValidationMessage;
        }
        CWDateTime startDate = period.getStart();
        List<BidGroup> bidGroups;
        try {
            bidGroups = bidManagerCustomizationAPI.getBidGroupsWithBidsForUserDateCategory(userId,
                    startDate, "current");
        } catch (UnauthorizedException exception) {
            // Unauthorized users should still be able to log out.
            return logoutValidationMessage;
        }
        if (bidGroups.size() == 1) {
            BidGroup bidGroup = bidGroups.get(0);
            String name = bidGroup.getName();
            if ("InvalidBidGroup".equals(name)) {
                logoutValidationMessage = localization.MSGR("logout_validation_invalid_bidgroup");
            }
        }
        return logoutValidationMessage;
    }

    /**
     * {@inheritDoc}
     */
    public void setUserCustomizationAPI(UserCustomizationAPI userCustomizationAPI) {
        this.userCustomizationAPI = userCustomizationAPI;
    }

    /**
     * {@inheritDoc}
     */
    public void setBidManagerCustomizationAPI(BidManagerCustomizationAPI bidManagerCustomizationAPI) {
        this.bidManagerCustomizationAPI = bidManagerCustomizationAPI;
    }

    /**
     * {@inheritDoc}
     */
    public void setLocalization(Localization localization) {
        this.localization = localization;
    }
}

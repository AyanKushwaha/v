package com.sas.interbids.bidgroup;

import static java.lang.String.format;

import java.util.Collection;
import java.util.List;

import javax.enterprise.context.SessionScoped;
import javax.enterprise.inject.Specializes;
import javax.inject.Inject;
import javax.servlet.http.HttpServletRequest;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.jeppesen.carmen.crewweb.framework.bo.Period;
import com.jeppesen.carmen.crewweb.interbids.bo.BidGroup;
import com.jeppesen.carmen.crewweb.interbids.bo.impl.BidGroupImpl;
import com.jeppesen.carmen.crewweb.interbids.context.InterbidsUserData;
import com.jeppesen.carmen.crewweb.interbids.validation.ValidatorResult;
//import com.jeppesen.carmen.crewweb.sso.service.SSOInitializationCallback;
import com.jeppesen.jcms.crewweb.common.exception.CWRuntimeException;
import com.jeppesen.jcms.crewweb.common.util.CWLog;
import com.jeppesen.jcms.wpf.security.cacs.config.ConfigMBean;
import com.sas.interbids.base.SasConstants;

/**
 * {@link SessionScoped} class that automatically creates the default bid group
 * for the current period if one doesn't exist already.
 */
@SessionScoped
@Specializes
public class DefaultBidGroupCreator extends InterbidsUserData {

	private static final long serialVersionUID = 1L;
	private static final CWLog LOG = CWLog.getLogger(DefaultBidGroupCreator.class);

	/**
	 * The bid category of current.
	 * BID_CATEGORY_CURRENT = "current";
	 */

	/**
	 * The bid category of preference.
	 * BID_CATEGORY_PREFERENCE = "preference";
	 */

	/**
	 * The bid group type of flight.
	 * BID_GROUP_TYPE_FLIGHT = "flight";
	 */

	/**
	 * The bid group type of preference.
	 * BID_GROUP_TYPE_PREFERENCE = "preference-bids";
	 */	

	Logger logger = LoggerFactory.getLogger(DefaultBidGroupCreator.class);

    @Inject
    ConfigMBean cacsConfig;
	
	@Override
	public void init(HttpServletRequest req) {
		super.init(req);
		if (getUserRole() != null) {
			Collection<String> features = cacsConfig.getRoleFeaturesInScope(getUserRole(), "not-used");
			setUserFeatures(features);
		}
    }
	
	@Override
	protected void createDefaultBidGroups() {
		LOG.debug(format("New session for initialized: crewId=%s, userId=%s", crewId, userId));
		if (userIsNotAdministrator()) {
			if (getUserManager().userHasCurrentPeriod(crewId, Period.STANDARD_BID_PERIOD)) {
				Period period = getUserManager().getCurrentPeriodForUser(crewId, Period.STANDARD_BID_PERIOD);
	
				populateBidGroup(crewId, period, SasConstants.BID_GROUP_NAME_CURRENT, SasConstants.BID_CATEGORY_CURRENT,
						SasConstants.BID_GROUP_TYPE_FLIGHT);
				
		        populateBidGroup(crewId, period, SasConstants.BID_GROUP_NAME_PREFERENCES, SasConstants.BID_CATEGORY_PREFERENCE,
		        		SasConstants.BID_GROUP_TYPE_PREFERENCE);
			}
		}
	}
	
	private boolean userIsNotAdministrator() {
		return !crewId.toLowerCase().startsWith("admin");
	}

	@Override
	protected void triggerTemplateCreateDefaultBidGroups() {
		templateCreateDefaultBidGroups();
	}
	
	@Override
	public void setUserFeatures(Collection<String> userFeatures) {
		super.setUserFeatures(userFeatures);
	}

	/**
	 * This method is to populate the bid group if needed.
	 * 
	 * @param userId
	 *            The user id to use
	 * @param period
	 *            The current period to use
	 * @param groupName
	 *            The name of the bid group to use
	 * @param category
	 *            The category of the bid to use
	 * @param groupType
	 *            The type of the bid group to use
	 */
	private void populateBidGroup(String userId, Period period, String groupName, String category, String groupType) {
		// Confirm that Current bid group exists.
		List<BidGroup> bidGroups = getBidManager().getBidGroupsForUserDateCategory(userId, period.getStart(), category);

		int groupCount = 0;

		for (BidGroup bidGroup : bidGroups) {
			if (category.equals(bidGroup.getCategory())) {
				groupCount++;
				break; // don't need to count till end
			}
		} // end BidGroup for loop

		// Only create bidGroup if it doesn't already exists for this category
		if (groupCount == 0) {
			createBidGroup(groupName, category, groupType);
		}

	}

	/**
	 * This method is to create the bid group object.
	 * 
	 * @param name
	 *            The name of the bid group to use
	 * @param category
	 *            The category of the bid to use
	 * @param type
	 *            The type of the bid group to use
	 */
	private void createBidGroup(String name, String category, String type) {
		BidGroupImpl bidGroup = new BidGroupImpl();
		bidGroup.setName(name);
		bidGroup.setDescription(name + " (auto-created)");
		bidGroup.setCategory(category);
		bidGroup.setType(type);

		try {
			ValidatorResult validatorResult = getBidManager().createBidGroup(bidGroup);

			if (validatorResult.isError()) {
				LOG.error("Could not auto-created default bid group (" + name + ").\n"
						+ validatorResult.getFailureMessages());
			}
		} catch (CWRuntimeException cwre) {
			LOG.error("Could not auto-create default bid group (" + name + ").", cwre);
		}
	}
}

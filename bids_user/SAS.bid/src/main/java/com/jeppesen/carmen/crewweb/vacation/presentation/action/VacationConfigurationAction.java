package com.jeppesen.carmen.crewweb.vacation.presentation.action;

import com.jeppesen.carmen.backendfacade.xmlschema.jmp.v2.*;
import com.jeppesen.carmen.crewweb.backendfacade.presentation.action.JMPErrorHandlingActionInvocationTemplate;
import com.jeppesen.carmen.crewweb.framework.configuration.LocaleConfiguration;
import com.jeppesen.carmen.crewweb.framework.presentation.action.BaseAction;
import com.jeppesen.carmen.crewweb.jmpframework.business.BidManager;
import com.jeppesen.carmen.crewweb.jmpframework.presentation.action.ConfigurationAction;
import com.jeppesen.carmen.crewweb.vacation.context.VacationApplicationContextImpl;
import com.jeppesen.jcms.crewweb.common.configuration.ConfigurationManager;
import com.jeppesen.jcms.crewweb.common.context.ICWContext;
import com.jeppesen.jcms.crewweb.common.exception.CWException;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;
import com.jeppesen.jcms.crewweb.common.util.CWLog;
import com.jeppesen.jcms.crewweb.common.util.TimeManager;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.util.*;

public class VacationConfigurationAction extends ConfigurationAction {

    private static final long serialVersionUID = 1L;

    private static final CWLog log = CWLog.getLogger(VacationConfigurationAction.class);

    public VacationConfigurationAction() {
        super(VacationApplicationContextImpl.getInstance().getBidManager(),
                VacationApplicationContextImpl.getInstance().getConfigurationModel().getLocaleConfiguration(
                        VacationApplicationContextImpl.getInstance().getConfigurationManager()),
                VacationApplicationContextImpl.getInstance().getConfigurationManager(),
                VacationApplicationContextImpl.getInstance().getTimeManager(),
                VacationApplicationContextImpl.getInstance().getLocalizationManager(),
                VacationApplicationContextImpl.getInstance().getAuditTrail());
    }

    private Map<String, Object> setPeriodInfoMap(JaxbCrewInitResponse userData) {
        final ConfigurationManager configurationManager = VacationApplicationContextImpl.getInstance().getConfigurationManager();
        final TimeManager timeManager = VacationApplicationContextImpl.getInstance().getTimeManager();

        JaxbPeriod period = userData.getPeriod();
        Map<String, Object> periodMap = null;
        if (period != null) {
            periodMap = new HashMap<>();
            Map<String, Object> crewBidWindowMap = new HashMap<>();
            Map<String, Object> crewBidPeriodMap = new HashMap<>();
            String crewHomeBaseTimeZone = userData.getCrewHomeBaseTimeZone();
            DateFormat formatter = new SimpleDateFormat(CWDateTime.ISO_8601_DATETIME_SECOND_FORMAT);
            if (crewHomeBaseTimeZone == null) {
                crewHomeBaseTimeZone = configurationManager.getPropertyAsString("crewweb.bid.window.timeZone", ConfigurationManager.MessageLevel.WARNING_MESSAGE);
            }

            if (crewHomeBaseTimeZone == null) {
                log.warn(String.format("No crew time zone defined for %s in awarding type %s for userid: %s. Using system default timezone: %s",
                        userData.getAwardingCategory(), userData.getAwardingType(), this.fetchContext().getBiddingUserId(),
                        TimeZone.getDefault().getID()));
            } else {
                formatter.setTimeZone(TimeZone.getTimeZone(crewHomeBaseTimeZone));
            }

            Calendar from = period.getBidWindow().getFrom();
            Calendar to = period.getBidWindow().getTo();

            // Introduced to fix SKS-539, SKS-548, SKJMP-1479
            boolean isMidnight = to.get(Calendar.HOUR_OF_DAY) == 0 && to.get(Calendar.MINUTE) == 0 && to.get(Calendar.SECOND) == 0;
            if (isMidnight) {
                ZoneId zoneId = crewHomeBaseTimeZone == null ? TimeZone.getDefault().toZoneId()
                                                             : TimeZone.getTimeZone(crewHomeBaseTimeZone).toZoneId();
                int offsetSeconds = ZonedDateTime.now(zoneId).getOffset().getTotalSeconds();
                int shift = offsetSeconds + 1;
                to.add(Calendar.SECOND, -shift);
            }

            crewBidWindowMap.put("from", formatter.format(from.getTime()));
            crewBidWindowMap.put("to", formatter.format(to.getTime()));
            periodMap.put("bidWindow", crewBidWindowMap);
            crewBidPeriodMap.put("from", period.getBidPeriod().getFrom());
            crewBidPeriodMap.put("to", period.getBidPeriod().getTo());
            periodMap.put("crewTimeZone", crewHomeBaseTimeZone);
            periodMap.put("bidPeriod", crewBidPeriodMap);
            periodMap.put("openForBidding", timeManager.nowInInterval(from, to));
        }

        return periodMap;
    }

    @Override
    public String getConfiguration() {
        final ICWContext context = fetchContext();
        final BaseAction action = this;

        return new JMPErrorHandlingActionInvocationTemplate<JaxbGetTypeBasedRoutingInfoResponse>(action, log){
            final BidManager bidManager = VacationApplicationContextImpl.getInstance().getBidManager();

            @Override
            protected JaxbGetTypeBasedRoutingInfoResponse getBackendResponse() throws CWException {
                return bidManager.getTypeBasedRoutingInfo();
            }

            @Override
            protected void createResponse(JaxbGetTypeBasedRoutingInfoResponse backendResponse) throws CWException {

                final LocaleConfiguration localeConfig = VacationApplicationContextImpl.getInstance().getConfigurationModel().getLocaleConfiguration(
                        VacationApplicationContextImpl.getInstance().getConfigurationManager());

                List<JaxbRoutingId> routingIdList = backendResponse.getRoutingId();

                final List<Object> allAwardingTypes = new ArrayList<>();

                for (final JaxbRoutingId jaxbRoutingId : routingIdList) {
                    final Map<String, Object> awTypeMap = new HashMap<>();
                    awTypeMap.put("name", jaxbRoutingId.getType());


                    new JMPErrorHandlingActionInvocationTemplate<JaxbCrewInitResponse>(action, log) {

                        @Override
                        protected JaxbCrewInitResponse getBackendResponse() throws CWException {
                            return bidManager
                                    .getInitializationData(context.getAuthenticatedUserId(),
                                            context.getBiddingUserId(), jaxbRoutingId.getType());
                        }

                        @Override
                        protected void createResponse(JaxbCrewInitResponse userData) throws CWException {
                            Map<String, Object> periodInfoMap = setPeriodInfoMap(userData);
                            if (periodInfoMap != null) {
                                awTypeMap.put("periodInfo", periodInfoMap);
                            }

                            JaxbCrewInformation crewInformation = userData.getCrewInformation();
                            awTypeMap.put("crewInfo", crewInformation);

                            awTypeMap.put("bidGroups", userData.getBidGroups());

                            allAwardingTypes.add(awTypeMap);

                        }

                        @Override
                        protected String localizedContextualErrorMessage() {
                            return MSGR("get_configuration_error");
                        }

                    }.execute();
                }

                addToResult("awardingTypes", allAwardingTypes);

                Map<String, Object> calendarConfigMap = new HashMap<>();
                String strWeekendDays = localeConfig.getWeekendDays();
                List<String> weekendDaysList = new ArrayList<>();

                if (strWeekendDays != null) {
                    String[] arrayWeekdendDays = strWeekendDays.split(",");
                    for (String str : arrayWeekdendDays){
                        weekendDaysList.add(str.trim());
                    }
                }
                calendarConfigMap.put("weekendDays", weekendDaysList);
                calendarConfigMap.put("firstDayOfWeek", localeConfig.getFirstDayOfWeek());
                calendarConfigMap.put("locale", localeConfig.getLocale());
                addToResult("calendarConfig", calendarConfigMap);
                addToResult("awardingCategory", getAwardingCatagory());
            }

            @Override
            protected String localizedContextualErrorMessage() {
                return MSGR("get_configuration_error");
            }

        }.execute();
    }

    @Override
    protected String getAwardingCatagory() {
        return VacationApplicationContextImpl.getInstance().getAwardingCategory();
    }
}

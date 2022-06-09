package com.sas.interbids.datasources;

import java.util.HashSet;
import java.util.Map;

import com.jeppesen.carmen.crewweb.backendfacade.bo.DataSourceContainer;
import com.jeppesen.carmen.crewweb.backendfacade.bo.DataSourceDescriptor;
import com.jeppesen.carmen.crewweb.backendfacade.customization.api.DataSourceProcessorInterface;
import com.jeppesen.carmen.crewweb.backendfacade.customization.datasource.DataSourceContainerField;
import com.jeppesen.carmen.crewweb.backendfacade.customization.datasource.DataSourceContainerFieldFactory;
import com.jeppesen.carmen.crewweb.backendfacade.customization.datasource.DataSourceContainerRecord;
import com.jeppesen.carmen.crewweb.backendfacade.customization.datasource.MutableDataSourceContainer;
import com.jeppesen.carmen.crewweb.framework.bo.Period;
import com.jeppesen.carmen.crewweb.framework.bo.UserGroup;
import com.jeppesen.carmen.crewweb.framework.bo.UserQualification;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserAPI;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserCustomizationAPI;
import com.jeppesen.carmen.crewweb.framework.context.aware.UserCustomizationAPIAware;

public class NumberFWDaysDataSource implements DataSourceProcessorInterface, UserCustomizationAPIAware {

	private UserCustomizationAPI userCustomizationAPI;
	private static final int DEFAULT_FW_DAYS = 2;
	private static final int FD_SH_VG_FW_DAYS = 2;


	@Override
	public void setUserCustomizationAPI(UserCustomizationAPI arg0) {
		this.userCustomizationAPI = arg0;
	}

	private static HashSet<String> FD_SH_GROUPS = new HashSet<String>();

	static {

		// FD_SH_GROUPS.add("FD SH FG");
		FD_SH_GROUPS.add("FD SH SKN VG");
		FD_SH_GROUPS.add("FD SH SKD VG");
		FD_SH_GROUPS.add("FD SH SKS VG");
	}

	private static final String CONTRACTVG = "contractvg";

	@Override
	public DataSourceContainer process(DataSourceDescriptor descriptor,
			Map<String, String> requestParams) {

		UserAPI userAPI = userCustomizationAPI.getUserAPI(userCustomizationAPI.getUserId());
		MutableDataSourceContainer result = generateRecords(getNumberOfDaysForCrew(userAPI));

		return result;
	}

	private int getNumberOfDaysForCrew(UserAPI userAPI) {
		for (UserGroup userGroup : userAPI.getUserGroups()) {
			if (isGroupInValidityPeriod(userCustomizationAPI, userGroup)) {
				if (FD_SH_GROUPS.contains(userGroup.getGroupName())) {
					if (hasVariableContractWithinPeriods()) {
						return FD_SH_VG_FW_DAYS;
					}
				}
			}
		}
		return DEFAULT_FW_DAYS;
	}

	private MutableDataSourceContainer generateRecords(int days) {

		DataSourceContainerField value = DataSourceContainerFieldFactory.createField("value");

		MutableDataSourceContainer result = DataSourceContainerFieldFactory.createContainer();
		result.addField(value);

		for (int i = 2; i <= days; i++) {
			DataSourceContainerRecord value_record = DataSourceContainerFieldFactory.createRecord();
			value_record.setField(value, i);
			result.addRecord(value_record);
		}

		return result;
	}


	private Boolean isGroupInValidityPeriod(UserCustomizationAPI userCustomizationAPI, UserGroup group) {
		Period currPeriod = userCustomizationAPI.getCurrentPeriodForUser(userCustomizationAPI.getCurrentUserAPI().getUserId(), "standard");
		return group.getStartTime().isBefore(currPeriod.getStart()) || group.getStartTime().equals(currPeriod.getStart()) &&
				group.getEndTime().isAfter(currPeriod.getEnd()) || group.getEndTime().isEqual(currPeriod.getEnd());
	}

	private boolean hasVariableContractWithinPeriods() {

		UserAPI userAPI = userCustomizationAPI.getUserAPI(userCustomizationAPI.getUserId());
		for (UserQualification qualification : userAPI.getUserQualifications()) {
			if (CONTRACTVG.equalsIgnoreCase(qualification.getQualificationName().toLowerCase())) {
				if (isQualificationWithinOpenPeriod(qualification)) {
					return true;
				}
			}
		}
		return false;
	}


	private boolean isQualificationWithinOpenPeriod(UserQualification qualification) {
		Period currentPeriodForUser = userCustomizationAPI.getCurrentPeriodForUser(userCustomizationAPI.getUserId(), "C_FW");
		return qualification.getEndTime().isAfter(currentPeriodForUser.getStart()) &&
				qualification.getStartTime().isBefore(currentPeriodForUser.getEnd());
	}

}

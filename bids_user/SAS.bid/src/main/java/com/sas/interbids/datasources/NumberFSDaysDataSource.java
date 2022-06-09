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

public class NumberFSDaysDataSource implements DataSourceProcessorInterface, UserCustomizationAPIAware {

	private UserCustomizationAPI userCustomizationAPI;
	private static final int DEFAULT_FS_DAYS = 2;
	private static final int FD_SH_VG_FS_DAYS = 1;
	private static final int FD_CJ_VG_FS_DAYS = 3;
	
	@Override
	public void setUserCustomizationAPI(UserCustomizationAPI arg0) {
		// TODO Auto-generated method stub
		this.userCustomizationAPI = arg0;
	}
	
	private static HashSet<String> FD_SH_GROUPS = new HashSet<String>();
	
	static {
		
		FD_SH_GROUPS.add("FD SH SKN FG");
		FD_SH_GROUPS.add("FD SH SKS FG");
		FD_SH_GROUPS.add("FD SH SKD FG");
		FD_SH_GROUPS.add("FD SH SKS VG");
		FD_SH_GROUPS.add("FD SH SKD VG");
	}
	
	private static final String CONTRACTVG = "contractvg";
	private static final String CJ = "cj";

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
					if (hasCJQualificationWithinPeriods()) {
						return FD_CJ_VG_FS_DAYS;
					}
					else if (hasVariableContractWithinPeriods()) {
						return FD_SH_VG_FS_DAYS;
					}
				}
			}
		}
		return DEFAULT_FS_DAYS;
	}
	
	private MutableDataSourceContainer generateRecords(int days) {
		
		DataSourceContainerField value = DataSourceContainerFieldFactory.createField("value");

		MutableDataSourceContainer result = DataSourceContainerFieldFactory.createContainer();
		result.addField(value);
		
		for (int i = 1; i <= days; i++) {
			DataSourceContainerRecord value_record = DataSourceContainerFieldFactory.createRecord();
			value_record.setField(value, i);
			result.addRecord(value_record);
		}

		return result;
	}

//	private MutableDataSourceContainer generateRecords(UserQualification qualification, int days) {
//		
//		CWDateTime startTime = qualification.getStartTime();
//		CWDateTime endTime = qualification.getEndTime();
//		
//		
//		
//		DataSourceContainerField value = DataSourceContainerFieldFactory.createField("value");
//
//		MutableDataSourceContainer result = DataSourceContainerFieldFactory.createContainer();
//		result.addField(value);
//		
//		for (int i = 1; i <= days; i++) {
//			DataSourceContainerRecord value_record = DataSourceContainerFieldFactory.createRecord();
//			value_record.setField(value, i);
//			result.addRecord(value_record);
//		}
//
//		return result;
//	}

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

    private boolean hasCJQualificationWithinPeriods() {

            UserAPI userAPI = userCustomizationAPI.getUserAPI(userCustomizationAPI.getUserId());
            for (UserQualification qualification : userAPI.getUserQualifications()) {
                if (CJ.equalsIgnoreCase(qualification.getQualificationName().toLowerCase())) {
                    if (isQualificationWithinOpenPeriod(qualification)) {
                        return true;
                    }
                }
            }
            return false;
        }

//	private List<UserQualification> getVariableContractPeriods() {
//		List<UserQualification> qual = new ArrayList<UserQualification>();
//		
//		UserAPI userAPI = userCustomizationAPI.getUserAPI(userCustomizationAPI.getUserId());
//		for (UserQualification qualification : userAPI.getUserQualifications()) {
//			if (CONTRACTVG.equalsIgnoreCase(qualification.getQualificationName().toLowerCase())) {
//				if (qualificationEndsAfterPeriodStart(qualification)) { 
//					qual.add(qualification);
//				}
//			}
//		}
//		return qual;
//	}

//	private boolean qualificationEndsAfterPeriodStart(UserQualification qualification) {
//		Period currentPeriodForUser = userCustomizationAPI.getCurrentPeriodForUser(userCustomizationAPI.getUserId(), "A_FS");
//		return qualification.getEndTime().isAfter(currentPeriodForUser.getStart());
//	}
	
	private boolean isQualificationWithinOpenPeriod(UserQualification qualification) {
		Period currentPeriodForUser = userCustomizationAPI.getCurrentPeriodForUser(userCustomizationAPI.getUserId(), "A_FS");
		return qualification.getEndTime().isAfter(currentPeriodForUser.getStart()) &&
				qualification.getStartTime().isBefore(currentPeriodForUser.getEnd());
	}
	
}

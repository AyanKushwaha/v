package com.sas.interbids.base;

import java.util.ArrayList;

import com.jeppesen.carmen.crewweb.backendfacade.bo.Activity;
import com.jeppesen.carmen.crewweb.backendfacade.bo.Duty;

public class DutyExtImpl extends DutyExt {

	public DutyExtImpl(Duty duty) {
		super(duty);
	}

	@Override
	public ArrayList<ActivityExtImpl> getActivitesExt() {
		ArrayList<ActivityExtImpl> l = new ArrayList<ActivityExtImpl>();
		for (Activity activity : duty.getActivities()) {
			l.add(new ActivityExtImpl(activity));
		}
		return l;
	}
	
}
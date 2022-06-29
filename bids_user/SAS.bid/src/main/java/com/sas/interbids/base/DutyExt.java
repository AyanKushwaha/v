package com.sas.interbids.base;

import java.util.ArrayList;
import java.util.HashMap;

import com.jeppesen.carmen.crewweb.backendfacade.bo.Activity;
import com.jeppesen.carmen.crewweb.backendfacade.bo.Duty;

public abstract class DutyExt implements Duty{

	protected Duty duty;

	public DutyExt(Duty duty) {
		this.duty = duty;
	}



	/**
	 * Get an attribute for the duty.
	 * 
	 * @param key the key for the attribute.
	 * @return the attribute value.
	 */
	public String getAttribute(String key) {
		return duty.getAttribute(key);
	}

	/**
	 * Get all attributes for this duty object.
	 * 
	 * @return a hash map with all attribute name and values.
	 */
	public HashMap<String, String> getAttributes() {
		return duty.getAttributes();
	}

	/**
	 * Connect an activity with the duty. Will be added to the end of the activity list.
	 * 
	 * @param activity the activity to add.
	 */
	public void addActivity(Activity activity) {
		duty.addActivity(activity);
	}

	/**
	 * Get all activities for this duty.
	 * 
	 * @return all activities.
	 */
	public ArrayList<Activity> getActivities() {
		return duty.getActivities();
	}
	
	
	public abstract ArrayList<? extends ActivityExt> getActivitesExt();
}
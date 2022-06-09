package com.sas.interbids.base;
import java.util.HashMap;

import com.jeppesen.carmen.crewweb.backendfacade.bo.Activity;

public abstract class ActivityExt implements Activity {
	
	protected Activity activity;
	
	public ActivityExt(Activity activity) {
		this.activity = activity;
	}
	
	
	
	/**
	 * Get an attribute for the Activity.
	 * 
	 * @param key the key.
	 * @return the attribute value.
	 */
	public String getAttribute(String key) {
		return activity.getAttribute(key);
	}

	/**
	 * Get all attributes for this activity object.
	 * 
	 * @return a hash map with all attribute name and values.
	 */
	public HashMap<String, String> getAttributes() {
		return activity.getAttributes();
	}
	
}
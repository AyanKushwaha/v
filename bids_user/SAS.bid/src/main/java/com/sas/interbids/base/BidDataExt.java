package com.sas.interbids.base;

import java.util.List;

import com.jeppesen.carmen.crewweb.interbids.customization.api.BidData;
import com.jeppesen.carmen.crewweb.interbids.customization.api.BidPropertyData;
import com.jeppesen.jcms.crewweb.common.exception.CWRuntimeException;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;

public abstract class BidDataExt implements BidData {
	
	private BidData bidData;
	
	public BidDataExt(BidData bidData) {
		this.bidData = bidData;
	}
	
	 /**
     * Get the bid type.
     * 
     * @return The bid type.
     */
    public String getType() {
    	return bidData.getType();
    }

    /**
     * Get creation date and time.
     * 
     * @return the created date and time.
     */
    public CWDateTime getCreated() {
    	return bidData.getCreated();
    }

    /**
     * Get creator.
     * 
     * @return the user id if the user who created the bid.
     */
    public String getCreatedBy() {
    	return bidData.getCreatedBy();
    }

    /**
     * Get last updated date and time.
     * 
     * @return - the last updated date and time. <br/> - null if never updated.
     */
    public CWDateTime getUpdated() {
    	return bidData.getUpdated();
    }

    /**
     * Get updater who last updated the bid.
     * 
     * @return - the user id of the user who updated the record last<br/> - null if never updated.
     */
    public String getUpdatedBy() {
    	return bidData.getUpdatedBy();
    }

    /**
     * Get the end date of the bid.
     * 
     * @return the end date, null if UFN (open end date)
     */
    public CWDateTime getEndDate() {
    	return bidData.getEndDate();
    }

    /**
     * Get the start date of the bid.
     * 
     * @return the start date.
     */
    public CWDateTime getStartDate() {
    	return bidData.getStartDate();
    }
    

    /**
     * Check if the bid is locked or not.
     * 
     * @return true if the bid is marked as locked, otherwise returns false.
     */
    public boolean isLocked() {
    	return bidData.isLocked();
    }
	
    /**
     * This method gets the value for the given property value key.
     * <p/>
     * The key needs to use the full path to the requested value. It supports both bid related properties such as type,
     * and also direct access to single instance properties (that occur once in the list of bid properties).
     * <p/>
     * If the method detect that there are more than one property matching the key it will throw a runtime exception to
     * fail as fast as possible since the bid definition doesn't match the export logic.
     * <p/>
     * If <b>Example:</b><br/>
     * <code>data.get(BID_TYPE);<br>
     * data.get(BID_PROPERTY_PREFIX + "layover.station");</code>
     * 
     * @param key The fully qualified key, i.e. "layover.station".
     * @return The value matching the key, i.e. "LAX", or <code>null</code> if the key doesn't match anything.
     * @throws CWRuntimeException if the key match more than one value.
     */
	public String get(String key) {
		return bidData.get(key);
	}

	    /**
	     * This methods returns a list with the full key to all properties. Can be useful when looping through all
	     * properties for a bid without knowing the keys.
	     * 
	     * @return List of keys for all properties.
	     */
	public List<String> getAllPropertyKeys() {
		return bidData.getAllPropertyKeys();
	}

	/**
	 * This methods returns a list with the full key to all properties for the given property type. Can be useful when
	 * looping through all properties for a property type without knowing the keys.
	 * 
	 * @return List of the property keys for the given property type.
	 */
	public List<String> getAllPropertyKeysForType(String propertyType) {
		return bidData.getAllPropertyKeysForType(propertyType);
	}

	/**
	 * Get all bid property export data containers for a given bid property type. This is useful when having
	 * combination/complex bids with more than one bid property of the same type.
	 * <p/>
	 * <b>Example:</b><br/>
	 * <code>data.getAllByPropertyType("layover");<br/></code>
	 * 
	 * @param propertyType The property type name.
	 * @return A list of BidPropertyExportData objects with the data for the given property type.
	 */
	public List<BidPropertyData> getAllByPropertyType(String propertyType) {
		return bidData.getAllByPropertyType(propertyType);
	}

	/**
	 * Check if a property type exists in the bid data. This method is useful when having to check if a property exists
	 * before performing some property depending logic.
	 * <p/>
	 * <b>Example:</b><br/>
	 * 
	 * <pre>
	 * if (data.propertyExists("layover")) {
	 *   ...do some layover dependent logic...
	 * }
	 * </pre>
	 * 
	 * @param propertyType The property type to look for.
	 * @return true if it exists in the bid data object.
	 */
	public boolean propertyExists(String propertyType) {
		return bidData.propertyExists(propertyType);
	}
	
	
	/*
	 * Additional methods
	 */
	
	protected String getPropertyValue(String propertyKey) {
		return bidData.get(BID_PROPERTY_PREFIX + propertyKey);
	}
	
	protected String getTransientValue(String transientKey) {
		return bidData.get(BID_TRANSIENT_PREFIX + transientKey);
	}
	
	
	
}
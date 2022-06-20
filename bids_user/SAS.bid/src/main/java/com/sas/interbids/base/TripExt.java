package com.sas.interbids.base;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Set;

import com.jeppesen.carmen.crewweb.backendfacade.bo.CrewComplementVector;
import com.jeppesen.carmen.crewweb.backendfacade.bo.Duty;
import com.jeppesen.carmen.crewweb.backendfacade.bo.ImmutableTrip;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;

public abstract class TripExt implements ImmutableTrip {
	protected ImmutableTrip trip;

	public TripExt(ImmutableTrip trip) {
		this.trip = trip;
	}

	/**
	 * Get an attribute for the pairing.
	 * 
	 * @param key the key of the attribute value.
	 * @return the attribute.
	 */
	public String getAttribute(String key) {
		return trip.getAttribute(key);
	}

	/**
	 * Get all attributes for this trip object.
	 * 
	 * @return a hash map with all attribute name and values.
	 */
	// FIXME: WHY an implementation class in the API?
	public HashMap<String, Object> getAttributes() {
		return trip.getAttributes();
	}

	/**
	 * Get all attribute keys.
	 * 
	 * @return all attribute keys in a set.
	 */
	public Set<String> getAttributeKeys() {
		return trip.getAttributeKeys();
	}

	/**
	 * Get all duties for this trip.
	 * 
	 * @return duties all duties.
	 */
	// FIXME: WHY an implementation class in the API?
	public ArrayList<Duty> getDuties() {
		return trip.getDuties();
	}
	
	
	public abstract ArrayList<? extends DutyExt> getDutiesExt();
	

	/**
	 * Get crr id.
	 * 
	 * @return crrId.
	 */
	public String getCrrId() {
		return trip.getCrrId();
	}

	/**
	 * Get start date.
	 * 
	 * @return start date
	 */
	public CWDateTime getStart() {
		return trip.getStart();
	}

	/**
	 * Get end date.
	 * 
	 * @return end date
	 */
	public CWDateTime getEnd() {
		return trip.getEnd();
	}

	/**
	 * get the unique id for the trip.
	 * 
	 * @return unique id
	 */
	public String getUniqueId() {
		return trip.getUniqueId();
	}

	/**
	 * Returns the crew complement vector for this trip.
	 * <p>
	 * Not all implementations or installations of Bid support this attribute. If there is no information available, an
	 * empty {@link CrewComplementVector} is returned (this method never returns null).
	 * 
	 * @return the crew complement vector for this trip.
	 */
	public CrewComplementVector getCrewComplementVector() {
		return trip.getCrewComplementVector();
	}


}
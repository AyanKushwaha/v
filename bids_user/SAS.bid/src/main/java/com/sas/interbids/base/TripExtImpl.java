package com.sas.interbids.base;

import java.util.ArrayList;

import com.jeppesen.carmen.crewweb.backendfacade.bo.Duty;
import com.jeppesen.carmen.crewweb.backendfacade.bo.ImmutableTrip;

public class TripExtImpl extends TripExt {

	public TripExtImpl(ImmutableTrip trip) {
		super(trip);
	}

	@Override
	public ArrayList<DutyExtImpl> getDutiesExt() {
		ArrayList<DutyExtImpl> l = new ArrayList<DutyExtImpl>();
		for (Duty duty : trip.getDuties()) {
			l.add(new DutyExtImpl(duty));
		}
		return l;
	}
	
	
	
}
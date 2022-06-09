package com.sas.interbids.formatter;

import java.util.HashSet;
import java.util.Set;


public class TripDetailsConstants {
	
	private TripDetailsConstants() {
	}

	protected static Set<String> type_flight = new HashSet<String>();
	protected static Set<String> type_deadhead = new HashSet<String>();
	protected static Set<String> type_personal_reserve_training_or_ground = new HashSet<String>();
	protected static Set<String> type_reserve_training_or_ground = new HashSet<String>();
	protected static Set<String> type_request = new HashSet<String>();
	
	static {
		type_flight.add("flight");
	}
	
	static {
		type_deadhead.add("deadhead");
	}
	
	static {
		type_request.add("FS");
		type_request.add("FW");
		type_request.add("F0");
		type_request.add("F3S");
		type_request.add("F32");
		type_request.add("F7S");
		type_request.add("FS1");
	}
	
	static {
		type_personal_reserve_training_or_ground.add("personal");
		type_personal_reserve_training_or_ground.add("training");
		type_personal_reserve_training_or_ground.add("ground");
		type_personal_reserve_training_or_ground.add("UNDEFINED");
	}
	
	static {
		type_reserve_training_or_ground.add("training");
		type_reserve_training_or_ground.add("ground");
	}

}

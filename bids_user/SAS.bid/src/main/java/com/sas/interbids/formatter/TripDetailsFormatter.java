package com.sas.interbids.formatter;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;

import com.jeppesen.carmen.crewweb.backendfacade.bo.Activity;
import com.jeppesen.carmen.crewweb.backendfacade.bo.Duty;
import com.jeppesen.carmen.crewweb.backendfacade.bo.ImmutableTrip;
import com.jeppesen.carmen.crewweb.backendfacade.customization.api.TripDetailsFormatterInterface;
import com.jeppesen.carmen.crewweb.backendfacade.customization.api.TripReportContext;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;

/**
 * This class contains the default trip details formatting logic. It generates a
 * HTML table containing all trip, duty, activity properties available from the
 * source trip object.
 */

public class TripDetailsFormatter implements TripDetailsFormatterInterface {

	/**
	 * start date end position in string.
	 */
	private static final int columns = 4;
	
	protected static final Pattern regex_whitespace_comma_whitespace = Pattern.compile("\\s*,\\s*");
	protected static final Pattern regex_comma_whitespace = Pattern.compile(",\\s*");
	protected static final Pattern regex_whitespace = Pattern.compile("\\s");

	@Override
	public String generateTripDetails(ImmutableTrip trip) {
		StringBuilder builder = new StringBuilder();
		// builder.append("<table class='trip-details'>");
		builder.append("<table width='400' class='trip-details'>");
		builder.append("<tr>");
		builder.append("<td colspan='" + columns + "' class='heading'>");

		String tripType =  trip.getAttribute("type");
		if (tripType != null) {
			// For personal and reserve activities type and code is displayed
			if (isPersonalReserveTrainingOrGround(tripType)) {
				builder.append("Type: ");
				builder.append(!tripType.equalsIgnoreCase("undefined") ? tripType : "");
				builder.append(" ");
				builder.append(trip.getAttribute("code"));
				builder.append("</td>");
				builder.append("</tr>");
//				builder.append("<tr><td>&nbsp;</td></tr>");

				// For other, eg flights, Trip id, Operates and Crew complement
				// is shown on top
			} else { 

				// Create activity header row for flights
				builder.append("<tr>");

				builder.append(generateCrewComplHeader(trip));
				builder.append("</tr>");
				builder.append("<tr>");
				builder.append(generateActivityHeader(tripType));
				builder.append("</tr>");
			}

			ArrayList<Duty> duties = trip.getDuties();
			for (int j = 0; j < duties.size(); j++) {
				Duty duty = duties.get(j);

				// Duty (RTD) level

				// For personal, reserve and training duties only start and end
				// times are shown
				if (isPersonalReserveTrainingOrGround(tripType)) {
					builder.append(generateDetailInformationForPersonal(duty));
					/*
					builder.append("<tr>");
					// builder.append("<td>");
					builder.append("<td colspan='" + columns + "'>");
					builder.append(duty.getAttribute("startdate_local"));
					builder.append(" ");
					builder.append(duty.getAttribute("starttime_local"));
					builder.append(" ");
					builder.append("-");
					builder.append(" ");
					builder.append(duty.getAttribute("enddate_local"));
					builder.append(" ");
					builder.append(duty.getAttribute("endtime_local"));
					builder.append("</td>");
					builder.append("</tr>");
					*/

					// For other, eg flights, Briefing start time is shown
				} else if (isFlight(tripType)){
					builder.append("<tr><td></td>");
					builder.append("<td>");
					builder.append("C/I");
					builder.append("</td>");
					builder.append("<td></td><td>");
					builder.append(duty.getAttribute("starttime_local"));
					builder.append("</td>");
					builder.append("</tr>");
				}

				// Activitiy level

				// For flights, reserves, ground and training activities
				// detailed information about the activities are shown
			
				if (isFlight(tripType)
						|| isReserveTrainingOrGround(tripType)) {


					// Create activity details rows
					ArrayList<Activity> activities = duty.getActivities();
					for (int i = 0; i < activities.size(); i++) {
						Activity activity = activities.get(i);
						
						String activityType = activity.getAttribute("type");
						builder.append("<tr>");
						if (isFlight(activityType) || isDeadhead(activityType)) {

							builder.append("<td>");
							builder.append(activity.getAttribute("carrier"));
							builder.append(" ");
							builder.append(activity.getAttribute("number"));
							builder.append("</td>");

							builder.append("<td>");
							builder.append(activity
									.getAttribute("startstation"));
							builder.append("-");
							builder.append(activity.getAttribute("endstation"));
							builder.append("</td>");

							builder.append("<td>");
							builder.append(activity
									.getAttribute("starttime_local"));
							builder.append("</td>");

							builder.append("<td>");
							builder.append(activity
									.getAttribute("endtime_local"));
							builder.append("</td>");


							builder.append("<td>");
							builder.append(activity.getAttribute("blocktime"));
							builder.append("</td>");

							// If other (should be reserve or ground) print one
							// for each activity

							
						} else if (isReserveTrainingOrGround(activityType)) {
							builder.append("<td></td>");
							builder.append("<td>");
							builder.append(activity.getAttribute("code"));
							builder.append("</td>");

							builder.append("<td>");
							builder.append(activity
									.getAttribute("starttime_local"));
							builder.append("</td>");

							builder.append("<td>");
							builder.append(activity
									.getAttribute("endtime_local"));
							builder.append("</td>");

						}
					}

					if (isFlight(tripType)) {
						// For other, eg flights, Debriefing end time is shown
						builder.append("<tr><td></td>");
						builder.append("<td>");
						builder.append("C/O");
						builder.append("</td>");
						builder.append("<td></td><td>");
						builder.append(duty.getAttribute("endtime_local"));
						builder.append("<td></td><td>");
						if (!duty.getAttribute("resttime").equals("None") && 
								duty != duties.get(duties.size()-1)) {
							builder.append(duty.getAttribute("resttime"));
							if (duty.getAttribute("restrequired") != null) {
								builder.append(" (");
								builder.append(duty.getAttribute("restrequired"));
								builder.append(")");
							}
						}
						builder.append("</td>");
						builder.append("</tr>");
						builder.append("<tr><td>&nbsp;</td></tr>");
					}
				}
			}
			// For flights Freedays and Categories are shown at buttom
/*			if (isFlight(tripType)) {
				builder.append("<tr>");
				builder.append("<td colspan='" + 2 + "'>");
				builder.append("Free days ");
				if (!trip.getAttribute("freedays").equals("None")) {
					builder.append(trip.getAttribute("freedays"));
				}
				builder.append("</td>");
				builder.append("</tr>");
				builder.append("<tr>");
				builder.append("<td colspan='" + 2 + "'>");
				builder.append("Categories ");
				builder.append(trip.getAttribute("categories"));
				builder.append("</td>");
				builder.append("</tr>");
			}*/
			// }
		}
		builder.append("</table>");
		return builder.toString();
	}

	private boolean isFlight(String type){
		boolean result = false;
		if(TripDetailsConstants.type_flight.contains(type)){
			result = true;
		}
		return result;
	}
	
	private boolean isRequest(String type){
		boolean result = false;
		if(TripDetailsConstants.type_request.contains(type)){
			result = true;
		}
		return result;
	}
	
	private boolean isDeadhead(String type){
		boolean result = false;
		if(TripDetailsConstants.type_deadhead.contains(type)){
			result = true;
		}
		return result;
	}
	
	private boolean isPersonalReserveTrainingOrGround(String type){
		boolean result = false;
		if(TripDetailsConstants.type_personal_reserve_training_or_ground.contains(type)){
			result = true;
		}
		return result;
	}
	
	private boolean isReserveTrainingOrGround(String type){
		return TripDetailsConstants.type_reserve_training_or_ground.contains(type);
	}
	
	private String getTDHeadAndValue(String heading, String value) {
		StringBuilder builder = new StringBuilder();
		builder.append("<TD class='heading'>");
		builder.append("<TD>");
		builder.append(heading);
		builder.append("</TD><TD>");
		builder.append(value);
		builder.append("</TD>");
		return builder.toString();
	}
	
	private String generateCrewComplHeader(ImmutableTrip trip) {
		String crew_compl = trip.getAttribute("crewcompl");
		String compl[] = getListFromString(crew_compl);
		
		StringBuilder result = new StringBuilder();
		result.append("Positions: ");
		
		for (String pos : compl) {
			String[] p = regex_whitespace.split(pos);
			int num_pos = 0;
			try {
				num_pos = Integer.parseInt(p[0]);
				
			} catch (Exception e) {
				break;
			}
			
			if (num_pos > 0 && p.length > 1) {
				result.append(p[0] + " " + p[1] + ", ");
			}

		}
		
		return result.toString();
	}
	
	public String[] getListFromString(String string) {

		// Remove the extra "," at the beginning of the string in order not the get an empty field at the beginning
		if (string.charAt(0) == ',') {
			string = string.substring(1, string.length());
		}

		// Get a list of all selected weekdays
		String[] list = {}; 
		try {
			list = regex_comma_whitespace.split(string);
			
		} catch (Exception e) {
//			LOG.debug("No weekdays selected");
		}

		return list;
	}

	private String generateActivityHeader(String type) {

		StringBuilder builder = new StringBuilder();
		String[] headers = null;
		if (isFlight(type)) {
			headers = new String[] { "Flight", "Dep-Arr", "Start local",
					"End local", "Block", "Rest" };
		}
		// Header for reserves
		else if (isReserveTrainingOrGround(type)) {
			headers = new String[] { "Code", "Start local", "End local" };
		}
		// Header for request
		
		else if (isRequest(type)) {
			headers = new String[] { "Request", " ", " " };
		}
		// Default in case activity of type UNDEFINED is sent  
		else {
			headers = new String[] { "Code", "Start local", "End local" };
		}

		for (String header : headers) {
			builder.append("<td class='heading'>");
			builder.append(header);
			builder.append("</td>");
		}
		return builder.toString();
	}

	@Override
	public String generateTripReport(ImmutableTrip trip) {
		return generateTripDetails(trip);
	}

	@Override
	public String generateTripReportFooter(List<? extends ImmutableTrip> arg0,
			TripReportContext arg1) {
		return null;
	}

	@Override
	public String generateTripReportHeader(List<? extends ImmutableTrip> arg0,
			TripReportContext arg1) {
		return null;
	}

	@Override
	public String generateTripSummary(ImmutableTrip trip) {
		StringBuilder builder = new StringBuilder();
		builder.append(trip.getAttribute("startdate"));
		builder.append(" ");
		builder.append(trip.getAttribute("starttime"));
		builder.append(" ");

		ArrayList<Duty> duties = trip.getDuties();

		for (int i = 0; i < duties.size(); i++) {
			ArrayList<Activity> activities = duties.get(i).getActivities();
			if (i == 0) {
				builder.append(activities.get(0).getAttribute("startstation"));
				builder.append(" ");
			}
			builder.append(activities.get(activities.size() - 1).getAttribute(
					"endstation"));
			builder.append(" ");
		}

		builder.append(trip.getAttribute("enddate"));
		builder.append(" ");
		builder.append(trip.getAttribute("endtime"));

		return builder.toString();
	}
	
	private String generateDetailInformationForPersonal(Duty duty) {
		StringBuilder builder = new StringBuilder();
		
		CWDateTime startDate = CWDateTime.parseDateTime(duty.getAttribute("startdate_local") + " " + duty.getAttribute("starttime_local"));
		CWDateTime endDate = CWDateTime.parseDateTime(duty.getAttribute("enddate_local") + " " + duty.getAttribute("endtime_local"));
//		if (duty.getAttribute("endtime_local").equalsIgnoreCase("00:00")) {
//			endDate.addMinutes(-1);
//		}

		builder.append("<tr>");
		builder.append("<td colspan='" + columns + "'>");
//		builder.append(duty.getAttribute("startdate_local"));
		builder.append(CWDateTime.formatDateTime(startDate));
		builder.append(" ");
		builder.append("-");
		builder.append(" ");
		builder.append(CWDateTime.formatDateTime(endDate));
		builder.append("</td>");
		builder.append("</tr>");
		builder.append("<tr><td>&nbsp;</td></tr>");
		
		return builder.toString();
	}

}

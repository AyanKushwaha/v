/* -*- crg -*- */

/*--------------------------------------*/
/* Report with KPIs regarding the use   */
/* os the TOR functionality
/*--------------------------------------*/

options 
   text =  fixed noframe novspace;
   ascwidth = 1000;
end

main:
box
    repeat foreach default_context;
    make
    column
	(text "Number of changed trips: %d", 
	    studio_tor.%tor_plan_num_changed_chains%),
	(text "Percentage changed trips: %d%%", 
	    studio_tor.%tor_plan_degree_changed_chains%),
	(text "Number of changed duties: %d", 
	    studio_tor.%tor_plan_num_changed_duties%),
	(text "Percentage changed duties: %d%%", 
	    studio_tor.%tor_plan_degree_changed_duties%),
	(text "Number of changed legs: %d", 
	    studio_tor.%tor_plan_num_changed_legs%),
	(text "Percentage changed legs: %d%%", 
	    studio_tor.%tor_plan_degree_changed_legs%),
	(text 1x1 ""),
	(text bold "Number of changed leg connections (before/after):"),
	(text "  Deadhead: %d", 
	    studio_tor.%tor_plan_number_of_connections_type_0%),
	(text "  Not in table: %d", 
	    studio_tor.%tor_plan_number_of_connections_type_1%),
	(text "  Identical: %d", 
	    studio_tor.%tor_plan_number_of_connections_type_2%),
	(text "  Start/end of trip: %d",
	    studio_tor.%tor_plan_number_of_connections_type_3%),
	(text "  Start/end of duty - on-duty : %d", 
	    studio_tor.%tor_plan_number_of_connections_type_4%),
	(text "  Start/end of duty - deadhead: %d", 
	    studio_tor.%tor_plan_number_of_connections_type_5%),
	(text "  Within duty - on-duty: %d", 
	    studio_tor.%tor_plan_number_of_connections_type_6%),
	(text "  Within duty - deadhead: %d", 
	    studio_tor.%tor_plan_number_of_connections_type_7%);
    end
end

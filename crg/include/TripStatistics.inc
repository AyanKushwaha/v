/* -*- crg -*- */
/* $Header$ */
/*--------------------------------------*/
/* Simple report with basic statistics	*/
/*--------------------------------------*/

options 
   text =  fixed noframe novspace;
   ascwidth = 1000;
end


gen_stat_pos : box

 repeat 1 times;
 make

    a2t:row (text "");
    a3t:row (text "");

    r2t: row (text " "),*;
    r3t: row (text "Block time"),*;
    r4t: row (text "Duty days"),*;
    r5t: row (text "Block time per calendar day"),*;
    r5bt: row (text "Block time per duty"),*;
    r6t: row (text "Duty periods"),*;
    r7t: row (text "Operating duty periods"),*;
    r8t: row (text "Duty time"),*;
    r9t: row (text "TAFB"),*;
    r10t:row (text "Passive flights"),*;
    r11t:row (text "Passive time"),*;
    r12t:row (text "AC changes"),*;
    r13t:row (text "Hotel nights"),*;
    r14t:row (text "Number of hard duties"), *;
    c1t: column r2t,
		r4t,r6t,r12t,r13t,r14t, (row (text " "),*),
		r3t,r8t,a2t,r9t,(row (text " "),*),
		r5t,r5bt,r7t,(row (text " "),*),
		r10t,r11t,(row (text " "),*),
		a3t;
 relate
    row +c1t,c1t;
 end

 repeat crg_crew_pos.%num_cockpit_pos% + 1 times;
 make

    a2:row (text "");
    a3:row (text "");

    r2: row (text right "%10D",crg_pairing_statistics.%pos_str_vis%);
    r3: row (text right "%10D",
	    crg_pairing_statistics.%total_block_hours%(
		crg_pairing_statistics.%pos_str%));
    r4: row (text right "%10D",
	    crg_pairing_statistics.%total_days%(
		crg_pairing_statistics.%pos_str%));
    r5: row (text right "%10D",
	    crg_pairing_statistics.%total_block_per_day%(
		crg_pairing_statistics.%pos_str%)); 
    r5b: row (text right "%10D",
	    crg_pairing_statistics.%total_block_per_duty%(
		crg_pairing_statistics.%pos_str%)); 
    r6: row (text right "%10D",
	    crg_pairing_statistics.%total_duties%(
		crg_pairing_statistics.%pos_str%));
    r7: row (text right "%10D",
	    crg_pairing_statistics.%total_operating_duties%(
		crg_pairing_statistics.%pos_str%));
    r8: row (text right "%10D",
	    crg_pairing_statistics.%total_duty_time%(
		crg_pairing_statistics.%pos_str%)); 
    r9: row (text right "%10D",
	    crg_pairing_statistics.%total_tafb%(
		crg_pairing_statistics.%pos_str%));
    r10:row (text right "%10D",
	    crg_pairing_statistics.%total_passive_flights%(
		crg_pairing_statistics.%pos_str%));
    r11:row (text right "%10D",
	    crg_pairing_statistics.%total_deadhead_time%(
		crg_pairing_statistics.%pos_str%));
    r12:row (text right "%10D",
	    crg_pairing_statistics.%total_ac_change%(
		crg_pairing_statistics.%pos_str%));
    r13:row (text right "%10D",
	    crg_pairing_statistics.%total_nights%(
		crg_pairing_statistics.%pos_str%));
    r14:row (text right "%10D",
	    crg_pairing_statistics.%total_hard_duties%(
		crg_pairing_statistics.%pos_str%));
    c1: column r2,
		r4,r6,r12,r13,r14, (row (text " "),*),
		r3,r8,a2,r9,(row (text " "),*),
		r5,r5b,r7,(row (text " "),*),
		r10,r11,(row (text " "),*),
		a3;
 relate
    row +c1,c1;
 end

 info1: row -+c1t,-+c1;


    a1: row (text ""),*;

 r1: row (text 20x1 "Active legs "),
	 (text right "%i",
	 crg_pairing_statistics.%compressed_all_number_of_legs%);
 r2: row (text 20x1 "Retimed legs "),
	 (text right "%i",
	 retiming.%num_retimed_legs%);

 column r1,a1,r2,(row (text " "),*),info1;

end


transit: box
 repeat 1 times;
 make
    t1: row (text "                < 1:00   1:00-1:15  1:15-1:30  1:30-1:45  1:45-2:00     >2:00  "), *;

    repeat crg_crew_pos.%num_cockpit_pos% times;
    make
     ta: row (text "Transit %D   %7D    %7D    %7D    %7D    %7D    %7D  ",
	crg_pairing_statistics.%pos_str%,
	crg_pairing_statistics.%cxn_lt_100%(crg_pairing_statistics.%pos_str%),
	crg_pairing_statistics.%cxn_100_115%(crg_pairing_statistics.%pos_str%), 
	crg_pairing_statistics.%cxn_115_130%(crg_pairing_statistics.%pos_str%),
	crg_pairing_statistics.%cxn_130_145%(crg_pairing_statistics.%pos_str%), 
	crg_pairing_statistics.%cxn_145_200%(crg_pairing_statistics.%pos_str%), 
	crg_pairing_statistics.%cxn_gt_200%(crg_pairing_statistics.%pos_str%)),
	*;
    relate
     column +ta,ta;
    end

    column t1,-+ta;
 end
end

patterns: box
    repeat 1 times;
    make
    column
    (text "Flights covered by..."),
    (row (text " "), *),
    (row (text left 10x1 " 0 trips"),*, (text 7x1 right "%i   ",
	    crg_pairing_statistics.%0_complexing_patterns%)),
    (row (text 10x1 " 1 trips"),*, (text 7x1 right "%i   ",
	    crg_pairing_statistics.%1_complexing_patterns%)),
    (row (text 10x1 " 2 trips"),*, (text 7x1 right "%i   ",
	    crg_pairing_statistics.%2_complexing_patterns%)),
    (row (text 10x1 " 3 trips"),*, (text 7x1 right "%i   ",
	    crg_pairing_statistics.%3_complexing_patterns%)),
    (row (text 10x1 " 4 trips"),*,(text 7x1 right "%i   ",
	    crg_pairing_statistics.%4_complexing_patterns%)),
    (row (text 10x1 " 5 trips"),*,(text 7x1 right "%i   ",
	    crg_pairing_statistics.%5_complexing_patterns%)),
    (row (text 10x1 " 6 trips"),*,(text 7x1 right "%i   ",
	    crg_pairing_statistics.%6_complexing_patterns%)),
    (row (text 1x1 "")),
    (row (text 10x1 " Average compl. patterns"),*,
	 (text 7x1 right "%D   ",
format_int(crg_pairing_statistics.%average_complexing_patterns%, 
	    "%v2.d"))),*;
    end
end

sensitivity: box
    repeat 1 times;
    make
    dt1: row (text bold "Turn in"),*;
    dt2: row (text "Number of flights preceded by...\n(flights starting a duty \nhave no preceding flight)"),*;
    d0: row (text 12x1 " 0 flights"),*,(text 7x1 right "%i   ",
	crg_pairing_statistics.%0_turnin_legs_non_duty_start%);
    d1: row (text 12x1 " 1 flights"),*,(text 7x1 right "%i   ",
	crg_pairing_statistics.%1_turnin_legs_non_duty_start%);
    d2: row (text 12x1 " 2 flights"),*,(text 7x1 right "%i   ",
	crg_pairing_statistics.%2_turnin_legs_non_duty_start%);
    d3: row (text 12x1 " 3 flights"),*,(text 7x1 right "%i   ",
	crg_pairing_statistics.%3_turnin_legs_non_duty_start%);
    d4: row (text 12x1 " 4 flights"),*,(text 7x1 right "%i   ",
	crg_pairing_statistics.%4_turnin_legs_non_duty_start%);
    d5: row (text 12x1 " 5 flights"),*,(text 7x1 right "%i   ",
	crg_pairing_statistics.%5_turnin_legs_non_duty_start%);
    d6: row (text 12x1 " 6 flights"),*,(text 7x1 right "%i   ",
	crg_pairing_statistics.%6_turnin_legs_non_duty_start%);

    dt3:row (text bold "Turn out"), *;
    dt4: row (text "Number of flights followed by...\n(flights ending a duty \nhave no following flight)"),*;
    d10:row (text 12x1 " 0 flights"),*,(text 7x1 right "%i   ",
	crg_pairing_statistics.%0_turnout_legs_non_duty_end%);
    d11:row (text 12x1 " 1 flights"),*,(text 7x1 right "%i   ",
	crg_pairing_statistics.%1_turnout_legs_non_duty_end%);
    d12: row (text 12x1 " 2 flights"),*,(text 7x1 right "%i   ",
	crg_pairing_statistics.%2_turnout_legs_non_duty_end%);
    d13:row (text 12x1 " 3 flights"),*,(text 7x1 right "%i   ",
	crg_pairing_statistics.%3_turnout_legs_non_duty_end%);
    d14:row (text 12x1 " 4 flights"),*,(text 7x1 right "%i   ",
	crg_pairing_statistics.%4_turnout_legs_non_duty_end%);
    d15:row (text 12x1 " 5 flights"),*,(text 7x1 right "%i   ",
	crg_pairing_statistics.%5_turnout_legs_non_duty_end%);
    d16:row (text 12x1 " 6 flights"),*,(text 7x1 right "%i   ",
	crg_pairing_statistics.%6_turnout_legs_non_duty_end%);

    sac1: column (text " "),
	dt1,!,(row (text " "), *),dt2,(row (text " "), *),
	d0,d1,d2,d3,d4,d5,d6,(row (text 1x1 "")),*;

    sac2: column (text " "),
	dt3,!,(row (text " "), *),dt4,(row (text " "), *),
	d10,d11,d12,d13,d14,d15,d16,(row (text 1x1 "")),*;
    	
    row sac1,!,sac2;

    end
end


/*
 * Use cost function table in rave module trip_cost 
 * to lookup cost elements and their values 
 */
cost_stat: box
    repeat 2 times;
    /* 1st loop is real cost, 2nd loop is penalties */
    make
        repeat 100 times;
		make
		    if trip_cost.%element_exist_ix1_ix% then
				name: text 50x1 "%D", 
					trip_cost.%element_name_ix1_ix%;
				cost: text right "%D", 
					crg_basic.%print_figure%(trip_cost.%total_element_cost_ix1_ix%);
				element: row name, cost;
		    end
		relate
		    if trip_cost.%element_exist_ix1_ix% then
				column +element, element;
	    	end
		end
	    
		if index(0) = 1 then
		    /* We only want to sum real costs */
		    header: row (text bold "Real Costs");
		    total: row (text bold 50x1 "Total Real Cost"),
			       (column !, 
				  (text right "%D", 
				     crg_basic.%print_figure%(trip_cost.%total_section_cost_ix%)));
			cost: column header, !, -+element, total;
		else
			header: row (text bold "Penalties");
			cost: column (text 1x1 ""), header, !, -+element;
		end
	    
	relate
	    column +cost, cost;
	end
end

crr_rtd_stat: box
    b1: row (box crr_rtd_stat_trip),*;
    b2: row (box crr_rtd_stat_duty),*;
    column b1,b2;
end


crr_rtd_stat_duty: box
 repeat crg_crew_pos.%num_cockpit_pos% times;
 make
   repeat foreach crg_pairing_statistics.duty_num_leg_set;
   sort duty.%num_legs%;
   make
    c1: row (text right "%9D",
	    crg_pairing_statistics.%total_num_duties%(
		crg_pairing_statistics.%pos_str2%)),*;
   relate
    column +c1,c1;
   end

   c2: row (text " "),*;
   a: column c2,-+c1;
 relate
   row +a,a;
 end

 repeat foreach crg_pairing_statistics.duty_num_leg_set;
 sort duty.%num_legs%;
 make
   t: row (text 35x1 "Duties with %i legs", 
	   duty.%num_legs%),*;
 relate
   column +t,t;
 end

 g1: row (text " "),*;
 row (column g1,-+t),-+a;
end


crr_rtd_stat_trip: box
 repeat crg_crew_pos.%num_cockpit_pos% times;
 make
   repeat foreach crg_pairing_statistics.trip_duty_days_set;
   sort trip.%days%;
   make
    c1: row (text right "%4D(%2i%%)",
	    crg_pairing_statistics.%total_num_pairings%(
		crg_pairing_statistics.%pos_str2%),
	    crg_pairing_statistics.%percentage_trips%(
		crg_pairing_statistics.%pos_str2%)),*;
   relate
    column +c1,c1;
   end

   c2:row (text right "%9D",
	    crg_pairing_statistics.%pos_str%),*;
   a: column c2,-+c1;
 relate
   row +a,a;
 end

 repeat foreach crg_pairing_statistics.trip_duty_days_set;
 sort trip.%days%;
 make
   t: row (text 35x1 "Trips with %i days", 
	   trip.%days%),*;
 relate
   column +t,t;
 end

 g1: row (text " "),*;
 row (column g1,-+t),-+a;
end



/* main box */
box
   repeat foreach marked_in_window_main;
   make
    if crg_pairing_statistics.%cabin_stat% then
	b3: column
	    (row (text bold "Complexing patterns")),!,
	    (row (box patterns),*);
	b4: column  
	    (row (text bold "Delay sensitivity")),!,
	    (row (box sensitivity),*);
    else
	b3: row (text ""),*;
	b4: row (text ""),*;
    end

    b14: row (text ""),*;

    b11: row (box cost_stat),*;
    b12: row (box crr_rtd_stat),*;
    b1: row (box gen_stat_pos),*;
    b2: row (box transit),*;

   column 
	(text noframe 1x1 " "),
	(text bold "Costs"),!,b11,page,
	(text noframe 1x1 " "),
	(text bold "General statistics"),!,b1,page,
	(text noframe 1x1 " "),b14,page,
	(text noframe 1x1 " "),
	(text bold "Transit distribution (AC change only)"),!,b2,page,
	(text noframe 1x1 " "),
	(text bold "Trip & Duty statistics"),!,b12,page,
	(text noframe 1x1 " "),b3,page,
	(text noframe 1x1 " "),b4,page,
	(tag "EndOfReport");
  end
end

/* end of file */


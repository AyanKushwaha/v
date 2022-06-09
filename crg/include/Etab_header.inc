/* -*- crg -*- 
 *
 *  $Header$
 *
 *  import: 
 *     %CRG_time_of_list_creation%
 */

etab_header_top: 
box
    repeat foreach default_context;
    make
	hd:column
	    (row
		(text "\/\*\n   %s\n\n   from %s/%s/%s/%s\n   by %s, %s (rule set: %s)\n",
		"NameOfReport", fp_name,fp_version,lp_name,sp_name,
                user, crg_date.%now_abs%, rule_set_name), *);
	column hd, (text noframe 0x1 "");
    end
end

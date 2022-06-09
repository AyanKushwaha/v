/* -*- crg -*- 
*
* $Header$
*
*******************************************************
FAIRNESS REPORTS
--------------------------------------------------------
 
Use:
    This rule file is used by the reports CrewFairness and
    FairnessStatistics.
 
Requirement:
 
--------------------------------------------------------
Author:  Standard Concepts
Created: 19Aug99, September 2004
*******************************************************/

define(NameOfReport, "Fairness Info")
include(CRGInclude/typeset_standard.inc)

define(RowsPerPage,35)

options
  orientation = landscape;
  text = noframe fixed novspace;
end
 
/*
** MAIN BOX
*/

main:
box
    repeat foreach default_context;
    make
        repeat foreach iterators.roster_set;
        make
            if (ix-1) mod RowsPerPage = 0 then
              table_header: row (box page_hdr), *;
            end
            table_item: 
              column (box one_row), page;

            if ix = 1 then
              c: column table_header, PADFULL, table_item;
            elseif (ix-1) mod RowsPerPage = 0 then
              c: column PADSMALL, newpage, PADFULL, table_header,
                 PAD, table_item;
            elseif (ix-1) mod 5  = 0 then
              c: column (text " "), table_item;
            else
              c: column table_item;
            end
        relate
            column +c, c;
        end
	column -+c,(tag "EndOfReport");
    end
end

one_row:
box
	right_crew_info: text 20 "%s", studio_fairness.%crew_name%;
  mid_crew_info: text 10 "%s", report_common.%employee_number%;
	left_crew_info: text 10 right "%D",fairness.%total_cost%;
	repeat 40 times;
	make
	    if fairness.%distribute_ix%,
	       fairness.%crew_can_have_ix% then
		crew_element: box crew_element_with_info;
	    elseif fairness.%distribute_ix% then
		crew_element: box crew_element_cant_have_info;
	    end
	relate
	    if fairness.%distribute_ix% then
		row +crew_element,crew_element;
	    end
	end
	one_crew: row right_crew_info,mid_crew_info,-+crew_element,left_crew_info;
end

/*
* THE PAGE HEADER
*/

page_hdr:
box

    right_hdr_info: text bold 20 "Crew";
    empty_item: text 20 " ";
    align [left,right] right_hdr_info, empty_item;

    mid_hdr_info: text bold 10 "Empl no";
    empty_item2: text 10 " ";
    align [left,right] mid_hdr_info, empty_item2;
    
    left_hdr_info: text bold 10 right "Total";
    empty_item3: text 10 " ";
    align [left,right] left_hdr_info, empty_item3;

    repeat 40 times;
    make
        if fairness.%distribute_ix%,fairness.%is_rel_ix% then
            element: text bold 25 "%s",fairness.%text_ix%;
            empty_item: text 25 " ";
        elseif fairness.%distribute_ix% then
            element: text bold 20 "%s",fairness.%text_ix%;
            empty_item: text 20 " ";
	end
        align [left,right] element, empty_item;
    relate
        if fairness.%distribute_ix% then
	    row +element,element;
	end
    end
    hdr: row right_hdr_info,mid_hdr_info,-+element,left_hdr_info;
end

/*
** THE BOX FOR ONE CREW/ONE FAIR SHARE ELEMENT
**  There are 2 different boxes:
**	- With satisfaction values
**	- With information that the crew can/should not have this fair
**	  share element
*/

crew_element_with_info:
box 
    if fairness.%is_rel_ix% then
       text 25 "%s (%s) %i"
	   ,default(studio_fairness.%roster_value_ix_txt%,"0")
	   ,default(studio_fairness.%personal_target_ix_txt%,"0")
	   ,default(studio_fairness.%cost_ix%,0);
    else 
       text 20 "%s (%s) %i"
	   ,default(studio_fairness.%roster_value_ix_txt%,"0")
	   ,default(studio_fairness.%personal_target_ix_txt%,"0")
	   ,default(studio_fairness.%cost_ix%,0);
    end
end

crew_element_cant_have_info:
box
    if fairness.%is_rel_ix% then
	text 25 "-- (--) 0"; 
    else 
	text 20 "-- (--) 0"; 
    end
end
/* end of file */

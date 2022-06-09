/* -*- crg -*- 
*
* $Header$
*
*******************************************************
FAIRNESS REPORTS
--------------------------------------------------------
 
Use:
    This rule file is used by the reports CrewFairnessOutput
 
Requirement:
 
--------------------------------------------------------
Author:  Erik Gustafsson
Created: 11Dec06
*******************************************************/

define(NameOfReport, "Fairness Info")
include(CRGInclude/common_defs.inc)

options
    ascwidth = 400;
    ascii = asctrimpage;
    text = noframe fixed novspace;
end

/*
** MAIN BOX
*/
main:
box
  repeat foreach default_context;  
  make
    r0: row (text "%s", NameOfReport),*;
    r1: row (text "%s",	if is_dated_mode then "Planning Period:" else "Standard Period:"),(text "%s  ", crg_date.%print_pp%),
	    (text "Rule Set:"),(text "%s  ", rule_set_name),
	    (text "Plan:"),(text "%s/%s/%s/%s  ", fp_name,fp_version,lp_name,sp_name),*;
	if crg_comment <> "" then
	    r2: row (text max 80x2 wbreak "Comment: %s", crg_comment),*;
	end
    hd0: column r0,r1,r2, !!;
    repeat 40 times;
    make
      if fairness.%distribute_ix% then
        element: row (text ";%s value;target;cost",fairness.%text_ix%);
      end
      relate
      if fairness.%distribute_ix% then
        row +element,element;
      end
    end
    hdr: row (text "Crew"),(text ";Empno"),-+element,(text ";Total"),*;
       
    repeat foreach iterators.roster_set;
    make
      left_crew_info: text "%s", studio_fairness.%crew_name%;
      mid_crew_info: text ";%s", report_common.%employee_number%;
	    right_crew_info: text ";%D",fairness.%total_cost%;
      repeat 40 times;
      make
        if fairness.%distribute_ix% then
          crew_element: box crew_element_with_info;
        end
        relate
        if fairness.%distribute_ix% then
          row +crew_element,crew_element;
        end
      end
      one_crew: column (row left_crew_info,mid_crew_info,-+crew_element,right_crew_info,*), page;
      relate
      column +one_crew, one_crew;
    end
    column hd0,hdr, -+one_crew;
  end
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
    if fairness.%crew_can_have_ix% then
        text ";%s;%s;%i"
	   ,default(studio_fairness.%roster_value_ix_txt%,"0")
	   ,default(studio_fairness.%personal_target_ix_txt%,"0")
	   ,default(studio_fairness.%cost_ix%,0);
    else 
	text ";-;-;0";
    end
end

/* end of file */

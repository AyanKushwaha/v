#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# By Johan Winberg STODI
#  -Report to get FTEContribution for each crew.
#  -Default saved at samba

# The report can be run by right click in roster view.

import Cui, Variable
import carmensystems.rave.api as r
import carmstd.studio.cfhExtensions as cfhExtensions
import os.path
import os
import shutil
import carmensystems.publisher.api as p
from datetime import timedelta
from datetime import date
from datetime import datetime
import Tkinter,tkFileDialog



#*****************************************************************
#*****************************************************************

class Report(p.Report):
    def create(self): 

        myname = os.environ.get("USER")
        Homepath = "/samba-share/reports/FTECalcOutput/"
        #timeStamp = str(datetime.now().date())
        lp, sp = r.eval('global_lp_name','global_sp_name')
        reportName = "FTECalcOutput_" + str(lp) + "_" + str(sp) 
        root = Tkinter.Tk()
        root.withdraw()
        myFormats = [('CSV file','*.csv'),('Text file','*.txt'),]
        fileOut = tkFileDialog.asksaveasfile(parent=root, initialdir = Homepath, initialfile = reportName, mode='w', filetypes=myFormats, title="Save the output text file as...")
        extension = fileOut.name.split('/')[-1][-3:]



#Definitions of Roster values       
        R_VALUES = ['report_typeofduty.%empno%','report_typeofduty.%fullname%', 'report_common.%format_period_start%','report_typeofduty.%rank%','report_typeofduty.%crew_category%',
                     'report_typeofduty.%homebase%','report_typeofduty.%group_at_pp_start%','report_typeofduty.%pt_factor_pp_start%',
                    'report_typeofduty.%region%', 'report_typeofduty.%ac_qual%','report_typeofduty.%is_temporary%','report_typeofduty.%is_mff%','report_typeofduty.%fte_calculation%',
                    'report_typeofduty.%block_time_calendar_month%','report_typeofduty.%block_time_calendar_month_long_haul%', 
                    'report_typeofduty.%long_haul_legs_in_calendar_month%', 'report_typeofduty.%short_haul_legs_in_calendar_month%',
                    'report_typeofduty.%instructor_qual_pp_start%', 'report_typeofduty.%sim_instr_duties_in_calendar_month%', 'report_typeofduty.%nr_lifus_legs_as_instr_in_calendar_month%',
                    'report_typeofduty.%nr_lc_legs_as_instr_in_calendar_month%']
                        
        
        roster_expr = r.foreach(r.iter('iterators.roster_set',
                                       where='fundamental.%is_roster%'), *R_VALUES)
        rosters, = r.eval('default_context',roster_expr)
        header_is_set = False
        
        for (ix, crew_id, name, date, rank, crew_category, homebase, group, pt_factor, region, ac_qual, temp_crew, is_mff, fte_calc, 
             block_time, block_time_lh, legs_lh, legs_sh, instr_qual, sim_instr, lifus_instr, lc_instr) in rosters:


            if not header_is_set:
                L = ["CrewID","Name", "Date","Rank","CrewCategory", "Homebase", "Group", "PTFactor", "Region", "AcQual","IsResourcePool","IsMFF", "FTEContribution",
                     "BLHinMonth", "LH_BLHinMonth", "LH_legs_in_month", "SH_legs_in_month", "InstructorQual", "SIMinstrDuties", "LIFUSinstrLegs", "LCinstrLegs"]                   
                     
                header_is_set = True

            L.append("\n" + crew_id)
            L.append(name)
            L.append(date)
            L.append(rank)
            L.append(crew_category)
            L.append(homebase)
            L.append(str(group))
            L.append(str(pt_factor))
            L.append(region)
            L.append(str(ac_qual))
            if temp_crew:
                L.append(str("RP"))
            else:
                L.append(str(" "))
            if is_mff:
                L.append(str("MFF"))
            else:
                L.append(str(" "))
            L.append(str(fte_calc))
            L.append(str(block_time))
            L.append(str(block_time_lh))
            L.append(str(legs_lh))
            L.append(str(legs_sh))
            L.append(str(instr_qual))
            L.append(str(sim_instr))
            L.append(str(lifus_instr))
            L.append(str(lc_instr))
            
    
        if extension == "txt":
            pad = "\t"
        else:
            pad = ";"

       #print "L", L
        fileOut.writelines(pad.join(L))
        fileOut.close()
        filename = fileOut.name.split('/')[-1]
        cfhExtensions.show("Report: " + filename + " written to " + Homepath + ", done!") 

# End of file

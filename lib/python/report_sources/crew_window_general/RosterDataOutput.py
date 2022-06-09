#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# 2018-01-15 Updated and renamed by lars Andersson, SAS
#  -Renamed from "TypeOfDuty to "RosterDataOutput" to avoid mistake with database version of "TypeOfDuty"
#  -Default saved at samba
#  -Unused columns are removed, some bugs fixed and new columns added
# 
# To run report in tracking studio add these rows:
#""" `TypeOfDuty` ^RuleSetLoaded _A REDO TRANS
#    f.exec CuiCrgDisplayTypesetReport(gpc_info, CuiWhichArea, "window", "crew_window_general/SWE_TypeOfDuty.py", 0)"""
# under the section "Menu CrewGeneralReportMenu" in the file:
# menu_scripts/menus/customization/application/MainDat24CrewCompMode2_Tracking.menu
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


####### FUNCTIONS PART ##########

def str2date(d):
    x = str(d).split('-')
    YYYY = x[0]
    MM = x[1]
    DD = x[2]
    return date(int(YYYY), int(MM), int(DD))

def in_def_area(d, start_para, end_para):
    return (str2date(d) >= str2date(start_para) and
    str2date(d) < str2date(end_para))

def jump2date(d, i):
    y = str2date(d)
    xx = timedelta(days=i)
    next_d  = y + xx
    return str(next_d)


def diff_date(d1,d2):
    if d1 == "-999" or d2 == "-999":
        return -999
    diff =  str2date(d2)-str2date(d1)
    return diff.days

#*****************************************************************
#*****************************************************************

class Report(p.Report):
    def create(self): 

        myname = os.environ.get("USER")
        Homepath = "/samba-share/reports/RosterDataOutput/"
        #timeStamp = str(datetime.now().date())
        lp, sp = r.eval('global_lp_name','global_sp_name')
        reportName = "RosterDataOutput_" + str(lp) + "_" + str(sp) 
        root = Tkinter.Tk()
        root.withdraw()
        myFormats = [('CSV file','*.csv'),('Text file','*.txt'),]
        fileOut = tkFileDialog.asksaveasfile(parent=root, initialdir = Homepath, initialfile = reportName, mode='w', filetypes=myFormats, title="Save the output text file as...")
        extension = fileOut.name.split('/')[-1][-3:]

#Definitions of Leg values
#Used in DutyAsString column        
        L_VALUES = ['report_meal.%meal_code%',
                    'leg.%flight_name%',
                    'duty_code.%leg_code%']
        leg_expr = r.foreach(r.iter('iterators.leg_set'), *L_VALUES)

#Definitions of Duty values    
        D_VALUES = ['report_typeofduty.%start_date_lt%',
                    'report_typeofduty.%main_duty_code_at_date%',
                    'report_typeofduty.%main_group_code_at_date%',
                    'report_typeofduty.%next_duty_codes_at_date%',
                    'report_typeofduty.%first_duty_start_at_date%',
                    'report_typeofduty.%start_lt%',
                    'report_typeofduty.%end_lt%',                  
                    'report_typeofduty.%duty_days%',
                    'report_typeofduty.%days_to_next_real_duty%',
                    'report_typeofduty.%space_to_next_duty_date%',
                    'report_typeofduty.%is_long_haul_over_midnight%',
                    'report_typeofduty.%duty_ends_after_midnight_not_lh%',
                    'report_typeofduty.%trips_last_duty_is_lh%',
                    'report_typeofduty.%is_last_in_trip%',
                    'report_typeofduty.%date_is_bought%',
                    'bought_days.%duty_bought_type%',
                    'report_typeofduty.%rank_duty_start%',
                    'crew.%part_time_factor_duty_start%',
                    'report_typeofduty.%part_il_fact_at_date%', 
                    'report_typeofduty.%base_at_duty_start%',
                    'report_typeofduty.%region_at_date%',
                    'report_typeofduty.%ac_quals_at_date%',
                    'report_typeofduty.%nof_next_duties_at_date%', #Remove?               
                    'report_typeofduty.%next_duty_start%',
                    'report_typeofduty.%next_duty_code%',
                    'report_typeofduty.%next_duty_groupcode%',
                    'report_typeofduty.%long_haul_at_date%',
                    'crg_duty_points.%fdp_time%',                                   #only FDP
                    'crg_info.%_duty_time%',
                    'report_typeofduty.%duty_first_day%',
                    'report_typeofduty.%duty_second_day%',
                    'report_typeofduty.%block_time_at_date%',
                    'report_typeofduty.%blh_day1%',
                    'report_typeofduty.%blh_day2%',
                    'report_typeofduty.%f_or_v_at_date%',
                    'crew.%agreement%',
                    'freedays.%req_freedays_in_month%',
                    'report_typeofduty.%is_extended_fdp%',
                    'oma16.%block_time_in_last_28_days_end_day%',
                    'duty_period.%is_split%',
                    'duty.%is_flight_duty%',
                    'report_typeofduty.%report_cost_of_a_roster_day%',
                    'crg_roster.%layover_info%']
        
        D_VALUES.append(leg_expr)
            
        duty_expr = r.foreach(r.iter('iterators.duty_set'), *D_VALUES)

#Definitions of Roster values       
        R_VALUES = ['report_typeofduty.%empno%',
                    'report_typeofduty.%format_per_start%',
                    'report_typeofduty.%format_per_end%',
                    'fp_name',
                    'fp_version',
                    'lp_name',
                    'sp_name',
                    'rule_set_name']

        R_VALUES.append(duty_expr)
        
        roster_expr = r.foreach(r.iter('iterators.roster_set',
                                       where='fundamental.%is_roster%'), *R_VALUES)
        rosters, = r.eval('default_context',roster_expr)
        header_is_set = False
        
        for (ix,
             idz,
             start_para,
             end_para,
             fp_name,
             fp_version,
             lp_name,
             sp_name,
             rule_set_name,
             my_duties) in rosters:

# Upper case letter i comment are corresponding to column in Excel
# BBB must syncronize with bbb section below
            if not header_is_set:
                L = ["Empno", #A
                     "Rank", #B
                     "AcQual", #C
                     "PartTime", #D
                     "PartILfactor", #E
                     "Base", #F
                     "Region", #G
                     "Date", #H
                     "MainAct", #I
                     "MainGrpAct", #J
                     "BLHInDutypass", #K
                     "FDP", #L
                     "DutyTimeInDutypass", #M
                     "DutyAsString",
                     "LayoverStation",#N 
                     "DutyStartLT", #O
                     "LHorSH", #P
                     "Bought", #Q
                     "Group", #R
                     "Agreement", #S
                     "Req_F", #T
                     "Extension", #U
                     "BLH_In_28d", #V
                     "TripCost", #W
                     "Plan: "+ fp_name + "/" + fp_version +"/"+ lp_name +"/"+ sp_name + " ruleset: "+ rule_set_name] #X

                header_is_set = True
            second_duty = False
            skip_next = False
            skip_loops = 0
            new_crew = True
            for indx, (ig,
                 startDate,
                 dcode,
                 group_code,
                 next_duty_codes_at_date,
                 first_start_at_date,
                 start_lt,
                 end_lt,
                 dutyDays,
                 days_to_next_real_duty,
                 space_to_next_duty_date,
                 is_long_haul_over_midnight,
                 after_midnight,
                 trips_last_duty_is_lh,
                 is_last_in_trip,
                 is_bought,
                 fx_code,
                 rank_at_date,
                 pt_fact_at_date,
                 pt_IL_fact,
                 base_at_date,
                 region_at_date,
                 qual_at_date,
                 nof_next_duties, 
                 next_duty_startLT,
                 next_duty_code,
                 next_duty_groupcode,
                 long_haul_at_date,
                 fdp,
                 dp,
                 duty_day1,
                 duty_day2, 
                 block_time_at_date,
                 blh_day1, 
                 blh_day2, 
                 group,
                 agreement,
                 req_f_in_month,
                 is_subq_extension,
                 blh_in_28d,      
                 is_split,
                 fltDuty,
                 dayCost,
                 layover_station,
                 my_legs) in enumerate(my_duties):

                D = startDate
                duty_day1_sum_next = duty_day1
                blh_day1_sum_next = blh_day1
                #debug                
                #print D
                #print indx
                #print len(my_duties)
                #print is_split

                if D >= start_para and D <= end_para:
                    if indx < len(my_duties)-1:
                       next_duty = my_duties[indx+1]
                       if D==next_duty[1] and not is_split:
                           duty_day1_sum_next = duty_day1 + next_duty[31]
                           blh_day1_sum_next = blh_day1 + next_duty[31]

                if skip_loops > 0: #duplets of duty allready taken care of.
                    skip_loops = skip_loops - 1
                    continue
                skip_loops = nof_next_duties

# Create a string including dutycode, mealcode and flt_nr
                prev_leg_code = ""
                all_acts = "-"
                S = ""           
                for (ig, meal_code, flts, duty_code) in my_legs: #Add duty prefix
                    S = S + (str(meal_code) + " " + duty_code + str(flts) + " ")
                    all_acts = S


#bbb section correspond with section BBB above
                if in_def_area(D, start_para, end_para): #defined by month loaded in CCT or pp_start month in CCR.
                    L.append("\n"+idz)
                    L.append(rank_at_date)
                    L.append(qual_at_date)
                    L.append(str(pt_fact_at_date))
                    L.append(str(pt_IL_fact))
                    L.append(base_at_date)
                    L.append(region_at_date)
                    L.append(D)
                    L.append(dcode)
                    L.append(group_code)
                    L.append(str(block_time_at_date))
                    if fltDuty:
                        L.append(str(fdp))
                    else:
                        L.append("00:00")
                    L.append(str(dp))
                    L.append(all_acts)
                    if layover_station == "":
                        L.append("-")
                    else:
                        L.append(layover_station)
                    if fltDuty:
                        L.append(str(first_start_at_date))
                    else:
                        L.append("-")
                    L.append(long_haul_at_date)
                    if is_bought:
                        L.append(fx_code)
                    else:
                        L.append("-")
                    L.append(group)
                    L.append(str(agreement))
                    L.append(str(req_f_in_month))
                    if is_subq_extension:
                        L.append("yes")
                    else:
                        L.append("no")
                    L.append(str(blh_in_28d))
                    L.append(str(dayCost))
                else: #Date is not within defined area. 
                    if  str2date(D) > str2date(end_para):
                        break #if after defined area

                #print D + " dutydays=" + (str(dutyDays))
                #print is_split
                # days_to_next_real_duty is used fpr the special case when LA92 IL7 might
                #run over midnight but is consider as one duty by rave. 
                if dutyDays > 1: #(dutyDays > 2 or (dutyDays > 1 and days_to_next_real_duty > 0)): #If duty runs over several days (not co after midnight),
                                                      #make a print for each day. LH after midnight counts as 2 duty days.
                    i = 1
                    for i in range(1,dutyDays):
                        D = jump2date(D,1)
                        #print "loop" + (str(D))
                        if in_def_area(D, start_para, end_para):
                            L.append("\n"+idz)
                            L.append(rank_at_date)
                            L.append(qual_at_date)
                            L.append(str(pt_fact_at_date))
                            L.append(str(pt_IL_fact))
                            L.append(base_at_date)
                            L.append(region_at_date)
                            L.append(D)
                            L.append(dcode)
                            L.append(group_code)
                            L.append("00:00")         #block_time_at_date. We only count block_time to duty's start date
                            L.append("00:00")         #FDP  We only count_time to duty's start date
                            L.append("00:00")         #duty_time_at_date. We only count duty_time to duty's start date
                            if dcode == "FLT":
                                L.append("-")
                            else:
                                L.append(all_acts)
                            L.append("-")
                            L.append("-")             #str(first_start_at_date))
                            L.append(long_haul_at_date)
                            L.append("-")             #is_boughtT
                            L.append(group)
                            L.append(str(agreement))
                            L.append(str(req_f_in_month))
                            if is_subq_extension:
                                L.append("yes")
                            else:
                                L.append("no")
                            L.append(str(blh_in_28d))
                            L.append(str(dayCost))
                            #L.append("longDuty")
                    if is_long_haul_over_midnight and diff_date(D,next_duty_startLT)== 0:
                        skip_loops = 1
                #IF space to next duty
                #if next_duty_startLT != "-999": #If not last duty in subplan
                #print "space to next duty date = " + str(space_to_next_duty_date)
                if space_to_next_duty_date != -999 : #space_to_next_duty_date
                    #if is_long_haul_over_midnight:
                    space = space_to_next_duty_date  #diff_date(D,next_duty_startLT)
                    
                    D = jump2date(D,1)
                    while space > 1: #If space between duties, fill in the blanks
                        space = space -1
                        if in_def_area(D, start_para, end_para):
                            L.append("\n"+idz)
                            L.append(rank_at_date)
                            L.append(qual_at_date)
                            L.append(str(pt_fact_at_date))
                            L.append(str(pt_IL_fact))
                            L.append(base_at_date)
                            L.append(region_at_date)
                            L.append(D)
                            if not is_last_in_trip and next_duty_code == "FLT":
                                #print "Slipping " + D
                                L.append("SLP")
                                L.append("FLT")
                                L.append("00:00")   #block_time_at_date
                                L.append("00:00")   #FDP _at_date
                                L.append("00:00")   #Dutytime
                                L.append("-")#all_actsB
                                if layover_station == "":
                                    L.append("-")
                                else:
                                    L.append(layover_station)
                                L.append("-")       #str(first_start_at_date))
                                L.append(long_haul_at_date)
                                L.append("-")       #is_bought
                                L.append(group)
                                L.append(str(agreement))
                                L.append(str(req_f_in_month))
                                if is_subq_extension:
                                    L.append("yes")
                                else:
                                    L.append("no")
                                L.append(str(blh_in_28d))
                                L.append(str(dayCost))
                            else:
                                L.append("-")     #task code
                                L.append("-")     #task group
                                L.append("00:00") #block_time_at_dateh
                                L.append("00:00") #FDP
                                L.append("00:00") #Dutytime
                                L.append("-")     #all_acts
                                if layover_station == "":
                                    L.append("-")
                                else:
                                    L.append(layover_station)
                                L.append("-")     #first_start_at_date
                                L.append("-")     #long_haL.append("00:00")      
                                L.append("-")     #is_bought
                                L.append(group)   #group
                                L.append(str(agreement))
                                L.append(str(req_f_in_month))
                                if is_subq_extension:
                                    L.append("yes")
                                else:
                                    L.append("no")
                                L.append(str(blh_in_28d))
                                L.append(str(dayCost))
         
                        D = jump2date(D,1)
                else:
                    print "-999 D = " +D
                    D = jump2date(D,1)
                    while in_def_area(D, start_para, end_para):
                        L.append("\n"+idz)
                        L.append(rank_at_date)
                        L.append(qual_at_date)
                        L.append(str(pt_fact_at_date))
                        L.append(str(pt_IL_fact))
                        L.append(base_at_date)
                        L.append(region_at_date)
                        L.append(D)
                        L.append("-")    #code
                        L.append("-")    #group
                        L.append("00:00") #block_time_at_date
                        L.append("00:00") #FDP
                        L.append("00:00") #Dutytime
                        L.append("-")    #all_acts
                        if layover_station == "":
                            L.append("-")
                        else:
                            L.append(layover_station)                    
                        L.append("-")    #first_start_at_date
                        L.append("-")    #long_haul_at_date
                        L.append("-")    #is_bought
                        L.append(group)  #group
                        L.append(str(agreement))
                        L.append(str(req_f_in_month))
                        if is_subq_extension:
                            L.append("yes")
                        else:
                            L.append("no")
                        L.append(str(blh_in_28d))
                        L.append(str(dayCost))
                        D = jump2date(D,1)

    
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

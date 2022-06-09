#!/usr/bin/env python
#
# by Johan Winberg STODI 2021-03-24
# Report on all Pairings in window.
# Used to get different properties on duties in pairings which are used to present different KPIs in Power BI.
# The report is default saved on Sambaserver in directory "samba-share/reports/PairingsKPIOutput"
#

import Cui
import carmensystems.rave.api as r
import carmstd.studio.cfhExtensions as cfhExtensions
import os.path
import os
import shutil
import carmensystems.publisher.api as p
from datetime import datetime
import Tkinter,tkFileDialog
import glob
from _ast import If


#*****************************************************************
#*****************************************************************

class PairingsKPIOutput(p.Report):
    def create(self):
        if 'SASDEV' in os.getenv("CARMSYSTEMNAME", ""):
           username = os.environ.get("USER")
           Homepath = "/home/" + username
        else:
           samba_path = os.getenv('SAMBA', "/samba-share")
           Homepath = samba_path + "/reports/PairingsKPIOutput"
        #timeStamp = str(datetime.now().date())
        #local and subplan name
        lp, sp = r.eval('global_lp_name','global_sp_name')
        reportName = "PairingsKPI_" + str(lp) + "_" + str(sp)

        root = Tkinter.Tk()
        root.withdraw()
        myFormats = [
            ('CSV file','*.csv'),
            ('Text file','*.txt')
            ]
        fileOut = tkFileDialog.asksaveasfile(parent=root, initialdir = Homepath, initialfile = reportName, mode = 'w', filetypes=myFormats, title="Save the output text file as...")
        # If process is cancelled then return
        if fileOut is None:
           return

        #Choose file type
        extension = fileOut.name.split('/')[-1][-3:]

#A. Imported values from Rave code. To be given name and used later in the report. Name must be given in the same order as they are imported.
        D_VALUES = ['report_common.%trip_start_day_formatted%','report_common.%trip_id%','trip.%days%','report_common.%duty_start_day_formatted%', 'report_common.%rank_based_on_comp%',
                    'report_common.%crew_cat_based_on_comp%','trip.%homebase%', 
                    'trip.%region%','report_common.%duty_ac_family%','report_common.%number_of_deadheads%','report_common.%number_of_active_legs%',
                    'report_common.%duty_days%','report_common.%trip_num_layovers%','report_common.%layover_info%','duty.%block_time_sched_active_legs%','crg_info.%_duty_time%','crg_info.%_rest_time%','rest.%duty_minimum_time%', 
                    'report_common.%time_above_min_rest_after_dp%','report_common.%rest_intervals%', 'report_common.%fdp_time%','oma16.%max_daily_fdp%',
                    'report_common.%time_to_max_fdp%',"report_common.%fdp_intervals%", 'oma16.%is_extended_fdp%','trip.%name%','duty.%start_hb%', 'duty.%end_hb%',
                    'duty.%is_last_in_trip%','duty.%is_first_in_trip%','duty_period.%is_split%','report_common.%is_first_lh_duty%','trip.%is_long_haul%']
                    
                    
                    
        duty_expr = r.foreach(r.iter('iterators.duty_set'), *D_VALUES)


        trip, = r.eval('default_context',duty_expr)
        header_is_set = False

#A. Valuenames for all Rave variables previously imported in this report. Must be in the same order as: "A. Imported values.."
        for (ix, trip_date,trip_id, trip_days, duty_date, rank, crew_cat, base, region, ac_fam, deadheads, active_legs, duty_days, layovers, layover_station, blh, duty_hrs, actual_rest,
             min_rest, time_to_min_rest, rest_intervals, fdp, maxfdp, time_to_max_fdp, fdp_interval, is_extended, trip_name, duty_start_hb, duty_end_hb, is_last_duty,
             is_first_duty, is_split, is_first_lh, is_lh) in trip:

            if not header_is_set:

#B. Header name for each column in the outputfile
                L = ["TripStartDate","TripID","TripDays", "DutyStartDate","Rank","CrewCategory", "Homebase", "Region","ACFamily", "Deadheads", "ActiveLegs", "DutyDays","Layovers",
                     "LayoverStation", "BlockTime", "DutyTime", "RestTime", "MinimumRest", "Timetominrest","RestIntervals", "FDPTime", "MaxFDP","TimetoMaxFDP","FDPInterval", 
                     "Extension", "TripName", "DutyStartHB", "DutyEndHB"]

                header_is_set = True

#B. Imported values writes on every row in outputfile. One row for each duty. Must be in the same order as the header
            L.append("\n" + str(trip_date))
            L.append(str(trip_id))
            if is_lh and is_first_lh:
                L.append(str(trip_days))
            elif is_last_duty and not is_lh:
                L.append(str(trip_days))
            else:
                L.append("")
            L.append(str(duty_date))
            L.append(str(rank))
            L.append(str(crew_cat))
            L.append(str(base))
            L.append(str(region))
            L.append(str(ac_fam))
            L.append(str(deadheads))
            L.append(str(active_legs))
            L.append(str(duty_days))
            if is_last_duty:
                L.append(str(layovers))
            else:
                L.append(str("0"))
            L.append(str(layover_station))
            L.append(str(blh))
            L.append(str(duty_hrs))
            if not is_last_duty:
                L.append(str(actual_rest))
            else:
                L.append(str("00:00"))
            if not is_last_duty:
                L.append(str(min_rest))
            else:
                L.append(str("00:00"))
            if not is_last_duty and not is_split:
                L.append(str(time_to_min_rest))
            else:
                L.append(str("00:00"))
            L.append(str(rest_intervals))   
            L.append(str(fdp))
            L.append(str(maxfdp))
            L.append(str(time_to_max_fdp))
            L.append(str(fdp_interval))
                     
            if is_extended:
                 L.append("True")
            else:
                L.append("False")
            if trip_name == "MANKO":
                L.append(str(trip_name))
            else:
                L.append("ROSTER")
            L.append(str(duty_start_hb))
            L.append(str(duty_end_hb))
        if extension == "txt":
            pad = "\t"
        else:
            pad = ";"

        fileOut.writelines(pad.join(L))
        fileOut.close()
        filename = fileOut.name.split('/')[-1]
        filename = filename.encode('latin1')
        cfhExtensions.show("Report: " + reportName + " written to " + filename + ", done!")

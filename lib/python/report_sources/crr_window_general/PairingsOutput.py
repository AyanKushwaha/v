#!/usr/bin/env python
#
# Av Lars Andersson STOOJ 2016-10-10
# Updated version By Lars Andersson 2017-12-18
# Report on all Pairings in window.
# Used to make it possible to export parings and make it possible to measure crew and AC cnx.create reports in common applications.
# The report is default saved on Sambaserver in dirctory "samba-share/reports/PairingsOutput"
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


#*****************************************************************
#*****************************************************************

class PairingsOutput(p.Report):
    def create(self):

        Homepath = "/samba-share/reports/PairingsOutput"
        lp, sp = r.eval('global_lp_name','global_sp_name')
        reportName = "Pairings_" + str(lp) + "_" + str(sp)

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
        L_VALUES = ['trip.%start_hb%','trip_id','assigned_crew_position_1','assigned_crew_position_2','assigned_crew_position_3','assigned_crew_position_5','assigned_crew_position_6',
                    'assigned_crew_position_7','departure','departure_airport_name','flight_number','deadhead','aircraft_type','arrival','arrival_airport_name','leg.%connection_time%',
                    'aircraft_change','leg.%block_time%','leg.%region%','crg_trip.%next_fltnr_in_trip%','trip.%days%','trip_cost.%trip_real_costs%','trip_cost.%trip_soft_costs%','fdp.%time%','oma16.%max_daily_fdp%',
                    'oma16.%is_extended_fdp%','crg_info.%_duty_time%','crg_info.%_trip_time%','fdp.%is_last_leg_in_fdp%','leg.%is_last_in_trip%','leg.%is_first_in_trip%',
                    'leg.%is_last_in_duty%','trip.%homebase%','rest.%minimum_time%','crg_info.%_rest_time%']
        leg_expr = r.foreach(r.iter('iterators.leg_set'), *L_VALUES)


        trip, = r.eval('default_context',leg_expr)
        header_is_set = False

#A. Valuenames for all Rave variables previously imported in this report. Must be in the same order as: "A. Imported values.."
        for (ix, date, tripId, fc, fp, fr, ap, AS, ah, dep_time, dep_stn, flt_nbr, dh, ac, arr_time, arr_stn,cnx, ac_cng, BLH,
             region, nextLeg, tripLen, pair_cost, post_pair_cost, FDP, maxFDP, is_extension, duty_in_duty, duty_in_trip, last_in_fdp,
             last_leg_in_trip, first_leg_in_trip, last_leg_in_duty, base, minRest, actRest,) in trip:
            if not header_is_set:

#B. Header name for each column in the outputfile
                L = ["TripStartLocalHB","Trip_ID","FC","FP","FR","AP","AS","AH","DepUTC","DepStn","FltNr","Deadhead",
                     "AcType","ArrUTC","ArrStn","Cnx","AC_CNG","BLH","LegRegion", "Next_Leg", "DutyInDuty","FDP","MaxFDP","Extension",
                     "MinRest","ActRest","TripDays","HomeBase","DutyInTrip","PairingCost","PostPairingCost"]
                header_is_set = True

#B. Imported values writes on every row in outputfile. One row for each flt. Must be in the same order as the header
            if first_leg_in_trip:
                L.append("\n" + str(date))
            else:
                L.append("\n" + ("-"))
            L.append(str(tripId))
            L.append(str(fc))
            L.append(str(fp))
            L.append(str(fr))
            L.append(str(ap))
            L.append(str(AS))
            L.append(str(ah))
            L.append(str(dep_time))
            L.append(str(dep_stn))
            L.append(str(flt_nbr))
            L.append(str(dh))
            L.append(str(ac))
            L.append(str(arr_time))
            L.append(str(arr_stn))
            L.append(str(cnx))
            L.append(str(ac_cng))
            L.append(str(BLH))
            L.append(str(region))

            if last_leg_in_duty:
                L.append(str("-"))
                L.append(str(duty_in_duty))
            else:
                L.append(str(nextLeg))
                L.append("-")
            if last_in_fdp:
                L.append(str(FDP))
                L.append(str(maxFDP))
                if is_extension:
                    L.append("yes")
                else:
                    L.append("no")
            else:
                L.append("-")
                L.append("-")
                L.append("-")
            if last_leg_in_duty:
                L.append(str(minRest))
                L.append(str(actRest))
            else:
                L.append("-")
                L.append("-")
            if first_leg_in_trip:
                L.append(str(tripLen))
            else:
                L.append("-")
            L.append(str(base))
            if last_leg_in_trip:
                L.append(str(duty_in_trip))
                L.append(str(pair_cost))
                L.append(str(post_pair_cost))
            else:
                L.append("-")
                L.append("-")
                L.append("-")

        if extension == "txt":
            pad = "\t"
        else:
            pad = ";"

        fileOut.writelines(pad.join(L))
        fileOut.close()
        filename = fileOut.name.split('/')[-1]
        filename = filename.encode('latin1')
        cfhExtensions.show("Report: " + reportName + " written to " + filename + ", done!")

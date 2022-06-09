"""
 $Header$
 
 Plan Statistics
 
 ...
   
 Created:    March 2007
 By:         Erik Gustafsson, Jeppesen Systems AB

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from RelTime import RelTime

# constants =============================================================={{{1
TITLE = 'Plan Statistics'

class PlanStatistics(SASReport):
    
    def create(self, context='default_context'):
        # Basic setup
        SASReport.create(self, TITLE, orientation=PORTRAIT, usePlanningPeriod=True)

        # Get Planning Period start and end
        pp_days, = R.eval('pp.%days%')
        pp_days = pp_days*1.0
        pp_days = max(1.0,pp_days)
                
        # Assigned production
        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where='fundamental.%is_roster%'),
            'report_common.%crew_rank%',
            'report_common.%crew_homebase%',
            'report_common.%crew_is_long_haul_pp_start%',
            'report_common.%crew_flight_days_LH%',
            'report_common.%crew_flight_days_SH%',
            'report_common.%crew_block_time_LH%',
            'report_common.%crew_block_time_SH%',
            'report_common.%crew_deadheads%',
            'report_common.%crew_deadhead_block_time%',
            'report_common.%crew_duty_time%',
            'report_common.%crew_duty_time_no_night_upg%',
            'report_common.%crew_layovers%',
            'report_common.%crew_training_days%',
            'report_common.%crew_vacation_days%',
            'report_common.%crew_freedays%',
            'report_common.%crew_compdays%',
            )
        rosters, = R.eval(context,roster_expr)

        ranksAtBase = dict()
        for base in self.SAS_BASES:
            ranksAtBase[base] = dict()

        noOfCrew = dict()
        flightdays = dict()
        blockhours = dict()
        deadheads = dict()
        deadheadBlockhours = dict()
        dutyTime = dict()
        layovers = dict()
        trainingdays = dict()
        vacationdays = dict()
        freedays = dict()
        compdays = dict()
        
        for (ix, rank, base, longhaul,
             crewFlightdaysLH,
             crewFlightdaysSH,
             crewBlockhoursLH,
             crewBlockhoursSH,
             crewDeadheads,
             crewDeadheadBlockhours,
             crewDutyTime,
             crewDutyTimeNoNightUpg,
             crewLayovers,
             crewTrainingdays,
             crewVacationdays,
             crewFreedays,
             crewCompdays) in rosters:
            if not (rank in self.SAS_RANKS):
                rank = "Other"
            if not (base in self.SAS_BASES):
                base = "Other"
            
            ranksAtBase[base][rank] = True
            
            if longhaul:
                qual = "LH"
            else:
                qual = "SH"
                
            noOfCrew[base] = noOfCrew.get(base,dict())
            noOfCrew[base][rank] = noOfCrew[base].get(rank,0)+1

            flightdays[base] = flightdays.get(base,dict())
            flightdays[base][rank] = flightdays[base].get(rank,dict())
            flightdays[base][rank]["LH"] = flightdays[base][rank].get("LH",0)+crewFlightdaysLH
            flightdays[base][rank]["SH"] = flightdays[base][rank].get("SH",0)+crewFlightdaysSH
            
            blockhours[base] = blockhours.get(base,dict())
            blockhours[base][rank] = blockhours[base].get(rank,dict())
            blockhours[base][rank]["LH"] = blockhours[base][rank].get("LH",RelTime(0))+crewBlockhoursLH
            blockhours[base][rank]["SH"] = blockhours[base][rank].get("SH",RelTime(0))+crewBlockhoursSH
            
            deadheads[base] = deadheads.get(base,dict())
            deadheads[base][rank] = deadheads[base].get(rank,0)+crewDeadheads

            deadheadBlockhours[base] = deadheadBlockhours.get(base,dict())
            deadheadBlockhours[base][rank] = deadheadBlockhours[base].get(rank,RelTime(0))+crewDeadheadBlockhours

            dutyTime[base] = dutyTime.get(base,dict())
            dutyTime[base][rank] = dutyTime[base].get(rank,dict())
            dutyTime[base][rank]["NU"] = dutyTime[base][rank].get("NU",RelTime(0))+crewDutyTime
            dutyTime[base][rank]["NoNU"] = dutyTime[base][rank].get("NoNU",RelTime(0))+crewDutyTimeNoNightUpg
            
            layovers[base] = layovers.get(base,dict())
            layovers[base][rank] = layovers[base].get(rank,0)+crewLayovers

            trainingdays[base] = trainingdays.get(base,dict())
            trainingdays[base][rank] = trainingdays[base].get(rank,0)+crewTrainingdays
            
            vacationdays[base] = vacationdays.get(base,dict())
            vacationdays[base][rank] = vacationdays[base].get(rank,0)+crewVacationdays

            freedays[base] = freedays.get(base,dict())
            freedays[base][rank] = freedays[base].get(rank,0)+crewFreedays

            compdays[base] = compdays.get(base,dict())
            compdays[base][rank] = compdays[base].get(rank,0)+crewCompdays


        # Remaining production
        rank_expr = R.foreach(
            R.times(10),
            'fundamental.%py_index%',
            'crew_pos.%trip_assigned_pos%(fundamental.%py_index%)',
            )
        rem_prod_expr = R.foreach(
            R.iter('iterators.trip_set',
                   where=('not fundamental.%is_roster%',
                          'trip.%has_only_flight_duty%',
                          'planning_area.%trip_is_in_planning_area%',
                          'crew_pos.%trip_assigned% > 0','trip.%pp_days% > 0', 'not hidden')),
            'trip.%code%',
            'trip.%homebase%',
            'trip.%is_long_haul%',
            rank_expr,
            'trip.%days%',
            'trip.%pp_block_time%',
            'trip.%start_utc%',
            )
        remaining_prod, = R.eval('sp_crrs',rem_prod_expr)

        # To map crew vector to actual rank
        ranks = {}
        for i in range(10):
            pos = i+1
            ranks[pos], = R.eval('crew_pos.%%pos2func%%(%s)' % pos)

        mancoFlightdays = dict()
        mancoBlockhours = dict()
        mancoTrips = dict()
        for (ix, code, base, longhaul, crew, tripDays, tripBlockhours, tripStart) in remaining_prod:
            if base not in self.SAS_BASES:
                base = "Other"
            if (code != "BL"):
                if longhaul:
                    qual = "LH"
                else:
                    qual = "SH"
                for (jx, pos, count) in crew:
                    if (count > 0):
                        rank = ranks[pos]
                        ranksAtBase[base][rank] = True

                        mancoFlightdays[base] = mancoFlightdays.get(base,dict())
                        mancoFlightdays[base][rank] = mancoFlightdays[base].get(rank,dict())
                        mancoFlightdays[base][rank][qual] = mancoFlightdays[base][rank].get(qual,0)+tripDays
            
                        mancoBlockhours[base] = mancoBlockhours.get(base,dict())
                        mancoBlockhours[base][rank] = mancoBlockhours[base].get(rank,dict())
                        mancoBlockhours[base][rank][qual] = mancoBlockhours[base][rank].get(qual,RelTime(0))+tripBlockhours
             
                        mancoTrips[base] = mancoTrips.get(base,dict())
                        mancoTrips[base][rank] = mancoTrips[base].get(rank,0)+1
                        
        for base in self.SAS_BASES:
            if (ranksAtBase[base]):
                basePage = Column(border=border(bottom=0))
                # Header
                header = self.getTableHeader((base,))
                # No of crew
                noOfCrewRow = Row(Text("Number of crew", font = Font(weight=BOLD), padding=padding(2,5,2,2)))
                # Flightdays
                flightdaysBlock = Column()
                flightdaysSH = Row(Text("Shorthaul", font = Font(weight=BOLD), align=RIGHT))
                flightdaysLH = Row(Text("Longhaul", font = Font(weight=BOLD), align=RIGHT))
                flightdaysTot = Row(Text("Total", font = Font(weight=BOLD), align=RIGHT))
                avFlightdaysCrew = Row(Text("Average per crew", font = Font(weight=BOLD), align=RIGHT))
                avFlightdaysSH = Row(Text("Shorthaul", font = Font(weight=BOLD), align=RIGHT))
                avFlightdaysLH = Row(Text("Longhaul", font = Font(weight=BOLD), align=RIGHT))
                avFlightdaysTot = Row(Text("Total", font = Font(weight=BOLD), align=RIGHT))
                
                # Blockhours
                blockhoursBlock = Column(Row(Text("Number of block hours (Assigned)", font = Font(weight=BOLD), padding=padding(2,5,2,2)), border=border(top=0)))
                blockhoursSH = Row(Text("Shorthaul", font = Font(weight=BOLD), align=RIGHT))
                blockhoursLH = Row(Text("Longhaul", font = Font(weight=BOLD), align=RIGHT))
                blockhoursTot = Row(Text("Total", font = Font(weight=BOLD), align=RIGHT))
                avBlockhoursCrew = Row(Text("Average per crew", font = Font(weight=BOLD), align=RIGHT))
                # Deadheads
                deadheadsBlock = Column(Row(Text("Deadheads", font = Font(weight=BOLD), padding=padding(2,5,2,2)), border=border(top=0)))
                deadheadsRow = Row(Text("Total", font = Font(weight=BOLD), align=RIGHT))
                avDeadheadsCrew = Row(Text("Average per crew", font = Font(weight=BOLD), align=RIGHT))
                deadheadBlockhoursRow = Row(Text("Block hours", font = Font(weight=BOLD), align=RIGHT))
                # Various averages
                averagesBlock = Column(Row(Text("Averages per crew", font = Font(weight=BOLD), padding=padding(2,5,2,2)), border=border(top=0)))
                dutyTimeRow = Row(Text("Duty time", font = Font(weight=BOLD), align=RIGHT))
                layoverRow = Row(Text("Layovers", font = Font(weight=BOLD), align=RIGHT))
                trainingRow = Row(Text("Training days", font = Font(weight=BOLD), align=RIGHT))
                vacationRow = Row(Text("Vacation days", font = Font(weight=BOLD), align=RIGHT))
                freedaysRow = Row(Text("Freedays", font = Font(weight=BOLD), align=RIGHT))
                compdaysRow = Row(Text("Compdays", font = Font(weight=BOLD), align=RIGHT))
                # Manco flightdays
                mancoBlock = Column()
                mancoFlightdaysBlock = Column(Row(Text("Number of flight days (Manco)", font = Font(weight=BOLD), padding=padding(2,5,2,2)), border=border(top=0)))
                mancoFlightdaysSH = Row(Text("Shorthaul", font = Font(weight=BOLD), align=RIGHT))
                mancoFlightdaysLH = Row(Text("Longhaul", font = Font(weight=BOLD), align=RIGHT))
                mancoFlightdaysTot = Row(Text("Total", font = Font(weight=BOLD), align=RIGHT))
                # Manco blockhours
                mancoBlockhoursBlock = Column(Row(Text("Number of block hours (Manco)", font = Font(weight=BOLD), padding=padding(2,5,2,2)), border=border(top=0)))
                mancoBlockhoursSH = Row(Text("Shorthaul", font = Font(weight=BOLD), align=RIGHT))
                mancoBlockhoursLH = Row(Text("Longhaul", font = Font(weight=BOLD), align=RIGHT))
                mancoBlockhoursTot = Row(Text("Total", font = Font(weight=BOLD), align=RIGHT))
                avMancoBlockhours = Row(Text("Average per day", font = Font(weight=BOLD), align=RIGHT))
                # Manco trips per day
                mancoTripsDay = Row(Text("Manco trips per day", font = Font(weight=BOLD), padding=padding(2,5,2,2)), border=border(top=0))
                # Total blockhours (Assigned + Manco)
                sumBlockhoursBlock = Column(Row(
                    Text("Total number of block hours (Assigned + Manco)", font = Font(weight=BOLD), padding=padding(2,5,2,2)), border=border(top=0)))
                sumBlockhoursSH = Row(Text("Shorthaul", font = Font(weight=BOLD), align=RIGHT))
                sumBlockhoursLH = Row(Text("Longhaul", font = Font(weight=BOLD), align=RIGHT))
                sumBlockhoursTot = Row(Text("Total", font = Font(weight=BOLD), align=RIGHT))
                
                totCrew = 0
                totFlightdaysSH = 0
                totFlightdaysLH = 0
                totBlockhoursSH = RelTime(0,0)
                totBlockhoursLH = RelTime(0,0)
                totDeadheads = 0
                totDeadheadBlockhours = RelTime(0,0)
                totDutyTime = RelTime(0,0)
                totDutyTimeNoNightUpg = RelTime(0,0)
                totLayovers = 0
                totTrainingdays = 0
                totVacationdays = 0
                totFreedays = 0
                totCompdays = 0
                totMancoFlightdaysSH = 0
                totMancoFlightdaysLH = 0
                totMancoBlockhoursSH = RelTime(0,0)
                totMancoBlockhoursLH = RelTime(0,0)
                totMancoTrips = 0
                totSumBlockhoursSH = RelTime(0,0)
                totSumBlockhoursLH = RelTime(0,0)
                
                for rank in self.SAS_RANKS:
                    if (ranksAtBase[base].get(rank, False)):
                        # Header
                        header.add(Text(rank, align=RIGHT))
                        # No of crew
                        noCrew = getDataItem(noOfCrew, base, rank)
                        totCrew += noCrew
                        noOfCrewRow.add(printDataItem(noCrew, pad=True))
                        noCrew = max(0.001, noCrew)
                        # Flightdays
                        tmp1 = getDataItem(flightdays, base, rank, "SH")
                        tmp2 = getDataItem(flightdays, base, rank, "LH")
                        totFlightdaysSH += tmp1
                        totFlightdaysLH += tmp2
                        flightdaysSH.add(printDataItem(tmp1))
                        flightdaysLH.add(printDataItem(tmp2))
                        flightdaysTot.add(printDataItem(tmp1+tmp2))
                        avFlightdaysSH.add(printDataItem(tmp1/pp_days))
                        avFlightdaysLH.add(printDataItem(tmp2/pp_days))
                        avFlightdaysTot.add(printDataItem((tmp1+tmp2)/pp_days))
                        avFlightdaysCrew.add(printDataItem(1.0*(tmp1+tmp2)/noCrew))
                        # Blockhours
                        tmp1 = getDataItem(blockhours, base, rank, "SH", True)
                        tmp2 = getDataItem(blockhours, base, rank, "LH", True)
                        totBlockhoursSH += tmp1
                        totBlockhoursLH += tmp2
                        blockhoursSH.add(printTimeItem(tmp1))
                        blockhoursLH.add(printTimeItem(tmp2))
                        blockhoursTot.add(printTimeItem(tmp1+tmp2))
                        avBlockhoursCrew.add(printTimeItem((tmp1+tmp2)/noCrew))
                        # Deadheads
                        tmp = getDataItem(deadheads, base, rank)
                        totDeadheads += tmp
                        deadheadsRow.add(printDataItem(tmp))
                        avDeadheadsCrew.add(printDataItem(1.0*tmp/noCrew))
                        tmp = getDataItem(deadheadBlockhours, base, rank, None, True)
                        totDeadheadBlockhours += tmp
                        deadheadBlockhoursRow.add(printTimeItem(tmp))
                        # Various averages
                        tmp0 = getDataItem(dutyTime, base, rank, "NU", True)
                        tmp1 = getDataItem(dutyTime, base, rank, "NoNU", True)
                        totDutyTime += tmp0
                        totDutyTimeNoNightUpg += tmp1
                        dutyTimeRow.add(
                            printTimeItem(str(tmp0/noCrew)+" ("+str(tmp1/noCrew)+")"))
                        
                        tmp = getDataItem(layovers, base, rank)
                        totLayovers += tmp
                        layoverRow.add(printDataItem(1.0*tmp/noCrew))
                        tmp = getDataItem(trainingdays, base, rank)
                        totTrainingdays += tmp
                        trainingRow.add(printDataItem(1.0*tmp/noCrew))
                        tmp = getDataItem(vacationdays, base, rank)
                        totVacationdays += tmp
                        vacationRow.add(printDataItem(1.0*tmp/noCrew))
                        tmp = getDataItem(freedays, base, rank)
                        totFreedays += tmp
                        freedaysRow.add(printDataItem(1.0*tmp/noCrew))
                        tmp = getDataItem(compdays, base, rank)
                        totCompdays += tmp
                        compdaysRow.add(printDataItem(1.0*tmp/noCrew))
                        # Manco flightdays
                        tmp1 = getDataItem(mancoFlightdays, base, rank, "SH")
                        tmp2 = getDataItem(mancoFlightdays, base, rank, "LH")
                        totMancoFlightdaysSH += tmp1
                        totMancoFlightdaysLH += tmp2
                        mancoFlightdaysSH.add(printDataItem(tmp1))
                        mancoFlightdaysLH.add(printDataItem(tmp2))
                        mancoFlightdaysTot.add(printDataItem(tmp1+tmp2))
                        # Manco blockhours
                        tmp1 = getDataItem(mancoBlockhours, base, rank, "SH", True)
                        tmp2 = getDataItem(mancoBlockhours, base, rank, "LH", True)
                        totMancoBlockhoursSH += tmp1
                        totMancoBlockhoursLH += tmp2
                        mancoBlockhoursSH.add(printTimeItem(tmp1))
                        mancoBlockhoursLH.add(printTimeItem(tmp2))
                        mancoBlockhoursTot.add(printTimeItem(tmp1+tmp2))
                        avMancoBlockhours.add(printDataItem((tmp1+tmp2)/pp_days))
                        # Manco trips per day
                        tmp = getDataItem(mancoTrips, base, rank)
                        totMancoTrips += tmp
                        mancoTripsDay.add(printDataItem(tmp/pp_days, pad=True))
                        # Total blockhours (Assigned + Manco)
                        tmp1 = getDataItem(mancoBlockhours, base, rank, "SH", True)+getDataItem(blockhours, base, rank, "SH", True)
                        tmp2 = getDataItem(mancoBlockhours, base, rank, "LH", True)+getDataItem(blockhours, base, rank, "LH", True)
                        totSumBlockhoursSH += tmp1
                        totSumBlockhoursLH += tmp2
                        sumBlockhoursSH.add(printTimeItem(tmp1))
                        sumBlockhoursLH.add(printTimeItem(tmp2))
                        sumBlockhoursTot.add(printTimeItem(tmp1+tmp2))

                
                # Header
                header.add(printDataItem("Tot.", True))
                basePage.add(header)
                # No of crew
                noOfCrewRow.add(printDataItem(totCrew, True, True))
                basePage.add(noOfCrewRow)
                # Flightdays
                flightdaysSH.add(printDataItem(totFlightdaysSH, True))
                flightdaysLH.add(printDataItem(totFlightdaysLH, True))
                flightdaysTot.add(printDataItem(totFlightdaysSH+totFlightdaysLH, True))
                avFlightdaysSH.add(printDataItem(totFlightdaysSH/pp_days, True))
                avFlightdaysLH.add(printDataItem(totFlightdaysLH/pp_days, True))
                avFlightdaysTot.add(printDataItem((totFlightdaysSH+totFlightdaysLH)/pp_days, True))
                if totCrew == 0:
                    avFlightdaysCrew.add(printDataItem(0, True))
                    avBlockhoursCrew.add(printTimeItem(0, True))
                    avDeadheadsCrew.add(printDataItem(0, True))
                    dutyTimeRow.add(printTimeItem("0 (0)", True))
                    layoverRow.add(printDataItem(0, True))
                    trainingRow.add(printDataItem(0, True))
                    vacationRow.add(printDataItem(0, True))
                    freedaysRow.add(printDataItem(0, True))
                    compdaysRow.add(printDataItem(0, True))
                else:
                    avFlightdaysCrew.add(printDataItem(1.0*(totFlightdaysSH+totFlightdaysLH)/totCrew, True))
                    avBlockhoursCrew.add(printTimeItem((totBlockhoursSH+totBlockhoursLH)/totCrew, True))
                    avDeadheadsCrew.add(printDataItem(1.0*totDeadheads/totCrew, True))
                    dutyTimeRow.add(
                        printTimeItem(str(totDutyTime/totCrew) +
                                      " ("+str(totDutyTimeNoNightUpg/totCrew)+")", True))
                    layoverRow.add(printDataItem(1.0*totLayovers/totCrew, True))
                    trainingRow.add(printDataItem(1.0*totTrainingdays/totCrew, True))
                    vacationRow.add(printDataItem(1.0*totVacationdays/totCrew, True))
                    freedaysRow.add(printDataItem(1.0*totFreedays/totCrew, True))
                    compdaysRow.add(printDataItem(1.0*totCompdays/totCrew, True))
                
                flightdaysBlock.add(Row(Text("Number of flight days", font = Font(weight=BOLD), padding=padding(2,5,2,2)), border=border(top=0)))
                flightdaysBlock.add(flightdaysSH)
                flightdaysBlock.add(flightdaysLH)
                flightdaysBlock.add(flightdaysTot)
                flightdaysBlock.add(avFlightdaysCrew)
                flightdaysBlock.add(Row(Text("Average no. of flight days per day", font = Font(weight=BOLD), padding=padding(2,5,2,2)), border=border(top=0)))
                flightdaysBlock.add(avFlightdaysSH)
                flightdaysBlock.add(avFlightdaysLH)
                flightdaysBlock.add(avFlightdaysTot)
                basePage.add(flightdaysBlock)
                # Blockhours
                blockhoursSH.add(printTimeItem(totBlockhoursSH, True))
                blockhoursLH.add(printTimeItem(totBlockhoursLH, True))
                blockhoursTot.add(printTimeItem(totBlockhoursSH+totBlockhoursLH, True))
                blockhoursBlock.add(blockhoursSH)
                blockhoursBlock.add(blockhoursLH)
                blockhoursBlock.add(blockhoursTot)
                blockhoursBlock.add(avBlockhoursCrew)
                basePage.add(blockhoursBlock)
                # Deadheads
                deadheadsRow.add(printDataItem(totDeadheads, True))
                deadheadBlockhoursRow.add(printTimeItem(totDeadheadBlockhours, True))
                deadheadsBlock.add(deadheadsRow)
                deadheadsBlock.add(avDeadheadsCrew)
                deadheadsBlock.add(deadheadBlockhoursRow)
                basePage.add(deadheadsBlock)
                averagesBlock.add(dutyTimeRow)
                averagesBlock.add(layoverRow)
                averagesBlock.add(trainingRow)
                averagesBlock.add(vacationRow)
                averagesBlock.add(freedaysRow)
                averagesBlock.add(compdaysRow)
                basePage.add(averagesBlock)
                # Manco flightdays
                mancoFlightdaysSH.add(printDataItem(totMancoFlightdaysSH, True))
                mancoFlightdaysLH.add(printDataItem(totMancoFlightdaysLH, True))
                mancoFlightdaysTot.add(printDataItem(totMancoFlightdaysSH+totMancoFlightdaysLH, True))
                mancoFlightdaysBlock.add(mancoFlightdaysSH)
                mancoFlightdaysBlock.add(mancoFlightdaysLH)
                mancoFlightdaysBlock.add(mancoFlightdaysTot)
                mancoBlock.add(mancoFlightdaysBlock)
                # Manco blockhours
                mancoBlockhoursSH.add(printTimeItem(totMancoBlockhoursSH, True))
                mancoBlockhoursLH.add(printTimeItem(totMancoBlockhoursLH, True))
                mancoBlockhoursTot.add(printTimeItem(totMancoBlockhoursSH+totMancoBlockhoursLH, True))
                avMancoBlockhours.add(printTimeItem((totMancoBlockhoursSH+totMancoBlockhoursLH)/pp_days, True))
                mancoBlockhoursBlock.add(mancoBlockhoursSH)
                mancoBlockhoursBlock.add(mancoBlockhoursLH)
                mancoBlockhoursBlock.add(mancoBlockhoursTot)
                mancoBlockhoursBlock.add(avMancoBlockhours)
                mancoBlock.add(mancoBlockhoursBlock)
                # Manco trips per day
                mancoTripsDay.add(printDataItem(totMancoTrips/pp_days, True, True))
                mancoBlock.add(mancoTripsDay)
                basePage.add(mancoBlock)
                # Total blockhours (Assigned + Manco)
                sumBlockhoursSH.add(printTimeItem(totSumBlockhoursSH))
                sumBlockhoursLH.add(printTimeItem(totSumBlockhoursLH))
                sumBlockhoursTot.add(printTimeItem(totSumBlockhoursSH+totSumBlockhoursLH))
                sumBlockhoursBlock.add(sumBlockhoursSH)
                sumBlockhoursBlock.add(sumBlockhoursLH)
                sumBlockhoursBlock.add(sumBlockhoursTot)
                basePage.add(sumBlockhoursBlock)

                self.add(basePage)
                self.page0()
       
def getDataItem(struct, key1, key2, key3=None, reltime=False):
    try:
        if key3:
            tmp = struct[key1][key2][key3]
        else:
            tmp = struct[key1][key2]
    except:
        if reltime:
            tmp = RelTime(0,0)
        else:
            tmp = 0
    return tmp

def printDataItem(value, bold=False, pad=False):
    if (type(value)==type(1.0)):
        if (value != 0):
            output = "%.2f" %(value)
        else:
            output = 0
    else:
        output = value
    output = Text(output, align=RIGHT)
    if bold:
        output.set(font=Font(weight=BOLD))
    if pad:
        output.set(padding=padding(2,5,2,2))
    return output

def printTimeItem(value, bold=False):
    if bold:
        return Text(value, align=RIGHT, font=Font(weight=BOLD))
    else:
        return Text(value, align=RIGHT)
# End of file

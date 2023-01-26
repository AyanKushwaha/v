"""
 $Header$
 
 Sim Dated Info

 Lists all OPC/OTS and AST activities in the planning period, using
 a weekly view.

 Created:    August 2007
 By:         Erik Gustafsson, Jeppesen Systems AB

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from RelTime import RelTime
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator as CCL
import Cui
import report_sources.include.ReportUtils as ReportUtils

# constants =============================================================={{{1
CONTEXT = 'default_context'
TITLE = 'Sim Dated Info'

class SimDatedInfo(SASReport):
    def addSim(self, simulator):
        simcode = simulator["code"]
        simbase = simulator["base"]
        day = simulator["day"]
        time = simulator["time"]
        slices = simulator["slices"]
        #print "base: " + simbase
        if (len(simbase) < 2):
            #"Handles case when no base was given seems to be an error no time to handle now"
            return
        # Slices: emp_or_comp, name, rank, lpc1, lpc2, crewbase, quals, code, pos, dutycode

        # 0: Instructors (modified in rave code)
        # 1: FC
        # 2: FP
        # 4: FU (Supervisors and Supernum)
        # 9: TL (AST/ASF/FFS)
        # 10: Unassigned (modified in rave code)
        
        positions = (0,1,2,4,9,10)
        pos2rank = {0:"TR",1:"FC",2:"FP",4:"FU",9:"TL"}

        sim_ordered = dict()
        for pos in positions:
            sim_ordered[pos] = []
        
        for simslice in slices:
            (ix, emp_comp, name, rank, lpc1, lpc2, crewbase, quals, code, pos, dutycode, hasAttribute, attribute) = simslice
            if pos not in positions:
                # Silly way to handle when crew is assigned in bad position
                pos = 9
                name = "Bad position"
                (name, rank, lpc1, lpc2, crewbase, quals, dutycode) = ("Bad position","-","-","-","-","-","-")
            try:
                sim_ordered[pos].append((emp_comp, name, rank, lpc1, lpc2, crewbase, quals, code, pos, dutycode, hasAttribute, attribute))
            except:
                # This is too general, but we need to handle bad data
                print "Problem with simslice: ",simslice
                pass
                    
        simbox = Column(border=border(left=1, right=1, top=1, bottom=1))
        simbox.add(Row(Text("%s %s %s" %(simcode, time, simbase), colour="#ffffff"), background="#000000"))
        for pos in positions:
            if pos < 10:
                for (emp_comp, name, rank, lpc1, lpc2, crewbase, quals, code, pos, dutycode, hasAttribute, attribute) in sim_ordered[pos]:
                    thiscrew = Column(border=border(bottom=1))
                    thiscrew.add(Text("%s %s %s" %(emp_comp, name, rank)))
                    if hasAttribute:
                        thiscrew.add(Text("%s" %(attribute)))
                    thiscrew.add(Text("%s %s %s" %(dutycode, crewbase, quals)))
                    thiscrew.add(Text(lpc1))
                    if lpc2:
                        row4 = lpc2
                    else:
                        row4 = " "
                    thiscrew.add(Text(row4))
                    simbox.add(Row(thiscrew))
            else:
                for (emp_comp, name, rank, lpc1, lpc2, crewbase, quals, code, pos, dutycode, hasAttribute, attribute) in sim_ordered[pos]:
                    if emp_comp:
                        unassigned = Column(border=border(bottom=1))
                        unassigned.add(Row(Text("Remaining: ")))
                        unassigned.add(Row(Text(emp_comp)))
                        simbox.add(Row(unassigned))
        if not simbase in self.data:
            self.data[simbase] = dict()
        if not day in self.data[simbase]:
            self.data[simbase][day] = dict()
        added = False
        ix = 0
        while (not added):
            time_ix = "%s-%s" %(time, ix)
            if not time_ix in self.data[simbase][day]:
                self.data[simbase][day][time_ix] = simbox
                added = True
            else:
                ix += 1

    def sortSims(self):
        self.sorted_data = dict()
        for base in self.data:
            self.sorted_data[base] = dict()
            for date in self.data[base]:
                self.sorted_data[base][date] = []
                simKeys = self.data[base][date].keys()
                simKeys.sort()
                i = 0
                for simKey in simKeys:
                    databox = self.data[base][date][simKey]
                    if ((i % 2) == 0 and not (i == 0)):
                        temp = Column(width=100)
                        dateStr = "%s" %(date)
                        temp.add(self.getTableHeader((dateStr,)))
                        temp.add(databox)
                        databox = temp
                    self.sorted_data[base][date].append(databox)
                    i += 1

    def getRowsForWeek(self, base, monday):
        dateRow = Row()
        outRows = []
        for i in range(7):
            #dateStr = self.dates[monday + RelTime(i*24,0)]
            dateStr = "%s" %(monday + RelTime(i*24,0))
            outCol = Column(width=100)
            outCol.add(self.getTableHeader((dateStr,)))
            dateRow.add(outCol)
        outRows.append(dateRow)
        weekHasSims = True
        while (weekHasSims):
            weekHasSims = False
            simRow = Row()
            for i in range(7):
                date = monday + RelTime(i*24,0)
                if date in self.sorted_data[base]:
                    try:
                        thisSim = self.sorted_data[base][date].pop(0)
                        weekHasSims = True
                        simRow.add(thisSim)
                    except:
                        simRow.add(Column())
                else:
                    simRow.add(Column())
            if weekHasSims:
                outRows.append(simRow)
        outRows.append(Row(Text(" ")))
        return outRows
        

    def create(self):

        #################
        ## Basic setup
        #################
        

        self.pp_start,self.pp_end,pp_days,firstWD,non_pp,report_start,report_end = R.eval(
            'fundamental.%pp_start%',
            'fundamental.%pp_end%',
            'pp.%days%',
            'report_common.%first_weekday_in_pp%',
            'report_common.%sim_dated_info_non_pp%',
            'report_common.%sim_dated_info_start_date%',
            'report_common.%sim_dated_info_end_date%',
            )
        if non_pp:
            # These functions exists in SASReport, but we need other values for this report
            ppmod = ReportUtils.PPModifier(report_start,report_end)
            self.pp_start = report_start
            self.pp_end = report_end
        
        SASReport.create(self, TITLE, orientation=LANDSCAPE, usePlanningPeriod=True)

        dates, = R.eval(
            R.foreach(R.times('pp.%days%'),
                      'fundamental.%date_index%',
                      'format_time(fundamental.%date_index%, "%a, %b %d")',
                      ))
        
        self.dates = dict()
        for (ix, date, dateStr) in dates:
            self.dates[date] = dateStr

        self.data = dict()            
        sim_expr = R.foreach(R.iter('iterators.leg_set',
                                    where = ('report_courses.%simulator_for_dated_report%', 'duty.%starts_in_pp%')),
                             'report_common.%simulator_key_starttime_day%', # Used for identification
                             'report_common.%simulator_start_day%', # Used for placement in report
                             'report_common.%simulator_task_code%', # Simulator header in report
                             'report_common.%simulator_homebase%', # Simulator header in report
                             'report_common.%simulator_starttime_str%', # Simulator header in report
                             R.foreach('equal_legs',
                                       R.foreach('iterators.leg_set',
                                                 # Crew info for simulator
                                                 'report_common.%simulator_emp_or_comp%',
                                                 'report_common.%crew_surname%',
                                                 'report_common.%crew_rank%',
                                                 'report_common.%lpc_opc_or_ots_str_1%',
                                                 'report_common.%lpc_opc_or_ots_str_2%',
                                                 'report_common.%crew_homebase%',
                                                 'report_common.%ac_quals%',
                                                 # Assignment dependent info
                                                 'report_common.%simulator_code%',
                                                 'report_common.%simulator_pos%',
                                                 'report_common.%simulator_duty_code%',
                                                 'report_courses.%has_attribute%',
                                                 'report_courses.%training_attribute%'
                                                 )
                                       )
                             )

        sim_win1, = R.eval('default_context', sim_expr)

        try:
            saved = CCL().fetchcurrent()
            CCL(Cui.CuiArea1,"window").reinstate()
            sim_win2, = R.eval('default_context', sim_expr)
        finally:
            if saved:
                saved.reinstate()

        sims = sim_win1 + sim_win2

        tempdata = dict()
        for (ix, key, day, code, base, time_str, slices) in sims:
            if key in tempdata:
                # Already added
                continue
            else:
                slices, = slices # Unpack
                (foo, slices) = slices # Unpack
                tempdata[key] = {"code":code, "base":base, "day":day, "time":time_str, "slices":slices}
                
        for key in tempdata:
            self.addSim(tempdata[key])

        self.sortSims()

        # Build the report
        for base in self.data:
            header = self.getDefaultHeader()
            header.add(Row(Text(base, font=Font(size=self.FONTSIZEHEAD, weight=BOLD))))
            self.setHeader(header)

            WDNum = 1
            preIx = WDNum - firstWD
            monday = self.pp_start + RelTime(preIx*24,0)
            while monday < self.pp_end:
                rows = self.getRowsForWeek(base, monday)
                for weekrow in rows:
                    self.add(weekrow)
                    self.page0()
                if len(rows) == 1:
                    # No sims
                    pass
                else:
                    self.page()
                    
                monday += RelTime(7*24,0)
            self.page()
            
        if non_pp:
            # The report used own interval, so we reset pp
            del ppmod

        
### End of file

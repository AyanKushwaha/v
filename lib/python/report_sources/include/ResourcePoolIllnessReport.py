

"""
Resource Pool Illness
"""

import carmensystems.rave.api as R

import Cfh
import Cui

from AbsTime import AbsTime
from AbsDate import AbsDate
from RelTime import RelTime
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
import utils.DisplayReport as display

EMP_NO_WIDTH = 40
NAME_WIDTH = 150
RANK_WIDTH = 20
ILL_CODE_WIDTH = 40
ILL_DATE_WIDTH = 80
TOTAL_DUTY_HOURS_WIDTH = 40
DUTY_HOURS_WIDTH = 85
VALUE_WIDTH = 50
LINE_WIDTH = 10
REST_WIDTH = 140

def ColW(*a, **k):
    """Column with width = VALUE_WIDTH"""
    k['width'] = VALUE_WIDTH
    return Column(*a, **k)

def TextL(*a, **k):
    """Text aligned to the left"""
    k['align'] = LEFT
    return Text(*a, **k)

class ResourcePoolIllnessReport(SASReport):
    """
    Creates an ResourcePoolIllness for the month of current planning period, if created
    from Studio or the salary module, or for three months back if created from
    the batch job (report server).

    Arguments to report:

    'starttime' - Real start time of report generation.
    'firstdate' - First day of period requested.
    'lastdate'  - Last day of period requested (time point not included in
                  interval).
    'admcode'   - Optional. Type of run ('N' = Normal, 'T' = Test Run). Note: 'retro'
                  runs do not create statement (maybe this is wrong?).
    'note'      - Optional. Comment to the run.
    'extsys'    - Optional. Salary system to use ('DK', 'NO', 'SE', ...)
    'CONTEXT'   - Optional. Context to use when iterating.
                  ('default_context', 'sp_crew') When not set, 'sp_crew'
                  will be used.
    'fromStudio' - Optional. True if the report is created from Studio
    """

    def create(self):
        firstdate = AbsTime(int(self.arg('firstdate')))
        lastdate = AbsTime(int(self.arg('lastdate')))
        context = self.arg('CONTEXT')
        if context is None:
            # Called from report server
            admcode = self.arg('admcode')
            note = self.arg('note')
            extsys = self.arg('extsys')
            context = 'sp_crew'
        else:
            admcode = None
            note = "Interactive"
            extsys = None
        context = 'sp_crew'
        title = "Resource Pool Illness Reporting"

        headerItemsDict = {'Period: ': '%s - %s' % (AbsDate(firstdate), AbsDate(lastdate))}
        
        SASReport.create(self, title, showPlanData=False, orientation=LANDSCAPE, headerItems=headerItemsDict)

        header = self.getDefaultHeader()
        header.add(self.getTableHeader(
            items=('Emp. No', 'Name', 'Rank', 'ILL Code', 'ILLNESS Date', 'Total Duty Hours', 'Duty Hours 450', 'Duty Hours 456'),
            widths=(EMP_NO_WIDTH, NAME_WIDTH, RANK_WIDTH, ILL_CODE_WIDTH, ILL_DATE_WIDTH, TOTAL_DUTY_HOURS_WIDTH, DUTY_HOURS_WIDTH, DUTY_HOURS_WIDTH),
            aligns=(LEFT, LEFT, LEFT, LEFT, LEFT, LEFT, LEFT, LEFT)))
        self.setHeader(header)
        
        bgColorRow = '#eeeeee'
        
        rosterExpression = 'crew.%%is_cabin%% and crew.%%is_sks%% and crew.%%is_temporary_at_date%%(%s)' % firstdate
        tripExpression = 'trip.%is_illness%'
        
        cbag = R.context(context).bag()
        for roster_bag in cbag.iterators.roster_set(where=rosterExpression,
                                                    sort_by=('report_common.%crew_surname%')):
            empNo = roster_bag.report_common.employee_number_at_date(firstdate)
            surName = roster_bag.report_common.crew_surname()
            firstName = roster_bag.report_common.crew_firstname()
            rank = roster_bag.crew.rank()
            printedCrew = False

            for trip_bag in roster_bag.iterators.trip_set(where=tripExpression,
                                                          sort_by=('trip.%start_hb%')):
                illCode = trip_bag.trip.code()
                illfirstdate = trip_bag.trip.start_hb()
                illTripDays = trip_bag.report_overtime.ill_temp_duty_time_num_days()

                for duty_bag in trip_bag.iterators.duty_set(sort_by=('duty.%start_hb%')):
                    for tripDay in range(illTripDays):
                        illDate = illfirstdate.adddays(tripDay)
                        illDutyHoursDay = duty_bag.report_overtime.ill_temp_duty_time_day(tripDay)

                        if illDate >= firstdate and illDate < lastdate:                    
                            if not printedCrew:
                                if bgColorRow == '#ffffff':
                                    bgColorRow = '#eeeeee'
                                else:
                                    bgColorRow = '#ffffff'
                            self.printRow(empNo, surName, firstName, rank, printedCrew, illCode, illDate, illDutyHoursDay, bgColorRow)
                            if tripDay == 0:
                                printedCrew = True
            self.page()

    def printRow(self, empNo, surName, firstName, rank, printedCrew, illCode, illDate, illDutyHoursDay, bgColorRow):
        totalDutyTimeDecimal = self.dutyTimeDecimal(illDutyHoursDay)
        
        dutyHours450 = min(totalDutyTimeDecimal, 12.0)
        if totalDutyTimeDecimal > 12.0:
            dutyHours456 = totalDutyTimeDecimal - 12.0
        else:
            dutyHours456 = 0.0
                
        if printedCrew:
            empNo = ''
            surName = ''
            firstName = ''
            rank = ''

        rowContent = []
        rowContent.append(Column(Text('%s' % empNo), width=EMP_NO_WIDTH+18))
        rowContent.append(Column(Text('%s %s' % (surName, firstName)), width=NAME_WIDTH+18))
        rowContent.append(Column(Text('%s' % rank), width=RANK_WIDTH+23))
        
        rowContent.append(Column(Text('%s' % illCode), width=ILL_CODE_WIDTH+25))
        rowContent.append(Column(Text('%s' % AbsDate(illDate)), width=ILL_DATE_WIDTH+25))
        rowContent.append(Column(Text('%s' % illDutyHoursDay, align=RIGHT), width=TOTAL_DUTY_HOURS_WIDTH))
        rowContent.append(Column(Text('%0.2f' % dutyHours450, align=RIGHT), width=DUTY_HOURS_WIDTH+10))
        rowContent.append(Column(Text('%0.2f' % dutyHours456, align=RIGHT), width=DUTY_HOURS_WIDTH))

        self.add(Row(*rowContent, background=bgColorRow))

    def dutyTimeDecimal(self, dutyTime):
        hh, mm = dutyTime.split()
        mm = (mm/60.0)
        return (hh+mm)


def runReport(scope='window'):
    """Run PRT Report with data found in 'area', setting 'default_context'."""
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    try: del rptForm
    except: pass
    rptForm = display.reportFormDate('Resource Pool Illness Report')
    rptForm.show(1)
    if rptForm.loop() == Cfh.CfhOk:
        startDate = rptForm.getStartDate()
        endDate = rptForm.getEndDate()
        nowTime, = R.eval('fundamental.%now%')
        args = 'firstdate=%s lastdate=%s fromStudio=TRUE ' % (startDate, endDate)
        args += 'CONTEXT=default_context starttime=%d' % int(nowTime)
        
    try:
        Cui.CuiSetCurrentArea(Cui.gpc_info, area)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, 'WINDOW')
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, area, 'window',
            '../lib/python/report_sources/include/ResourcePoolIllnessReport.py', 0, args)
    except Exception, e:
        print e
    return

"""
 Production Days Info 

 ProductionDaysInfo report showing planned production, max limit and target.

 Created:    22Nov2010
 By:         Pierre Nordblom, Jeppesen Systems AB

"""

from carmensystems.publisher.api import *
import carmensystems.rave.api as r
from report_sources.include.SASReport import SASReport
from report_sources.include.ReportUtils import DataCollection, OutputReport
from AbsDate import AbsDate


TITLE = "Production Days Info"

def htext(*a, **k):
    """Text for header row"""
    k['align'] = LEFT
    k['padding'] = padding(2, 2, 12, 2)
    return Text(*a, **k)


def htext_b(*a, **k):
    """Text for header row"""
    k['background'] = '#efefef'
    return htext(*a, **k)


def right(*a, **k):
    """Text aligned right."""
    k['align'] = RIGHT
    k['padding'] = padding(2, 2, 12, 2)
    return Text(*[str(x) for x in a], **k)


def right_b(*a, **k):
    k['background'] = '#efefef'
    return right(*a, **k)


def left(*a, **k):
    """Text aligned left."""
    k['align'] = LEFT
    k['padding'] = padding(2, 2, 12, 2)
    return Text(*[str(x) for x in a], **k)


def left_b(*a, **k):
    k['background'] = '#efefef'
    return left(*a, **k)


class ProductionDaysInfo(SASReport):
    def create(self, outputType='general'):
        self.csvReport = (outputType == 'csv')
        SASReport.create(self, TITLE, orientation=LANDSCAPE,
                usePlanningPeriod=True)

        if self.csvReport: self.csvRows = list()
        
        crewExpr = r.foreach(r.iter('iterators.roster_set', 
                                    where='report_ccr.%flight_crew_region_valid%'),
                             'report_ccr.%crew_surname%',
                             'report_ccr.%crew_firstname%',
                             'report_ccr.%employee_number%',
#                             'report_ccr.%crew_rank%',                            
                             'report_ccr.%homebase_at_pp_start%',
                             'report_ccr.%rule_start%',
                             'report_ccr.%rule_end%',                             
#                             'report_ccr.%ac_qual_at_pp_start%',							 
                             'report_ccr.%nr_production_days_until_now%',                             
                             'report_ccr.%target%',
                             'report_ccr.%prod_days_mon%',
                             'report_ccr.%month_target_prod%',                             
                             'report_ccr.%nr_va_days%',
                             'report_ccr.%nr_of_scaled_production_days%',
                             'report_ccr.%max_production_days_limit_in_year%',
                             'report_ccr.%part_time_factor%',
                             'report_ccr.%avail_factor%',                             
                             'report_ccr.%crew_excluded_from_max_production_rule%',
                             'crew.%is_passive_plus_at_pp_start%')
                             
        crewData, = r.eval('default_context', crewExpr)

        if self.csvReport:
            self.csvRows.append("") 
            header = self.get_header()
            self.csvRows.append(header)
        else:
            headerBox = self.get_header()
            self.add(Row(headerBox))

        background = False
        crewInfo = []

        background_excluded = False
        crewInfoExcluded = []
        crewInfoPassive = []
        rows_crew_excluded = []
        if crewData:
            for crew in crewData:
    
                crewBox = Column()
                excluded_crew = crew[-2]
                passive_plus_crew = crew[-1]
                         
                if self.csvReport:
                    row = self.get_row(crew, background_excluded)

                    if excluded_crew:
                        rows_crew_excluded.append(row)
                    else:
                        self.csvRows.append(row)
                else:
                    if excluded_crew and not passive_plus_crew:
                        row = self.get_row(crew, background_excluded)
                        crewBox.add(row)
                        crewInfoExcluded.append(crewBox)
                        background_excluded = not background_excluded
                    elif passive_plus_crew:
                        row = self.get_row(crew, background_excluded)
                        crewBox.add(row)
                        crewInfoPassive.append(crewBox)
                        background_excluded = not background_excluded
                    else:
                        row = self.get_row(crew, background)
                        crewBox.add(row)
                        crewInfo.append(crewBox)
                        background = not background
        
            if self.csvReport:

                if rows_crew_excluded:
                    self.csvRows.append("")
                    self.csvRows.append("Crew member(s) not affected by the 'Max 179 production days' rule")
                    header = self.get_header()
                    self.csvRows.append(header)
                    self.csvRows.append(row)  
                
                self.set(font=Font(size=14))
                csvObject = OutputReport(TITLE, self, self.csvRows)
                self.add(csvObject.getInfo())
            else:
                for crew in crewInfo:
                    self.add(Row(crew))
                    self.page0()

                if crewInfoExcluded:
                    self.add(Row(""))
                    headerExcludedBox = Column()
                    headerExcludedBox.add(Row(
                        htext("Crew member(s) not affected by the 'Max 179 production days' rule"),
                        font=self.HEADERFONT))

                    self.add(Row(headerExcludedBox))
                    headerBox = self.get_header()
                    self.add(Row(headerBox))
        
                    for crew in crewInfoExcluded:
                        self.add(Row(crew))
                        self.page0()

                if crewInfoPassive:
                    self.add(Row(""))
                    headerPassiveBox = Column()
                    headerPassiveBox.add(Row(
                        htext("Passive+ Crew"),
                        font=self.HEADERFONT))

                    self.add(Row(headerPassiveBox))
                    headerPassiveBox = self.get_header()
                    self.add(Row(headerPassiveBox))
        
                    for crew in crewInfoPassive:
                        self.add(Row(crew))
                        self.page0()

        else:
            self.add(Row("No production was found for the selected crew member(s).",
                    font=self.HEADERFONT, height=36))
       


    def scale_and_round(self, value, dec):
        scale = 1000.0
        scaled_value = value / scale
        rounded_value = round(scaled_value, dec)
        return rounded_value

    def get_row(self, crew, background):
        ix, surname, firstname, emp_no, homebase, rule_start, rule_end, p_days, target, prod_days_mon, month_target_prod, va_in_year, maxlimit_year, maxlimit, part_time, avail_factor, excluded_crew, passive_crew= crew
        name = surname+", "+firstname+" ("+homebase+")"
        part_time = str(part_time)+"%"
        p_days = self.scale_and_round(p_days, 2)
        target = self.scale_and_round(target, 2)
        va_in_year = self.scale_and_round(va_in_year, 2)
        rule_start = str(rule_start)
        rule_start = str(rule_start[0:9])
        rule_end = str(rule_end)
        rule_end = str(rule_end[0:9])        
        maxlimit_year = self.scale_and_round(maxlimit_year, 2)
        maxlimit = self.scale_and_round(maxlimit, 2)
        avail_factor = self.scale_and_round(avail_factor, 2)
        crew_info = (name, emp_no, rule_start, rule_end, p_days, target, prod_days_mon, month_target_prod, va_in_year, maxlimit_year, maxlimit, part_time, avail_factor)

        if self.csvReport:
             row = self.get_output(crew_info)
        else:
            if background:
                row = Row(left_b(crew_info[0]),
                          left_b(crew_info[1]),
                          left_b(crew_info[2]),
                          right_b(crew_info[3]),
                          right_b(crew_info[4]),
                          right_b(crew_info[5]),
                          right_b(crew_info[6]),
                          right_b(crew_info[7]),
                          right_b(crew_info[8]),
                          right_b(crew_info[9]),
                          right_b(crew_info[10]),
                          right_b(crew_info[11]),
                          right_b(crew_info[12]))
            else:
                row = Row(left(crew_info[0]),
                          left(crew_info[1]),
                          left(crew_info[2]),
                          right(crew_info[3]),
                          right(crew_info[4]),
                          right(crew_info[5]),
                          right(crew_info[6]),
                          right(crew_info[7]),
                          right(crew_info[8]),
                          right(crew_info[9]),
                          right(crew_info[10]),
                          right(crew_info[11]),
                          right(crew_info[12]))  
                
        return row

    def get_output(self, items):
        output = ""
        for item in items:
            output = output + str(item) + ";"

        return output
            
    def get_header(self):
        header = ("Name", "Empno", "Start", "End", "Prod Days", "Target", "Prod Days(M)", "Target(M)", "VA", "Max(full)", "Max(so far)", "PT", "A-Factor")

        if self.csvReport:
               headerBox = self.get_output(header)
        else:
            headerBox = Column()
            headerBox.add(Row(
                htext(header[0]),
                htext(header[1]),
                htext(header[2]),
                htext(header[3]),
                htext(header[4]),
                htext(header[5]),
                htext(header[6]),
                htext(header[7]),
                htext(header[8]),
                htext(header[9]),
                htext(header[10]),
                htext(header[11]),
                htext(header[12]),
                font=self.HEADERFONT,
                background=self.HEADERBGCOLOUR))

        return headerBox

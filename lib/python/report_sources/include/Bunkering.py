"""
 Bunkering report showing targets, banked and recovered days.

"""

from carmensystems.publisher.api import *
import carmensystems.rave.api as r
from report_sources.include.SASReport import SASReport
from report_sources.include.ReportUtils import DataCollection, OutputReport
from AbsDate import AbsDate


TITLE = "Bunkering Info"


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


class Bunkering(SASReport):
    def create(self, outputType='general'):
        self.csvReport = (outputType == 'csv')
        SASReport.create(self, TITLE, orientation=LANDSCAPE,
                         usePlanningPeriod=True)

        if self.csvReport:
            self.csvRows = list()

        crewExpr = r.foreach(r.iter('iterators.roster_set',
                                    where='bunkering.%has_bunkering_agreement_in_pp%'),
                             'report_ccr.%crew_surname%',
                             'report_ccr.%crew_firstname%',
                             'report_ccr.%employee_number%',
                             'report_ccr.%homebase_at_pp_start%',
                             'bunkering.%crew_agreement_pp_start%',
                             'bunkering.%start_crew%',
                             'bunkering.%end_crew%',
                             'bunkering.%max_p%',
                             'bunkering.%p_target%',
                             'bunkering.%p_actual%',
                             'bunkering.%days_banked%',
                             'bunkering.%crew_month_original_freedays_report%',
                             'bunkering.%crew_month_minimum_freedays_report%',
                             'bunkering.%crew_month_scheduled_freedays_report%',
                             'bunkering.%days_banked_report%',
                             'bunkering.%recovered_days_report%',
                             'crew.%in_variable_group_pp_start%')

        crewData, = r.eval('default_context', crewExpr)

        if self.csvReport:
            self.csvRows.append('')
            self.csvRows.append('Variable Crew with a -CVxx agreement')
            header = self.get_header()
            self.csvRows.append(header)

        background = False
        crewInfo = []
        crewInfoFixed = []

        background_fixed = False
        fixed_crew = []
        if crewData:
            for crew in crewData:

                crewBox = Column()
                variable_crew = crew[-1]

                if self.csvReport:
                    row = self.get_row(crew, background_fixed)
                    if variable_crew:
                        self.csvRows.append(row)
                    else:
                        fixed_crew.append(row)
                else:
                    if variable_crew:
                        row = self.get_row(crew, background)
                        crewBox.add(row)
                        crewInfo.append(crewBox)
                        background = not background
                    else:
                        row = self.get_row(crew, background_fixed)
                        crewBox.add(row)
                        crewInfoFixed.append(crewBox)
                        background_fixed = not background_fixed

            if self.csvReport:
                if fixed_crew:
                    self.csvRows.append('')
                    self.csvRows.append('Fixed Crew with a -CVxx agreement')
                    header = self.get_header()
                    self.csvRows.append(header)
                    for row in fixed_crew:
                        self.csvRows.append(row)
                self.set(font=Font(size=14))
                csvObject = OutputReport(TITLE, self, self.csvRows)
                self.add(csvObject.getInfo())
            else:
                headerVariableBox = Column()
                headerVariableBox.add(Row(
                    htext('Variable Crew with a -CVxx agreement'),
                    font=self.HEADERFONT))
                self.add(Row(headerVariableBox))
                headerBox = self.get_header()
                self.add(Row(headerBox))
                for crew in crewInfo:
                    self.add(Row(crew))
                    self.page0()

                if crewInfoFixed:
                    self.add(Row(''))
                    headerFixedBox = Column()
                    headerFixedBox.add(Row(
                        htext('Fixed Crew with a -CVxx agreement'),
                        font=self.HEADERFONT))
                    self.add(Row(headerFixedBox))
                    headerBox = self.get_header()
                    self.add(Row(headerBox))
                    for crew in crewInfoFixed:
                        self.add(Row(crew))
                        self.page0()

        else:
            self.add(Row("No selected crew with -CVxx agreement",
                         font=self.HEADERFONT, height=36))

    def get_row(self, crew, background):
        ix, surname, firstname, emp_no, homebase, agreement, agreement_start, agreement_end, max_p, p_target, p_actual,\
            banked, f_target, f_target_reduced, f_assigned, recovered, banked_new, variable_crew = crew
        name = surname + ", " + firstname + " (" + homebase + ")"
        agreement_start = str(agreement_start)
        agreement_start = str(agreement_start[0:9])
        agreement_end = str(agreement_end)
        agreement_end = str(agreement_end[0:9])
        crew_info = (name, emp_no, agreement, agreement_start, agreement_end, max_p,
                     p_target, p_actual, banked,
                     f_target, f_target_reduced, f_assigned, recovered, banked_new)

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
                          right_b(crew_info[12]),
                          right_b(crew_info[13]))
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
                          right(crew_info[12]),
                          right(crew_info[13]))

        return row

    def get_output(self, items):
        output = ""
        for item in items:
            output = output + str(item) + ";"

        return output

    def get_header(self):
        header = ("Name", "Empno", "Agreement", "Start", "End", "MaxP",
                  "PTarget(<PP)", "PActual(<PP)", "Banked(<PP)",
                  "FTarget", "FTargetReduced", "FAssigned", "Banked", "Recovered")

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
                htext(header[13]),
                font=self.HEADERFONT,
                background=self.HEADERBGCOLOUR))

        return headerBox

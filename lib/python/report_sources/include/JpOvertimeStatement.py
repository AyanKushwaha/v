"""
Japanese overtime statement

This report generates overtime statement excel files for japanese crew.
"""

# imports ================================================================{{{1
import Cui
import carmensystems.rave.api as R
import carmstd.rave
import xlsxwriter
from RelTime import RelTime
from carmensystems.publisher.api import Column
from carmensystems.publisher.api import LANDSCAPE
from carmensystems.publisher.api import Row
from report_sources.include.SASReport import SASReport

# constants =============================================================={{{1
CONTEXT = 'sp_crew'
CSV_DIR = "/samba-share/reports/JpOvertimeStatement"

# classes ================================================================{{{1


def reltime_to_string(time, blank_zero=False):
    if blank_zero and time == RelTime(0):
        return ''
    else:
        return str(time)


class JpOvertimeStatement(SASReport):
    """
    Create the report using the Python Publisher API.
    """

    def create(self):
        # Get Planning Period start and end
        (period_start,) = R.eval('fundamental.%pp_start%')
        period_end = period_start.addmonths(1)

        period_monyyyy = str(period_start)[2:9]
        title = "Overtime Statement for %s" % period_monyyyy

        # Basic setup

        SASReport.create(self, title, usePlanningPeriod=True, orientation=LANDSCAPE)

        column = Column()

        column.add(Row("Overtime statements have been generated for the following crew"))

        jp_leg_query = R.foreach(R.iter('iterators.leg_set',
                                        where='leg.%is_flight_duty% and leg.%ci_start_lt% >= ' + str(period_start) + ' and leg.%ci_start_lt% < ' + str(period_end)),
                                 'report_jp_overtime.%leg_date%',
                                 'report_jp_overtime.%leg_fd%',
                                 'report_jp_overtime.%leg_ci%',
                                 'report_jp_overtime.%leg_co%',
                                 'report_jp_overtime.%leg_duty_time_for_ot%',
                                 'report_jp_overtime.%leg_ot_normal%',
                                 'report_jp_overtime.%leg_ot_over_16_hours%',
                                 'report_jp_overtime.%leg_nw_normal%',
                                 'report_jp_overtime.%is_passive_flight%')

        jp_duty_query = R.foreach(R.iter('iterators.duty_set',
                                         where='duty.%is_flight_duty% and duty.%is_on_duty%'),
                                  'duty.%start_hb%',
                                  'duty.%end_hb%',
                                  jp_leg_query)

        jp_crew_query = R.foreach(R.iter('iterators.roster_set',
                                         where='report_jp_overtime.%crew_is_jp%',
                                         sort_by='report_jp_overtime.%crew_name%'),
                                  'report_jp_overtime.%crew_employee_number%',
                                  'report_jp_overtime.%crew_name%',
                                  'report_jp_overtime.%crew_group%',
                                  jp_duty_query)
        jp_crew, = R.eval(CONTEXT, jp_crew_query)

        workbook = xlsxwriter.Workbook('/samba-share/reports/JpOvertimeStatement/JpOvertimeStatement%s.xlsx' % period_monyyyy)

        bold            = workbook.add_format({'bold': True})
        white_bg        = workbook.add_format({'border': 1,
                                               'text_wrap': True,
                                               'font_name': 'Arial',
                                               'font_size': 10,
                                               'align': 'center'})
        white_bg_bold   = workbook.add_format({'bold': True,
                                               'border': 1,
                                               'text_wrap': True,
                                               'font_name': 'Arial',
                                               'font_size': 10,
                                               'align': 'center'})
        light_blue_bg   = workbook.add_format({'bg_color': '#CCFFFF',
                                               'border': 1,
                                               'text_wrap': True,
                                               'font_name': 'Arial',
                                               'font_size': 10,
                                               'align': 'center'})
        pink_bg =         workbook.add_format({'bg_color': '#FF99CC',
                                               'border': 1,
                                               'text_wrap': True,
                                               'font_name': 'Arial',
                                               'font_size': 10,
                                               'align': 'center'})
        light_yellow_bg = workbook.add_format({'bg_color': '#FFFF99',
                                               'border': 1,
                                               'text_wrap': True,
                                               'font_name': 'Arial',
                                               'font_size': 10,
                                               'align': 'center'})

        summary_name_col = 0
        summary_employee_number_col = 1
        summary_ot_normal_col = 2
        summary_ot_over_16_hours_col = 3
        summary_nw_normal_col = 4

        summary_worksheet = workbook.add_worksheet("Summary %s" % period_monyyyy)

        summary_worksheet.set_column(summary_name_col, summary_name_col, 16)
        summary_worksheet.set_column(summary_employee_number_col, summary_employee_number_col, 13)
        summary_worksheet.set_column(summary_ot_normal_col, summary_ot_normal_col, 13)
        summary_worksheet.set_column(summary_ot_over_16_hours_col, summary_ot_over_16_hours_col, 13)
        summary_worksheet.set_column(summary_nw_normal_col, summary_nw_normal_col, 16)

        summary_line = 0
        summary_worksheet.merge_range(summary_line, summary_name_col, summary_line, summary_nw_normal_col, 'Merged range')
        summary_worksheet.write(summary_line, summary_name_col, title, bold)
        summary_line += 2

        summary_worksheet.set_row(summary_line, 24.75)
        summary_worksheet.merge_range(summary_line, summary_ot_normal_col, summary_line, summary_ot_over_16_hours_col, 'Merged range')
        summary_worksheet.write(summary_line, summary_ot_normal_col, 'OT hours', pink_bg)
        summary_worksheet.write(summary_line, summary_nw_normal_col, 'NW hours\n(22:00-05:00 JPN)', pink_bg)
        summary_line += 1

        summary_worksheet.write(summary_line, summary_name_col, 'Name', light_blue_bg)
        summary_worksheet.write(summary_line, summary_employee_number_col, 'Employee number', light_blue_bg)
        summary_worksheet.write(summary_line, summary_ot_normal_col, 'Normal', light_blue_bg)
        summary_worksheet.write(summary_line, summary_ot_over_16_hours_col, '> 16 hrs', light_blue_bg)
        summary_worksheet.write(summary_line, summary_nw_normal_col, 'Normal', light_blue_bg)

        summary_line += 1

        summary_sum_ot_normal = RelTime(0)
        summary_sum_ot_over_16_hours = RelTime(0)
        summary_sum_nw_normal = RelTime(0)

        crew_leg_date_col = 0
        crew_leg_flt_col = 1
        crew_leg_ci_col = 2
        crew_leg_co_col = 3
        crew_leg_duty_time_col = 4
        crew_leg_ot_normal_col = 5
        crew_leg_ot_over_16_hours_col = 6
        crew_leg_nw_normal_col = 7
        crew_leg_info_col = 8

        for index, crew_employee_number, crew_name, crew_group, duties in jp_crew:
            column.add(Row(Column(crew_employee_number), Column(crew_name)))

            crew_worksheet = workbook.add_worksheet("%s %s" % (crew_employee_number, crew_name))

            crew_worksheet.set_column(crew_leg_date_col, crew_leg_date_col, 10)
            crew_worksheet.set_column(crew_leg_flt_col, crew_leg_flt_col, 9.43)
            crew_worksheet.set_column(crew_leg_ci_col, crew_leg_ci_col, 9.43)
            crew_worksheet.set_column(crew_leg_co_col, crew_leg_co_col, 9.43)
            crew_worksheet.set_column(crew_leg_duty_time_col, crew_leg_duty_time_col, 9.43)
            crew_worksheet.set_column(crew_leg_ot_normal_col, crew_leg_ot_normal_col, 13)
            crew_worksheet.set_column(crew_leg_ot_over_16_hours_col, crew_leg_ot_over_16_hours_col, 13)
            crew_worksheet.set_column(crew_leg_nw_normal_col, crew_leg_nw_normal_col, 16)
            crew_worksheet.set_column(crew_leg_info_col, crew_leg_info_col, 13)

            crew_worksheet.merge_range(0, 0, 0, 5, 'Merged range')
            crew_worksheet.write(0, 0, title, bold)

            crew_worksheet.write(2, 0, 'Name:')
            crew_worksheet.merge_range(2, 1, 2, 2, 'Merged range')
            crew_worksheet.write(2, 1, crew_name)

            crew_worksheet.merge_range(2, 3, 2, 4, 'Merged range')
            crew_worksheet.write(2, 3, 'Employee number:')
            crew_worksheet.write(2, 5, "%s" % crew_employee_number)

            crew_worksheet.write(3, 0, 'Dept:')
            crew_worksheet.write(3, 1, crew_group)

            crew_worksheet.set_row(5, 24.75)
            crew_worksheet.merge_range(5, crew_leg_ot_normal_col, 5, crew_leg_ot_over_16_hours_col, 'Merged range')
            crew_worksheet.write(5, crew_leg_ot_normal_col, 'OT hours', pink_bg)
            crew_worksheet.write(5, crew_leg_nw_normal_col, 'NW hours\n(22:00-05:00 JPN)', pink_bg)

            crew_worksheet.write(6, crew_leg_date_col, 'Date', light_blue_bg)
            crew_worksheet.write(6, crew_leg_flt_col, 'Flight', light_blue_bg)
            crew_worksheet.write(6, crew_leg_ci_col, 'Checkin', light_blue_bg)
            crew_worksheet.write(6, crew_leg_co_col, 'Checkout', light_blue_bg)
            crew_worksheet.write(6, crew_leg_duty_time_col, 'Duty time', light_blue_bg)

            crew_worksheet.write(6, crew_leg_ot_normal_col, 'Normal', light_blue_bg)
            crew_worksheet.write(6, crew_leg_ot_over_16_hours_col, '> 16 hrs', light_blue_bg)
            crew_worksheet.write(6, crew_leg_nw_normal_col, 'Normal', light_blue_bg)
            crew_worksheet.write(6, crew_leg_info_col, 'Information', light_blue_bg)

            crew_line = 7

            crew_sum_ot_normal = RelTime(0)
            crew_sum_ot_over_16_hours = RelTime(0)
            crew_sum_nw_normal = RelTime(0)

            for index, start_hb, end_hb, legs in duties:
                for index, leg_date, leg_fd, leg_ci, leg_co, leg_duty_time, leg_ot_normal, leg_ot_over_16_hours, leg_nw_normal, is_passive_flight in legs:
                    crew_worksheet.write(crew_line, crew_leg_date_col, leg_date, white_bg)
                    crew_worksheet.write(crew_line, crew_leg_flt_col, leg_fd, white_bg)
                    crew_worksheet.write(crew_line, crew_leg_ci_col, reltime_to_string(leg_ci), white_bg)
                    crew_worksheet.write(crew_line, crew_leg_co_col, reltime_to_string(leg_co), white_bg)
                    crew_worksheet.write(crew_line, crew_leg_duty_time_col, reltime_to_string(leg_duty_time), white_bg)
                    crew_worksheet.write(crew_line, crew_leg_ot_normal_col, reltime_to_string(leg_ot_normal, blank_zero=True), white_bg)
                    crew_worksheet.write(crew_line, crew_leg_ot_over_16_hours_col, reltime_to_string(leg_ot_over_16_hours, blank_zero=True), white_bg_bold)
                    crew_worksheet.write(crew_line, crew_leg_nw_normal_col, reltime_to_string(leg_nw_normal, blank_zero=True), white_bg)
                    info_list = []
                    if leg_ot_over_16_hours > RelTime(0):
                        info_list.append("> 16h")
                    if is_passive_flight is True:
                        info_list.append("P")

                    crew_worksheet.write(crew_line, crew_leg_info_col, ' '.join(info_list), white_bg)

                    crew_sum_ot_normal += leg_ot_normal
                    crew_sum_ot_over_16_hours += leg_ot_over_16_hours
                    crew_sum_nw_normal += leg_nw_normal

                    crew_line += 1

            crew_worksheet.merge_range(crew_line, crew_leg_date_col, crew_line, crew_leg_flt_col, 'Merged range')
            crew_worksheet.write(crew_line, crew_leg_date_col, "Sum", light_yellow_bg)
            crew_worksheet.write(crew_line, crew_leg_ot_normal_col, reltime_to_string(crew_sum_ot_normal), light_yellow_bg)
            crew_worksheet.write(crew_line, crew_leg_ot_over_16_hours_col, reltime_to_string(crew_sum_ot_over_16_hours), light_yellow_bg)
            crew_worksheet.write(crew_line, crew_leg_nw_normal_col, reltime_to_string(crew_sum_nw_normal), light_yellow_bg)

            summary_worksheet.write(summary_line, summary_name_col, crew_name, white_bg)
            summary_worksheet.write(summary_line, summary_employee_number_col, crew_employee_number, white_bg)
            summary_worksheet.write(summary_line, summary_ot_normal_col, reltime_to_string(crew_sum_ot_normal), white_bg)
            summary_worksheet.write(summary_line, summary_ot_over_16_hours_col, reltime_to_string(crew_sum_ot_over_16_hours), white_bg)
            summary_worksheet.write(summary_line, summary_nw_normal_col, reltime_to_string(crew_sum_nw_normal), white_bg)
            summary_line += 1

            summary_sum_ot_normal += crew_sum_ot_normal
            summary_sum_ot_over_16_hours += crew_sum_ot_over_16_hours
            summary_sum_nw_normal += crew_sum_nw_normal

        summary_worksheet.merge_range(summary_line, summary_name_col, summary_line, summary_employee_number_col, 'Merged range')
        summary_worksheet.write(summary_line, summary_name_col, "Sum", light_yellow_bg)
        summary_worksheet.write(summary_line, summary_ot_normal_col, reltime_to_string(summary_sum_ot_normal), light_yellow_bg)
        summary_worksheet.write(summary_line, summary_ot_over_16_hours_col, reltime_to_string(summary_sum_ot_over_16_hours), light_yellow_bg)
        summary_worksheet.write(summary_line, summary_nw_normal_col, reltime_to_string(summary_sum_nw_normal), light_yellow_bg)

        workbook.close()

        self.add(column)

    def headerRow(self, dates):
        """Generate table header"""
        left_headers = ['Empno', 'Name', 'Group', 'Sum bid days month 1']
        tmp_row = self.getCalendarRow(dates, leftHeaders=left_headers)
        tmp_csv_row = self.getCalendarRow(dates, leftHeaders=left_headers, csv=True)
        return tmp_row, tmp_csv_row


def setContext(scope='window'):
    global global_context

    global_context = 'default_context'
    context = global_context

    """Run PRT Report in scope 'scope'."""
    if scope == 'plan':
        area = Cui.CuiNoArea
        context = 'sp_crew'
    elif scope == 'object':
        area = Cui.CuiGetCurrentArea(Cui.gpc_info)
        crewId = Cui.CuiCrcEvalString(Cui.gpc_info, area, "object", "crew.%id%")
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, Cui.CuiScriptBuffer, Cui.CrewMode, Cui.CrewMode, [crewId], 0)
        global_context = carmstd.rave.Context("window", Cui.CuiScriptBuffer)
        area = Cui.CuiNoArea
        scope = 'plan'
    else:
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, scope)
    return (context, area)


def runReport(scope='window'):
    (context, area) = setContext(scope)
    nowTime, = R.eval('fundamental.%now%')
    args = 'CONTEXT=%s fromStudio=TRUE starttime=%d' % (context, int(nowTime))
    Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, area, scope,
                                   '../lib/python/report_sources/include/JpOvertimeStatement.py', 0, args)

# End of file

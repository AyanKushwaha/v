"""
 $Header$
 
 Request Reciept

 Lists granted FS and F7S requests
  
 Created:    April 2012
 By:         Anna Olsson, Jeppesen Systems AB

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
import Cui

# constants =============================================================={{{1
TITLE = 'Request Reciept'

class RequestReciept(SASReport):

    def create(self, report_type, crew_id, headers=True):
        object_report = (report_type == "object")
        general_report = not object_report
        # Basic setup
        SASReport.create(self, TITLE, headers=headers, showPlanData=False, usePlanningPeriod=True)
        if not crew_id:
            crew_id = self.arg('crew_id')

        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiNoArea, "internal_object")
        Cui.gpc_set_one_crew_chain(Cui.gpc_info, crew_id)

        # As opposed to the warnings presented in the GUI, this report
        # catches all warnings, regardless of priority
        fs_days_expr = R.foreach(
             R.times('interbids.%%crew_num_requests%%("%s","FS")' %crew_id),
                    'interbids.%%request_start_ix%%("%s","FS",fundamental.%%py_index%%)' %crew_id,
                    'interbids.%%request_end_ix%%("%s","FS",fundamental.%%py_index%%)' %crew_id,
                    'interbids.%%request_days_ix%%("%s","FS",fundamental.%%py_index%%)' %crew_id
            )
        fs_summary_expr = R.foreach(
             R.times('3'),
                     'interbids.%%show_6_month_summary%%("%s", "FS",fundamental.%%py_index%%)' %crew_id ,
                     'interbids.%6_months_start_ix%(fundamental.%py_index%)',
                     'interbids.%6_months_end_ix%(fundamental.%py_index%)',
                     'interbids.%%request_days_in_6_months_ix%%("%s", "FS",fundamental.%%py_index%%)' %crew_id
             )
        fw_days_expr = R.foreach(
             R.times('interbids.%%crew_num_requests%%("%s","FW")' %crew_id),
                    'interbids.%%request_start_ix%%("%s","FW",fundamental.%%py_index%%)' %crew_id,
                    'interbids.%%request_end_ix%%("%s","FW",fundamental.%%py_index%%)' %crew_id,
                    'interbids.%%request_days_ix%%("%s","FW",fundamental.%%py_index%%)' %crew_id
            )
        fw_summary_expr = R.foreach(
             R.times('3'),
                     'interbids.%%show_6_month_summary%%("%s", "FW",fundamental.%%py_index%%)' %crew_id ,
                     'interbids.%6_months_start_ix%(fundamental.%py_index%)',
                     'interbids.%6_months_end_ix%(fundamental.%py_index%)',
                     'interbids.%%request_days_in_6_months_ix%%("%s", "FW",fundamental.%%py_index%%)' %crew_id
             )
        f7s_days_expr = R.foreach(
             R.times('interbids.%%crew_num_requests%%("%s","F7S")' %crew_id),
                    'interbids.%%request_start_ix%%("%s","F7S",fundamental.%%py_index%%)' %crew_id,
                    'interbids.%%request_end_ix%%("%s","F7S",fundamental.%%py_index%%)' %crew_id,
                    'interbids.%%request_days_ix%%("%s","F7S",fundamental.%%py_index%%)' %crew_id
            )

        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where = 'interbids.%%crew_has_any_request%%("%s") and interbids.%%roster_crewid%% = "%s"'%(crew_id,crew_id)),
            'report_common.%crew_string%',
            fs_days_expr,
            fs_summary_expr,
            fw_days_expr,
            fw_summary_expr,
            f7s_days_expr
            )
        rosters, = R.eval("default_context", roster_expr)   

        if not rosters:
            # No warnings were found
            self.add(Text("No request bids for crew", font=Font(weight=BOLD)))

        else:

            # Keep all crew in a list
            crew = list()

            # Loop over all the 'bags' that comes from the RAVE expression
            # and collect the data
            for roster in rosters:
                # print "  ## roster:", roster
                (ix, crew_string, fs_days, fs_summary, fw_days, fw_summary, f7s_days) = roster
                # Format output by looping over the crew with warnings and their warnings

                crew_col = Column()
                # The crew header
                crew_col.add(Row(Text(crew_string, font = self.HEADERFONT)))
                # Space
                crew_col.add(Row(Text('')))
                crew_col.add(Row(Text('')))
                
                col_width = 90

                # Add info about FS days
                if fs_days:
                    crew_col.add(Row(Text("Granted FS Requests", font = self.HEADERFONT), background=self.HEADERBGCOLOUR))
                    fs_column = Column()
                    fs_header_row = Row()
                    fs_header_row.add(Text("Start", font = Font(weight = BOLD)))
                    fs_header_row.add(Text("End", font = Font(weight = BOLD)))
                    fs_header_row.add(Text("Days", font = Font(weight = BOLD)))
                    fs_column.add(fs_header_row)
                    for (ix, start, stop, days) in fs_days:
                          fs_row = Row()
                          fs_row.add(Text(start.ddmonyyyy()[:9], width = col_width))
                          fs_row.add(Text(stop.adddays(-1).ddmonyyyy()[:9], width = col_width))
                          fs_row.add(Text(days))
                          fs_column.add(fs_row)

                    crew_col.add(Row(fs_column))
                    crew_col.add(Row(Text(' ')))
                    
                #Add a summary of FS days for the three closest calendar half years
                # use rave variable if we should display summary 
             
                    
                if (fs_days and fs_summary):
                    add_summary = False
                    fs_summary_column = Column()
                    fs_summary_header_row = Row()
                    fs_summary_header_row.add(Text("Start"))
                    fs_summary_header_row.add(Text("End"))
                    fs_summary_header_row.add(Text("Total Granted Days",font = Font(weight = BOLD)))
                    fs_summary_column.add(fs_summary_header_row)
                    # use rave variable if we should display summary 
                    for(ix, show, start, stop, days) in fs_summary:
                        if show:
                            add_summary = True
                            fs_sum_row = Row()
                            fs_sum_row.add(Text(start.ddmonyyyy()[:9], width =  col_width))
                            fs_sum_row.add(Text(stop.adddays(-1).ddmonyyyy()[:9], width =  col_width))
                            fs_sum_row.add(Text(days))
                            fs_summary_column.add(fs_sum_row)
                    if add_summary:
                        crew_col.add(Row(Text("FS Half Year Summary", font = self.HEADERFONT), background=self.HEADERBGCOLOUR))
                        crew_col.add(Row(fs_summary_column))
                        crew_col.add(Row(Text(' ')))

                # Add info about FW days
                if fw_days:
                    crew_col.add(Row(Text("Granted FW Requests", font = self.HEADERFONT), background=self.HEADERBGCOLOUR))
                    fw_column = Column()
                    fw_header_row = Row()
                    fw_header_row.add(Text("Start", font = Font(weight = BOLD)))
                    fw_header_row.add(Text("End", font = Font(weight = BOLD)))
                    fw_header_row.add(Text("Days", font = Font(weight = BOLD)))
                    fw_column.add(fw_header_row)
                    for (ix, start, stop, days) in fw_days:
                          fw_row = Row()
                          fw_row.add(Text(start.ddmonyyyy()[:9], width = col_width))
                          fw_row.add(Text(stop.adddays(-1).ddmonyyyy()[:9], width = col_width))
                          fw_row.add(Text(days))
                          fw_column.add(fw_row)

                    crew_col.add(Row(fw_column))
                    crew_col.add(Row(Text(' ')))

                #Add a summary of FW days for the three closest calendar half years
                # use rave variable if we should display summary


                if (fw_days and fw_summary):
                    add_summary = False
                    fw_summary_column = Column()
                    fw_summary_header_row = Row()
                    fw_summary_header_row.add(Text("Start"))
                    fw_summary_header_row.add(Text("End"))
                    fw_summary_header_row.add(Text("Total Granted Days",font = Font(weight = BOLD)))
                    fw_summary_column.add(fw_summary_header_row)
                    # use rave variable if we should display summary
                    for(ix, show, start, stop, days) in fw_summary:
                        if show:
                            add_summary = True
                            fw_sum_row = Row()
                            fw_sum_row.add(Text(start.ddmonyyyy()[:9], width =  col_width))
                            fw_sum_row.add(Text(stop.adddays(-1).ddmonyyyy()[:9], width =  col_width))
                            fw_sum_row.add(Text(days))
                            fw_summary_column.add(fw_sum_row)
                    if add_summary:
                        crew_col.add(Row(Text("FW Half Year Summary", font = self.HEADERFONT), background=self.HEADERBGCOLOUR))
                        crew_col.add(Row(fw_summary_column))
                        crew_col.add(Row(Text(' ')))


                # Add info about F7S days
                if f7s_days:
                    crew_col.add(Row(Text("Granted F7S Requests", font = self.HEADERFONT), background=self.HEADERBGCOLOUR))
                    f7s_column = Column()
                    f7s_header_row = Row()
                    f7s_header_row.add(Text("Start", font = Font(weight = BOLD)))
                    f7s_header_row.add(Text("End", font = Font(weight = BOLD)))
                    f7s_header_row.add(Text("Days", font = Font(weight = BOLD)))
                    f7s_column.add(f7s_header_row)
                    for (ix, start, stop, days) in f7s_days:
                          f7s_row = Row()
                          f7s_row.add(Text(start.ddmonyyyy()[:9], width =  col_width))
                          f7s_row.add(Text(stop.adddays(-1).ddmonyyyy()[:9], width = col_width))
                          f7s_row.add(Text(days))
                          f7s_column.add(f7s_row)


                    crew_col.add(Row(f7s_column))

                # Wrap the column in a row to prevent a page break within the warnings
                # for a crew
                crew_row = Row(crew_col)
                self.add(crew_row)

                # Create some distance to the next crew, will unfortunately create
                # some pages with a starting blank line
                self.add(Text(' '))
                self.page0()
            
# End of file

"""
 $Header$
 
 Crew Warning Info

 Lists the warnings for each crew
  
 Created:    April 2007
 By:         Jonas Carlsson, Jeppesen Systems AB

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport

# constants =============================================================={{{1
TITLE = 'Crew Warning Info'

class CrewWarningInfo(SASReport):

    def create(self, report_type, headers=True, context='default_context'):
        object_report = (report_type == "object")
        general_report = not object_report
        # Basic setup
        SASReport.create(self, TITLE, headers=headers, usePlanningPeriod=True)

        # As opposed to the warnings presented in the GUI, this report
        # catches all warnings, regardless of priority
        warning_section_expr = R.foreach(
            R.times('crew_warnings.%crew_nr_section_priorities%(fundamental.%py_index%)',
                    where = 'crew_warnings.%section_priority_warning%(fundamental.%py_index1%, fundamental.%py_index%)'),
            'crew_warnings.%section_priority_code%(fundamental.%py_index1%, fundamental.%py_index%)',
            'crew_warnings.%section_priority_descr%(fundamental.%py_index1%, fundamental.%py_index%)'
            )
        warning_expr = R.foreach(
            R.times('crew_warnings.%crew_nr_warning_sections%',
                    where = 'crew_warnings.%crew_has_warning_in_section%(fundamental.%py_index%)'),
            'crew_warnings.%crew_section_group%(fundamental.%py_index%)',
            warning_section_expr
            )
        roster_expr = R.foreach(
            R.iter('iterators.roster_set', where = 'crew_warnings.%crew_has%'),
            'report_common.%crew_string%',
            'crew_warnings.%warnings_short%',
            'crew_warnings.%use_groups%',
            warning_expr
            )
        rosters, = R.eval(context, roster_expr)

        if not rosters:
            # No warnings were found
            self.add(Text("No warnings for crew", font=Font(weight=BOLD)))

        else:

            # Keep all crew in a list
            crew = list()

            # Loop over all the 'bags' that comes from the RAVE expression
            # and collect the data
            for (ix, crew_string, warnings_short, use_groups, warnings) in rosters:

                # Found a crew with warnings, crew a new entry in the list with
                # an empty warnings dictionary
                data = dict()
                crew.append((crew_string, use_groups, data))

                for (ix, group, section) in warnings:
                    for (ix, code, descr) in section:
                        data[group] = data.get(group, list())
                        data[group].append((code, descr))


            # Format output by looping over the crew with warnings and their warnings
            for (c_str, use_groups, group_dict) in crew:
                crew_col = Column()
                # The crew header
                crew_col.add(Row(Text(c_str, font = self.HEADERFONT), background=self.HEADERBGCOLOUR))

                # Warnings for a crew, grouped by 'group'
                for group in group_dict.keys():
                    group_row = Row()
                    if use_groups:
                        group_row.add(Text(group, font = Font(weight = BOLD)))
                    warning_col = Column()

                    # Warnings for a group
                    for (code, descr) in group_dict[group]:
                        warning_row = Row()
                        warning_row.add(Text(code, font = Font(weight = BOLD)))
                        warning_row.add(Text(descr))
                        warning_col.add(warning_row)

                    group_row.add(warning_col)
                    crew_col.add(group_row)

                # Wrap the column in a row to prevent a page break within the warnings
                # for a crew
                crew_row = Row(crew_col)
                self.add(crew_row)

                # Create some distance to the next crew, will unfortunately create
                # some pages with a starting blank line
                self.add(Text(' '))
                self.page0()
            
# End of file

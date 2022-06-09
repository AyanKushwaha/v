"""
 $Header$
 
 New Hire Follow Up

 Lists all crew in need of a new hire follow up.
  
 Created:    September 2014
 By:         Ralf Damaschke, HiQ Goteborg
 
"""

# imports
import carmensystems.rave.api as R
import carmensystems.publisher.api as P
from report_sources.include.SASReport import SASReport
from AbsDate import AbsDate
from RelTime import RelTime

# constants
CONTEXT = 'default_context'
TITLE = 'New Hire Follow Up'

class NewHireFollowUp(SASReport):
    def create(self):
        # Basic setup
        SASReport.create(self, TITLE, orientation=P.LANDSCAPE, usePlanningPeriod=True)
        
        table = P.Column()
        table.add(P.Row(
                P.Text("New hire emp no"), 
                P.Text("New hire name"), 
                P.Text("ILC date"), 
                P.Text("Last day for next follow-up flight"),
                P.Text("Assigned in pp"),
                P.Text("Mentor emp no"),
                P.Text("Mentor name"),
                font=P.Font(weight=P.BOLD)))
        
        follow_ups, = R.eval(CONTEXT, R.foreach(R.iter('iterators.roster_set', where=('training.%crew_can_have_follow_up_in_pp%')),
                'crew.%id%',
                'crew.%firstname%',
                'crew.%surname%',
                'crew.%new_hire_ilc_date%', 
                'training.%current_new_hire_follow_up_end_date%',
                'training.%scheduled_follow_up_in_pp%',
                'crew.%new hire_mentor%',
                'crew.%firstname_at_date_by_id%(crew.%new_hire_mentor%, now)',
                'crew.%surname_at_date_by_id%(crew.%new_hire_mentor%, now)'))
        
        for(ix, crew_id, firstname, surname, ilc_date, follow_up_end_date, assigned_date, mentor_id, mentor_firstname, mentor_surname) in follow_ups:
            table.add(P.Row(crew_id, self.format_name(firstname, surname), str(AbsDate(ilc_date)), str(AbsDate(follow_up_end_date)), assigned_date, mentor_id, 
                            self.format_name(mentor_firstname, mentor_surname) ))
        self.add(table)
        
        
    def format_name(self, firstname, surname):
        if surname is None or firstname is None:
            return ""
        else:
            return surname + ', ' + firstname

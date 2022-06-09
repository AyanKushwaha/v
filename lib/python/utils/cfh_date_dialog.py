#####

##
#####
__version__ = "$Revision$"

"""
cfh_date_dialog
Module for selecting period from user. Checks that period is non-negative and has valid input
@date: 21Apr2008
@author: Per Groenberg
@org Jeppesen Systems AB
"""
import Cui
import Cfh
import AbsDate
import AbsTime
import RelTime
import tempfile
import os
import utils.CfhFormClasses as CFC
import carmensystems.rave.api as R

CancelFormError = CFC.CancelFormError

def _testForm():
    try:
        form = PeriodSelectionForm(dateForm=True)
        print form()
        print form.get_period()
    except CancelFormError, err:
        print str(err)

            
class PeriodSelectionForm(CFC.BasicCfhForm):
    """Generic period selection form, the dateForm flag toggles date/time
    """
    def __init__(self,dateForm=False):

        self.time_or_date = ('Time','Date')[dateForm]
        title = 'Please enter %ss:'%self.time_or_date.lower()
        CFC.BasicCfhForm.__init__(self,title)

        (default_start, default_end) = R.eval('fundamental.%now%',
                                              'add_months(fundamental.%now%,1)')
        self.add_date_combo(0, 1, 'start', 'Start %s:'%self.time_or_date,
                            str(default_start), date=dateForm)
        self.add_date_combo(1, 1, 'end', 'End %s:'%self.time_or_date,
                            str(default_end), date=dateForm)
        self.dateForm = dateForm
        
    def check_ok_action(self):
        (s_t,e_t) = self.get_period()
        if s_t is None or e_t is None:
            return "Please enter valid %ss"%self.time_or_date.lower()
        if s_t > e_t:
            return 'Start time must be smaller than end time'
        return ''
    
    def assign_default_values(self, start_t, end_t):
        start_t = str(start_t)
        end_t = str(end_t)
        if self.dateForm:
            start_t = start_t.split()[0]
            end_t = end_t.split()[0]
        self.start_field.assign(start_t)
        self.end_field.assign(end_t)
           
    def get_period(self):
        """
        Gets period from values in form
        """
        start_val = self.start_field.getValue()
        end_val = self.end_field.getValue()
        
        if not start_val or not end_val:
            return (None,None)
        try:
            if self.dateForm:
                start_time = AbsDate.AbsDate(start_val)
                end_time = AbsDate.AbsDate(end_val)
            else:
                start_time = AbsTime.AbsTime(start_val)
                end_time = AbsTime.AbsTime(end_val)
            return (start_time, end_time)
        except:
            return (None,None)
    @property
    def start(self):
        return self.get_period()[0]
    @property
    def end(self):
        return self.get_period()[1]

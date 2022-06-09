#

#
__version__ = "$Revision$"
"""
SelectCrewForm
Module for doing:
Select crew by id, empno or surname, needed to be able to select
crew with empty rosters on empno

Dropped filter principle and mark match by commenting out them
@date:09Sep2008
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""

import utils.CfhFormClasses as CFC
import Select

import Cui
import Cfh
import Errlog

global SELECT_CREW_FORM
SELECT_CREW_FORM = None


class CrewSelectBox(CFC.BasicCfhForm):
    def __init__(self,title='Filter by crew Id/Empno/Surname'):
        
        CFC.BasicCfhForm.__init__(self,title)

        self.add_filter_combo(0,1, "filter_method", "Filter Method", "REPLACE",
                              ["REPLACE","SUBFILTER","ADD"])

        self.add_filter_combo(2,1,"crewid","Crew Id:",'*',[])
        self.add_filter_combo(3,1,"empno","Employment Nr:",'*',[])
        self.add_filter_combo(4,1,"surname","Surname:",'*',[])
          
        #Add reset button
        self.reset = CFC.ResetAction(self, "RESET", self.button_area, "Reset Form", "_Reset") 
   
    def get_form_bypass(self):
        return {'FILTER_METHOD':self.filter_method,
                'crew.%id%':self.crew_id or '*',
                'crew.%extperkey%': self.empno or '*',
                'crew.%surname%':self.surname or '*'}
    
    @property
    def filter_method(self):
        return self.filter_method_field.getValue()
    @property
    def crew_id(self):
        return self.crewid_field.getValue()
    @property
    def empno(self):
        return self.empno_field.getValue()
    @property
    def surname(self):
        return self.surname_field.getValue()

def select_crew(area=Cui.CuiWhichArea):
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, area)
    global SELECT_CREW_FORM
    if not SELECT_CREW_FORM:
        SELECT_CREW_FORM = CrewSelectBox()
        
    try:
        SELECT_CREW_FORM()
        filter_expr = SELECT_CREW_FORM.get_form_bypass()
        Select.selectCrew(filter_expr, usePlanningArea=True, area=area)
    except CFC.CancelFormError, cf:
        Errlog.log("SelectCrewFrom::select_crew:: user cancelled form")
        return 1
    except Exception, e:
        Errlog.log("SelectCrewFrom::select_crew::"+str(e))
        return -1
    

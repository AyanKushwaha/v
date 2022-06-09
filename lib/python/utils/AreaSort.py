#

#
__version__ = "$Revision$"
"""
AreaSort
Module for doing:
TO maintain window sorting we store objects 
@date:06Feb2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""


import Cui
import utils.CfhFormClasses as CFC
import Errlog

class InteractiveForm(CFC.BasicCfhForm):
    """
    We need to store interactive form values, hence we need our own little form
    """
    def __init__(self, title=""):
        CFC.BasicCfhForm.__init__(self,title)

        self.add_filter_combo(0,1, "sort_order", "Sort Order", "",[], upper=False)
  
        #Add reset button
        self.reset = CFC.ResetAction(self, "RESET", self.button_area, "Reset Form", "_Reset") 
   
    def get_form_bypass(self):
        return {'FORM': 'interactive_sort',
                'METHOD_STR': self.sort_order,
                'OK': '',
                }
    @property
    def sort_order(self):
        return self.sort_order_field.getValue()
    
#Wrapper object for keeping track of current sort
INTERACTIVE = 'interactive'

class AreaSorter:
    """
    Sorts area, but stores no values
    """
    def sort(self, area, mode, value):
        if str(mode).lower() == INTERACTIVE:
            self.sort_interactive(area)
        else:
            Cui.CuiSortArea(Cui.gpc_info,area,mode,value)

    def sort_interactive(self, area):
        try:
            form = InteractiveForm('Sort rows in Window%d'%(int(area)+1))
            form()
            Cui.CuiSortInteractive(form.get_form_bypass(),Cui.gpc_info,area)
            value = form.sort_order
            mode = Cui.CuiSortRuleValue # We sort by rulevalues in interactive mode
            return (mode, value)
        except CFC.CancelFormError, err:
            Errlog.log('AreaSort:%s'%err)
            return None
        
    def restore_sorting(self,area):
        """
        Don't affect anything
        """
        return 0
    
class StoreAreaSorter(AreaSorter):
    """
    Stores valeus of sort to retore current sorting
    """
    def __init__(self):
        self.__current_sorting = {}
        
    def sort(self, area, mode, value=None):
        """
        Sort given area according to mode and value
        """
        if str(mode).lower() == INTERACTIVE:
            form_values = self.sort_interactive(area)
            if form_values:
                mode, value = form_values
            else:
                return 1
                 
        else:
            Cui.CuiSortArea(Cui.gpc_info,area,mode,value)
        self.__current_sorting[area] = [mode,value]
        
    def restore_sorting(self, area):
        """
        Used stored values to restore sorting
        """
        if self.__current_sorting.has_key(area):
            mode = self.__current_sorting[area][0]
            value = self.__current_sorting[area][1]
            Errlog.log('AreaSorter::Restoring area sort in window'+\
                       '%d using %s:%s'%(int(area+1),str(mode),value))
            Cui.CuiSortArea(Cui.gpc_info,area,mode,value)
            

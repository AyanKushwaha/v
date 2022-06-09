#

#
__version__ = "$Revision$"
"""
CfhFormClasses
Module for doing:
Help Classes for Cfh Forms
@date:25Sep2008
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""
import Cfh
import AbsTime
import RelTime
# Help Classes in forms

class ResetAction(Cfh.Function):
    def __init__(self, parent, *args):
        Cfh.Function.__init__(self,parent, *args)
        self._parent = parent
    def action(self):
        self._parent.reset_form()

class TimeString(Cfh.String):
    """A wrapper for Date Entry which checks input"""
    def __init__(self,parent,date, *args):
        self._date = date
        Cfh.String.__init__(self,parent, *args)
                              
    def check(self,text):
        try:
            AbsTime.AbsTime(text)
        except:
            return "Please enter a valid %s in format %s" %\
                   (['time','date'][self._date],
                    ['01FEB2008 00:00','01FEB2008'][self._date])
        return Cfh.String.check(self, text)

class RelTimeString(Cfh.String):
    """A wrapper for Date Entry which checks input"""
    def __init__(self,parent,date, *args):
        self._date = date
        Cfh.String.__init__(self,parent, *args)
                              
    def check(self,text):
        try:
            RelTime.RelTime(text)
        except:
            return "Please enter a valid time in format 12:30"
        return Cfh.String.check(self, text)

class Number(Cfh.Number):
    """A wrapper for Number Entry which checks input against limit"""
    def __init__(self,parent, limit, *args):
        self._limit = limit
        Cfh.Number.__init__(self,parent, *args)
                              
    def check(self,number):
        if int(number) > self._limit and self._limit <> 0:
            return "Number must be at most %s" %self._limit
        else:
            return Cfh.Number.check(self, number)
    
class CfhCheckDone(Cfh.Done):
    def __init__(self, parent,*args):
        Cfh.Done.__init__(self, parent, *args)
        self._parent = parent 
        self._check_methods = []
    def register_check(self,check_func, arg=None):
        if check_func not in self._check_methods:
            self._check_methods.append([check_func, arg])
            
    def action(self):
        for func,arg in self._check_methods:
            if arg:
                message = func(arg)
            else:
                message = func()
            if message:
                break
        if not message: 
            Cfh.Done.action(self)
        else:
            self._parent.message(message,True) #isError = True
        
class CancelFormError(Exception):
    def __init__(self,err_str):
        self._err_str = err_str
    def __str__(self):
        return "%s Form Cancelled"%self._err_str

class BasicCfhForm(Cfh.Box):
    """
    Basic form for Cfh, uses dynamic layout with loc and dim
    All entered field will get name name+'_field'
    Added combos will be created like 'label: field'
    """
    _FIELD_SUFFIX = '_field'
    _LABEL_SUFFIX = '_label'

    def __init__(self,title='Basic Form:'):
        self._is_built = False
        self._string_components = {}
        self._abstime_components = {}
        self._reltime_components = {}
        self._toggle_components = {}
        self._number_components = {}
        self._delta_x = 0
        self._delta_y = 10
        self._x_positions = []
        self._form_name = ''.join([("_",char)[char.isalpha()] for char in title]).upper()
        Cfh.Box.__init__(self,self._form_name)
        self.setText(title)
        self.button_area = Cfh.Area(Cfh.Loc(-1,-1))
        self.done = CfhCheckDone(self, "OK", self.button_area, "Ok", "_Ok")
        self.done.register_check(self.check_ok_action)
        self.cancel = Cfh.Cancel(self, "CANCEL", self.button_area, "Cancel", "_Cancel")

    def check_ok_action(self):
        """
        Override to something useful
        """
        return None
    
    def add_label(self, x, y, name, label_str, style=Cfh.CfhSLabelNormal):
        """
        Adds a normal label to form
        """
        self._check_name(name)
        x, y = self._check_positions(x, y)
        label_name = name+BasicCfhForm._LABEL_SUFFIX
        label = Cfh.Label(self,label_name.upper(),
                          Cfh.Area(Cfh.Dim(20, 1), Cfh.Loc(x,y)),
                          label_str)
        label.setStyle(style)
        setattr(self,label_name,label)

    def add_number_combo(self, x, y, name, label_str, default, limit=0):
        """
        Number component
        """
        self._check_name(name)
        x, y = self._check_positions(x, y)
        label_name = name+BasicCfhForm._LABEL_SUFFIX
        field_name = name+BasicCfhForm._FIELD_SUFFIX
        label = Cfh.Label(self,label_name.upper(),
                          Cfh.Area(Cfh.Dim(5, 1), Cfh.Loc(x,y)),
                          label_str)
        field = Number(self, limit, field_name.upper(),
                       Cfh.Area(Cfh.Dim(2, 1),
                                Cfh.Loc(x+self._delta_x, y+self._delta_y)),
                       default)
        
        setattr(self,label_name,label)
        setattr(self,field_name, field)
        self._number_components[field] = default
        
    def add_date_combo(self, x, y, name, label_str, default, date=True, reltime=False):
        """
        Time component, Label: Time/Date
        """
        self._check_name(name)
        x, y = self._check_positions(x, y)
        label_name = name+BasicCfhForm._LABEL_SUFFIX
        field_name = name+BasicCfhForm._FIELD_SUFFIX
        label = Cfh.Label(self,label_name.upper(),
                          Cfh.Area(Cfh.Dim(10, 1), Cfh.Loc(x,y)),
                          label_str)
        if reltime:
            field = RelTimeString(self, date, field_name.upper(),
                           Cfh.Area(Cfh.Dim(10, 1),
                                    Cfh.Loc(x+self._delta_x, y+self._delta_y)),
                           8,default)
        else:
            field = TimeString(self,date,field_name.upper(),
                           Cfh.Area(Cfh.Dim(10, 1),
                                    Cfh.Loc(x+self._delta_x, y+self._delta_y)),
                           [15,9][date],default)
        field.setMandatory(True)
        setattr(self,label_name,label)
        setattr(self,field_name, field)
        if reltime:
            self._reltime_components[field] = default
        else:
            self._abstime_components[field] = default
        
    def add_filter_combo(self, x,y , name, label_str, default, options=[], upper=True,
                         style = Cfh.CfhSChoiceCombo):
        """
        text string selection, if options the menu will be set
        """
        self._check_name(name)
        x, y = self._check_positions(x, y)
        label_name = name+BasicCfhForm._LABEL_SUFFIX
        field_name = name+BasicCfhForm._FIELD_SUFFIX
        label = Cfh.Label(self,label_name.upper(),
                          Cfh.Area(Cfh.Dim(10, 1), Cfh.Loc(x,y)),
                          label_str)
        if options:
            max_length = max([len(option) for option in options])
        else:
            max_length = 100
        field = Cfh.String(self,field_name.upper(),
                           Cfh.Area(Cfh.Dim(max(10,int(len(default)/1.5)), 1),
                                    Cfh.Loc(x+self._delta_x, y+self._delta_y)),
                           max_length,
                           default)
        field.setMandatory(True)
        if options:
            field.setMenuOnly(True)
            field.setMenuString(";"+";".join(options))
        if upper:
            field.setTranslation(Cfh.CfhEntry.ToUpper)
        field.setStyle(style)
        setattr(self,label_name,label)
        setattr(self,field_name, field)
        self._string_components[field] = default
        
    def add_toggle_combo(self, x, y, name, label_str, default):
        """
        Toggle button
        """
        self._check_name(name)     
        x, y = self._check_positions(x, y)
        label_name = name+"_label"
        field_name = name+"_field"
        label = Cfh.Label(self,label_name.upper(),
                          Cfh.Area(Cfh.Dim(10, 1), Cfh.Loc(x,y)),
                          label_str)
        field = Cfh.Toggle(self,field_name.upper(),
                           Cfh.Area(Cfh.Dim(10, 1), Cfh.Loc(x+self._delta_x, y+self._delta_y)),
                           default)
        field.setMandatory(True)
        setattr(self,label_name,label)
        setattr(self,field_name, field)
        self._toggle_components[field] = default

    def _check_name(self, name):
        """
        Check that name is not already used
        """
        label_name = name+BasicCfhForm._LABEL_SUFFIX
        field_name = name+BasicCfhForm._FIELD_SUFFIX
        if hasattr(self, label_name) or hasattr(self, field_name):
            raise Exception('Component %s already exists in form'%name)
    
    def _check_positions(self, x, y):
        if self._delta_x == 0:
            x = x + 1
        
        self._x_positions.append(x + self._delta_x)
        
        return x, y
    
    def get_values(self):
        """
        Get field values
        """
        return [AbsTime.AbsTime(comp.valof()) for comp in \
                self._abstime_components.keys()] + \
                [RelTime.RelTime(comp.valof()) for comp in \
                self._reltime_components.keys()] + \
                [comp.valof() for comp in
                 self._string_components.keys() +\
                 self._toggle_components.keys()]
    
    def reset_form(self):
        
        items = self._abstime_components.items() + \
                self._reltime_components.items() +\
                self._string_components.items() +\
                self._toggle_components.items()

        for field, default in items:
            field.assign(default)
            
    def build(self):
        """
        If we want to resuse form, we can only build once
        """
        if not self._is_built:
            self.add_label(max(self._x_positions) + self._delta_x, 0, "X_MAX_SEPARATOR", "")

            Cfh.Box.build(self)

        self._is_built = True
    
    def __call__(self):
        """Main entry point."""
        self.build()
        self.show(1)
        if self.loop():
            raise CancelFormError(self._form_name)
        return self.get_values()

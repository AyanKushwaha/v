#

#
__version__ = "$Revision$"
"""
duty_break_handler
Module for doing:
Manually setting and removing duty break tag to crew_activity
@date:20Aug2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""
import Errlog

import Cui
import Gui
import Variable
import carmensystems.rave.api as r

import carmusr.Attributes as Attributes
import carmusr.HelperFunctions as HF

_MODULE = 'duty_break_handler'
_LOG_TEMPLATE = _MODULE+':: %s manual duty break for activity %s %s (UTC) for crewid %s'

try:
    _DUTY_BREAK_ATTRIBUTE, =  r.eval('default_context','attributes.%duty_break_attribute%')
except:
    # best guess
    _DUTY_BREAK_ATTRIBUTE = "DUTY_BREAK"

def clear_attribute():
    set_attribute_val(None)

def set_break_attribute():
    set_attribute_val("DUTY_BREAK")

def set_merge_attribute():
    set_attribute_val("DUTY_MERGE")

def set_attribute_val(val):
    try:
        area=Cui.CuiAreaIdConvert(Cui.gpc_info,Cui.CuiWhichArea)
        current_leg = Variable.Variable("")
        Cui.CuiGetSelectionObject(Cui.gpc_info, area, Cui.LegMode, current_leg)

        leg_id = current_leg.value
        
        leg_object = HF.LegObject(leg_id, area)
        
        (crew_id,
         attr,
         st,
         code) = leg_object.eval('crew.%id%',
                                'attributes.%leg_duty_break_attribute%',
                                "leg.%start_utc%",
                                "leg.%code%")
    
        Errlog.log('Old value was "%s" on leg %s' % (attr, str(leg_id)))
        if val is None:
            Attributes.RemoveAssignmentAttrCurrent(_DUTY_BREAK_ATTRIBUTE)
            Errlog.log(_LOG_TEMPLATE%('Removed', code, str(st), crew_id))
        else:
            Attributes.SetAssignmentAttrCurrent(_DUTY_BREAK_ATTRIBUTE, str=val)
            Errlog.log(_LOG_TEMPLATE%('Added "' + val+'"', code, str(st), crew_id))
    except Exception, err:
        Errlog.log(_MODULE+':: Error changing duty break: %s'%str(err))
        Gui.GuiMessage('Manual duty break could not be changed')
        return -1
    return 0

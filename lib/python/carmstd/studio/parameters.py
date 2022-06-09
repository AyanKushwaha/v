
"""
Rules and Parameters
------------------------------
Studio Application

Functionality:
RuleSet class for handling rule sets
ParameterSet class for handling parameter sets
Parameters for handling single parameters

"""
import Cui
import os
#import string
import Variable
import carmensystems.rave.api as r

#------------------------ Rule Set -------------------------
def getCurrentRuleSetName():
    path=Variable.Variable("")
    Cui.CuiCrcGetRulesetName(path)
    if path.value == '':
        raise ValueError("No RuleSet loaded")
    return os.path.basename(path.value)

def loadRuleSet(name):
    """
    Loads the specified rule set in studio
    """
    path="$CARMTMP/crc/rule_set/GPC/$ARCH/" +name
    Cui.CuiCrcLoadRuleset(Cui.gpc_info, path)
    
#------------------------ Parameter Set -------------------------
def loadParameterSet(name):
    """
    Loads the specified parameter set
    """
    Cui.CuiCrcLoadParameterSet(Cui.gpc_info,name)
    
def saveParameterSet(name):
    """
    Saves the parameter set
    """
    Cui.CuiCrcSaveParameterSet(Cui.gpc_info, "", name)
    
#------------------------ Parameter -------------------------
useParameterCache=0

def setParameterValue(name,value):
    Cui.CuiCrcSetParameterFromString(name,str(value))

def getParameterValue(name):
    return r.eval(r.expr(name))[0] 

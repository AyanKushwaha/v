
"""
Rules and Parameters
------------------------------
Matador Application

Functionality:
RuleSet class for handling rule sets
ParameterSet class for handling parameter sets
Parameters for handling single parameters

"""
import MatadorScript

#------------------------ Parameter -------------------------
def setParameterValue(name,value): 
    MatadorScript.set_rule_parameter(name,str(value))

def getParameterValue(name): 
    return MatadorScript.set_rule_parameter(name,str(value))

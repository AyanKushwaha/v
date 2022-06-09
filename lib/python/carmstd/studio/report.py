#######################################################

# report.py
# -----------------------------------------------------
# Application: Studio
#
# Created:    2005-12-02
# By:         Carmen
#######################################################
"""
This module contains functionality for creating crg reports
in python.
"""
import os
import Cui
import parameters
import Variable
import tempfile


def saveReport(name,fullPath,format,area=None,scope=None):
    """
    Saves a report in a specified format.
    """

    if area==None:
        area=Cui.CuiNoArea
    if scope==None:
        if area!=Cui.CuiNoArea:
            scope="window"
        else:
            scope="plan"

    # Verify loaded rule set
    parameters.getCurrentRuleSetName()

    # Run the report and save the result in out (Must be a Variable)
    if format=="ascii":
        Cui.CuiCrgCreatePlainReport(Cui.gpc_info, area, scope,
                                    name, Variable.Variable(fullPath), "ascii")        
    elif format=="pdf":
        pdlTmp = tempfile.mktemp(suffix="_PDL")
        pdlTmpCsl=Variable.Variable(pdlTmp)
        fontDir=os.path.expandvars('$CARMSYS/data/crg_fonts')
        fontCfg="pdlfonts.cfg.latin1"
        
        pdlBin=os.path.expandvars('$CARMSYS/bin/$ARCH/pdl')
        Cui.CuiCrgCreatePlainReport(Cui.gpc_info, area, scope,
                                    name, pdlTmpCsl, "dump")
        os.system('cd ' + fontDir + ';' + pdlBin+' -o '+fullPath+" -d pdf -f . -F "+fontCfg + " " + pdlTmp)
        os.unlink(pdlTmp)
    else:
        raise ValueError("Unsupported format "+format)

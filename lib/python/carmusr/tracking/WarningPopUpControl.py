#

#
"""
WarningPopUpControl

Contains functions to control whether the warnings
in roster operations should be enabled or not.

"""

import Crs
import Csl
import Integer
import traceback


# Set up a csl object on import for shorter code later on.
csl = Csl.Csl()

# This variable is needed to keep track on the first time getSuppressCheckLegalityDialogue
# is called 
init_done = False

def getSuppressCheckLegalityDialogue():
    """
    Read default value from resource file and set the toggle.

    """
    global init_done
    
    try:
        if not init_done:
            csl.setInteger("show_legality_dialogues", Integer.Integer(1))
            Crs.CrsSetAppModuleResource("default","dialogues","suppressCheckLegalityDialogue","False","Set by toolbar toggle")
            init_done = True
    except:
        traceback.print_exc()


def setSuppressCheckLegalityDialogue():
    """
    Read current status of toggle button and set the resource. The resource is not used for 
    saving the state between sessions since it is always set to true at start up. 
    It seems however that the actual dialog is displayed when the resource is set to true. It
    probably a part of carmsys.
    """

    try:
        boolInt = csl.getInteger("show_legality_dialogues").getRep()
        # Set resource from csl-value
        suppress = ("True","False")[boolInt]            
        Crs.CrsSetAppModuleResource("default","dialogues","suppressCheckLegalityDialogue",suppress,"Set by toolbar toggle")
    except:
        traceback.print_exc()

        
    


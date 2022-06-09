##########################
#
# Set vinstructor tag
#
##########################
"""
1. Filter out instructor legs with missing instructor tag
2. Set instructor tag on selected legs
"""

import Select
import Cui
import carmusr.training_attribute_handler as Training

def filterAndSelectInstrLegs():
    """
    Filter out instructor legs without instructor code
    and select them
    """

    studioarea = Cui.CuiArea0
    
    # Unmark all legs first
    Cui.CuiDisplayObjects(Cui.gpc_info, studioarea, Cui.CrewMode, Cui.CuiShowAll)
    Cui.CuiUnmarkAllLegs(Cui.gpc_info, studioarea, "window")

    leg_select = {"leg.%has_started%": "FALSE",
                  "leg.%has_instructor_code%": "FALSE",
                  "training.%instructor_to_be_tagged_at_publish%": "TRUE",
                  "FILTER_METHOD": "REPLACE",
                  'FILTER_MARK': 'LEG',
              }

    Select.select(leg_select,
                  windowArea=studioarea)
                

def setInstrTagOnMarkedLegs():

    studioarea = Cui.CuiScriptBuffer

    leg_select = {"marked": "TRUE",
                  "FILTER_METHOD": "REPLACE"}


    Select.select(leg_select,
                  studioarea,
                  Cui.CrewMode)
    Training.set_instructor_tag(
        mode="MARKED", attribute="", area=studioarea, flags = 0)

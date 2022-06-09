#

#
"""
This module is imported to the __main__ module by StudioCustom.py at start up.
It should not be imported by other modules

The module contains CTF import menu commands for Studio
"""
import carmdata.Ctf2Rrl as Ctf2Rrl

def CreateLpPlanFromCTF():
    """
    Creates A local plan from CTF
    """
    CREATE_LP = True
    CREATE_SP = False
    CREATE_ENV = False
    ONLY_DATED = False
    SPECIFY_CREW_PLAN = False
    Ctf2Rrl.Ctf2Rrl(CREATE_LP,CREATE_SP,CREATE_ENV,ONLY_DATED,SPECIFY_CREW_PLAN)

def CreateLpSpPlanFromCTF():
    """
    Creates a sub plan and local plan from CTF
    """
    CREATE_LP = True
    CREATE_SP = True
    CREATE_ENV = False
    ONLY_DATED = False
    SPECIFY_CREW_PLAN = False
    Ctf2Rrl.Ctf2Rrl(CREATE_LP,CREATE_SP,CREATE_ENV,ONLY_DATED,SPECIFY_CREW_PLAN)

def CreateSpPlanFromCTF():
    """
    Creates a sub-plan from already existing Local plan
    """
    CREATE_LP = False
    CREATE_SP = True
    CREATE_ENV = False
    ONLY_DATED = False
    SPECIFY_CREW_PLAN = False
    Ctf2Rrl.Ctf2Rrl(CREATE_LP,CREATE_SP,CREATE_ENV,ONLY_DATED,SPECIFY_CREW_PLAN)



# Import menu commands for rostering
def CreateCcrSpPlansFromCTF():
    """
    Creates default plans
    """
    CREATE_LP = False
    CREATE_SP = True
    CREATE_ENV = True
    Ctf2Rrl.Ctf2Rrl(CREATE_LP,CREATE_SP,CREATE_ENV)

def CreateCCRPlansFromCTF():
    """
    Creates a sub-plan from already existing Local plan
    """
    CREATE_LP = True
    CREATE_SP = True
    CREATE_ENV = True
    ONLY_DATED = False
    SPECIFY_CREW_PLAN = False
    Ctf2Rrl.Ctf2Rrl(CREATE_LP,CREATE_SP,CREATE_ENV,ONLY_DATED,SPECIFY_CREW_PLAN)


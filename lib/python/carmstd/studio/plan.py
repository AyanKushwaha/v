#######################################################

#  plan.py
# -----------------------------------------------------
#  Studio application  
#  This file should include normal actions on different
#  plan. This includes local plans (LocalPlan) and 
#  sub-plans (SubPlan).
#
# ------------------------------------------------------
# Created:    2005-12-01
# By:         Carmen
#######################################################
import Cui
import Variable
import string
import os


def unload():
    """
    Unloads the plans
    """
    Cui.CuiUnloadPlans(Cui.gpc_info, Cui.CUI_SILENT)

#----------------------- local plan -------------------------
def getCurrentLocalPlanPath():
    """
    Returns the localplan path
    If no localplan is loaded a ValueError is thrown
    """
    localplan_path = Variable.Variable("")
    Cui.CuiGetLocalPlanPath(Cui.gpc_info, localplan_path)
    if localplan_path.value == '':
        raise ValueError("No LocalPlan loaded")   
    return localplan_path.value

def getLocalPlanEtabPath():
    """
    Returns the path to the LpLocal etab dir
    """
    var=Variable.Variable("")
    Cui.CuiGetLocalPlanEtabLocalPath(Cui.gpc_info,var)
    return var.value

def loadLocalPlan(filePath):
    """
    Loads the local plan specified by filePath
    """
    Cui.CuiOpenLocalPlan(Cui.gpc_info,filePath)

def saveLocalPlan(filePath=None):
    """
    Saves the loaded localplan
    filePath: If set it will be saved with this name, otherwise
              will it be saved with the same name as before
    """
    flags = Cui.CUI_SAVE_DONT_CONFIRM | Cui.CUI_SAVE_SILENT | Cui.CUI_SAVE_FORCE | Cui.CUI_SAVE_SKIP_SP
    if filePath==None:
        Cui.CuiSavePlans(Cui.gpc_info,flags) 
    else:
        formdata = {
            'FORM': 'LOCAL_PLAN_PROPERTIES',
            'LP_NAME':filePath
            }
        parts = string.split(filePath, os.sep)
        lpPath = string.join(parts[len(parts)-4:-1], os.sep)
        tname=Variable.Variable(lpPath)
        Cui.CuiSaveLocalPlan(formdata,Cui.gpc_info,tname,flags)

def createLocalPlanFromSSIM(fpAttr):
    """
    Creates a new localplan from SSIM using fp2rrl

    fpAttr: Bypass Attributes as an hashtab (Where the keys are the same as in the Cfh-form fp2rrl)

    Note: Currently requires link from the CARMUSR.
    """
    flags=Cui.CUI_CREATE_LP_SYNCHRONOUS|Cui.CUI_CREATE_LP_SILENT|Cui.CUI_CREATE_LP_FORCE
    Cui.CuiCreateLocalPlan(fpAttr, Cui.gpc_info,flags)


#----------------------- sub plan -------------------------
def getCurrentSubPlanName():
    """
    Returns the subplan name
    If no subplan is loaded a ValueError is thrown
    
    NOTE: This should not be used in batch mode
    """
    subplan = Variable.Variable("")
    Cui.CuiGetSubPlanName(Cui.gpc_info, subplan)
    if subplan.value == '':
        raise ValueError("No SubPlan loaded")
    return subplan.value

def getSubPlanEtabPath():
    """
    Returns the path to the SpLocal etab dir
    """
    var=Variable.Variable("")
    Cui.CuiGetSubPlanEtabLocalPath(Cui.gpc_info,var)
    return var.value

def loadSubPlan(filePath):
    """
    Loads the specified sub-plan
    Dig out pathes relative LOCAL_PLAN directory
    """
    parts = string.split(filePath, os.sep)
    lpPath = string.join(parts[len(parts)-4:-1], os.sep)
    spPath = string.join(parts[len(parts)-4:], os.sep)
    flags = Cui.CUI_OPEN_PLAN_SILENT|Cui.CUI_OPEN_PLAN_DONT_CONFIRM|Cui.CUI_OPEN_PLAN_FORCE
    Cui.CuiOpenSubPlan(Cui.gpc_info, lpPath, spPath, flags)

def loadSubPlanSolution(filePath,solution):
    """
    Loads the specified solution in the sub-plan
    Dig out pathes relative LOCAL_PLAN directory
    """ 
    parts = string.split(filePath, os.sep)
    lpPath = string.join(parts[len(parts)-4:-1], os.sep)
    spPath = string.join(parts[len(parts)-4:], os.sep)
    flags=Cui.CUI_LOAD_SOLUTION_DONT_CONFIRM|Cui.CUI_LOAD_SOLUTION_SILENT|Cui.CUI_LOAD_SOLUTION_FORCE
    Cui.CuiLoadSolution(Cui.gpc_info,lpPath,spPath, solution,flags)

def loadSubPlanAsEnv(filePath):
    """
    Loads the specified plan as environment plan
    """
    parts = string.split(filePath, os.sep)
    lpPath = string.join(parts[len(parts)-4:-1], os.sep)
    spPath = string.join(parts[len(parts)-4:], os.sep)
    flags = Cui. CUI_LOAD_SOLUTION_DONT_CONFIRM | Cui.CUI_LOAD_SOLUTION_SILENT | Cui.CUI_LOAD_SOLUTION_FORCE

    Cui.CuiLoadEnvSubPlan(Cui.gpc_info, lpPath, spPath, flags)

def saveSubPlan(fileName=None):
    """
    Saves the loaded subplan
    name: If set it will be saved with this name (basename), otherwise
          will it be saved with the same name
    """
    if fileName==None:
        Cui.CuiSaveSubPlan(Cui.gpc_info, 0, 7)
    else:
        Errlog.log("Saving sp: %s" % fileName)
        tname=Variable.Variable(fileName)
        Cui.CuiSaveSubPlan(Cui.gpc_info, tname, 7)

def saveSubPlanWithNewLocalPlan(filePath):
    """
    Move sub plan to new local plan
    """
    flags = Cui.CUI_MOVE_SP_TO_NEW_LP_DEFAULT | Cui.CUI_MOVE_SP_TO_NEW_LP_SILENT
    tname=Variable.Variable(filePath)
    Cui.CuiMoveSubPlan(Cui.gpc_info,tname,0,0,flags)

def createSubPlanFromCtf(ctfAttr):
    """
    Creates a subplan from CTF using ctf2rrl
    ctfAttr: Bypass attributes as an hashtab (Where the keys are the same as in the Cfh-form ctf2rrl)
    """
    flags=Cui.CUI_CREATE_SP_SYNCHRONOUS|Cui.CUI_CREATE_SP_SILENT|Cui.CUI_CREATE_SP_FORCE|Cui.CUI_CREATE_SP_DONT_CONFIRM
    Cui.CuiCreateSubPlanFromCtf(ctfAttr, Cui.gpc_info, flags)

def loadCrew(filePath):
    """
    Loads the crew plan specified in filePath.
    The crew plan must reside in the directory defined in the
    carmen resource CrewPlanDir 
    """
    parts=string.split(filePath, os.sep)
    if len(parts)==1:
        fileName=filePath
    else:
        fileName=parts[-1]
    Cui.CuiLoadCrewPlan(Cui.gpc_info,fileName,"")

def loadGroundDuties(groundDutyFile):
    """Loads a ground duty file into the current localplan

    groundDutyFile: Filename from GROUND_DUTY_FILES
    """
    carmuser = os.environ["CARMUSR"]
    Cui.CuiLoadGroundDuties(Cui.gpc_info,os.path.join(carmuser,'GROUND_DUTY_FILES',groundDutyFile),1)

def splitSubPlan(splitCrew,splitTrip,Name='Trips',slice=0):
    """
    Splits the currently loaded subplan, by the map parameters

    splitTrip: Rave variable for splitting trips
    splitCrew: Rave variable for splitting crew
    """
    Cui.CuiSplitSubPlan(Cui.gpc_info,splitCrew,splitTrip,Name,1, slice)

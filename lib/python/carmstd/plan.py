#######################################################
#
# Plan
# -----------------------------------------------------
#  
#  This file should include normal actions on different
#  plan. This includes local plans (LocalPlan) and 
#  sub-plans (SubPlan).
#
# ------------------------------------------------------
# Created:    2004-11-02
# By:         Carmen
#######################################################

import os
from application import application

if application=="Studio":
    import carmstd.studio.plan as plan
elif application=="Matador":
    import carmstd.matador.plan as plan

def getCurrentLocalPlan():
    """
    Returns a local plan instance of the
    currently loaded local plan
    """
    return LocalPlan(plan.getCurrentLocalPlanPath())

def getCurrentSubPlan():
    """
    Returns a sub plan instance of the
    currently loaded sub plan
    """
    return SubPlan(plan.getCurrentSubPlanName(),LocalPlan(plan.getCurrentLocalPlanPath()))

def getCurrentSubPlanName():
    """
    Returns the name of the currently loaded sub plan
    """
    return plan.getCurrentSubPlanName()

def get_current_sub_plan():
    return getCurrentSubPlan()

def unload():
    """
    Unloads the currently loaded LocalPlan & SubPlan
    """
    plan.unload()

class LocalPlan:
    """
    Class for local plan.
    Holds the locla plan atttributes and contains
    methods for loading and saving plans.
    """
    def __init__(self,filePath):
        """
        Arguments:
        filePath: String. Path relative to the directory
                  defined by the carmen resource LocalPlanPath
        """
        self.filePath=filePath
        
    def getFileName(self):
        """
        Get the name of the localplan
        """
        return os.path.basename(self.getFilePath())
    
    def getFilePath(self):
        """
        Returns the file path of the local plan relative to
        the directory defined by the carmen resource LocalPlanPath
        """
        return self.filePath
    
    def getEtabPath(self):
        """
        Get the etab path for localplan local etables
        
        return: filePath
        """
        return plan.getLocalPlanEtabPath()
    
    def load(self):
        """
        Load the localplan
        """
        plan.loadLocalPlan(self.filePath)
    def save(self):
        """
        Saves the LocalPlan with same name.

        exception ValueError if the plan is not loaded
        """
        if not (self==getCurrentLocalPlan()):
            raise ValueError("The localplan is not loaded, and hence can it not be saved!")
        plan.saveLocalPlan()
    def saveAs(self,filePath):
        """
        Saves the the LocalPlan as filePath
        Arguments:
        filePath: String. Path relative to the directory
                  defined by the carmen resource LocalPlanPath
        exception ValueError if the plan is not loaded
        """
        if not (self==getCurrentLocalPlan()):
            raise ValueError("The localplan is not loaded, and hence can it not be saved!")
        self.filePath=filePath
        plan.saveLocalPlan(self.filePath)
        
    def createFromSSIM(self,ssimFilePath,start,end,iata_codes='*',carriers='*',
                       dated_mode='Yes',time_offset='0:00',set_op_suffix='Yes'):
        """
        Creates a local plan from a SSIM file.
        Arguments:
        ssimFilePath: String. Name of SSIM file in the directory
                      defined by the carmen resource FpFilesDir
        start: String. Local period start in format 01Jan2001
        end: String. Local period end in format 01Jan2001
        iata_codes: String. Aircraft types
        carriers: String.
        dated_mode: String
        time_offset: String. Reltime format
        set_op_suffix:String. Solves conflicting legs with suffix

        Requires that the SSIM files is available in FP_FILES from carmusr
        """
        fpAttr={
            "FORM": "FP2RRL",
            "ACTIVE_FP_FILES_1":ssimFilePath,
            "START": start,
            "END": end,
            "TIME_OFFSET": time_offset,
            "DATED_MODE": dated_mode,
            "ACTIVE_CARRIERS": carriers,
            "IATA_CODES": iata_codes,
            "LP_NAME": self.getFilePath(),
            "SET_OPSUFFIX_OF_CONFLICTING_LEGS": set_op_suffix
            }
        plan.createLocalPlanFromSSIM(fpAttr)
        
    def __eq__(self,other):
        return isinstance(other,LocalPlan) and self.getFilePath() == other.getFilePath()

class SubPlan:
    """
    Class for a subplan.

    Ex.
    SubPlan('BASE',LocalPlan('$CARMUSR/LOCAL_PLAN/FLEET/OLD_VERSION/ALL_BASES'))
    SubPlan.load()
    SubPlan.saveAs('BASE',LocalPlan('$CARMUSR/LOCAL_PLAN/FLEET/NEW_VERSION/ALL_BASES'))
    SubPlan.loadCrew('CrewTable.etab')
    SubPlan.save()
    """
    def __init__(self,fileName,localplan):
        """
        Initialise a SubPlan

        fileName: Name of the sublan
        localplan: The localplan where the subplan resides (default is the currently loaded subplan)
        """
        self.fileName=fileName
        self.localplan=localplan
    def getFileName(self):
        """
        Get the name of the subplan
        return: fileName
        """
        return self.fileName
    def getFilePath(self):
        """
        Get the filePath to the subplan
        return: filePath relative to directory defined by
                the carmen resource LocalPlanPath
        """
        return os.path.join(self.localplan.getFilePath(),self.getFileName())

    def get_file_path(self):
        return self.getFilePath()

    def getEtabPath(self):
        """
        Get the etab path for subplan local etables
        return: filePath
        """
        return plan.getSubPlanEtabPath()
    
    def getLocalPlan(self):
        """
        Returns an instance of the loaded local plan.
        """
        return self.localplan
    
    def load(self):
        """
        Load the subplan into memory
        """
        plan.loadSubPlan(self.getFilePath())
        
    def loadSolution(self,solution):
        """
        Load a solution of a subplan.
        solution: String. Name of the solution to load.
                  E.g. Solution_1 
        """
        plan.loadSubPlanSolution(self.getFilePath(),solution)
        
    def loadBestSolution(self):
        """
        Loads the best solution to the subplan (According to the link best_solution). 
        """
        self.loadSolution('best_solution')
    def loadLastSolution(self):
        """
        Loads the last solution of a subplan. (The solution with the highest number)
        """
        snr = 0
        while(os.path.exists(os.path.join(subplan.getFilePath(),'APC_FILES',"Solution_%d" % snr+1))):
            snr += 1
        if snr==0:
            raise ValueError("No solution exists, or bad path to the subplan")
        self.loadSolution("Solution_%d" % snr)
    def loadAsEnvironment(self):
        """
        Loads the specified plan as environment
        """
        plan.loadSubPlanAsEnv(self.getFilePath())
    def isCurrent(self):
        """
        Checks whether the subplan is in memory
        """
        return self==getCurrentSubPlan()
    def loadCrew(self,fileName):
        """
        Loads a crew plan into the subplan

        fileName: Name of crew table to load.
                  Either path or name

        exception ValueError if the plan is not loaded
        """
        if self.isCurrent():
            plan.loadCrew(fileName)
        else:
            raise ValueError("The subplan is not loaded, and hence can it not be saved!")
    def save(self):
        """
        Saves the SubPlan with same name.

        exception ValueError if the plan is not loaded
        """
        self.saveAs(self.fileName)
    
    def saveAs(self,fileName,localplan=None):
        """
        Saves the the SubPlan as filePath

        exception ValueError if the plan is not loaded
        """
        if not localplan:
            localplan=self.getLocalPlan()
        if not self.isCurrent():
            raise ValueError("The subplan is not loaded, and hence can it not be saved!")
        self.fileName=fileName
        if not localplan==self.localplan:
            self.localplan=localplan
            plan.saveSubPlanWithNewLocalPlan(self.getFilePath())
        else:
            plan.saveSubPlan(self.getFileName())
            
    def createFromCtf(self,ctfFilePath,crewTableFileName=None):
        """
        Creates a sub-plan from a Ctf file in the loaded local plan
        Args:
        ctfFilePath: String, name of the ctf file in the directory
                     defined by the carmen resource IntxFilePath
        crewTableFileName: String, name of the crew plan in the
                           dir defined by the Carmen resource CrewPlanDir
        """
        ctfAttr={
            'FORM':'CTF2RRL',
            'INPUT_CTF_FILES':ctfFilePath,
            'INPUT_LOCAL_PLAN':self.getLocalPlan().getFilePath(),
            'SP_NAME':self.getFileName()}
        if crewTableFileName:
            ctfAttr['INPUT_CREW_FILES']=crewTableFileName
        plan.createSubPlanFromCtf(ctfAttr)

    def split(self,crewVariableName,tripVariableName,slice=0):
        """
        Not finished
        Splits subplan, by the map parameters

        splitTrip: Rave variable for splitting trips
        splitCrew: Rave variable for splitting crew

        returns a list of created SubPlans
        """
        #if not self.isCurrent():
        #    raise ValueError('The subplan is not loaded, and hence can it not be splitted!')
        print getCurrentSubPlan().getFilePath()
        print self.getFilePath()
        plan.splitSubPlan(crewVariableName,tripVariableName,self.getFileName(),slice)
        # !!! Not yet implemented
        createdSubplans=[]
        return createdSubplans
    
    def __eq__(self,other):
        return isinstance(other,SubPlan) and self.getFilePath() == other.getFilePath()

if __name__=='__main__':
    import sys
    try:
        SubPlan(sys.argv[2],LocalPlan(sys.argv[1])).load()
    except:
        SubPlan(sys.argv[1]).load()

def local_plan_is_loaded():
    """Checks whether a local plan is loaded.

    @return: True if a local plan is loaded, False otherwise.
    @rtype: bool
    """
    try:
        getCurrentLocalPlan()
    except ValueError:
        return False
    return True

def sub_plan_is_loaded():
    """Checks whether a sub-plan is loaded.

    @return: True if a sub-plan is loaded, False otherwise.
    @rtype: bool
    """
    try:
        getCurrentSubPlan()
    except ValueError:
        return False
    return True

#

#
"""
A module for creating plans from CTF files by starting Ctf2Rrl.
"""

import dircache
import glob
import os
import os.path
import signal
import tempfile

import Errlog
import Cfh
import carmstd.cfhExtensions as cfhExtensions
import Crs
import Csl
import Cps
import Localization


def Ctf2RrlChildHandler(pid, status, childData):
    """
    Given to Cps.Spawn() to be called when the process is terminated.
    """
    
    # childData is a tuple containing (command, descr, logFile, errFile, flags)

    # Show log file
    title = Localization.MSGR("Logfile from Ctf2Rrl.")

    if os.WIFEXITED(status):
        if os.WEXITSTATUS(status) == 0: # os.WEXITSTATUS(status) returns the exit code.
            title += " " + Localization.MSGR("Program finished sucessfully.")
        else: 
            title += " " + Localization.MSGR("Program exited with an error code.")
    elif os.WTERMSIG(status):
        title += " " + Localization.MSGR("Program terminated.")
    else:
        title += " " + Localization.MSGR("Program terminated abnormally.")
    cfhExtensions.showFile(childData[2], title)
    
    
def getLocalPlanList(onlyListDatedLocalPlans = False):
    """
    Returns a list of all local plans (on the form a/b/c) in the current CARMUSR.
    Takes an optional argument onlyListDatedLocalPlans (default False).
    """
    
    localPlanDir = Crs.CrsGetModuleResource("config", Crs.CrsSearchModuleDef, "LocalPlanPath")
    list = []
    for localPlan in glob.glob(localPlanDir + "/*/*/*/localplan"):
        if not os.path.isfile(localPlan) or not os.path.getsize(localPlan):
            continue
        if onlyListDatedLocalPlans and not os.path.isfile(os.path.join(os.path.dirname(localPlan), ".Dated")):
            continue
        list.append(os.path.dirname(localPlan[len(localPlanDir):]))
    return list


def Ctf2Rrl(createLocalPlan = False, createSubPlan = True, createEnvPlan = True,
        onlyListDatedLocalPlans = True, specifyCrewPlan = True, specifyDates = False,
        checkboxForceStandard = False, trafficDaysInUDOR = False,
        logfile = "$CARMTMP/logfiles/Ctf2Rrl"):
    """
    Shows a form where arguments to Ctf2Rrl is given. Then calls the binary (located
    through a resource) with these arguments. The process is started with Cps.Spawn()
    and the logfile is shown when the process terminates.
    """

    # Find binary
    ctfBin = Crs.CrsGetModuleResource("Ctf2Rrl", Crs.CrsSearchModuleDef, "Ctf2Rrl")
    if ctfBin == None:
        Errlog.set_user_message(Localization.MSGR("Could not find Ctf2Rrl binary."))
        return

    frm = Cfh.Box("CTF2RRL")

    # Add buttons
    ok = Cfh.Done(frm, "OK")
    cancel = Cfh.Cancel(frm, "CANCEL")

    # Add fields
    ctfFile = Cfh.FileName(frm, "CTF_FILE", 0)
    # List CTF files in file name field
    ctfDir = Crs.CrsGetModuleResource("config", Crs.CrsSearchModuleDef, "IntxFilesPath")
    if ctfDir == None:
        Errlog.set_user_message(Localization.MSGR("Could not retrieve resource for IntxFilesPath."))
        return
    ctfFileList = [""] + dircache.listdir(ctfDir) # First string is the title of the pick list
    ctfFile.setMenu(ctfFileList)
    ctfFile.setMenuOnly(True)
    ctfFile.setEditable(False)

    crewplan = None
    if specifyCrewPlan:
        crewplan = Cfh.FileName(frm, "CREW_PLAN", 0)
        crewplanCrsValue = Crs.CrsGetModuleResource("config", Crs.CrsSearchModuleDef, "CrewPlanDir")
        if crewplanCrsValue == None:
            Errlog.set_user_message(Localization.MSGR("Could not retrieve resource for CrewPlanDir."))
            return
        # The crew plan dir must be under $CARMUSR
        crewplanDir = os.path.expandvars("$CARMUSR") + "/" + crewplanCrsValue 
        crewplanList = [""] + dircache.listdir(crewplanDir) # First string is the title of the pick list
        crewplan.setMenu(crewplanList)
        crewplan.setMenuOnly(True)
        crewplan.setEditable(False)

    localPlan = None
    if createLocalPlan or createSubPlan or createEnvPlan:
        localPlan = Cfh.PathName(frm, "LOCAL_PLAN", 0, "", 3, 3)
        if not createLocalPlan:
            # List existing local plans. First string is the title of the pick list.
            localPlanList = [""] + getLocalPlanList(onlyListDatedLocalPlans) 
            localPlan.setMenu(localPlanList)
            localPlan.setMenuOnly(True)
            localPlan.setEditable(False)

    subPlan = None
    if createSubPlan:
        subPlan = Cfh.PathName(frm, "SUB_PLAN", 0, "", 1, 1)

    envPlan = None
    if createEnvPlan:
        envPlan = Cfh.PathName(frm, "ENV_PLAN", 0, "", 1, 1)

    startDate = None
    endDate = None
    if specifyDates:
        startDate = Cfh.Date(frm, "START_DATE", -1) # -1 as default value leaves the field empty
        endDate = Cfh.Date(frm, "END_DATE", -1)

    forceStandard = None
    if checkboxForceStandard:
        forceStandard = Cfh.Toggle(frm, "FORCE_STANDARD", 0)

    # Define the layout of the form
    layout = """
FORM;CTF2RRL;`Create plans from CTF`
FIELD;CTF_FILE;`CTF file`
FIELD;START_DATE;`Start date`
FIELD;END_DATE;`End date`
FIELD;CREW_PLAN;`Crew plan`
FIELD;LOCAL_PLAN;`Local plan`
FIELD;SUB_PLAN;`Sub-plan`
FIELD;ENV_PLAN;`Environment plan`
FIELD;FORCE_STANDARD;`Force plan type to standard`
BUTTON;OK;`OK`;`_OK`
BUTTON;CANCEL;`Cancel`;`_Cancel`
"""

    # Create layout as a temporary CFH file
    cfhFilePath = tempfile.mktemp()
    cfhFile = open(cfhFilePath, "w")
    cfhFile.write(layout)
    cfhFile.close()

    # Load the temporary CFH file as a form and delete the file
    frm.load(cfhFilePath)
    os.unlink(cfhFilePath)

    frm.show(True)
    
    ctfCommand = ""
    if frm.loop() == Cfh.CfhOk and ctfFile.valof():
        # If a logfile exists - remove it.
        if os.path.isfile(os.path.expandvars(logfile)):
            os.unlink(os.path.expandvars(logfile))

        ctfArgs = " -i " + os.path.normpath(ctfDir + "/" + ctfFile.valof()) # valof() may return truncated name
        ctfArgs += " -l %L" # Cps.Spawn() replaces %L with logfile
        if localPlan and localPlan.valof():
            if createLocalPlan:
                ctfArgs += " -t " + localPlan.valof()
            if subPlan and subPlan.valof():
                ctfArgs += " -o " + localPlan.valof() + "/" + subPlan.valof()
            if envPlan and envPlan.valof():
                ctfArgs += " -p " + localPlan.valof() + "/" + envPlan.valof()
        if startDate and startDate.valof() and startDate.valof() >= 0:
            ctfArgs += " -s " + startDate.toString(startDate.valof())
        if endDate and endDate.valof() and startDate.valof() >= 0:
            ctfArgs += " -e " + endDate.toString(endDate.valof())
        if crewplan and crewplan.valof():
            ctfArgs += " -c " + crewplan.valof()
        if forceStandard and forceStandard.valof():
            ctfArgs += " -d"
        if trafficDaysInUDOR:
            ctfArgs += " -q"
        ctfCommand = ctfBin + ctfArgs

    if ctfCommand:
        # Run command.
        #
        # Cps.Spawn() takes flags as a string argument. From man page:
        #
        # 'i'; indicate when the process ends (popup)
        # 's'; save the logfile (else automatically deleted)
        # 'k'; kill sub-process when parent exits
        # 'g'; run in separate process group
        # 'u'; can't be killed by user
        # 'e'; alert user if process doesn't return 0
        # 'h'; hide from user
        # 'p'; prevent multiple starts (with same descr),
        #      send SIGUSR2 to existing process instead.
        # 'q'; silent

        logfilePath = os.path.normpath(os.path.expandvars(logfile))
        ctfProcess = Cps.Spawn(ctfCommand, "Ctf2Rrl", "s", Ctf2RrlChildHandler, logfilePath)
        Cps.Wait(ctfProcess)
        
if __name__ == "__main__":

    Ctf2Rrl()

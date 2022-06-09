#####################################################

#
# A module for the fairness functionality in rostering
#
# Contains:
#     Creating Fairness target values
#     Fetch/update crew fairness data for long term fairness
#

import Cui
import Cfh
import AbsDate
import AbsTime
import RelTime
import Errlog
import carmstd.rave as rave
import carmstd.cfhExtensions as cfhExtensions
import carmensystems.rave.api as R
import carmusr.HelperFunctions as HelperFunctions
import carmensystems.mave.etab as etab
import modelserver as M
import os
import re
import tempfile
import Variable as PYV

########################################################################
# Create new fairness target values for all non-hidden crew in the
# planning area

def mins2ReltStr(minutes):
    """Helper function for formatting of reltimes. Takes an int as argument."""
    hrs = int(minutes+0.5)/60
    min = int(minutes+0.5)%60
    string = "%d:%02d"%(hrs,min)
    return string

def getTempDirectory():
    v = PYV.Variable('dummy')
    Cui.CuiGetSubPlanEtabLocalPath(Cui.gpc_info, v)
    spLocalPath = v.value
    return spLocalPath

def getTotalWork(element, subelement, group):
    args = (element, subelement, group)
    (prework, fixedwork) = R.eval("sp_crew",
                                  'studio_fairness.%%python_preassigned_work%%("%s","%s","%s")'%args,
                                  'studio_fairness.%%python_fixed_work%%("%s","%s","%s")'%args
                                  )
    openwork, = R.eval("sp_crrs",
                       'studio_fairness.%%python_open_work_trips%%("%s","%s","%s")'%args
                       )
    return prework + openwork - fixedwork

def getTotalWorkRate(element, subelement, group):
    args = (element, subelement, group)
    workrate, = R.eval("sp_crew",
                       'studio_fairness.%%python_total_work_rate%%("%s","%s","%s")'%args
                       )
    return workrate
                       
def createFairnessTargetValues():
    if HelperFunctions.isDBPlan():
        cfhExtensions.show("createFairnessTargetValue: Should not run in Database!")
        Errlog.log("In Fairness::createFairnessTargetValue: Should not run in Database!")
        return
    Errlog.log("In Fairness::createFairnessTargetValues: Creating Fairness factors...")
        
    # Find list of all active elements and decide if they are customized or not
    if not cfhExtensions.confirm("Regenerate fairness targets for all crew and trips in plan? This might take several minutes.", title="Generate new targets"):
        Errlog.log("In Fairness::createFairnessTargetValues: Cancelled by the user.")
        return None

    # Write targets here
    dirToUse = getTempDirectory()
    targetsOut = os.path.join(dirToUse, "fairness_target_cache.etab")
    personalTargetsOut = os.path.join(dirToUse, "fairness_personal_targets_cache.etab")
    crewOut = os.path.join(dirToUse, "fairness_crew_cache.etab")
    
    # Retrieve element list
    MAX_FAIRNESS_ELEMENTS = 30
    elementList, = R.eval(R.foreach(R.times(MAX_FAIRNESS_ELEMENTS),
                            'fairness.%string1_ix%',
                            'fairness.%string2_ix%',
                            'fairness.%is_customized_target_ix%',
                            'fairness.%distribute_ix%'))
    
    #print elementList
    fairness_groups, = R.eval("sp_crew",
                              R.foreach(R.iter('iterators.roster_set',
                                               where=('planning_area.%crew_is_in_planning_area%'
                                                      )),
                                        'fairness.%fairness_crew_group%'))
    
    fairnessCrewGroups = []
    for dummy, fgroup in fairness_groups:
        if fgroup in fairnessCrewGroups:
            pass
        else:
            fairnessCrewGroups.append(fgroup)
            
    print fairnessCrewGroups

    scheduledCustomTargets = {}
    fullTimeTargets = {}
    for dummy, element, subelement, customized, active in elementList:
        # Skip non-set element
        if element == "" or not active:
            continue
        # Transform the customized string, will not affect its boolean property
        if not customized:
            customized = ""
        Errlog.log("In Fairness::createFairnessTargetValues: creating target for %s-%s %s"%(element,subelement,customized and "(custom)"))

        if not customized:
            # We have a standard target
            for group in fairnessCrewGroups:
                args = (element, subelement, group)
                workrate = getTotalWorkRate(element, subelement, group)
                work = getTotalWork(element, subelement, group)
                try:
                    target = (100*work+0.0)/workrate
                except:
                    target = 0

                key = (element, subelement, group) # Left crew group undefined
                fullTimeTargets[key] = (work, workrate, target)

        if customized:
            # We have a customized target
            # Since customized targets can be dependent on each other
            # we can't just generate it for each element that is iterated
            # here. Instead we schedule it for later
            Errlog.log("In Fairness::createFairnessTargetValues: scheduling target generation for custom element %s-%s "%(element,subelement))
            scheduledCustomTargets[element] = element

    ##################################################################################
    # Generation of custom targets below
    # This code is very implementation specific
    # Customized targets requires a specific set of Fairness_crew_group settings.
    # Fairness crew group will not be used automatically here
    
    # 1. SAS "CC DUTY TIME" with subelements LH, SH, TOT and crew groups APKL APKK ASKL ASKK AHKL AHKK
    if scheduledCustomTargets.has_key("CC DUTY TIME"):
        Errlog.log("In Fairness::createFairnessTargetValues: running target generation for custom element CC DUTY TIME")
        # Check crew-group settings
        allowedGroups = ["AP,KL", "AP,KK", "AS,KL", "AS,KK", "AH,KL", "AH,KK"]
        for group in fairnessCrewGroups:
            if not group in allowedGroups:
                Errlog.log("In Fairness::createFairnessTargetValues: custom target CC DUTY TIME can't handle group: '%s'"%group)
                cfhExtensions.show("The custom target CC DUTY TIME can't handle fairness group %s. Please change fairness crew group parameters."%group, title="Error")
                return
        customElementCCDUTYTIME(fullTimeTargets)

    # 2. SAS "CC DUTY DAYS" with subelements LH, SH, TOT and crew groups APKL APKK ASKL ASKK AHKL AHKK
    if scheduledCustomTargets.has_key("CC DUTY DAYS"):
        Errlog.log("In Fairness::createFairnessTargetValues: running target generation for custom element CC DUTY DAYS")
        # Check crew-group settings
        allowedGroups = ["AP,KL", "AP,KK", "AS,KL", "AS,KK", "AH,KL", "AH,KK"]
        for group in fairnessCrewGroups:
            if not group in allowedGroups:
                Errlog.log("In Fairness::createFairnessTargetValues: custom target CC DUTY DAYS can't handle group: '%s'"%group)
                cfhExtensions.show("The custom target CC DUTY DAYS can't handle fairness group %s. Please change fairness crew group parameters."%group, title="Error")
                return
        customElementCCDUTYDAYS(fullTimeTargets)
        

    #############################
    # Here we write targets and crew factors to file
            
    targetKeys = fullTimeTargets.keys()
    crewLines = []

    # Write etab headers
    targetFile = open(targetsOut, "w")
    targetFile.write("""5
SString1,
SString2,
SCrewFunc,
IITarget,
RRTarget,
""")
    crewFile = open(crewOut, "w")
    crewFile.write("""5
SCrewId,
SString1,
SString2,
IWorkrate,
ISenFactor,
""")
    personalTargetsFile = open(personalTargetsOut, "w")
    personalTargetsFile.write("""5
SCrewId,
SString1,
SString2,
IIPTarget,
RRPTarget,
""")
    
    for key in targetKeys:
        #print "in second loop"
        #print key
        target = int(fullTimeTargets[key][2])
        targetrel = mins2ReltStr(target)
        
        # Write to file
        targetFile.write('"%s","%s","%s", %s, %s,\n'%(key[0],key[1],key[2],target,targetrel))
                     
        crewList, = R.eval('sp_crew', R.foreach(R.iter('iterators.roster_set',
                                                       where='studio_fairness.%%crew_share_work%%("%s","%s","%s")'%(key[0], key[1], key[2])),
                                                'crew.%id%',
                                                'studio_fairness.%%python_crew_work_rate%%("%s","%s")'%(key[0], key[1])))
        #print crewList
        for crew in crewList:
            crewFile.write('"%s","%s","%s", %s, 0,\n'%(crew[1], key[0], key[1], crew[2]))

            # Calculate personal target
            crewTargetInt = (target * crew[2])/100
            crewTargetRel = mins2ReltStr(crewTargetInt)
            personalTargetsFile.write('"%s","%s","%s", %s, %s,\n'%(crew[1],key[0],key[1],crewTargetInt, crewTargetRel))

    
    targetFile.close()
    crewFile.close()
    personalTargetsFile.close()

    
    
    Cui.CuiCrcRefreshEtabs(os.path.dirname(targetsOut),
                           Cui.CUI_REFRESH_ETAB_FORCE)
    Errlog.log("In Fairness::createFairnessTargetValues: done creating targets.")
    cfhExtensions.show("Fairness tables created")
    return

def customElementCCDUTYTIME(fullTimeTargets):
    Errlog.log("In Fairness::customElementCCDUTYTIME: calculating custom targets.")

    # AP, CC DUTY TIME elements
    workrateAPKL = getTotalWorkRate("CC DUTY TIME", "LH", "AP,KL")
    workrateAPKK = getTotalWorkRate("CC DUTY TIME", "SH", "AP,KK")
    workAPKL = getTotalWork("CC DUTY TIME", "LH", "AP,KL")
    workAPKK = getTotalWork("CC DUTY TIME", "SH", "AP,KK")
    targetAPKL = 0
    targetAPKK = 0
    try:
        targetAPKL = (workAPKL+0.0)/workrateAPKL
    except:
        targetAPKL = 0
    try:
        targetAPKK = (workAPKK+0.0)/workrateAPKK
    except:
        targetAPKK = 0
        
    print "************"
    print "AP DUTY TIME"
    print " WorkRate LH APKL: " +str(workrateAPKL/100)
    print " Work(Hours) LH APKL: " +str(workAPKL/100)
    print " WorkRate SH APKL: " +str(workrateAPKK/100)
    print " Work(Hours) SH APKK: " +str(workAPKK/100)
    print " No-share target AP,KL: " + str(targetAPKL)
    print " No-share target AP,KK: " + str(targetAPKK)
     
    FKL = 0
    if targetAPKL < targetAPKK:
        FKL = (workAPKK - workrateAPKK * targetAPKL + 0.0)/(workrateAPKK + workrateAPKL)
        targetAPKK = (workAPKK-FKL*workrateAPKL+0.0)/workrateAPKK
        print " APKL can help APKK"
        print "   rebate size = " + str(FKL)
        print "   new target APKL: " + str(targetAPKL+FKL)
        print "   new target APKK: " + str(targetAPKK)

    # We don't store total work and workrate anymore
    fullTimeTargets[("CC DUTY TIME", "LH", "AP,KL")] = (0, 0, int(0.5+100*targetAPKL))
    fullTimeTargets[("CC DUTY TIME", "SH", "AP,KL")] = (0, 0, int(0.5+100*FKL))
    fullTimeTargets[("CC DUTY TIME", "SH", "AP,KK")] = (0, 0, int(0.5+100*targetAPKK))
    fullTimeTargets[("CC DUTY TIME", "TOT", "AP,KL")] = (0, 0, int(0.5+100*targetAPKK))
    fullTimeTargets[("CC DUTY TIME", "TOT", "AP,KK")] = (0, 0, int(0.5+100*targetAPKK))
     
    # DUTY TIME FOR AS & AH
    # FACTOR FOR weighting work between AS & AH, changing this factor will make AS work 0.9 of AH in total.
    FACTOR_AS_AH = 1.0

    workrateASKL = getTotalWorkRate("CC DUTY TIME", "LH", "AS,KL")
    workrateASKK = getTotalWorkRate("CC DUTY TIME", "SH", "AS,KK")
    workrateAHKK = getTotalWorkRate("CC DUTY TIME", "SH", "AH,KK")
    workrateAHKL = getTotalWorkRate("CC DUTY TIME", "LH", "AH,KL")

    workAHKL = getTotalWork("CC DUTY TIME", "LH", "AH,KL")
    workAHKK = getTotalWork("CC DUTY TIME", "SH", "AH,KK")
    workASKL = getTotalWork("CC DUTY TIME", "LH", "AS,KL")

    try:
        targetAHKL = (workAHKL+0.0)/workrateAHKL
    except:
        targetAHKL = 0
    try:
        targetASKL = (workASKL+0.0)/workrateASKL
    except:
        targetASKL = 0
    try:
        targetASAHKK = (workAHKK+0.0)/(workrateAHKK+FACTOR_AS_AH*workrateASKK)
    except:
        targetASAHKK = 0

    print "************"
    print "AS/AH DUTY TIME"
    print " WorkRate ASKL: " +str(workrateASKL/100)
    print " WorkRate ASKK: " +str(workrateASKK/100)
    print " Work(Hours) ASKL: " +str(workASKL/100)
    print " WorkRate AHKL: " +str(workrateAHKL/100)
    print " Work(Hours) AHKL: " +str(workAHKL/100)
    print " WorkRate AHKK: " +str(workrateAHKK/100)
    print " Work(Hours) AHKK: " +str(workAHKK/100)
    print " No-share target AS,KL: " +str(targetASKL)
    print " No-share target AH,KL: " +str(targetAHKL)
    print " No-share target ASAH,KK: " +str(targetASAHKK)

    FAHKL = 0
    FASKL = 0
    if targetAHKL < targetASAHKK and targetASKL < targetASAHKK:
        FAHKL = (workAHKK - (targetAHKL-targetASKL)*workrateASKL-(workrateAHKK+workrateASKK)*targetAHKL)/((workrateAHKK+workrateASKK) + (workrateAHKL + workrateASKL))
        FASKL = targetAHKL+FAHKL-targetASKL
        targetASAHKK = (workAHKK - FAHKL * (workrateAHKL + workrateASKL) - (targetAHKL-targetASKL)*workrateASKL)/(workrateAHKK+workrateASKK)
        print " AHKL and ASKL can help ASAHKK"
        print "   rebate size AHKL = " + str(FAHKL) + " ASKL = " + str(FASKL)
        print "   new AHKL target: " + str(targetAHKL+FAHKL)
        print "   new ASKL target: " + str(targetASKL+FASKL)
        print "   new ASAHKK target: " + str(targetASAHKK)
    else:
        # WARNING NOT IMPLEMENTED YET
        cfhExtensions.show("Info: \nThe fairness cases where ASKL and AHKL do not\n help ASAHKK is not implemented", title="INFO!!!")

    fullTimeTargets[("CC DUTY TIME", "LH", "AS,KL")] = (0, 0, int(0.5+100*targetASKL))
    fullTimeTargets[("CC DUTY TIME", "SH", "AS,KL")] = (0, 0, int(0.5+100*FASKL))
    fullTimeTargets[("CC DUTY TIME", "LH", "AH,KL")] = (0, 0, int(0.5+100*targetAHKL))
    fullTimeTargets[("CC DUTY TIME", "SH", "AH,KL")] = (0, 0, int(0.5+100*FAHKL))
    fullTimeTargets[("CC DUTY TIME", "SH", "AS,KK")] = (0, 0, int(0.5+100*targetASAHKK))
    fullTimeTargets[("CC DUTY TIME", "SH", "AH,KK")] = (0, 0, int(0.5+100*targetASAHKK))
    
    fullTimeTargets[("CC DUTY TIME", "TOT", "AH,KL")] = (0, 0, int(0.5+100*targetASAHKK))
    fullTimeTargets[("CC DUTY TIME", "TOT", "AS,KL")] = (0, 0, int(0.5+100*targetASAHKK))
    fullTimeTargets[("CC DUTY TIME", "TOT", "AH,KK")] = (0, 0, int(0.5+100*targetASAHKK))
    fullTimeTargets[("CC DUTY TIME", "TOT", "AS,KK")] = (0, 0, int(0.5+100*targetASAHKK))

    return

def customElementCCDUTYDAYS(fullTimeTargets):
    Errlog.log("In Fairness::customElementCCDUTYDAYS: calculating custom targets.")
    
    # AP, CC DUTY DAYS elements
    workrateAPKL = getTotalWorkRate("CC DUTY DAYS", "LH", "AP,KL")
    workrateAPKK = getTotalWorkRate("CC DUTY DAYS", "SH", "AP,KK")
    workAPKL = getTotalWork("CC DUTY DAYS", "LH", "AP,KL")
    workAPKK = getTotalWork("CC DUTY DAYS", "SH", "AP,KK")
    targetAPKL = 0
    targetAPKK = 0
    try:
        targetAPKL = (workAPKL+0.0)/workrateAPKL
    except:
        targetAPKL = 0
    try:
        targetAPKK = (workAPKK+0.0)/workrateAPKK
    except:
        targetAPKK = 0
    
    print "************"
    print "AP DUTY DAYS"
    print " WorkRate LH APKL: " +str(workrateAPKL/100)
    print " Work(Hours) LH APKL: " +str(workAPKL/100)
    print " WorkRate SH APKL: " +str(workrateAPKK/100)
    print " Work(Hours) SH APKK: " +str(workAPKK/100)
    print " No-share target AP,KL: " + str(targetAPKL)
    print " No-share target AP,KK: " + str(targetAPKK)
     
    FKL = 0
    if targetAPKL < targetAPKK:
        FKL = (workAPKK - workrateAPKK * targetAPKL + 0.0)/(workrateAPKK + workrateAPKL)
        targetAPKK = (workAPKK-FKL*workrateAPKL+0.0)/workrateAPKK
        print " APKL can help APKK"
        print "   rebate size = " + str(FKL)
        print "   new target APKL: " + str(targetAPKL+FKL)
        print "   new target APKK: " + str(targetAPKK)

    # We don't store total work and workrate anymore
    fullTimeTargets[("CC DUTY DAYS", "LH", "AP,KL")] = (0, 0, int(0.5+100*targetAPKL))
    fullTimeTargets[("CC DUTY DAYS", "SH", "AP,KL")] = (0, 0, int(0.5+100*FKL))
    fullTimeTargets[("CC DUTY DAYS", "SH", "AP,KK")] = (0, 0, int(0.5+100*targetAPKK))
    fullTimeTargets[("CC DUTY DAYS", "TOT", "AP,KL")] = (0, 0, int(0.5+100*targetAPKK))
    fullTimeTargets[("CC DUTY DAYS", "TOT", "AP,KK")] = (0, 0, int(0.5+100*targetAPKK))
     
    # DUTY DAYS FOR AS & AH
    # FACTOR FOR weighting work between AS & AH, changing this factor will make AS work 0.9 of AH in total.
    FACTOR_AS_AH = 1.0

    workrateASKL = getTotalWorkRate("CC DUTY DAYS", "LH", "AS,KL")
    workrateASKK = getTotalWorkRate("CC DUTY DAYS", "SH", "AS,KK")
    workrateAHKK = getTotalWorkRate("CC DUTY DAYS", "SH", "AH,KK")
    workrateAHKL = getTotalWorkRate("CC DUTY DAYS", "LH", "AH,KL")

    workAHKL = getTotalWork("CC DUTY DAYS", "LH", "AH,KL")
    workAHKK = getTotalWork("CC DUTY DAYS", "SH", "AH,KK")
    workASKL = getTotalWork("CC DUTY DAYS", "LH", "AS,KL")

    try:
        targetAHKL = (workAHKL+0.0)/workrateAHKL
    except:
        targetAHKL = 0
    try:
        targetASKL = (workASKL+0.0)/workrateASKL
    except:
        targetASKL = 0
    try:
        targetASAHKK = (workAHKK+0.0)/(workrateAHKK+FACTOR_AS_AH*workrateASKK)
    except:
        targetASAHKK = 0

    print "************"
    print "AS/AH DUTY DAYS"
    print " WorkRate ASKL: " +str(workrateASKL/100)
    print " WorkRate ASKK: " +str(workrateASKK/100)
    print " Work(Hours) ASKL: " +str(workASKL/100)
    print " WorkRate AHKL: " +str(workrateAHKL/100)
    print " Work(Hours) AHKL: " +str(workAHKL/100)
    print " WorkRate AHKK: " +str(workrateAHKK/100)
    print " Work(Hours) AHKK: " +str(workAHKK/100)
    print " No-share target AS,KL: " +str(targetASKL)
    print " No-share target AH,KL: " +str(targetAHKL)
    print " No-share target ASAH,KK: " +str(targetASAHKK)

    FAHKL = 0
    FASKL = 0
    if targetAHKL < targetASAHKK and targetASKL < targetASAHKK:
        FAHKL = (workAHKK - (targetAHKL-targetASKL)*workrateASKL-(workrateAHKK+workrateASKK)*targetAHKL)/((workrateAHKK+workrateASKK) + (workrateAHKL + workrateASKL))
        FASKL = targetAHKL+FAHKL-targetASKL
        targetASAHKK = (workAHKK - FAHKL * (workrateAHKL + workrateASKL) - (targetAHKL-targetASKL)*workrateASKL)/(workrateAHKK+workrateASKK)
        print " AHKL and ASKL can help ASAHKK"
        print "   rebate size AHKL = " + str(FAHKL) + " ASKL = " + str(FASKL)
        print "   new AHKL target: " + str(targetAHKL+FAHKL)
        print "   new ASKL target: " + str(targetASKL+FASKL)
        print "   new ASAHKK target: " + str(targetASAHKK)
    else:
        # WARNING NOT IMPLEMENTED YET
        cfhExtensions.show("Warning: \nThe fairness cases where ASKL and AHKL do not\n help ASAHKK is not yet implemented", title="WARNING!!!")

    fullTimeTargets[("CC DUTY DAYS", "LH", "AS,KL")] = (0, 0, int(0.5+100*targetASKL))
    fullTimeTargets[("CC DUTY DAYS", "SH", "AS,KL")] = (0, 0, int(0.5+100*FASKL))
    fullTimeTargets[("CC DUTY DAYS", "LH", "AH,KL")] = (0, 0, int(0.5+100*targetAHKL))
    fullTimeTargets[("CC DUTY DAYS", "SH", "AH,KL")] = (0, 0, int(0.5+100*FAHKL))
    fullTimeTargets[("CC DUTY DAYS", "SH", "AS,KK")] = (0, 0, int(0.5+100*targetASAHKK))
    fullTimeTargets[("CC DUTY DAYS", "SH", "AH,KK")] = (0, 0, int(0.5+100*targetASAHKK))
    
    fullTimeTargets[("CC DUTY DAYS", "TOT", "AH,KL")] = (0, 0, int(0.5+100*targetASAHKK))
    fullTimeTargets[("CC DUTY DAYS", "TOT", "AS,KL")] = (0, 0, int(0.5+100*targetASAHKK))
    fullTimeTargets[("CC DUTY DAYS", "TOT", "AH,KK")] = (0, 0, int(0.5+100*targetASAHKK))
    fullTimeTargets[("CC DUTY DAYS", "TOT", "AS,KK")] = (0, 0, int(0.5+100*targetASAHKK))

    return



########################################################################
# Fetch individual crew fairness targets to data base.
# Called by MenuCommandsExt in fetch_assignments
#


def get_tail(str):
    """ Return the tail of log starting from str """
    
    fn = tempfile.mktemp(".log")

    try:
        path = os.environ['LOG_FILE']
    except:
        return []
 
    os.system('tail -10000 '+path+ ' > ' + fn)
    logfile = open(fn,'r').readlines()

    last_new_start = 0
    for i in range(len(logfile)):
        if logfile[i].find(str) > -1:
            last_new_start = i  

    # Remove earlier stuff
    del logfile[:last_new_start]
    os.remove(fn)
    
    return logfile


def find_path():
    """Looks for the path for local plan and sub plan in the log file"""
    
    fetch_form = "'FORM': 'FETCH_ASSIGNMENTS'"
    
    log = get_tail(fetch_form)

    localplan = ''
    subplan = ''

    try:
        localplan = log[1].split("'")[3]
        subplan = log[2].split("'")[3]
    except:
        pass
 
    return [localplan, subplan]


def fetch_crew_fairness_targets():
    Errlog.log('In Fairness::fetch_crew_fairness_targets: fetching crew targets...')

    month, = R.eval('fairness.%deviation_time_stamp%')
    
    plans = find_path()
    if not plans[0] or not plans[1]:
        Errlog.log("In Fairness:fetch_crew_fairness_targets: Could not find plan path")
        return -1

    full_plan = os.path.join(plans[0],plans[1])
    sp_path = os.path.join("$CARMDATA/LOCAL_PLAN", full_plan)
    sp_etab_path = os.path.join(sp_path, "etable/SpLocal")

    # Load history table in DB
    tm = M.TableManager.instance()
    try:
        history_table = tm.table("crew_fairness_history")
    except M.TableNotFoundError, err:
        Errlog.log('Fairness::fetch_crew_fairness_targets: %s' % err)
        return -1
        
    # Load personal targets (without history) from subplan
    session = etab.Session()
    try:
        personal_targets = etab.load(session, os.path.join(sp_etab_path,"fairness_personal_targets_cache.etab"))
    except ValueError, err:
        Errlog.log('In Fairness::fetch_crew_fairness_targets: %s' % err)
        return -1

    # Calculate personal targets with history and store in crew_fairness_history
    for row in personal_targets:
        crewid = row.CrewId
        element = row.String1
        sub = row.String2
        is_rel_element, = R.eval('fairness.%%is_rel%%("%s", "%s")'%(element, sub))

        # DB keys cannot be null
        if not sub:
            sub = "-"

        # Fetch targets for long term fairness elements
        include_in_history, = R.eval('fairness.%%include_in_history%%("%s","%s")'%(element, sub))
        if include_in_history:
            search_criteria = "(&(crew_id=%s)(fairness_element=%s)(fairness_subelement=%s)(time_stamp<%s))" %(crewid, element, sub,  month)

            # Find latest entry before current month
            prev_date = AbsTime.AbsTime("01Jan1986 00:00")
            for entry in history_table.search(search_criteria):
                next_date = entry.time_stamp
                if next_date > prev_date:
                    prev_date = next_date
            try:
                prev_row = history_table[(crewid, element, sub, prev_date)]
                prev_dev_rel = prev_row.dev_rel
                prev_dev_int = prev_row.dev_int
                if prev_dev_rel == None:
                    prev_dev_rel = 0
                if prev_dev_int == None:
                    prev_dev_int = 0

            # If no previous entry historic deviation should be zero
            except M.EntityNotFoundError:
                prev_dev_rel = RelTime.RelTime("0:00")
                prev_dev_int = 0

            # Create new entry, or overwrite if entry already exists due to previous fetch same month
            try: 
                new_row = history_table.create((crewid, element, sub, month))
                if is_rel_element:
                    new_row.target_rel = row.RPTarget - prev_dev_rel
                else:
                    new_row.target_int = row.IPTarget - prev_dev_int
            except M.EntityError:
                old_row = history_table[(crewid, element, sub, month)]
                if is_rel_element:
                    old_row.target_rel = row.RPTarget - prev_dev_rel
                else:
                    old_row.target_int = row.IPTarget - prev_dev_int
                    
    Errlog.log('In Fairness::fetch_crew_fairness_targets: Fetch complete')
    return 0




########################################################################
# Update crew fairness history with deviation from target
#

def update_crew_fairness_history():

    Errlog.log('In Fairness::update_crew_fairness_history: updating historic values in table "crew_fairness_history"')

    month, = R.eval('fairness.%deviation_time_stamp%')
   
    bag = R.context('sp_crew').bag()

    tm = M.TableManager.instance()
    try:
        history_table = tm.table("crew_fairness_history")
    except M.TableNotFoundError, err:
        Errlog.log('In Fairness::update_crew_fairness_history: %s' % err)
        return
    
    counter = 0
    for crew_bag in bag.iterators.roster_set(where="not hidden"):
        crewid = crew_bag.crew.id()
        search_criteria = "(&(crew_id=%s)(time_stamp=%s))" %(crewid, month)
        for row in history_table.search(search_criteria):
            roster_value = crew_bag.fairness.roster_value(row.fairness_element, row.fairness_subelement)
            rel_target = row.target_rel
            if rel_target:
                row.dev_rel = RelTime.RelTime(roster_value) - rel_target
            else:
                row.dev_int = roster_value - row.target_int
        counter += 1
    Errlog.log('In Fairness::update_fairness_history: Updated historic values for %s crew' % counter)

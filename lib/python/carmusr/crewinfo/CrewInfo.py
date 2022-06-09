#
# When adding a new tab, only add the class created in CrewInfoTables to the
# tablesList function.
#

import carmusr.crewinfo.CrewInfoTables as CrewInfoTables
import carmusr.crewinfo.crew_profile as crew_profile
import utils.time_util as time_util

import AbsTime
from RelTime import RelTime
import modelserver as M
from tm import TM
import time

from utils.performance import log
import utils.wave
utils.wave.register()

if not utils.wave.STANDALONE:
    import carmstd.cfhExtensions as cfhExtensions
    import Cui
    import carmusr.HelperFunctions as HF
    import MenuState

global tables
global formInfo
global crewId
crewId = None

# The functions below should not need to be changed when a new tab is added to
# the Crew Info

def getCrewId():
    return Cui.CuiCrcEvalString(Cui.gpc_info,
                               Cui.CuiWhichArea,
                               "object",
                               "crr_crew_id")


def getNewCrew(plan, empNo):
    import time
    global tables
    global formInfo
    global cxt

    cxt.errorInfo.clear()
    
    if utils.wave.STANDALONE:
        TM.refresh()
    
    crewId = None
    nowTime = utils.wave.get_now_utc(True)
    rows = []
    ldap = '(|(crew.id=%s)(extperkey=%s))' % (empNo, empNo)
    for row in TM.crew_employment.search(ldap):
        try:
            if row.validfrom <= nowTime and row.validto >= nowTime:
                crewId = row.crew.id
                break
            else:
                rows.append(row)  
        except:
            pass
    else:
        if rows:
            rows.sort(cmp = lambda x,y: cmp(x.validto, y.validto))
            crewId = rows[-1].crew.id

    if crewId is None:
        message = ("Crew '%s' not found."
                   "Please enter a valid employment number and press enter."
                  ) % empNo
    else:
        cxt.refresh(nowTime, crewId)
        message = cxt.errorInfo.errorMessage() + " "
    cxt.formInfo.setStatusMessage(message, (message.strip() != ""))
    

def checkForChanges(plan, is_save_check=None):
    global tables
    global formInfo
    global checked_modified_tables
    checked_modified_tables = []
    formInfo.setUnsaved(False)   
    for tname, table in tables.items():
        if table.checkForChanges():
            formInfo.setUnsaved(True)
            if is_save_check:          
                checked_modified_tables.append(table)
            else:
                break


def saveChanges(plan):
    global cxt
    global checked_modified_tables
 
    try:
        modified_tables = checked_modified_tables[:]
        del checked_modified_tables
    except:
        raise Exception("Programming error: "
                        + "checkForChanges must be called before saveChanges")

    log("CrewInfo ---------- SUBMIT CREW %s" % cxt.crewId)
    
    saved_tables = []
    error_tables = []
    
    empTable = cxt.tables.CrewEmployment
    contTable = cxt.tables.CrewContract
    checkMismatch = False
    for table in modified_tables:
        if table.TM_NAME == "crew_employment":
            empTable = table
            checkMismatch = True
        if  table.TM_NAME == "crew_contract":
            contTable = table
            checkMismatch = True
    if checkMismatch:
        mismatchErr = validateMismatch(empTable, contTable)   
        if mismatchErr.strip():
            error_tables.append((contTable, mismatchErr))
            
    if not error_tables:
        for table in modified_tables:
            try:
                err = table.save()
            except CrewInfoTables.ValidationException, ex:
                err = str(ex)
            if err.strip():
                error_tables.append((table, err))
            else:
                table.refresh(cxt.nowTime, cxt.crewId)
                table.cxt = cxt
                table.formInfoTable = cxt.formInfo.getTable()
                table.afterAllTablesLoaded()
                saved_tables.append(table)
            
    if error_tables:
        msg = "%s. " % error_tables[0][1].lstrip().rstrip('. ')
        if saved_tables:
            tlist = ",".join([te[0].getDisplayName() for te in error_tables])
            msg += "Changes in %s were not applied." % tlist
        else:
            msg += "No changes were applied."
        cxt.formInfo.setStatusMessage(msg, isErrorMessage=True,
                                      errorTable=error_tables[0][0].getTabName())
    else:
        msg = "Changes successfully applied."
        cxt.formInfo.setStatusMessage(msg)

    log("CrewInfo ---------- %s" % msg)
    
    if saved_tables:
        if utils.wave.STANDALONE:
            TM.save()
        else:
            for table in saved_tables:
                for tname in table.getSourceName():
                    Cui.CuiReloadTable(tname)
            HF.redrawAllAreas(Cui.CrewMode)

    cxt.tables.CrewSummary.refresh(cxt.nowTime, cxt.crewId)
    cxt.tables.CrewProfile.refresh(cxt.nowTime, cxt.crewId)

def createNewRow(plan, table):
    global tables
    global formInfo
    time = formInfo.getTime()
    for t in tables:
        if t == table:
            tables[t].createRow(time)
            break

def resetStatusMsg(plan):
    global formInfo
    formInfo.setStatusMessage(" ", False)

def initiateTables(plan, tmpTablesPrefix="tmp_cbi_", tablesToLoad="ALL", 
                   crewIdNonGlobal=None):
    global tables
    global crewId
    global formInfo
    global cxt

    # Set the menu state OpenWaveForms to hide Undo buttons in Studio
    # on opening wave forms (Crew Info, Crew Accounts, Crew Training,
    # Crew Block Hours). SASCMS-4562
    if not utils.wave.STANDALONE:
        MenuState.setMenuState('OpenWaveForms', 1, forceMenuUpdate = True)
    
    # We can be used by functions outside of crew info. In that case we are
    # called with crewid as parameter
    if crewIdNonGlobal:
        crewId = crewIdNonGlobal

    # tmpTablesPrefix should be used so that every application can have its own set of temp tables.
    # tmp_cbi_ is the default, and should be used for the Crew Info-application.
    # tablesToLoad is a tuple with strings with the names of the tables to load, as they appear in
    # the database.
    
    cxt = CrewInfoTables.CrewInfoContext.create(
        utils.wave.get_now_utc(True), crewId, tmpTablesPrefix)
    formInfo = cxt.formInfo
    tables = cxt.tables.asDict()
    
    if utils.wave.STANDALONE:
        sources = []
        for table in tables.itervalues():
            sources.extend(table.getSourceName())
        TM(*sources)
        TM(['crew_rank_set'])
        TM.newState()
    
    message = cxt.errorInfo.errorMessage() + " "
    cxt.formInfo.setStatusMessage(message,(message != " "))
    

def startCrewInfoForm():
    import StartTableEditor
    global crewId
    crewId = getCrewId()
    
    formName = "crew_info.xml"
    fullFormPath = '$CARMUSR/data/form/'+formName
    
    if not utils.wave.STANDALONE and \
        str(StartTableEditor.getFormState(fullFormPath)).lower() not in ('none', 'error'):
        try:
            cfhExtensions.show("Crew Info Form is open,\nplease reuse already open form!")
        except Exception, err:
            Errlog.log("CrewInfo.py:: %s"%err)
        return
        
    StartTableEditor.StartTableEditor(
        ['-f', fullFormPath , '-P','system.forms.debug=false'], "Crew Info")
    

def showDetails(plan, table, selection):
    return tables[table].showDetails(selection)

def validateMismatch(empTable, contTable):
    empIntervalSet = time_util.IntervalSet()
    contIntervalSet = time_util.IntervalSet()
    contRetIntervalSet = time_util.IntervalSet()

    for row in empTable:
        interval = time_util.TimeInterval(row.validfrom, row.validto + RelTime(24,0))
        empIntervalSet.add(interval)

        
    for row in contTable:
        if row.contract.contract.grouptype == "R":
            interval = time_util.TimeInterval(row.validfrom, row.validto + RelTime(24,0))
            contRetIntervalSet.add(interval)
        else:
            interval = time_util.TimeInterval(row.validfrom, row.validto + RelTime(24,0))
            contIntervalSet.add(interval)
    
    #Interval where active contracts and employment do not overlap
    intervalSetDiff = contIntervalSet ^ empIntervalSet
    #Interval where diff is not covered by retirement contract. Retirement contract do not need an employment.
    intervalSetDiffRet = intervalSetDiff - contRetIntervalSet
    try:
        diff = intervalSetDiffRet.pop()
        return "Crew has active contract but no employment, or employment without contract, %s - %s" % (diff[0], diff[1])
    except KeyError:
        return ""

def refreshProfile(plan):
    # The standalone version on first start does not
    # have a crewId hence we do not refresh.
    if cxt.crewId is None:
        return
    cxt.tables.CrewProfile.refresh(cxt.nowTime, cxt.crewId)
    
# Register service functions which shall be accessed from the xml window
from utils.wave import LocalService, ModelChangeService, unicode_args_to_latin1 as u2l
class cbi_get_new_crew(LocalService):         func = u2l(getNewCrew)
class cbi_save_changes(ModelChangeService):   func = saveChanges
class cbi_check_for_changes(LocalService):    func = checkForChanges
class cbi_create_new_row(LocalService):       func = createNewRow
class cbi_initiate_tables(LocalService):      func = initiateTables
class cbi_reset_status_message(LocalService): func = resetStatusMsg
class cbi_show_details(LocalService):         func = u2l(showDetails)
class cbi_refresh_profile(LocalService):      func = refreshProfile
utils.wave.register()

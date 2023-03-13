#

#
"""
View Leave Accounts Form
"""

from AbsTime import AbsTime
from RelTime import RelTime
import carmusr.AccountHandler as AccountHandler
import carmstd.cfhExtensions as cfhExtensions

from tm import TempTable
from tm import TM
import StartTableEditor
from modelserver import EntityNotFoundError
from modelserver import EntityError
from modelserver import DateColumn
from modelserver import StringColumn
from modelserver import RefColumn
from modelserver import BoolColumn
from modelserver import IntColumn
from modelserver import UUIDColumn
from modelserver import TimeColumn

import Cui
import carmensystems.services.dispatcher as CSD
import carmensystems.rave.api as R
import time
import os
import sys
from utils.dave import EC
import utils.wave
import utils.PerformanceMonitor as pm
from carmusr.application import isDayOfOps

import MenuState

from salary.reasoncodes import REASONCODES 
# Accounts
F0 = 'F0'
F0_BUFFER = 'F0_BUFFER'
F3 = 'F3'
F31 = 'F31'
F32 = 'F32'
F33 = 'F33'
F35 = 'F35'
F36 = 'F36'
F37 = 'F37'
F38 = 'F38'
F3S = 'F3S'
F7 = 'F7'
F7S = 'F7S'
PR = 'PR'
# Added FS as part of SASBids5 project
FS = 'FS'
F89 = 'F89'
F9 = 'F9'
F15 = 'F15'
F16 = 'F16'
VA1 = 'VA1'
VA = 'VA'
VA_SAVED1 = 'VA_SAVED1'
VA_SAVED2 = 'VA_SAVED2'
VA_SAVED3 = 'VA_SAVED3'
VA_SAVED4 = 'VA_SAVED4'
VA_SAVED5 = 'VA_SAVED5'

BOUGHT = 'BOUGHT'
BOUGHT_COMP = 'BOUGHT_COMP'
BOUGHT_COMP_F3S = 'BOUGHT_COMP_F3S'
BOUGHT_8 = 'BOUGHT_8'
BOUGHT_F3 = 'BOUGHT_F3'
BOUGHT_F3_2 = 'BOUGHT_F3_2'
BOUGHT_BL = 'BOUGHT_BL'
BOUGHT_FORCED = 'BOUGHT_FORCED'
SOLD = 'SOLD'
BOUGHT_PR='BOUGHT_PR'

# Actions
IN_ADMIN   = REASONCODES["IN_ADMIN"]  #'IN Administrative'
IN_CORR    = REASONCODES["IN_CORR"]   #'IN Correction'
IN_FLY_VAF = REASONCODES["IN_FLY_VAF"] #'IN Flying on VA/F day'
IN_IRR     = REASONCODES["IN_IRR"]     #'IN Irregularity'
IN_MEET    = REASONCODES["IN_MEET"]    #'IN Meeting'
IN_OT      = REASONCODES["IN_OT"]      #'IN Overtime'
IN_CONV    = REASONCODES["IN_CONV"]    #'IN Conversion'
IN_MISC    = REASONCODES["IN_MISC"]    #'IN Miscellaneous'
IN_MAN     = REASONCODES["IN_MAN"]     #'IN Manual'
OUT_CORR   = REASONCODES["OUT_CORR"]   #'OUT Correction'
PAY        = REASONCODES["PAY"]        #'OUT Payment'
PAY_CORR   = REASONCODES["PAY_CORR"]   #'IN Payment Correction'
SAVED      = REASONCODES["OUT_SAVED"]      #'OUT Saved'
UNSAVED    = REASONCODES["OUT_UNSAVED"]    #'OUT Unsaved'



MOVE_PAIR={SAVED:REASONCODES["IN_SAVED"],
           UNSAVED:REASONCODES["IN_UNSAVED"]}


IN_ACTIONS = [IN_ADMIN, IN_CORR, IN_FLY_VAF, IN_IRR, IN_MEET, IN_OT, IN_CONV,
              IN_MISC, IN_MAN, PAY_CORR]
OUT_ACTIONS = [OUT_CORR, PAY]

ACTION = {}
# Compensation days accounts
COMPDAY_ACTIONS = [IN_ADMIN, IN_CORR, IN_FLY_VAF, IN_IRR, IN_MEET, IN_OT,
                   IN_CONV, IN_MISC, OUT_CORR, PAY, PAY_CORR]

COMPDAY_ACTIONS_NO_PAY = [IN_ADMIN, IN_CORR, IN_FLY_VAF, IN_IRR, IN_MEET, IN_OT,
                   IN_CONV, IN_MISC, OUT_CORR]
                   
#ACTION[F0] = COMPDAY_ACTIONS + [REASONCODES['OUT_CONV']]
ACTION[F0] = COMPDAY_ACTIONS_NO_PAY + [REASONCODES['OUT_CONV']]
ACTION[F0_BUFFER] = COMPDAY_ACTIONS + [REASONCODES['OUT_CONV']]
ACTION[F3]  = COMPDAY_ACTIONS
#ACTION[F31]  = COMPDAY_ACTIONS
ACTION[F31] = COMPDAY_ACTIONS_NO_PAY
ACTION[F32] = COMPDAY_ACTIONS = [IN_ADMIN, IN_CORR, IN_FLY_VAF, IN_IRR, IN_MEET, IN_OT,
                   IN_CONV, IN_MISC, OUT_CORR]
ACTION[F33] = COMPDAY_ACTIONS
ACTION[F35] = COMPDAY_ACTIONS
ACTION[F36] = COMPDAY_ACTIONS
ACTION[F3S] = COMPDAY_ACTIONS
ACTION[F7S] = COMPDAY_ACTIONS
ACTION[F89] = COMPDAY_ACTIONS
ACTION[F9]  = COMPDAY_ACTIONS
ACTION[F15] = COMPDAY_ACTIONS
ACTION[F16] = COMPDAY_ACTIONS
# Vacation accounts
ACTION[VA1] = [IN_CORR, OUT_CORR]
ACTION[FS]  = [IN_MAN, OUT_CORR]
#ACTION[VA]  = [IN_MAN, IN_CORR, OUT_CORR, PAY, PAY_CORR, SAVED]
ACTION[VA]  = [IN_MAN, IN_CORR, OUT_CORR, SAVED]
ACTION[F7]  = [IN_MAN, IN_CORR, OUT_CORR, PAY, PAY_CORR]
ACTION[F37] = [IN_CORR, OUT_CORR]
ACTION[F38] = [IN_MAN, IN_CORR, OUT_CORR]

ACTION[VA_SAVED1] = [IN_CORR, OUT_CORR, UNSAVED]
ACTION[VA_SAVED2] = [IN_CORR, OUT_CORR, UNSAVED]
ACTION[VA_SAVED3] = [IN_CORR, OUT_CORR, UNSAVED]
ACTION[VA_SAVED4] = [IN_CORR, OUT_CORR, UNSAVED]
ACTION[VA_SAVED5] = [IN_CORR, OUT_CORR, UNSAVED]
ACTION[VA1] = [IN_CORR, OUT_CORR]

# Bought / Sold
#ACTION[BOUGHT] = [IN_CORR, OUT_CORR]
ACTION[BOUGHT] = []
ACTION[BOUGHT_COMP] = [IN_CORR, OUT_CORR]
#ACTION[BOUGHT_8] = [IN_CORR, OUT_CORR]
ACTION[BOUGHT_8] = []
#ACTION[BOUGHT_BL] = [IN_CORR, OUT_CORR]
ACTION[BOUGHT_BL] = []
ACTION[BOUGHT_COMP_F3S] = [IN_CORR, OUT_CORR]
ACTION[BOUGHT_F3] = [IN_CORR, OUT_CORR]
ACTION[BOUGHT_F3_2] = [IN_CORR, OUT_CORR]
#ACTION[BOUGHT_FORCED] = [IN_CORR, OUT_CORR]
ACTION[BOUGHT_FORCED] = []
#ACTION[SOLD] = [IN_CORR, OUT_CORR]
ACTION[SOLD] = []
ACTION[PR] = [IN_CORR, OUT_CORR]

"""
Temporary class that holds crew information.
"""
class CrewInfoTable(TempTable):
    _name = 'tmp_account_crew_info'
    _keys = [StringColumn('id', 'Id')]
    _cols = [StringColumn('emp_no', 'Employee Number'),
             StringColumn('last_name', 'Last Name'),
             StringColumn('first_name', 'First Name'),
             StringColumn('rank'),
             StringColumn('main_cat'),
             StringColumn('homebase'),
             StringColumn('message')]
    
    def __init__(self, crewId):
        TempTable.__init__(self)
        for row in self:
            row.remove()
        row = self.create((str(crewId),))
        setCrewInScriptBuffer(crewId)
        rosters, = R.eval('default_context', R.foreach(
            R.iter('iterators.roster_set',
                   where='crew.%%id%% = "%s"' % crewId),
            'crew.%employee_number%',
            'crew.%surname%',
            'crew.%firstname%',
            'crew.%rank%',
            'crew.%main_func%',
            'crew.%homebase%'))

        for (ix, empNo, lastName, firstName, rank, mainCat,
             homebase) in rosters:
            row.emp_no = empNo
            row.last_name = lastName
            row.first_name = firstName
            row.rank = rank
            row.main_cat = mainCat
            row.homebase = homebase
            row.message = ''


class IdClass(object):
    
    def __init__(self, id=None):
        self._id = id
    def getCrewId(self):
        return self._id
    
    def setCrewId(self, empno):
        id = None
        empno = empno.encode("latin-1")
        utils.wave.refresh_wave_values()
        nowTime = utils.wave.get_now_utc(True)

        rows = []
        ldap = '(|(crew.id=%s)(extperkey=%s))' % (empno, empno)
        for crew in TM.crew_employment.search(ldap):
            try:
                if crew.validfrom <= nowTime and crew.validto >= nowTime:
                    id = crew.crew.id
                    break
                else:
                    rows.append(crew)  
            except:
                pass
        else:
            if rows:
                rows.sort(cmp = lambda x,y: cmp(x.validto, y.validto))
                id = rows[-1].crew.id

        if id is None:
            message = ("Crew '%s' not found."
                       "Please enter a valid employment number."
                        ) % empno
            for row in TM.tmp_account_crew_info:
                row.message = message
                break
            raise CrewNotFoundException()
        else:
            self._id = id
       
class CrewNotFoundException(Exception):
    pass

"""
Temporary class for date selection.
"""
class DateTable(TempTable):
    _name = 'tmp_account_date'
    _keys = [StringColumn('id', 'Id')]
    _cols = [DateColumn('date', 'Date')]

    def __init__(self, id):
        TempTable.__init__(self)
        for row in self:
            row.remove()
        try:
            self._row = self.create((id,))
        except EntityError:
            self._row = self[(id,)]
        self.refresh()
            
    def refresh(self):
        self._row.date = utils.wave.get_now_date_utc(refresh=True)

"""
Temporary class for actions on accounts.
"""
class ActionTable(TempTable):
    _name = 'tmp_account_action'
    _keys = [StringColumn('id', 'Id'),
             StringColumn('action', 'Account Action')]
    _cols = [StringColumn('si', 'SI')]

    def __init__(self, id, account=None):
        TempTable.__init__(self)
        for row in self:
            row.remove()
        if account is not None and ACTION.has_key(account): 
            for action in ACTION[account]:
                row = self.create((id, action))

"""
Temporary class for leave account entries.
"""
class AccountEntryTable(TempTable):
    _name = 'tmp_account_entry'
    _keys = [IntColumn('index', 'Index'),
             RefColumn('crew', 'crew', 'Crew')]
    _cols = [DateColumn('date', 'Date'),
             RefColumn('account', 'account_set', 'Account'),
             StringColumn('reason', 'Reason'),
             StringColumn('amount', 'Amount'),
             StringColumn('balance', 'Balance'),
             StringColumn('si', 'SI'),
             StringColumn('comment', 'Comment'),
             StringColumn('source', 'Source'),
             StringColumn('published', 'Published'),
             StringColumn('sortkey', 'Sorted by tim, entrytime and index'),
             ]

    def __init__(self, crewId):
        TempTable.__init__(self)
        for row in self:
            row.remove()

class WarningTable(TempTable):
    _name = 'tmp_account_warning'
    _keys = [StringColumn('id', 'Id')]
    _cols = [DateColumn('date', 'Date'),
             StringColumn('account', 'Account'),
             StringColumn('amount', 'Amount'),
             StringColumn('balance', 'Balance'),
             StringColumn('si', 'SI'),
             StringColumn('warn_text', 'Warning Text'),
             StringColumn('warn_type', 'Warning'),
             DateColumn('warn_date', 'Warning Date'),
             StringColumn('user_role','User Role')]
    def __init__(self, id):
        TempTable.__init__(self)
        for row in self:
            row.remove()


"""
Exception class used when an undefined action is used for account updates.
"""
class UndefinedActionException(Exception):
    def __init__(self, *args):
        Exception.__init__(self, *args)
        self.wrapped_exc = sys.exc_info()

def setCrewInScriptBuffer(crewId):
    """
    Moves specified crew to script buffer.
    """
    Cui.CuiDisplayGivenObjects(
        Cui.gpc_info, Cui.CuiScriptBuffer, Cui.CrewMode, Cui.CrewMode,
        [str(crewId)], 0)
    Cui.CuiCrgSetDefaultContext(
        Cui.gpc_info, Cui.CuiScriptBuffer, 'WINDOW')

    return

def updateAccount(crewId, account, action, reason, date, amount, comment):
    """
    Updates account with specified parameters.
    """
    entry = TM.account_entry.create((TM.createUUID(),))
    entry.crew = TM.crew[(crewId,)]
    entry.tim = date
    entry.account = TM.account_set[(account,)]
    entry.source = action
    entry.reasoncode = reason
    entry.amount = amount
    entry.man = True
    entry.si = comment or ""
    entry.published = True
    entry.rate = amount>0 and 100 or -100
    entry.entrytime = utils.wave.get_now_utc(refresh=True)
    entry.username = R.eval('user')[0]
    return entry


    
def checkAction(*args):
    """
    Checks if balance might become negative on account for a transaction.
    """
    global isDayOfOps
    global idObj
    crewId = idObj.getCrewId()
    account = args[2]
    action = args[3]
    date = AbsTime(args[4])
    amount = float(args[5])

    WarningTable(crewId)

    # Find account entries

    # Get baseline data, if no baseline, date is 1Jan1901
    baseline_data = AccountHandler.getBaseLineData(crewId,account)
    baseline_date = AbsTime('1Jan1901')
    balance = 0.0
    for baseline in baseline_data:
        if baseline_data[baseline]['TIM'] >= baseline_date and baseline != 'DAILY':
            baseline_date = baseline_data[baseline]['TIM']
            balance = float(baseline_data[baseline]['VAL'])/100.0
  
    accountEntries = [_ for _ in TM.tmp_account_entry if \
                      _.crew.id == crewId and \
                      _.account.id == account and \
                      _.date >= baseline_date and \
                      _.date <= date and \
                      bool(_.amount) ]

    # Sort entries so that balance is calculated in order
    accountEntries.sort(key=lambda e: e.sortkey)
    if action in OUT_ACTIONS or action == SAVED or action == UNSAVED:
        amount = -amount

    amountAdded = False
    if len(accountEntries) > 0:
        for entry in accountEntries:
            if not amountAdded and date < entry.date:
                balance += float(amount)
                amountAdded = True
            if amountAdded and balance < 0:
                break
            entryAmount = float(entry.amount)
            balance += entryAmount

    if not amountAdded:
        balance += amount
    warning = None

    # SOLD account will give a warning if balance is positive, other accounts
    # will give warning if the balance is negative. (WP NonCore-FAT 465)
    account_warning = balance > 0 if account in ['SOLD'] else balance < 0

    if date < baseline_date or account_warning:
        warning = TM.tmp_account_warning.create((crewId,))
        warning.date = date
        warning.account = account
        warning.amount = '%.2f' % amount
        warning.balance = '%.2f' % balance
        warning.user_role = os.environ.get('CARMROLE',"").lower()

        if date < baseline_date: # Baseline warning before balance!
            if isDayOfOps:
                    warning.warn_type = "baseline_dayofop"
                    warning.warn_date = baseline_date
                    warning.warn_text = """Transaction is made before baseline date. Change 
to ordinary studio to make this change, reaccumulate 
data to make the change visible."""
            else:
                    warning.warn_type = "baseline_studio"
                    warning.warn_date = baseline_date
                    warning.warn_text = """Transaction is made before baseline date. You need 
to accumulate data to make this change visible in 
studio."""
        else:
            warning.warn_type = "balance"
            warning.warn_text = "Transaction will cause %s balance on account." % (
                    ('negative', 'positive')[account in ['SOLD']],)


def addTransaction(*args):
    """
    Creates a new transaction and updates accounts.
    """
    global idObj
    # Get parameters
    crewId = idObj.getCrewId()
    account = args[2]
    reason = action = args[3]
    date = AbsTime(args[4])
    amount = int(round(float(args[5]) * 100, 0))
    comment = args[6]

    # Perform transaction according to action
    # Positive account update
    if action in IN_ACTIONS:
        updateAccount(crewId, account, action, reason, date, amount, comment)
    # Negative account update
    elif action in OUT_ACTIONS:
        updateAccount(crewId, account, action, reason, date, -amount, comment)
    # "Move" between accounts
    elif action == SAVED or action == UNSAVED:
        entryFrom=entryTo=None
        try:
            entryFrom=updateAccount(crewId, account, action, reason, date, -amount, comment)
            #Get reason for matching transaction
            reason = MOVE_PAIR[action]
            if action == SAVED:
                toAccount = VA_SAVED1
            else:
                toAccount = VA
            entryTo=updateAccount(crewId, toAccount, action, reason, date, amount, comment)
        # One entry could not be created, remove matching
        except EntityNotFoundError, err:
            if entryFrom is not None:
                entryFrom.remove()
            if entryTo is not None:
                entryTo.remove()
            raise err
    else:
        raise UndefinedActionException(action)
    # Reload account table for rave
    Cui.CuiReloadTable('account_entry',1)
    return

def get_account_entry_string(crew, account):

    uuid_set = []
    for row in crew.referers('account_entry','crew'):
        if row.account.id.upper() == account.upper():
            uuid_set.append(str(row.id))
    uuid_set.sort()
    
    return ';'.join(uuid_set)

def updateCrew(*args):
    global idObj
    try:
        idObj.setCrewId(args[1])
    except CrewNotFoundException:
        #If crew not found, return
        return

    CrewInfoTable(idObj.getCrewId())
    WarningTable(idObj.getCrewId())

    updateForm(*args)

EC_INST = None
    
def updateForm(*args):
    
    global idObj    
    """
    Updates form data tables.
    """
    
    # Set the menu state OpenWaveForms to hide Undo buttons in Studio
    # on opening wave forms (Crew Info, Crew Accounts, Crew Training,
    # Crew Block Hours). SASCMS-4562
    if not utils.wave.STANDALONE:
        MenuState.setMenuState('OpenWaveForms', 1, forceMenuUpdate = True)    

    # Get parameters
    crewId = idObj.getCrewId()
    account = args[2]
    action = args[3]
    if action == 'NULL':
        action = None

    try:
        crew = TM.crew[(crewId,)]
    except EntityError:
        raise Exception('Could not find crew %s in crew table'%crewId)

    pm.time_reset('Updating account view for crew %s and account %s'%(crewId, account))
    
    DateTable(crewId)

    # Update selected account
    # Get state before 
    pre_string = get_account_entry_string(crew, account)
    setCrewInScriptBuffer(crewId)
    
    # This is the new faster bulk-function
    AccountHandler.updateAccountsForCrewInWindow([crewId],
                                                 [account],
                                                 Cui.CuiScriptBuffer)
    # Get state after
    post_string = get_account_entry_string(crew, account)
    # Tell user if we updated info in the background
    for row in TM.tmp_account_crew_info:
        row.message = ['',
                       'Crew account info updated by form'][pre_string != post_string]
        break
        
    # Update actions for view
    ActionTable(crewId, account)

    # Find account entries
    AccountEntryTable(crewId)
    TM.tmp_account_entry.removeAll()
    index = 0
    # Get baseline data, if no baseline, TIM in None
    pm.time_tic("Account setup")
    baseline_data = AccountHandler.getBaseLineData(crewId,account)

    for baseline in baseline_data:
        if baseline_data[baseline]['TIM'] is not None:
            _create_baseline_entry(crew,                                       
                                   baseline,
                                   baseline_data,
                                   account)

    pm.time_tic("Get baseline")
    
    model_collection = set()
    for model_row in crew.referers('account_entry','crew'):
        if model_row.account.id == account:
            model_collection.add(model_row.id)
            _create_tmp_entry(crew, model_row, source='model')
    
    pm.time_tic("Collect account entry info from model")
    # Get period to use ec account entiries outside
    if baseline_data:
        ec_start = max([baseline_data[baseline]['TIM'] for baseline in baseline_data])
    else:
        ec_start = AbsTime('31Dec2099')
    # loaded end
    ec_end,= R.eval('default_context','fundamental.%plan_end%')

    global EC_INST
    if EC_INST == None:
        EC_INST = EC(TM.getConnStr(), TM.getSchemaStr())
    try:
        for entry in EC_INST.account_entry.search("(crew='%s')"%crewId):
            if entry.account == account and \
               (entry.tim < ec_start or \
                entry.tim >= ec_end) and \
                entry.id not in model_collection:
                _create_tmp_entry(crew, entry)
    finally:
        pass
            
    pm.time_tic("Collect account entry info from database") 
    # Update balances
    tmp_entries = [_ for _ in TM.tmp_account_entry]
    tmp_entries.sort(key=lambda e: e.sortkey)
    current_balance = 0
    for tmp_entry in tmp_entries:
        if tmp_entry.balance is None:
            current_balance += float(tmp_entry.amount)
            tmp_entry.balance = '%.2f'%current_balance
        else:
            current_balance = float(tmp_entry.balance)
    pm.time_tic("Update balances")  
    pm.time_log()
    return 0

def _create_baseline_entry(crew, name, baseline_data, account):
    index = max([_.index for _ in TM.tmp_account_entry] or [0]) + 1
    tmpEntry = TM.tmp_account_entry.create((index, crew))
    tmpEntry.date = baseline_data[name]['TIM']
    tmpEntry.account = TM.account_set[(account,)]
    tmpEntry.amount = ""
    tmpEntry.reason = "BASELINE %s"%name
    tmpEntry.balance = '%.2f' % (float(baseline_data[name]['VAL'])/100.0)
    tmpEntry.comment = "ACCOUNT BASELINE"
    tmpEntry.si = "Created %s"%baseline_data[name]['LASTRUN']
    tmpEntry.source = 'baseline'
    tmpEntry.published = 'Y'
    tmpEntry.sortkey = "%s+%s+%08d" % (tmpEntry.date.yyyymmdd(),
            '01Jan1986 00:00', tmpEntry.index)
    return tmpEntry

def _create_tmp_entry(crew, entry, source='database'):
    index = max([_.index for _ in TM.tmp_account_entry] or [0])+1
    amount = float(entry.amount) / 100
    # Only count account_entry
    tmpEntry = TM.tmp_account_entry.create((index, crew))
    tmpEntry.date = entry.tim
    # Entry can be either EC-object or TM-object
    if type(entry.account) == type("string"):
        tmpEntry.account = TM.account_set[(entry.account,)]
    else:
        tmpEntry.account = entry.account

    tmpEntry.reason = entry.reasoncode
    tmpEntry.amount = '%.2f' % amount
 #   tmpEntry.balance = '%.2f' % balance

    tmpEntry.published = ['N','Y'][bool(entry.published)]
    
    # The comment(entry.si) goes to tmp.comment, the timestamp is in si
    comment = (entry.si, '')[entry.si is None]
    # make a comment on high rate vacation for SKN crew
    if entry.source and \
           ('VAD' in entry.source or \
            'VAH' in entry.source or \
            'VA1D' in entry.source or \
            'VA1H' in entry.source):
        if comment not in (None,'',' '):
            comment += ' / ' # Add separator
        comment += entry.source

    tmpEntry.comment = comment
    tmpEntry.si = '%s %s' % (  (entry.username,'')[entry.username is None],
                               entry.entrytime)
    tmpEntry.source = source

    try:
        sort_et = entry.entrytime.yyyymmdd()
    except:
        sort_et = '19860101 00:00'

    tmpEntry.sortkey = "%s+%s+%08d" % (tmpEntry.date.yyyymmdd(), sort_et, tmpEntry.index)
    return tmpEntry

def start():
    """
    Starts the leave account view.
    """
    global idObj
    # Get crew id
    crewId = Cui.CuiCrcEvalString(
        Cui.gpc_info, Cui.CuiWhichArea, 'object', 'crew.%id%')
    idObj = IdClass(crewId)

    # Starts the leave account form.
    form_name = '$CARMUSR/data/form/leave_accounts.xml'
    state = StartTableEditor.getFormState(form_name)
    if state not in (None,'error'):
        cfhExtensions.show("Crew leave account form already opened.")
    else:
        # Init tables
        utils.wave.init_wave_values()
        ActionTable(crewId)
        DateTable(crewId)
        AccountEntryTable(crewId)
        CrewInfoTable(crewId)
        WarningTable(crewId)
    
        # Register functions
        from utils.wave import unicode_args_to_latin1 as u2l
        cmt = "carmensystems.mirador.tablemanager.account_%s"
        CSD.registerService(u2l(addTransaction), cmt % "add_transaction")
        CSD.registerService(u2l(updateForm),     cmt % "update_view")
        CSD.registerService(u2l(checkAction),    cmt % "check_action")
        CSD.registerService(u2l(updateCrew),     cmt % "update_crew")
    
        # Get crew information
        setCrewInScriptBuffer(crewId)
    
        # Start the form
        StartTableEditor.StartTableEditor(['-f', form_name])
    return

#####################################################

#
# AccountHandler contains functions for storing and
# maintaining the account_entry table. This table is
# automatically updated in the plan interval for a
# changed crew at save. It can also be updated at
# will if another process or form (e.g. the AccountView)
# wants to show the most valid information from the
# roster
#
# Contains:
#      A function for updating the balance for a
#      single crew and single account
#
#
# David Lennartsson, Jeppesen 2007-02-28
#

import Cui
import AbsTime
import RelTime
import Errlog
import utils.Names as Names
import carmensystems.rave.api as R
import time
import carmusr.HelperFunctions as HF
import application
from salary.reasoncodes import REASONCODES




### This functionality only works while on DB-plans
try:
    from tm import TM
    from utils.dave import EC
    from modelserver import EntityError
    from modelserver import EntityNotFoundError
    import utils.selctx
except:
    # This handles when the script is called when product=cas and
    # modelserver isn't available
    pass
try:
    BOUGHT_ACCOUNT_NAME = R.eval('default_context', "bought_days.%account_name%")[0].upper()
    BOUGHT_ACCOUNT_NAMES = [el.upper() for el in R.eval(
        'default_context',
        "bought_days.%account_name%",
        "bought_days.%bl_account_name%",
        "bought_days.%comp_account_name%",
        "bought_days.%bought8_account_name%",
        "bought_days.%bought_f3s_account_name%",
        "bought_days.%bought_f3_account_name%",
        "bought_days.%bought_f3_2_account_name%",
        "bought_days.%co_on_f_account_name%",
        "bought_days.%bought_sby_account_name%",
        "bought_days.%bought_prod_account_name%",
        "bought_days.%bought_duty_account_name%",
        "bought_days.%bought_pr_account_name%",
    )]
except:
    # Best guesses
    BOUGHT_ACCOUNT_NAME = 'BOUGHT'
    BOUGHT_ACCOUNT_NAMES = ['BOUGHT','BOUGHT_SBY','BOUGHT_PROD','BOUGHT_DUTY','BOUGHT_BL', 'BOUGHT_COMP', 'BOUGHT_8', 'BOUGHT_COMP_F3S', 'BOUGHT_F3', 'BOUGHT_F3_2', 'BOUGHT_FORCED', 'BOUGHT_PR']


##################################################################
# Function for updating the publication status for transactions
# for crew in window
#
def setPublished(ival_start = None, ival_end = None, currentArea = Cui.CuiArea0):
    """
    This command reruns the update for all crew in window 0 and then
    publishes all unpublished activities.
    """
    # Check if in database plan
    try:
        TM(["account_set", "account_entry"])
    except:
        Errlog.set_user_message("Only available in database plans")
        return
    
    # get list of crew id for all crew in window 0
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, currentArea, "window")
    crewList, = R.eval("default_context", R.foreach('iterators.roster_set', 'crew.%id%'))
    # Remove the stupid tuple
    crewList = [str(crew) for _, crew in crewList]

    # Update all the accounts
    # Should only the publication period be updated
    updateChangedCrew(crewList)

    # Set context on crew, eval the stuff we want
    Cui.CuiSetSelectionObject(Cui.gpc_info, currentArea, Cui.CrewMode, crewList[0])
    # Shouldn't the period be the publication period?
    if not ival_start:
        ival_start = Cui.CuiCrcEval(Cui.gpc_info, currentArea, "object", "fundamental.%pp_start%")
    if not ival_end:
        ival_end = Cui.CuiCrcEval(Cui.gpc_info, currentArea, "object", "fundamental.%pp_end%")

    # set published status for all transactions in interval
    _setPublishedInWindow(ival_start, ival_end, crewList)


def _setPublishedInWindow(ival_start, ival_end, crewList):
    """
    This command updates the publication status for all transactions in the
    current window.
    """
    Errlog.log("AccountHandler.py::in _setPublishedInWindow")
    stime = time.time()
    crewSet = set(crewList)

    need_reload = False
    for entry in TM.account_entry.search("(& (published=false) (tim>=%s) (tim<%s))" % (ival_start, ival_end)):
            try:
                if str(entry.crew.id) in crewSet:
                    # print entry
                    entry.published = True
                    need_reload = True
            except:
                # We did hit an entry for whom we have not loaded
                continue
            
    if need_reload:
        Errlog.log("AccountHandler.py::_setPublishedInWindow::RELOAD")
        Cui.CuiReloadTable("account_entry", 1)

    Errlog.log("AccountHandler.py::_setPublishedInWindow finsihed in: %.2f s" % (time.time()-stime))
    Errlog.log("AccountHandler.py::leaving _setPublishedInWindow")


##################################################################
# Function for updating the accounts for all changed crew
#
# Improvement: add possibility to override the date interval?


def updateChangedCrew(crew_list=[]):
    """
    This command updates the accounts for all locally modified crew.
    The shall be called from the savePreProc function.
    """
    Errlog.log("AccountHandler.py::in updateChangedCrew()")
    # Check if in database plan
    if not _assert_update():
        return
    # Select modified crew
    modified_crew = Cui.CuiGetLocallyModifiedCrew(Cui.gpc_info) if not crew_list else crew_list

    if not modified_crew:
        Errlog.log("AccountHandler.py:: updateChangedCrew: No modified crew found")
        return

    Errlog.log("AccountHandler.py:: %d changed crew" % len(modified_crew))

    # The new bulk-check is always faster than the old function
    account_set = set([account.id for account in TM.account_set if (
        'SAVED' not in account.id.upper() and
        'ENTITLEMENT' not in account.id.upper() and
        'BUFFER' not in account.id.upper())])

    updateAccountsForCrewInWindow(modified_crew, account_set)


##################################################################
# Function for updating all accounts for all crew in the window
# This function consumes more memory but should be faster for
# many crew (This code is duplicated in the functions above
# for one or some crew
#

F0 = "F0"
F3 = "F3"
F3S = "F3S"
F7 = "F7"
F7S = "F7S"
F9 = "F9"
F15 = "F15"
F16 = "F16"
F31 = "F31"
F32 = "F32"
F33 = "F33"
F35 = "F35"
F36 = "F36"
F38 = "F38"
F89 = "F89"
PR = "PR"
PRE = "PRE"
CCR = "CCR"
CCT = "CCT"
UNKNOWN_APP = "UNKNOWN_APP"

def get_app():
    if application.isTracking:
        return CCT
    elif application.isRostering:
        return CCR
    elif application.isPreplanning:
        return PRE
    else:
        return UNKNOWN_APP

y = True
n = False

REMOVE_LOOKUP_MAP = {
    # (is_published, is_bought, account) : do_remove
    (y, y, F0): y,
    (y, n, F0): n,
    (n, y, F0): y,
    (n, n, F0): y,

    (y, y, F3): y,
    (y, n, F3): y,
    (n, y, F3): y,
    (n, n, F3): y,

    (y, y, F3S): y,
    (y, n, F3S): y,
    (n, y, F3S): y,
    (n, n, F3S): y,

    # F32 similar to F3
    (y, y, F32): y,
    (y, n, F32): y,
    (n, y, F32): y,
    (n, n, F32): y,

    # F35 similar to F3
    (y, y, F35): y,
    (y, n, F35): y,
    (n, y, F35): y,
    (n, n, F35): y,

    # F7 similar to F3
    (y, y, F7): y,
    (y, n, F7): y,
    (n, y, F7): y,
    (n, n, F7): y,

    (y, y, F7S): y,
    (y, n, F7S): y,
    (n, y, F7S): y,
    (n, n, F7S): y,

    # F38 same as F7
    (y, y, F38): y,
    (y, n, F38): y,
    (n, y, F38): y,
    (n, n, F38): y,

    (y, y, F9): y,
    (y, n, F9): n,
    (n, y, F9): y,
    (n, n, F9): y,

    (y, y, F15): y,
    (y, n, F15): n,
    (n, y, F15): y,
    (n, n, F15): y,

    (y, y, F16): y,
    (y, n, F16): n,
    (n, y, F16): y,
    (n, n, F16): y,

    (y, y, F31): y,
    (y, n, F31): y,
    (n, y, F31): y,
    (n, n, F31): y,

    (y, y, F33): y,
    (y, n, F33): y,
    (n, y, F33): y,
    (n, n, F33): y,

    (y, y, F36): y,
    (y, n, F36): n,
    (n, y, F36): y,
    (n, n, F36): y,

    # F89 similar to F36
    (y, y, F89): y,
    (y, n, F89): n,
    (n, y, F89): y,
    (n, n, F89): y,

    # For PR
    (y, y, PR): y,
    (y, n, PR): n,
    (n, y, PR): y,
    (n, n, PR): y,
}


def get_is_bought(crew_id, account_entry):
    f_day_start = account_entry.tim
    query_str = "(& (crew=%s) (start_time<=%s) (end_time>%s) (day_type=F*))" % (crew_id, f_day_start, f_day_start)
    # look for match (f_day_start within bought period for given crew)
    try:
        res = TM.bought_days.search(query_str)
        list_res = list(res)
    except Exception, err:
        import traceback
        traceback.print_exc(err)
    # if a match was found, then day is bought
    return len(list_res) > 0



def get_is_saved(entry):
    is_saved = len(TM.auditTrail(entry)) != 0
    return is_saved


def get_do_remove(is_pub, is_bought, account):
    app = get_app()

    if app in [PRE, CCR]:
        return True
    # else app is CCT

    if account[0] != 'F':
        return True
    # else account is F-account

    lookup_tuplet = (is_pub, is_bought, account)
    return REMOVE_LOOKUP_MAP[lookup_tuplet]


def get_is_in_published_period(abstime):
    """
Checks whether the passed in month is in "published period":
If today is <= 15th of month (Roster release day), then the published period ends at end of this month.
If today is > 15th of month, then the published period ends at end of next month.

Some testcode:

import carmusr.AccountHandler as ah
from AbsTime import AbsTime
print ah.get_is_in_published_period(AbsTime("17Sep2016"))
print ah.get_is_in_published_period(AbsTime("01Oct2016"))
print ah.get_is_in_published_period(AbsTime("01Nov2016"))

"""
    # print "  ## get_is_in_published_period(abstime) <- ", abstime
    now_time = _get_now_time()
    # print "  ## now_time:", now_time
    publish_limit = now_time.month_floor().adddays(15)
    # print "  ## publish_limit:", publish_limit

    # if today is >= publish_limit, then published_period ends last date of next month, else last of this month
    publised_period_end = now_time.month_ceil()
    if now_time >= publish_limit:
        publised_period_end = publised_period_end.addmonths(1)
    # print "  ## publised_period_end:", publised_period_end

    is_in_published_period = abstime < publised_period_end
    # print "  ## is_in_published_period:", is_in_published_period
    return is_in_published_period


def updateAccountsForCrewInWindow(crewid_list, account_list, currentArea=Cui.CuiScriptBuffer):
    """
    This command updates all accounts for all crew in crewid_list. Crew must also
    be in the currentArea.
    """
    Errlog.log("AccountHandler.py:: in updateAccountsForCrewInWindow")
    # Check if in database plan
    if not _assert_update():
        return

    username = Names.username()
    
    nowtime = _get_now_time()
    # Set not published in rostering, but published in Pre and CCT
    if application.isPlanning:
        published = False
    else:
        published = True

    _ONE_DAY = RelTime.RelTime('24:00')

    ppstart = R.eval("pp_start_time")[0]
    ppend = R.eval("pp_end_time")[0]

    # Set crew in scriptbuffer, This is important!! (i.e. don't remove)
    _set_crew_in_buffer(crewid_list)
    # For each account we have to add all activities in the roster
    # We also need to remove all activities not in the roster
    
    # Fetch all entries and work on them
    Errlog.log("AccountHandler.py:: Fetching all account information...")
    crewid_list = set(crewid_list) # improve performance by using sets
    TM(["account_set", "account_entry"])

    nr_entries = 0
    nr_active = 0
    nr_valid = 0
    nr_invalid = 0
    nr_broken = 0
    need_reload = False

    # Check rosters
    for crew_id in crewid_list:
        crew_object = _get_crew_object(crew_id)
        for entry in TM.crew[(crew_id,)].referers('account_entry', 'crew'):  # get entries for crew
            try:
                entry_start = entry.tim
                if entry.man or not (ppstart < entry_start <= ppend):
                    continue
                # Have to catch possible missing reference
                nr_entries += 1
                account = str(entry.getRefI('account'))
                if account not in account_list:
                    continue
                nr_active += 1

                reason = ""
                source = ""
                if entry.reasoncode is not None:
                    reason = str(entry.reasoncode)
                if entry.source is not None:
                    source = str(entry.source)

                rave_valid_exp = 'compdays.%%online_transaction_valid%%("%s", %s, "%s", %s, "%s", %s, "%s")' % (
                    str(entry.crew.id), str(entry.tim), str(entry.account.id), str(entry.amount), reason, str(entry.rate), source)
                # print "  ## rave_valid_exp:", rave_valid_exp
                valid, = crew_object.eval(rave_valid_exp)
                # print "  ## valid:", valid
                if valid is None:
                    # SASCMS-2510
                    raise Exception('compdays.%online_transaction_valid%() was void')
                if not valid:
                    nr_invalid += 1

                    is_published = entry.published and get_is_saved(entry) and get_is_in_published_period(entry.tim)
                    is_bought = get_is_bought(crew_id, entry)

                    if get_do_remove(is_published, is_bought, account):
                        entry.remove()
                        need_reload = True
                else:
                    nr_valid += 1

            except Exception, err:
                Errlog.log("AccountHandler.py:: account_entry %s contains bad data: %s" % (str(entry.id), err))
                nr_broken += 1
    
    Errlog.log("AccountHandler.py:: removed all invalid transactions")
    Errlog.log("AccountHandler.py:: %s/%s/%s/%s/%s (entries/active/valid/invalid/broken)" % (
        nr_entries, nr_active, nr_valid, nr_invalid, nr_broken))
    if need_reload:
        Errlog.log("AccountHandler.py::updateAccountsForCrewInWindow::RELOAD after valid-check")
        Cui.CuiReloadTable("account_entry", 1)
        need_reload = False

    # initialize created account count
    account_count = {}
    for account in account_list:
        account_count[account] = 0
    #################################################################
    for crew_id in crewid_list:
        crew_object = _get_crew_object(crew_id)
        unbooked_where_expr = "compdays.%leg_has_online_transaction_unbooked%"
        leg_where_expr = 'compdays.%leg_affects_accounts% <> ""'

        unbooked_eval_expr = R.foreach(
            R.iter('iterators.leg_set', where=unbooked_where_expr),
            R.foreach(
                R.times('compdays.%nr_account_set_entries%', where=leg_where_expr),
                'leg.%start_hb%',
                'compdays.%leg_affects_accounts%',
                'compdays.%leg_affects_amounts%',
                'compdays.%leg_affects_rates%',
                'compdays.%leg_affects_reasons%',
                'compdays.%leg_affects_sources%',
                'compdays.%leg_affects_comments%'))
        unbooked_tnxs, = crew_object.eval(unbooked_eval_expr)
        for _, tnxs_for_leg in unbooked_tnxs:
            for tnx_for_leg in tnxs_for_leg:
                _, start_hb, account, amount, rate, reason, source, si = tnx_for_leg
                if account not in account_list:
                    continue
                entry = {'crew': crew_id,
                         'amount': amount,
                         'account': account,
                         'tim': start_hb,
                         'source': source,
                         'si': si,
                         'reason': reason,
                         'nowtime': nowtime,
                         'username': username,
                         'rate': rate,
                         'published': published}
                if account in account_count:
                    account_count[account] += 1
                else:
                    account_count[account] = 1  # in case leg affects account not in list.
                _create_account_entry(entry)
                need_reload = True

    # Check if we bought some account-giving activity
    need_reload |= _check_unbooked_bought_periods(
        crewid_list, ppstart, ppend, (published, nowtime), account_list, account_count)

    for account, count in account_count.items():
        Errlog.log("AccountHandler.py::updateAccountsForCrewInWindow: Found %s unbooked %s" % (count, account))
    
    if need_reload:
        Errlog.log("AccountHandler.py::updateAccountsForCrewInWindow::RELOAD after booking")
        Cui.CuiReloadTable("account_entry", 1)


EC_INST = None

def getBaseLineData(crewId, account):
    """
    Get the baseline info, if existant
    """
    baseline_data = {}


    for entry in TM.accumulator_int_run.search("(accname='balance')"):
        try:
            key = entry.acckey
            if key in ('C','F'):
                key = 'COMMON'
            if not baseline_data.has_key(key):
                baseline_data[key] = {'TIM':None, 'VAL':0, 'LASTRUN':None}
            baseline_data[key]['TIM'] = AbsTime.AbsTime(entry.accstart)
            baseline_data[key]['LASTRUN'] = AbsTime.AbsTime(entry.lastrun)
        except Exception, err:
            Errlog.log('AccountHandler.py:: Getting baseline %s'%err)

    try:
        global EC_INST

        if EC_INST == None:
            conn_str = TM.getConnStr()
            schema_str = TM.getSchemaStr()
            EC_INST = EC(conn_str, schema_str)
        for acc_row in EC_INST.account_baseline.search('(crew=%s)'%crewId):
            if acc_row.id == account:
                for baseline in baseline_data:
                    try:
                        if acc_row.tim  == baseline_data[baseline]['TIM']:
                            baseline_data[baseline]['VAL'] = acc_row.val
                    except Exception, err:
                        Errlog.log('AccountHandler.py:: Getting baseline %s'%err)
    finally:
        pass

    return baseline_data


def _check_unbooked_bought_periods(crew_list, ppstart, ppend, entry_info, account_list, account_count):
    """
    Loop through bought periods and create needed account entrys, if account is given
    code updates account matching bought periods
    """
    migration_date, = R.eval('default_context', 'compdays.%account_migration_date%')

    bought_period_cache = []

    bought_periods_to_check = []
    for crew_id in crew_list:
        try:
            crew = TM.crew[(crew_id,)]
            is_svs, = R.eval(
                R.selected('levels.leg'),
                'crew.%has_agmt_group_svs%'
                )
            print "is_svs", is_svs
            if is_svs:
                for bought_period in crew.referers('bought_days_svs', 'crew'):
                    # Check period and migration date, migration date is a safe check!
                    if bought_period.start_time < migration_date or \
                        not (bought_period.start_time <= ppend and bought_period.end_time >= ppstart):
                        continue
                    bought_periods_to_check.append(bought_period)         
            else:
                for bought_period in crew.referers('bought_days', 'crew'):
                    # Check period and migration date, migration date is a safe check!
                    if bought_period.start_time < migration_date or \
                        not (bought_period.start_time <= ppend and bought_period.end_time >= ppstart):
                        continue
                    bought_periods_to_check.append(bought_period)
            
        except EntityNotFoundError:
            Errlog.log("AccountHandler.py:: Warning: " +
                       "Table bought_day has reference to no-existing" +
                       " crew id:%s" % str(bought_period.getRefI('crew')))
    for bought_period in bought_periods_to_check:
        crew_id = bought_period.crew.id
        # Check if already booked
        # If we bought some other activity then we need to mimic that leg lookup
        account = bought_period.day_type  # The account for the other activity
        if account is not None and account in account_list:
            affect_account_info = _bought_period_account_effect(bought_period, account)
            if affect_account_info['effects']:  # this bought activity has to affect its account
                amount = affect_account_info['amount']

                booked, = R.eval('default_context',
                                 'compdays.%%online_transaction_entry_check%%("%s","%s",%s,%s)' % (
                                     crew_id,
                                     account,
                                     amount,
                                     bought_period.start_time))
                if not booked:
                    bought_period_cache.append([account, bought_period])
                    account_count[account] += 1
                    
        # separate BOUGHT_BL and BOUGHT
        account = bought_period.account_name  # The bought account
        if account is not None and account in account_list and account in BOUGHT_ACCOUNT_NAMES:
            rate = 100  # For bought we assume rate is 100
            amount = rate*int((bought_period.end_time -
                               bought_period.start_time)/RelTime.RelTime('24:00'))

            booked, = R.eval('default_context',
                             'compdays.%%online_transaction_entry_check%%("%s","%s",%s,%s)' % (
                                crew_id,
                                account,
                                amount,
                                bought_period.start_time))
            if not booked:
                bought_period_cache.append([account, bought_period])
                account_count[account] += 1

    # Book periods in account_entry
    # Either in BOUGHT or activity account
    for account, bought_period in bought_period_cache:
        if account not in BOUGHT_ACCOUNT_NAMES:  # not BOUGHT, BOUGHT_BL, or BOUGHT_COMP
            _create_activity_account_entry_from_bought_period(bought_period, account, *entry_info)
        else:
            _create_bought_account_entry_from_bought_period(bought_period, *entry_info)
    return len(bought_period_cache) > 0  # There were unbooked tnxs



def _create_activity_account_entry_from_bought_period(bought_period,
                                                      account,published, nowtime ):
    """
    Bought account activities still affecte their accounts
    """
    affect_account_info = _bought_period_account_effect(bought_period,account)
    entry={'crew':bought_period.crew.id,
           'amount':affect_account_info['amount'],
           'account':account,
           'tim':bought_period.start_time,
           'source': bought_period.day_type + ' on Roster',
           'si':'BOUGHT %s on Roster'%bought_period.day_type,
           'reason':REASONCODES["OUT_ROSTER"],
           'nowtime':nowtime,
           'username':bought_period.uname,
           'rate':affect_account_info['rate'],
           'published':published
           }
    # create the actual account
    _create_account_entry(entry)


def _create_bought_account_entry_from_bought_period(bought_period, published, nowtime):
    """
    Create BOUGHT(_BL) account entry from bought period
    """
    source, = R.eval('default_context',
                     'compdays.%%bought_day_source%%("%s")'%bought_period.day_type)
    account = bought_period.account_name
    amount = 100*int((bought_period.end_time-bought_period.start_time)/RelTime.RelTime('24:00'))
    # Bought F3_2 activites should be booked as 2 F3 in F3 account
    if account == "BOUGHT_F3_2":
        amount = 2*amount
    
    entry={'crew': bought_period.crew.id,
           'amount':amount,
           'account':account,
           'tim':bought_period.start_time,
           'source':source,
           'si':'BOUGHT %s: %s'%(bought_period.day_type,bought_period.si),
           'reason':REASONCODES[BOUGHT_ACCOUNT_NAME],
           'nowtime':nowtime,
           'username':bought_period.uname or Names.username(),
           'rate':100,
           'published':published
           }
    # create the actual account
    _create_account_entry(entry)


def _create_account_entry(entry={}):
    """
    Creates an account entry from given dict-data
    """
    newentry = None
    try:
        newentry = TM.account_entry.create((TM.createUUID(),))
        newentry.crew = TM.crew[(entry["crew"],)]
        newentry.account = TM.account_set[(entry["account"],)]
        newentry.tim = entry['tim']
        newentry.source = entry['source'] 
        newentry.si = entry['si']
        newentry.reasoncode = entry['reason']
        newentry.entrytime = entry['nowtime']
        newentry.username = entry['username']
        newentry.amount = entry['amount']
        newentry.rate = entry['rate']
        newentry.man = False
        newentry.published = entry['published']
    except Exception, err:
        if newentry:
            newentry.remove() # Don't leave "empty" account_entries
        Errlog.log("AccountHandler.py:: Error creating account entry:\n'%s'\n"%err)
        return None
    return newentry


def _bought_period_account_effect(bought_period, account):
    """
    Bought account activities still affecte their accounts
    This lookup uses same as normal assigned account-giving activties
    """
    code = bought_period.day_type
    start_utc = bought_period.start_time
    days = int((bought_period.end_time - bought_period.start_time)/RelTime.RelTime('24:00'))
    # get crew object
    crew_object = _get_crew_object(bought_period.crew.id)
    fc, fg, region, patprod = crew_object.eval(
        'crew.%is_pilot%',
        'crew.%%in_fixed_group%%(%s)' % str(start_utc),
        'crew.%%region_at_date%%(%s)' % str(start_utc),
        'crew.%%pattern_prod_ratio_at_date%%(%s)' % str(start_utc))

    arg_string = '"%s","%s", %s, %s,"%s", %s, %s, %s, %s' % (
        account, code, days, fc, region, fg, True, patprod, start_utc)
    # print "  ## arg_string:", arg_string

    affect_account, affect_amount, affect_reason, affect_source = crew_object.eval(
        'compdays.%%activity_affects_account%%(%s)' % arg_string,
        'compdays.%%activity_affects_amount%%(%s)' % arg_string,
        'compdays.%%activity_affects_reason%%(%s)' % arg_string,
        'compdays.%%activity_affects_source%%(%s)' % arg_string)

    ret_data = {
        'days': days, 'effects': affect_account,
        'rate': affect_amount / days, 'amount': affect_amount,
        'reason': affect_reason, 'source': affect_source}
    # print "  ## ret_data:", ret_data

    return ret_data


def _set_crew_in_buffer(crewid_list):
    Cui.CuiDisplayGivenObjects(Cui.gpc_info,
                               Cui.CuiScriptBuffer,
                               Cui.CrewMode,
                               Cui.CrewMode,
                               [str(_id) for _id in crewid_list],
                               0)


def _get_crew_object(crew_id):
    """
    Set crew in scriptbuffer and return crew object
    Make sure crew is in scriptbuffer!
    """

    bc = utils.selctx.BasicContext()
    
    class ReportServerCrewObject(utils.selctx.SingleCrewFilter):
        '''
        Mock crew object to use in report server
        The normal CrewObject with context locator doesnt work so we create our own mockup!
        '''
        def eval(self, *eval_string):  # @ReservedAssignment
            '''
            eval sting in given context
            '''
            context = self.context()
            try:
                ret = R.eval(context, *eval_string)
                return ret
            except R.UsageError:
                # wrong level, fix that quick
                # somewhat trail and error to get the indices correct
                # but it seems to mimic the CrewObject
                # if we send a list or tuple we need to repack answer
                if (isinstance(eval_string, tuple) or isinstance(eval_string, list)) and len(eval_string) > 1:
                    ret = []
                    for item in eval_string:
                        ret.append(R.eval(context, R.foreach('iterators.roster_set', item))[0][0][1],)  # need to be tuple to mimic CrewObject!
                    return ret
                else:
                    ret = (R.eval(context, R.foreach('iterators.roster_set', *eval_string))[0][0][1],)  # need to be tuple to mimic CrewObject!
                    return ret

    return HF.CrewObject(crew_id, Cui.CuiScriptBuffer) if not bc.isRS else ReportServerCrewObject(crew_id)


def _get_now_time():
    now_time, = R.eval('default_context', 'fundamental.%now%')
    return now_time


def _assert_update():
    # Check if in database plan 
    try:
        assert HF.isDBPlan()
        assert application.PAIRING != application.get_product_from_ruleset()
    except AssertionError:
        Errlog.log("AccountHandler.py:: Only available in database plan and not Pairing ruleset")
        return False
    return True


def _debug_transaction_valid(crew_object, entry):
    try:
        print 'Debugging validity for %s'%str(entry)
        transactionid = entry.id
        expr = ('compdays.%%transaction_account%%("%s")'%transactionid, 
                'compdays.%%transaction_crew%%("%s")'%transactionid,
                'compdays.%%transaction_reason%%("%s")'%transactionid,
                'compdays.%%transaction_time%%("%s")'%transactionid,
                'compdays.%%transaction_amount%%("%s")'%transactionid,
                'compdays.%%transaction_rate%%("%s")'%transactionid,
                'compdays.%%transaction_source%%("%s")'%transactionid)

        (account, crew, reason, time, amount, rate, source) = crew_object.eval(*expr)
        
        expr3 = ('bought_days.%%type_on_day%%(%s)'%time,
                 'bought_days.%%start_time_t%%(%s)'%time,
                 'bought_days.%%end_time_t%%(%s)'%time)

        (qk, qk2, qk3) = crew_object.eval(*expr3)
        print  [str(el) for el in (qk, qk2, qk3)]
        
        if rate == 0:
            days = 0
        else:
            days =  amount / rate
        
        expr2 = ('compdays.%%_roster_reason%%("%s")'%reason,
                 'bought_days.%%matching_bought_period_exists%%("%s",%s, %s, %s)' % (qk, time, days, account))
        (roster_reason, period_exists) =  crew_object.eval(*expr2)
        print '-----------------------------------------------------------------------'
        print [str(el) for el in (account, crew, reason, str(time), amount, rate, source, days)]
        print [str(el) for el in (roster_reason, period_exists)]
    except Exception, err:
        print 'Error in debug'
        print err
# end of file    


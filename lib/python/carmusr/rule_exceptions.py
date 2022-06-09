import os
import types
import time

from Localization import MSGR

from carmensystems.mave.core import ldapescape
from carmensystems.mave import etab
from AbsTime import AbsTime
from RelTime import RelTime
import Gui
import Errlog

from carmstd import etab_ext, cui_ext, log, bag_handler

ZERO_SECONDS = RelTime("0:00")
RULE_EXCEPTIONS_TABLE = 'rule_exceptions.%etab_name%'


try:
    import carmensystems.studio.rave.private.RuleException

    def OpenEditFormCrew():
        Errlog.log("In rule_exceptions::OpenEditFormCrew: wrapper for rule exception gui")
        #RuleException.CheckIllegalities()
        carmensystems.studio.rave.private.RuleException.CheckIllegalities()
except:
    Errlog.log("Failed to create RuleException wrapper")


def fetch_save_reload_table(func):
    """
    Decorator wrapping the function with the following table operations:
    - Fetch the table with rule exceptions.
    - Execute func()
    - Sort, save, and reload the table.
    """
    def func_wrapper(*args, **kwargs):
        etable = load_table(RULE_EXCEPTIONS_TABLE)
        func(etable, *args, **kwargs)
        sort_save_reload_exceptions_table(etable)
    return func_wrapper


def sort_save_reload_exceptions_table(etable):
    etable.sort(("crew",))
    cui_ext.reload_table(etable, removeSp=True)


@fetch_save_reload_table
def create(etable, scope="marked"):
    """
    Create rule exceptions for all crew members marked in the left margin or the plan.
    Called by Rule Exceptions > Create and Gherkin.
    """
    if scope == "marked":
        handler = bag_handler.MarkedRostersLeft()
    elif scope == "plan":
        handler = bag_handler.PlanRosters()
    else:
        Gui.GuiError(MSGR("No object selected to create rule exceptions, possible values are a Marked Rosters or the Plan"))
        return
    for chain_bag in handler.bag.chain_set():
        chain_id = chain_bag.rule_exceptions.resource_id()
        rule_exceptions = []
        for _, failure in chain_bag.rulefailures():
            rule_exceptions.append(get_rule_exception(failure))
        create_for_chain(etable, chain_id, rule_exceptions)

    cui_ext.set_message_area('Rule exceptions created')


@fetch_save_reload_table
def clear(etable, scope="marked"):
    """
    Clears the rule exceptions from all crew members marked
    in the left margin or the plan.
    Called by Rule Exceptions > Remove and Gherkin.
    """
    if scope == "marked":
        handler = bag_handler.MarkedRostersLeft()
    elif scope == "plan":
        handler = bag_handler.PlanRosters()
    else:
        Gui.GuiError(MSGR("No object selected to clear rule exceptions, possible values are a Marked Rosters or the Plan"))
        return
    for chain_bag in handler.bag.chain_set():
        crew = chain_bag.rule_exceptions.resource_id()
        _remove_matching_rule_exceptions(etable, {'crew': crew})
    cui_ext.set_message_area('Rule exceptions cleared')


def create_for_chain(etable, chain_id, exceptions):
    """
    Create rule exceptions for chain_id based on exceptions.
    Does not save, nor refresh etable. This is supposed to be done externally.
    """
    static_info = get_static_info()
    old_rows = {}

    for row in etable.search('(&(crew=%s))' % chain_id):
        old_rows[(row.crew, row.ruleid, row.starttime)] = row
    for exc_dict in exceptions:
        exc_dict.update({"crew": chain_id})
        exc_dict.update(static_info)
        new_key = (chain_id, exc_dict['ruleid'], exc_dict['starttime'])
        if new_key in old_rows:
            # Remove a row if it is in the old table and we have a change in values
            old_row = old_rows[new_key]
            if exc_dict["overrel"] == ZERO_SECONDS and exc_dict["overint"] == 0:
                continue
            else:
                exc_dict["overrel"] += old_row.overrel
                exc_dict["overint"] += old_row.overint
                etable.remove(old_row)
        etable.append(exc_dict)


@fetch_save_reload_table
def remove_matching_rule_exceptions(etable, search_keys=None):
    """
    Wrapper method that saves and reloads the rule exceptions table upon
    removal of exceptions.
    This method is called by the legality report for individual or chain-grouped
    removals.
    """
    _remove_matching_rule_exceptions(etable, search_keys)


def _remove_matching_rule_exceptions(etable, search_keys=None):
    """
    Remove all rule exception rows matching the given keys, supplied as a dictionary.
    (**kwargs can't be used since the calling prt.action() does not support it.)

    Valid keys: crew, ruleid, starttime, ruleremark
    If no keys are given all rows are removed.
    """
    if search_keys is None:
        search_keys = {}

    crew = search_keys.get('crew', '*')
    ruleid = search_keys.get('ruleid', '*')
    starttime = search_keys.get('starttime', '*')
    ruleremark = search_keys.get('ruleremark', '*')

    # Sanitize string for LDAP search
    if ruleremark != '*':
        ruleremark = ldapescape("%s", ruleremark)

    search_ldap = '(&(crew=%s)(ruleid=%s)(starttime=%s)(ruleremark=%s))'
    search_filter = search_ldap % (crew, ruleid, starttime, ruleremark)

    result_rows = []
    for row in etable.search(search_filter):
        result_rows.append(row)

    # We can not remove an item while iterating over a search result,
    # as the search result iterator is invalidated if the underlying data
    # container is modified
    for row in result_rows:
        etable.remove(row)


def get_rule_exception(rule_failure):
    """
    Return a dict representing an exception for rule_failure.
    @type rule_failure: A bag representing the rule failure to create
    a rule exception for.
    """
    ruleid = rule_failure.rule.name()
    starttime = rule_failure.startdate

    # If no startdate is defined we create an exception anyway,
    # but it most likely won't apply. The rule is badly implemented.
    if not isinstance(starttime, AbsTime):
        log.info("Missing startdate definition for rule id %s" % ruleid)
        starttime = AbsTime("1Jan1986")
    activitykey = rule_failure.failobject
    if rule_failure.failtext:
        ruleremark = rule_failure.failtext.replace('\n', ' ')
    else:
        ruleremark = 'Not found'
    actualval = rule_failure.actualvalue
    limitval = rule_failure.limitvalue
    if isinstance(rule_failure.overshoot, int):
        overrel = ZERO_SECONDS
        overint = rule_failure.overshoot
    else:
        overrel = rule_failure.overshoot
        if not overrel: overrel = ZERO_SECONDS
        overint = 0

    return {"ruleid": ruleid,
            "starttime": starttime,
            "activitykey": str(activitykey),
            "ruleremark": ruleremark,
            "limitval": str(limitval),
            "actualval": str(actualval),
            "overrel": overrel,
            "overint": overint}


def load_table(rave_path):
    re_fallback = os.path.expandvars("$CARMUSR/crc/etable/SpLocal/rule_exception")
    return etab_ext.load(etab.Session(), rave_path, copy_from=re_fallback, forceSp=True)


def get_static_info():
    """Get information for the rule exception."""
    user = os.environ.get("USER")
    y, m, d, hh, mm = time.gmtime()[0:5]
    ctime = AbsTime(y, m, d, hh, mm)
    reason = 'Manual'
    si = ""
    return {"username": user,
            "ctime": ctime,
            "reason": reason,
            "si": si}

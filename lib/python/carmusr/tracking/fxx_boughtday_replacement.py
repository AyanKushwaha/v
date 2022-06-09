"""
ref SKCMS-628
"""

from tm import TM
import utils.Names
import carmensystems.rave.api as rave

from carmusr.tracking.util.dialog import show_message_dialog, show_do_cancel_dialog, DO
from carmusr.tracking.util.studio import get_leg_object
from carmusr.tracking.util.time_shell import abstime
from carmusr.tracking.util.time_studio import set_now
from salary.reasoncodes import REASONCODES
from salary.account.common.studio import create_account_entry

def _create_entry(crew_id, tim, account, now, source_str, is_add):
    entry = TM.account_entry.create((TM.createUUID(),))

    entry.crew = TM.crew[(crew_id,)]
    entry.tim = tim
    entry.account = TM.account_set[(account,)]
    entry.source = source_str
    entry.amount = 100 if is_add else -100
    entry.man = False
    entry.si = "Bought day %s compensation added at crew's request" % account if is_add else \
        "Bought day %s compensation removed at crew's request" % account
    entry.published = True
    entry.rate = 100 if is_add else -100
    entry.reasoncode = "IN Irregularity" if is_add else "OUT Irregularity"
    entry.entrytime = now
    entry.username = utils.Names.username()


def _replace_dialog_with_args(now, crew_id, start_date, source15_str, source16_str):

    query_str = "(& (crew=%s) (tim=%s) (| (& (account=F15)(source=%s))  (& (account=F16)(source=%s)) ) )" % (
        crew_id, start_date, source15_str, source16_str)
    print "  ## query_str:", query_str

    balance = 0
    for entry in TM.account_entry.search(query_str):
        balance += entry.amount

    if balance <= 0:
        r = show_do_cancel_dialog(
            "Grant F-days",
            """This will grant an F15 and an F16 compensation day,
which will replace bought day compensation for selected day.""",
            "Grant")
        if r == DO:
            _create_entry(crew_id, start_date, "F15", now, source15_str, True)
            _create_entry(crew_id, start_date, "F16", now, source16_str, True)
            create_account_entry(crew_id, "BOUGHT", "Converted to F15+F16", REASONCODES["OUT_CONV"], "", -100, start_date, now, -100)
    else:
        r = show_do_cancel_dialog(
            "Remove F-days",
            """An F15 and F16 compansation day already exists.

This will remove previously granted compensation days.
The crew will instead be payed for for the bought day.""",
            "Remove")
        if r == DO:
            _create_entry(crew_id, start_date, "F15", now, source15_str, False)
            _create_entry(crew_id, start_date, "F16", now, source16_str, False)
            create_account_entry(crew_id, "BOUGHT", "Reverted convertion to F15+F16", REASONCODES["IN_CONV"], "", 100, start_date, now, 100)


def replace_dialog():
    """
    This function is called from    mainDat25CrewCompMode1_Tracking.menu
    and from                        mainDat25CrewCompMode1_DayOfOps.menu
    """
    print "carmusr.tracking.fxx_boughtday_replacement.replace_dialog()"

    # set_now()  # call once to remove any manipulations done previously
    # set_now("05Dec2015 23:59")

    result = get_leg_object().eval(
        "fundamental.%now%",
        "crew.%id%",
        "duty.%start_day%",
        "report_overtime.%bought_FD_F15_source_str%",
        "report_overtime.%bought_FD_F16_source_str%",

    )
    print "  ## result:", result

    return _replace_dialog_with_args(*result)

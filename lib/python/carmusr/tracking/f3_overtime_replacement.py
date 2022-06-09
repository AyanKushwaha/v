"""
ref SKCMS-691
"""

from tm import TM
import utils.Names

from carmusr.tracking.util.dialog import show_message_dialog, show_do_cancel_dialog, DO
from carmusr.tracking.util.studio import get_leg_object
#from carmusr.tracking.util.time import set_now


def create_entry(crew_id, tim, now, source_str, is_add):
    entry = TM.account_entry.create((TM.createUUID(),))

    entry.crew = TM.crew[(crew_id,)]
    entry.tim = tim
    entry.account = TM.account_set[("F3",)]
    entry.source = source_str
    entry.amount = 100 if is_add else -100
    entry.man = False
    entry.si = "Overtime F3 compensation added at crew's request" if is_add else "Overtime F3 compensation removed at crew's request"
    entry.published = True
    entry.rate = 100 if is_add else -100
    entry.reasoncode = "IN Irregularity" if is_add else "OUT Irregularity"
    entry.entrytime = now
    entry.username = utils.Names.username()


def replace_dialog():
    """
    This function is called from    mainDat25CrewCompMode1_Tracking.menu
    and from                        mainDat25CrewCompMode1_DayOfOps.menu
    """
    print "carmusr.tracking.f3_overtime_replacement.replace_dialog()"

    # set_now()  # call once to remove any manipulations done previously
    # set_now("05Dec2015 23:59")

    qualified_crew, overtime_units, checkout_date, crew_id, now, source_str, is_valid, valid_date = \
        get_leg_object().eval(
            "salary_overtime.%OT_FD_qualified_crew%",
            "salary_overtime.%OT_FD_units%",
            "duty.%end_day%",
            "crew.%id%",
            "fundamental.%now%",
            "report_overtime.%OT_FD_F3_source_str%",
            "parameters.%f3_overtime_comp_valid%(fundamental.%now%)",
            "parameters.%f3_overtime_comp_valid_date%"
        )

    if not is_valid:
        show_message_dialog(
            "Not valid yet",
            """This options will only become valid starting %s.""" % valid_date)
        return

    if not qualified_crew:
        show_message_dialog(
            "Not qualified crew",
            """This options is applicable only to FD, except for CJ pilots (including SK).""")
        return

    if overtime_units == 0:
        show_message_dialog(
            "No overtime",
            """No applicable overtime found for selected duty.""")
        return

    c_m = checkout_date.month_floor()
    n_d = now.day_floor()
    n_m = now.month_floor()
    n_limit = n_m.adddays(4)
    limit_passed = False
    if n_m != c_m:
        if n_m.addmonths(-1) == c_m:  # n_m - 1 == c_m:  careful!
            limit_passed = n_d >= n_limit
        else:
            limit_passed = True

    if limit_passed:
        print "  ## limit passed!"
        show_message_dialog(
            "Limit passed",
            """An F3 compensation day can be granted no later than the 4th day of the month following the month of the checkout day.
This is due to deadlines for salary runs.""")
        return

    balance = 0
    query_str = "(& (crew=%s) (tim=%s) (account=F3) (source=%s))" % (crew_id, checkout_date, source_str)
    print "  ## query_str:", query_str
    for entry in TM.account_entry.search(query_str):
        balance += entry.amount

    if balance <= 0:
        r = show_do_cancel_dialog(
            "Grant F3",
            """This will grant an F3 compensation day,
which will replace overtime compensation for selected duty.

Warning! Requires 'Save' from Studio to be commited to database.""",
            "Grant")
        if r == DO:
            create_entry(crew_id, checkout_date, now, source_str, True)
    else:
        r = show_do_cancel_dialog(
            "Remove F3",
            """An F3 compansation day already exists.

This will remove previously granted F3 compensation day.
The crew will in stead be payed for overtime for selected duty.

Warning! Requires 'Save' from Studio to be commited to database.""",
            "Remove")
        if r == DO:
            create_entry(crew_id, checkout_date, now, source_str, False)




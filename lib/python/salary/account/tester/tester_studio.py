"""
This script is for testging/sumulation different grant/remove/update scripts.

It should only be loaded from within a Studio, and is generally lauched by simulator.py


"""

import carmusr.tracking.util.time_shell as tshell
import carmusr.tracking.util.time_studio as tstudio
import adhoc.developer_menu as devmen

from Cfh import Box, Function, Done, Area, Loc, Dim, Label, String, Separator
from tm import TM
import carmstd.studio.cfhExtensions as cfhExtensions

import salary.account.f0.f0_grant as f0_grant
import salary.account.f0.f0_correct as f0_correct

import salary.account.f9.f9_grant as f9_grant
import salary.account.f9.f9_reset as f9_reset

import salary.account.f36.f36_grant as f36_grant
import salary.account.f36.f36_correct as f36_correct
import salary.account.f36.f36_reset as f36_reset


MONTHS_STR = ";" + ";".join(tshell.MONTHS)
YEARS = ["2015", "2016", "2017", "2018", "2019", "2020"]
YEAR_STR = ";" + ";".join(YEARS)

CONTINUE = "CONTINUE"
ABORT = "ABORT"

needs_reload = False  # gets set to True run is done, and False when reload is done


def reload_dialog():
    print "  reload_dialog ..."
    if needs_reload:
        button_strings = ["Reload first", "Skip reload", "Abort run"]
        buttons = [(s,s) for s in button_strings]
        res = cfhExtensions.ask(
            "Reload of data (in Rave) needed after doing run, before doing new run.", title="Reload", buttons=buttons)
        print "  ## res:", res
        if res == button_strings[0]:
            do_reload()
            return CONTINUE
        elif res == button_strings[1]:
            return CONTINUE
        else:
            return ABORT
    return CONTINUE


def do_reload():
    print "  do_reload ..."
    devmen.DeveloperMenu("-").action_reload()
    global needs_reload
    needs_reload = False


class ReloadFn(Function):
    def action(self):
        do_reload()


class ResetFn(Function):
    def action(self):
        print "  reset ..."
        TM.reset(["account_entry"])
        global needs_reload
        needs_reload = True


class RunFn(Function):

    def __init__(self, month_cfh_string, year_cfh_string, *args):
        Function.__init__(self, *args)
        self.month = month_cfh_string
        self.year = year_cfh_string

    def run(self, runable):
        now_str = "01%s%s" % (self.month.getValue(), self.year.getValue())
        tstudio.set_now(now_str)
        print "  run ..."
        if reload_dialog() == ABORT:
                return
        # print "  ## now:", now_str
        runable()
        tstudio.set_now()
        global needs_reload
        needs_reload = True


class F0GrantFn(RunFn):
    def action(self):
        self.run(f0_grant.main)


class F0CorrectFn(RunFn):
    def action(self):
        self.run(f0_correct.main)


class F9GrantFn(RunFn):
    def action(self):
        self.run(f9_grant.main)


class F9ResetFn(RunFn):
    def action(self):
        self.run(f9_reset.main)


class F36GrantFn(RunFn):
    def action(self):
        self.run(f36_grant.main)


class F36CorrectFn(RunFn):
    def action(self):
        self.run(f36_correct.main)


class F36ResetFn(RunFn):
    def action(self):
        self.run(f36_reset.main)


def area(x, y, w, h=1):
    return Area(Dim(w, h), Loc(x, y))


def inc(n, step=1):
    return n + step


class NumberVar:

    def __init__(self, number=0):
        self.num = number

    def __call__(self):
        return self.get()

    def get(self):
        return self.num

    def set(self, number):
        self.num = number
        return self

    def inc(self, step=1):
        self.num = inc(self.num, step)
        return self


def main():
    print " tester_studio.main"

    box = Box("box", "Tester")

    now = tshell.abstime_now()
    now_year_str = now.getValue()[5:9]
    now_month_str = now.getValue()[2:5].capitalize()

    row_val = NumberVar(1)
    now_label = Label(box,  None, area(row_val.get(), 0, 5), "Now:")

    month = String(box, "month", area(row_val.get(), 6, 6), 3, now_month_str)
    month.setMenuOnly(1)
    month.setMenuString(MONTHS_STR)

    year = String(box, "year", area(row_val.get(), 12, 7), 4, now_year_str)
    year.setMenuOnly(1)
    year.setMenuString(YEAR_STR)  # TODO: fix this hardcoding

    row_val.inc()
    f0_grant_button = F0GrantFn(month, year, box, "f0_grant", area(row_val.inc().get(), 0, 25), "Run F0 grant", None, 0, 0, 0)
    f0_corr_button = F0CorrectFn(month, year, box, "f0_corr", area(row_val.inc().get(), 0, 25), "Run F0 correct", None, 0, 0, 0)
    row_val.inc()
    f9_grant_button = F9GrantFn(month, year, box, "f9_grant", area(row_val.inc().get(), 0, 25), "Run F9 grant", None, 0, 0, 0)
    f9_reset_button = F9ResetFn(month, year, box, "f9_reset", area(row_val.inc().get(), 0, 25), "Run F9 reset", None, 0, 0, 0)
    row_val.inc()
    f36_grant_button = F36GrantFn(month, year, box, "f36_grant", area(row_val.inc().get(), 0, 25), "Run F36 grant", None, 0, 0, 0)
    f36_corr_button = F36CorrectFn(month, year, box, "f36_corr", area(row_val.inc().get(), 0, 25), "Run F36 correct", None, 0, 0, 0)
    f36_reset_button = F36ResetFn(month, year, box, "f36_reset", area(row_val.inc().get(), 0, 25), "Run F36 reset", None, 0, 0, 0)
    row_val.inc()
    row_val.inc()
    reload_button = ReloadFn(box,  "reload",  area(row_val.inc().get(), 0, 25), "Reload Rave data", None, 0, 0, 0)
    row_val.inc()
    reset_button = ResetFn(box,  "reset",  area(row_val.inc().get(), 0, 25), "Reset account_entry", None, 0, 0, 0)

    blank_line = Label(box,  None, area(row_val.inc().get(), 0, 25), None)
    done = Done(box, "exit", area(-1, -1, 20), "Done", None)

    box.build()
    box.show(1)

    if box.loop():
        raise "loop"

    return "EXIT"


# (& (crew=34943) (account=F36) (tim>=01Jan2015) )
# (& (crew=35859) (account=F36) (tim>=01Jan2016) )

"""This module must only be imported from "within studio",
as it loads studio-specific modules."""

from tm import TM
import utils.Names
import tempfile
import Csl


def entitlement_corr_reason(n):
    return "IN Entitlement"

def create_account_entry(
        crew_id, account_set,
        source,
        reasoncode,
        si,
        amount,
        tim, entrytime,
        rate=100):

    entry = TM.account_entry.create((TM.createUUID(),))
    entry.crew = TM.crew[(crew_id,)]
    entry.tim = tim
    entry.account = TM.account_set[(account_set,)]
    entry.source = source
    entry.si = si
    entry.amount = amount
    entry.rate = rate
    entry.reasoncode = reasoncode
    entry.entrytime = entrytime
    entry.man = False
    entry.username = utils.Names.username()
    entry.published = True


def create_and_open_temp_file():
    """Abstraction function to create a temp file"""
    f_name = tempfile.mktemp()
    f = open(f_name, "w")
    return f


def show_file_in_window(title, temp_f):
    """Uses csl to show a text file"""
    Csl.Csl().evalExpr('csl_show_file("%s","%s",0)' % (title, temp_f.name))


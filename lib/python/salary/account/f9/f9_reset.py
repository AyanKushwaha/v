"""
Not to be called directly.
See f9.py for usage.
"""

import carmensystems.rave.api as R
from tm import TM
import Cui

import salary.account.common.shell as sh
import salary.account.common.studio as st


class Sum:
    """a simple object for encapsulating the sum."""

    def __init__(self):
        self.__sum = 0

    def add(self, n):
        self.__sum += n

    def get(self):
        return self.__sum


def main():
    print "f9_remove.py main()"

    do_save, is_daemon = sh.get_save_and_daemon()
    print "  ## do_save:", do_save
    print "  ## is_daemon:", is_daemon

    now, reset_str = R.eval('fundamental.%now%',"report_account.%f9_reset_str%")
    reset_str_legacy = "OUT Correction"
    # print "  now:", now
    year_start = now.addyears(-1).year_floor()
    year_end = now.addyears(-1).year_ceil()
    jan_first = now.year_floor()
    # print "  jan02:", jan02

    crew_map = dict()

    # accumulate values for last year
    query_str = "(& (tim>=%s) (tim<%s) (account=F9) (! (| (reasoncode=%s) (reasoncode=%s))))" % (
        year_start, year_end, reset_str, reset_str_legacy)
    print "  ## query_str:", query_str

    for entry in TM.account_entry.search(query_str):
        crew_id = entry.crew.id
        # print "         crew_id:", crew_id, " amount:", entry.amount
        crew_map.setdefault(crew_id, Sum()).add(entry.amount)

    # add any corrections
    for crew_id, sum_obj in crew_map.iteritems():
        _sum = sum_obj.get()
        print "    crew:", crew_id, "  _sum:", _sum
        if _sum > 0:
            print " creating entry ..."
            st.create_account_entry(
                crew_id, "F9",
                "salary.account.f9.f9_reset",
                reset_str,
                "",
                _sum*-1,
                jan_first, now)

    if do_save:
        TM.save()
        revid = TM.getSaveRevId()
        print "Saved changes with revid %s" % revid

    if is_daemon:
        Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)

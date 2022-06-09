"""
Not to be called directly.
See f36.py for usage.
"""

import carmensystems.rave.api as R
from tm import TM
import Cui

import salary.account.common.shell as sh
import salary.account.common.studio as st





def main():
    print "f36_remove.py main()"

    do_save, is_daemon = sh.get_save_and_daemon()
    print "  ## do_save:", do_save
    print "  ## is_daemon:", is_daemon

    now, reset_str = R.eval("fundamental.%now%", "report_account.%f36_reset_str%")
    reset_str_legacy = '"F36'  # "36 because of typo in previous version of similar script
    year_start = now.addyears(-1).year_floor()
    year_end = now.addyears(-1).year_ceil()
    jan_first = now.year_floor()

    out_file = st.create_and_open_temp_file()

    def outln(strng=""):
        print strng
        if is_daemon:
            return
        out_file.write(strng + "\n")

    outln(" now: %s" % now)

    f_str = " [%3s]   %-5s   %-35s  %5s"
    line = f_str % ("CNT", "ID", "NAME", "CORR")
    outln(line)
    outln("")

    # accumulate values for last year
    crew_map = dict()
    query_str = "(& (tim>=%s) (tim<%s) (account=F36) (! (| (reasoncode=%s) (reasoncode='%s'))))" % (
        year_start, year_end, reset_str, reset_str_legacy)
    print "  ## query_str:", query_str

    for entry in TM.account_entry.search(query_str):
        crew_id = entry.crew.id
        crew_map.setdefault(crew_id, sh.Sum()).add(entry.amount)

    # add any corrections
    for crew_id, sum_obj in crew_map.iteritems():
        amount = sum_obj.get() * -1
        name, = R.eval('crew.%%fullname_by_id%%("%s")' % crew_id)
        line = f_str % ("", crew_id, name, amount)
        outln(line)
        if amount != 0:
            print " creating entry ..."
            st.create_account_entry(
                crew_id, "F36",
                "salary.account.f36.f36_reset",
                reset_str,
                "",
                amount,
                jan_first, now)

    outln("")
    outln("END")
    out_file.close()

    if do_save:
        TM.save()
        revid = TM.getSaveRevId()
        print "  ## Saved changes with revid: %s" % revid

    if is_daemon:
        Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)
    else:
        st.show_file_in_window("F36 reset result", out_file)

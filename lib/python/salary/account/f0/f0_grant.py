"""
Not to be called directly.
See f0.py for usage.
"""

import carmensystems.rave.api as R
from tm import TM
import Cui

import salary.account.common.shell as sh
reload(sh)
import salary.account.common.studio as st
reload(st)


def main():
    print "f0_grant.py main()"
    do_save, is_daemon = sh.get_save_and_daemon()
    print "  ## do_save:", do_save
    print "  ## is_daemon:", is_daemon

    now, = R.eval('fundamental.%now%')
    jan01 = now.addyears(1).year_floor()  # 01Jan____ (now-year)

    where_str = "report_account.%%is_f0_eligable_at_date%%(%s)" % jan01
    print "  ## where_str:", where_str

    crew_list, = R.eval(
        "sp_crew",
        R.foreach(
            R.iter("iterators.roster_set", where=where_str),
            "crew.%id%",
            "crew.%fullname%",
            "report_account.%%f0_quota_at_date%%(%s)" % jan01,
            "report_account.%%duty_percent_at_date%%(%s)" % jan01,
            "report_account.%%f0_quota_group_desc_at_date%%(%s)" % jan01,
        ))

    temp_f = st.create_and_open_temp_file()

    def wln(s):
        temp_f.write(s + "\n")

    f_str = " [%3s]   %-5s   %-35s  %5s   %3s%%   %s"
    line = f_str % ("CNT", "ID", "NAME", "GRANT", "", "DESC")
    print line
    wln(line)
    wln("")

    for ix, crew_id, name, amount, duty_percent, desc in crew_list:
        line = f_str % (ix, crew_id, name, amount, duty_percent, desc)
        print line
        wln(line)
        st.create_account_entry(
                crew_id, "F0",
                "Entitled F0 days",
                "IN Entitlement",
                "",
                amount,
                jan01, now)
    wln("")
    wln("END")
    temp_f.close()
    print "  ## grant done "

    if do_save:
        TM.save()
        revid = TM.getSaveRevId()
        print "  ## Saved changes with revid %s" % revid

    if is_daemon:
        Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)
    else:
        st.show_file_in_window("F0 grant result", temp_f)

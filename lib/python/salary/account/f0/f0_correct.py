"""
Not to be called directly.
See f0.py for usage.
"""

import carmensystems.rave.api as R
from tm import TM
import Cui

import salary.account.common.shell as sh
import salary.account.common.studio as st

from salary.reasoncodes import REASONCODES


TAB1 = " " * 4
TAB2 = TAB1 * 2
TAB3 = TAB1 * 3
TAB4 = TAB1 * 4

ACCOUNT = "F0"


def entry_tag(n):
    return "(DO ENTRY)" if n else ""


def main():
    print "f0_correct.py main()"
    do_save, is_daemon = sh.get_save_and_daemon()
    print "  do_save:", do_save
    print "  is_daemon:", is_daemon

    out_file = st.create_and_open_temp_file()
    
    def outln(strng=""):
        print strng
        if is_daemon:
            return
        out_file.write(strng + "\n")

    now, entitled_str, correction_str, round_str = R.eval(
        'fundamental.%now%',
        'report_account.%f0_entitled_str%',
        'report_account.%f0_correction_str%',
        'report_account.%f0_round_str%',
    )

    year_start = now.year_floor()
    now_month_start = now.month_floor()

    months = [year_start.addmonths(ix) for ix in range(12)]
    month_reduction_strings = R.eval(*['report_account.%%f0_reduction_str_built%%(%s)' % m for m in months])
    month_incremented_expr = "add_months(%s, fundamental.%%py_index%% - 1)" % year_start

    # where_str = "report_account.%%is_f0_eligable_at_date%%(%s)" % now_month_start

    crews, = R.eval(
        "sp_crew",
        R.foreach(
            R.iter("iterators.roster_set"),  # , where=where_str
            "crew.%id%",
            "crew.%fullname%",
            'report_account.%%account_sum_year%%(%s, "%s", "%s")' % (year_start, ACCOUNT, entitled_str),
            'report_account.%%account_sum_year%%(%s, "%s", "%s")' % (year_start, ACCOUNT, correction_str),
            'report_account.%%account_sum_year%%(%s, "%s", "%s")' % (year_start, ACCOUNT, round_str),
            R.foreach(
                R.times(12),
                "report_account.%%f0_quota_at_date%%(%s)" % month_incremented_expr,  # is for year, not month.
                'report_account.%%reducing_days_in_month%%(%s, "%s")' % (month_incremented_expr, ACCOUNT),
                'report_account.%%f0_reduction_in_month%%(%s)' % month_incremented_expr,
                'report_account.%%account_sum_month%%(%s, "%s", report_account.%%f0_reduction_str_built%%(%s))' % (
                    month_incremented_expr, ACCOUNT, month_incremented_expr)
            ),
        ))

    outln(" now: %s" % now)

    crew_str = " [%3s]    %-5s    %-35s"
    crew_heading = crew_str % ("CRW", "ID", "NAME")
    outln()
    outln(crew_heading)

    month_str = TAB1 + " [%2s]   %10s    %10s    %10s    %10s    %10s  %s"
    month_heading = month_str % ("MTH", "ENTITLED", "REDUCER", "REDUCTION", "CORR FOUND", "CORR NEEDED", "")

    for crew in crews:
        outln()
        outln()
        outln(crew_str % crew[:3])
        outln()
        outln(month_heading)

        ixc, crew_id, crew_name, entitled_found, entitled_corr_found, round_found, months = crew

        corrections_total_existing = entitled_corr_found
        entitled_corr_new_sum = 0

        entitled_pr_month_sum = 0

        for month in months:
            ixm, entitled_pr_month, reducer, reduction_calc, reduction_corr_found = month
            ixm0 = int(str(ixm)) - 1
            entitled_pr_month_sum += entitled_pr_month
            reduction_corr_new = 0
            if reducer != 0:
                if reduction_calc != reduction_corr_found:
                    reduction_corr_new = reduction_calc - reduction_corr_found  # should normally be a negative number

            corrections_total_existing += reduction_corr_found
            entitled_corr_new_sum += reduction_corr_new

            outln(
                month_str % (
                    ixm, "%s/12" % entitled_pr_month, reducer, reduction_calc, reduction_corr_found,
                    reduction_corr_new, entry_tag(reduction_corr_new)))
            if reduction_corr_new:
                st.create_account_entry(
                    crew_id, ACCOUNT,
                    month_reduction_strings[ixm0],
                    REASONCODES["OUT_REDUCTION" if reduction_corr_new < 0 else "IN_REDUCTION"],
                    "",
                    reduction_corr_new,
                    year_start.addmonths(ixm0), now,
                    -100 if reduction_corr_new < 0 else 100)

        entitled_balance_found = entitled_found + entitled_corr_found
        entitled_should_be = entitled_pr_month_sum / 12  # is for 12 years. Divide to get for 12 months.
        entitled_corr_new = entitled_should_be - entitled_balance_found

        entitled_corr_new_sum += entitled_corr_new

        total_balance_is = entitled_found + corrections_total_existing
        total_balance_should_be = total_balance_is + entitled_corr_new_sum

        # round_found = int(round(total_balance_is, -2)) - total_balance_is  # TODO: REMOVE!
        total_balance_w_rounds_is = total_balance_should_be + round_found
        total_balance_w_rounds_should_be = int(round(total_balance_should_be, -2))
        round_new = total_balance_w_rounds_should_be - total_balance_w_rounds_is

        outln()
        outln(" ENTITLED         found: %4s    should be: %4s    corr found: %4s     corr needed: %4s  %s" % (
            entitled_found, entitled_should_be, entitled_corr_found, entitled_corr_new, entry_tag(entitled_corr_new)))
        if entitled_corr_new:
            st.create_account_entry(
                crew_id, ACCOUNT,
                entitled_str,
                REASONCODES["OUT_CORR" if entitled_corr_new < 0 else "IN_CORR"],
                "",
                entitled_corr_new,
                now_month_start, now,
                -100 if entitled_corr_new < 0 else 100)
        outln()
        outln(" TOTAL            found: %4s    should be: %4s   corrs found: %4s    corrs needed: %4s" % (
            total_balance_is, total_balance_should_be, corrections_total_existing, entitled_corr_new_sum))

        outln(" TOTAL ROUNDED    found: %4s    should be: %4s  rounds found: %4s    round needed: %4s  %s" % (
            total_balance_w_rounds_is, total_balance_w_rounds_should_be, round_found, round_new, entry_tag(round_new)))
        if round_new:
            st.create_account_entry(
                crew_id, ACCOUNT,
                round_str,
                REASONCODES["OUT_ROUND" if round_new < 0 else "IN_ROUND"],
                "",
                round_new,
                now_month_start, now,
                -100 if round_new < 0 else 100)

    outln()
    outln("END")
    out_file.close()
    print "  ## correct done "

    if do_save:
        TM.save()
        revid = TM.getSaveRevId()
        print "  ## Saved changes with revid: %s" % revid

    if is_daemon:
        Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)
    else:
        st.show_file_in_window("F0 corrections report", out_file)

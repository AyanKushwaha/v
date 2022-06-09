"""
Not to be called directly.
See f9.py for usage.
"""

import carmensystems.rave.api as R
from tm import TM
import Cui

import salary.account.common.shell as sh
import salary.account.common.studio as st


def main():
    print "f9_grant.py main()"

    do_save, is_daemon = sh.get_save_and_daemon()
    print "  ## do_save:", do_save
    print "  ## is_daemon:", is_daemon

    now, = R.eval('fundamental.%now%', )
    jan01 = now.addyears(1).year_floor()

    # (& (account=F9) (crew=44137))
    where_str = 'crew.%%has_agmt_group_sks_fd%% ' \
                'and crew.%%in_variable_group%%(%s) ' \
                'and not crew.%%has_ac_qln%%(%s, "CJ")' \
                % (jan01, jan01)

    print "  ## where_str:", where_str

    crew_list, = R.eval(
        'sp_crew',
        R.foreach(
            R.iter('iterators.roster_set', where=where_str),
            'crew.%id%'))

    for (ix, crew_id) in crew_list:
        # print "  ## crew_id:", crew_id
        st.create_account_entry(
                crew_id, "F9",
                "Entitled F9 day",
                "IN Entitlement",
                "",
                100,
                jan01, now)

    print "  ## grant done "

    if do_save:
        TM.save()
        revid = TM.getSaveRevId()
        print "Saved changes with revid %s" % revid

    if is_daemon:
        Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)

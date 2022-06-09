"""
Not to be called directly.
See f32.py for usage.
"""

import carmensystems.rave.api as R
from tm import TM
import Cui

import salary.account.common.shell as sh
import salary.account.common.studio as st


def main():
    print "f32_60plu_grant.py main()"

    do_save, is_daemon = sh.get_save_and_daemon()
    print "  ## do_save:", do_save
    print "  ## is_daemon:", is_daemon

    now, = R.eval('fundamental.%now%', )
    jan01 = now.year_floor()
    Sep01 = jan01.addmonths(8)
    Nov01 = jan01.addmonths(10)
    Nov_20_yrs = Nov01.addyears(-20)
    print "Nov_before_20_yrs:", Nov_20_yrs
    print "date is : " , Nov01


    


    # (& (account=F32) 

    where_str = 'crew.%%is_cabin%% ' \
                    'and crew.%%has_agmt_group_skd_cc%% ' \
                    'and report_account.%%has_age_60plus%%(%s)' \
                    'and report_account.%%is_f32_crew_base_group_at_date%%(%s)'\
                    'and report_account.%%crew_has_min_20yrs_exp_at_cph%%(%s,%s)'\
                    % (Nov01,now,Nov01,Nov_20_yrs)
                    

    crew_list, = R.eval(
            'sp_crew',
            R.foreach(
                R.iter('iterators.roster_set', where=where_str),
                'crew.%id%'))

    for (ix, crew_id) in crew_list:
        print "  ## crew_id:", crew_id
        st.create_account_entry(
                crew_id, "F32",
                "Entitled F32 day",
                "IN Entitlement",
                "Senior Day",
                100,
                Sep01, now)

    print "  ## grant done "
    
    if do_save:
        TM.save()
        revid = TM.getSaveRevId()
        print "Saved changes with revid %s" % revid

    if is_daemon:
        Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)




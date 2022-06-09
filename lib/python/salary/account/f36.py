"""
This script handles the new F36 account type.
Ref. SKCMS-673, SKCMS-814
"""

import sys

import salary.account.common.shell as sh
import carmusr.tracking.util.time_shell as tshell


def main():

    args = sh.get_sys_args()
    print "  optional argument --save found:", args.save
    print "  optional argument --daemon found:", args.daemon

    if not (args.grant or args.correct or args.reset):
        print """Run with argument:
grant      - Adds F36 days for all cabin crew based on agreement at 01Jan
             (To be run on 01Nov)
reset      - Resets any unused or overused F36 from the previous year.
             (To be run on 02Jan)
correct     - Corrects entitlements, reductions, and rounding
             (To be run on 01 every month)

--save     - Optional argument.  Without it, only a "dry run" is performed (no commit to DB).
--daemon   - Optional argument. Runs the process without GUI.
             Without it, Tracking studio is opened, all output goes to standard out,
             and the process only exits when studio is closed.

example usages:
    # in a "user", first do:
    bin/cmsshell  # must be in cmsshell

    carmrunner salary/account/f36.py grant
    carmrunner salary/account/f36.py grant --daemon
    carmrunner salary/account/f36.py grant --save --daemon
"""
        return 2

    command = sh.studio_launch_command(args.daemon)
    pp_start = tshell.abstime_now()
    pp_start_month_start = pp_start.month_floor()
    pp_start_month_end = pp_start_month_start.month_ceil()

    environment = sh.get_environmnent()
    sh.set_save_and_daemon(environment, args)

    if args.grant:
        sh.set_studio_params(
            environment,
            pp_start_month_start.year_floor().addyears(1),
            pp_start_month_end.year_floor().addyears(1),
            "'salary.account.f36.f36_grant;salary.account.f36.f36_grant.main()'")
    elif args.correct:
        sh.set_studio_params(
            environment,
            pp_start_month_start.addmonths(-1),
            pp_start_month_start.addmonths(2),
            "'salary.account.f36.f36_correct;salary.account.f36.f36_correct.main()'")
    elif args.reset:
        sh.set_studio_params(
            environment,
            pp_start_month_start,
            pp_start_month_end,
            "'salary.account.f36.f36_reset;salary.account.f36.f36_reset.main()'")

    return_code = sh.run_command(command, environment)
    print "return_code: %s" % return_code

    print "####### F36 SCRIPT ENDED #######"
    return 0


if __name__ == '__main__':
    main()

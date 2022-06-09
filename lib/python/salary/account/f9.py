"""
This script handles the new F9 account type.
Ref. SKCMS-648
"""

import salary.account.common.shell as sh
import carmusr.tracking.util.time_shell as tshell


def main():
    args = sh.get_sys_args()
    print "  optional argument --save found:", args.save
    print "  optional argument --daemon found:", args.daemon

    if not (args.grant or args.reset):
        print """Run with argument:
grant      - Adds one F9 day for all crew in VG, SKS-FD-AG. Only crew who are in VG on 01Jan are entitled.
             (To be run on 01Nov)
reset     - Resets any unused F9 from the previous year.
             (To be run on 02Jan)

--save     - Optional argument.  Without it, only a "dry run" is performed (no commit to DB).
--daemon   - Optional argument. Runs the process without GUI.
             Without it, Tracking studio is opened, all output goes to standard out,
             and the process only exits when studio is closed.

example usages:
    # in cmsshell
    carmrunner salary/account/f9.py grant
    carmrunner salary/account/f9.py grant --daemon
    carmrunner salary/account/f9.py grant --save --daemon
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
            "'salary.account.f9.f9_grant;salary.account.f9.f9_grant.main()'")
    elif args.reset:
        sh.set_studio_params(
            environment,
            pp_start_month_start,
            pp_start_month_end,
            "'salary.account.f9.f9_reset;salary.account.f9.f9_reset.main()'")

    return_code = sh.run_command(command, environment)
    print "return_code: %s" % return_code

    print "####### F9 SCRIPT ENDED #######"
    return 0


if __name__ == '__main__':
    main()

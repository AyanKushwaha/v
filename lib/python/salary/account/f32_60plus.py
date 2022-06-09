

"""
This script handles the new f32_60plus account type.
Ref. SKCMS-2474
"""

import salary.account.common.shell as sh
import carmusr.tracking.util.time_shell as tshell


def main():
    args = sh.get_sys_args()
    print "  optional argument --save found:", args.save
    print "  optional argument --daemon found:", args.daemon
    
    if not (args.grant):
        print """Run with argument:
grant      - Adds one F32 day for all crew in  SKD-cc-AG. Only crew who are 60 yr old or more on 01NOV are entitled.
             (To be run on 01Sep)

--save     - Optional argument.  Without it, only a "dry run" is performed (no commit to DB).
--daemon   - Optional argument. Runs the process without GUI.
             Without it, Tracking studio is opened, all output goes to standard out,
             and the process only exits when studio is closed.

example usages:
    # in cmsshell
    carmrunner salary/account/f32_60plus.py grant
    carmrunner salary/account/f32_60plus.py grant --daemon
    carmrunner salary/account/f32_60plus.py grant --save --daemon
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
            "'salary.account.f32.f32_60plus_grant;salary.account.f32.f32_60plus_grant.main()'")

    


    return_code = sh.run_command(command, environment)
    print "return_code: %s" % return_code

    print "####### F32 SCRIPT ENDED #######"
    return 0

if __name__ == '__main__':
    main()

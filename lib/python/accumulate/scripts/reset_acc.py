"""
This script handles the resetting value in accumulator_int table.
"""

import accumulate.scripts.common.shell as sh
import carmusr.tracking.util.time_shell as tshell


def main():
    args = sh.get_sys_args()
    print "  optional argument --save found:", args.save
    print "  optional argument --daemon found:", args.daemon
    
    if not (args.grant):
        print """Run with argument:
grant      - Allows to run the script

--save     - Optional argument.  Without it, only a "dry run" is performed (no commit to DB).
--daemon   - Optional argument. Runs the process without GUI.
             Without it, Tracking studio is opened, all output goes to standard out,
             and the process only exits when studio is closed.

example usages:
    # in cmsshell
    carmrunner accumulate/scripts/reset_acc.py grant
    carmrunner accumulate/scripts/reset_acc.py grant --daemon
    carmrunner accumulate/scripts/reset_acc.py grant --save --daemon
"""
        return 2

    command = sh.studio_launch_command(args.daemon)
    pp_start = tshell.abstime_now()
    pp_start_month_start = pp_start.month_floor()
    pp_start_month_end = pp_start_month_start.month_ceil()

    environment = sh.get_environmnent()
    sh.set_save_and_daemon(environment, args)
    print "pp start month start is  " , pp_start_month_start.addmonths(0)
    print "pp start month end is ", pp_start_month_end.addmonths(2)
    if args.grant:
        sh.set_studio_params(
            environment,
            pp_start_month_start.addmonths(0),
            pp_start_month_end.addmonths(2),
            "'accumulate.scripts.reset_acc.reset_accgrant;accumulate.scripts.reset_acc.reset_accgrant.main()'")


    return_code = sh.run_command(command, environment)
    print "return_code: %s" % return_code

    print "####### Reset Accumulate script ENDED #######"
    return 0

if __name__ == '__main__':
    main()

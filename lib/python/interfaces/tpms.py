"""
This the two TPMS interfaces
Ref. SKCMS-788
"""

import salary.account.common.shell as sh
import carmusr.tracking.util.time_shell as tshell


def main():

    args = sh.get_sys_args()
    print "  optional argument --save found:", args.save
    print "  optional argument --daemon found:", args.daemon

    if not (args.crew or args.roster):

        # TODO: correct this usage instruction
        print """Run with argument:
crew      - Exports crew data
roster    - Exports crew training rosters
--save     - Optional argument.  Without it, only a "dry run" is performed (no commit to DB).
--daemon   - Optional argument. Runs the process without GUI.
             Without it, Tracking studio is opened, all output goes to standard out,
             and the process only exits when studio is closed.

example usages:
    # in a "user", first do:
    bin/cmsshell  # must be in cmsshell

    carmrunner interfaces/tpms.py crew --deamon
    carmrunner interfaces/tpms.py roster --daemon
    carmrunner interfaces/tpms.py crew 
    carmrunner interfaces/tpms.py roster
"""
        return 2

    command = sh.studio_launch_command(args.daemon)
    now = tshell.abstime_now()
    pp_start_month_start = now.month_floor()
    pp_start_month_end = now.month_ceil()

    environment = sh.get_environmnent()
    sh.set_save_and_daemon(environment, args)

    if args.crew:
        sh.set_studio_params(
            environment,
            pp_start_month_start.addmonths(-6),
            pp_start_month_end.addmonths(6),
            "'report_sources.hidden.TPMS;report_sources.hidden.TPMS.TPMSCrewReport()'")
    elif args.roster:
        sh.set_studio_params(
            environment,
            pp_start_month_start.addmonths(-1),
            pp_start_month_end.addmonths(2),
            "'report_sources.hidden.TPMS;report_sources.hidden.TPMS.TPMSRosterReport()'")

    return_code = sh.run_command(command, environment)
    print "return_code: %s" % return_code

    print "####### F0 SCRIPT ENDED #######"
    return 0


if __name__ == '__main__':
    main()

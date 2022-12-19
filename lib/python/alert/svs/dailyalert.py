"""
This is for the daily alert report generation
Ref. SKCMS-3018
"""

import alert.svs.common.shell as sh
import carmusr.tracking.util.time_shell as tshell


def main():
    args = sh.get_sys_args()
    print "  optional argument --save found:", args.save
    print "  optional argument --daemon found:", args.daemon

    if not (args.grant):
        # TODO: correct this usage instruction
        print """Run with argument:
grant      - Exports alert data
--save     - Optional argument.  Without it, only a "dry run" is performed (no commit to DB).
--daemon   - Optional argument. Runs the process without GUI.
             Without it, Tracking studio is opened, all output goes to standard out,
             and the process only exits when studio is closed.

example usages:
    # in a "user", first do:
    bin/cmsshell  # must be in cmsshell

    carmrunner alert/svs/dailyalert.py grant --deamon
"""
        return 2

    command = sh.studio_launch_command(args.daemon)
    now = tshell.abstime_now()
    pp_start_month_start = now.month_floor()
    pp_start_month_end = now.month_ceil()

    environment = sh.get_environmnent()
    sh.set_save_and_daemon(environment, args)

    if args.grant:
        sh.set_studio_params(
            environment,
            pp_start_month_start.addmonths(-2),
            pp_start_month_end.addmonths(2),
            "'report_sources.hidden.DailyAlert;report_sources.hidden.DailyAlert.send_daily_alert()'")

    return_code = sh.run_command(command, environment)
    print "return_code: %s" % return_code

    print "####### DAILY ALERT SCRIPT ENDED #######"
    return 0


if __name__ == '__main__':
    main()

"""
This script is for testing/sumulation different grant/remove/update scripts.

If run directly form terminal, then main() is called.  Main will in turn start a studio, and and open a period
 from 3 months before current year until 1 month into the year following this.

The period can pe specified with start and end date, or simply just start-date.
If just start-date, then that gets rounded down to begining of that month, and end date is 3 months later.
"""

import sys
import salary.account.common.shell as sh
import carmusr.tracking.util.time_shell as tshell


def default_period(start=None):
    """returns 3 months, starting the first of 1 month back"""
    if start:
        start = start.month_floor()
    else:
        start = tshell.abstime_now().month_floor().addmonths(-1)
    end = start.addmonths(3)
    return start, end


def main():
    print sys.argv
    args = sys.argv[1:]
    print args

    if len(args) == 2:
        start, end = (tshell.abstime(args[0]), tshell.abstime(args[1]))
    elif len(args) == 1:
        start, end = default_period(tshell.abstime(args[0]))
    else:
        start, end = default_period()

    start = str(start).split(" ")[0]
    end = str(end).split(" ")[0]

    environment = sh.get_environmnent()
    sh.set_studio_params(
        environment, start, end,
        "'salary.account.tester.tester_studio;salary.account.tester.tester_studio.main()'")
    command = sh.studio_launch_command(False)

    print "  ### "
    print "  #  Starting Tester with period:", start, "-", end
    print "  ### "

    return_code = sh.run_command(command, environment)

    print "  ### "
    print "  # Tester launch ended (%s)" % return_code
    print "  ### "
    return 0


if __name__ == '__main__':
    main()

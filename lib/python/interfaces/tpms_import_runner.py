import salary.account.common.shell as sh
import carmusr.tracking.util.time_shell as tshell


def main():
    args = sh.get_sys_args()
    print "  optional argument --save found:", args.save
    print "  optional argument --daemon found:", args.daemon

    command = sh.studio_launch_command(args.daemon)
    now = tshell.abstime_now()
    pp_start_month_start = now.adddays(0).month_floor()
    pp_start_month_end = now.adddays(0).month_ceil()

    environment = sh.get_environmnent()
    sh.set_save_and_daemon(environment, args)

    py_cmd = 'interfaces.tpms_import;interfaces.tpms_import.run()'

    sh.set_studio_params(
        environment,
        pp_start_month_start,
        pp_start_month_end,
        "'%s'" % py_cmd)

    return_code = sh.run_command(command, environment)
    print "return_code: %s" % return_code

    print "####### F0 SCRIPT ENDED #######"
    return 0


if __name__ == '__main__':
    main()

"""
This module must only be imported from "within cmsshell",
as it loads carmsys-specific modules.
"""

import os
import subprocess
import sys


# constants 
GRANT = "grant"
RESET = "reset"
CORRECT = "correct"
SAVE = "--save"
DAEMON = "--daemon"
CREW = "crew"
ROSTER = "roster"

DO_SAVE = "DO_SAVE"
IS_DAEMON = "IS_DAEMON"

TRUE = "True"
FALSE = "False"


def get_sys_args():
    print "  ## sys.argv:", sys.argv
    return Data(
        grant=GRANT in sys.argv,
        reset=RESET in sys.argv,
        correct=CORRECT in sys.argv,
        save=SAVE in sys.argv,
        daemon=DAEMON in sys.argv,
        crew=CREW in sys.argv,
        roster=ROSTER in sys.argv,
    )


def get_carmusr_path():
    return os.environ['CARMUSR']


def studio_launch_command(is_daemon):
    carmusr_path = get_carmusr_path()
    return [carmusr_path + '/bin/studio.sh', '-S', 't', '-d'] \
        if is_daemon else \
        [carmusr_path + '/bin/studio.sh', '-S', 't']


def get_environmnent():
    return dict(os.environ)


def set_save_and_daemon(environment, args):
        environment[DO_SAVE] = TRUE if args.save else FALSE
        environment[IS_DAEMON] = TRUE if args.daemon else FALSE


def get_save_and_daemon():
    return (
        os.getenv(DO_SAVE, FALSE) == TRUE,
        os.getenv(IS_DAEMON, FALSE) == TRUE, )


def run_command(command, environment):
    proc = subprocess.Popen(command, env=environment)
    return_code = proc.wait()
    return return_code


def set_studio_params(environment, pp_start, pp_end, script_str_str):
        environment["PERIOD_START"] = str(pp_start)[0:9]
        environment["PERIOD_END"] = str(pp_end)[0:9]
        environment["PLANNING_AREA"] = "ALL"
        environment["START_SCRIPT"] = script_str_str


class Data:
    """
A simple container fuction - easier to use and understand than lists
Simply init it with k=v pair, then call them.
Add utiity methods to class if needed.
example:
Data.my_sum = lambda self: self.a + self.b
dat = Data(a=1, b=2)
print "a:",dat.a, " b:" dat.b, " sum:", dat.my_sum()
"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __str__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)


class Sum:
    """a simple object for encapsulating sum."""

    def __init__(self):
        self.__sum = 0

    def add(self, n):
        self.__sum += n

    def get(self):
        return self.__sum



"""
Small tool that makes sure that we run with Carmpython, and that we source
'$CARMUSR/etc/carmenv.sh' first.
"""

import os
import subprocess
import sys
from tempfile import mkstemp


__version__ = '$Revision$'
__all__ = ['run', 'CarmPythonError']


shell_script = """#!/bin/sh
. $CARMUSR/etc/carmenv.sh
$CARMSYS/bin/carmpython ${1+"$@"}
"""


class CarmPythonError(Exception):
    """Cannot even start with 'carmpython', check your installation!"""
    msg = ''
    def __init__(self, msg=''):
        self.msg = msg

    def __str__(self):
        if self.msg:
            return self.msg
        else:
            return self.__doc__


def run():
    """Run the Python code with Carmpython as interpreter."""
    try:
        # BSIRAP is typically not available unless we run carmpython executable.
        import BSIRAP
    except:
        # Probably not running with carmpython
        if sys.executable.startswith('/opt/Carmen'):
            raise CarmPythonError()
        try:
            os.environ['CARMUSR']
        except:
            raise CarmPythonError("Environment CARMUSR must be set.")
        # Create small shell script and re-run the lot, but now with 'carmpython'
        fd, fn = mkstemp(suffix='.sh', prefix='fixrunner_', dir='/tmp', text=True)
        rc = 0
        try:
            f = os.fdopen(fd, 'w')
            f.write(shell_script)
            f.close()
            os.chmod(fn, 0700)
            p = subprocess.Popen(['/bin/sh', fn] + sys.argv)
            pid, status = os.waitpid(p.pid, 0)
            rc = os.WEXITSTATUS(status)
        finally:
            os.unlink(fn)
        sys.exit(rc)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

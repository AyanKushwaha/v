
# [acosta:07/169@15:04] Rewritten pkgPath

"""
Utility to make it easier to run Python scripts together with Mirador.

Usage:

    # In a source file that has to be run in a Studio environment or to be
    # started by Mirador - put the following statements before any imports of
    # Studio/TableManager modules:

    import utils.mdor
    utils.mdor.start(__name__)

    # The rest of the code can remain unchanged, note that the module 'resets'
    # the main module name to be just '__main__' which makes it possible to
    # keep the same layout for Studio / TableManager and command line scripts.

    # e.g.
    from tm import TM, TMC
    ...
    ...
    if __name__ == '__main__':
        # If started from Mirador:
        if utils.mdor.started:
            TM = TMC(connect_string, schema_name)
        ...
        ...

This module tries to findout what was the packagepath of the calling module.
in some cases this will fail (when using 'carmpython').

In those cases use this syntax:
    import utils.mdor
    utils.mdor.start(__name__, 'replication.mymodule')
    # where 'replication.mymodule' is the relative package path to the module.
- or -
    import utils.mdor
    utils.mdor.start(__name__, 'replication/mymodule.py')
"""

import os
import sys
import inspect


# Flag that will be True in case the script was started by Mirador.
started = False


class UsageException(Exception):
    """ User defined exception. """
    msg = ''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)


def start(caller=None, script=None):
    """ To be called from the module that contains __main__. """
    if caller == '__main__':
        if script is None:
            frame = inspect.currentframe()
            try:
                F = inspect.getouterframes(frame)
                # Get calling scripts file name
                script = F[-1][1]
            finally:
                del frame
        try:
            # Check if started from within Studio
            import Cui
        except:
            try:
                mirador = os.path.join(os.environ['CARMSYS'], 'bin', 'mirador')
            except:
                raise UsageException('The environment CARMSYS must be set.')
            args = ['mirador', '-s', pkgPath(script)] + sys.argv[1:]
            rc = os.execvp(mirador, args)
            #return rc >> 8
            sys.exit(rc)
    else:
        # If started from Mirador
        global started
        if not started:
            sys.modules.get(caller).__name__ = '__main__'
        started = True


def pkgPath(script):
    """ Create a relative package path 'pkg1.pkg2.module' from a script name. """
    L = []
    (d, b) = os.path.split(script)
    L.append(b)
    while d:
        if os.path.isfile(os.path.join(d, '__init__.py')):
            # the file __init__.py signals that this is a package.
            (d, b) = os.path.split(d)
            L.append(b)
        else:
            # No __init__.py, assume we are at top level.
            break

    # Join the elements in reverse order
    p = '.'.join(L[::-1])

    # Strip .py extension
    if p.upper().endswith(".PY"):
        p = p[:-3]
    return p


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

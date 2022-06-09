
# [acosta:06/347@11:25] Stolen from Fredrik Lundh.

"""
Some useful routines that can be used for debugging/fault handling.
"""

import os, sys, traceback

__all__ = ['getCause', 'locator']


def locator(o):
    """Return name of the method we are within.
    Typical usage would be:
    def method(self, arg1, arg2):
        print "%s(%s, %s)" % (locator(self), arg1, arg2)

    This removes the risk that a method that changed it's name, would have
    debug printouts that show the old name.
    """
    return "%s.%s.%s" % (o.__class__.__module__, o.__class__.__name__,
            sys._getframe(1).f_code.co_name)


def getCause():
    """
    Print out last line causing the exception.
    """
    try:
        (type, value, tb) = sys.exc_info()
        if tb is None:
            return "No exception on stack."
        info = traceback.extract_tb(tb)
        (filename, lineno, function, text) = info[-1]
        filename = os.path.split(filename)[-1]
        return "%s[%d]: %s: %s (in %s)." % (filename, lineno, type.__name__, str(value), function)
    finally:
        # clean up
        type = value = tb = None


if __name__ == '__main__':
    # Basic test
    try:
        print x[0]
    except:
        print getCause()


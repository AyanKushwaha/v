
# [acosta:06/328@14:11] Some formatting functions

"""
Contains some formatting functions that are useful when writing to
flat file.
"""

__all__ = ['CHR', 'INT', 'DATE', 'NVL']

class CellOverFlowError(ArithmeticError):
    pass

# functions =============================================================={{{1

def hours(reltime):
    """ Return integer representing RelTime expressed as number of hours. """
    if int(NVL(reltime)) == 0:
        return 0
    (hhh, mm) = reltime.split()
    return hhh + int(round(mm / 60))


def minutes(reltime):
    """ Return integer representing RelTime expressed as number of minutes. """
    if int(NVL(reltime)) == 0:
        return 0
    (hhh, mm) = reltime.split()
    return (60 * hhh) + mm


def NVL(x, default=0):
    """ Same as Oracle's NVL macro. Return default value if x is None. """
    if x is None:
        return default
    return x


# CHR --------------------------------------------------------------------{{{2
def CHR(c, string):
    """
    Return a ' '-padded left-adjusted string of width c
    """
    if string is None:
        return c * ' '
    else:
        try:
            return "%-*.*s" % (c, c, str(string))
        except:
            return c * ' '


# DATE -------------------------------------------------------------------{{{2
def DATE(date, iso=False):
    """
    Return date in form YYYYMMDD. Input date is AbsTime() instance.
    The iso flag decides the output format, 2006-10-20 or 20061020.
    """
    from AbsTime import AbsTime
    if isinstance(date, AbsTime):
        if iso:
            return "%04d-%02d-%02d" % date.split()[:3]
        else:
            return "%04d%02d%02d" % date.split()[:3]
    else:
        if iso:
            return '0000-00-00'
        else:
            return 8 * '0'


# INT --------------------------------------------------------------------{{{2
def INT(c, number):
    """
    Return a '0'-padded right-adjusted string of width c
    """
    if number is None:
        return c * '0'
    else:
        try:
            s = "%0*d" % (c, int(number))
            if len(s) > c:
                raise CellOverFlowError("Value '%d' too large to fit in cell of width '%s'." % (int(number), c))
            return s[:c]
        except CellOverFlowError, e:
            raise
        except:
            # The string 'number' could not be expressed as a number
            return c * '0'


# main ==================================================================={{{1
# for basic tests only
if __name__ == '__main__':
    import unittest
    unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromName('utils.test_utils.Test_fmt'))


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

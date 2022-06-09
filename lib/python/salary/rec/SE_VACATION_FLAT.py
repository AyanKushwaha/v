
# [acosta:07/092@12:59] For vacation lists.

"""
Swedish salary system (PALS).
Flat file format, for vacation lists.
"""

from salary.fmt import PALS2

# For description of record format see ../fmt.py

class SE_VACATION_FLAT(PALS2):
    """ Record definition for Vacation lists STO. """
    def __init__(self, rf, buntid='9097'):
        now = "%04d%02d%02d" % rf.rundata.starttime.split()[:3]
        rf.name = rf.getNextFileName('VAC-SE-%s' % (now))
        self.buntid = buntid

    def record(self, extperkey, type, start, end):
        # Note the number of arguments!
        self.empno = extperkey
        self.type = type
        self.startdate = start
        self.enddate = end
        return str(self)


# EOF

"""
New Swedish salary system.
Comma Separated Values (CSV) format.
"""


from salary.fmt import CSVFormatter


class S3_CSV(CSVFormatter):
    def __init__(self, runfiles):
        self.rundata = runfiles.rundata

    def pre(self):
        if self.rundata.runtype == 'ALLOWNCE_D':
            return "'day','crew','article','units'"
        else:
            return "'crew','article','units'"

    def record(self, extperkey, extartid, amount):
        # amount is an (offset, amount) tuple in the daily allowances run type
        if self.rundata.runtype == 'ALLOWNCE_D':
            result = ''
            # that int(str(...)) below is used to get rid of leading zeros
            for (offset, a) in amount:
                result += '%d,%s,%s,%.2f\n' % (int(str(self.rundata.firstdate.adddays(offset))[:2]), extperkey, extartid, a / 100.0)
            return result[:-1]
        else:
            return '%s,%s,%.2f' % (extperkey, extartid, amount / 100.0)

# EOF

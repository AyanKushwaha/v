

"""
44.6.2 Vacation lists OSL

NOTE: this format differs from the SAP formats used otherwise.
"""

from salary.fmt import SAP, SAPVacationRecordMaker, utils

class NO_VACATION_FLAT(SAP):

    def record(self, extperkey, type, start, end):
        self.numberOfRecords += 1
        self._rec = SAPVacationRecordMaker()
        return str(self._rec(
            RECTP=1,
            BEGDA=start,
            ENDDA=utils.last_date(end),
            PERNR=extperkey,
            LGART=type,
            ANZHL=utils.days(start, end)))

# EOF

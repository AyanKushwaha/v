# -*- coding: latin-1 -*-

"""
New Swedish salary system.
Flat file format.
"""

from salary.fmt import SAP, SAPScheduleRecordMaker, SAPAbsenceRecordMaker, SAPTcScheduleRecordMaker, SAPAllScheduleRecordMaker, utils
from tm import TM
from salary.api import getAllArticleIds
from operator import itemgetter

class S3_FLAT(SAP):
    """ Utilizes common SAP format """

    def _retirement_date(self, rundata, extperkey, extartid):
        # this should work as long as (extsys, extperkey) is unique
        salary_run = TM.table('salary_run_id')[(rundata.runid,)]
        crew = TM.table('salary_basic_data')[(salary_run, extperkey, extartid,)].crewid
        return TM.table('crew')[(crew.id,)].retirementdate

    def record(self, extperkey, extartid, amount):
        if self.rd.runtype == "PERDIEM":
            self.numberOfRecords += 1
            rec = self._rec(
                RECTP=1,
                BEGDA=self.rd.firstdate,
                ENDDA=utils.last_date(self.rd.lastdate),
                PERNR=extperkey,
                LGART=extartid,
                WAERS=self.waers,
                KOSTL=self.kostl,
                BETRG=-amount if extartid in getAllArticleIds('MEAL', self.rd.extsys, \
                    self.rd.firstdate, self.rd.lastdate) else amount)
            return str(rec)

        if self.rd.runtype == "ALLOWNCE_D":
            res = ''
            for (offset, a) in amount:
                self.numberOfRecords += 1
                rec = self._rec(
                    RECTP=1,
                    BEGDA=self.rd.firstdate.adddays(offset),
                    ENDDA=self.rd.firstdate.adddays(offset),
                    PERNR=extperkey,
                    LGART=extartid,
                    ANZHL=a)
                res += str(rec) + '\n'
            return res[:-1]

        if self.rd.runtype == "ALLOWNCE_M":
            self.numberOfRecords += 1
            retirement_date = self._retirement_date(self.rd, extperkey, extartid)
            rec = self._rec(
                RECTP=1,
                BEGDA=self.rd.firstdate,
                # This is specifically for CALM_OTFC and CALW - the Swedish salary office wants
                # them to be reported on a retirement date if one is present in a calculation period.
                ENDDA=retirement_date if extartid in \
                    getAllArticleIds('CALM_OTFC', self.rd.extsys, self.rd.firstdate, self.rd.lastdate) + \
                    getAllArticleIds('CALW', self.rd.extsys, self.rd.firstdate, self.rd.lastdate) \
                    and retirement_date \
                    and retirement_date >= self.rd.firstdate \
                    and retirement_date <= self.rd.lastdate \
                    else utils.last_date(self.rd.lastdate),
                PERNR=extperkey,
                LGART=extartid,
                ANZHL=amount)
            return str(rec)

        elif self.rd.runtype == "SCHEDULE":

            self._rec = SAPScheduleRecordMaker()
            res = ""
            for (offset, a) in  amount:
                res += str(self._rec( PERNR=extperkey, DATE=self.rd.firstdate.adddays(offset))) + "\n"
                self.numberOfRecords += 1

            return res[:-1]

        elif self.rd.runtype == "TCSCHEDULE":

            self._rec = SAPTcScheduleRecordMaker()
            res = ""
            for (offset, a) in  amount:
                part = a % 100
                hhmm = int(round((a - part) + part * 0.6))
                res += str(self._rec(PERNR=extperkey, DATE=self.rd.firstdate.adddays(offset), ENDTIME=hhmm)) + "\n"
                self.numberOfRecords += 1

            return res[:-1]

        elif self.rd.runtype == "SCHED_CCSE":

            self._rec = SAPAllScheduleRecordMaker()
            res = ""

            for (offset, a) in  amount:
                part = a % 100
                hhmm = int(round((a - part) + part * 0.6))
                res += str(self._rec(PERNR=extperkey, DATE=self.rd.firstdate.adddays(offset), ENDTIME=hhmm)) + "\n"
                self.numberOfRecords += 1

            return res[:-1]

        elif self.rd.runtype == "ABSENCE":
            print '12455: S3_FLAT.record: extperkey = %s, extartid = %s, amount = %s' % (str(extperkey), str(extartid), str(amount))

            self._rec = SAPAbsenceRecordMaker()

            sorted_amounts = sorted(amount, key=itemgetter(0))
            (period_start, a) = sorted_amounts[0]
            prev_offset = period_start
            print '12455: S3_FLAT.record: prev_offset = period_start = %s' % (str(prev_offset))
            period_len = 1
            res = ""
            for (offset, a) in sorted_amounts[1:]:
                print '12455: S3_FLAT.record: iterating over amount: offset = %s, a = %s' % (str(offset), str(a))
                if(offset - prev_offset) != 1:
                    # New period starting
                    begin_date = self.rd.firstdate.adddays(period_start)
                    end_date = self.rd.firstdate.adddays(period_start + period_len - 1)
                    if end_date >= self.rd.lastdate or end_date < self.rd.firstdate or begin_date >= self.rd.lastdate or begin_date < self.rd.firstdate:
                        raise Exception("ERROR: %s-%s outside %s-%s" % (begin_date, end_date, self.rd.firstdate, self.rd.lastdate))
                    elif end_date < begin_date:
                        raise Exception("ERROR: inv. period %s-%s" % (begin_date, end_date))
                    print '12455: S3_FLAT.record: offset > prev_offset + 1, so we write an interval: %s' % (str(self._rec(RECTP=1, BEGDA=begin_date, ENDDA=end_date, PERNR=extperkey, LGART=extartid)))
                    res += str(self._rec(RECTP=1,
                                         BEGDA=begin_date,
                                         ENDDA=end_date,
                                         PERNR=extperkey,
                                         LGART=extartid)) + "\n"
                    self.numberOfRecords += 1
                    period_len = 1
                    period_start = offset
                    print '12455: S3_FLAT.record: period_len = %s, period_start = %s' % (str(period_len), str(period_start))
                else:

                    period_len += 1
                    print '12455: S3_FLAT.record: period_len = %s' % (str(period_len))

                prev_offset = offset
                print '12455: S3_FLAT.record: prev_offset = offset = %s' % (str(prev_offset))

            # Record for last period
            begin_date = self.rd.firstdate.adddays(period_start)
            end_date = self.rd.firstdate.adddays(period_start + period_len - 1)
            if end_date >= self.rd.lastdate or end_date < self.rd.firstdate or begin_date >= self.rd.lastdate or begin_date < self.rd.firstdate:
                raise Exception("ERROR: %s-%s outside %s-%s" % (begin_date, end_date, self.rd.firstdate, self.rd.lastdate))
            elif end_date < begin_date:
                raise Exception("ERROR: inv. period %s-%s" % (begin_date, end_date))
            print '12455: S3_FLAT.record: writing the last interval: %s' % (str(self._rec(RECTP=1, BEGDA=begin_date, ENDDA=end_date, PERNR=extperkey, LGART=extartid, ANZHL=period_len)))
            res += str(self._rec(RECTP=1,
                                 BEGDA=begin_date,
                                 ENDDA=end_date,
                                 PERNR=extperkey,
                                 LGART=extartid,
                                 ANZHL=period_len))
            self.numberOfRecords += 1

            return res
        else:
            return super(S3_FLAT, self).record(extperkey, extartid, amount)
# EOF

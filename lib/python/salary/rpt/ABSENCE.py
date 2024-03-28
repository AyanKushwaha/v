"""
Absence transactions
Testing
"""

from salary.rpt import EmailReport
import salary.api as api


class S2(EmailReport):
    pass


class S3(EmailReport):

    def __init__(self, rd):
        dict.__init__(self)
        self.rundata = rd
        records = api.getDailyRecordsFor(rd.runid)
        # repacking the dictionary
        for extperkey in records:
            for extartid in records[extperkey]:
                prev_offset = -2
                for offset, amount in sorted(records[extperkey][extartid], key=lambda x: x[0]): # sorted by offset
                    if offset - prev_offset > 1:
                        if not extartid in self.keys():
                            self[extartid] = 1
                        else:
                            self[extartid] += 1
                    prev_offset = offset


    def report(self):
        date = "%04d-%02d" % self.rundata.firstdate.split()[:2]
        region = self.rundata.extsys
        L = [
            'Subject: %s %s %s' % (date, self.subject, self.rundata.runtype),
            ''
            ]
        L.append('Periode: %s' % date)
        L.append('Region:  %s' % (region,))
        L.append('Run-id:  %s' % (self.rundata.runid,))
        L.append('')
        L.append('               Number of   Sum')
        L.append('               Records')
        t_count = 0
        for artid in sorted(self):
            count = self[artid]
            t_count += count
            L.append('Lonart : %-6s %8s' % (artid, count))
        L.append('')
        L.append('TOTAL           %8s' % (t_count))
        L.append('')
        L.append('UNDERSKRIFT OG DATO FOR GODKENDELSE: ' + 20 * '.') 
        return '\n'.join(L)

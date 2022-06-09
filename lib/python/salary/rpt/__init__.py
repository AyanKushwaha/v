

"""
Package salary.rpt, common functions
"""

import salary.conf as conf
import salary.api as api
from salary.run import GenericReport


class EmailReport(GenericReport):
    """
    This report (for delivery of jobstatus by email) was put here because
    it is used as-is by all of the different run types (AMBI, OVERTIME, ...)
    """
    subject = 'Afstemningsunderlag'

    def __init__(self, rd):
        GenericReport.__init__(self, rd)

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
        t_sum = 0
        for artid in sorted(self):
            count, sum = self[artid]
            t_count += count
            t_sum += sum
            L.append('Lonart : %-6s %8s %14.2f' % (artid, count, sum / 100.0))
        L.append('')
        L.append('TOTAL           %8s %14.2f' % (t_count, t_sum / 100.0))
        L.append('')
        L.append('UNDERSKRIFT OG DATO FOR GODKENDELSE: ' + 20 * '.') 
        return '\n'.join(L)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

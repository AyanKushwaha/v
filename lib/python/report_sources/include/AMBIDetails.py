

"""
Test report to verify the AMBI interface.
"""

import carmensystems.publisher.api as prt

from report_sources.include.SASReport import SASReport
from utils.rave import RaveIterator, MiniEval

def B(*a, **k):
    """Bold text."""
    k['font'] = prt.Font(weight=prt.BOLD)
    return prt.Text(*a, **k)

class Report(SASReport):

    def create(self):
        SASReport.create(self, 'AMBI Details')

        plan = MiniEval({'ambi_norm': 'ambi.%ambi_norm_p%'}).eval('default_context')
        self.add('AMBI norm: %s' % plan.ambi_norm)

        ri = RaveIterator(RaveIterator.iter('iterators.roster_set'), {
            'id': 'crew.%id%',
            'empno': 'crew.%employee_number%',
            'logname': 'crew.%login_name%',
            'rank': 'crew.%rank%',
        })

        li = RaveIterator(RaveIterator.iter('iterators.leg_set'), {
            'id': 'leg.%flight_id%',
            'dutycd': 'duty_code.%leg_code%',
            'st': 'leg.%start_lt%',
            'et': 'leg.%end_lt%',
            'st_utc': 'ambi.%leg_start%',
            'et_utc': 'ambi.%leg_end%',
            'acreg': 'leg.%ac_reg%',
            'adep': 'leg.%start_station%',
            'ades': 'leg.%end_station%',
            'ambi': 'ambi.%leg_ambi_time%',
            'ambi_f': 'ambi.%leg_ambi_oy_time%',
            'ambi_s': 'ambi.%leg_ambi_sby_time%',
            'ambi_g': 'ambi.%leg_ambi_gd_time%',
            'in_dnk': 'ambi.%activity_in_denmark%',
            'corr': 'ambi.%correction%',
            })

        ri.link(li)
        rosters = ri.eval('default_context')
        header_items = ('DC', 'ID', 'A/C Reg', 'ST', 'ADEP', 'ADES', 'ET',
            'Duration', 'In DNK?', 'Corr', 'AMBI F', 'AMBI S', 'AMBI G', 'AMBI')

        #header = self.getDefaultHeader()
        #header.add(prt.Row(*[B(x) for x in header_items]))
        #self.setHeader(header)

        first = True
        for crew in rosters:
            if not first:
                self.newpage()
            first = False

            self.add(prt.Row(height=16))
            self.add(prt.Isolate(prt.Row(B('%s(%s) %-3.3s %s' % (crew.empno,
                crew.id, crew.rank, crew.logname)))))
            self.add(prt.Row(height=16))
            self.add(prt.Row(*[B(x) for x in header_items]))

            for leg in crew:
                self.add(prt.Row(
                    leg.dutycd,
                    leg.id,
                    no_void(leg.acreg),
                    leg.st_utc,
                    leg.adep,
                    leg.ades,
                    leg.et_utc,
                    no_empty(leg.et_utc - leg.st_utc),
                    ('', 'Y')[leg.in_dnk],
                    no_empty(leg.corr),
                    no_empty(leg.ambi_f),
                    no_empty(leg.ambi_s),
                    no_empty(leg.ambi_g),
                    no_empty(leg.ambi)))
                self.page()


def no_empty(rt):
    try:
        if int(rt) == 0:
            return ''
        else:
            return prt.Text(str(rt), align=prt.RIGHT)
    except:
        return '?'

def no_void(value):
    if value is None:
        return ''
    return value



# [acosta:08/330@15:46] Created

"""
Report with published changes of rosters.

INFORMED -> LATEST
"""

import Cui
import cio.rv as rv
import carmensystems.rave.api as rave
import carmensystems.publisher.api as prt

from report_sources.include.SASReport import SASReport
from report_sources.hidden.CIOReport import CIOReport, H2, RowSpacer


from_state = rv.TRACKING_INFORMED_TYPE
to_state = None


# Report ================================================================={{{1
class Report(CIOReport):
    use_utc = True

    def create(self):
        self.crewid, = rave.eval(rave.selected(rave.Level.chain()), 'crew.%id%')
        self.r = rv.EvalRoster(self.crewid)
        SASReport.create(self, 'Roster Changes (Latest)', showPlanData=False)
        self.add(RowSpacer())
        self.add(prt.Isolate(prt.Column(
            prt.Row(
                prt.Column(H2(self.r.extperkey)),
                prt.Column(H2(self.r.logname),
            width=int(0.8 * self.pageWidth))))))
        self.revised_schedule(from_state, to_state)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

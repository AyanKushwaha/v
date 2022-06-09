'''
Alertness Distribution Report
'''

from carmusr.fatigue.report import AlertnessDistributionReport
from carmensystems.studio import cpmbuffer
from carmensystems.studio import cuibuffer
import carmensystems.rave.api as rave
import Cui

class Report(AlertnessDistributionReport):
    def get_bag(self):
        win_buf = cuibuffer.CuiBuffer(Cui.CuiWhichArea, cuibuffer.WindowScope)
        self._buf = cpmbuffer.CpmBuffer(win_buf, 'marked')
        return rave.buffer2context(self._buf).bag()


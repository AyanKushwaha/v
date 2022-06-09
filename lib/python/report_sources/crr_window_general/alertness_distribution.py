'''
Alertness Distribution Report
'''
from carmensystems.studio import cpmbuffer
from carmensystems.studio import cuibuffer
import carmensystems.rave.api as rave
import Cui
from carmusr.fatigue.report import AlertnessDistributionReport

class Report(AlertnessDistributionReport):
    def get_bag(self):
        self._buf = cuibuffer.CuiBuffer(Cui.CuiWhichArea, cuibuffer.WindowScope)
        return rave.buffer2context(self._buf).bag()


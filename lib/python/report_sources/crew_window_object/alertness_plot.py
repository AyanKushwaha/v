"""
Alertness plot report
"""
import Cui
import carmensystems.rave.api as rave
from carmensystems.studio import cuibuffer
from carmusr.fatigue.report import AlertnessPlotReport

class Report(AlertnessPlotReport):
    def get_set(self):
        self._buf = cuibuffer.CuiBuffer(Cui.CuiWhichArea, cuibuffer.MarkedLeftScope)
        return rave.buffer2context(self._buf).bag().iterators.chain_set()

    def get_plot_interval(self, bag):
        start = bag.fundamental.pp_start()
        end = bag.fundamental.pp_end()
        return (start,end)

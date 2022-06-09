"""
Alertness plot report
"""
import Cui
import carmensystems.rave.api as rave
from carmensystems.studio import cuibuffer
from carmusr.fatigue.report import AlertnessPlotReport

class Report(AlertnessPlotReport):
    def get_set(self):
        self._buf = cuibuffer.CuiBuffer(Cui.CuiWhichArea, cuibuffer.MarkedScope)
        return rave.buffer2context(self._buf).bag().iterators.trip_set()

    def get_plot_interval(self, bag):
        start = bag.report_fatigue.trip_interval_start()
        end = bag.report_fatigue.trip_interval_end()
        return (start,end)


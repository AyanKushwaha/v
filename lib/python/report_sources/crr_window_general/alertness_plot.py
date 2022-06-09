"""
Alertness plot report
"""
import Cui
import carmensystems.rave.api as rave
from carmensystems.studio import cuibuffer
from carmusr.fatigue.report import AlertnessPlotReport

class Report(AlertnessPlotReport):
    def get_set(self):
        self._buf = cuibuffer.CuiBuffer(Cui.CuiWhichArea, cuibuffer.WindowScope)
        return rave.buffer2context(self._buf).bag().chain_set()
    
    def ignore_bag(self, bag):
        return not bag.report_fatigue.contains_legs_in_pp()
    
    def get_plot_interval(self, bag):
        start = bag.report_fatigue.chain_interval_start()
        end = bag.report_fatigue.chain_interval_end()
        return (start, end)
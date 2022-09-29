#
# Pie Charts
#

from __future__ import division
from __future__ import absolute_import
import carmensystems.publisher.api as prt

from carmusr.calibration.mappings import DrawExt
from carmusr.calibration.mappings import studio_palette as sp


class PieMember(object):

    def __init__(self, label, value, **kw):
        self.label = label
        self.value = value
        self.kw = kw

    def get_common_tooltip_txt(self, tot):
            txt = "%s (%0.1f%%)" % (self.value, 100 * self.value / tot) if int(self.value) else "-"
            return "%s: %s" % (self.label, txt)


class PieChart(prt.Canvas):
    """
    A sub class of Canvas for drawing pie charts.
    """

    min_percent = 1.2

    def __init__(self, width, height, members, tooltip_header="", tooltip_footer="", *args, **kw):

        self.members = members
        self.tooltip_header = tooltip_header
        self.tooltip_footer = tooltip_footer
        prt.Canvas.__init__(self, width, height, *args, **kw)

    def draw_value(self, tot, value):
        if not value:
            return value
        return max(value, tot * self.min_percent / 100)

    def draw(self, gc):
        gc.coordinates(-1000, -1000, 1000, 1000)
        de = DrawExt(self, gc)
        data_type = type(self.members[0].value)
        tot = sum((m.value for m in self.members), data_type(0))
        common_tooltip_text = "\n".join(m.get_common_tooltip_txt(tot) for m in self.members)
        for m in self.members:
            m._tooltip = "%s%s\n\n%s%s" % (self.tooltip_header, m.label, common_tooltip_text, self.tooltip_footer)

        acc = 0
        for mem in self.members:
            mem._acc = acc
            # RelTime needs to be int to be convertible to float in circle_arc
            mem._draw_value = int(self.draw_value(tot, mem.value))
            acc += mem._draw_value

        rad = min(de.cx2p(1000.0), de.cy2p(1000.0))
        for mem in sorted(self.members, key=lambda it: it.value, reverse=True):  # Order matters for tooltip and action,
            if not int(mem.value):
                continue
            if mem.value == tot:
                de.circle(0, 0, rad, colour=sp.Black, tooltip=mem._tooltip, **mem.kw)
            else:
                de.circle_arc(0,
                              0,
                              rad,
                              360 * mem._acc / acc,
                              360 * (mem._acc + mem._draw_value) / acc,
                              True,
                              colour=sp.Black,
                              tooltip=mem._tooltip,
                              **mem.kw)

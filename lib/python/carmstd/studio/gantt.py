import carmensystems.publisher.api as p
from carmensystems.basics.abstime import AbsTime
from carmensystems.basics.reltime import RelTime
import datetoolkit as dt
from copy import copy


def get_bar_width(date):
    """
    Return the width of the bar. it is doubled for Mondays.
    @param date: AbsTime.
    """
    if date.time_of_week()/RelTime("24:00") == 0:
        return 2
    return 1


class Gantt(p.Canvas):
    """
    Kind of abstract class to derive from. It represents
    a Gantt. The bars for the days are drawn.
    The child class must have a draw method.
    """
    def __init__(self,start_day,end_day,width,height,**kw):
        p.Canvas.__init__(self, width, height, **kw)
        self.start_day = start_day
        self.end_day   = end_day
        # self.set(align=p.RIGHT)

    def draw(self,gc):
        """
        Has to be called in the draw method of the child class.
        """
        x0,y0,x1,y1 = gc.get_coordinates()
        gc.coordinates(self.start_day, y0, self.end_day, y1)
        self._draw_bars(gc, y0, y1)

    def _draw_bars(self,gc,y0,y1):
        """
        draw the bars of the gantt.
        the get_bar_width function is called to determine the width of the bars.
        """
        for day in dt.day_range(self.start_day.day_floor(), self.end_day.day_ceil()):
            gc.path([(day,y0), (day,y1)], width = get_bar_width(day))

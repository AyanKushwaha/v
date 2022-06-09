#
# This file has been copied from NiceToHaveIQ by 'ADM/copy_from_nth'.
# In NiceToHaveIQ the file is found as 'lib/python/nth/studio/prt/canvas_draw_ext.py'.
# Please do not change the file. Copy new versions from NiceToHaveIQ instead.
#
# File: <NiceToHaveIQ>/lib/python/nth/studio/prt/canvas_draw_ext.py
"""
The class DrawExt to simplify usage of Canvas.
"""

#
# Put it in your CARMUSR as:
# "CARMUSR/lib/python/report_sources/include/canvas_draw_ext.py"
#
#
# Created by Stefan Hammar in Nov 2006
# Added circle_arc in June 2007. Stefan Hammar.
#

import math


class DrawExt(object):

    def __init__(self, canvas, gc):
        self.gc = gc  # The coordinates of gc may change.
        self.size = canvas.size()

    #
    # Methods for distance and coordinate transformation.
    #

    def m2p(m):
        """ Convert mm to points """
        return m * 72 / 25.4
    m2p = staticmethod(m2p)

    def p2m(p):
        """ Convert points to mm """
        return p * 25.4 / 72
    p2m = staticmethod(p2m)

    def cty(self):
        """Total range of Y coordinates"""
        c = self.gc.get_coordinates()
        return c[3] - c[1]

    def ctx(self):
        """Total range of X coordinates"""
        c = self.gc.get_coordinates()
        return c[2] - c[0]

    def p2cx(self, x):
        """Convert points to X coordinates"""
        return 1.0 * x * self.ctx() / self.size[0]

    def p2cy(self, y):
        """Convert points to Y coordinates"""
        return 1.0 * y * self.cty() / self.size[1]

    def cx2p(self, x):
        """Convert X coordinates to points"""
        return 1.0 * x * self.size[0] / self.ctx()

    def cy2p(self, y):
        """Convert Y coordinates to points"""
        return 1.0 * y * self.size[1] / self.cty()

    def pos_p2cx(self, p):
        """
        The x coordinate for a position in the original coordinate system.
        Negative value goes from the right.
        """
        if abs(p) > self.size[0]:
            raise ValueError("argument bigger than width of Canvas")
        if p < 0:
            p = self.size[0] + p
        return self.gc.get_coordinates()[0] + self.p2cx(p)

    def pos_p2cy(self, p):
        """
        The x coordinate for a position in the original coordinate system.
        Negative value goes from the top.
        """
        if abs(p) > self.size[1]:
            raise ValueError("argument bigger than height of Canvas")
        if p < 0:
            p = self.size[1] + p
        return self.gc.get_coordinates()[1] + self.p2cy(p)

    # Combinations

    def m2cy(self, m):
        return self.p2cy(self.m2p(m))

    def m2cx(self, m):
        return self.p2cx(self.m2p(m))

    def cx2m(self, x):
        return self.p2m(self.cx2p(x))

    def cy2m(self, y):
        return self.p2m(self.cy2p(y))

    def cy2cx(self, y):
        return self.p2cx(self.cy2p(y))

    def cx2cy(self, x):
        return self.p2cy(self.cx2p(x))

    def pos_m2cx(self, m):
        return self.pos_p2cx(self.m2p(m))

    def pos_m2cy(self, m):
        return self.pos_p2cy(self.m2p(m))

    #
    # Methods for drawing
    #

    def circle(self, pos_x, pos_y, radius, segments=None, **kw):
        """
        Draw a circle in a Canvas.

        Parameters
          pos      : The center of the circle (in coordinates)
          radius   : In points.
          segments : The amount of lines to use in the path.
                     None sets a reasonable number of segments.
          **kw     : Additional named arguments to "gc.path".
        """
        kw["close"] = True
        kw["lines360"] = segments
        self.circle_arc(pos_x, pos_y, radius, 0, 360, **kw)

    def circle_arc(self, pos_x, pos_y, radius, fr, to, segment=False, lines360=None, **kw):
        """
        Draw a circle arc or a circle segment in a Canvas.

        Parameters
          pos      : The center of the circle (in coordinates).
          radius   : In points.
          fr       : Start angle (0-360).
          to       : End angle (0-360).
          segment  : If true a circle segment. If false only a circle arc.
          lines360 : The amount of lines to use in the path for a full circle.
                     None sets a reasonable number.
          **kw     : Additional named arguments to "gc.path".
        """
        if not lines360:
            lines360 = max(50, radius / 2)
        if segment:
            kw["close"] = True  # To get the entire area "click able"
        xrad = self.p2cx(radius)
        yrad = self.p2cy(radius)
        s = 2 * math.pi * fr / 360
        d = 2 * math.pi * (to - fr) / 360
        lines = max(2, int(lines360 * (to - fr) / 360))
        points = [(pos_x + xrad * math.sin(s + d * ix / lines),
                   pos_y + yrad * math.cos(s + d * ix / lines)) for ix in range(lines + 1)]

        if segment:
            points.append((pos_x, pos_y))
            points.insert(0, (pos_x, pos_y))

        self.gc.path(points, **kw)

    def square(self, pos_x, pos_y, edge, **kw):
        """
        Draw a square in a Canvas.

        Parameters
           pos_x : X pos in the coordinate system.
           pos_y : Y pos in the coordinate system.
           edge  : Length (in points)
           **kw  : Additional named arguments to "gc.rectangle"
           """
        self.gc.rectangle(pos_x, pos_y, self.p2cx(edge), self.p2cy(edge), **kw)

    def plot(self, x0, y0, x_width, add_x_pp, func, nlspp=2, **kw):
        """
        Let you plot an f(x) curve.
        x always starts with 0 and is increased with "add_x_pp"
        per point.

        Parameters:
           x0,y0           : Start point in the coordinate system.
           x_width         : Distance to the end of the plot (in points)
           add_x_pp        : Increase x in func(x) call this much per point
           func            : The plot function (return points)
           nlspp           : The number of line segments per point in x.
           **kw            : Additional named arguments to gc.path.
        """
        num_plot_points_f = x_width * nlspp
        num_plot_points = int(num_plot_points_f)
        nlspp -= (num_plot_points_f - num_plot_points) / num_plot_points
        segm_width = self.p2cx(1.0) / nlspp
        x_arg_step = 1.0 * add_x_pp / nlspp

        ll = [[]]
        for step in range(num_plot_points + 1):
            f = self.p2cy(func(x_arg_step * step))
            if f:
                ll[-1].append((x0 + step * segm_width,
                               y0 + f))

            else:
                if len(ll[-1]):
                    ll.append([])

        for l in ll:
            if len(l) > 1:
                self.gc.path(l, **kw)

    def canvas_border(self, dist=0, **kw):
        """
        Draw a border around a Canvas.

        Arguments:
          dist : Distance to the edge in points.
          **kw : Additional arguments to "gc.path".

        """
        self.gc.path([(self.pos_p2cx(dist), self.pos_p2cy(dist)),
                      (self.pos_p2cx(self.size[0] - dist), self.pos_p2cy(dist)),
                      (self.pos_p2cx(self.size[0] - dist), self.pos_p2cy(self.size[1] - dist)),
                      (self.pos_p2cx(dist), self.pos_p2cy(self.size[1] - dist))],
                     close=True,
                     **kw)

####################################
# Self testing code
####################################

import carmensystems.publisher.api as p

try:
    from nth.studio.prt.studiopalette import studio_palette  # @UnusedImport @UnresolvedImport
except (NameError, ImportError):
    from report_sources.include.studiopalette import studio_palette  # @Reimport @UnresolvedImport

sp = studio_palette


class _TestDrawExt(p.Canvas):

    def draw(self, gc):
        maxx = 4000
        maxy = 2000
        gc.coordinates(0, 0, maxx, maxy)
        de = DrawExt(self, gc)

        de.canvas_border(colour=sp.BrightRed)
        de.canvas_border(dist=3, colour=sp.BrightBlue)

        #
        # coordinate information
        #
        gc.text(de.m2cx(3),
                maxy - de.m2cy(3),
                "x: 0 .. %s,   y: 0 .. %s" % (maxx, maxy),
                colour=sp.Grey
                )

        #
        # test circle
        #
        de.circle(800, 1500, 30)
        gc.text(800, 1500, "r=30pt", valign=p.CENTER, align=p.CENTER)

        de.circle(1000, 250, de.cx2p(200), colour=sp.Red, width=3.0)
        gc.text(1000 + 200 + de.m2cx(1.5),
                250, "r=200 x",
                valign=p.CENTER,
                colour=sp.Red)

        de.circle(2500, 450, de.cy2p(200), colour=sp.Blue, width=3.0)
        gc.text(2500 + de.cy2cx(200) + de.m2cx(1.5),
                450, "r=200 y",
                valign=p.CENTER,
                colour=sp.Blue)

        #
        # test circle segment
        #

        de.circle_arc(2750, 1700, 30, 0, 30, True, fill=sp.BrightGreen)
        de.circle_arc(2750, 1700, 30, 30, 100, True, fill=sp.DarkGreen)
        de.circle_arc(2750, 1700, 30, 100, 360, True, fill=sp.LightGreen)

        #
        # test circle arcs
        #

        de.circle_arc(3400, 1000, 15, 0, 30, colour=sp.BrightGreen, width=2)
        de.circle_arc(3400, 1000, 15, 30, 100, colour=sp.DarkGreen, width=2)
        de.circle_arc(3400, 1000, 15, 100, 360, colour=sp.LightGreen, width=2)

        de.circle_arc(3400, 700, 10, 0, 180, fill=sp.BrightRed)

        #
        # test square
        #
        gc.text(1500 + de.m2cx(1.5),
                1000,
                "Square 3 mm",
                align=p.LEFT,
                valign=p.CENTER,
                )
        de.square(1500,
                  1000,
                  de.m2p(3),
                  fill=sp.Red,
                  align=p.RIGHT,
                  valign=p.CENTER,
                  )

        #
        # 1 cm long lines
        #
        gc.path([(800, 800),
                 p.Move(de.m2cx(10), 0)])
        gc.path([(800, 800),
                 p.Move(0, de.p2cy(de.m2p(10)))])
        gc.text(800 + de.m2cx(5), 800 + de.m2cy(5),
                "1 cm",
                valign=p.CENTER,
                align=p.CENTER)

        #
        # 2 cm long sin plot
        #
        de.plot(2500, 1300, de.m2p(20), math.pi * 2 / de.m2p(5),
                lambda x: math.sin(x) * de.m2p(5))
        gc.path([(2500, 1300),
                 p.Move(de.m2cx(20), 0)],
                colour=sp.Red)


class Report(p.Report):

    def create(self):
        self.add('Test of the report: ' + __name__)
        self.add(_TestDrawExt(300, 400))

if __name__ == "__main__":
    import nth.studio.report_generation as rg  # @UnresolvedImport
    rg.reload_and_display_report()

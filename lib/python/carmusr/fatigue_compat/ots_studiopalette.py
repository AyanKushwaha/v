#
# This file has been copied from NiceToHaveIQ by 'ADM/copy_from_nth'.
# In NiceToHaveIQ the file is found as 'lib/python/nth/studio/prt/studiopalette.py'.
# Please do not change the file. Copy new versions from NiceToHaveIQ instead.
#
# File: <NiceToHaveIQ>/lib/python/nth/studio/prt/studiopalette.py
"""
This module provides one attribute, "studio_palette", which is
an instance of the class "carmensystems.publisher.api.ColourPalette".
It contains the following colours:

1. Colours in Studio's palette.
2. All colour values you can use for Rudobs in Rave.
3. A few other commonly used colours:
   JeppesenBlue, JeppesenLightBlue, ReportBlue and ReportLightBlue

START TO USE:
Put a copy of this file in
"$CARMUSR/lib/python/report_sources/include".

You can look at the example in the end of the code to see how
it can be used.

GOOD TO KNOW:
You can use the command "Special> Reports> Show the Studio Palette"
to get information about the available colours.
"""

from carmensystems.publisher.api import ColourPalette
import Gui
import Crs


class StudioColourPalette(ColourPalette):

    def get_all_colours(self):
        """
        Should be used instead of __dict__ to get access to
        all the colours.
        """
        self.JeppesenBlue  # Do the init if needed.
        return self.__dict__

    def __init__(self):
        """
        Maybe the colours in Studio are not defined yet. Let's wait.
        """
        pass

    def __getattribute__(self, *args, **kw):
        try:
            return ColourPalette.__getattribute__(self, *args, **kw)
        except AttributeError:
            ColourPalette.__init__(self, **self._get_data())
            return ColourPalette.__getattribute__(self, *args, **kw)

    @staticmethod
    def _get_data():
        # Get the colours in Studio
        ln = [Gui.GuiColorNumber2Name(i) for i in range(Gui.C_MAX_COLORS)]
        lv = [Gui.GuiColorName2ColorCode(n) for n in ln]
        if lv[0] is None:
            raise RuntimeError("Studio has not defined all the colours yet.")

        d = dict(zip(ln, lv))

        # Add Jeppesen Corporate colours.
        d['JeppesenBlue'] = '#3366CC'
        d['JeppesenLightBlue'] = '#8DBCD4'
        d['ReportBlue'] = '#99CCFF'
        d['ReportLightBlue'] = '#E8EEFF'

        # Get all the colour Resources.
        r = Crs.CrsGetFirstResourceInfo()
        while r:
            if (r.module == "colours" and r.application == "default"):
                d[r.name] = d.get(r.rawValue, '#FFFFFF')
            r = Crs.CrsGetNextResourceInfo()

        r = Crs.CrsGetFirstResourceInfo()
        while r:
            if (r.module == "colours" and r.application == "gpc"):
                d[r.name] = d.get(r.rawValue, '#FFFFFF')
            r = Crs.CrsGetNextResourceInfo()

        return d

# Public instance
studio_palette = StudioColourPalette()

#
# This shows how you can use this module.
#

import carmensystems.publisher.api as p
# from report_sources.include.studiopalette import studio_palette


class Report(p.Report):

    def create(self):

        def split_cc(cc):
            return int(cc[1:3], 16), int(cc[3:5], 16), int(cc[5:7], 16)

        def get_base_color(cc):
            least, mid, most = sorted(split_cc(cc))
            red, green, blue = split_cc(cc)
            if most == least:
                return 0  # grey
            if most - mid > mid - least:
                if most == red:
                    return 1  # red
                if most == green:
                    return 2  # green
                return 3  # blue
            if least == blue:
                return 4  # yellow
            if least == green:
                return 5  # magenta
            return 6  # cyan

        def my_color_sorter(col1, col2):
            b1 = get_base_color(col1[0])
            b2 = get_base_color(col2[0])
            diff = b1 - b2
            if diff:
                return diff
            return sum(split_cc(col2[0])) - sum(split_cc(col1[0]))

        sp = studio_palette

        self.add("")
        self.add("All colours in the Studio palette:")
        self.add("")

        d = {}
        for n, cc in sorted(sp.get_all_colours().items()):
            d[cc] = d.get(cc, [])
            d[cc].append(n)

        prev_base_col = 0
        for cc, n in sorted(d.items(), my_color_sorter):
            base_col = get_base_color(cc)
            top = 1 if base_col == prev_base_col else 2
            prev_base_col = base_col
            self.add(p.Row(p.Text(", ".join(n), width=250),
                           p.Text("",
                                  width=150,
                                  background=cc),
                           p.Text(cc),
                           border=p.border(left=1, right=1, bottom=1, top=top)))
            self.page()

        self.add("")
        self.add("")

        self.add(p.Text("EXAMPLE 1: Colour 'Marked' and background 'Blue'.",
                        font=p.font(weight=p.BOLD),
                        colour=sp.Marked,
                        background=sp.Blue))

        self.add(p.Text("EXAMPLE 2: Colour 'BrightYellow' and background 'JeppesenBlue'.",
                        font=p.font(weight=p.BOLD),
                        colour=sp.BrightYellow,
                        background=sp.__getattribute__("JeppesenBlue")))

# Self test.
#
if __name__ == "__main__":
    import nth.studio.report_generation as rg  # @UnresolvedImport
    rg.reload_and_display_report()

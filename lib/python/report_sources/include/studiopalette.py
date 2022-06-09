# $Source$
"""
This module provides an instance of the class 
"carmensystems.publisher.api.ColourPalette"
containing all colours in Studio's palette. 
Put a copy or a link to this file in 
"$CARMUSR/lib/python/report_sources/include".
 
You could use the command "Special/Misc/Show Working Window Colors" to 
get information about the available colours. 

You could look at the example below in the code to see how the palette 
could be used.
"""

#
# By Stefan Hammar in Dec 2006.
#

from carmensystems.publisher.api import ColourPalette
import Gui
import Crs

"""
def _studioPaletteInit():
    ln = [Gui.GuiColorNumber2Name(i) for i in range(Gui.C_MAX_COLORS)]
    lv = [Gui.GuiColorName2ColorCode(n) for n in ln]
    d = dict(zip(ln, lv))
    d["SKGrey"] = "#666666"
    d['JeppesenBlue'] = '#3366CC'
    d['JeppesenLightBlue'] = '#8DBCD4'
    d['ReportBlue'] = '#77AAFF'
    d['ReportLightBlue'] = '#CFDDEF'
    return ColourPalette(**d)

studio_palette = _studioPaletteInit()
"""

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
        d['ReportBlue'] = '#77AAFF'
        d['ReportLightBlue'] = '#CFDDEF'
        # Add SK colour
        d["SKGrey"] = "#666666"

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
# This is how you use this module:
#

import carmensystems.publisher.api as p
from report_sources.include.studiopalette import studio_palette as sp #@UnresolvedImport

class Report(p.Report):

    def create(self):
        self.add(p.Text('Test of the studio_palette',
                        colour=sp.BrightRed,
                        background=sp.Green))


if __name__ == "__main__":
    import report_generation as rg
    rg.display_prt_report(source="include.studiopalette")

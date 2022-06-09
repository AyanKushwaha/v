#

'''
PRT standard report parts from OTS.

This module contains functionality that is used for PRT reports.

Added to CARMUSR as a part of the work to support Retiming. 

'''

import carmensystems.publisher.api as p
import Dates

from report_sources.include.studiopalette import studio_palette as sp

bold_font = p.font(weight=p.BOLD)


class SimpleTable(p.Column):
    """
    The simple table class makes it easier to create simple tables
    with a standardized format:
    Bold Header on ReportBlue background
    [Label | data] on alternating White and ReportLightBlue bg
    Single frame around the table
    """
    def __init__(self, title, cross_name='', use_page=True,
                 expandable=False, image='table.jpg'):
        """
        @param title: The header name of the table
        @type title: prt.Box or string
        @param cross_name: prt object name of the SimpleTable instance
                           used together with prt.Crossref()
        @type cross_name: string
        @param use_page: Should page0 breaks be added, default True
        @type use_page: Boolean
        @param expandable: Specifies whether the data section should be
                           expandable. NOTE: this does not work well with sorting
                           or any linking back to this report
        @type expandable: Boolean
        @param image: image to be shown instead of the default table icon
        @type image: string
        """
        p.Column.__init__(self)
        self.use_page = use_page
        self.image = image

        self.num_rows = 0
        self.set(border=p.border_frame(1))

        # The title_row will make sure the background is completely colored
        self.title_row = p.Row(font=p.font(size=10, weight=p.BOLD),
                                 background=sp.ReportBlue
                                 )
        # The title contains the actual objects (icon + texts)
        # which will be isolated from the rest of the table
        self.title = p.Row(p.Image(self.image,
                                       name=cross_name,
                                       padding=p.padding(2, 2, 2, 2)))
        self.title_row.add(p.Isolate(self.title))

        self.add_title(title)
                
        self.link_row = p.Row(font=p.font(size=8),
                                background=sp.Grey,
                                border=p.border(bottom=2,
                                                colour=sp.DarkGrey))
        self.num_link = 0

        self.sub_title = p.Row(font=p.font(size=6),
                               border=p.border(bottom=2,
                                               colour=sp.DarkGrey),
                                               background=sp.ReportBlue)
        self.num_st = 0


        self.table = p.Column()

        if expandable:
            p.Column.add(self, p.Expandable(self.title_row,
                                            self.table,
                                            background=sp.ReportBlue))
        else:
            p.Column.add(self, self.title_row)
            p.Column.add(self, self.table)



    def add_title(self, title):
        """
        Method to add table headers
        @param title: column header
        @type title: string or report object

        @returns: the title object that was just added
        @rtype: report object
        """
        return self.title.add(p.Isolate(title))
 
    def add_link(self, link):
        """
        Method to add links and arrow image to other versions
        or other reports
        @param link: the link to the other report, or header text
        @type link: prt link object, string

        @returns: the link that was just added
        @rtype: report object
        """
        if self.num_link == 0:
            self.table.add(self.link_row)

        if isinstance(link, str):
            ret = p.Text(link) # Makes it possible to add a link header
        else:
            ret = p.Row(p.Image('arrow.jpg',
                                valign=p.CENTER,
                                align=p.RIGHT),
                        link) # Assume proper link object

        self.link_row.add(ret)
        self.num_link += 1

        return ret

    
    def add_sub_title(self, sub_title):
        """
        Method to add column headers
        @param sub_title: column header
        @type sub_title: string or report object

        @returns: the sub title that was just added
        @rtype: report object
        """
        if self.num_st == 0:
            self.table.add(self.sub_title)
                    
        if isinstance(sub_title, str):
            ret = p.Text(sub_title)
        else:
            ret = sub_title # Assume report object
            
        self.sub_title.add(ret)
        self.num_st += 1

        return ret

    def add(self, row):
        """
        Method to add one table row of data
        @param row: data row to add to the table
        @type row: report ojbect or string
        @returns: the same row that was just added
        @rtype: report row
        """
        
        if isinstance(row, p.Row):
            ret = row
        else:
            ret = p.Row(row)
        
        ret.set(background=[sp.White, sp.ReportLightBlue][self.num_rows % 2])

        self.table.add(ret)
        self.num_rows += 1

        # Decrease risk of having single rows on next page
        if self.use_page and self.num_rows % 5 == 0:
            self.page0()

        return ret



def abs2hhmm(a):
    """
    method to format an absolut time into HH:MM (08:42)
    @param a: time to be formated
    @type a: AbsTime
    @return: time in hh:mm
    @rtype: string
    """
    return '%02i:%02i' % a.split()[-2:]


def abs2guidatestr(a):
    return Dates.FDatInt2Date(a.getRep())
    
# End of file

'''

This module contains standard functionality
that is used by all PRT reports.
'''

import locale
import time
import types

from RelTime import RelTime
from Localization import MSGR
import Names
import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave
import carmensystems.studio.reports.CuiContextLocator as CuiContextLocator

from carmusr.fatigue_compat.ots_studiopalette import studio_palette
import carmusr.fatigue_compat.ots_plan as plan
import carmusr.fatigue_compat.ots_bag_handler as bag_handler


def format_int(value, form="%s"):
    '''
    Formats a number according to the set locale.

    LC_NUMERIC in the config extension file decides the separation
    @param value: Value to format
    @type value: int
    '''
    return locale.format(form, value, True)


BOLD_FONT = prt.font(weight=prt.BOLD)


class StandardReport(prt.Report):
    """
    Base class for all PRT reports in OTS.
    """
    def __del__(self):
        cls = self.__class__
        print "*********************************************************************"
        print "%s.StandardReport.__del__:" % __name__
        print "An instance of '%s.%s' has been deleted." % (cls.__module__, cls.__name__)
        print "*********************************************************************"

    def create(self):
        """
        Should normally be called in the beginning of the create method
        of the sub-classes.
        """
        self.store_bag()
        self.standard_header()
        self.standard_footer()

    def store_bag(self):
        """
        Stores a bag for the context, which is decided by the methods
        get_scope and get_type.
        Available types: select, all, win, and legs.
        """

        # Store the current area and bag for interaction
        self.current_context = CuiContextLocator.CuiContextLocator().fetchcurrent()

        # IDEA: Remove this "magic strings" pattern
        # and replace by enums/(or similar) in a conceptual tree structure
        if self.get_scope() == "window":
            if self.get_type() == "roster":
                self.bag_wrapper = bag_handler.MarkedRostersMain()
            if self.get_type() == "trip":
                self.bag_wrapper = bag_handler.MarkedTripsMain()
            if self.get_type() == "leg":
                self.bag_wrapper = bag_handler.MarkedLegsMain()
        if self.get_scope() == "margin":
            if self.get_type() == "roster":
                self.bag_wrapper = bag_handler.MarkedRostersLeft()
            if self.get_type() == "all_roster":
                self.bag_wrapper = bag_handler.WindowChains()
        if self.get_scope() == "plan":
            if self.get_type() == "leg":
                self.bag_wrapper = bag_handler.PlanFreeLegs()
        self.bag = self.bag_wrapper.bag

        self.warning = self.bag_wrapper.warning

    def get_scope(self):
        """
        Should return the scope of the report,
        i.e. 'window', 'margin'(, or 'plan')
        """
        return "window"

    def get_type(self):
        """
        Should return the type of the report,
        i.e. 'roster', 'trip'(, 'duty', or 'leg')
        """
        raise NotImplementedError

    def get_header_text(self):
        """
        Should return the text you want to be in the
        header of the report (e.g. Check Legality)
        """
        raise NotImplementedError

    def standard_header(self):
        '''
        Defines a standard report header:
        -----------------------------------------------------------
        *REPORT TITLE*                                   *OTS LOGO*
        Planning Period:     01Nov-02Dec2003 (LT)
        Rule Set Name:       default_jcp  (Nov03_dated/TRAINING_CAMP_JCP)
        Plan:                TT / COMMON / Dated_1 / HotelStatistics
        Comment*:            This is a report comment
        Partial selections*: 2 trips were ignored
        -----------------------------------------------------------
        @rtype: None
        '''

        title = self.get_header_text()

        ctx_bag = rave.context('default_context').bag()

        try:
            plan_name = plan.get_current_sub_plan().get_file_path()
            plan_name = ' / '.join(plan_name.split('/'))
        except ValueError:
            plan_name = MSGR("No plan loaded")

        h1 = prt.Row(prt.Text(title, colspan=2,
                              font=prt.font(size=14, weight=prt.BOLD),
                              colour=studio_palette.Black))

        pp_start = ctx_bag.fatigue_mappings.period_start_utc()
        pp_end = ctx_bag.fatigue_mappings.period_end_utc()

        if pp_start:
            pp_text = '%s-%s' % (pp_start.ddmonyyyy(True),
                                 pp_end.ddmonyyyy(True))
        else:
            pp_text = MSGR('N/A')

        h2 = prt.Row(prt.Text(MSGR('Planning Period: '), font=BOLD_FONT),
                     prt.Text(pp_text))

        h3 = prt.Row(prt.Text(MSGR('Rule Set Name: '), font=BOLD_FONT),
                     prt.Text('%s   (%s)' % (ctx_bag.rule_set_name(),
                                             ctx_bag.map_parameter_set_name())))

        h4 = prt.Row(prt.Text(MSGR('Plan: '), font=BOLD_FONT),
                     prt.Text(plan_name))

        comment = ctx_bag.report_comment()
        if comment:
            h5 = prt.Row(prt.Text(MSGR('Comment: '), font=BOLD_FONT),
                         prt.Text(comment))
        else:
            h5 = prt.Row()

        if self.warning != "":
            warning_desc = prt.Text(MSGR("Warning"), font=BOLD_FONT)
            warning_text = prt.Text(self.warning,
                                    colour=studio_palette.BrightRed)
            h6 = prt.Row(warning_desc, warning_text)
        else:
            h6 = prt.Row()

        header = \
            prt.Column(prt.Row(prt.Isolate(prt.Column(h1, h2, h3, h4, h5, h6,
                                                      font=prt.font(face=prt.SANSSERIF, size=8),
                                                      colour=studio_palette.VeryDarkGrey)),
                               prt.Column(prt.Image('sas_logo.jpg',
                                                    align=prt.RIGHT,
                                                    width=30,
                                                    height=30)),
                               border=prt.border(bottom=1)),
                       prt.Text(''))
        self.add(prt.Header(header,
                            width=self.page_width()))

    def standard_footer(self):

        c1 = prt.Column(
            prt.Image('examples/jeppesen_simple_logo.jpg',
                      colspan=2,
                      align=prt.RIGHT,
                      border=prt.border(bottom=1)),

            prt.Row(prt.Text(MSGR('Printed '),
                             time.strftime('%d%b%Y %X'),
                             MSGR(' by '), Names.username()),
                    prt.Text(prt.Crossref('current_page'), ' (',
                             prt.Crossref('last_page'), ')',
                             align=prt.RIGHT),
                    font=prt.font(face=prt.SANSSERIF, size=8),
                    colour=studio_palette.VeryDarkGrey))

        self.add(prt.Footer(c1, width=self.page_width()))


class SimpleTableRow(prt.Row):

    DEFAULT_PADDING = prt.padding(left=5, right=5)

    def __init__(self, *components, **properties):
        if 'padding' in properties:
            self.padding = properties['padding']
            del properties['padding']
        else:
            self.padding = self.DEFAULT_PADDING

        prt.Row.__init__(self, **properties)
        for component in components:
            self.add(component)

    def add(self, component):
        if isinstance(component, prt.Container):
            # We can't assume anything about inner containers.
            # They may contain colspan and other difficulties
            pass
        elif isinstance(component, prt.Box):
            component.set(padding=self.padding)
        elif isinstance(component, types.IntType) or isinstance(component, RelTime):
            component = prt.Text(component,
                                 padding=self.padding,
                                 align=prt.RIGHT)
        else:
            component = prt.Text(component,
                                 padding=self.padding)

        return prt.Row.add(self, component)


class SimpleTable(prt.Column):
    """
    The simple table class makes it easier to create simple tables
    with a standardized format:
    Bold Header on ReportBlue background
    [Label | data] on alternating White and ReportLightBlue bg
    Single frame around the table
    """
    def __init__(self, title, cross_name='', use_page=True, image='table.jpg'):
        """
        @param title: The header name of the table
        @type title: prt.Box or string
        @param cross_name: prt object name of the SimpleTable instance
                           used together with prt.Crossref()
        @type cross_name: string
        @param use_page: Should page0 breaks be added, default True
        @type use_page: Boolean
        @param image: image to be shown instead of the default table icon
        @type image: string
        """
        prt.Column.__init__(self)
        self.use_page = use_page
        self.image = image

        self.num_rows = 0
        self.set(border=prt.border_frame(1))

        # The title_row will make sure the background is completely coloured
        self.title_row = prt.Row(font=prt.font(size=10, weight=prt.BOLD),
                                 background=studio_palette.ReportBlue)
        # The title contains the actual objects (icon + texts)
        # which will be isolated from the rest of the table
        self.title = prt.Row(prt.Image(self.image,
                                       name=cross_name,
                                       padding=prt.padding(2, 2, 2, 2)))
        self.title_row.add(prt.Isolate(self.title))

        self.add_title(title)

        self.link_row = prt.Row(
            font=prt.font(size=8),
            background=studio_palette.Grey,
            border=prt.border(bottom=2,
                              colour=studio_palette.DarkGrey))
        self.num_link = 0

        self.sub_title = SimpleTableRow(
            font=prt.font(size=7),
            border=prt.border(bottom=2,
                              colour=studio_palette.DarkGrey),
            background=studio_palette.ReportBlue)
        self.num_st = 0

        self.table = prt.Column()

        prt.Column.add(self, self.title_row)
        prt.Column.add(self, self.table)

    def add_title(self, title):
        """
        Method to add table headers
        @param title: column header
        @type title: string or report object

        @returns: the title object that was just added
        @rtype: report object
        """
        return self.title.add(prt.Isolate(title))

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
            ret = prt.Text(link)  # Makes it possible to add a link header
        else:
            ret = prt.Row(prt.Image('arrow.jpg',
                                    valign=prt.CENTER,
                                    align=prt.RIGHT),
                          link)  # Assume proper link object

        self.link_row.add(ret)
        self.num_link += 1

        return ret

    def add_sub_title(self, sub_title, align=prt.LEFT, page_break=False):
        """
        Method to add column headers
        @param sub_title: column header
        @type sub_title: string or report object
        @param align: The alignment for the header
        @type align: prt.
        @param page_break: Should subtitle be displayed after a page break, default False
        @type use_page: Boolean

        @returns: the sub title that was just added
        @rtype: report object
        """

        if isinstance(sub_title, types.StringType):
            sub_title = prt.Text(sub_title, align=align)

        # The sub_title row should only be shown if it is non-empty
        if self.num_st == 0:
            if page_break:
                self.table.add_header(self.sub_title)
            else:
                self.table.add(self.sub_title)

        self.sub_title.add(sub_title)
        self.num_st += 1

        return sub_title

    def add(self, row):
        """
        Method to add one table row of data
        @param row: data row to add to the table.
                    prt.Row used as is.
                    Any other object wrapped in a SimpleTableRow.
        @type row: Any
        @returns: the row that was just added
        @rtype: report row
        """

        if not isinstance(row, prt.Row):
            row = SimpleTableRow(row)

        if (self.num_rows % 2):
            background = studio_palette.ReportLightBlue
        else:
            background = studio_palette.White

        row.set(background=background)

        self.table.add(row)
        self.num_rows += 1

        # Decrease risk of having single rows on next page.
        # Increased from %5 to %7 to prevent overwriting of "Jeppesen" footer image
        if self.use_page and self.num_rows % 7 == 0:
            self.table.page0()

        return row


class SimpleDiagram(SimpleTable):
    """
    The simple diagram class inherits from SimpleTable and will override
    the icon to display a diagram image instead.
    """
    def __init__(self, title, cross_name=''):
        """
        @param title: The header name of the table
        @type title: prt.Box or string
        @param cross_name: prt object name of the SimpleDiagram instance
                           used together with prt.Crossref()
        @type cross_name: string
        """
        SimpleTable.__init__(self, title, cross_name=cross_name,
                             use_page=False,
                             image='diagram.jpg')


class SimpleCalendar(SimpleTable):
    """
    The simple calendar class inherits from SimpleTable and will override
    the icon to display a calendar image instead.
    """

    def __init__(self, title, cross_name='', report_type='weekly'):
        """
        @param title: The header name of the table
        @type title: prt.Box or string
        @param cross_name: prt object name of the SimpleDiagram instance
                           used together with prt.Crossref()
        @type cross_name: string
        @param report_type: specifies whether the calendar is weekly
        @type report_type: string (only 'weekly' is supported)
        """
        SimpleTable.__init__(self, title, cross_name=cross_name,
                             use_page=False,
                             image='calendar.jpg')

        if report_type == 'weekly':
            self.add_sub_title('')
            self.add_sub_title(MSGR('Mon'))
            self.add_sub_title(MSGR('Tue'))
            self.add_sub_title(MSGR('Wed'))
            self.add_sub_title(MSGR('Thu'))
            self.add_sub_title(MSGR('Fri'))
            self.add_sub_title(MSGR('Sat'))

            self.add_sub_title(prt.Text(MSGR('Sun'),
                                        colour=studio_palette.Sunday))
        else:
            print 'standardreport.SimpleCalender :: only "weekly" tables are supported, returning empty table'


def abs2hhmm(a):
    """
    method to format an absolut time into HH:MM (08:42)
    @param a: time to be formated
    @type a: AbsTime
    @return: time in hh:mm
    @rtype: string
    """
    return '%02i:%02i' % a.split()[-2:]


def abs2hhourm(r):
    """
    method to format a reltime into HhMM (8h42)
    @param a: time to be formated
    @type a: AbsTime
    @return: time in HhMM
    @rtype: string
    """
    return '%2ih%02i' % r.split()[-2:]


def abs2dhm(r):
    """
    method to format a reltime time into DdHhM (2d8h42)
    @param a: time to be formated
    @type a: RelTime
    @return: time in DdHhM
    @rtype: string
    """
    raw_h, m = r.split()[-2:]
    raw_d = raw_h / 24
    d = raw_d and '%sd' % raw_d or ''
    h = raw_h % 24

    return '%s%ih%02i' % (d, h, m)


def abs2ddmmyyyy(a):
    """
    method to format an absolute time into ddmmyyyy (24122009)
    @param a: time to be formated
    @type a: AbsTime
    @return: time in ddmmyyyy
    @rtype: string
    """
    (y, m, d) = a.split()[:3]
    return '%02i%02i%4i' % (d, m, y)


def abs2ddmonyyyy(a):
    """
    method to format an absolute time into ddmonyyyy (12DEC2009)
    @param a: time to be formated
    @type a: AbsTime
    @return: time in ddmonyyyy
    @rtype: string
    """
    return a.ddmonyyyy(True)

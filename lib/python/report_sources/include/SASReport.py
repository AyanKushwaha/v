#

#
# [acosta:06/310@11:15] Changing 'Crossref' back to 'Marker', since it's unclear
#                       if SAS CMS will use Carmen 14.
#
# [vazquez:2007/08/14] Fixed the headerItems part of the SASReport, it showed the whole
#                      dictionary "{'headerItems':{'Month':'Jan','Base':'CPH'}}"
#                      instead of "Month: Jan, Base: CPH" in the report
#
# [acosta:08/094@13:43] Moved imports of Cui and Variable to implementing class, so that
#                       reports can be generated in a "non-Studio" environment.


import time
import carmensystems.rave.api as r
from carmensystems.publisher.api import *
import carmensystems.publisher.nordiclight as NordicLight
from AbsTime import AbsTime
import report_sources.include.ReportUtils as ReportUtils

class AutoPageBreakTable:
    """
    A baseclass for a table which autmatically will pagebreak after reaching page_height in height
    Added rows needs to have attribute 'row_height' defined!
    on 'create()' the table will be written to report
    the table is meant to be used in SASReport subclasses
    It sets the current height in report during creation
    """
    def __init__(self, parent, page_height):
        """
        @parameter parent : a SASReport derived class
        """
        self._parent = parent
        self._rows = []
        self._page_height = page_height

    @property
    def rows(self):
        return self._rows
    
    def add_row(self, row):
        if not hasattr(row,'row_height'):
            raise ValueError("AutoPageBreakTable.add_row: Row must have attribute row_height")
        self.rows.append(row)
        self.rows.sort()
        
    def create_header(self, current_col):
        """
        Override to something useful
        """
        return 0
    
    def create(self):
        _height = self._parent.get_height()
        current_col = Column(width=self._parent.pageWidth)
        _height += self.create_header(current_col) #Header text + label
        for row in self.rows:
            current_col.add(row)
            _height += row.row_height
            if _height > self._page_height:
                self._parent.add(current_col)
                self._parent.newpage()
                current_col = Column(width=self._parent.pageWidth)
                _height = self.create_header(current_col) #Header text + label, init height
        self._parent.add(current_col)
        self._parent.set_height(_height)
        
class SASReport(Report):
    """
    Base class for SAS standard layout reports.
    """
    def __init__(self,*args):
        Report.__init__(self,*args)
        # To handle the pagebreaks
        self._current_page_height = 0
        
    def get_height(self):
        return self._current_page_height
    
    def set_height(self, height):
        self._current_page_height = height
        
    def increase_height(self, incr):
        self._current_page_height += incr
      
    def create(self, title=None, showPlanData=True, pageWidth=520, orientation=PORTRAIT, 
               headers=True, usePlanningPeriod=False, runByUser = None, showPageTotal=True, margins=None, **headerItems):
        """Creates the standard report with header.

        string -- the title of the report
        pageWidth = 520 for portrait, 770 for landscape
        headerItems -- dictionary of extra header items
        """

        #Standard SAS info
        self.SAS_RANKS = "FC","FP","FR","AP","AS","AH","AA","Other"
        self.SAS_BASES = "CPH","STO","OSL","TRD","SVG","BJS","NRT","SHA","Other"
        
        self.setpaper(orientation)

        # Might not be optimal solution
        # Assumes that landscape uses other page width than 520
        if orientation == LANDSCAPE and pageWidth == 520:
            pageWidth = 770

        # Get the Nordic light colour palette
        self.colourPalette = NordicLight.palette()
        
        self.pageWidth = pageWidth
        self.FONTSIZEBODY = 8
        self.set(font = Font(size=self.FONTSIZEBODY), margins=margins)
        self.FONTSIZEHEAD = 9
        self.HEADERBGCOLOUR = '#cdcdcd'
        self.HEADERFONT = Font(size=self.FONTSIZEHEAD, weight=BOLD)
        self.BODYFONT = Font(size=self.FONTSIZEBODY)
        (year,month,day,hours,minutes) = time.localtime()[0:5]
        timezoneName = time.tzname[time.daylight]
        self.now = AbsTime(year,month,day,hours,minutes)
        self.title = title
        self.showPlanData = showPlanData
        if showPlanData:
            # [acosta:08/094@13:43] See header
            import Cui, Variable

            buf = Variable.Variable()

            if usePlanningPeriod:
                planningPeriod, = r.eval(
                    'crg_date.%print_period%(fundamental.%pp_start%, fundamental.%pp_end%-0:01)')
            else:
                planningPeriod, = r.eval(
                    'crg_date.%print_period%(calendar.%month_start%, calendar.%month_end%-0:01)')
            self.planningPeriod = planningPeriod

            Cui.CuiGetSubPlanPath(Cui.gpc_info, buf)
            if not buf.value:
                Cui.CuiGetLocalPlanPath(Cui.gpc_info,buf)
            self.plan = buf.value or "-"

            self.ruleSet, = r.eval('rule_set_name')
            self.planning_area, = r.eval('crg_info.%planning_area_crew%')
        self.headerItems = headerItems

        if headers:
            self.setHeader(self.getDefaultHeader(pageWidth))               
            self.add(self.getDefaultFooter(pageWidth, runByUser, showPageTotal))

    def getPlanningDataItems(self):
        return (self.planningPeriod, self.ruleSet, self.plan, self.planning_area)
    
    def getDefaultFooter(self, pageWidth=None, runByUser=None, showPageTotal=True):
        timezoneName = time.tzname[time.daylight]
        if not pageWidth:
            pageWidth = self.pageWidth
        
        if runByUser is not None:
            user = runByUser
        else:
            try:
                user = r.eval('user')[0]
            except:
                # [acosta:08/094@16:28] Non-Studio env
                import utils.Names as Names
                user = Names.username()
        
        if showPageTotal:
            pageText = Text(Crossref('current_page'),
                            '(',Crossref('last_page'),')',align=RIGHT)
        else:
            pageText = Text(Crossref('current_page'), align=RIGHT)
            
        return Footer(Row(Text("Created ", self.now, " ", timezoneName, " by ", user),
                            pageText,
                            font=Font(size=8),
                            border=border(top=2)),
                            width=pageWidth)

    def getDefaultHeader(self, pageWidth=None):
        if not pageWidth:
            pageWidth = self.pageWidth
        header = Header(width=pageWidth)
        headerRow = Row()

        headerRow.add(Text(self.title,
                           padding=padding(top=1, bottom=1),
                           font=Font(face=SANSSERIF, size=14, weight=BOLD),
                           colspan=10))

        headerRow.add(Image("sas_logo.jpg", 30, 30, align=RIGHT))
        header.add(headerRow)

        if self.showPlanData:
            subHeaderRow = Row(Text('Period:',
                                    padding=padding(left=2, right=1),
                                    align=RIGHT),
                               Text(self.planningPeriod,
                                    padding=padding(left=0, right=2),
                                    align=LEFT,
                                    font=Font(weight=BOLD)),
                               Text('Rule Set:',
                                    padding=padding(left=2, right=1),
                                    align=RIGHT),
                               Text(self.ruleSet,
                                    padding=padding(left=0, right=2),
                                    align=LEFT,
                                    font=Font(weight=BOLD)),
                               Text('Plan:',
                                    padding=padding(left=2, right=1),
                                    align=RIGHT),
                               Text(self.plan,
                                    padding=padding(left=0, right=2),
                                    align=LEFT,
                                    font=Font(weight=BOLD)),
                               Text('Area:',
                                    padding=padding(left=2, right=1),
                                    align=RIGHT),
                               Text(self.planning_area,
                                    padding=padding(left=0, right=2),
                                    align=LEFT,
                                    font=Font(weight=BOLD)),
                               font=Font(size=8))
        else:
            subHeaderRow = Row(Text('', font=Font(size=8)))
 
        if self.headerItems.has_key("headerItems"):
            for label in self.headerItems["headerItems"]:
                    subHeaderRow.add(Text('%s' % label,
                                          padding=padding(left=2, right=1),
                                          align=RIGHT))
                    subHeaderRow.add(Text('%s ' % self.headerItems["headerItems"][label],
                                          padding=padding(left=0, right=2),
                                          align=LEFT,
                                          font=Font(weight=BOLD)))
        
        header.add(Isolate(subHeaderRow))
        try:
            # [acosta:08/094@13:48] When invoked from launcher, Rave is not there...
            comment, = r.eval("crg_comment")
        except:
            comment = ''
        if comment != "":
            commentRow = Row(Text('Comment: %s' % comment,
                                padding=padding(left=2, right=1),
                                align=RIGHT,
                                font=Font(size=8)))
            header.add(Isolate(commentRow))
        header.add(Row(Text(' ', padding=padding(top=0, bottom=0)),
                       border=border(top=2)))

        return header

    def getHeader(self):
        return self.header

    def setHeader(self, header):
        self.add(header)
        self.header = header

    def getTableHeader(self, items, vertical=False, widths=None, aligns=None, def_width=0):
        if vertical:
            output = Column(font=Font(weight=BOLD), border=None)
        else:
            output = Row(font=self.HEADERFONT, border=None, background=self.HEADERBGCOLOUR)
        ix = 0
        for item in items:
            if aligns:
                txt = Text(item, align=aligns[ix])
            else:
                txt = Text(item)
            if widths:
                tmpCol = Column(width=widths[ix])
            elif def_width > 0:
                tmpCol = Column(width=def_width)
            else:
                tmpCol = Column()
            if vertical:
                output.add(txt)
            else:
                tmpCol.add(txt)
                output.add(tmpCol)
            ix += 1            
        return output

    def getCalendarHeaderRow(self):
        return Row(font=Font(size=6, weight=BOLD), border=None, background=self.HEADERBGCOLOUR)
    
    def getCalendarRow(self, dates, leftHeader=None, rightHeader=None,
                       csv=False, cols=1, isDated=True, markWeekday=None,
                       leftHeaders=None):
        dates_str = []
        if isDated:
            for date in dates:
                tmp_date, = r.eval('crg_date.%%print_day_month%%(%s)' % date)
                weekday, = r.eval('time_of_week(%s) / 24:00' % date)
                dates_str.append((tmp_date, weekday))
        else: dates_str = [('Mon', 0), ('Tue', 0), ('Wed', 0), ('Thu', 0),
                           ('Fri', 0), ('Sat', 0), ('Sun', 0)]
            
        if csv:
            tmpRow = ""
            if leftHeader:
                tmpRow = leftHeader
            if leftHeaders:
                tmpRow = ';'.join(leftHeaders)
            for (date, weekday) in dates_str:
                tmpRow += ";"+date
            if rightHeader:
                tmpRow += ";"+rightHeader
        else:
            tmpRow = self.getCalendarHeaderRow()
            if leftHeader:
                tmpRow.add(Text(leftHeader, colspan=cols))
            if leftHeaders:
                for leftHeader in leftHeaders:
                    tmpRow.add(Text(leftHeader, colspan=cols))
            for (date, weekday) in dates_str:
                if markWeekday == weekday:
                    tmpRow.add(Text(date,align=RIGHT, colour=self.colourPalette.VeryDarkRed))
                else:
                    tmpRow.add(Text(date,align=RIGHT))
            if rightHeader:
                tmpRow.add(Text(rightHeader,align=RIGHT))
        return tmpRow
    
    def modify_pp(self):
        """
        If parameter set, use month instead of planning period
        """
        try:
            if r.param("report_common.%report_use_planning_month_p%").value():
                _start_time, = r.eval("fundamental.%pp_start%")
                _end_time, = r.eval("fundamental.%publ_period_end%")
                # Change period, will be reset on lost of scope for method due to cleanup of _ppmod
                self._ppmod = ReportUtils.PPModifier(_start_time, _end_time)
        except:
            pass # Non-studio enviroment
        
    def reset_pp(self):
        """
        Reset pp by deleting object
        """
        try:
            del self._ppmod
        except:
            pass # not created
        
# End of file


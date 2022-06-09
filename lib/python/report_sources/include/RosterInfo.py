#####

##
#####
__version__ = "$Revision$"

"""
RosterInfo report in prt-format
@date: 2jun2008
@author: Per Groenberg
@org Jeppesen Systems AB
"""

import carmensystems.publisher.api as p
import carmensystems.rave.api as r
import report_sources.include.SASReport as SASReport
import carmstd.studio.gantt as gantt
import carmstd.studio.datetoolkit as datetoolkit
import carmensystems.publisher.nordiclight as nordiclight
import RelTime


palette = nordiclight.palette()
#global parameters
_spacer_height = 5
_flight_text_height = 7
_trip_rectangle_height = 8
_roster_height = 80
_compact_roster_height = 18
_roster_header_height = 20
_roster_width = 770
_page_height = 395
_trip_rectangle_color = palette.Grey
_text_height = 8
_gnd_size = 10
_crew_info_width = 50

_code_indent = 60
_ONE_MIN=RelTime.RelTime('00:01')
_DAY=RelTime.RelTime('24:00')
# there are three kinds of roster report in the standard concept user
# _AbstractRosterReport is an abstract class from which the _CompactReport,
# _DutyBasedReport and _FlightBasedReport derive. This abstract class
# helps to factorise the code.
class _AbstractRosterReport(SASReport.SASReport):
    
    def create(self, context='default_context'):
        #
        # used to calculate when we shall put a page break
        # is needed to be able to put the gantt header for each page
        #
        self.modify_pp()
        SASReport.SASReport.create(self, title=self.get_title(), showPlanData=True,
                                   orientation=p.LANDSCAPE, usePlanningPeriod=True)
        self.set_height(0)
    
        self.default_bag=r.context(context).bag()
        #
        # Set report values
        #
        #self.set(font=p.Font(face=p.SANSSERIF,size=_text_height))
        #self.setpaper(orientation=p.LANDSCAPE)
        #
        # Add a header and a footer
        #
        #self.add(sas_report.getDefaultHeader(orientation=p.LANDSCAPE))
        #self.add(standardreport.standard_footer(orientation=p.LANDSCAPE))
        
        #
        # first_day and end_day (some extra days added to get the ends the trips
        #
        
        self.first_day = self.default_bag.report_common.report_pp_start()
        self.extra_days = 3 # can be controlled via rave
        self.end_day = self.default_bag.report_common.report_pp_end().\
                       adddays(self.extra_days)

        
        #self.add_column_header()
        
        
        for roster_bag in self.default_bag.iterators.roster_set():
            self.add_one_crew(roster_bag)
            self.add_spacer()
        self.reset_pp()
        
    def add_spacer(self):
        self.add(p.Row(p.Text(" "),height=_spacer_height))
        
    def add_column_header(self):
        """
        add the column header ( one cell per day,
        weekday and day of the month in cell
        """
        self.add(self.get_column_header())
        
    def get_column_header(self):
        """
        Return header
        """
        return  _GanttHeader(self.extra_days,self.first_day,
                             self.end_day, _roster_width, 
                             _roster_header_height, align=p.RIGHT,
                             border=p.border_frame(1))
    
    def add_one_crew(self, roster_bag):
        """
        The information for one crew member is splitted in these
        parts:
            - crew_info (Crew Info)
            Is the left information for every crew.
            Contains information like Crew Id, name etc...
            - a gantt of the trips of the crew.
        
        @param roster_bag :  bag. Contains a roster.
        """
        crew_rows = self._get_rows(roster_bag)
        current_crew_rows_heigth = 0
        for heigth, row in crew_rows:
            current_crew_rows_heigth += heigth

        if self.get_height() > 0 and \
               self.get_height()+current_crew_rows_heigth > _page_height:
            self.newpage()
            self.reset_height=0
            #self.add_column_header()

        self.increase_height(current_crew_rows_heigth)
        
        for heigth,row in crew_rows:
            self.add(row)
        
            
    def _get_roster_row(self, roster_bag):
        crew_info, info_height = self.get_crew_info(roster_bag)
        current_roster = self.get_roster_gantt(roster_bag)
        current_roster_size = current_roster.size()[1]
        return (info_height+ _roster_header_height+ current_roster_size + _spacer_height,
                p.Column(crew_info,
                         self.get_column_header(), 
                         current_roster,
                         border=p.border_frame(1)))
    
    def _get_rows(self,roster_bag):
        return [self._get_roster_row(roster_bag)]
        
    def get_crew_info(self, roster_bag):
        """
        Returns the crew info aera. The duty based and flight reports have the save
        crew info area
        
        @param roster_bag :  bag. Contains a roster.
        """
        
        #crew_info = p.Column(border=p.border_frame(1), width=_crew_info_width)
        #crew_info.add(p.Row("%-16.16s" % roster_bag.report_roster.crew_name(),
        #                    "%-s" % roster_bag.report_roster.crew_rank()))
        #crew_data= p.Row()22222
        text = '  '.join(["%-18.18s" % roster_bag.report_roster.crew_name(),
                          "%-18.18s" % roster_bag.report_roster.crew_empno(),
                          "%-18.18s" % roster_bag.report_roster.crew_pt_factor(),
                          "%-10.18s" %roster_bag.report_roster.crew_rank(),
                          "%-10.18s" %roster_bag.report_roster.crew_base(),
                          "%-10.18s" %roster_bag.report_roster.crew_group(),
                          "%-10.18s" %roster_bag.report_roster.crew_sen()])
        crew_info = p.Row(p.Text(text,align=p.LEFT, valign=p.BOTTOM),
                          border=p.border_frame(1), height=_compact_roster_height)
        #crew_info.add(crew_data)
        
        return crew_info, _compact_roster_height

#
# class to use for a flight based report
# the get_roster_gantt is overwritten
# the create method call the parent create method.
#
class _FlightBasedReport(_AbstractRosterReport):
    def create(self, context='default_context'):
        self.roster_height =  _roster_height
        _AbstractRosterReport.create(self, context=context)
        
    def get_title(self):
        return "Roster Info"
    
    def get_roster_gantt(self,roster_bag):
        return _FlightBasedRosterGantt(self.first_day, 
                                      self.end_day,
                                      _roster_width,
                                      self.roster_height,
                                      roster_bag)
        
    
class _Duty(object):
    """
    Object used to store duty data. 
    """
    def __init__(self, duty_bag):
        """
        reported data stored for each duty
            start_date : AbsTime. date when the duty starts
            start_time : string. time when the duty starts
            end_time : string. time when the duty ends
            layover : string.
        @param duty_bag: bag. Represents a duty
        """
        
        self.start_date = duty_bag.report_roster.duty_start_date()
        try:
            self.start_time =  "%02d%02d" % duty_bag.report_roster.duty_start().split()[3:5]
        except:
            self.start_time = "????"
        try:
            self.end_time = "%02d%02d" % duty_bag.report_roster.duty_end().split()[3:5]
        except:
            self.end_time = "????"
        self.layover =  duty_bag.report_roster.layover_info()
        self.end_date = duty_bag.report_roster.duty_real_end_date()
        
        #
        #if the duty ends the following day, the '>' caracter is added at the end
        #
        #if duty_bag.report_roster.duty_real_end_date() > duty_bag.report_roster.duty_start_date():
        #    self.end_time= "%s%s" % (self.end_time,">")
        #
        # liste of the flight info to report
        #    
        self.legs=[]
        self.has_cabin_training = False
        for leg_bag in duty_bag.iterators.leg_set():
            if leg_bag.report_common.leg_is_any_cabin_training():
                self.has_cabin_training = True
            flight_info = leg_bag.report_roster.flight_info()
            if leg_bag.leg.is_simulator() and int(leg_bag.leg.check_in()) > 0:
                self.legs.append('B' + leg_bag.leg.code()[1:])
            if leg_bag.leg.is_ground_duty() or leg_bag.leg.is_pact():
                duty_code = ''
                if leg_bag.leg.is_ol123() and leg_bag.duty_code.leg_code():
                    duty_code = '[' + leg_bag.duty_code.leg_code() + ']'
                self.legs.append(leg_bag.report_common.leg_code() + ' ' + flight_info)
                self.legs.append(duty_code)
            else:
                self.legs.append(flight_info)
            if leg_bag.leg.meal_stop():
                self.legs.append("MEAL")
            if leg_bag.leg.is_simulator() and int(leg_bag.leg.check_out()) > 0:
                self.legs.append('D' + leg_bag.leg.code()[1:])
                
            
    def get_flight_nb(self):
        return len(self.legs)
        
class _Trip(object):
    """
    Object used to store trip data.
    """
    def __init__(self, trip_bag):
        """
        reported data stored for each trip
            duties : list of duty objects. Duties of the trip
            is_flight_duty : boolean.
            real_start : AbsTime. date when trip starts
            real_end : AbsTime. date when the trip ends
            
            start = AbsTime. date and time when trip starts
            end = AbsTime. date and time when trip ends
            name = string. id of the trip
            
            code = string.  task code when is not flight duty
            start_time_aux = string. time when trip starts (used only for non flight duty trip) 
            end_time_aux = string. time when trip ends (used only for non flight duty trip)
            
        @param trip_bag: bag. Represents a trip
        """
        #duties of the trip
        self.duties = []
        self.has_only_flight_duty = trip_bag.trip.has_only_flight_duty()
        self.real_start = trip_bag.report_roster.trip_real_start_date()
        self.real_end = trip_bag.report_roster.trip_real_end_date()
        
        self.start = trip_bag.report_roster.trip_start()
        self.end = trip_bag.report_roster.trip_end()
        self.name = ""  # Removed for SASCMS-1541: trip_bag.trip.name()
        
        self.code = trip_bag.trip.code()
        self.start_time_aux = trip_bag.report_roster.start_time_aux()
        self.end_time_aux = trip_bag.report_roster.end_time_aux()

        self.is_standby =  trip_bag.trip.is_standby()
        for duty_bag in trip_bag.iterators.duty_set():
            self.duties.append(_Duty(duty_bag))

        self._days_n_codes = {}
        for leg in trip_bag.iterators.leg_set():
            start_date = leg.crg_roster.leg_start_date()
            if ((not self._days_n_codes.has_key(start_date)) and
                (not leg.leg.group_code() == "PAT") and
                (not leg.leg.is_flight_duty() or self.is_standby) and
                (not leg.report_common.leg_is_any_cabin_training())):
                for day_ix in range(int((leg.leg.end_date() - leg.leg.start_date())/_DAY) + 1):
                    self._days_n_codes[start_date+_DAY * day_ix] = leg.crg_info.leg_code()
        
        
    def __getitem__(self, day):
        return self._days_n_codes.get(day,"")

    def __iter__(self):
        return iter(self._days_n_codes)

    def get_first_duty(self):
        if len(self.duties)==0:
            return None
        return self.duties[0]
    
    def get_last_duty(self):
        if len(self.duties)==0:
            return None
        return self.duties[len(self.duties)-1]
            

#
# class used to draw the header of the rosters
#
class _GanttHeader(gantt.Gantt):
    def __init__(self, extra_days,first_day,
                 end_day, _roster_width, 
                 _roster_header_height,
                 align=p.RIGHT,
                 border=p.border_frame(1)):
        self.extra_days = extra_days
        gantt.Gantt.__init__(self,first_day,
                             end_day, _roster_width, 
                             _roster_header_height,
                             align=align,
                             border=border)
        
    def draw(self,gc):
        #
        # calls the parent draw method for the bars
        #
        gantt.Gantt.draw(self,gc)
        
        #
        # computes the 'y' positions
        #
        x0,y0,x1,y1 = gc.get_coordinates()
        
        text_height = gc.text_size("CODE")[1]
        padding = int((y1 - y0 - 2* text_height) / 3)
        
        weekday_pos = y1 - padding
        date_pos = y0 + padding + text_height
        for day in datetoolkit.day_range(self.start_day, self.end_day-_ONE_MIN):
            
            year, month, date, hour, minute = day.split()
            # gray dates outside planning period
            if day>= self.end_day.adddays(-self.extra_days):
                offset = _ONE_MIN*45
                gc.rectangle(day+offset,y1, _DAY-offset*2, #Tested via trial and error
                             _roster_header_height,fill=palette.Grey)
            gc.text(datetoolkit.add_half_day(day), weekday_pos, datetoolkit.get_weekday(day),
                    align=p.CENTER,
                    font=p.Font(face=p.SANSSERIF))
            gc.text(datetoolkit.add_half_day(day), date_pos, date,
                    align=p.CENTER,
                    font=p.Font(face=p.SANSSERIF))    

#
# Abstract class, derives form gantt.Gantt, is a Canvas
#
class _RosterGantt(gantt.Gantt):
    """
    object used to draw the crew gantt.
    """
    def __init__(self, start_day, end_day, width, height, roster_bag, **kw):
                            
        #data structure where the trip of the roster are stored,
        #for each rave trip a python trip object is created
        self.trips = [] 
        for trip_bag in roster_bag.iterators.trip_set():
            self.trips.append(_Trip(trip_bag))
            
        self.compute_height(height)
            
        # the 'y' positions of the different texts and rectangle
        self.task_info_height_pos = self.height-3
        self.trip_rectangle_pos = self.task_info_height_pos - _text_height-1
        self.start_time_pos = self.trip_rectangle_pos - _trip_rectangle_height-1 
        self.end_time_pos = self.start_time_pos-self.max_duty_flight_nb*_flight_text_height -\
                            _text_height-1
        self.layover_pos = self.end_time_pos - _text_height-1 
        gantt.Gantt.__init__(self, start_day, end_day, width, self.height, **kw)
    
    def compute_height(self,height):
        """
        sets the height. It is redefined for compactRosterGantt in which case
        the height will be increased.
        """
        self.max_duty_flight_nb = 0     
        self.height = height
       
    def get_max_duty_flight_nb(self):
        """
        returns the greatest number of the duty flights. 
        """ 
        max_duty_leg_nb=0
        for trip in self.trips:
            for duty in trip.duties:
                if max_duty_leg_nb<duty.get_flight_nb():
                    max_duty_leg_nb = duty.get_flight_nb()
        return max_duty_leg_nb
    

    def draw(self,gc):
        #
        # calls the parent draw method where are drawn the bars.
        #
        gantt.Gantt.draw(self,gc)
        
        #
        # this method is rewrite in the sub classes.
        # Drawns the information in the gantt
        #
        self.draw_trips(gc)
        


                

class _FlightBasedRosterGantt(_RosterGantt):
    
    def compute_height(self,height):
        self.max_duty_flight_nb = self.get_max_duty_flight_nb()
        self.height = height+self.max_duty_flight_nb*_flight_text_height

    def _draw_time_test(self, gc, x_pos, y_pos, t):
        # [acosta:08/238@13:29] This is probably the wrong place, but sometimes
        # t is None (void).
        time = (t or "ZZ:ZZ")
        gc.text(datetoolkit.add_hour(x_pos), 
                y_pos, 
                time[0:2], font=p.font(size=8))
        gc.text(datetoolkit.add_hour(x_pos)+_ONE_MIN*600, 
                y_pos-0.3, 
                time[2:5], font=p.font(size=7))
        
    def draw_trips(self,gc):
        for trip in self.trips:
            if not trip.has_only_flight_duty or trip.is_standby:
                for duty in trip.duties:
                    # Check for PAT or DH
                    # Only specify ground duty if more than one
                    if duty.get_flight_nb() > 1 or duty.has_cabin_training:
                        for leg_num in xrange(duty.get_flight_nb()):
                            gc.text(duty.start_date +_ONE_MIN*_code_indent, 
                                    self.start_time_pos-leg_num*_flight_text_height-_text_height-1,
                                    duty.legs[leg_num],
                                    font=p.font(size=_flight_text_height))
                                
                    #if trip[duty.start_date] <> "":
                    for td in trip:
                        gc.text(datetoolkit.add_half_day(td),
                                self.task_info_height_pos,
                                trip[td], align=p.CENTER, font=p.font(size=_gnd_size))
                        #gc.text(datetoolkit.add_half_day(duty.start_date),
                        #        self.task_info_height_pos,
                        #        trip[duty.start_date], align=p.CENTER, font=p.font(size=_gnd_size))
                
                # some of the none flight duty trips have start and end times.
                # they are reported in the start and end date cells
                self._draw_time_test(gc, trip.real_start,
                                     self.start_time_pos,
                                     trip.start_time_aux)
                self._draw_time_test(gc, trip.real_end,
                                     self.end_time_pos,
                                     trip.end_time_aux)
            else:
                # duty start and end times reported in the duty date cell
                self._draw_time_test(gc, trip.get_first_duty().start_date,
                                     self.start_time_pos,
                                     trip.get_first_duty().start_time)
                self._draw_time_test(gc, trip.get_last_duty().end_date,
                                     self.end_time_pos,
                                     trip.get_last_duty().end_time)
                for duty in trip.duties:
                    for leg_num in xrange(duty.get_flight_nb()):
                        if duty.legs[leg_num] == "MEAL":
                            # Mark meals with grey background
                            gc.rectangle(duty.start_date+_ONE_MIN*_code_indent, 
                                         self.start_time_pos-leg_num*_flight_text_height-\
                                         _text_height-1,
                                         _ONE_MIN*60*20 ,
                                         _flight_text_height, 
                                         fill=palette.Grey)
                            
                        gc.text(duty.start_date +_ONE_MIN*_code_indent, 
                                self.start_time_pos-leg_num*_flight_text_height-_text_height-1,
                                duty.legs[leg_num],
                                font=p.font(size=_flight_text_height))
                        
                # the trip id reported in the first duty cell
                gc.text(datetoolkit.add_hour(trip.real_start),
                        self.task_info_height_pos,
                        trip.name)

            # layover
            for duty in trip.duties:
                gc.text(datetoolkit.add_half_day(duty.start_date), 
                        self.layover_pos, 
                        duty.layover, align=p.CENTER)
            
    
    
        
class _RosterInfo(_FlightBasedReport):
    pass
                          







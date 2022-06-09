"""
 $Header$
 
 Sim Dated Info

 Lists all OPC and AST activities in the planning period, using
 a weekly view.

 Created:    August 2007
 By:         Erik Gustafsson, Jeppesen Systems AB

"""

# imports ================================================================{{{1
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from RelTime import RelTime
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator as CCL
import Cui
import report_sources.include.ReportUtils as ReportUtils

# constants =============================================================={{{1
CONTEXT = 'default_context'
TITLE = 'Course Schedule Info'
class CrewBase(object):
    def __init__(self, id, first, last):
        self.__id = id
        self.__first = first
        self.__last = last

    @property
    def name(self):
        return self.__last + " " + self.__first

    @property
    def id(self):
        return self.__id

    def __str__(self):
        return self.name + " " + self.id

class Crew(CrewBase):
    def __init__(self, id, first, last):
        CrewBase.__init__(self, id, first, last)
        self.__simActivityGroup = None
    
    @property
    def hasSimActivityGroup(self):
        return self.__simActivityGroup != None
    
    @property
    def simActivityGroup(self):
        return self.__simActivityGroup

    def setSimActivityGroup(self, simActivityGroup):
        self.__simActivityGroup = simActivityGroup
        simActivityGroup.addCrew(self)

    def __str__(self):
        return CrewBase.__str__(self) + " " + str(self.hasSimActivityGroup) + " " + str(self.simActivityGroup)

class CaActivityCrew(CrewBase):
    def __init__(self, id, first, last):
        CrewBase.__init__(self, id, first, last)
        self.__course = None
        self.__activities = []

    @property
    def course(self):
        return self.__course

    def setCourse(self, course):
        self.__course = course
        
    def addActivity(self, act):
        self.__activities.append(act)

    @property
    def activities(self):
        return self.__activities
        
    def __str__(self):
        return CrewBase.__str__(self) + "no acts: " + str(len(self.__activities)) + " course: " + str(self.course)
    
class SimActivityGroup(object):
    def __init__(self, ix):
        self.__crew =  []
        self.__activities = []
        self.__index = ix

    def addCrew(self, crew):
        self.__crew.append(crew)
        
    @property
    def crew(self):
        return self.__crew
    
    @property
    def group_id(self):
        return str(self.__index)
    
    def addActivity(self, activity):
        self.__activities.append(activity)
        
    @property
    def activities(self):
        return self.__activities

    def __str__(self):
        return "sag no act: " + str(len(self.activities)) + "no crew: " + str(len(self.crew))
    
class Course(object):
    def __init__(self, id, info):
            self.__id = id
            self.__activities = []
            self.__simActivityGroups = []
            self.__crew = dict()
            self.__info = info

    @property
    def id(self):
        return self.__id

    def addCrew(self, crew):
        self.__crew[crew.id] = crew
        
    @property
    def crew(self):
        return self.__crew.values()
    
    def addActivity(self, activity):
        self.__activities.append(activity)
        
    @property
    def activities(self):
        return self.__activities

    def addSimActivityGroup(self, activity):
        self.__simActivityGroups.append(activity)
        
    @property
    def simActivityGroups(self):
        return self.__simActivityGroups
    
    @property
    def hasSimActivityGroup(self):
        return (self.__simActivityGroups != None)
    
    @property
    def info(self):
        return self.__info

    def __str__(self):
        return self.id + " " + self.info

class Activity(object):
    def __init__(self,  code, group, desc, date, start, end, base, showDate = True):
            self.__code = code
            self.__group = group
            self.__desc = desc
            self.__date = date
            self.__start = start
            self.__end = end
            self.__base = base
            self.__showDate = showDate
            
    @property
    def base(self):
        return self.__base
    
    @property
    def end(self):
        return self.__end
    
    @property
    def start(self):
        return self.__start

    @property
    def dateStr(self):
        if self.showDate:
            return str(self.__date)
        else:
            return ''
    @property
    def duty(self):
        return self.__code
    @property
    def type(self):
        return self.__group
    @property
    def info(self):
        return self.__desc

    @property
    def showDate(self):
        return self.__showDate
    def __str__(self):
        return self.type + " " + self.info + " " + self.duty + " " + self.dateStr + " " + str(self.start) + " " + str(self.end)
    
class CourseInfoBase(SASReport):

    def presentCourseInfo(self, course):
        box = Column(border=border(bottom=1))
        row1 = Row(Text("Crew Schedule"))
        box.add(row1)
        row2 = Row(Text("Course: %s Aircraft Type: %s " %(course.id, course.info)))
        box.add(row2)
        return box

    def getCrewRow(self, crew):
        row = Row(Text("%s %s " %(crew.id, crew.name)))
        return row

    def presentCourseCrew(self, crews, id = ''):
        
        column1 = Column(Text("Crew: %s" %(id,)))
        column2 = Column(Text(""))
        if len(crews) > 1:
            column3 = Column(Text("Students:"))
        else:
            column3 = Column(Text("Student:"))
        column4 = Column()
        for crew in crews:
            column4.add(self.getCrewRow(crew))
        row1 = Row()
        row1.add(column1)
        row1.add(column2)
        row1.add(column3)
        row1.add(column4)
        row2 = Row()
        column1 = Column(Text("Date"), width = 100)
        column2 = Column(Text("Start"))
        column3 = Column(Text("End"))
        column4 = Column(Text("Duty"))
        column5 = Column(Text("Type"))
        column6 = Column(Text("Information"))
        column7 = Column(Text("Base"))
        row2.add(column1)
        row2.add(column2)
        row2.add(column3)
        row2.add(column4)
        row2.add(column5)
        row2.add(column6)
        row2.add(column7)
        box = Column(border=border(bottom=1))
        box.add(row1)
        box.add(row2)
        return box

    def presentCourseActivity(self, act):
        row = Row()
        dateCol = Column(Text(act.dateStr), width = 100)
        row.add(dateCol)
        startCol = Column(Text(str(act.start)))
        endCol = Column(Text(str(act.end)))
        sessionCol = Column(Text(str(act.duty)))
        actCol = Column(Text(str(act.type)))
        locCol = Column(Text(str(act.info)))
        baseCol = Column(Text(str(act.base)))
        row.add(startCol)
        row.add(endCol)
        row.add(sessionCol)
        row.add(actCol)
        row.add(locCol)
        row.add(baseCol)
        return row

    def presentCourseActivities(self, activities):
        box = Column()
        for activity in activities:
            if activity:
                box.add(self.presentCourseActivity(activity))
        return box
    
    def presentSimGroup(self, simGroup):
        self.add(self.presentCourseCrew(simGroup.crew, simGroup.group_id))
        self.add(self.presentCourseActivities(simGroup.activities))
        
    def presentSimGroups(self, simGroups):
        for simGroup in simGroups:
            self.newpage()
            self.presentSimGroup(simGroup)
        

            


class CourseInfo(CourseInfoBase):
    def create(self):
        #################
        ## Basic setup
        #################
        data = self.getData()
        self.presentData(data)

    def presentData(self, data):
        SASReport.create(self, TITLE, orientation=PORTRAIT, usePlanningPeriod=True)
        for course in data:
            self.add(self.presentCourseInfo(course))
            self.add(self.presentCourseCrew(course.crew))
            self.add(self.presentCourseActivities(course.activities))
            self.add(self.presentSimGroups(course.simActivityGroups))
            self.newpage()

    def getData(self):
        crewDict = self.getCrewDict()
        return self.getCourses(crewDict)
            
    def getCrewDict(self):
        crew_expr = R.foreach(R.iter('iterators.roster_set',
                                    where = ('report_courses.%crew_has_training%')),
                              'crew.%id%',
                              'crew.%employee_number%', # Used for placement in report
                              'crew.%firstname%', # Used for placement in report
                              'crew.%surname%', # Used for placement in report     
                             )
        sims, = R.eval('default_context', crew_expr)
        crewDict = dict()
        for (ix, crew_id, emp_no, first, last) in sims:
            crewDict[crew_id] = Crew(emp_no, first, last)
        return crewDict

    def getCourses(self, crewDict):
        course_expr = R.foreach(R.iter('report_courses.course_leg_set',
                                       where = ('report_courses.%ground_course_or_sim%')),
                                'report_courses.%course_name%', # Used for identification
                                'report_courses.%aircraft_type%', # Used for placement in report
                                R.foreach(R.iter('report_courses.course_activity_leg_set',
                                       where = ('report_courses.%ground_course%', 'report_courses.%show_in_common%')),
                                          # Crew info for simulator
                                          'report_courses.%code%',
                                          'report_courses.%group_code%',
                                          'report_courses.%description%',
                                          'report_courses.%start_date%',
                                          'leg.%start_od%',
                                          'leg.%end_od%',
                                          'report_common.%leg_base%',
                                          R.foreach('iterators.leg_set',
                                          # Crew info for simulator
                                          'crew.%id%'
                                          )
                                ),
                                R.foreach(R.iter('report_courses.course_simulator_leg_set',
                                       where = ('report_courses.%simulator%')),
                                          'report_courses.%code%',
                                          'report_courses.%group_code%',
                                          'report_courses.%description%',
                                          'report_courses.%start_date%',
                                          'leg.%start_od%',
                                          'leg.%end_od%',
                                          'report_courses.%briefing_start%',
                                          'report_courses.%debriefing_end%',
                                          'report_common.%leg_base%',
                                          R.foreach('iterators.leg_set',
                                          # Crew info for simulator
                                          'crew.%id%'
                                          )
                                )
                      )
        courses_raw, = R.eval('default_context', course_expr)
        courses =  []
        i = 0
        for (ix, course, ac_type, act_slices, sim_slices) in courses_raw:
            course = Course(course, ac_type) 
            simActivityGroup = None                   
            for (ix, code, group, desc, date, start, end, base, crew_slices) in act_slices:
                act = Activity(code, group, desc, date, start, end, base)
                course.addActivity(act)
                for (ix, crewId) in crew_slices:
                    course.addCrew(crewDict[crewId])
            sim_group_ix = 0
            for (ix, code, group, desc, date, start, end, briefstart, debriefend, base, crew_slices) in sim_slices:
                briefing = Activity(code, 'Briefing', '', date, briefstart, start, base)
                act = Activity(code, group, desc, date, start, end, base, False)
                debriefing = Activity(code, 'Debriefing', '', date, end, debriefend, base, False)
                for (ix, crewId) in crew_slices:
                     crew = crewDict[crewId]
                     if simActivityGroup:
                          crew.setSimActivityGroup(simActivityGroup)
                     if crew.hasSimActivityGroup:
                         simActivityGroup = crew.simActivityGroup
                         break
                     else:
                         sim_group_ix = sim_group_ix + 1
                         simActivityGroup = SimActivityGroup(sim_group_ix)
                         course.addSimActivityGroup(simActivityGroup)
                         crew.setSimActivityGroup(simActivityGroup)
                simActivityGroup.addActivity(briefing)
                simActivityGroup.addActivity(act)
                simActivityGroup.addActivity(debriefing)
                simActivityGroup = None
            courses.append(course)
        return courses

class CourseCrewInfo(CourseInfoBase):
        
    def create(self):
        TITLE = 'Course Crew Info'
        #################
        ## Basic setup
        #################
        data = self.getData()
        self.presentData(data)

    def presentData(self, data):
        SASReport.create(self, 'Course Crew Info', orientation=PORTRAIT, usePlanningPeriod=True)
        for crew in data:
            #print str(crew)
            self.add(self.presentCourseInfo(crew.course))
            self.add(self.presentCourseCrew([crew,]))
            self.add(self.presentCourseActivities(crew.activities))
            self.newpage()
            

    def getData(self):
        crews = []
        course_expr = R.foreach(R.iter('iterators.roster_set',
                                    where = ('report_courses.%crew_has_training%')),
                              'crew.%employee_number%', # Used for placement in report
                              'crew.%firstname%', # Used for placement in report
                              'crew.%surname%', # Used for placement in report
                                R.foreach(R.iter('report_courses.course_leg_set',
                                       where = ('report_courses.%ground_course_or_sim%')),
                                          'report_courses.%course_name%', # Used for identification
                                          'report_courses.%aircraft_type%', # Used for placement in report
                                          R.foreach(R.iter('report_courses.all_course_activity_leg_set',
                                                           where = ('report_courses.%ground_course_or_sim%')),
                                                    'report_courses.%code%',
                                                    'report_courses.%group_code%',
                                                    'report_courses.%description%',
                                                    'report_courses.%start_date%',
                                                    'leg.%start_od%',
                                                    'leg.%end_od%',
                                                    'report_common.%leg_base%',
                                      )    
                                 
                                )
                      )
        crew_raw, = R.eval('default_context', course_expr)
        for (ix, crew_id, first, last, course_slices) in crew_raw:
            crew = CaActivityCrew(crew_id, first, last)
            for (ix, course, ac_type, act_slices) in course_slices:
                course = Course(course, ac_type)
                #print "crew: " + str(crew) + "course: " + str(course)
                crew.setCourse(course)
                for (ix, code, group, desc, date, start, end, base) in act_slices:
                    act = Activity(code, group, desc, date, start, end, base)
                    crew.addActivity(act)
            crews.append(crew)
        return crews
        
### End of file

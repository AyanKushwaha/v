#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
from carmstd import bag_handler
from RelTime import RelTime
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator as CCL
import Cui
import report_sources.include.ReportUtils as ReportUtils
import carmensystems.publisher.api as p
import os
import os.path
from datetime import datetime
#*****************************************************************
#*****************************************************************
#*****************************************************************

TITLE = 'Crew_training_name'

###################################################################
# ï¿½ndra i klassen DataContainer sï¿½ att den innehï¿½ller sï¿½ mï¿½nga 
# variabler som du behï¿½ver skriva ut vï¿½rdet pï¿½ i din rapport.
# Variablernas namn ï¿½r upp till dig men mï¿½ste matcha det du anvï¿½nder 
# i metoden presentRow() lï¿½ngst ned

def formatDate(date):
    try:
        d = date.yyyymmdd()
        return "%s-%s-%s" %(d[:4], d[4:6], d[6:])
    except:
        return str(date)

def formatDateStr(date):
    try:
        d = date.ddmonyyyy()
        return "%s" %(d[:9])
    except:
        return str(date)
    
class CourseDay(object):
    def __init__(self, course_bag):
        self.__partisipants = []
        self.__name = course_bag.report_training.instructor_student_group_code()
        for course in course_bag.iterators.leg_set(sort_by="not report_training.%is_instructor_on_course%"):
            self.__partisipants.append(Partisipant(course.report_training.crew_empno(),
                    course.report_training.crew_personal_no(),
                    course.report_training.crew_name(),
                    course.report_training.crew_adress(),
                    course.report_training.crew_rank(),
                    course.report_training.crew_department(),
                    course.report_training.course_code(),
                    course.report_training.start_lt(),
                    course.report_training.end_lt(),
                    course.report_training.is_instructor_on_course()))

    @property
    def partisipants(self):
        return self.__partisipants

    @property
    def no_entries(self):
        return len(self.__partisipants) + 2

    @property
    def name(self):
        return self.__name

class Partisipant(object):
    def __init__(self, empno, crew_personal_no, crew_name, crew_adress, crew_rank, crew_department, instructor_student_group_code, start, end, is_instructor):
        self.__empno =  empno 
        self.__crew_personal_no = crew_personal_no
        self.__crew_name =  crew_name
        self.__crew_adress = crew_adress
        self.__crew_rank =  crew_rank
        self.__crew_department = crew_department
        self.__instructor_student_group_code = instructor_student_group_code
        self.__start = start
        self.__end = end
        self.__is_instructor = is_instructor
        
    @property
    def crew_personal_no(self):
        return self.__crew_personal_no
    
    @property
    def crew_adress(self):
        return self.__crew_adress
    
    @property
    def empno(self):
        return self.__empno 
    
    @property
    def crew_name(self):
        return self.__crew_name

    @property
    def crew_rank(self):
        return self.__crew_rank

    @property
    def crew_department(self):
        return self.__crew_department

    @property
    def instructor_student_group_code(self):
        return self.__instructor_student_group_code

    @property
    def start(self):
        return self.__start

    @property
    def end(self):
        return self.__end

    @property
    def is_instructor(self):
        return self.__is_instructor

def create():
        d = CrewAMUTrainingList()
        d.create()
        
class CrewAMUTrainingList(SASReport):
    
    def create(self):
        data = self.getData()
        self.presentOutputData(data)
        self.presentData(data)
        

    def getData(self):
        tbh = bag_handler.WindowChains()
        courseDays = []
        for course_bag in tbh.bag.report_training.training_group_leg_set(where = 'fundamental.%is_roster% and report_training.%leg_is_training_to_consider%', sort_by= ("leg.%start_date_lt%", 'report_training.%instructor_student_group_code%')):
            courseDays.append(CourseDay(course_bag))
        return courseDays
        ## W_VALUES = ['report_training.%crew_empno%',
##                     'report_training.%crew_personal_no%',
##                     'report_training.%crew_name%',
##                     'report_training.%crew_adress%',
##                     'report_training.%crew_rank%',
##                     'report_training.%crew_department%',
##                     'report_training.%instructor_student_group_code%',
##                     'report_training.%start_date_lt%',
##                     'report_training.%end_date_lt%',
##                     'report_training.%is_instructor_on_course%']
        
##         trip_expr = R.foreach(R.iter('iterators.leg_set'), *W_VALUES)

##         # Rostervalues to be used
##         # Uttrycket where= anvï¿½nds fï¿½r att fï¿½rfiltrera det du hï¿½mtar frï¿½n Rave
##         R_VALUES = []
##         R_VALUES.append(trip_expr) 
##         roster_expr = R.foreach(R.iter('report_training.training_group_leg_set',
##                                        where='fundamental.%is_roster% and report_training_fc.%leg_is_training_to_consider%', sort_by = ('report_training.%start_date_lt%', 'report_training.%instructor_student_group_code%')), *R_VALUES)

##         # Evaluate all values
##         rosters, = R.eval('default_context',roster_expr)
     
##         data = self.filterValuesForOutput(rosters)
##         return data
    
    
    

    def getHeaderRow(self):
        row=Row(border=border(top=1),font=font(SERIF,weight=BOLD))
        column1 = Column(Text('Medarbejdernum'),border=border(left=1,right=1)) 
        column2 = Column(Text('Cpr. nr.'),border=border(left=1,right=1))
        column3 = Column(Text('Navn'),border=border(left=1,right=1))
        column4 = Column(Text('Adresse'),border=border(left=1,right=1))
        column5 = Column(Text('Stilling'),border=border(left=1,right=1))
        column6 = Column(Text('Afdelingskode'),border=border(left=1,right=1))
        column7 = Column(Text('Betegnelse'),border=border(left=1,right=1))
        column8 = Column(Text('Start '),border=border(left=1,right=1))
        column9 = Column(Text('Slut '),border=border(left=1,right=1))
        column10 = Column(Text('Instrukt�r'),border=border(left=1,right=1))
        row.add(column1)
        row.add(column2)
        row.add(column3)
        row.add(column4)
        row.add(column5)
        row.add(column6)
        row.add(column7)
        row.add(column8)
        row.add(column9)
        row.add(column10)
        return row
           
    def presentData(self, data):        
        SASReport.create(self, TITLE, orientation=LANDSCAPE, usePlanningPeriod=True)
        column=Column()
        column.add(self.getHeaderRow())
        rows_per_page = 28
        newPage = False
        i = 0
        for course in data:
            if (i >= rows_per_page):
                newPage = True
                i = 0
            first = False
            i+=course.no_entries
            if newPage:
                column.newpage()
            column.add(self.presentCourse(course, newPage))
            newPage = False
        self.add(column)
        
    def getOutputHeaderRow(self):
        return "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" %(
            'Medarbejdernummer',
            'Cpr. nr.',
            'Navn',
            'Adresse',
            'Stilling ',
            'Afdelingskode',
            'Kursusbetegnelse',
            'Kursus start',
            'slut',
            'Instrukt�r')
            
        
    def presentOutputData(self, data):
        csvRows = []
        csvRows.append(self.getOutputHeaderRow())
        for course in data:
            csvRows.extend(self.presentOutputCourse(course))
        self.printCsvRows(csvRows)

    def printCsvRows(self, csvRows):
        samba_path = os.getenv('SAMBA', "/samba-share")
        mypath = "%s/%s/" %(samba_path, 'reports/Training')
        if not os.path.isdir(mypath):
            os.makedirs(mypath)
        timeStamp = str(datetime.now().date())
        reportName = "AMU_Training_Info_%s" %(timeStamp)
        myFile = mypath + reportName + '.csv'
        csvFile = open(myFile, "w")
        for row in csvRows:
            csvFile.write(row + "\n")
                    
    def presentCourse(self, course, newPage = False):
                
        col = Column()
        if newPage:
            col.add_header(self.getHeaderRow())
        row = Row(Text(course.name), border=border(bottom=1,top=1), height=15)
        col.add(row)
        for partisipant in course.partisipants:
            col.add(self.presentTrainingBlocksForCrew(partisipant, newPage))
        return col

    def presentOutputCourse(self, data):
        crewRows = []
        for partisipant in data.partisipants:
            
                crewRows.append("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" %(partisipant.empno,
                                                                  partisipant.crew_personal_no,
                                                                  partisipant.crew_name,
                                                                  partisipant.crew_adress,
                                                                  partisipant.crew_rank,
                                                                  partisipant.crew_department,
                                                                  partisipant.instructor_student_group_code,
                                                                  partisipant.start,
                                                                  partisipant.end,
                                                                  partisipant.is_instructor))
        return crewRows
                
        

    def presentTrainingBlocksForCrew(self, partisipant, firstOnPage = False):
        row = Row()
        column1 = Column(Text(partisipant.empno),border=border(left=1,right=1))
        column2 = Column(Text(partisipant.crew_personal_no),border=border(left=1,right=1))
        column3 = Column(Text(partisipant.crew_name),border=border(left=1,right=1))
        column4 = Column(Text(partisipant.crew_adress),border=border(left=1,right=1))
        column5 = Column(Text(partisipant.crew_rank),border=border(left=1,right=1))
        column6 = Column(Text(partisipant.crew_department),border=border(left=1,right=1))
        column7 = Column(Text(partisipant.instructor_student_group_code),border=border(left=1,right=1))
        column8 = Column(Text(formatDateStr(partisipant.start)),border=border(left=1,right=1))
        column9 = Column(Text(formatDateStr(partisipant.end)),border=border(left=1,right=1))
        column10 = Column(Text(partisipant.is_instructor),border=border(left=1,right=1))
        row.add(column1)
        row.add(column2)
        row.add(column3)
        row.add(column4)
        row.add(column5)
        row.add(column6)
        row.add(column7)
        row.add(column8)
        row.add(column9)
        row.add(column10)
        return row


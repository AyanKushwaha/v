#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
import carmensystems.rave.api as R
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport
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
# �ndra i klassen DataContainer s� att den inneh�ller s� m�nga 
# variabler som du beh�ver skriva ut v�rdet p� i din rapport.
# Variablernas namn �r upp till dig men m�ste matcha det du anv�nder 
# i metoden presentRow() l�ngst ned

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
    
class DataContainer(object):
    def __init__(self, id, empno, fullname,  training_blocks):
        self.__id = id
        self.__empno = empno
        self.__fullname = fullname
        self.__training_blocks = training_blocks
        
    @property
    def id(self):
        return self.__id
    
    @property
    def seniority(self):
        return self.__seniority
    
    @property
    def empno(self):
        return self.__empno 
    
    
    @property
    def fullname(self):
        return self.__fullname

    @property
    def rank(self):
        return self.__rank
        
    @property
    def ac_qual(self):
        return self.__ac_qual
    
    @property
    def base(self):
        return self.__base
    
    @property
    def special_qual(self):
        return self.__special_qual

    @property
    def blocktime(self):
        return self.__blocktime
    
    @property
    def training_blocks(self):
        return self.__training_blocks

    @property
    def no_entries(self):
        return len(self.__training_blocks)

    def no_entriesForBase(self, base):
        return sum(1 for x in self.training_blocks if x[7] == base)
        
    def hasTrainingBlockForBase(self, base):
        return self.no_entriesForBase(base) > 0
        

def create():
        d = CrewTrainingList()
        d.create()
        
class CrewTrainingList(SASReport):
    
    def create(self):
        data = self.getData()
        self.presentOutputData(data)
        self.presentData(data)
        

    def getData(self):
        
        
        W_VALUES = ['report_training_fc.%wop_training_arrival%',
                    'report_training_fc.%wop_training_arrival_flight%',
                    'report_training_fc.%wop_training_arrival_transport_to_hotel%',
                    'report_training_fc.%wop_training_departure%',
                    'report_training_fc.%wop_training_departure_flight%',
                    'report_training_fc.%wop_training_departure_transport_from_hotel%',
                    'report_training_fc.%wop_training_station%',
                    'report_training_fc.%wop_to_consider_has_training_hotel%']
        
        trip_expr = R.foreach(R.iter('report_training_fc.wop_training_set_set',
                                       where='report_training_fc.%wop_to_consider_report%'), *W_VALUES)

        # Rostervalues to be used
        # Uttrycket where= anv�nds f�r att f�rfiltrera det du h�mtar fr�n Rave
        R_VALUES = ['crew.%id%' ,'crew.%employee_number%', 'crew.%fullname%']
        R_VALUES.append(trip_expr) 
        roster_expr = R.foreach(R.iter('iterators.roster_set',
                                       where='fundamental.%is_roster% and report_training_fc.%crew_to_concider%', sort_by = ('report_training_fc.%first_training_start%', 'crew.%employee_number%')), *R_VALUES)

        # Evaluate all values
        rosters, = R.eval('default_context',roster_expr)
     
        data = self.filterValuesForOutput(rosters)
        return data
    
    
    def filterValuesForOutput(self, rosters):
        
        # Listan kommer inneh�lla objekt av typen DataContainer. 
        # Varje objekt skrivs sedan ut i rapporten som en rad
        output_list = []
      
        # I varje niv� (roster, trip...) loopar du �ver alla variabler du plockade ut
        # i R.iter( [variabel1, variabel2, ...] i metoden getData
        # L�gger du till en ny Ravevariabel d�r ska den ocks� in h�r nedan p� r�tt st�lle
        for (_, id, empno, fullname,  training_blocks) in rosters:
            entry = DataContainer(id, empno, fullname, training_blocks)
            output_list.append(entry)                                               
        return output_list

    def getHeaderRow(self):
        row=Row(border=border(top=1),font=font(SERIF,weight=BOLD))
      
        column1 = Column(Text('ID'),border=border(left=1,right=1))
        column2 = Column(Text('EMP NO'))
        column3 = Column(Text('NAME'),border=border(left=1,right=1))
        column4 = Column(Text('Arr date'),border=border(left=1,right=1))
        column5 = Column(Text('fltnr'),border=border(left=1,right=1))
        column6 = Column(Text('Transport'))
        column7 = Column(Text('Dep date'),border=border(left=1,right=1))
        column8 = Column(Text('fltnr'),border=border(left=1,right=1))
        column9 = Column(Text('Transport'))
        column10 = Column(Text('dest'),border=border(left=1,right=1))
        column11 = Column(Text('hotel need'),border=border(left=1,right=1))
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
        row.add(column11)
        return row

    def getBaseSet(self):
        airports = R.set('report_training_fc.training_airports_to_consider')
        return airports.members()

    def presentData(self, data):        
        SASReport.create(self, TITLE, orientation=PORTRAIT, usePlanningPeriod=True)
        column=Column()
        column.add(self.getHeaderRow())
        crew_per_page = 48
        newPage = False
        i = 0
        for base in self.getBaseSet():
            for entry in data:
                if (i >= crew_per_page):
                    newPage = True
                    i = 0
                first = False
                i+=entry.no_entriesForBase(base)
                if newPage:
                    column.newpage()
                if entry.hasTrainingBlockForBase(base):
                    column.add(self.presentCrew(entry, base, newPage))
                newPage = False
            newPage = True
            i = 0
        self.add(column)
        
    def getOutputHeaderRow(self):
        return "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" %(
        'ID',
        'EMPNO',
        'NAME',
        'ArrDate',
        'ArrFltnr',
        'ArrTransport',
        'DepDate',
        'DepFltnr',
        'DepTransport',
        'dest',
        'hotel need')
        
    def presentOutputData(self, data):
        csvRows = []
        csvRows.append(self.getOutputHeaderRow())
        for base in self.getBaseSet():
            for entry in data:
                if entry.hasTrainingBlockForBase(base):
                    csvRows.extend(self.presentOutputCrew(entry, base))
        self.printCsvRows(csvRows)

    def printCsvRows(self, csvRows):
        samba_path = os.getenv('SAMBA', "/samba-share")
        mypath = "%s/%s/" %(samba_path, 'reports/Training')
        if not os.path.isdir(mypath):
            os.makedirs(mypath)
        timeStamp = str(datetime.now().date())
        reportName = "Training_Info_%s" %(timeStamp)
        myFile = mypath + reportName + '.csv'
        csvFile = open(myFile, "w")
        for row in csvRows:
            csvFile.write(row + "\n")
                    
    def presentCrew(self, data, base, newPage = False):
                
        col = Column()
        if newPage:
            col.add_header(self.getHeaderRow())
        row = Row(border=border(bottom=1,top=1), height=15)
       
        # H�r plockar vi v�rden fr�n objektet DataContainer
        column1 = Column(Text(data.id),border=border(left=1,right=1))
        column2 = Column(Text(data.empno))
        column3 = Column(Text(data.fullname),border=border(left=1,right=1))
        row.add(column1)
        row.add(column2)
        row.add(column3)
        row.add(self.presentTrainingBlocksForCrew(data.training_blocks, base, newPage))
        
        col.add(row)
        return col

    def presentOutputCrew(self, data, base):
        crewRows = []
        for (_, arrival,  arrival_flight, arrival_transp_hotel, departure, departure_flight, departure__transp_hotel, station, has_hotel) in data.training_blocks:
            if station == base:
                arrTrans = "Apt-Training"
                if arrival_transp_hotel:
                    arrTrans = "Apt-Hotel"
                depTrans = "Training-Apt"
                if departure__transp_hotel:
                    depTrans = "Hotel-Apt"
                crewRows.append("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" %(data.id, data.empno, data.fullname, formatDate(arrival),  str(arrival_flight), arrTrans, formatDate(departure), str(departure_flight), depTrans, station, str(has_hotel)))
        return crewRows
                
        

    def presentTrainingBlocksForCrew(self, data, base, firstOnPage = False):
        col = Column()
        for (_, arrival,  arrival_flight, arrival_transp_hotel, departure, departure_flight, departure__transp_hotel, station, has_hotel) in data:
            if station == base:
                arrTrans = "Apt-Training"
                if arrival_transp_hotel:
                    arrTrans = "Apt-Hotel"
                depTrans = "Training-Apt"
                if departure__transp_hotel:
                    depTrans = "Hotel-Apt"
                col.add(self.presentTrainingBlocksForStation(arrival,  arrival_flight, arrTrans, departure, departure_flight, depTrans, station, has_hotel))
        return col

    
    def presentTrainingBlocksForStation(self, arrival,  arrival_flight, arrTrans, departure, departure_flight, depTrans, station, has_hotel):
        row = Row()
        column1 = Column(Text(arrival),border=border(left=1,right=1))
        column2 = Column(Text(arrival_flight),border=border(left=1,right=1))
        column3 = Column(Text(arrTrans))
        column4 = Column(Text(departure),border=border(left=1,right=1))
        column5 = Column(Text(departure_flight),border=border(left=1,right=1))
        column6 = Column(Text(depTrans))
        column7 = Column(Text(station),border=border(left=1,right=1))
        column8 = Column(Text(str(has_hotel)),border=border(left=1,right=1))
        row.add(column1)
        row.add(column2)
        row.add(column3)
        row.add(column4)
        row.add(column5)
        row.add(column6)
        row.add(column7)
        row.add(column8)
        return row


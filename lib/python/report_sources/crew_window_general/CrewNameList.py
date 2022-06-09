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

#*****************************************************************
#*****************************************************************
#*****************************************************************

TITLE = 'Crew_empno_name'

###################################################################
# Ändra i klassen DataContainer så att den innehåller så många 
# variabler som du behöver skriva ut värdet på i din rapport.
# Variablernas namn är upp till dig men måste matcha det du använder 
# i metoden presentRow() längst ned

class DataContainer(object):
    def __init__(self, id, empno, fullname, rank, ac_qual, base, special_qual):
            self.__id = id
            self.__empno = empno
            self.__fullname = fullname
            self.__rank = rank
            self.__ac_qual = ac_qual
            self.__base = base
            self.__special_qual = special_qual

    @property
    def id(self):
        return self.__id
    
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




class CrewNameList(SASReport):
    
    def create(self):
        data = self.getData()
        self.presentData(data)        
        
    def getData(self):
        
        L_VALUES = []
        leg_expr = R.foreach(R.iter('iterators.leg_set'), *L_VALUES)

        
        D_VALUES = ['duty.%start_utc%',
                    'duty.%in_pp%']
        D_VALUES.append(leg_expr)
        duty_expr = R.foreach(R.iter('iterators.duty_set'), *D_VALUES)

        # Tripvalues to be used
        T_VALUES = []
        T_VALUES.append(duty_expr)
        trip_expr = R.foreach(R.iter('iterators.trip_set'), *T_VALUES)

        # Rostervalues to be used
        # Uttrycket where= används för att förfiltrera det du hämtar från Rave
        R_VALUES = ['crew.%id%' ,'crew.%employee_number%', 'crew.%fullname%', 'crew.%rank%' , 'crg_info.%ac_quals%', 
                    'crew.%homebase%', 'crew.%special_qual_pp_start%']
        R_VALUES.append(trip_expr) 
        roster_expr = R.foreach(R.iter('iterators.roster_set',
                                       where='fundamental.%is_roster%'), *R_VALUES)

        # Evaluate all values
        rosters, = R.eval('default_context',roster_expr)
     
        data = self.filterValuesForOutput(rosters)
        return data
    
    
    def filterValuesForOutput(self, rosters):
        
        # Listan kommer innehålla objekt av typen DataContainer. 
        # Varje objekt skrivs sedan ut i rapporten som en rad
        output_list = []
      
        # I varje nivå (roster, trip...) loopar du över alla variabler du plockade ut
        # i R.iter( [variabel1, variabel2, ...] i metoden getData
        # Lägger du till en ny Ravevariabel där ska den också in här nedan på rätt ställe
        for (ix, id ,empno, fullname, rank, ac_qual, base, special_qual, my_trips) in rosters:                
           # for (iy, my_duties) in my_trips:
                                                            
                  #  for (iz, date, pp, my_legs) in my_duties:
                   #     if pp:
            #if pp:      #        for (ig ) in my_legs:
             entry = DataContainer(id, empno, fullname, rank, ac_qual, base, special_qual )
             output_list.append(entry)                                               
        return output_list
    
           
    def presentData(self, data):        
        SASReport.create(self, TITLE, orientation=PORTRAIT, usePlanningPeriod=True)
        column=Column()
        row=Row(border=border(top=1),font=font(SERIF,weight=BOLD))
      
        column1 = Column(Text('ID'),border=border(left=1,right=1))
        column2 = Column(Text('EMP NO'))
        column3 = Column(Text('NAME'),border=border(left=1,right=1))
        column4 = Column(Text('RANK'))
        column5 = Column(Text('AC QUAL',width=15),border=border(left=1,right=1))
        column6 = Column(Text('BASE'))
        column7 = Column(Text('SPECIAL QUAL',width=15),border=border(left=1,right=1))
        column8 = Column(Text('NOTES'),border=border(right=1))
        column9 = Column(Text('CHECK',width=5),border=border(right=1)) 
        row.add(column1)
        row.add(column2)
        row.add(column3)
        row.add(column4)
        row.add(column5)
        row.add(column6)
        row.add(column7)
        row.add(column8)
        row.add(column9)
        column.add_header(row)
        
        #Loopa över alla rader i listan data. Det som kommer ut är av typen DataContainer
        for entry in data:
         
            column.add(self.presentRow(entry))
            column.page0()
        self.add(column)
            
       
    def presentRow(self, data):
                
        box = Column()
        row = Row(border=border(bottom=1,top=1), height=15)
       
        # Här plockar vi värden från objektet DataContainer
        column1 = Column(Text(data.id),border=border(left=1,right=1))
        column2 = Column(Text(data.empno))
        column3 = Column(Text(data.fullname),border=border(left=1,right=1))
        column4 = Column(Text(data.rank))
        column5 = Column(Text(data.ac_qual, width=15),border=border(left=1,right=1))
        column6 = Column(Text(data.base))
        column7 = Column(Text(data.special_qual),border=border(left=1,right=1))
        column8 = Column(width=170,border=border(right=1))
        column9 = Column(width=5,border=border(right=1)) 
        row.add(column1)
        row.add(column2)
        row.add(column3)
        row.add(column4)
        row.add(column5)
        row.add(column6)
        row.add(column7)
        row.add(column8)
        row.add(column9)
        

        # En mer kompakt och direkt metod
        # row = Row(Text("%s %s %s" %(data.id, data.date, data.attrib)))
        
        box.add(row)
        return box

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

TITLE = 'Crew_F36_report'

###################################################################
# Ändra i klassen DataContainer så att den innehåller så många 
# variabler som du behöver skriva ut värdet på i din rapport.
# Variablernas namn är upp till dig men måste matcha det du använder 
# i metoden presentRow() längst ned

class DataContainer(object):
    def __init__(self, base, empno, fullname, ptfactor, f36days, f36target, f36balance1, f36balance2, f36balance3, f36available, inputf36balance, inputf36available):
            self.__base = base
            self.__empno = empno
            self.__fullname = fullname
            self.__ptfactor = ptfactor
            self.__f36days = f36days
            self.__f36target = f36target
            self.__f36balance1 = f36balance1
            self.__f36balance2 = f36balance2
            self.__f36balance3 = f36balance3
            self.__f36available = f36available
            self.__inputf36balance = inputf36balance
            self.__inputf36available = inputf36available

    @property
    def base(self):
        return self.__base
    
    @property
    def empno(self):
        return self.__empno 
        
    @property
    def fullname(self):
        return self.__fullname

    @property
    def ptfactor(self):
        return self.__ptfactor
        
    @property
    def f36days(self):
        return self.__f36days
    
    @property
    def f36target(self):
        return self.__f36target

    @property
    def f36balance1(self):
        return self.__f36balance1
    
    @property
    def f36balance2(self):
        return self.__f36balance2
    
    @property
    def f36balance3(self):
        return self.__f36balance3

    @property
    def f36available(self):
        return self.__f36available

    @property
    def inputf36balance(self):
        return self.__inputf36balance
    
    @property
    def inputf36available(self):
        return self.__inputf36available


class F36Report(SASReport):
    
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
        R_VALUES = ['crew.%homebase%', 'crew.%employee_number%', 'crew.%fullname%', 'crew.%part_time_factor%' ,
                    'freedays.%f36_days_in_pp_month%', 
                    'crew.%monthly_f36_target%',
                    'crew.%f36_balance_num%',
                    'crew.%f36_balance_den%',
                    'crew.%f36_balance_den%',
                    'studio_freedays.%availability%',
                    'crew.%input_f36_balance%',
                    'crew.%input_f36_availabledays%'
                    ]
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
        sumF36days = 0
        sumF36target = 0
        sumF36balance1 = 0.0
        sumF36balance2 = 0
        sumF36balance3 = 0.0
        sumF36available = 0
        sumInputF36balance = 0
        sumInputF36available = 0
        for (ix, base ,empno, fullname, ptfactor, f36days, f36target, f36balance1, f36balance2, f36balance3, f36available, inputf36balance, inputf36available, my_trips) in rosters:                
             entry = DataContainer(base, empno, fullname, ptfactor, f36days, f36target, f36balance1, f36balance2, f36balance3, f36available, inputf36balance, inputf36available )
             f36balance4 = 0.0
             f36balance5 = 0.0
             f36balance4 = float(f36balance1)/float(f36balance2)
             f36balance5 = f36balance4 - float(f36days)
             #print f36balance4
             #print f36balance2
             entry = DataContainer(base, empno, fullname, ptfactor, f36days, f36target, f36balance1, f36balance2, f36balance5, f36available, f36balance4, inputf36available )
             output_list.append(entry)
             if f36days == None:
                 f36days = 0
             if f36target == None:
                 f36target = 0
             if f36balance1 == None:
                 f36balance1 = 0
             if f36balance2 == None:
                 f36balance2 = 0
             #f36balance3 = 0.0                 
             if f36available == None:
                 f36available = 0
             if inputf36balance == None:
                 inputf36balance = 0
             if inputf36available == None:
                 inputf36available = 0                 
             sumF36days += f36days
             sumF36target += f36target
             #f36balance3 = float(f36balance1)
             #print f36balance3
             sumF36balance1 += f36balance3
             sumF36balance3 += f36balance5
             #print f36available
             sumF36available += f36available
             sumInputF36balance += f36balance4
             sumInputF36available += inputf36available
        entry = DataContainer('Total', '', '', '', sumF36days, sumF36target, sumF36balance1, sumF36balance2, sumF36balance3, sumF36available, sumInputF36balance, sumInputF36available )
        output_list.append(entry)
        return output_list
    
           
    def presentData(self, data):        
        SASReport.create(self, TITLE, orientation=PORTRAIT, usePlanningPeriod=True)
        column=Column()
        row=Row(border=border(top=1),font=font(SERIF,weight=BOLD))
      
        column1 = Column(Text('Base'),border=border(left=1,right=1))
        column2 = Column(Text('Emp No'))
        column3 = Column(Text('Name'),border=border(left=1,right=1))
        column4 = Column(Text('Service Grade',width=12),border=border(left=1,right=1))
        column5 = Column(Text('Assigned F36 Days',width=15),border=border(left=1,right=1))
        column6 = Column(Text('Targeted F36',width=15),border=border(left=1,right=1))
        column7 = Column(Text('Balance',width=15),border=border(left=1,right=1))        
        column8 = Column(Text('Availability',width=15),border=border(left=1,right=1))
        column9 = Column(Text('Input Balance',width=15),border=border(left=1,right=1))
        column10 = Column(Text('Input Availability',width=20),border=border(left=1,right=1)) 
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
        column.add_header(row)
        
        #Loopa över alla rader i listan data. Det som kommer ut är av typen DataContainer
        for entry in data:
         
            column.add(self.presentRow(entry))
            column.page0()
        self.add(column)
            
       
    def presentRow(self, data):
                
        dataBox = Column()
        row = Row(border=border(bottom=1,top=1), height=15)
        #    box = Column()
        
        # Här plockar vi värden från objektet DataContainer
        
        column1 = Column(Text(data.base),border=border(left=1,right=1))
        column2 = Column(Text(data.empno))
        column3 = Column(Text(data.fullname),border=border(left=1,right=1))
        column4 = Column(Text(data.ptfactor))
        column5 = Column(Text(data.f36days, width=15),border=border(left=1,right=1))
        column6 = Column(Text(data.f36target, width=15),border=border(left=1,right=1))
        column7 = Column(Text(data.f36balance3, width=15),border=border(left=1,right=1))
        column8 = Column(Text(data.f36available, width=15),border=border(left=1,right=1))
        column9 = Column(Text(data.inputf36balance, width=15),border=border(left=1,right=1))
        column10 = Column(Text(data.inputf36available, width=15),border=border(left=1,right=1))
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

        # En mer kompakt och direkt metod
        # row = Row(Text("%s %s %s" %(data.id, data.date, data.attrib)))
        dataBox.add(row)
        
        box = Column()
        box.add(Row(dataBox))
        
        return box        


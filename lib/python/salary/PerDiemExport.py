'''
Created on 24 feb 2012

@author: sven.olsson
'''

from AbsDate import AbsDate
from AbsTime import AbsTime
import carmensystems.rave.api as R
import csv
import os
import salary.PerDiem as PerDiem
import salary.api as api
import salary.conf as conf
import time


def writePerDiem(filename='exportPerDiem.csv'):
    filepath = os.path.join(api.reportDirectory(), filename)
    csvFile = open(filepath,'wb')
    writer = csv.writer(csvFile, delimiter=',')
    
    CONTEXT = 'sp_crew'
#    CONTEXT = 'default_context'

    crew_list, =  R.eval(CONTEXT, R.foreach(R.iter('iterators.roster_set'),'crew.%id%'))
    crew_list =  [crew[1] for crew in crew_list]
    pdm = PerDiem.PerDiemRosterManager(CONTEXT, crewlist=crew_list)
    writer.writerow(["Country", "Empl_no", "Rank", "Date", "Flight", "From", "To", "stop_country", "PerDiem", "PD Rate", "Total", "Currency", "Exchg rate", "Total", "Currency", "Tax", "Tax Amount", "PD Tax free", "Currency"])
    for crew in pdm.getPerDiemRosters():
        empNo = crew.empNo
        rank = crew.rank
        homeCurrency = crew.homeCurrency

        for trip in crew.trips:
            taxd_trip = trip.getTaxDeduct()
            if trip.actualPerDiem <= 0 and taxd_trip <= 0: continue
            tripTaxDeductFactor = 0.0

            for leg in trip.legs:
                currStr = round(leg.compensationPerDiem / 100, 2)
                if currStr >= 10000 and currStr == int(currStr):
                    currStr = "%7d" % int(currStr)
                else:
                    currStr = "%7.2f" % currStr
                country = trip.country
                date = AbsDate(leg.startUTC)
                flight = leg.flight
                startStation = leg.startStation
                endStation = leg.endStation
                stopCountry = leg.stopCountry
                perdiem = leg.allocatedPerDiem
                perdiemRate = round(leg.compensationPerDiem / 100, 2)
                perdiemTotal = perdiem * perdiemRate
                currency = leg.currency
                
                exchangeRate = leg.exchangeRate
                totalHomeCurrency = perdiemTotal * exchangeRate
                
                taxFactor = leg.dispTaxDeductFactor
                if not taxFactor > 0:
                    taxFactor = 0
                taxFactorStr = "%.02f" % taxFactor
                if isinstance(leg.dispTaxDeductAmount, str):
                    taxAmountStr = leg.dispTaxDeductAmount
                    taxFactorStr = "???"
                    taxFreeStr = "???"
                elif leg.dispTaxDeductAmount and leg.dispTaxDeductAmount > 0:
                    taxAmount = round(int(leg.dispTaxDeductAmount) / 100, 2)
                    taxFree = taxFactor * taxAmount

                    taxAmountStr = "%.02f" % taxAmount
                    taxFactorStr = "%.02f" % taxFactor
                    taxFreeStr = "%.02f" % taxFree
                else:
                    taxAmountStr = '0';
                    taxFreeStr = '0';
                if perdiemTotal > 0 or taxFreeStr != '0':
                    perdiemTotalStr = "%.02f" % perdiemTotal
                    totalHomeCurrencyStr = "%.02f" % totalHomeCurrency
                    
                    writer.writerow([country, empNo, rank, date, flight, startStation, endStation, stopCountry, perdiem, perdiemRate, perdiemTotalStr, currency, exchangeRate, totalHomeCurrencyStr, homeCurrency, taxFactorStr, taxAmountStr, taxFreeStr, homeCurrency])
    csvFile.close()

def PerDiemExport(askDateRange):
    sal_start0 = R.param(conf.startparam).value()
    sal_end0 = R.param(conf.endparam).value()
    
    if askDateRange:
        salStart = R.eval("report_overtime.%month_start%")[0]
        salEnd = AbsTime(salStart).addmonths(1)
        if salEnd > R.eval("fundamental.%pp_end%")[0] or salStart < R.eval("fundamental.%pp_start%")[0]:
            salStart = R.eval("fundamental.%pp_start%")[0]
            salEnd = AbsTime(salStart)
            salEnd = salEnd.addmonths(1)
        l = askSalaryPeriod(salStart, salEnd)
        if not l: return
        sal_start, sal_end = l
        print sal_start, sal_end
    else:
        sal_start = R.eval("report_overtime.%month_start%")[0]
        sal_end = R.eval("report_overtime.%month_end%")[0]

    try:
        R.param(conf.startparam).setvalue(sal_start)
        R.param(conf.endparam).setvalue(sal_end)
        timestampFormat="%Y%m%d_%H%M%S"
        writePerDiem(filename='PerDiemExport_%s.csv' % (time.strftime(timestampFormat)))
    finally:
        R.param(conf.startparam).setvalue(sal_start0)
        R.param(conf.endparam).setvalue(sal_end0)


def askSalaryPeriod(sal_start, sal_end):
    import utils.DisplayReport as display
    import Cfh
    class reportFormDatePlan(display.reportFormDate):
        def __init__(self, hdrTitle):
            display.reportFormDate.__init__(self, hdrTitle)
        def setDefaultDates(self):
            return (int(sal_start),int(sal_end))
    try: del rptForm
    except: pass
    rptForm = reportFormDatePlan('Export Per Diem')
    rptForm.show(1)
    if rptForm.loop() == Cfh.CfhOk:
        return (AbsTime(rptForm.getStartDate()), AbsTime(rptForm.getEndDate()))
    return None
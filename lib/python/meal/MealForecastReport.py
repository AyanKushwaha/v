#

#

"""This module holds Crew Meal Forecast Report functionality.
"""
import calendar

import carmensystems.rave.api as R
from AbsDate import AbsDate
from RelTime import RelTime
from carmensystems.publisher.api import *

import meal.Meal as Meal
import utils.DisplayReport as DisplayReport
from meal.MealDataClasses import SpecialMealOrderLine
from report_sources.include.SASReport import SASReport
from utils.divtools import default as d


def generateMealForecastFile(order, fileTypeSuffix, isTestReport):
    """Creates a crew meal forecast report in a file.
    
    Valid fileTypeSuffix are:
      'pdf', 'xml'
    """
    (fhdl, fileName) = Meal.newMealOutputFile('F', order.orderNumber, fileTypeSuffix, isTestReport)

    if fileTypeSuffix == 'pdf':
        DisplayReport.reportValues['order'] = order
        fhdl.close()
        generateReport('meal.MealForecastReport', fileName, PDF)

    elif fileTypeSuffix == 'xml':
        fhdl.write(createMealForecastXml(order))
        fhdl.close()        
    else:
        raise ValueError, 'Wrong fileTypeSuffix:%s'%fileTypeSuffix

    return fileName


class MealForecastReport(SASReport):
    """Implements a pdf crew meal forecast report as a SAS standard layout report.
    """

    def create(self): 
        order = DisplayReport.reportValues['order']
        
        #If beginning and end of month
        if order.fromDate.split()[2:] == (1,0,0) and\
           order.fromDate.split()[1] == order.toDate.split()[1] and\
           order.toDate.split()[1] != (order.toDate + RelTime('24:00')).split()[1]:

            interval = str(order.fromDate)[2:9]
        else:
            interval = '%s - %s' % (str(order.fromDate)[:9], str(order.toDate)[:9])

        SASReport.create(self, 'Crew Meal %sForecast'%("", "TEST")[Meal.isTestEnv],
                         runByUser=order.username,
                         orientation = LANDSCAPE,
                         showPlanData=False,
                         headerItems={'Forecast Nr: ': order.orderNumber,
                                      'Airport: ':"%s, %s" % (order.loadStation,order.airportName),
                                      'Period: ':interval,
                                      'Created: ':str(order.date)[:9]})

        supplierBox = Column(Text('Supplier',border=border(top=1, bottom=1),
                                 background='#cdcdcd',
                                 align=CENTER,
                                 colspan=2))
        supplierBox.add(Row(Text('Company:', font=font(weight=BOLD)),       Text('%s' % order.supplier.name)))
        supplierBox.add(Row(Text('Department:', font=font(weight=BOLD)),    Text('%s' % d(order.supplier.department))))
        supplierBox.add(Row(Text('Phone 1:', font=font(weight=BOLD)),       Text('%s' % d(order.supplier.phone1))))
        supplierBox.add(Row(Text('Phone 2:', font=font(weight=BOLD)),       Text('%s' % d(order.supplier.phone2))))
        supplierBox.add(Row(Text('Fax:', font=font(weight=BOLD)),           Text('%s' % d(order.supplier.fax))))

        # e-mail addresses may be separated by comma or space (", " or "," or " ").
        mail_list_str = order.supplier.email.replace(' ',',')
        mail_list_str = mail_list_str.replace(',,',',')
        mail_list = mail_list_str.split(',')
        nr_supplier_mails = len(mail_list)
        supplier_mails = Column()
        for mail in mail_list:
            supplier_mails.add(Text('%s' % d(mail)))

        supplierBox.add(Row(Text('e-mail:',font=font(weight=BOLD)), supplier_mails))

        customerBox = Column(Text('Customer',border=border(top=1, bottom=1),
                                  background='#cdcdcd',
                                  align=CENTER,
                                  colspan=2))
        customerBox.add(Row(Text('Company:', font=font(weight=BOLD)),       Text('%s' % order.customer.name)))
        customerBox.add(Row(Text('Region:', font=font(weight=BOLD)),        Text('%s' % order.customer.regionName)))
        customerBox.add(Row(Text('Department:', font=font(weight=BOLD)),    Text('%s' % d(order.customer.department))))
        customerBox.add(Row(Text('Phone 1:', font=font(weight=BOLD)),       Text('%s' % d(order.customer.phone1))))
        customerBox.add(Row(Text('Phone 2:', font=font(weight=BOLD)),       Text('%s' % d(order.customer.phone2))))
        customerBox.add(Row(Text('Fax:', font=font(weight=BOLD)),           Text('%s' % d(order.customer.fax))))

        # e-mail addresses may be separated by comma or space (", " or "," or " ").
        mail_list_str = order.customer.email.replace(' ',',')
        mail_list_str = mail_list_str.replace(',,',',')
        mail_list = mail_list_str.split(',')
        nr_customer_mails = len(mail_list)
        customer_mail = Column()
        for mail in mail_list:
            customer_mail.add(Text('%s' % d(mail)))

        
        customerBox.add(Row(Text('e-mail:', font=font(weight=BOLD)),customer_mail))

        wisInvoiceBox = Column(Text('WIS invoice information',border=border(top=1, bottom=1),
                                    background='#cdcdcd',
                                    align=CENTER,
                                    colspan=2))
        wisInvoiceBox.add(Text('%s' % order.customer.invoiceCompanyName))
        wisInvoiceBox.add(Text('%s' % order.customer.invoiceAddrName))
        wisInvoiceBox.add(Text('%s' % order.customer.invoiceAddrLine1))
        wisInvoiceBox.add(Text('%s' % order.customer.invoiceAddrLine2))
        wisInvoiceBox.add(Text('%s' % order.customer.invoiceAddrLine3))
        wisInvoiceBox.add(Text(' '))
        wisInvoiceBox.add(Text('%s' % order.customer.invoiceControlStaff))

        orderBox = Column(Row(supplierBox, Text(' '), customerBox, Text(' '), wisInvoiceBox))

        mealLoadData = {}
        for ol in order.orderLines:
            key = '%s%s%s' % (ol.loadFlight,  ol.mainCat, ol.mealCode)
            if isinstance(ol, SpecialMealOrderLine):
                key += '%s' % ol.special_meal_code.id
            if not mealLoadData.has_key(key):
                mealLoadData[key] = {}
            dateKey = '%s' % AbsDate(ol.loadDepDateLt)
            if not mealLoadData[key].has_key(dateKey):
                mealLoadData[key][dateKey] = []
            mealLoadData[key][dateKey].append(ol)
        sortedKeys = mealLoadData.keys()
        sortedKeys.sort()

        self.add(Isolate(Row(orderBox)))

        self.add(Row(' '))

        self.createHeader(order.fromDate, order.toDate)
        
        bgColor = 'ffffff'
        
        rowCount = 0
        first = True
        for key in sortedKeys:
            forecastLines = mealLoadData[key]

            if bgColor == 'ffffff':
                bgColor = 'dedede'
            else:
                bgColor = 'ffffff'

            total = 0
            dateCounter = AbsDate(order.fromDate)
            flightRow = None
            while dateCounter <= AbsDate(order.toDate):
                dateKey = '%s' % dateCounter
                if forecastLines.has_key(dateKey):
                    amount = sum([line.amount for line in forecastLines[dateKey]])
                else:
                    amount = 0
                total += amount

                if not flightRow and forecastLines.has_key(dateKey):
                    ol = forecastLines[dateKey][0]
                    flightRow = Row(
                        Text(ol.loadFlight, background='#%s' % bgColor),
                        Text('%s' % ('FD', 'CC')[ol.mainCat == 'C'], background='#%s' % bgColor),
                        Text('%s - %s' %
                             (ol.mealCode, '%s - %s' % (d(ol.mealDescription), ol.special_meal_code.id)
                             if isinstance(ol, SpecialMealOrderLine) else
                             d(ol.mealDescription)),
                             background='#%s' % bgColor),
                        Text(' ')
                    )

                    # Fill out with 0 to the first line.
                    counter = AbsDate(order.fromDate)
                    while counter < dateCounter:
                        flightRow.add(Text('%s' % 0, background='#%s' % bgColor, align=RIGHT))
                        counter = counter + RelTime(24, 00)

                if flightRow:
                    flightRow.add(Text('%s' % amount, background='#%s' % bgColor, align=RIGHT))

                dateCounter = dateCounter + RelTime(24, 00)

            if flightRow is not None:
                rowCount += 1
                if (rowCount == 30-max(nr_supplier_mails,nr_customer_mails) and first) or \
                   (rowCount == 37 and not first):
                    rowCount = 0
                    first = False
                    self.newpage()
                    self.createHeader(order.fromDate, order.toDate)
                    
                self.add(flightRow)

                flightRow.add(Text('%s' % total, background='#%s' % bgColor, align=RIGHT))

    def createHeader(self, fromdate, todate):
        days = int((todate - fromdate) / RelTime(24, 00)) + 1
        self.add(Row(
            Text('Meal Load', colspan=3, border=border(top=1, bottom=1), background='#cdcdcd', align=CENTER),
            Text(' '),
            Text('Number of meals to load on days in month', colspan=days + 1, border=border(top=1, bottom=1),
                 background='#cdcdcd', align=CENTER)
        ))

        mealSubHeadRow = Row(Column(Text('Flight', rowspan=2, valign=CENTER, align=CENTER)),
                             Column(Text('FD'), Text('CC')),
                             Column(Text('Meal', rowspan=2, valign=CENTER, align=CENTER)),
                             Text(' '),
                             font=font(weight=BOLD))

        while(fromdate <= todate):
            day = fromdate.split()[2]
            mealSubHeadRow.add(Column(Text(' '), Text('%2s' % day, align=RIGHT)))
            fromdate = fromdate + RelTime(24, 00)
        mealSubHeadRow.add(Column(Text(' '), Text('Total', align=RIGHT)))

        self.add(mealSubHeadRow)


def createMealForecastXml(order):
    """Returns a string containing a crew meal forecast report in xml.
    """

    daysInMon = calendar.monthrange(*order.fromDate.split()[:2])[1]
    orderMonthStr, = R.eval('format_time(%s, "%%b %%Y")' % order.fromDate)

    resultList = [
        '<?xml version="1.0" encoding="ISO-8859-1"?>\n',
        '<!DOCTYPE SASCrewMealForecast SYSTEM "SASCrewMealForecast.dtd" >\n',
        '<SASCrewMealForecast>\n',
        '<forecastNo>%s</forecastNo>\n' % order.orderNumber,
        '<forecastDate>%s-%02d-%02d</forecastDate>\n' % order.date.split()[:3],
        '<forecastMonth>%s</forecastMonth>\n' % orderMonthStr,
        '<supplier>\n',
        '<company>%s</company>\n' % order.supplier.name,
        '<contactDep>%s</contactDep>\n' % d(order.supplier.department),
        '<phone1>%s</phone1>\n' % d(order.supplier.phone1),
        '<phone2>%s</phone2>\n' % d(order.supplier.phone2),
        '<fax>%s</fax>\n' % d(order.supplier.fax),
        '<eMail>%s</eMail>\n' % d(order.supplier.email),
        '</supplier>\n',
        '<customer>\n',
        '<company>%s</company>\n' % order.customer.name,
        '<region>%s</region>\n' % order.customer.regionName,
        '<contactDep>%s</contactDep>\n' % d(order.customer.department),
        '<phone1>%s</phone1>\n' % d(order.customer.phone1),
        '<phone2>%s</phone2>\n' % d(order.customer.phone2),
        '<fax>%s</fax>\n' % d(order.customer.fax),
        '<eMail>%s</eMail>\n' % d(order.customer.email),
        '</customer>\n',
        '<mealForecastInfo>\n',
        '<cmLoadAirport>\n',
        '<cmStnCd>%s</cmStnCd>\n' % order.loadStation,
        '<cmAirportName>%s</cmAirportName>\n' % order.airportName,
        '</cmLoadAirport>\n']

    mealLoadData = {}
    for orderLine in order.orderLines:
        key = '%s%s%s' % (orderLine.loadFlight, orderLine.mainCat, orderLine.mealCode)
        if isinstance(orderLine, SpecialMealOrderLine):
            key += '%s' % orderLine.special_meal_code.id
        if not mealLoadData.has_key(key):
            mealLoadData[key] = {'loadFlight':orderLine.loadFlight,
                                 'mainCat':orderLine.mainCat,
                                 'mealCode':
                                     '%s - %s' % (orderLine.mealCode, orderLine.special_meal_code.id)
                                     if isinstance(orderLine, SpecialMealOrderLine) else
                                     orderLine.mealCode,
                                 'mealDescription':orderLine.mealDescription,
                                 'amountsForDays':{}
                                 }
        
        day = AbsDate(orderLine.loadDepDateLt)
        
        if day in mealLoadData[key]['amountsForDays']:
            mealLoadData[key]['amountsForDays'][day].append(orderLine.amount)
        else:
            mealLoadData[key]['amountsForDays'][day] = [orderLine.amount]

    sortedKeys = mealLoadData.keys()
    sortedKeys.sort()

    for key in sortedKeys:
        total = 0

        resultList.extend(
            ['<forecastLegInfo>\n',
             '<fltId>%s</fltId>\n' % mealLoadData[key]['loadFlight'],
             '<consumptionRank>%s</consumptionRank>\n' % ('FD', 'CC')[mealLoadData[key]['mainCat'] == 'C'],
             '<mealCode>%s</mealCode>\n' % mealLoadData[key]['mealCode'],
             '<mealDesc>%s</mealDesc>\n' % d(mealLoadData[key]['mealDescription'])])

        dateCounter = AbsTime(order.fromDate)

        while (dateCounter <= AbsTime(order.toDate)):
            amounts = mealLoadData[key]['amountsForDays'].get(dateCounter, [])
            dayTotAmount = sum(amounts)
            dayIndex = dateCounter.split()[2]
            resultList.extend(
                ['<forecastDayInfo>\n',
                 '<dayNo>%d</dayNo>\n' % dayIndex,
                 '<forecast>%s</forecast>\n' % dayTotAmount,
                 '</forecastDayInfo>\n'])
            total += dayTotAmount
            dateCounter = dateCounter + RelTime(24, 00)

        resultList.extend(
            ['<total>%s</total>\n' % total,
             '</forecastLegInfo>\n'])
        

    resultList.extend(['</mealForecastInfo>\n',
                       '</SASCrewMealForecast>'])

    return ''.join(resultList)

def _lineCmp(x, y):
    """Utility to compare two lines.
    """

    if x > y:
        return 1
    elif x == y:
        return 0
    else:
        return -1


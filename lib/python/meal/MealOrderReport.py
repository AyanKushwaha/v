#

#

"""This module holds Crew Meal Order Report functionality.
"""
import time

from carmensystems.publisher.api import *

import meal.Meal as Meal
import utils.DisplayReport as DisplayReport
from meal.MealDataClasses import SpecialMealOrderLine
from report_sources.include.SASReport import SASReport
from utils.divtools import default as d


def generateMealOrderFile(order, fileType, isTestReport):
    """Creates a crew meal order report in a file.
    
    Valid fileTypes are:
      'pdf', 'xml', 'CreateCari', 'DeleteCari', 'Telex'
    """

    if fileType == 'pdf':
        (fd, fileName) = Meal.newMealOutputFile('O', order.orderNumber, 'pdf', isTestReport)
        DisplayReport.reportValues['order'] = order
        generateReport('meal.MealOrderReport', fileName, PDF)
        return fileName

    elif fileType == 'xml':
        fileName = 'O'
        extension = 'xml'
        result = createMealOrderXml(order)

    elif fileType == 'CreateCari':
        fileName = 'MealOrderCreateCari'
        extension = 'xml'
        result = createMealOrderCreateCariXml(order)
        
    elif fileType == 'DeleteCari':
        fileName = 'MealOrderDeleteCari'
        extension = 'xml'
        result = createMealOrderDeleteCariXml(order)

    elif fileType == 'Telex':
        fileName = 'MealOrderTelex'
        extension = 'txt'
        result = createMealOrderTelex(order, isTestReport)
    else:
        raise ValueError, 'Wrong fileType:%s'%fileType

    (fhdl, fileName) = Meal.newMealOutputFile(fileName, order.orderNumber, extension, isTestReport)
    fhdl.write(result)
    fhdl.close()        
        
    return fileName

class MealOrderReport(SASReport):
    """ Implements a pdf crew meal order report as a SAS standard layout report.
    
    """

    def create(self):
        order = DisplayReport.reportValues['order']


        SASReport.create(self,
                         'Crew Meal %sOrder%s'%(("", "TEST")[Meal.isTestEnv],("", " ADD")[order.update_order]),
                         runByUser=order.username,
                         showPlanData=False,
                         headerItems={'Order Nr: ': order.orderNumber, 
                                      'Load Airport: ':"%s, %s" % (order.loadStation,order.airportName),
                                      'Meal Delivery Date: ':str(order.fromDate)[:9]})


        supplierBox = Column(Text('Supplier',border=border(top=1, bottom=1),
                                 background='#cdcdcd',
                                 align=CENTER,
                                 colspan=2))
        supplierBox.add(Row(Text('Company:', font=font(weight=BOLD)), Text('%s' % order.supplier.name)))
        supplierBox.add(Row(Text('Department:', font=font(weight=BOLD)), Text('%s' % d(order.supplier.department))))
        supplierBox.add(Row(Text('Phone 1:', font=font(weight=BOLD)), Text('%s' % d(order.supplier.phone1))))
        supplierBox.add(Row(Text('Phone 2:', font=font(weight=BOLD)), Text('%s' % d(order.supplier.phone2))))
        supplierBox.add(Row(Text('Fax:', font=font(weight=BOLD)), Text('%s' % d(order.supplier.fax))))

        # e-mail addresses may be separated by comma or space (", " or "," or " ").
        mail_list_str = order.supplier.email.replace(' ',',')
        mail_list_str = mail_list_str.replace(',,',',') 
        mail_list = mail_list_str.split(',')
        supplier_mails = Column()
        for mail in mail_list:
            supplier_mails.add(Text('%s' % d(mail)))
            
        supplierBox.add(Row(Text('e-mail:',font=font(weight=BOLD)), supplier_mails))

        # e-mail addresses may be separated by comma or space (", " or "," or " ").
        if order.supplier.sita_email:
            mail_list_str = order.supplier.sita_email.replace(' ',',')
            mail_list_str = mail_list_str.replace(',,',',') 
            mail_list = mail_list_str.split(',')
            sita_mails = Column()
            for mail in mail_list:
                sita_mails.add(Text('%s' % d(mail)))
        else:
            sita_mails = ''

        supplierBox.add(Row(Text((' ', 'Dispatch:')[order.update_order], font=font(weight=BOLD)),
                        (Text(' '), sita_mails)[order.update_order]))

        customerBox = Column(Text('Customer',border=border(top=1, bottom=1),
                                  background='#cdcdcd',
                                  align=CENTER,
                                  colspan=2))
        customerBox.add(Row(Text('Company:', font=font(weight=BOLD)), Text('%s' % order.customer.name)))
        customerBox.add(Row(Text('Region:', font=font(weight=BOLD)), Text('%s' % order.customer.regionName)))
        customerBox.add(Row(Text('Department:', font=font(weight=BOLD)), Text('%s' % d(order.customer.department))))
        customerBox.add(Row(Text('Phone 1:', font=font(weight=BOLD)), Text('%s' % d(order.customer.phone1))))
        customerBox.add(Row(Text('Phone 2:', font=font(weight=BOLD)), Text('%s' % d(order.customer.phone2))))
        customerBox.add(Row(Text('Fax:', font=font(weight=BOLD)), Text('%s' % d(order.customer.fax))))

        # e-mail addresses may be separated by comma or space (", " or "," or " ").
        mail_list_str = order.customer.email.replace(' ',',')
        mail_list_str = mail_list_str.replace(',,',',') 
        mail_list = mail_list_str.split(',')
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
        
        self.add(Isolate(Row(orderBox)))

        self.add(Row(' '))

        self.add(Row(Text('Crew Meal Load Leg',
                          colspan=4,
                          border=border(top=1, bottom=1),
                          background='#cdcdcd',
                          align=CENTER),
                     Text(' '),
                     Text('Crew Meal Consumption Leg',
                          colspan=5,
                          border=border(top=1, bottom=1),
                          background='#cdcdcd',
                          align=CENTER)))

        self.add(Row(
            Column(Text(' '), Text('Date')),
            Column(Text(' '), Text('Flight')),
            Column(Text(' '), Text('Meal')),
            Column(Text(' '), Text('Info')),
            Text(' '),
            Column(Text(' '), Text('Amount')),
            Column(Text('FD'), Text('CC')),
            Column(Text(' '), Text('Flight')),
            Column(Text('From'), Text('Station')),
            Column(Text('To'), Text('Station')),
            font=font(weight=BOLD)))

        bgColor = 'ffffff'
        orderLines = order.orderLines
        orderLines.sort()
        for orderLine in orderLines:
            info = orderLine.special_meal_code.id if isinstance(orderLine, SpecialMealOrderLine) else ''
            if bgColor == 'ffffff':
                bgColor = 'dedede'
            else:
                bgColor = 'ffffff'
            self.add(Row(
                Text('%s-%02d-%02d' % orderLine.loadDepDateLt.split()[:3], background='#%s' % bgColor),
                Text(orderLine.loadFlight, background='#%s' % bgColor),
                Text('%s - %s' % (orderLine.mealCode, d(orderLine.mealDescription)), background='#%s' % bgColor),
                Text(info, background='#%s' % bgColor),
                Text(' '),
                Text('%s' % orderLine.amount, background='#%s' % bgColor),
                Text('%s' % ('FD','CC')[orderLine.mainCat == 'C'], background='#%s' % bgColor),
                Text(orderLine.consFlight, background='#%s' % bgColor),
                Text('%s' % orderLine.consDepAirport, background='#%s' % bgColor),
                Text('%s' % orderLine.consArrAirport, background='#%s' % bgColor)
            ))
            self.page0()




def createMealOrderXml(order):
    """Returns a string containing a crew meal order report in xml.
    """
    
    resultList = [
        '<?xml version="1.0" encoding="ISO-8859-1"?>\n',
        '<!DOCTYPE SASCrewMealOrder SYSTEM "SASCrewMealOrder.dtd" >\n',
        '<SASCrewMealOrder>\n',
        '<orderNo>%s</orderNo>\n' % order.orderNumber,
        '<orderDate>%s-%02d-%02d</orderDate>\n' % order.date.split()[:3],
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
        '<crewMealInfo>\n',
        '<cmLoadAirport>\n',
        '<cmStnCd>%s</cmStnCd>\n' % order.loadStation,
        '<cmAirportName>%s</cmAirportName>\n' % order.airportName,
        '</cmLoadAirport>\n']

    for orderLine in order.orderLines:
        resultList.extend(
            ['<cmLegInfo>\n',
             '<cmLoad>\n',
             '<fltDate>%s-%02d-%02d</fltDate>\n' % orderLine.loadDate.split()[:3],
             '<fltId>%s</fltId>\n' % orderLine.loadFlight,
             '<mealCode>%s</mealCode>\n' % getMealCodeText(orderLine, orderLine.mealCode),
             '<mealDesc>%s </mealDesc>\n' % d(orderLine.mealDescription),
             '<mealNo>%s</mealNo>\n' % orderLine.amount,
             '</cmLoad>\n',
             '<cmConsumption>\n',
             '<consumptionRank>%s</consumptionRank>\n' % ('FD', 'CC')[orderLine.mainCat == 'C'],
             '<fltId>%s</fltId>\n' % orderLine.consFlight,
             '<stnFrom>%s</stnFrom>\n' % orderLine.consDepAirport,
             '<stnTo>%s</stnTo>\n' % orderLine.consArrAirport,
             '</cmConsumption>\n',
             '</cmLegInfo>\n'])

    resultList.extend(['</crewMealInfo>\n', '</SASCrewMealOrder>'])

    return ''.join(resultList)

def getMealCodeText(orderLine, defaultText):
    return ('%s - %s' % (defaultText, orderLine.special_meal_code.id)
     if isinstance(orderLine, SpecialMealOrderLine) else
            defaultText)

def createMealOrderCreateCariXml(order):
    """Returns a string containing a MealOrderCreateCari report in xml.
    """

    resultList = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<crewMessage xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="crewMealOrderCreate.xsd" version="1.00">\n',
        '<messageName>CrewMealOrderCreate</messageName>\n',
        '<messageBody>\n',
        '<crewMealOrderCreate version="1.00">\n',
        '<carrier>%s</carrier>\n' % order.customer.name,
        '<orderNumber>%s</orderNumber>\n' % order.orderNumber,
        '<toDate>%s-%02d-%02d</toDate>\n' % order.toDate.split()[:3],
        '<orderLines>\n']

    for ix, orderLine in enumerate(order.orderLines, 1):
        resultList.extend(
            ['<orderLine>\n',
             '<lineNumber>%s</lineNumber>\n' % ix,
             '<loadFlight>\n',
             '<flightId>%s</flightId>\n' % orderLine.loadFlight,
             '<stdDate>%s-%02d-%02d</stdDate>\n' % orderLine.loadDate.split()[:3],
             '<depStation>%s</depStation>\n' % orderLine.loadDepAirport,
             '</loadFlight>\n',
             '<consumptionFlight>\n',
             '<flightId>%s</flightId>\n' % orderLine.consFlight,
             '<stdDate>%s-%02d-%02d</stdDate>\n' % orderLine.consDate.split()[:3],
             '<depStation>%s</depStation>\n' % orderLine.consDepAirport,
             '</consumptionFlight>\n',
             '<mealTitle>%s</mealTitle>\n' % getMealCodeText(orderLine, orderLine.mealDescription),
             '<cariText></cariText>\n',
             '<mainRank>%s</mainRank>\n' % ('F', 'A')[(orderLine.mainCat == 'C')],
             '<noOfMealsToOrder>%s</noOfMealsToOrder>\n' % orderLine.amount,
             '</orderLine>\n'])
            
    resultList.extend(['</orderLines>\n',
                       '</crewMealOrderCreate>\n',
                       '</messageBody>\n',
                       '</crewMessage>'])

    return ''.join(resultList)

def createMealOrderDeleteCariXml(order):
    """Returns a string containing a MealOrderDeleteCari report in xml.
    """
    resultList = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<crewMessage xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="crewMealOrderDelete.xsd" version="1.00">\n',
        '<messageName>CrewMealOrderDelete</messageName>\n',
        '<messageBody>\n',
        '<crewMealOrderDelete version="1.00">\n',
        '<orderNumber>%s</orderNumber>\n' % order.orderNumber,
        '</crewMealOrderDelete>\n',
        '</messageBody>\n',
        '</crewMessage>']

    return ''.join(resultList)


def createMealOrderTelex(order, isTestReport):
    """ Returns a string containing the Telex mail body
    """

    # FIXME: The mail format is implemented from the example in the spec. Is it correct?
    #QX CPHHRXH                                                                      Telex type & receiver (supplier attribute)
    #.CPHPGSK 141312 JUL10                                                           Sender, date, time(local), month & year.
    #SAS Crew Meal Order ADD                                                         Text agreed upon by Gategourmet.
    #SK Danmark Crew Meal TESTOrder ADD, 99999, 2010-07-14, CPH, Gate Gourmet CPH    Order mail subject.
    #-SK503 2010-06-18 B-Hot breakfast 2 FD SK503 CPH LHR                            PDF detail line.
    #-SK503 2010-06-18 H-Hot meal 5 CC SK504 LHR CPH                                 Do
    #-SK503 2010-06-18 S-Sandwich 2 FD SK504 LHR CPH                                 do
    #END                                                                             End of telex text.

    run_time = time.strptime("%d %d %d %d %d" % (order.date.split()), "%Y %m %d %H %M" )
    
    lines = ['QX %sHRXH\n' % (order.supplier.station)]
    lines.append('.%sPGSK %s\n' % (order.supplier.station, time.strftime("%d%H%M %b%y", run_time)))
    lines.append('SAS Crew Meal Order ADD\n')
    lines.append("%s %s Crew Meal %sOrder ADD " % (order.customer.name, order.customer.regionFullName, ("", "TEST")[isTestReport]) + \
                 "%s, %s, " % (order.update_order_flight, order.orderNumber) + \
                 "%s-%02d-%02d, " % (order.date.split()[:3]) + \
                 "%s, %s\n" % (order.loadStation, order.supplier.name))

    for orderLine in order.orderLines:
        line = "-%s " % (orderLine.loadFlight.replace(' ','')) + \
               "%s-%02d-%02d " % orderLine.loadDate.split()[:3] + \
               "%s-%s %s " % (orderLine.mealCode, orderLine.mealDescription, orderLine.amount) + \
               "%s " % ('FD', 'CC')[orderLine.mainCat == 'C'] + \
               "%s %s %s\n" % (orderLine.consFlight.replace(' ',''), orderLine.consDepAirport, orderLine.consArrAirport)
        
        lines.append(line)
        
    lines.append("END\n")

    return ''.join(lines)


#

#
"""
Crew Meal Report server script.

This modul is intended to be run by a reportserver.

It is part of a client server solution:
client:     MealOrderFormHandler
middelware: DigJobQueue  -> Dig 
server:     report server -> CrewMealOrderReport -> MealOrderRun
"""

import logging
import os
import sys

import carmensystems.rave.api as R
from AbsTime import *
from RelTime import RelTime
import datetime

import meal.Meal as Meal
import meal.MealForecastReport as MealForecastReport
import meal.MealOrderData as MealOrderData
import meal.MealOrderReport as MealOrderReport
from meal.MealExceptions import change_exception_args, AccumulatedExceptions, DataError, InParamError
from tm import TM

log = logging.getLogger('MealOrderRun')

######################################################

def _processReports(mealOrdersIterator, update = False, create=False, cancel=False, forceAllTypes=False, send=False, mailAddrs=[]):
    """ Processes orders. Returns:dict{filenames:receivers, ...}
        mealOrdersIterator is an iterator/list of MealOrder() instances.
    
    """
    typeExtension = {'pdf': 'application/pdf', 'xml': 'text/xml', 'Telex': 'text/plain'}
    resultList = []

    for order in mealOrdersIterator:
        typesToRun = []

        try:

            orderNo = int(order.orderNumber)
            print("### DEBUG ### SKCMS-1169: _processReports for order %s" % (orderNo))
            if order.forecast:
                mealReport_FuncRef = MealForecastReport.generateMealForecastFile
            else:
                mealReport_FuncRef = MealOrderReport.generateMealOrderFile

            if cancel and update:
                raise InParamError("Update orders may not be cancelled, order %u is an update order" % orderNo)
            elif cancel and order.sent:
                create = False
                send = True
                if order.supplier.pdf:
                    typesToRun.append('pdf')
                if order.supplier.xml:
                    typesToRun.append('xml')
                if not order.forecast:
                    typesToRun.append('DeleteCari')
            elif cancel and not order.sent:
                # Orders that haven't been sent to supplier will be deleted silently without
                # any mails to suppliers
                create = False
                send = False
            elif forceAllTypes:
                create = True
                send = False
                if order.forecast:
                    typesToRun = ['pdf', 'xml']
                else:
                    typesToRun = ['pdf', 'xml', 'CreateCari', 'DeleteCari']
            elif create:
                if order.supplier.pdf:
                    typesToRun.append('pdf')
                if order.supplier.xml:
                    typesToRun.append('xml')
                if update or not order.forecast:
                    typesToRun.append('CreateCari')
                if update and not typesToRun:  # Only append Telex if no other types have been added
                    typesToRun.append('Telex')
            elif send:
                if order.supplier.pdf:
                    typesToRun.append('pdf')
                if order.supplier.xml:
                    typesToRun.append('xml')
                if (update or not order.forecast) and not order.sent and not mailAddrs:
                    typesToRun.append('CreateCari')
                if update and not order.sent and not mailAddrs and not typesToRun:  # Telex only if typesToRun is empty
                    typesToRun.append('Telex')
            else:
                raise ValueError, 'Nothing to do. No command given in inparams:\n' +\
                                  'create=%s, cancel=%s, forceAllTypes=%s, send=%s' %\
                                  (create, cancel, forceAllTypes, send)

            if not forceAllTypes:
                if not (order.supplier.pdf or order.supplier.xml):
                    raise ValueError, "Supplier %s has no pdf or xml preference" % order.supplier.supplierId

            if len(mailAddrs):
                sendToList = mailAddrs
                sendToListTelex = mailAddrs
            else:
                sendToList = [order.supplier.email, order.customer.email]
                sendToListTelex = [order.supplier.sita_email]
            subject = _makeMailSubject(order, cancel)

            resultsThisOrder = []
            for reportType in typesToRun:
                try:
                    if create:
                        fileName = mealReport_FuncRef(order, reportType, forceAllTypes or Meal.isTestEnv)
                        _writeFileName(order, reportType, fileName)
                    elif reportType == 'DeleteCari':
                        fileName = mealReport_FuncRef(order, reportType, forceAllTypes or Meal.isTestEnv)
                    else:
                        fileName = _readFileName(order, reportType)

                    if send and not (update and not order.update_order):
                        if (order.supplier.pdf and reportType == 'pdf') or (order.supplier.xml and reportType == 'xml'):
                            if not fileName:
                                raise DataError, "Order %s has empty %s file column, required by supplier %s." %\
                                                 (orderNo, reportType, order.supplier.supplierId)
                            if not os.path.exists(fileName):
                                raise DataError, "Cannot find %s file for order %s:\n%s" %\
                                                 (reportType, orderNo, fileName)

                        if reportType in ('CreateCari', 'DeleteCari'):
                            resultsThisOrder.append(_makeReportDict(fileName,
                                                                    'text/xml',
                                                                    reportType))
                        elif reportType in ("Telex"):
                            resultsThisOrder.append(_makeReportDict(fileName,
                                                                    typeExtension[reportType],
                                                                    'telex',
                                                                    sendToListTelex,
                                                                    subject))
                        elif reportType in "xml" and update:
                            # The XML report shall not be sent for updates
                            pass
                        else:
                            resultsThisOrder.append(_makeReportDict(fileName,
                                                                    typeExtension[reportType],
                                                                    'mail',
                                                                    sendToList,
                                                                    subject))
                except AccumulatedExceptions, e:
                    change_exception_args(e,
                                          'MealOrderRun.py - Could not create/send report for order %s. %s' % (
                                           orderNo, e.args[0]))
                    log.error(str(e))
                    break
            else:
                #Only executed if no exception
                if cancel:
                    if order.forecast or not order.sent:
                        for order_line_entity in order.entity.referers("meal_order_line", "order"):
                            order_line_entity.remove()
                        order.entity.remove()
                    else:
                        order.entity.cancelled = True
                if send and not mailAddrs and not (update and not order.update_order):
                    order.entity.sent = True

                resultList += resultsThisOrder

        except Exception, e:
            change_exception_args(e, 'MealOrderRun.py - Could not process order %s. %s' % (orderNo, e.args[0]))
            log.error(str(e))
            AccumulatedExceptions().register(e)
            continue

    return resultList

def _writeFileName(order, reportType, fileName):
    """Helper to write a file name in matching column for the reportType.
    """
    if reportType == 'pdf':
        order.entity.pdf_file = fileName
    elif reportType == 'xml':
        order.entity.xml_file = fileName
    elif reportType == 'CreateCari':
        order.entity.cari_create_file = fileName
    elif reportType == 'DeleteCari':
        pass # The DeleteCari file path is not stored in the database
    elif reportType == 'Telex':
        pass # The telex file path it not stored in the database
    else:
        raise InParamError("Invalid report type")

def _readFileName(order, reportType):
    """Helper to get file name from matching column for the reportType.
    """
    if reportType == 'pdf':
        fileName = order.entity.pdf_file
    elif reportType == 'xml':
        fileName = order.entity.xml_file
    elif reportType == 'CreateCari':
        fileName = order.entity.cari_create_file
    else:
        raise InParamError("Invalid report type")
        
    # If the file does not exists, it may be that the file was created in a previous
    # version and that the CARMDATA has been moved in the current version. Let's try 
    # if the file can be found in the current CARMDATA directory.
    if not os.path.exists(fileName):
        
        exportDir = Meal.getExportDir()
        backup_fileName = os.path.join(exportDir, os.path.basename(fileName))
        
        if os.path.exists(backup_fileName) and os.path.isfile(backup_fileName):
            fileName = backup_fileName

    return fileName

def _makeReportDict(file, type, protocol, addr=None, subject=None):
    """ This function makes a report dict that it handed over to
        the next step in the dig channel
    """
    destList = []
    if protocol == "mail":
        attachment = os.path.split(file)[-1]
        for a in addr:
            destList.append(("mail",{'to': a,
                                     'subject': subject.decode('latin-1'),
                                     'attachmentName': attachment,
                                     'body' : "This is an automatically generated mail from Crew Meal. Please, do NOT reply to this mail!"}))    
    elif protocol == "telex":
        for a in addr:
            destList.append(("mail",{'to': a,
                                     'subject': subject}))        
    else:
        # Protocol represents logical report name, destination
        # to be specified by dig channel
        destList.append(("CREW_MEAL", {'subtype':protocol}))
        
    reportDict = {'content-type': type,
                  'content-location': file,
                  'destination': destList}
    
    return reportDict

def _makeMailSubject(order, cancel=False):
    """ Creates a string with the mail subject
     
    """

    if order.update_order:
        type = "Order"
        interval = "%s-%02d-%02d" % order.fromDate.split()[:3] 
    elif order.forecast:
        type = "Forecast"
        
        #If whole month
        if order.fromDate.split()[2:] == (1,0,0) and\
           order.fromDate.split()[1] == order.toDate.split()[1] and\
           order.toDate.split()[1] != (order.toDate + RelTime('24:00')).split()[1]:
            interval = "%s-%02d"%(order.fromDate.split())[:2]
        else:
            interval = "%s-%02d-%02d to %s-%02d-%02d" % \
                     (order.fromDate.split()[:3] + order.toDate.split()[:3])
    else:
        type = "Order"
        interval = "%s-%02d-%02d" % order.fromDate.split()[:3]

    cancelled = ("", " cancelled")[cancel]
    test = ("", "TEST")[Meal.isTestEnv]
        
    subject = "%s %s Crew Meal %s%s%s%s%s, %s, %s, %s, %s" % \
            (order.customer.name,
             order.customer.regionFullName,
             test,
             type,
             ("", " ADD")[order.update_order],
             ("", " %s" % (order.update_order_flight))[order.update_order],
             cancelled,
             order.orderNumber,
             interval,
             order.loadStation,
             order.supplier.name)
    return subject


def mealOrderRun(fromDate=None, toDate=None, forecast=False, weekly=False, send=False, loadAirport=False,
                 region=False, runByUser=None, reportServer=True):
    """Creates meal orders & lines, runs reports and sends mails(via dig).
    """
    resultList = []
    # Table manager might be locked when report server given flag reload.
    if TM.islocked():
        TM.unlock()

    try:
        # Get needed dates in one rave lookup
        meal_rundate, loaded_data_period_start, loaded_data_period_end, now = \
                    R.eval('report_meal.%meal_rundate%',
                           'fundamental.%loaded_data_period_start%',
                           'fundamental.%loaded_data_period_end%',
                           'fundamental.%now%')
        
    
        if fromDate:
            fromDate = AbsTime(fromDate).day_floor()
        else:
            fromDate = meal_rundate
            log.info("mealOrderRun RAVEDATE: %s" % fromDate)
            #fromDate = AbsTime(int(fromDate))

            if weekly:
                fromDate = fromDate.adddays(4).day_floor()
            elif forecast:
		# Forecast is run 20. in month, for the next month
                fromDate = fromDate.month_ceil()
            else:
                fromDate = fromDate.day_floor()
                
        if toDate:
            toDate = AbsTime(toDate).day_ceil()
        else:
            if weekly:
                toDate = fromDate.adddays(6).day_ceil()
            elif forecast:
                toDate = fromDate.addmonths(1, PREV_VALID_DAY) - RelTime('24:00')
            else:
                toDate = fromDate.day_ceil()
    
        if fromDate < loaded_data_period_start or \
           (forecast and toDate > loaded_data_period_end):
            raise InParamError, \
                  "The %s is outside the report servers loaded data period:%s" % (
                      ("order date:%s"%fromDate, "forcast interval:(%s - %s)"%(fromDate, toDate))[forecast],
                      "(%s - %s)"%(loaded_data_period_start, loaded_data_period_end))
            
    
        log.info('Using from:%s to:%s' % (fromDate.split(), toDate.split()))
        
        OrderTables = MealOrderData.OrderTablesManager()
        
        mealOrderList = OrderTables.createOrders(fromDate=fromDate,
                                                toDate=toDate, 
                                                forecast=forecast, 
                                                reportServer=reportServer,
                                                station=loadAirport,
                                                region=region,
                                                runByUser=runByUser,
                                                runDate=now)

        resultList = _processReports(mealOrdersIterator=mealOrderList,
                                     create=True,
                                     send=send)
        
    except AccumulatedExceptions, e:
        change_exception_args(e,
                              'MealOrderRun.py - Could not create new %s. %s'% (
                              ('order', 'forecast')[forecast], e.args[0]))
        log.error(str(e))
        
    # Add accumulated errors to let dig notify admins 
    resultList.extend(AccumulatedExceptions().makeDigReturnList())
    return resultList

def processMealOrderList(mealOrderList=[], forecast=False, cancel=False,
                         testAllTypes=False, send=False, mailAddrs=[]):
    """Processes all orders in mealOrderList according to inparams.
    """

    # searchStr example:'(&(forecast=true)(|((order_number=27))(order_number=23)))'
    searchStr = "(&(forecast=%s)(|(order_number="% ('false', 'true')[forecast] +\
                ")(order_number=".join(mealOrderList) +\
                ")))"
                
    # Table manager might be locked when report server given flag reload.
    if TM.islocked():
        TM.unlock()

    orders = []
    
    for order_entity in TM.meal_order.search(searchStr):
        order_handler = MealOrderData.MealOrderHandler(order_entity.order_number, forecast)        
        orders.append(order_handler.getMealOrder())

    resultList = _processReports(mealOrdersIterator=orders,
                                 create=False,
                                 cancel=cancel,
                                 send=send,
                                 forceAllTypes=testAllTypes,
                                 mailAddrs=mailAddrs)
    
    # Add accumulated errors to let dig notify admins 
    resultList.extend(AccumulatedExceptions().makeDigReturnList())

    return resultList


def mealOrderUpdate(reportServer=False, runByUser=None, send = False, loadAirport=False,
                    region=False, updateTime = False):
    """ Evaluates the meal shortage. Complementary orders created if shortages
        are found.
    """

    # Table manager might be locked when report server given flag reload.
    if TM.islocked():
        TM.unlock()
        
    try:
        
        # Get needed dates in one rave lookup
        update_horizon, offset, now = R.eval('report_meal.%meal_order_update_horizon%',
                                             'report_meal.%meal_order_update_offset%',
                                             'fundamental.%now%')

        OrderTables = MealOrderData.OrderTablesManager()
        
        # If the caller supplied an update time - use it otherwise use the current time
        # time
        if updateTime:
            fromDate = AbsTime(updateTime)
            toDate = AbsTime(updateTime) + offset #SKCMS-1845: time window change to correspond to the 15 minute start interval of the update job.
        else:
            fromDate = now + update_horizon
            toDate = now + update_horizon + offset  #SKCMS-1845: time window change to correspond to the 15 minute start interval of the update job.
        
        # Finds the shortages and creates the update orders. The resulting list is the 
        # database order entries.
        print("### DEBUG ### SKCMS-1169: mealOrderUpdate")
        print("### DEBUG ### SKCMS-1169: createOrders called with parameter set: fromDate=%s, toDate=%s, reportServer=%s, station=%s, region=%s, update=True, runByUser=%s, runDate=%s" % (fromDate, toDate, reportServer, loadAirport, region, runByUser, now))
        mealOrderList = OrderTables.createOrders(fromDate=fromDate, 
                                                 toDate = toDate, 
                                                 reportServer = reportServer,
                                                 station=loadAirport,
                                                 region=region,
                                                 update = True,
                                                 runByUser=runByUser, 
                                                 runDate=now)
            
        # This function takes the list and creates reports/e-mails from data base entries.
        # The resultList contains entries describing the reports and outgoing e-mails
        resultList = _processReports(mealOrdersIterator=mealOrderList,
                                     update=True,
                                     create=True,
                                     send=send)
    
        # Add accumulated errors to let dig notify admins 
        resultList.extend(AccumulatedExceptions().makeDigReturnList())
                
        return resultList
            
    except AccumulatedExceptions, e:
        change_exception_args(e,
                              'MealOrderRun.py - Could not create update order %s'% (e.args[0]))
        log.error(str(e))
        return []


def sendMealUpdateOrderList(mealOrderList=[], mailAddrs=[]):
    """Processes all orders in mealOrderList according to inparams.
    """

    # searchStr example:'(|(order_update_num=27)(order_update_num=23))'
    
    searchStr = "(|(order_update_num=" + \
                ")(order_update_num=".join(mealOrderList) + \
                "))"
                
    # Table manager might be locked when report server given flag reload.
    if TM.islocked():
        TM.unlock()

    orders = []
    
    for order_entity in TM.meal_order_update.search(searchStr):
        order_handler = MealOrderData.MealUpdateOrderHandler(order_entity.order_update_num, order_entity.meal_order)        
        orders.append(order_handler.getMealOrder())

    resultList = _processReports(mealOrdersIterator=orders,
                                 update=True,
                                 create=False,
                                 cancel=False,
                                 forceAllTypes=False,
                                 send=True,
                                 mailAddrs=mailAddrs)
    
    # Add accumulated errors to let dig notify admins 
    resultList.extend(AccumulatedExceptions().makeDigReturnList())

    return resultList

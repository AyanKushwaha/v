#

#
"""
Crew Meal Order Form Handler

This module is intended to be the back end of a Wave form launched directly on Mirador & Dave.
Together they are the client of a client server solution:

client:     MealOrderFormHandler
middelware: DigJobQueue  -> Dig 
server:     report server -> rs_CrewMealOrderReport -> MealOrderRun

"""
import traceback

import os
import getpass

from modelserver import TableManager
from modelserver import DateColumn
from modelserver import TimeColumn
from modelserver import StringColumn
from modelserver import RefColumn
from modelserver import BoolColumn
from modelserver import IntColumn
import carmensystems.services.dispatcher as csd
from AbsDate import AbsDate
from AbsTime import *

from tm import TM
from utils.TimeServerUtils import TimeServerUtils
from utils.data_error_log import log
from dig.DigJobQueue import DigJobQueue

import logging
log = logging.getLogger('MealOrderFormHandler')

#TM = None #Wait getting Tablemanager instance to when initializing class
############################ Temporary tables used for the form ################
class TmpTable:
    """Base class for temporary tables
    """
    def __init__(self):
        """Creates or opens a table with the name in the name attribute
        """
        self.tm = TableManager.instance()
        try:
            self.table = self.tm.table(self.name)
            self.clearTable()
        except:
            self.tm.createTable(self.name, self.keys, self.cols)
            self.table = self.tm.table(self.name)

    def clearTable(self):
        """Removes all rows
        """
        self.table.removeAll()

    def createRow(self):
        """Creates a default row
        """
        return self.table.create(self.key)

    def getRow(self):
        """Returns the default row
        """
        return self.table[self.key]

class ParamTable(TmpTable):
    """Parameters for searching or creating orders/forecasts
    """
    name = 'tmp_meal_order_param'
    keys = [StringColumn('id', 'Id')]
    cols = [DateColumn('from_date', 'From Date'),
            DateColumn('to_date', 'To Date'),
            BoolColumn('one_station', 'One Station'),
            StringColumn('load_station', 'Load Station'),
            RefColumn('region', 'meal_customer', 'Region'),
            StringColumn('mail', 'Override Mail Addresses')]
    key=('param_row',)

    def createRow(self):
        """Overrides createRow and sets some default values.
        """
        row = TmpTable.createRow(self)
        row.one_station = False
        row.load_station = ''
        return row

class FilterTable(TmpTable):
    """Filter for filtering tables
    """
    name = 'tmp_filter_month'
    keys = [IntColumn('id', 'Id')]
    cols = [DateColumn('filter_date', 'Date in used Month for filter base')]
    key=(1,)

    def init(self):
        row = TmpTable.createRow(self)
        timeSrv = TimeServerUtils(useSystemTimeIfNoConnection = True)
        now_tup = timeSrv.getTime().timetuple()
        row.filter_date = AbsTime(*now_tup[:5])


class NrSelectedInMealTable(TmpTable):
    """Holds how many rows that are selected for table
    """
    name = 'tmp_nr_selected'
    keys = [StringColumn('table_name', 'Table Name')]
    cols = [IntColumn('nr_selected_rows', 'Number of Selected Rows')]
    key= ('tableId_row',)

class MessageTable(TmpTable):
    """Message used for user dialogs
    
    Note that only row 0 is used, i.e. overwritten for each new message.
    """
    name = 'tmp_meal_message'
    keys = [IntColumn('id', 'Id')]
    cols = [StringColumn('message', 'Message', 1024)]
    key= (1,)

    def clearDefaultRow(self):
        """Overwites message with empty string.
        """
        row = self.getRow()
        row.message = ""

class MealOrderTable(TmpTable):
    """Meal Order search results
    """
    name = 'tmp_meal_order'
    keys = [StringColumn('order_number', 'Order Number'),
            BoolColumn('forecast', 'Forecast')]
    cols = [DateColumn('order_date', 'Order Date'),
            StringColumn('load_station', 'Load Airport'),
            StringColumn('customer', 'Customer'),
            StringColumn('supplier', 'Supplier'),
            DateColumn('from_date', 'From Date'),
            DateColumn('to_date', 'To Date'),
            BoolColumn('select', 'Select'),
            BoolColumn('sent', 'Sent'),
            StringColumn('username', 'User Name'),
            StringColumn('pdf_doc', 'pdf'),
            StringColumn('xml_doc', 'xml')]
    key= ('order_row',)

    def createRow(self, key):
        """Method that overrides method in base class
    
        Takes a key as argument
        """
        return self.table.create(key)

class MealUpdateOrderTable(TmpTable):
    """Meal updates order search results
    """
    name = 'tmp_meal_update'
    keys = [StringColumn('update_order_num', 'Order Number')]
    cols = [StringColumn('load_station', 'Load Airport'),
            StringColumn('supplier', 'Supplier'),
            StringColumn('customer', 'Customer'),
            DateColumn('from_date', 'From Date'),
            BoolColumn('select', 'Select'),
            StringColumn('pdf_doc', 'pdf'),
            StringColumn('xml_doc', 'xml'),
            StringColumn('username', 'User Name'),
            TimeColumn('order_time', 'Order Time')]
    
    key= ('order_row',)

    def createRow(self, key):
        """Method that overrides method in base class
    
        Takes a key as argument
        """
        return self.table.create(key)


class MealForecastTable(MealOrderTable):
    """Meal Forecast search results
    """
    name = 'tmp_meal_forecast'

class MealOrderLinesTable(TmpTable):
    """Meal Order search results
    """
    name = 'tmp_meal_order_lines'
    keys = [IntColumn('index', 'Index')]
    cols = [StringColumn("load_flight", "Load flight"),
            StringColumn("cons_flight", "Cons flight"),
            StringColumn("maincat", "Category"),
            StringColumn("meal_code", "Code"),
            StringColumn("amount", "Amount")]
    key= (1,)

    def createRow(self, key):
        """Method that overrides method in base class
    
        Takes a key as argument
        """
        return self.table.create(key)

class MealOrderUpdateLinesTable(TmpTable):
    """Meal Order search results
    """
    name = 'tmp_meal_order_update_lines'
    keys = [IntColumn('index', 'Index')]
    cols = [StringColumn("load_flight", "Load flight"),
            StringColumn("cons_flight", "Cons flight"),
            StringColumn("maincat", "Category"),
            StringColumn("meal_code", "Code"),
            StringColumn("amount", "Amount")]
    key= (1,)

    def createRow(self, key):
        """Method that overrides method in base class
    
        Takes a key as argument
        """
        return self.table.create(key)



############################ The handler for the form ##########################

class MealOrderFormHandler:
    """Main Form handler
    
    Initiates form, methods and temporary tables
    """

    def __init__(self):
        """Initiates methods and temporary tables used by the form
        """
        self.DJQ = DigJobQueue(channel='meal',
                               submitter = 'crew_meal_manual_job',
                               reportName = 'report_sources.report_server.rs_CrewMealOrderReport')
        
        self.paramTable = ParamTable()
        self.paramTable.createRow()
        self.filterTable = FilterTable()
        self.filterTable.init()
        self.messageTable = MessageTable()
        self.messageTable.createRow()
        self.orderTable = MealOrderTable()
        self.forecastTable = MealForecastTable()
        self.updateTable = MealUpdateOrderTable()
        self.orderLineTable = MealOrderLinesTable()
        self.orderUpdateLineTable = MealOrderUpdateLinesTable()
        self.applyTablesfilter()
        self.nrSelectedTable = NrSelectedInMealTable()
        self.saveNrSelectedRows('dummy','MealOrderReport')
        self.saveNrSelectedRows('dummy','MealForecastReport')
        self.saveNrSelectedRows('dummy','MealUpdateReport')

        self.checkOrders = False
        self.checkForecasts = False
        self.checkUpdates = False


        csd.registerService(
            self.saveNrSelectedRows,
            "carmensystems.mirador.tablemanager.save_nr_selected_rows")
        csd.registerService(
            self.searchMealOrder,
            "carmensystems.mirador.tablemanager.search_meal_order")
        csd.registerService(
            self.createMealOrder,
            "carmensystems.mirador.tablemanager.create_meal_order")
        csd.registerService(
            self.sendMealOrderReports,
            "carmensystems.mirador.tablemanager.send_meal_orders_reports")
        csd.registerService(
            self.cancelMealOrder,
            "carmensystems.mirador.tablemanager.cancel_meal_order")
        csd.registerService(
            self.writeAllReportTypes,
            "carmensystems.mirador.tablemanager.write_all_report_types")
        csd.registerService(
            self.checkMealOrders,
            "carmensystems.mirador.tablemanager.check_meal_orders")
        csd.registerService(
            self.applyTablesfilter,
            "carmensystems.mirador.tablemanager.apply_filter")
        csd.registerService(
            self.checkDateInFilter,
            "carmensystems.mirador.tablemanager.check_date_in_filter")
        

    def start(self):
        """Starts the form.
        
        Should only be called when starting from inside Studio.
        """
        import StartTableEditor
        StartTableEditor.StartTableEditor(
            ['-f', '$CARMUSR/data/form/crew_meal_order.xml'])

    def saveNrSelectedRows(self, dummy, mealReportType=""):
        """Counts the selected rows in mealReportType's table and saves it.
        """
        if mealReportType == 'MealForecastReport':
            tableWithSelectCol = self.forecastTable.table
        elif mealReportType == 'MealOrderReport':
            tableWithSelectCol = self.orderTable.table
        elif mealReportType == 'MealUpdateReport':
            tableWithSelectCol = self.updateTable.table
        else:
            raise ValueError, "Not valid mealReportType:%s"%mealReportType

        # Count nr of selected rows in table
        rowIter = tableWithSelectCol.search('(select=true)')
        foundSelectedRows = len([x for x in rowIter])

        # Save in NrSelectedInMealTable
        for row in self.nrSelectedTable.table.search('(table_name=%s)'%mealReportType):
            break
        else:
            row = self.nrSelectedTable.table.create((mealReportType,))
        row.nr_selected_rows = foundSelectedRows

    def searchMealOrder(self, *args):
        """Registered method for handling searches for orders and forecasts
        """
        forecast = args[1] == 'forecast'
        update_orders = args[1] == 'update'
        self.messageTable.clearDefaultRow()

        param = self.paramTable.getRow()
        searchStr = '(customer=%s+%s)(cancelled=false)' % (param.region.company.id, param.region.region.id)
        
        if param.one_station:
            searchStr += '(load_station=%s)' % param.load_station.upper() if param.load_station else ""

        if update_orders:
            searchStr += '(from_date=%s)' % (AbsDate(param.from_date))
            table = self.updateTable
            checkSearchResult = self.checkUpdates
            formatStr = '%05d'        
        elif forecast:
            searchStr += '(forecast=true)(from_date>=%s)(to_date<=%s)' % (AbsDate(param.from_date),
                                                                          AbsDate(param.to_date))
            table = self.forecastTable
            checkSearchResult = self.checkForecasts
            formatStr = '%04d'
        else:
            searchStr += '(forecast=false)(from_date=%s)' % (AbsDate(param.from_date))
            table = self.orderTable
            checkSearchResult = self.checkOrders
            formatStr = '%05d'
                    
        searchStr = '(&%s)' % searchStr
        TM.refresh()
        table.clearTable()
        
        if update_orders:
            for order in TM.meal_order_update.search(searchStr):
                try:
                    tmpOrder = table.createRow(formatStr % order.order_update_num)
                    tmpOrder.order_time = order.creation_time
                    tmpOrder.load_station = order.load_station.id
                    tmpOrder.customer = '%s %s' % (order.customer.company.si,
                                                   order.customer.region.name)
                    tmpOrder.supplier = order.supplier.company
                    tmpOrder.from_date = order.from_date
                    tmpOrder.select = checkSearchResult
                    tmpOrder.username = order.username
                    if order.pdf_file:
                        tmpOrder.pdf_doc = os.path.split(order.pdf_file)[-1]
                    if order.xml_file:
                        tmpOrder.xml_doc = os.path.split(order.xml_file)[-1]
                except Exception, e:
                    message = self.messageTable.getRow()
                    errMsg = 'Reading order nr:%s gave error:%s' % (order.order_update_num, e)
                    log.error(errMsg)
                    message.message = errMsg[:1024]
        else:
            for order in TM.meal_order.search(searchStr):
                try:
                    tmpOrder = table.createRow((formatStr % order.order_number, order.forecast))
                    tmpOrder.order_date = order.order_date
                    tmpOrder.load_station = order.load_station.id
                    tmpOrder.customer = '%s %s' % (order.customer.company.si,
                                                   order.customer.region.name)
                    tmpOrder.supplier = order.supplier.company
                    tmpOrder.from_date = order.from_date
                    tmpOrder.to_date = order.to_date
                    tmpOrder.select = checkSearchResult
                    tmpOrder.username = order.username
                    tmpOrder.sent = order.sent
                    if order.pdf_file:
                        tmpOrder.pdf_doc = os.path.split(order.pdf_file)[-1]
                    if order.xml_file:
                        tmpOrder.xml_doc = os.path.split(order.xml_file)[-1]
                except Exception, e:
                    message = self.messageTable.getRow()
                    errMsg = 'Reading order nr:%s gave error:%s' % (order.order_number, e)
                    log.error(errMsg)
                    message.message = errMsg[:1024]


    def checkMealOrders(self, *args):
        """Registered method which sets whether search result should be checked or not
        """
        report_type = args[1]
        if report_type == "forecast":
            self.checkForecasts = args[2] == 'true'
        elif report_type == "update":
            self.checkUpdates = args[2] == 'true'
        else:
            self.checkOrders = args[2] == 'true'

    def createMealOrder(self, *args):
        """Registered method for creating orders or forecasts
        """
        forecast = args[1] == 'true'
        param = self.paramTable.getRow()
        
        params = {'commands':'create',
                  'forecast':('false', 'true')[forecast],
                  'fromDate':param.from_date,
                  'region':param.region.region.id,
                  'runByUser':getpass.getuser()}
        if forecast:
            params['toDate'] = param.to_date
            params['server'] = "rs_latest"
        if param.one_station:
            params['loadAirport'] = param.load_station.upper()
        
        self.DJQ.submitJob(params=params, reloadModel='1')
        

    def _getSelectedOrders(self, reporttype):
        """Returns an iterator over the selected orders in GUI.
        """
        if reporttype == 'forecast':
            return self.forecastTable.table.search('(select=true)')
        elif reporttype == 'update':
            return self.updateTable.table.search('(select=true)')
        else:
            return self.orderTable.table.search('(select=true)')


    def cancelMealOrder(self, dummy, forecast):
        """Registered method for cancelling orders or forecasts
        """
        forecast = forecast == 'true' # Make boolean
        params = {'commands':'cancel',
                  'forecast':('false', 'true')[forecast]}
        for paramNr, order in enumerate(self._getSelectedOrders(('order', 'forecast')[forecast])):
            params['order'+str(paramNr)] = order.order_number

        self.DJQ.submitJob(params=params, reloadModel='1')
            

    def writeAllReportTypes(self, dummy, forecast):
        """Registered method for writing all types of reports to disk.
        """
        forecast = forecast == 'true' #make boolean
        params = {'commands':'testAllReports',
                  'forecast':('false', 'true')[forecast]}
        for i, order in enumerate(self._getSelectedOrders(('order', 'forecast')[forecast])):
            params['order'+str(i)] = order.order_number
            
        self.DJQ.submitJob(params=params, reloadModel='1')
        
    def sendMealOrderReports(self, dummy, report_type, override, mailaddresses=''):
        """Registered method for sending reports.
        """
        # This is a dummy example string presented in the GUI:
        defaultDummy = 'any.1@my.org,any.2@my.org,...,any.X@my.org'

        update = report_type == 'update' #make boolean                
        forecast = report_type == 'forecast' #make boolean
        override = override == 'true' #make boolean
        params = {'commands':('send', 'send;update')[update],
                  'forecast':('false', 'true')[forecast]}


        for i, order in enumerate(self._getSelectedOrders(report_type)):
            if update:
                params['order'+str(i)] = order.update_order_num
            else:
                params['order'+str(i)] = order.order_number
        
        if override and mailaddresses != defaultDummy:
            # Clean leading and trailing spaces & commas
            mailaddresses = mailaddresses.strip(' ,')
            mailAdrList = mailaddresses.split(',')
            for i, mailAddr in enumerate(mailAdrList):
                params['email'+str(i)] = mailAddr
            
        self.DJQ.submitJob(params=params, reloadModel='1')

    def fillTmpMealOrderLine(self,):
        """Fills tmp meal order line table
        """
        self.orderLineTable.clearTable()
        for index, order in enumerate(TM.meal_order_line):
            try:
                tmpOrder = self.orderLineTable.createRow((index+1,))
                flt = order.load_flight
                tmpOrder.load_flight = "%s/ %s %s-%s" % \
                    (flt.fd, str(flt.udor)[:9], flt.adep.id, flt.ades.id)
                flt = order.cons_flight
                tmpOrder.cons_flight = "%s/ %s %s-%s" % \
                    (flt.fd, str(flt.udor)[:9], flt.adep.id, flt.ades.id)
                tmpOrder.maincat = order.maincat.id
                tmpOrder.meal_code = order.meal_code.code
                tmpOrder.amount = "%s" % order.amount
            except Exception, e:
                message = self.messageTable.getRow()
                errMsg = 'Reading order line gave error:%s' % (e)
                log.error(errMsg)
                message.message = errMsg[:1024]

    def fillTmpMealOrderUpdateLine(self,):
        """Fills tmp meal order update line table
        """
        self.orderUpdateLineTable.clearTable()
        for index, order in enumerate(TM.meal_order_update_line):
            try:
                tmpOrder = self.orderUpdateLineTable.createRow((index+1,))
                flt = order.load_flight
                tmpOrder.load_flight = "%s/ %s %s-%s" % \
                    (flt.fd, str(flt.udor)[:9], flt.adep.id, flt.ades.id)
                flt = order.cons_flight
                tmpOrder.cons_flight = "%s/ %s %s-%s" % \
                    (flt.fd, str(flt.udor)[:9], flt.adep.id, flt.ades.id)
                tmpOrder.maincat = order.maincat.id
                tmpOrder.meal_code = order.meal_code.code
                tmpOrder.amount = "%s" % order.amount
            except Exception, e:
                message = self.messageTable.getRow()
                errMsg = 'Reading order line gave error:%s' % (e)
                log.error(errMsg)
                message.message = errMsg[:1024]
                        
    def _getFilterBoundries(self):
        """ Returns filter i.e. (from, to).
        """
        # Get time
        row = self.filterTable.getRow()
        time_tup = row.filter_date.split()
        # Calculate filter boundries
        now_yyyy, now_mon , now_day = time_tup[:3]
        end_yyyy = start_yyyy = now_yyyy
        start_mm = now_mon - 3
        end_mm = now_mon + 1
        if end_mm > 12:
            end_yyyy = end_yyyy +1
            end_mm -= 12
        elif start_mm < 1:
            start_yyyy -= 1
            start_mm += 12
        return (AbsDate(start_yyyy, start_mm, 1,), AbsDate(end_yyyy, end_mm, 1))

    def applyTablesfilter(self, dummy=None, orderNr=0, forecast='false'):
        """ Set standalonemeal filters for tables.
        """
        # Set default values. Can get 'NULL' when empty selection in waveform.
        if orderNr == 'NULL' or forecast == 'NULL':
            orderNr = 0
            forecast = 'false'
        # Set filter
        (start, end) = self._getFilterBoundries()
        dbPeriodStartStr = str(start)
        dbPeriodEndStr = str(end)
        filters = [("standalonemeal","start", dbPeriodStartStr),
                   ("standalonemeal","end", dbPeriodEndStr),
                   ("standalonemeal","ordernr", str(orderNr)),
                   ("standalonemeal","forecast", forecast)]
        TM.unloadTables(['meal_order', 'meal_order_line', 'meal_order_update', 'meal_order_update_line'])
        TM.reset(['meal_order', 'meal_order_line', 'meal_order_update', 'meal_order_update_line'])
        for (name, param, value) in filters:
            log.info('Set filter param: TM.addSelection("%s", "%s", %s)' % (name,param,value))
            print 'Set filter param: TM.addSelection("%s", "%s", "%s")' % (name,param,value)
            TM.addSelection(name,param,value)

        self.fillTmpMealOrderLine()
        self.fillTmpMealOrderUpdateLine()
    
    def checkDateInFilter(self, dummy=None, date=None):
        """Write GUI errormsg if to-/from-date outside filtered interval.
        """
        errMsg = ""
        #param = self.paramTable.getRow()
        (start, end) = self._getFilterBoundries()
        if date is None:
            return
        fromDate = AbsDate(date)
        if not (start <= fromDate <= end): 
            errMsg = "Warning! date %s is outside filtered interval:[%s - %s]" % \
                     (fromDate, start, end)
            log.error(errMsg)
            message = self.messageTable.getRow()
            message.message = errMsg[:1024]
        else:
            self.messageTable.clearDefaultRow()
        
############################ Utilities & helper functions ######################


def initFormTableManager(*args):
    """Helps delaying instantiation, of form & tmp tables, until needed.
    """
    global MH
    MH = MealOrderFormHandler()

############################ main ##############################################
csd.registerService(
    initFormTableManager,
    "carmensystems.mirador.tablemanager.crew_meal_initiate_tables")


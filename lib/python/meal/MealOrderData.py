#

#
"""This module implements a Crew Meal Order Data Handler
"""
import getpass
import logging

import Cui
import carmensystems.rave.api as R
#from carmensystems.dave import DMF in R22 replaced with
from carmensystems.dave import dmf as DMF
from AbsDate import AbsDate
from AbsTime import AbsTime
from modelserver import EntityError
from modelserver import EntityNotFoundError

from meal.MealDataClasses import MealSupplier, MealCustomer, MealOrderLine, MealOrder, SpecialMealOrderLine
from meal.MealExceptions import *
from tm import TM
from utils.selctx import BasicContext

log = logging.getLogger('MealOrderData')

#################  debugging utils #################
def debugPrint(fkn):
    """Decorator to print debug about call.
    """
    def wrapper(*args, **kwds):
        result = fkn(*args, **kwds)
        # remove 'self'
        if callable(args[0]):
            args = args[1:]
        print 'Calling:%s(%s, %s) -> %s' % (fkn.__name__, args, kwds, result)
        return result
    return wrapper
                          
#################  Data handling classes #################
class MealOrderHandler:
    """ Read order info from the data base and returns MealOrder. The MealUpdateOrderHandler
        makes the same thing for an update order returns the same data structure.
    
    """

    def __init__(self, orderNumber, isForecast):
        self.orderNumber = orderNumber
        self.forecast = isForecast

    def getMealOrder(self):
        """ Gets the meal order and returns a MealOrder instance 
        
        """
        # Idea: allow entities to be supplied!!!!!
        try:
            order_entity = TM.meal_order[(self.orderNumber, self.forecast)]

        except Exception, e:
            raise OrderNotFoundError, \
                  'Could not find %s Nr %s. No data could be loaded. error: %s' % \
                  (('order', 'forecast')[self.forecast], self.orderNumber, e)

        try:
            supp_entity = order_entity.supplier
            supplier = MealSupplier(supp_entity.supplier_id,
                                    supp_entity.company,
                                    supp_entity.department,
                                    getattr(supp_entity.station, "id", ""),
                                    supp_entity.phone1,
                                    supp_entity.phone2,
                                    supp_entity.fax,
                                    supp_entity.email,
                                    supp_entity.sita_email,
                                    supp_entity.pdf,
                                    supp_entity.xml)
        except Exception, e:
            raise SupplierNotFoundError, \
                  '%s Nr %s has invalid supplier data.  error: %s' % \
                  (('Order', 'Forecast')[self.forecast], self.orderNumber, e)
        try:
            cust_entity = order_entity.customer
            customer = MealCustomer(cust_entity.company.id,
                                    cust_entity.region.id,
                                    cust_entity.region.name,
                                    cust_entity.department,
                                    cust_entity.phone1,
                                    cust_entity.phone2,
                                    cust_entity.fax,
                                    cust_entity.email,
                                    cust_entity.invoicecompanyname,
                                    cust_entity.invoicecontrolstaff,
                                    cust_entity.invoiceaddrname,
                                    cust_entity.invoiceaddrline1,
                                    cust_entity.invoiceaddrline2,
                                    cust_entity.invoiceaddrline3)
        except Exception, e:
            raise CustomerNotFoundError, \
                  '%s Nr %s has invalid customer data. error: %s' % \
                  (('Order', 'Forecast')[self.forecast], self.orderNumber, e)
        orderLines = []
        for order_line in TM.meal_order_line.search('(order.order_number=%s)'%order_entity.order_number):
            try:
                orderLines.append(
                    MealOrderLine(order_line.load_flight.udor,
                                  order_line.load_flight.fd,
                                  order_line.load_flight.adep.id,
                                  order_line.cons_flight.udor,
                                  order_line.cons_flight.fd,
                                  order_line.cons_flight.adep.id,
                                  order_line.cons_flight.ades.id,
                                  order_line.maincat.id,
                                  order_line.meal_code.code,
                                  order_line.meal_code.description,
                                  order_line.amount,
                                  order_line.load_flight.sobt))
            except Exception, e:
                raise OrderLineNotFoundError, \
                      '%s Nr %s has invalid orderline. error: %s' % \
                      (('Order', 'Forecast')[self.forecast], self.orderNumber, e)
        try:
            meal_order_data =  MealOrder(self.orderNumber,
                                         order_entity.order_date,
                                         order_entity.load_station.id,
                                         order_entity.load_station.name,
                                         self.forecast,
                                         None,  # TODO NOT UPDATE
                                         order_entity.sent,
                                         order_entity.cancelled,
                                         order_entity.from_date,
                                         order_entity.to_date,
                                         supplier,
                                         customer,
                                         order_entity.username,
                                         order_entity,
                                         orderLines)
        except Exception, e:
            raise OrderNotFoundError, \
                  '%s Nr %s contains invalid data.  error: %s' % \
                  (('Order', 'Forecast')[self.forecast], self.orderNumber, e)

        return meal_order_data


class MealUpdateOrderHandler:
    """ Read order info from the data base and returns MealOrder. The MealOrderHandler
        makes the same thing for an ordinary order returns the same data structure.
    
    """

    def __init__(self, orderNumber, refOrder):
        self.orderNumber = orderNumber
        self.refOrder = refOrder

    def getMealOrder(self):
        """ Gets the meal order and returns a MealOrder instance 
        
        """
        try:
            order_entity = TM.meal_order_update[(self.refOrder, self.orderNumber)]

        except Exception, e:
            raise OrderNotFoundError, \
                  'Could not find Nr %s. No data could be loaded. error: %s' % (self.orderNumber, e)

        try:
            supp_entity = order_entity.supplier
            supplier = MealSupplier(supp_entity.supplier_id,
                                    supp_entity.company,
                                    supp_entity.department,
                                    getattr(supp_entity.station, "id", ""),
                                    supp_entity.phone1,
                                    supp_entity.phone2,
                                    supp_entity.fax,
                                    supp_entity.email,
                                    supp_entity.sita_email,
                                    supp_entity.pdf,
                                    supp_entity.xml)
        except Exception, e:
            raise SupplierNotFoundError, \
                  'Nr %s has invalid supplier data.  error: %s' % (self.orderNumber, e)
        try:
            cust_entity = order_entity.customer
            customer = MealCustomer(cust_entity.company.id,
                                    cust_entity.region.id,
                                    cust_entity.region.name,
                                    cust_entity.department,
                                    cust_entity.phone1,
                                    cust_entity.phone2,
                                    cust_entity.fax,
                                    cust_entity.email,
                                    cust_entity.invoicecompanyname,
                                    cust_entity.invoicecontrolstaff,
                                    cust_entity.invoiceaddrname,
                                    cust_entity.invoiceaddrline1,
                                    cust_entity.invoiceaddrline2,
                                    cust_entity.invoiceaddrline3)
        except Exception, e:
            raise CustomerNotFoundError, \
                  'Nr %s has invalid customer data. error: %s' % (self.orderNumber, e)
        orderLines = []
        for order_line in TM.meal_order_update_line.search('(order.order_update_num=%s)' % self.orderNumber):
            try:
                orderLines.append(
                    MealOrderLine(order_line.load_flight.udor,
                                  order_line.load_flight.fd,
                                  order_line.load_flight.adep.id,
                                  order_line.cons_flight.udor,
                                  order_line.cons_flight.fd,
                                  order_line.cons_flight.adep.id,
                                  order_line.cons_flight.ades.id,
                                  order_line.maincat.id,
                                  order_line.meal_code.code,
                                  order_line.meal_code.description,
                                  order_line.amount,
                                  order_line.load_flight.sobt))
            except Exception, e:
                raise OrderLineNotFoundError, \
                      'Nr %s has invalid orderline. error: %s' % (self.orderNumber, e)
        try:
            meal_order_data =  MealOrder(self.orderNumber,
                                         order_entity.creation_time,
                                         order_entity.load_station.id,
                                         order_entity.load_station.name,
                                         False,
                                         self.refOrder.order_number,  # TODO UPDATE
                                         order_entity.sent,
                                         order_entity.cancelled,
                                         order_entity.from_date,
                                         order_entity.to_date,
                                         supplier,
                                         customer,
                                         order_entity.username,
                                         order_entity,
                                         orderLines)
        except Exception, e:
            raise OrderNotFoundError, \
                  'Nr %s contains invalid data. error: %s' % (self.orderNumber, e)

        return meal_order_data


class OrderTablesManager:
    """Order Tables Manager
    """
    def __init__(self):
        bc = BasicContext()
        self.context = bc.getGenericContext()

    def refresh(self):
        TM.refresh()
        Cui.CuiReloadTable('meal_order')
        Cui.CuiReloadTable('meal_order_line')

    def newState(self):
        TM.newState()

    def save(self):
        TM.save()

    def undo(self):
        TM.undo()

    def repairOrderSequence(self, sequenceOrderNo, forecast=False):
        """Updates the sequence if it does not match actual data in table.
        """
        # Database sequences are used, one per order type.
        # However, in order to maintain backwards compatibility with
        # the old method we must ensure that the sequence value is not
        # lower than the currently highest order number. This also 
        # resolves any situations with damaged sequence due to e.g.
        # database maintenance.
        if forecast:
            sequence = "seq_meal_forecast"
        else:
            sequence = "seq_meal_order"

        log.warning("Sequence %s is out of sync! sequenceOrderNo=%d is already used! Not OK!" %
                    (sequence, sequenceOrderNo))
        tableOrderNo = 0

        searchStr = '(forecast=%s)'% ('false', 'true')[forecast]
        for order in TM.meal_order.search(searchStr):
            if order.order_number > tableOrderNo:
                tableOrderNo = order.order_number

        # Non forcast and update order shares the same sequence
        if not forecast:
            for order in TM.meal_order_update:
                if order.order_update_num > tableOrderNo:
                    tableOrderNo = order.order_update_num

        log.warning("Trying to correct! Setting sequence %s's CURRVAL to: %d" %
                    (sequence, tableOrderNo))
        DMF.BorrowConnection(TM.conn()).setSeqValue(sequence, tableOrderNo)


    def createUpdateItem(self, order, originalOrder_entity, load_date, loadFlight_entity, consFlight_entity, mainCat,
                         mealConsCodes, amount, supplier_entity, loadStn_entity, company_entity, region_entity, runDate,
                         runByUser, updateOrders, special_meals):
        """ Creates an order update line if needed. If an update order is needed a order line is created in the
            database. This means that a order line is always created and if no parent order is passed, it is
            created as well.
        """
        print('### DEBUG ### SKCMS-1845: createUpdateItem for order = %s and loadFlight_entity = %s' % (order, loadFlight_entity))
        meal_shrtg, special_shrtg = self.getMealShortages(originalOrder_entity, loadFlight_entity, consFlight_entity,
                                                          mainCat, mealConsCodes, amount, special_meals)

        # Create a new update order if there is a shortage and
        # no order exists or the date has changed.
        if (len(meal_shrtg)+len(special_shrtg)) > 0 and (order is None or AbsDate(load_date) > order.fromDate):
            print('### DEBUG ### SKCMS-1169: Create Update Order Entry')
            order  = self.createUpdateOrderEntry(originalOrder_entity, AbsDate(load_date), AbsDate(load_date),
                                                       supplier_entity, loadStn_entity, company_entity,
                                                       region_entity, runDate, runByUser)
            updateOrders.append(order)

        for meal_shortage in meal_shrtg:
            print('### DEBUG ### SKCMS-1169: Create Update Order Line Entry')
            self.createUpdateOrderLineEntry(order, meal_shortage[1], meal_shortage[2], meal_shortage[3],
                                            meal_shortage[4], meal_shortage[5])

        for _, load_flt_ety, cons_flt_ety, main_cat_ety, meal_ety, special_meal_ety, meal_diff in special_shrtg:

            line = self.create_update_special_line_entry(order, load_flt_ety, cons_flt_ety, main_cat_ety, meal_ety,
                                                         special_meal_ety, meal_diff)
            order.addOrderLine(line)

        return order


    def createOrderItem(self, order, load_date, forecast, fromDate, toDate, supplier_entity, loadStn_entity,
                        company_entity, region_entity, runDate, runByUser, loadFlight_entity, consFlight_entity,
                        mainCat, mealConsCodes, amount, createdOrders, special_meals):
        """ Creates a order item in the database. This means that a order line is always created and if no parent
            order is passed, it is created as well.
        """
        print('### DEBUG ### SKCMS-1169: Create Order Item for order=%s' % order)
        if (order is None or ((AbsDate(load_date) > order.fromDate) and not forecast)):
            # For orders: one order per day. For forecasts use same order for all days.
            order = self.createOrderEntry(forecast, AbsDate(fromDate), AbsDate(toDate), supplier_entity,
                                          loadStn_entity, company_entity, region_entity, runDate, runByUser)

            if createdOrders is not None:
                createdOrders.append(order)


        if loadFlight_entity is not None and consFlight_entity is not None and mainCat is not None and \
            mealConsCodes is not None and amount is not None:
            self.createOrderLineEntry(order, loadFlight_entity, consFlight_entity, mainCat, mealConsCodes, amount, special_meals)

        return order

    def createOrders(self, fromDate, toDate, forecast=False, update=False, reportServer=False,
                    station=False, region=False, runByUser=None, runDate=None ):
        """ Create order and writes them to the data base. This is used for both ordinary orders
            (including forecasts) and for update orders.
        """
        print('### DEBUG ### SKCMS-1169: createOrders entered') #Necessary?
        createdOrders = []

        if forecast and update:
            raise ArgumentInconsistencyError("forecast and update cannot both be true")

        if update:
            loadDateIterator = 'report_meal.update_load_time_set'
            loadDateFilter = ('report_meal.%%update_load_time%% >= %s' % (fromDate),
                              'report_meal.%%update_load_time%% < %s' % (toDate))
            loadDateVar = 'report_meal.%update_load_time%'

            loadStnIterator = 'report_meal.update_load_stn_set'
            loadStnVar = 'report_meal.%update_load_stn%'
            loadStnFilter = ('report_meal.%%update_load_stn%% = "%s"' % (station))

            loadSupplierIterator = 'report_meal.update_load_supplier_set'
            loadSupplierVar =  'report_meal.%update_load_supplier_id%'

            loadFlightNrVar = 'report_meal.%update_load_flight_nr%'
            loadFlightUdorVar = 'report_meal.%update_load_udor_str%'

        else:

            loadDateIterator = 'report_meal.load_day_set'
            loadDateVar = 'report_meal.%load_day%'
            loadStnIterator = 'report_meal.load_stn_set'
            loadStnVar = 'report_meal.%load_stn%'
            loadStnFilter = ('report_meal.%%load_stn%% = "%s"' % (station))
            loadSupplierIterator = 'report_meal.load_supplier_set'
            loadSupplierVar =  'report_meal.%load_supplier_id%'

            loadFlightNrVar = 'report_meal.%load_flight_nr%'
            loadFlightUdorVar = 'report_meal.%load_udor_str%'

            if forecast:
                loadDateFilter = ('report_meal.%%load_day%% >= %s' % (fromDate),
                                  'report_meal.%%load_day%% <= %s' % (toDate))
            else:
                loadDateFilter = ('report_meal.%%load_day%% = %s' % (fromDate))

        if not station:
            loadStnFilter = ()

        # To avoid too large memory footprint do rave lookup for each region
        customers = []
        try:
            for customer in TM.meal_customer.search('(region=%s)' % (region or '*')):
                customers.append((customer.company, customer.region))
        except Exception, e:
            raise CustomerNotFoundError('Customer not valid for region %s. error:%s' % (region, e))
        if not len(customers):
            raise CustomerNotFoundError('Customer not valid. Region %s not found.' % (region or ''))
        elif len(customers) > 1 and region:
            raise CustomerNotFoundError('Customer not valid. Several matches for region %s.' % region)

        bc = BasicContext()
        fre = R.foreach
        itr = R.iter
        foundData = False

        for (company_entity, region_entity) in customers:
            regionFilter = ('report_meal.%%meal_region%% = "%s"' % region_entity.id)

            regions_from_rave, = R.eval(
                bc.getGenericContext(),
                fre(itr('report_meal.meal_region_set',
                        where=regionFilter),
                    fre(itr('report_meal.has_meal_set',
                            where='report_meal.%has_consumption_code%'),
                        fre(itr(loadStnIterator,
                                where=loadStnFilter),
                            loadStnVar,
                            fre(itr(loadSupplierIterator),
                                loadSupplierVar,
                                fre(itr(loadDateIterator,
                                        where=loadDateFilter,
                                        sort_by=loadDateVar),
                                    loadDateVar,
                                    fre(itr('report_meal.load_service_type_set',
                                            sort_by='report_meal.%load_service_type%'),
                                        'report_meal.%load_service_type%',
                                        fre(itr('report_meal.opt_out_set',where ='report_meal.%opted_in_crew%'),                                       
                                        fre(itr('iterators.unique_leg_set',
                                                sort_by=loadFlightNrVar),
                                            loadFlightUdorVar,
                                            loadFlightNrVar,
                                            fre(itr('report_meal.meal_set'),
                                                'report_meal.%consumption_udor_str%',
                                                'report_meal.%consumption_flight_nr%',
                                                'report_meal.%consumption_stn%',
                                                fre(itr('report_meal.special_meal_code_set'), 'report_meal.%special_meal_code%'),
                                                'fundamental.%main_cat%',
                                                'report_meal.%consumption_code%',
                                                'report_meal.%meals%'))))))))))

            if regions_from_rave:
                has_meals = regions_from_rave[0][1]
            else:
                has_meals = []
            if has_meals:
                load_stations = has_meals[0][1]
            else:
                load_stations = []

            for (ix1, load_station, load_suppliers) in load_stations:
                loadStn_entity = None

                for (ix2, supplierId, load_dates) in load_suppliers:
                    current_order = None
                    supplier_entity = None
                    
                    for (ix3, load_date, load_service_types) in load_dates:
                        foundData = True
                        for (ix4, load_service_type, load_opt_in_crew_meals) in load_service_types:
                            for (ix5,  unique_legs) in load_opt_in_crew_meals:
                            #### Create/get meal order entry
                                try:
                                    if supplier_entity is None:
                                        supplier_entity = self.getSupplierEntity(supplierId, region_entity.id, AbsDate(load_date), load_service_type)

                                    if loadStn_entity is None:
                                        loadStn_entity = self.getStationEntity(load_station)

                                    if update:
                                        originalOrder_entity = self.getOrderEntity(AbsDate(load_date), loadStn_entity, supplier_entity, region_entity)

                                        if originalOrder_entity is None:

                                            try:
                                                empty_order = self.createOrderItem(None, load_date, forecast, fromDate,
                                                                                toDate, supplier_entity, loadStn_entity,
                                                                                company_entity, region_entity, runDate,
                                                                                runByUser, None, None, None, None, None,
                                                                                createdOrders, None)

                                            except AccumulatedExceptions, e:
                                                change_exception_args(e,
                                                                    'MealOrderRun.py - Could not create meal_order entry for ' + \
                                                                    'date=%s, supplier=%s, station=%s, company=%s, region=%s ' % \
                                                                    (load_date, supplier_entity.supplier_id, loadStn_entity.id,
                                                                    company_entity.id, region_entity.id) + \
                                                                    'Reason is exception:%s ' % (e) ,)
                                                log.error(str(e))
                                                continue

                                            originalOrder_entity = empty_order.entity

                                except AccumulatedExceptions, e:
                                    change_exception_args(e,
                                                        'MealOrderRun.py - Could not create meal_order entry for ' + \
                                                        'date=%s, supplier=%s, station=%s, company=%s, region=%s ' % \
                                                        (load_date, supplierId, load_station, company_entity.id, region_entity.id) + \
                                                        'Reason is exception:%s ' % (e))
                                    log.error(str(e))
                                    continue


                                prev_loadFlight = None
                                for (ix5, loadStart, loadFlight, meal_sets) in unique_legs:

                                    try:
                                        loadFlight_entity = self.getFlightEntity(loadStart, loadFlight, loadStn_entity)
                                    except AccumulatedExceptions, e:
                                        change_exception_args(e,
                                                            'MealOrderRun.py - Could not create meal_order_line entry for ' + \
                                                            'date=%s, supplier=%s, station=%s, company=%s, region=%s ' % \
                                                            (load_date, supplierId, station, company_entity.id, region_entity.id) + \
                                                            'loadFlight=%s ' % \
                                                            (loadFlight) + \
                                                            'Reason is exception:%s ' % (e))
                                        log.error(str(e))
                                    print("### DEBUG ### SKCMS-1169: for unique_legs, update=%s, prev_loadFligt=%s, loadFlight=%s" % (update, prev_loadFlight, loadFlight))
                                    # Check if an update order already been sent for that load
                                    if update and prev_loadFlight != loadFlight:
                                        print("### DEBUG ### SKCMS-1169: update=true and prev_loadFlight != loadFlight")
                                        if self.update_order_exists(loadFlight_entity):
                                            print("### DEBUG ### SKCMS-1169: Update order exists for %s" % (loadFlight_entity.fd))
                                            log.info("Update order exists for %s" % (loadFlight_entity.fd))
                                            continue

                                        # We want the create order flightwise. Reset the current order and a new 
                                        # will be created automatically 
                                        current_order = None

                                    if meal_sets == []:
                                        # If meal_sets is empty not futher action will be taken below except prev_loadFlight = loadFlight
                                        # We don't want this to happen since it can cause both missed Update orders and duplicates if pub_MealUpdateTask
                                        # should for some reason be run more then once every 15:th minute
                                        print("### DEBUG ### SKCMS-1845: Empty meal_sets for flight %s" % (loadFlight_entity.fd))
                                        continue

                                    prev_loadFlight = loadFlight

                                    for (_, consStart, consFlight, consDepAirport, special_meal_codes, mainCat, mealConsCodes, amount) in meal_sets:
                                        #### Create order lines entry
                                        t = [x for _,x in special_meal_codes]
                                        special_meals = dict((x, t.count(x)) for x in t)
                                        spl_meal_num = sum(map(special_meals.get, special_meals))
                                        meal_amount = amount - spl_meal_num

                                        try:

                                            consFlight_entity = self.getFlightEntity(consStart,
                                                                                    consFlight,
                                                                                    self.getStationEntity(consDepAirport))

                                            if update:
                                                current_order = self.createUpdateItem(current_order, originalOrder_entity,
                                                                                    load_date, loadFlight_entity,
                                                                                    consFlight_entity, mainCat,
                                                                                    mealConsCodes, meal_amount,
                                                                                    supplier_entity, loadStn_entity,
                                                                                    company_entity, region_entity,
                                                                                    runDate, runByUser, createdOrders,
                                                                                    special_meals)
                                            else:
                                                current_order = self.createOrderItem(current_order, load_date, forecast,
                                                                                fromDate, toDate, supplier_entity,
                                                                                loadStn_entity, company_entity,
                                                                                region_entity, runDate, runByUser,
                                                                                loadFlight_entity, consFlight_entity,
                                                                                mainCat, mealConsCodes, meal_amount,
                                                                                createdOrders, special_meals)

                                        except AccumulatedExceptions, e:
                                            change_exception_args(e,
                                                                'MealOrderRun.py - Could not create meal_order_line entry for ' + \
                                                                'date=%s, supplier=%s, station=%s, company=%s, region=%s ' % \
                                                                (load_date, supplierId, station, company_entity.id, region_entity.id) + \
                                                                'loadFlight=%s, consFlight=%s, consDepAirport=%s ' % \
                                                                (loadFlight, consFlight, consDepAirport) + \
                                                                'Reason is exception:%s ' % (e))
                                            log.error(str(e))
                                            continue
        if not foundData:
            log.warning('No Meal %s created for filters:\nLeg Set=%s\nLoad station=%s\nRegion=%s'%
                         (('Order', 'Forecast')[forecast], loadDateFilter, loadStnFilter, regionFilter))

        return createdOrders



    def createUpdateOrderEntry(self, parentOrder_entity, startDate, endDate, supplier_entity, station_entity,
                               company_entity, region_entity, runDate, runByUser=None):
        """ Creates an update meal order entry in db & returns the new order and found entities.
        
        """

        # Update order shall use the same order numbers as the normal orders        
        orderNo = DMF.BorrowConnection(TM.conn()).getNextSeqValue("seq_meal_order")
        log.info("Creating update order: %d" % (orderNo))

        try:
            customer_entity = TM.meal_customer[(company_entity, region_entity)]
        except Exception, e:
            raise CustomerNotFoundError('Customer (%s,%s) not valid. error:%s' % (company_entity.id, region_entity.id, e))

        try:
            order_entity  = TM.meal_order_update.create((parentOrder_entity, orderNo))
        except EntityError, e:
            # Try updating sequence if it is out of synch
            self.repairOrderSequence(orderNo, False)
            orderNo = DMF.BorrowConnection(TM.conn()).getNextSeqValue("seq_meal_order")
            log.info('Trying again to create the same now with orderNo:%s' % orderNo)
            order_entity  = TM.meal_order_update.create((parentOrder_entity, orderNo))

        order_entity.creation_time = runDate
        order_entity.supplier = supplier_entity
        order_entity.customer = customer_entity
        order_entity.load_station = station_entity
        order_entity.sent = False
        order_entity.cancelled = False
        order_entity.from_date = AbsTime(startDate)
        order_entity.to_date = AbsTime(endDate)
        order_entity.username = runByUser or getpass.getuser()

        supplier = MealSupplier(supplierId = supplier_entity.supplier_id,
                                name = supplier_entity.company,
                                department = supplier_entity.department,
                                station = getattr(supplier_entity.station, "id", ""),
                                phone1 = supplier_entity.phone1,
                                phone2 = supplier_entity.phone2,
                                fax = supplier_entity.fax,
                                email = supplier_entity.email,
                                sita_email = supplier_entity.sita_email,
                                pdf = supplier_entity.pdf,
                                xml = supplier_entity.xml)

        customer = MealCustomer(name = customer_entity.company.id,
                                regionName = customer_entity.region.id,
                                regionFullName = customer_entity.region.name,
                                department = customer_entity.department,
                                phone1 = customer_entity.phone1,
                                phone2 = customer_entity.phone2,
                                fax = customer_entity.fax,
                                email = customer_entity.email,
                                invoiceCompanyName = customer_entity.invoicecompanyname,
                                invoiceControlStaff = customer_entity.invoicecontrolstaff,
                                invoiceAddrName = customer_entity.invoiceaddrname,
                                invoiceAddrLine1 = customer_entity.invoiceaddrline1,
                                invoiceAddrLine2 = customer_entity.invoiceaddrline2,
                                invoiceAddrLine3 = customer_entity.invoiceaddrline3)

        if parentOrder_entity :
            parentOrderNumner = parentOrder_entity.order_number
        else:
            parentOrderNumner = 0

        update_order = MealOrder(order_entity.order_update_num,
                                 order_entity.creation_time,
                                 order_entity.load_station.id,
                                 order_entity.load_station.name,
                                 False,
                                 parentOrderNumner, # TODO UPDATE
                                 order_entity.sent,
                                 order_entity.cancelled,
                                 order_entity.from_date,
                                 order_entity.to_date,
                                 supplier,
                                 customer,
                                 order_entity.username,
                                 order_entity,
                                 [])

        return update_order


    def getMealShortages(self, original_order, loadFlight_entity, consFlight_entity, mainCat, mealConsCodes, amount,
                         special_meals):
        """ Creates an update meal order line entries in db & returns created/found entities.
            A shortage is not reported if an update order already exists

        """

        meal_shortages = []
        special_meal_shortages = []

        try:
            mainCat_entity= TM.crew_category_set[(mainCat,)]
        except Exception, e:
            raise CrewCategoryNotFoundError("CrewCategory (%s) is not valid. error:%s" % (mainCat, e))

        mealConsCodesList = mealConsCodes.split(',')

        # Create a dictionary where the code is the key and the value is the number of occurrences
        mealConsCodesDict = dict((i,mealConsCodesList.count(i)) for i in mealConsCodesList)
        for mealConsCode, occurrences in mealConsCodesDict.iteritems():

            try:
                meal_entity = TM.meal_code[(mealConsCode,)]
            except Exception, e:
                raise MealCodeNotFoundError("Meal Code (%s) is not valid. error:%s" % (mealConsCode, e))

            order_line_entity = self.getOrderLineEntity(consFlight_entity, mainCat_entity, meal_entity)

            if order_line_entity is not None:
                meal_diff = (amount * occurrences) - order_line_entity.amount
                if meal_diff > 0:
                    meal_shortages.append((original_order, loadFlight_entity, consFlight_entity, mainCat_entity,
                                           meal_entity, meal_diff))
            else:
                #Ok, there was no order for this kind of meal at all
                meal_shortages.append((original_order, loadFlight_entity, consFlight_entity, mainCat_entity,
                                       meal_entity, amount * occurrences))

            for special_meal_code, amount in special_meals.iteritems():
                try:
                    special_meal_entity = TM.meal_special_code_set[(special_meal_code,)]
                except Exception, e:
                    raise MealCodeNotFoundError("Meal Code (%s) is not valid. error:%s" % (special_meal_code, e))

                special_line_entity = self.get_special_order_line_entity(consFlight_entity, mainCat_entity, meal_entity,
                                                                         special_meal_entity)

                if special_line_entity is not None:
                    meal_diff = (amount * occurrences) - special_line_entity.amount
                    if meal_diff > 0:
                        special_meal_shortages.append((original_order, loadFlight_entity, consFlight_entity,
                                                       mainCat_entity, meal_entity, special_meal_entity, meal_diff))
                else:
                    # Ok, there was no order for this kind of meal at all
                    special_meal_shortages.append((original_order, loadFlight_entity, consFlight_entity, mainCat_entity,
                                                   meal_entity, special_meal_entity, amount * occurrences))

        return meal_shortages, special_meal_shortages

    def createUpdateOrderLineEntry(self, updateOrder, loadFlight_entity, consFlight_entity, mainCat_entity, meal_entity,
                                   amount):
        """ Creates an update meal order line entries in db & returns created/found entities.
        """
        query_tuple = (updateOrder.entity, loadFlight_entity, consFlight_entity, mainCat_entity, meal_entity,)
        try:
            orderLine_entity = TM.meal_order_update_line[query_tuple]
            orderLine_entity.amount += amount
        except EntityNotFoundError:
            print('### DEBUG ### SKCMS-1169: About to create Meal Order Update Line for: ', loadFlight_entity.fd)
            orderLine_entity = TM.meal_order_update_line.create(query_tuple)
            orderLine_entity.amount = amount

        orderLine = MealOrderLine(loadDate = orderLine_entity.load_flight.udor,
                                  loadFlight = orderLine_entity.load_flight.fd,
                                  loadDepAirport = orderLine_entity.load_flight.adep.id,
                                  consDate = orderLine_entity.cons_flight.udor,
                                  consFlight = orderLine_entity.cons_flight.fd,
                                  consDepAirport = orderLine_entity.cons_flight.adep.id,
                                  consArrAirport = orderLine_entity.cons_flight.ades.id,
                                  mainCat = orderLine_entity.maincat.id,
                                  mealCode = orderLine_entity.meal_code.code,
                                  mealDescription = orderLine_entity.meal_code.description,
                                  amount = amount,
                                  loadFlightSobt = orderLine_entity.load_flight.sobt)

        updateOrder.addOrderLine(orderLine)

    def create_update_special_line_entry(self, update_order, load_flt_entity, cons_flt_entity, main_cat_entity,
                                         meal_entity, special_entity, amount):
        """ Creates an update meal order line entries in db & returns created/found entities.
        """
        query_tuple = (update_order.entity, load_flt_entity, cons_flt_entity, main_cat_entity, meal_entity,
                       special_entity,)
        try:
            special_order_line_entity = TM.meal_spc_order_upd_line[query_tuple]
            special_order_line_entity.amount += amount
        except EntityNotFoundError:
            special_order_line_entity = TM.meal_spc_order_upd_line.create(query_tuple)
            special_order_line_entity.amount = amount

        return SpecialMealOrderLine(loadDate=special_order_line_entity.load_flight.udor,
                                    loadFlight=special_order_line_entity.load_flight.fd,
                                    loadDepAirport=special_order_line_entity.load_flight.adep.id,
                                    consDate=special_order_line_entity.cons_flight.udor,
                                    consFlight=special_order_line_entity.cons_flight.fd,
                                    consDepAirport=special_order_line_entity.cons_flight.adep.id,
                                    consArrAirport=special_order_line_entity.cons_flight.ades.id,
                                    mainCat=special_order_line_entity.maincat.id,
                                    mealCode=special_order_line_entity.meal_code.code,
                                    mealDescription=special_order_line_entity.meal_code.description,
                                    special_meal_code=special_entity,
                                    amount=amount,
                                    loadFlightSobt=special_order_line_entity.load_flight.sobt)


    def createOrderEntry(self, forecast, startDate, endDate, supplier_entity, station_entity,
                    company_entity, region_entity, runDate, runByUser=None):
        """Creates a new meal order entry in db & returns the new order and found entities.
        """
        if forecast:
            sequence = "seq_meal_forecast"
        else:
            sequence = "seq_meal_order"
        orderNo = DMF.BorrowConnection(TM.conn()).getNextSeqValue(sequence)
        log.info("Creating new %s: %d" % (('meal order','meal forecast')[forecast], orderNo))

        try:
            customer_entity = TM.meal_customer[(company_entity, region_entity)]
        except Exception, e:
            raise CustomerNotFoundError('Customer (%s,%s) not valid. error:%s' % (company_entity.id, region_entity.id, e))

        try:
            order_entity  = TM.meal_order.create((orderNo, forecast))
        except EntityError, e:
            # Try updating sequence if it is out of synch
            self.repairOrderSequence(orderNo, forecast)
            orderNo = DMF.BorrowConnection(TM.conn()).getNextSeqValue(sequence)
            log.info('Trying again to create the same now with orderNo:%s' % orderNo)
            order_entity  = TM.meal_order.create((orderNo, forecast))
        order_entity.order_date = runDate
        order_entity.supplier = supplier_entity
        order_entity.customer = customer_entity
        order_entity.load_station = station_entity
        order_entity.sent = False
        order_entity.cancelled = False
        order_entity.from_date = AbsTime(startDate)
        order_entity.to_date = AbsTime(endDate)
        order_entity.username = runByUser or getpass.getuser()

        supplier = MealSupplier(supplierId = supplier_entity.supplier_id,
                                name = supplier_entity.company,
                                department = supplier_entity.department,
                                station = getattr(supplier_entity.station, "id", ""),
                                phone1 = supplier_entity.phone1,
                                phone2 = supplier_entity.phone2,
                                fax = supplier_entity.fax,
                                email = supplier_entity.email,
                                sita_email = supplier_entity.sita_email,
                                pdf = supplier_entity.pdf,
                                xml = supplier_entity.xml)

        customer = MealCustomer(name = customer_entity.company.id,
                                regionName = customer_entity.region.id,
                                regionFullName = customer_entity.region.name,
                                department = customer_entity.department,
                                phone1 = customer_entity.phone1,
                                phone2 = customer_entity.phone2,
                                fax = customer_entity.fax,
                                email = customer_entity.email,
                                invoiceCompanyName = customer_entity.invoicecompanyname,
                                invoiceControlStaff = customer_entity.invoicecontrolstaff,
                                invoiceAddrName = customer_entity.invoiceaddrname,
                                invoiceAddrLine1 = customer_entity.invoiceaddrline1,
                                invoiceAddrLine2 = customer_entity.invoiceaddrline2,
                                invoiceAddrLine3 = customer_entity.invoiceaddrline3)

        order = MealOrder(order_entity.order_number,
                          order_entity.order_date,
                          order_entity.load_station.id,
                          order_entity.load_station.name,
                          forecast,
                          None, # TODO NOT UPDATE
                          order_entity.sent,
                          order_entity.cancelled,
                          order_entity.from_date,
                          order_entity.to_date,
                          supplier,
                          customer,
                          order_entity.username,
                          order_entity,
                          [])

        return order


    def createOrderLineEntry(self, order, loadFlight_entity, consFlight_entity, mainCat, mealConsCodes, amount,
                             special_meals):
        """Creates a new meal order line entries in db & returns created/found entities.
        """
        try:
            mainCat_entity= TM.crew_category_set[(mainCat,)]
        except Exception, e:
            raise CrewCategoryNotFoundError("CrewCategory (%s) is not valid. error:%s" % (mainCat, e))

        orderLine_entities = []
        for mealConsCode in mealConsCodes.split(','):
            try:
                meal_entity = TM.meal_code[(mealConsCode,)]
            except Exception, e:
                raise MealCodeNotFoundError("Meal Code (%s) is not valid. error:%s" % (mealConsCode, e))

            order_line_tuple = (order.entity, loadFlight_entity, consFlight_entity, mainCat_entity, meal_entity,)
            try:
                orderLine_entity = TM.meal_order_line[order_line_tuple]
                orderLine_entity.amount += amount
                if not orderLine_entity in orderLine_entities:
                    orderLine_entities.append(orderLine_entity)
                    log.info("Found duplicate of orderline entity:\n%s,%s,%s,%s" % \
                             (loadFlight_entity, consFlight_entity, mainCat_entity, meal_entity))

            except EntityNotFoundError:
                orderLine_entity = TM.meal_order_line.create(order_line_tuple)
                orderLine_entity.amount = amount
                orderLine_entities.append(orderLine_entity)


            orderLine = MealOrderLine(loadDate = orderLine_entity.load_flight.udor,
                                      loadFlight = orderLine_entity.load_flight.fd,
                                      loadDepAirport = orderLine_entity.load_flight.adep.id,
                                      consDate = orderLine_entity.cons_flight.udor,
                                      consFlight = orderLine_entity.cons_flight.fd,
                                      consDepAirport = orderLine_entity.cons_flight.adep.id,
                                      consArrAirport = orderLine_entity.cons_flight.ades.id,
                                      mainCat = orderLine_entity.maincat.id,
                                      mealCode = orderLine_entity.meal_code.code,
                                      mealDescription = orderLine_entity.meal_code.description,
                                      amount = amount,
                                      loadFlightSobt = orderLine_entity.load_flight.sobt)

            order.addOrderLine(orderLine)

            for special_meal_code, amount in special_meals.iteritems():
                try:
                    special_meal_code_entity = TM.meal_special_code_set[(special_meal_code,)]
                except Exception, e:
                    raise MealCodeNotFoundError("Meal Code (%s) is not valid. error:%s" % (special_meal_code, e))
                special_order_line_tuple = order_line_tuple + (special_meal_code_entity,)
                try:
                    special_line_entity = TM.meal_special_order_line[special_order_line_tuple]
                    special_line_entity.amount += amount
                    if not special_line_entity in orderLine_entities:
                        orderLine_entities.append(orderLine_entity)
                        log.info("Found duplicate of orderline entity:\n%s,%s,%s,%s" % \
                                 (loadFlight_entity, consFlight_entity, mainCat_entity, meal_entity))
                except EntityNotFoundError:
                    special_line_entity = TM.meal_special_order_line.create(special_order_line_tuple)
                    special_line_entity.amount = amount
                    orderLine_entities.append(special_line_entity)

                special_meal_line = SpecialMealOrderLine(
                    loadDate = special_line_entity.load_flight.udor,
                    loadFlight = special_line_entity.load_flight.fd,
                    loadDepAirport = special_line_entity.load_flight.adep.id,
                    consDate = special_line_entity.cons_flight.udor,
                    consFlight = special_line_entity.cons_flight.fd,
                    consDepAirport = special_line_entity.cons_flight.adep.id,
                    consArrAirport = special_line_entity.cons_flight.ades.id,
                    mainCat = special_line_entity.maincat.id,
                    mealCode = special_line_entity.meal_code.code,
                    mealDescription = special_line_entity.meal_code.description,
                    special_meal_code = special_line_entity.special_meal_code,
                    amount = amount,
                    loadFlightSobt = orderLine_entity.load_flight.sobt
                )
                order.addOrderLine(special_meal_line)


    def getSupplierEntity(self, supplierId, region, startDate, service_type):
        try:
            supplier_entity  = TM.meal_supplier.search(
                '(&(supplier_id=%s)(region=%s)(validfrom <= %s)(validto > %s)(pref_stc=%s))' %
                (supplierId, region, startDate, startDate, service_type)).next()
        except:
            #Try getting the supplier with pref_stc code " "
            try:
                supplier_entity  = TM.meal_supplier.search(
                    '(&(supplier_id=%s)(region=%s)(validfrom <= %s)(validto > %s)(pref_stc=%s))' %
                    (supplierId, region, startDate, startDate, " ")).next()
            except:
                #Try getting the supplier without pref_stc code
                try:
                    supplier_entity  = TM.meal_supplier.search(
                        '(&(supplier_id=%s)(region=%s)(validfrom <= %s)(validto > %s))' %
                        (supplierId, region, startDate, startDate)).next()
                except StopIteration, e:
                    raise SupplierNotFoundError('Supplier (id=%s, date=%s, region=%s, type=%s) not valid. error:%s' %
                                                (supplierId, startDate, region, service_type, e))

        return supplier_entity

    def getStationEntity(self, station):
        try:
            station_entity  = TM.airport[(station,)]
        except Exception, e:
            raise StationNotFoundError("Station %s is not valid. error:%s" % (station, e))
        return station_entity

    def getFlightEntity(self, flightStart, flightDescr, airport_entity):
        try:
            flight_entity = TM.flight_leg[(AbsTime(flightStart), flightDescr, airport_entity)]
        except Exception, e:
            raise FlightNotFoundError(
                "Flight (%s,%s,%s) is not valid. error:%s" %
                (flightStart, flightDescr, airport_entity.id, e))
        return flight_entity

    def getOrderLineEntity(self, consFlight_entity, mainCat_entity, meal_entitiy):
        search_str = "(&(order.forecast=false)(order.cancelled=false)(order.sent=true)"
        search_str += "(cons_flight.udor=%s)(cons_flight.fd=%s)(cons_flight.adep=%s)" % (consFlight_entity.udor, consFlight_entity.fd, consFlight_entity.adep.id)
        search_str += "(maincat.id=%s)" % (mainCat_entity.id)
        search_str += "(meal_code.code=%s))" % (meal_entitiy.code)

        order_line_entity = None
        nof_order_lines = 0

        for order_line in TM.meal_order_line.search(search_str):
            order_line_entity = order_line
            nof_order_lines += 1

        if nof_order_lines > 1:
            log.warning("Not expecting more than one meal order line")

        return order_line_entity

    def get_special_order_line_entity(self, cons_flight_entity, main_cat_entity, meal_entity, special_meal_entity):
        query = [
            '(&(order.forecast=false)(order.cancelled=false)(order.sent=true)',
            '(cons_flight.udor=%s)(cons_flight.fd=%s)' % (cons_flight_entity.udor, cons_flight_entity.fd),
            '(cons_flight.adep=%s)(maincat.id=%s)' % (cons_flight_entity.adep.id, main_cat_entity.id),
            '(meal_code.code=%s)(special_meal_code=%s))' % (meal_entity.code, special_meal_entity.id)
        ]
        seq = [x for x in TM.meal_special_order_line.search(''.join(query))]

        if len(seq) > 1:
            log.warning("Not expecting more than one special meal order line")

        return seq[0] if len(seq) else None

    def getOrderEntity(self, load_date, loadStn_entity, supplier_entity, region_entity):
        """ Gets original order. There can only be one per day and station. The supplier
            is however also a part of the search. 
         
        """

        order_entity = None

        searchStr = "(&(forecast=false)(sent=true)(cancelled=false)(supplier.supplier_id=%s)(supplier.region=%s)(customer.region=%s)(load_station.id=%s)(from_date=%s)(to_date=%s))" % \
                    (supplier_entity.supplier_id, supplier_entity.region.id, region_entity.id, loadStn_entity.id, AbsDate(load_date), AbsDate(load_date))

        daily_orders = TM.meal_order.search(searchStr)

        nof_orders = 0
        for order in daily_orders:
            order_entity = order
            nof_orders += 1

        if nof_orders > 1:
            raise MultipleEntries("Found many orders")

        # Okay, we didn't find any sent order. Check if there are any unsent orders that we can
        # use the order number from. The entries will however not be used.
        if nof_orders == 0:
            searchStr = "(&(forecast=false)(cancelled=false)(supplier.supplier_id=%s)(supplier.region=%s)(customer.region=%s)(load_station.id=%s)(from_date=%s)(to_date=%s))" % \
                        (supplier_entity.supplier_id, supplier_entity.region.id, region_entity.id, loadStn_entity.id, AbsDate(load_date), AbsDate(load_date))

            daily_orders = TM.meal_order.search(searchStr)

            for order in daily_orders:
                order_entity = order

        if order_entity is None:
            log.warning('Unable to find existing order for %s %s %s %s' %
                        (load_date, loadStn_entity, supplier_entity, region_entity))

        return order_entity


    def update_order_exists(self, loadFlight_entity):
        """ Checks if an update order already exists for a certain load flight 
        """
        search_str = "(&(load_flight.udor=%s)(load_flight.fd=%s))" % (loadFlight_entity.udor, loadFlight_entity.fd)
        print("### DEBUG ### SKCMS-1169: update_order_exists searchStr=%s" % (search_str))
        daily_orders = TM.meal_order_update_line.search(search_str)

        # There may exists many update order lines for a certain flight
        for dummy in daily_orders:
            print("### DEBUG ### SKCMS-1169: An update order exists - returns True")
            return True
        print("### DEBUG ### SKCMS-1169: An update order does not exists - returns False")
        return False



#################  main #################

from carmusr.HelperFunctions import utc2lt
from utils.RaveData import DataClass
from utils.divtools import fd_parser

#################  Data holding classes #################

class MealSupplier(DataClass):
    def __init__(self, supplierId, name, department, station, phone1, phone2,
                 fax, email, sita_email, pdf, xml):
        self.supplierId = supplierId
        self.name = name
        self.department = department
        self.station = station
        self.phone1 = phone1
        self.phone2 = phone2
        self.fax = fax
        self.email = email
        self.sita_email = sita_email
        self.pdf = pdf
        self.xml = xml


class MealCustomer(DataClass):
    def __init__(self, name, regionName, regionFullName, department, phone1, phone2, fax,
                 email, invoiceCompanyName, invoiceControlStaff, invoiceAddrName,
                 invoiceAddrLine1, invoiceAddrLine2, invoiceAddrLine3):
        self.name = name
        self.regionName = regionName
        self.regionFullName = regionFullName
        self.department = department
        self.phone1 = phone1
        self.phone2 = phone2
        self.fax = fax
        self.email = email
        self.invoiceCompanyName = invoiceCompanyName
        self.invoiceControlStaff = invoiceControlStaff
        self.invoiceAddrName = invoiceAddrName
        self.invoiceAddrLine1 = invoiceAddrLine1
        self.invoiceAddrLine2 = invoiceAddrLine2
        self.invoiceAddrLine3 = invoiceAddrLine3


class MealOrderLine(DataClass):
    """ Represents both ordinary meal order lines and update order lines

    """
    def __init__(self, loadDate, loadFlight, loadDepAirport,
                 consDate, consFlight, consDepAirport, consArrAirport,
                 mainCat, mealCode, mealDescription, amount, loadFlightSobt):
        self.loadDate = loadDate
        self.loadFlight = formatFlightName(loadFlight)
        self.loadDepAirport = loadDepAirport
        self.consDate = consDate
        self.consFlight = formatFlightName(consFlight)
        self.consDepAirport = consDepAirport
        self.consArrAirport = consArrAirport
        self.mainCat = mainCat
        self.mealCode = mealCode
        self.mealDescription = mealDescription
        self.amount = amount
        self.loadDepDateLt = utc2lt(loadDepAirport, loadFlightSobt)

    def __cmp__(self, other):
        """
        Compares two order lines so that they
        may be sorted.
        """
        if other == None:
            return -1

        for s, o in [(self.loadFlight, other.loadFlight),
                     (self.consFlight, other.consFlight),
                     (self.loadDate, other.loadDate),
                     (self.loadDepAirport, other.loadDepAirport),
                     (self.loadDepAirport, other.loadDepAirport),
                     (self.consDate, other.consDate),
                     (self.mainCat, other.mainCat),
                     (self.mealCode, other.mealCode),
                     (self.consDepAirport, other.consDepAirport),
                     (self.mealDescription, other.mealDescription)]:

            compare =  cmp(s,o)
            if compare != 0:
                return compare

        return 0


class MealOrder(DataClass):
    """ Represents both ordinary meal orders and update orders

    """

    def __init__(self, orderNumber, date, loadStation, airportName,
                 forecast, originalOrderNumber, sent, cancelled, fromDate, toDate, supplier,
                 customer, username, entity, orderLines):
        self.orderNumber = orderNumber
        self.date = date
        self.loadStation = loadStation
        self.airportName = airportName
        self.forecast = forecast
        self.originalOrderNumber = originalOrderNumber
        self.update_order = originalOrderNumber is not None
        # Updates are made flight wise, this variable is used to find out the flight that
        # this order relates to.
        self.update_order_flight  = None
        self.sent = sent
        self.cancelled = cancelled
        self.fromDate = fromDate
        self.toDate = toDate
        self.supplier = supplier
        self.customer = customer
        self.username = username
        self.orderLines = orderLines
        self.entity = entity

        if self.update_order and self.orderLines is not None and len(self.orderLines) > 0:
            self.update_order_flight = self.orderLines[0].loadFlight

    def addOrderLine(self, line):
        """ Adds an order line class or increases the amount if the order already
            exists .For an update order the load flight is set.
        """

        if line in self.orderLines:
            order = self.orderLines[self.orderLines.index(line)]
            order.amount += line.amount
        else:
            self.orderLines.append(line)

        if self.update_order:
            self.update_order_flight = line.loadFlight

    def __str__(self):
        datastrlist = []
        classstrlist = []
        for (name, val) in self.__dict__.iteritems():
            if isinstance(val, DataClass):
                classstrlist.append('%s:%s\n'%(name, val))
            elif not callable(val):
                datastrlist.append('%s:%s\n'%(name, val))
        for orderline in self.orderLines:
            classstrlist.append('%s'%(orderline))
        return "\n### Mealorder\n"+"".join(datastrlist)+"".join(classstrlist)+"###  Mealorder end\n"


class SpecialMealOrderLine(MealOrderLine):
    def __init__(self, loadDate, loadFlight, loadDepAirport,
                 consDate, consFlight, consDepAirport, consArrAirport,
                 mainCat, mealCode, mealDescription, special_meal_code, amount, loadFlightSobt):

        MealOrderLine.__init__(self, loadDate, loadFlight, loadDepAirport, consDate, consFlight,
                               consDepAirport, consArrAirport, mainCat, mealCode,
                               mealDescription,
                               amount, loadFlightSobt)
        self.special_meal_code = special_meal_code

    def __cmp__(self, other):
        res = MealOrderLine.__cmp__(self, other)
        if res == 0 and self.__class__ == other.__class__:
            return cmp(self.special_meal_code, other.special_meal_code)
        elif res == 0:
            return 1
        else:
            return res

############### helper functions ###############

def formatFlightName(raveFlightId):
    """Format rave's 'sk 000736 ' to SAS's 'SK 0736'
    """
    fl = fd_parser(raveFlightId)
    sasFlightId = '%s %04d%s' % (fl.carrier, fl.number, fl.suffix)
    return sasFlightId
"""
Creates a meal info report for a flight. It contains information about loaded 
and consumed meals.

"""

from copy import copy

import Cui
import carmensystems.rave.api as R
from AbsDate import AbsDate
from carmensystems.publisher.api import *

from report_sources.include.SASReport import SASReport
from tm import TM
from utils.divtools import fd_parser
from utils.rave import MiniEval


class Evaluator(dict):
    """Evaluate some values on current leg."""
    def __init__(self, fields):
        dict.__init__(self)
        self.area = Cui.CuiGetCurrentArea(Cui.gpc_info)
        me = MiniEval(fields)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, self.area, 'object')
        self.update(me.eval(R.selected(R.Level.atom())).__dict__)

    def __getattr__(self, key):
        return self.get(key, None)


class FlightValues(Evaluator):
    """ Represents a flight """

    def __init__(self, additional_fields={}):
        fields = {
            'now': 'fundamental.%now%',
            'ac_type': 'leg.%ac_type%',
            'adep': 'leg.%start_station%',
            'ades': 'leg.%end_station%',
            'category_code': 'leg.%category_code%',
            'code': 'leg.%code%',
            'flight_descriptor': 'leg.%flight_descriptor%',
            'flight_name': 'leg.%flight_name%',
            'group_code_description': 'leg.%group_code_description%',
            'is_flight': 'leg.%is_flight_duty%',
            'is_ground_duty': 'leg.%is_ground_duty%',
            'is_pact': 'leg.%is_pact%',
            'sta': 'leg.%end_UTC%',
            'sta_lt': 'leg.%end_lt%',
            'std': 'leg.%start_UTC%',
            'std_lt': 'leg.%start_lt%',
            'tail_id': 'leg.%tail_id%',
            'udor': 'leg.%udor%',
            'uuid': 'leg.%uuid%',
            }
        fields.update(additional_fields)
        Evaluator.__init__(self, fields)

        self.flight_id = self.flight_descriptor + self.adep + self.ades


class Meal(object):
    """ Represents a meal """

    def __init__(self, loadDate,
                 loadFlight, loadDepTime, loadArrTime, loadDepAirport, loadArrAirport,
                 consFlight, consDepTime, consArrTime, consDepAirport, consArrAirport,
                 mainCat, mealCode, mealDescription, amount):
        self.loadDate = loadDate
        self.loadFlight = loadFlight
        self.loadDepTime = loadDepTime
        self.loadArrTime = loadArrTime
        self.loadDepAirport = loadDepAirport
        self.loadArrAirport = loadArrAirport
        self.consDepTime = consDepTime
        self.consArrTime = consArrTime
        self.consFlight = consFlight
        self.consDepAirport = consDepAirport
        self.consArrAirport = consArrAirport
        self.mainCat = mainCat
        self.mealCode = mealCode
        self.mealDescription = mealDescription.strip()
        self.amount = amount

        self.load_flight_id = loadFlight + loadDepAirport + loadArrAirport
        self.cons_flight_id = consFlight + consDepAirport + consArrAirport


    def __cmp__(self, other):
        """
        Compares two order lines so that they
        may be sorted by consumption flight number.
        """
        res = cmp(self.loadFlight, other.loadFlight)
        if res != 0:
            return res

        res = cmp(self.consFlight, other.consFlight)
        if res != 0:
            return res

        res = cmp((self.mainCat, self.mealCode), (other.mainCat, other.mealCode))
        if res != 0:
            return res
        elif self.__class__ != other.__class__:
            return -1
        else:
            return 0


class SpecialMeal(Meal):
    """ Represents a meal """

    def __init__(self, **kwargs):
        self.special_meal_code = kwargs.pop('special_meal_code')
        super(SpecialMeal, self).__init__(**kwargs)

    def __cmp__(self, other):
        res = cmp(self.loadFlight, other.loadFlight)
        if res != 0:
            return res

        res = cmp(self.consFlight, other.consFlight)
        if res != 0:
            return res

        res = cmp((self.mainCat, self.mealCode), (other.mainCat, other.mealCode))
        if res != 0:
            return res

        if self.__class__ == other.__class__:
            return cmp(self.special_meal_code, other.special_meal_code)
        else:
            return 1

class MealOrder(object):
    """ Represents a meal order """

    def __init__(self, order_num, order_date, supplier_company, supplier_station, customer_company, customer_region):
        self.order_num = order_num
        self.order_date = order_date
        self.supplier_company = supplier_company
        self.supplier_station= supplier_station
        self.customer_company = customer_company
        self.customer_region = customer_region

    def __cmp__(self, other):
        return cmp(self.order_num, other.order_num)


class MealTable(object):
    """ Represents a load meal table """

    def __init__(self):

        self.bg_color = 'ffffff'

        self.col = Column(Row(Text('Load Leg',
                                   colspan=6,
                                   border=border(top=1, bottom=1),
                                   background='#cdcdcd',
                                   align=CENTER),
                              Text(' '),
                              Text('Consumption Leg',
                                   colspan=5,
                                   border=border(top=1, bottom=1),
                                   background='#cdcdcd',
                                   align=CENTER)))

        self.col.add(Row(Column(Text(' '), Text('Date')),
                         Column(Text(' '), Text('Flight')),
                         Column(Text(' '), Text('Meal')),
                         Column(Text(' '), Text('Info')),
                         Column(Text('From'), Text('Station')),
                         Column(Text('To'), Text('Station')),
                         Text(' '),
                         Column(Text(' '), Text('Quantity')),
                         Column(Text('FD'), Text('CC')),
                         Column(Text(' '), Text('Flight')),
                         Column(Text('From'), Text('Station')),
                         Column(Text('To'), Text('Station')),
                         font=font(weight=BOLD)))


    def add_entry(self, meal):
        """Adds an entry to the meal table """

        if self.bg_color == 'ffffff':
            self.bg_color = 'dedede'
        else:
            self.bg_color = 'ffffff'

        self.col.add(Row(Text('%s-%02d-%02d' % meal.loadDate.split()[:3], background='#%s' % self.bg_color),
                         Text(formatFlightName(meal.loadFlight), background='#%s' % self.bg_color),
                         Text('%s - %s' % (meal.mealCode, meal.mealDescription), background='#%s' % self.bg_color),
                         Text(
                             meal.special_meal_code.id
                             if isinstance(meal, SpecialMeal)
                             else '' , background='#%s' % self.bg_color),
                         Text('%s' % meal.loadDepAirport, background='#%s' % self.bg_color),
                         Text('%s' % meal.loadArrAirport, background='#%s' % self.bg_color),
                         Text(' '),
                         Text('%s' % meal.amount, background='#%s' % self.bg_color),
                         Text('%s' % ('FD','CC')[meal.mainCat == 'C'], background='#%s' % self.bg_color),
                         Text(formatFlightName(meal.consFlight),  background='#%s' % self.bg_color),
                         Text('%s' % meal.consDepAirport, background='#%s' % self.bg_color),
                         Text('%s' % meal.consArrAirport, background='#%s' % self.bg_color)))


class OrderTable(object):
    """ Represents an order table """

    def __init__(self):

        self.bg_color = 'ffffff'

        self.col = Column(Row(
            Column(Text(' '), Text('Order Number')),
            Column(Text(' '), Text('Order Date')),
            Column(Text(' '), Text('Supplier')),
            Column(Text(' '), Text('Customer')),
            font=font(weight=BOLD)
        ))


    def add_entry(self, order):
        """ Adds an order entry to the table """

        if self.bg_color == 'ffffff':
            self.bg_color = 'dedede'
        else:
            self.bg_color = 'ffffff'

        self.col.add(Row(
            Text(order.order_num, background='#%s' % self.bg_color),
            Text('%s-%02d-%02d' % order.order_date.split()[:3], background='#%s' % self.bg_color),
            Text("%s/%s" % (order.supplier_station, order.supplier_company), background='#%s' % self.bg_color),
            Text('%s/%s' % (order.customer_company, order.customer_region), background='#%s' % self.bg_color)
        ))



# PRT formatting functions ===============================================
def AText(*a, **k):
    """Text aligned to BOTTOM (used as 'base' class). """
    k['valign'] = BOTTOM
    return Text(*a, **k)


def H1(*a, **k):
    """Header text level 1: size 12, bold, space above."""
    k['font'] = Font(size=12, weight=BOLD)
    # Add some space on top of the header.
    k['padding'] = padding(2, 12, 2, 2)
    return AText(*a, **k)

def H2(*a, **k):
    """Header text level 2: size 9 bold."""
    k['font'] = Font(size=9, weight=BOLD)
    return AText(*a, **k)


def RowSpacer(*a, **k):
    """An empty row of height 12."""
    k['height'] = 12
    return Row(*a, **k)


def formatFlightName(raveFlightId):
    """Format rave's 'sk 000736 ' to SAS's 'SK 0736'
    """
    fl = fd_parser(raveFlightId)
    sasFlightId = '%s %04d%s' % (fl.carrier, fl.number, fl.suffix)
    return sasFlightId


# OrderedMeals (the PRT report) ========================================{{{1
class OrderedMeals(SASReport):
    """The actual report, using PRT toolkit."""

    def create(self):
        """ Create the report """
        SASReport.create(self, 'Crew Meal - Ordered Meals', False)

        # Flight information
        flight = FlightValues()
        self.add(H1("Flight Information"))
        self.add(Text("%s %s %s - %s" % (formatFlightName(flight.flight_descriptor),
                                         str(flight.udor).split()[0],
                                         flight.adep, flight.ades)))
        self.add(RowSpacer())


        # Get meal orders
        ordered_meals = []
        orders = []

        self._get_daily_orders(flight, ordered_meals, orders)
        self._get_update_orders(flight, ordered_meals, orders)

        ordered_meals.sort()
        orders.sort()

        # Ordered meals
        self.add(H1("Crew  Meals"))

        if len(ordered_meals) > 0:

            # The load meal table
            load_meal_table = MealTable()

            for meal in ordered_meals:
                load_meal_table.add_entry(meal)

            self.add(load_meal_table.col)

            self.add(RowSpacer())

        else:
            self.add(Text("No load or consumption meals for this flight"))

        # The meal orders
        self.add(H1("Booked Orders"))

        if len(orders) == 0:
            self.add(AText("No order data"))
        else:
            order_table = OrderTable()
            self.add(order_table.col)
            for order in orders:
                order_table.add_entry(order)


    def _get_daily_orders(self, flight, meals, orders):
        """ Get all daily orders related for the flight """

        mealSearchStr = "(&(forecast=false)(sent=true)(cancelled=false)" +\
                        "(from_date=%s)(to_date=%s))" % (flight.udor, flight.udor)

        for order in TM.meal_order.search(mealSearchStr):
            order_added = False

            for order_line in TM.meal_order_line.search('(order.order_number=%s)' % order.order_number):

                meal = Meal(order_line.load_flight.udor,
                            order_line.load_flight.fd,
                            order_line.load_flight.sobt,
                            order_line.load_flight.sibt,
                            order_line.load_flight.adep.id,
                            order_line.load_flight.ades.id,
                            order_line.cons_flight.fd,
                            order_line.cons_flight.sobt,
                            order_line.cons_flight.sibt,
                            order_line.cons_flight.adep.id,
                            order_line.cons_flight.ades.id,
                            order_line.maincat.id,
                            order_line.meal_code.code,
                            order_line.meal_code.description,
                            order_line.amount)

                order_added = self._add_or_increase_meal(flight, meal, meals) or order_added

            for order_line in TM.meal_special_order_line.search('(order.order_number=%s)' % order.order_number):

                special_meal = SpecialMeal(
                    loadDate=order_line.load_flight.udor,
                    loadFlight=order_line.load_flight.fd,
                    loadDepTime=order_line.load_flight.sobt,
                    loadArrTime=order_line.load_flight.sibt,
                    loadDepAirport=order_line.load_flight.adep.id,
                    loadArrAirport=order_line.load_flight.ades.id,
                    consFlight=order_line.cons_flight.fd,
                    consDepTime=order_line.cons_flight.sobt,
                    consArrTime=order_line.cons_flight.sibt,
                    consDepAirport=order_line.cons_flight.adep.id,
                    consArrAirport=order_line.cons_flight.ades.id,
                    mainCat=order_line.maincat.id,
                    mealCode=order_line.meal_code.code,
                    mealDescription=order_line.meal_code.description,
                    amount=order_line.amount,
                    special_meal_code=order_line.special_meal_code
                )

                order_added = self._add_or_increase_meal(flight, special_meal, meals) or order_added

            if order_added:
                # The supplier station may be Null in some cases
                if order.supplier.station is None:
                    supplier_station = "*"
                else:
                    supplier_station = order.supplier.station.id

                orders.append(MealOrder(order.order_number,
                                        order.order_date,
                                        order.supplier.company,
                                        supplier_station,
                                        order.customer.company.id,
                                        order.customer.region.id))

    def _get_update_orders(self, flight, meals, orders):
        """ Get all update orders related for the flight """

        search_str = "(&(sent=true)(cancelled=false)(from_date=%s)(to_date=%s))" % (flight.udor, flight.udor)

        for order in TM.meal_order_update.search(search_str):

            order_added = False

            for order_line in TM.meal_order_update_line.search('(order.order_update_num=%s)' % order.order_update_num):

                meal = Meal(order_line.load_flight.udor,
                            order_line.load_flight.fd,
                            order_line.load_flight.sobt,
                            order_line.load_flight.sibt,
                            order_line.load_flight.adep.id,
                            order_line.load_flight.ades.id,
                            order_line.cons_flight.fd,
                            order_line.cons_flight.sobt,
                            order_line.cons_flight.sibt,
                            order_line.cons_flight.adep.id,
                            order_line.cons_flight.ades.id,
                            order_line.maincat.id,
                            order_line.meal_code.code,
                            order_line.meal_code.description,
                            order_line.amount)

                order_added = self._add_or_increase_meal(flight, meal, meals) or order_added

            for order_line in TM.meal_slpc_order_upd_line.search('(order.order_update_num=%s)' % order.order_update_num):

                special_meal = SpecialMeal(
                    loadDate=order_line.load_flight.udor,
                    loadFlight=order_line.load_flight.fd,
                    loadDepTime=order_line.load_flight.sobt,
                    loadArrTime=order_line.load_flight.sibt,
                    loadDepAirport=order_line.load_flight.adep.id,
                    loadArrAirport=order_line.load_flight.ades.id,
                    consFlight=order_line.cons_flight.fd,
                    consDepTime=order_line.cons_flight.sobt,
                    consArrTime=order_line.cons_flight.sibt,
                    consDepAirport=order_line.cons_flight.adep.id,
                    consArrAirport=order_line.cons_flight.ades.id,
                    mainCat=order_line.maincat.id,
                    mealCode=order_line.meal_code.code,
                    mealDescription=order_line.meal_code.description,
                    amount=order_line.amount,
                    special_meal_code=order_line.special_meal_code
                )

                order_added = self._add_or_increase_meal(flight, special_meal, meals) or order_added

            if order_added:
                orders.append(MealOrder(order.order_update_num,
                                        AbsDate(order.creation_time),
                                        order.supplier.company,
                                        order.supplier.station.id,
                                        order.customer.company.id,
                                        order.customer.region.id))

    def _add_or_increase_meal(self, flight, meal, meals):
        if meal.cons_flight_id == flight.flight_id or meal.load_flight_id == flight.flight_id:
            # If the meal exists in the meals list, just increase the the amount of meals
            if not meal in meals:
                meals.append(copy(meal))
            else:
                indx = meals.index(meal)
                meals[indx].amount += meal.amount
            return True
        else:
            return False

# runReport --------------------------------------------------------------{{{2
def runReport():
    """Run the report (from outside.)"""
    Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiWhichArea,'object', "OrderedMeals.py", 0, 0)


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    runReport()

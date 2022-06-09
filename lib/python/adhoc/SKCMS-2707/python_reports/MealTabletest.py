"""
Move this python file to lib/python/report_sources/hidden/ 
Also make sure that the file lib/python/report_sources/report_server/rs_mealtabletest.py is available in the carmusr 
"""

from utils.xmlutil import XMLElement,XMLDocument
from AbsTime import AbsTime
from RelTime import RelTime
from tm import TM
from datetime import datetime
from utils.airport_tz import Airport
import carmensystems.rave.api as rave


def fetch_data(now,creatime_offset,deadline_offset):
 
    i = 1
    for order in TM.meal_spc_order_upd_line:
        print "The record count is ", i, "and the result is : ", order.amount
            #print "The record count is ", i, "and the result is : ", mealtest.load_flight.udor, " with todate ", mealtest.cons_flight.sobt
            #print "The record count is ", i, "and the order is : ", mealtest.order.order_update_num," and the udor date is ",  mealtest.load_flight.udor, " with todate ", mealtest.cons_flight.sobt
            #print "The record count is ", i, "and the order is : ", mealtest.order.order_meal_order_order_number , " + ", mealtest.order.order_meal_order_forecast," + ", mealtest.order.order_order_update_num , " and the udor date is ",  mealtest.load_flight.udor, " with todate ", mealtest.cons_flight.sobt
        i = i+1
    return i

    

class MealTabletest():

    def __init__(self, creation_time_offset, deadline_line_offset):
        self.now, = rave.eval('fundamental.%now%')
        self.creation_time_offset = creation_time_offset
        self.dead_line_offset = deadline_line_offset

    def make_reports(self):
        data = fetch_data(self.now, self.creation_time_offset, self.dead_line_offset)
        return data


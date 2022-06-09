"""
Simple report to show aircraft minimum connection times 
which are considered in Retiming.

by Niklas Johansson in Feb 2014.

"""
import carmensystems.publisher.api as p
import carmensystems.rave.api as R
from RelTime import RelTime
from carmensystems.publisher.api import *
from operator import attrgetter

from carmstd import bag_handler
from report_sources.include.SASReport import SASReport
import os
import os.path
from datetime import datetime
from sets import Set

WeekDays = ['Mon','Tue', 'Wed','Thu','Fri','Sat', 'Sun']
Bases = ['ARN', 'OSL', 'CPH']
DATED = True
WEEKLY = False
BaseSet = Set(Bases)

def formatDate(date):
    try:
        d = date.yyyymmdd()
        return "%s-%s-%s" %(d[:4], d[4:6], d[6:])
    except:
        return str(date)

def format_weekday(int_weekday):
    return WeekDays[int_weekday]

def formatDateStr(date, dated=DATED, withTime=True):
    try:
        if dated:
            return str(date)
        else:
            time = date.time_of_day()
            int_weekday = int(date.time_of_week()/RelTime(1,0,0))
            if withTime:
                return format_weekday(int_weekday) + str(time)
            else:
                return int_weekday
    except:
        return str(date)

class AcLeg(object):
    def __init__(self, leg_bag):
        self.__end_lt = leg_bag.leg.end_lt()
        self.__end_date = leg_bag.leg.end_date_lt()
        self.__start_lt = leg_bag.leg.start_lt()
        self.__start_date = leg_bag.leg.start_date()
        self.__start_weekday = formatDateStr(self.__start_date, False, False)
        self.__end_weekday = formatDateStr(self.__end_date, False, False)
        self.__first_good_leg_start_after_night_rest = leg_bag.studio_cpe.first_good_leg_start_after_night_rest()
        self.__last_good_leg_end_before_night_rest = leg_bag.studio_cpe.last_good_leg_end_before_night_rest()
        self.__next_leg_max_connection_time = leg_bag.studio_cpe.next_leg_within_max_connection_time()
        self.__ci_start_lt = leg_bag.studio_cpe.leg_start_lt()
        self.__co_end_lt = leg_bag.studio_cpe.leg_end_lt()
        self.__arrival_airport_name = leg_bag.leg.arrival_airport_name()
        self.__departure_airport_name = leg_bag.leg.departure_airport_name()
        self.__flight_name = leg_bag.crg_info.flight_name()
        self.__base_triangle =  leg_bag.studio_cpe.base_triangle()
        self.__leg_start_before_lh =  leg_bag.studio_cpe.leg_start_before_lh()
        self.__leg_start_lt_connecting_flight_earliest_start =  leg_bag.studio_cpe.leg_start_lt_connecting_flight_earliest_start()
        self.__lh_leg_earliest_start_lt_after_connecting_flight = leg_bag.studio_cpe.lh_leg_earliest_start_lt_after_connecting_flight()
        self.__leg_end_lt_raw =  leg_bag.studio_cpe.leg_end_lt_raw()
        self.__earliest_lh_leg_end_lt_connecting_flight_to_sh = leg_bag.studio_cpe.earliest_lh_leg_end_lt_connecting_flight_to_sh()
        self.__latest_lh_leg_end_lt_connecting_flight_to_sh = leg_bag.studio_cpe.latest_lh_leg_end_lt_connecting_flight_to_sh()
        self.__lh_leg_earliest_start_lt_after_connecting_flight_relaxed = leg_bag.studio_cpe.lh_leg_earliest_start_lt_after_connecting_flight_relaxed()
        self.__lh_leg_earliest_start_lt_after_connecting_flight_extended = leg_bag.studio_cpe.lh_leg_earliest_start_lt_after_connecting_flight_extended()
    
    @property
    def end_lt(self):
        return self.__end_lt

    @property
    def end_date(self):
        return self.__end_date

    @property
    def start_lt(self):
        return self.__start_lt

    @property
    def start_date(self):
        return self.__start_date

    @property
    def start_weekday(self):
        return self.__start_weekday
    
    @property
    def end_weekday(self):
        return self.__end_weekday
    
    @property
    def first_good_leg_start_after_night_rest(self):
        return self.__first_good_leg_start_after_night_rest

    @property
    def last_good_leg_end_before_night_rest(self):
        return self.__last_good_leg_end_before_night_rest
    
    @property
    def next_leg_max_connection_time(self):
        return self.__next_leg_max_connection_time

    @property
    def ci_start_lt(self):
        return self.__ci_start_lt

    @property
    def co_end_lt(self):
        return self.__co_end_lt

    @property
    def arrival_airport_name(self):
        return self.__arrival_airport_name

    @property
    def departure_airport_name(self):
        return  self.__departure_airport_name

    @property
    def flight_name(self):
        return  self.__flight_name

    @property
    def base_triangle(self):
        return  self.__base_triangle
    
    @property
    def leg_start_before_lh(self):
        return  self.__leg_start_before_lh
        
    @property
    def leg_start_lt_connecting_flight_earliest_start(self):
        return  self.__leg_start_lt_connecting_flight_earliest_start

    @property
    def lh_leg_earliest_start_lt_after_connecting_flight(self):
        return  self.__lh_leg_earliest_start_lt_after_connecting_flight
    
    @property
    def lh_leg_earliest_start_lt_after_connecting_flight_relaxed(self):
        return  self.__lh_leg_earliest_start_lt_after_connecting_flight_relaxed
    
    @property
    def lh_leg_earliest_start_lt_after_connecting_flight_extended(self):
        return self.__lh_leg_earliest_start_lt_after_connecting_flight_extended
    
    @property
    def earliest_lh_leg_end_lt_connecting_flight_to_sh(self):
        return  self.__earliest_lh_leg_end_lt_connecting_flight_to_sh
    @property
    def latest_lh_leg_end_lt_connecting_flight_to_sh(self):
        return  self.__latest_lh_leg_end_lt_connecting_flight_to_sh

    @property
    def leg_end_lt_raw(self):
        return  self.__leg_end_lt_raw



    def is_good_connection_to_LH_flight(self, lh_leg):
        return ((lh_leg.departure_airport_name == self.arrival_airport_name) and
            (lh_leg.start_lt >= self.lh_leg_earliest_start_lt_after_connecting_flight) and
                ((lh_leg.start_lt <= self.lh_leg_earliest_start_lt_after_connecting_flight_extended) or
                 (lh_leg.leg_start_lt_connecting_flight_earliest_start <= self.ci_start_lt)))
        
    def is_almost_good_connection_to_LH_flight(self, lh_leg):
        return ((lh_leg.departure_airport_name == self.arrival_airport_name) and
            (lh_leg.start_lt >= self.lh_leg_earliest_start_lt_after_connecting_flight_relaxed) and
                ((lh_leg.start_lt <= self.lh_leg_earliest_start_lt_after_connecting_flight_extended) or
                 (lh_leg.leg_start_lt_connecting_flight_earliest_start <= self.ci_start_lt)))

    def is_good_connection_from_LH_flight(self, lh_leg):
        return ((lh_leg.arrival_airport_name == self.departure_airport_name) and
            (lh_leg.leg_end_lt_raw <= self.earliest_lh_leg_end_lt_connecting_flight_to_sh) and
                (lh_leg.leg_end_lt_raw >= self.latest_lh_leg_end_lt_connecting_flight_to_sh))
        
    def getLegInfo(self):
        return "flight %s start:%s end:%s next start:%s" %(self.flight_name, formatDateStr(self.start_lt), formatDateStr(self.end_lt), formatDateStr(self.first_good_leg_start_after_night_rest))

    def getCSVLegInfo(self):
        return "%s;%s;%s;%s;%s;" %(self.flight_name, formatDateStr(self.start_lt), formatDateStr(self.end_lt), self.departure_airport_name, self.arrival_airport_name)

    def getLHLegInfo(self):
        return "flight %s start:%s end:%s ss:%s es:%s" %(self.flight_name, formatDateStr(self.start_lt), formatDateStr(self.end_lt), self.departure_airport_name, self.arrival_airport_name)

    def getLHLegCSVInfo(self):
        return "%s;%s;%s;%s;%s" %(self.flight_name, formatDateStr(self.start_lt), formatDateStr(self.end_lt), self.departure_airport_name, self.arrival_airport_name)

    def getConnectingSHLegInfo(self):
        return "\tflight %s start:%s end:%s ss:%s es:%s" %(self.flight_name, formatDateStr(self.start_lt), formatDateStr(self.end_lt), self.departure_airport_name, self.arrival_airport_name)

    def getConnectingSHCSVLegInfo(self):
        return "%s;%s;%s;%s;%s;" %(self.flight_name, formatDateStr(self.start_lt), formatDateStr(self.end_lt), self.departure_airport_name, self.arrival_airport_name)

class LHLegContainer(object):
    def __init__(self, lh_leg, dated):
        self.__lh_leg = lh_leg
        self.__dated = dated
        self.__incoming_connections = []
        self.__incoming_close_connections = []
        self.__outgoing_connections = []
        self.__datedStations = []
        
    @property 
    def dated(self):
        return self.__dated

    @property 
    def flight_name(self):
        return self.__lh_leg.flight_name

    @property 
    def start_lt(self):
        return self.__lh_leg.start_lt

    @property 
    def incomings(self):
        return self.__incoming_connections

    @property 
    def closeIncomings(self):
        return self.__incoming_close_connections
    
    @property
    def outgoings(self):
        return self.__outgoing_connections

    @property
    def isProblematic(self):
        return not self._isProblematic
        
    @property
    def _isProblematic(self):
        if self.outgoing:
            return self.hasAllIncommingConnections 
        else:
            return self.hasAllOutgoingConnections
        

    @property
    def hasAllIncommingConnections(self):
        return len(self.incomings) >= 2

    @property
    def hasAllOutgoingConnections(self):
        return len(self.outgoings) >= 2

    @property
    def arrival_airport_name(self):
        return self.__lh_leg.arrival_airport_name

    @property
    def departure_airport_name(self):
        return self.__lh_leg.departure_airport_name

    @property
    def outgoing(self):
        return (self.departure_airport_name in BaseSet)

    @property
    def problem_description(self):
        return "%s ni %d no %d" %(self.__lh_leg.getLHLegInfo(), len(self.incomings), len(self.outgoings))

    @property
    def csv_problem_description(self):
        return "%s;%d;%d;" %(self.__lh_leg.getLHLegCSVInfo(), len(self.incomings), len(self.outgoings))

    def addStation(self, station):
        add = False
        if self.outgoing:
            if station.name ==  self.departure_airport_name:
                add = True
        else:
            if station.name == self.arrival_airport_name:
                add = True
        #Only stations with the same departure airport needs to be added     
        if add:
            datedStation = None
            if self.outgoing:
                datedStation = station.getDatedStation(self.dated, self.__lh_leg, True)
            else:
                datedStation = station.getDatedStation(self.dated, self.__lh_leg, False)
            if datedStation:
                self.__datedStations.append(datedStation)

    def buildModel(self):
        for ds in self.__datedStations:
            if self.outgoing:
                for leg in ds.baseIncomings:
                    if leg.is_good_connection_to_LH_flight(self.__lh_leg):
                        self.incomings.append(leg)
                    elif leg.is_almost_good_connection_to_LH_flight(self.__lh_leg):
                        self.closeIncomings.append(leg)
            else:
                for leg in ds.baseOutgoings:
                    if leg.is_good_connection_from_LH_flight(self.__lh_leg):
                        self.outgoings.append(leg)
                    
        
        
        
class DatedStation(object):
    def __init__(self, station, date):
        self.__stationRef = station
        self.__date = date
        self.__incomings = []
        self.__outgoings = []
        self.__sorted = True
        self.isFirst = False
        self.__prevDatedStation = None
        self.__nextDatedStation = None
    
    def addIncoming(self, incoming_leg):
        self.__incomings.append(incoming_leg)
        self.__sorted = False
        

    def addOutgoing(self, outgoing_leg):
        self.__outgoings.append(outgoing_leg)
        self.__sorted = False

    def setPrev(self, prev):
        self.__prevDatedStation = prev
        if prev:
            prev.setNext(self)

    def setNext(self, next):
        self.__nextDatedStation = next

    def sort(self):
        if (not self.__sorted):
            self.__sortIncomings()
            self.__sortOutgoings()
            self.__sorted = True
        
    def __sortIncomings(self):
        self.__incomings = sorted(self.__incomings, key=lambda leg: leg.end_lt)

    def __sortOutgoings(self):
        self.__outgoings = sorted(self.__outgoings, key=lambda leg: leg.start_lt)

    @property
    def isBalanced(self):
        return (len(self.__incomings) == len(self.__outgoings))
    
    @property
    def incomings(self):
        return self.__incomings

    @property
    def baseIncomings(self):
        return [elem for elem in self.__incomings if elem.base_triangle]
        
    @property
    def outgoings(self):
        return self.__outgoings
        
    @property
    def baseOutgoings(self):
        return [elem for elem in self.__outgoings if elem.base_triangle]
    
    @property
    def hasFirstNightStop(self):
        self.sort()
        _ns = True
        first = self.getFirstOutgoing
        if first:
            for inc_leg in self.__incomings:
                if (first.start_lt > inc_leg.end_lt):
                    _ns = False
                    break
        else:
            return True
        return _ns
    
    @property
    def hasLastNightStop(self):
        self.sort()
        _ns = True
        last = self.getLastIncoming
        if last:
            for out_leg in self.__outgoings:
                if (last.end_lt < out_leg.start_lt):
                    _ns = False
                    break
            else:
                return True
        return _ns
    
    @property
    def hasNightStops(self):
        return (self.hasLastNightStop or self.hasFirstNightStop)
        
    @property
    def getLastIncoming(self):
        if (len(self.__incomings) > 0):
            self.sort()
            return self.__incomings[-1]
        else:
            return None

    @property
    def getFirstIncoming(self):
        if (len(self.__incomings) > 0):
            self.sort()
            return self.__incomings[0]
        else:
            return None

    @property
    def getFirstOutgoing(self):
        if (len(self.__outgoings) > 0):
            self.sort()
            return self.__outgoings[0]
        else:
            return None
        
    @property
    def getLastOutgoing(self):
        if (len(self.__outgoings) > 0):
            self.sort()
            return self.__outgoings[-1]
        else:
            return None
        
    @property
    def date(self):
        return self.__date

    def getProblematic(self):
        problematic = []
        if self.hasNightStops:
            try:
                last = self.getLastIncoming
                lastOut = self.getLastOutgoing
                if last:
                    isProblematic = True
                    if lastOut:
                        isProblematic = (last.end_lt > lastOut.start_lt)
                    if self.__nextDatedStation:
                        if isProblematic and not self.__nextDatedStation.hasGoodOutgoingLegFor(last):
                            problematic.append((last, "Not enought night rest"))
                first = self.getFirstOutgoing
                firstInc = self.getFirstIncoming
                if first:
                    isProblematic = True
                    if firstInc:
                        isProblematic = (first.start_lt < firstInc.end_lt)
                    if self.__prevDatedStation:
                        if isProblematic and not self.__prevDatedStation.hasGoodIncomingLegFor(first):
                            problematic.append((first, "Not enought night rest before"))
            except IndexError:
                #No outgoing legs for station on this data for category
                #return (self.__outgoings[0], "Not enought night rest before")
                pass
        return problematic
        
                
    def hasGoodOutgoingLegFor(self, prevLeg):
        self.sort()
        timeCorrection = RelTime(0,0,0)
        for out_leg in self.__outgoings:
            if (out_leg.start_lt < prevLeg.start_lt):
                timeCorrection = RelTime(7,0,0)
            if ((prevLeg.first_good_leg_start_after_night_rest <= (out_leg.ci_start_lt + timeCorrection)) or
            (prevLeg.next_leg_max_connection_time >= (out_leg.start_lt + timeCorrection))
                ):
                return True
        return False

    def hasGoodIncomingLegFor(self, nextLeg):
        self.sort()
        timeCorrection = RelTime(0,0,0)
        for in_leg in self.__incomings:
            try:
                if (in_leg.start_lt > nextLeg.start_lt) :
                    timeCorrection = RelTime(7,0,0)
                if (((nextLeg.ci_start_lt + timeCorrection) >= in_leg.first_good_leg_start_after_night_rest) or
                    ((nextLeg.start_lt + timeCorrection) <= in_leg.next_leg_max_connection_time)):
                    return True
            except:
                print str(nextLeg)
        return False

    def appendFindingTo(self, list):
        list.extend(self.getProblematic())
    
class Station(object):
    def __init__(self, station, qual_ref):
        self.__station = station
        self.__qual_ref = qual_ref
        self.__datedList = {}

    def addIncoming(self, incoming_leg, dated):
        key = None
        if dated:
            key =  incoming_leg.start_date
        else:
            key =  incoming_leg.start_weekday
        if not self.__datedList.has_key(key):
            datedStation = DatedStation(self, key)
            datedStation.addIncoming(incoming_leg)
            self.__datedList[key] = datedStation
        else:
            self.__datedList[key].addIncoming(incoming_leg)

    def addOutgoing(self, outgoing_leg, dated):
        key = None
        if dated:
            key =  outgoing_leg.start_date
        else:
            key =  outgoing_leg.start_weekday
        if not self.__datedList.has_key(key):
            datedStation = DatedStation(self, key)
            datedStation.addOutgoing(outgoing_leg)
            self.__datedList[key] = datedStation
        else:
            self.__datedList[key].addOutgoing(outgoing_leg)

    def getDatedStation(self, dated, leg, outgoing):
        key = None
        if outgoing:
            if dated:
                key = leg.start_date
            else:
                key = leg.start_weekday
        else:
            if dated:
                key = leg.end_date
            else:
                key = leg.end_weekday
        return self.__datedList.get(key)
    

    def getSortedStationDates(self):
        stationDates = self.__datedList.values()
        return sorted(stationDates, key =lambda stationDate: stationDate.date)

    def buildModel(self, dated, weekly, lh_list):
        prev = None
        first = None
        for stationDate in self.getSortedStationDates():
            if prev:
                stationDate.setPrev(prev)
            else:
                first = stationDate
            prev = stationDate
        if not dated:
            first.setPrev(prev)
            first.isFirst = True
        if self.name in BaseSet:
            for lh_container in lh_list:
                lh_container.addStation(self)

    
        
    def __sortIncomings(self):
        self.__incomings = sorted(self.__incomings, key=lambda leg: leg.end_lt)    

    def getProblematicLegs(self):
        _problemLegs = []
        if self.hasNightStops:
            for stationDate in self.getSortedStationDates():
                stationDate.appendFindingTo(_problemLegs)
        return sorted(_problemLegs, key=lambda touple: touple[0].start_lt)
    
    @property
    def hasNightStops(self):
        for date in self.__datedList.values():
            if date.hasNightStops:
                return True    
        return False

    @property
    def name(self):
        return self.__station

    @property
    def qual(self):
        return self.__qual_ref.name

    @property
    def planning_group(self):
        return self.__qual_ref.planning_group

    def getCSVInfo(self):
        return "%s;%s;%s" %(self.name, self.qual, self.planning_group)

    def getHeadCSVInfo(self):
        return "%s;%s;%s" %(self.planning_group, self.qual, self.name)
        

class PlanningGroup(object):
    def __init__(self, planning_group):
        self.__planning_group = planning_group
        self.qual_dict = {}

    def updateModelWith(self, leg_bag, incomming, dated):
        qual = None
        arrival_qual = leg_bag.studio_cpe.cpe_leg_qual()
        if not self.qual_dict.has_key(arrival_qual):
            qual = Qual(arrival_qual, self)
            self.qual_dict[arrival_qual] = qual
        else:
            qual = self.qual_dict[arrival_qual]
        qual.updateModelWith(leg_bag, incomming, dated)

    def updateModelWithFDP(self, duty_bag, dated):
        qual = None
        _qual = duty_bag.studio_cpe.cpe_duty_qual()
        if not self.qual_dict.has_key(_qual):
            qual = Qual(_qual, self)
            self.qual_dict[_qual] = qual
        else:
            qual = self.qual_dict[_qual]
        qual.updateModelWithFDP(duty_bag, dated)

    def buildModel(self, dated, weekly, lh_list):
        for qual in self.qual_dict.values():
            qual.buildModel(dated, weekly, lh_list)

    def getQuals(self):
        return self.qual_dict.values()

    @property
    def name(self):
        return self.__planning_group

class Qual(object):
    def __init__(self, qual, planning_group_ref):
        self.__qual = qual
        self.__planning_group_ref = planning_group_ref
        self.station_dict = {}
        self.flight_combo_dict = {}

    def updateModelWith(self, leg_bag, incomming, dated):
        station = None
        station_key = None
        if incomming:
            station_key = leg_bag.leg.arrival_airport_name()
        else:
            station_key = leg_bag.leg.departure_airport_name()
        if not self.station_dict.has_key(station_key):
            station = Station(station_key, self)
            self.station_dict[station_key] = station
        else:
            station = self.station_dict[station_key]
        for _leg in leg_bag.iterators.leg_set():
            if incomming:
                station.addIncoming(AcLeg(_leg), dated)
            else:
                station.addOutgoing(AcLeg(_leg), dated)

    def updateModelWithFDP(self, duty_bag, dated):
        _key = duty_bag.studio_cpe.cpe_duty_flight_names()
        fdp_flights = None
        if not self.flight_combo_dict.has_key(_key):
            fdp_flights = FDP_Flights(_key, self)
            self.flight_combo_dict[_key] = fdp_flights
        else:
            fdp_flights = self.flight_combo_dict[_key]
        for _duty in duty_bag.iterators.duty_set():
            fdp_flights.add(FDP_duty(_duty))

    def buildModel(self, dated, weekly, lh_list):
        for station in self.station_dict.values():
            station.buildModel(dated, weekly, lh_list)

    def getStations(self):
        return self.station_dict.values()

    def getFlights(self):
        return self.flight_combo_dict.values()

    @property
    def name(self):
        return self.__qual

    @property
    def planning_group(self):
        return self.__planning_group_ref.name

class FDP_Flights(object):
    def __init__(self, key, qual_ref):
        self.__key = key
        self.__qual_ref = qual_ref
        self.duty_list = []

    def add(self, duty):
        self.duty_list.append(duty)
        
    def getProblematicDuties(self):
        return [duty for duty in self.duty_list if (duty.co_a_mn or duty.close_to_fdp_maximum or duty.extension_is_notAllowed)]
        #return self.duty_list

    def getHeadCSVInfo(self):
        return "%s;%s;%s" %(self.planning_group, self.qual, self.name)

    def getCSVInfo(self):
        return "%s;%s;%s" %(self.planning_group, self.qual, self.name)

    @property
    def name(self):
        return self.__key

    
    @property
    def planning_group(self):
        return self.__qual_ref.planning_group

    @property
    def qual(self):
        return self.__qual_ref.name
    
        
        

class FDP_duty(object):
    def __init__(self, duty_bag):
        self.__start_lt = duty_bag.duty.start_lt()
        self.__checks_out_after_midnight = duty_bag.studio_cpe.duty_checks_out_after_midnight()
        self.__checks_out_before_two = duty_bag.studio_cpe.duty_check_out_after_midnight_before_two()
        self.__checks_out_after_two = duty_bag.studio_cpe.duty_check_out_after_midnight_after_two()
        self.__close_to_fdp_maximum = duty_bag.studio_cpe.close_to_fdp_maximum()
        self.__close_to_fdp_maximum_diff = duty_bag.studio_cpe.close_to_fdp_maximum_diff()
        self.__extension_is_notAllowed = duty_bag.studio_cpe.extension_is_not_allowed()

    @property
    def co_a_mn(self):
        return self.__checks_out_after_midnight

    @property
    def co_a_mn_b_two(self):
        return self.__checks_out_before_two

    @property
    def co_a_mn_a_two(self):
        return self.__checks_out_after_two

    @property
    def close_to_fdp_maximum(self):
        return self.__close_to_fdp_maximum

    @property
    def close_to_fdp_maximum_diff(self):
        return self.__close_to_fdp_maximum_diff

    @property
    def extension_is_notAllowed(self):
        return self.__extension_is_notAllowed

    def getCSVDutyInfo(self):
        return "%s;%s;%s;%s;%s;%s;" %(formatDateStr(self.__start_lt),str(self.__checks_out_before_two), str(self.__checks_out_after_two), str(self.__extension_is_notAllowed), str(self.__close_to_fdp_maximum), str(self.__close_to_fdp_maximum_diff) if self.__close_to_fdp_maximum else "")

    def getDutyInfo(self):
        return "%s;%s;%s;%s;%s;%s;" %(formatDateStr(self.__start_lt),str(self.__checks_out_before_two), str(self.__checks_out_after_two), str(self.__extension_is_notAllowed), str(self.__close_to_fdp_maximum), str(self.__close_to_fdp_maximum_diff))
        
        
class Report(SASReport):

    def updateModelWith(self, leg_bag, planning_group_dict, incomming, dated):
        planning_group = None
        planning_group_key = leg_bag.studio_cpe.cpe_leg_planning_group()
        if not planning_group_dict.has_key(planning_group_key):
            planning_group = PlanningGroup(planning_group_key)
            planning_group_dict[planning_group_key] = planning_group
        else:
            planning_group = planning_group_dict[planning_group_key]
        planning_group.updateModelWith(leg_bag, incomming, dated)

    def updateModelWithFDP(self, duty_bag, planning_group_dict, dated):
        planning_group = None
        _key = duty_bag.studio_cpe.cpe_duty_planning_group()
        if not planning_group_dict.has_key(_key):
            planning_group = PlanningGroup(_key)
            planning_group_dict[_key] = planning_group
        else:
            planning_group = planning_group_dict[_key]
        planning_group.updateModelWithFDP(duty_bag, dated)

    def updateLHModelWith(self, leg_bag, lh_list, dated):
        for _leg in leg_bag.iterators.leg_set():
            lh_leg = AcLeg(_leg)
            lh_list.append(LHLegContainer(lh_leg, dated))
        return lh_list

    def getData(self):
        tbh = bag_handler.WindowChains()
        global DATED, WEEKLY 
        dated, daily, = R.eval('global_is_dated_mode', 'base_constraints.%is_daily_problem%')
        weekly = not dated and not daily
        DATED = dated
        WEEKLY = weekly
        if tbh.warning:
            self.add(tbh.warning)
        if not tbh.bag:
            return
        planning_group_dict = self.getSHData(tbh, DATED)
        lh_list = self.getLHData(tbh, DATED)
        for planning_group in planning_group_dict.values():
            planning_group.buildModel(DATED, weekly, lh_list)
        for lh_coll in lh_list:
            lh_coll.buildModel()
        return planning_group_dict, lh_list
        
    def getSHData(self, tbh, dated):
        planning_group_dict = {}
        for leg_bag in tbh.bag.studio_cpe.arrival_airport_date_set(where = 'studio_cpe.%cpe_leg_to_consider% and not leg.%is_long_haul_aircraft%'):
            if ((not leg_bag.studio_cpe.cpe_leg_to_consider()) or  leg_bag.leg.is_long_haul_aircraft()):
                continue
            self.updateModelWith(leg_bag, planning_group_dict, True, dated)
        for leg_bag in tbh.bag.studio_cpe.departure_airport_date_set(where = 'studio_cpe.%cpe_leg_to_consider% and not leg.%is_long_haul_aircraft%'):
            if (not leg_bag.studio_cpe.cpe_leg_to_consider()) or  leg_bag.leg.is_long_haul_aircraft():
                continue
            self.updateModelWith(leg_bag, planning_group_dict, False, dated)
        for duty_bag in tbh.bag.studio_cpe.qual_planning_group_flight_duty_set(where = 'studio_cpe.%cpe_duty_to_consider%'):
            self.updateModelWithFDP(duty_bag, planning_group_dict, dated)
        return planning_group_dict

    def getLHData(self, tbh, dated):
        lh_list = []
        for leg_bag in tbh.bag.studio_cpe.departure_airport_date_set(where = 'studio_cpe.%cpe_leg_to_consider% and leg.%is_long_haul_aircraft%'):
            if leg_bag.studio_cpe.cpe_leg_to_consider() and leg_bag.leg.is_long_haul_aircraft():
                self.updateLHModelWith(leg_bag, lh_list, dated)
        return lh_list

    def sortLHList(self, lh_list):
        s = sorted(lh_list, key=attrgetter('start_lt'))     # sort on secondary key
        return sorted(s, key=attrgetter('flight_name'))
    
    def create(self, fileFormat = True):
        #Generate the report header and footer
        planning_group_dict, lh_list = self.getData()
        SASReport.create(self, "Brooken CPE report for the Aircrafts")
        csvRows = []
        csvHeader = []
        csvHeader.append("%s;%s;%s;%s" %("planning group", "qual", "station", "noProblems"))
        self.add(Row(Text("Night stop problems")))
        csvRows.append("Night stop problems")
        csvRows.append("%s;%s;%s;%s;%s;%s;%s;%s;;%s" %("station", "qual", "planning group", "Flight", "start", "end", "from", "to", "problem"))
        for planning_group in planning_group_dict.values():
            self.presentPlanningGroup(planning_group, csvRows, csvHeader)
            self.page0()
        csvHeader.append("%s;%s;%s;%s;%s;%s;%s;%s" %("planning group", "qual", "Flight", "noProblems", "co_a_12", "co_a_2am", "fdp", "extension problem"))
        csvRows.append("%s;%s;%s;%s;%s;%s;%s;%s;%s" %("planning group", "qual", "Flights", "date", "co_a_12", "co_a_2am", "extension problem", "fdp", "fdp_diff"))
        for planning_group in planning_group_dict.values():
            self.presentFDPPlanningGroup(planning_group, csvRows, csvHeader)
            self.page0()
        self.page()
        self.add(Row(Text("Connections to LH Flights")))
        csvRows.append("Connections to LH Flights")
        csvRows.append("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;" %("flight_name", "start_lt", "end", "departure_airport", "arrival_airport", "incomings", "outgoings", "flight_name", "start_lt", "end", "departure_airport", "arrival_airport","flight_name", "start_lt", "end", "departure_airport", "arrival_airport"))
        noLHProblems = 0
        for lh_leg in self.sortLHList([elem for elem in lh_list if elem.isProblematic]):
            self.presentLHLeg(lh_leg, csvRows)
            noLHProblems += 1
            self.page0()
        csvHeader.append("%s;;;%s" %("noLHProblems", str(noLHProblems)))
        self.printCSVToFile(csvRows, csvHeader)

    def printCSVToFile(self, csvRows, csvHeader):
        samba_path = os.getenv('SAMBA', "/samba-share")
        mypath = "%s/%s/" %(samba_path, 'reports/CPE')
        if not os.path.isdir(mypath):
            os.makedirs(mypath)
        timeStamp = str(datetime.now().date())
        reportName = "CPE_%s" %(timeStamp)
        myFile = mypath + reportName + '.csv'
        csvFile = open(myFile, "w")
        csvFile.write("\n")
        for row in csvHeader:
            csvFile.write(row + "\n")
        for row in csvRows:
            csvFile.write(row + "\n")
        csvFile.close()
        self.add("The output data is saved in %s" %myFile)
    
    def presentLHLeg(self, lh_leg, csvRows):
        self.add(Row(Text(lh_leg.problem_description)))
        textRow = lh_leg.csv_problem_description
        for close in lh_leg.closeIncomings:
            self.add(Row(Text(close.getConnectingSHLegInfo())))
            textRow += close.getConnectingSHCSVLegInfo()
        csvRows.append(textRow)

    def presentPlanningGroup(self, planning_group, csvRows, csvHeader):
        self.add(Row(Text("PlanningGroup: %s " %(planning_group.name))))
        for qual in planning_group.getQuals():
            self.presentQual(qual, csvRows, csvHeader)

    def presentFDPPlanningGroup(self, planning_group, csvRows, csvHeader):
        self.add(Row(Text("PlanningGroup: %s " %(planning_group.name))))
        for qual in planning_group.getQuals():
            self.presentFDPQual(qual, csvRows, csvHeader)

    def presentFDPQual(self, qual, csvRows, csvHeader):
        self.add(Row(Text("Qual: %s " %(qual.name))))
        noProblems = 0
        co_a_mn_b_two = 0
        co_a_mn_a_two = 0
        no_close_to_fdp_max = 0
        no_unallowed_extensions = 0
        flightProblems = []
        for fdpFlights in qual.getFlights():
            noFlightProblems, noNew_co_a_mn_b_two, noNew_co_a_mn_a_two, _no_close_to_fdp_max, _no_unallowed_extensions  = self.presentFDPFlights(fdpFlights, csvRows)
            if noFlightProblems > 0:
                flightProblems.append("%s;%s;%s;%s;%s;%s" %(fdpFlights.getHeadCSVInfo(), str(noFlightProblems), str(noNew_co_a_mn_b_two), str(noNew_co_a_mn_a_two), str(_no_close_to_fdp_max), str(_no_unallowed_extensions)))
                noProblems += noFlightProblems
                co_a_mn_b_two += noNew_co_a_mn_b_two
                co_a_mn_a_two += noNew_co_a_mn_a_two
                no_close_to_fdp_max += _no_close_to_fdp_max
                no_unallowed_extensions += _no_unallowed_extensions
            self.page0()
        csvHeader.append("%s;%s;;%s;%s;%s;%s;%s" %(qual.planning_group, qual.name, str(noProblems), str(co_a_mn_b_two), str(co_a_mn_a_two), str(no_close_to_fdp_max), str(no_unallowed_extensions)))
        csvHeader.extend(flightProblems)

    def presentFDPFlights(self, fdpFlights, csvRows):
        problems = fdpFlights.getProblematicDuties()
        noProblems = 0
        no_checkouts_after_midnight_before_two = 0
        no_checkouts_after_midnight_after_two = 0
        no_close_to_fdp_max = 0
        no_unallowed_extensions = 0
        if (len(problems) > 0):
            self.add(Row(Text(fdpFlights.name)))
            for duty in problems:
                _noProblems, _no_checkouts_after_midnight_before_two, _no_checkouts_after_midnight_after_two, _no_close_to_fdp_max, _no_unallowed_extensions   = self.presentProblematicDuty(duty, fdpFlights, csvRows)
                noProblems += _noProblems
                no_checkouts_after_midnight_before_two += _no_checkouts_after_midnight_before_two
                no_checkouts_after_midnight_after_two += _no_checkouts_after_midnight_after_two
                no_close_to_fdp_max += _no_close_to_fdp_max
                no_unallowed_extensions += _no_unallowed_extensions
        return noProblems, no_checkouts_after_midnight_before_two, no_checkouts_after_midnight_after_two, no_close_to_fdp_max, no_unallowed_extensions

    def presentProblematicDuty(self,  duty, fdpFlights, csvRows):
        self.add(Row(Text(duty.getDutyInfo())))
        csvRows.append("%s;%s" %(fdpFlights.getCSVInfo(),  duty.getCSVDutyInfo()))
        return 1, 1 if duty.co_a_mn_b_two else 0, 1 if duty.co_a_mn_a_two else 0, 1 if duty.close_to_fdp_maximum else 0, 1 if duty.extension_is_notAllowed else 0
        #print str(leg) + str
    
    def presentQual(self, qual, csvRows, csvHeader):
        self.add(Row(Text("Qual: %s " %(qual.name))))
        noProblems = 0
        stationProblems = []
        for station in qual.getStations():
            noStationProblems = self.presentStation(station, csvRows)
            if noStationProblems > 0:
                stationProblems.append("%s;%s" %(station.getHeadCSVInfo(), str(noStationProblems)))
                noProblems += noStationProblems
            self.page0()
        csvHeader.append("%s;%s;;%s" %(qual.planning_group, qual.name, str(noProblems)))
        csvHeader.extend(stationProblems)

    
    def presentStation(self, station, csvRows):
        problems = station.getProblematicLegs()
        noProblems = 0
        if (len(problems) > 0):
            self.add(Row(Text(station.name)))
            for leg, reason in problems:
                noProblems += self.presentProblematicLeg(leg, reason, station, csvRows)
        return noProblems

    def presentProblematicLeg(self,  leg, reason, station, csvRows):
        self.add(Row(Text(leg.getLegInfo() + str(reason))))
        csvRows.append("%s;%s;%s" %(station.getCSVInfo(),  leg.getCSVLegInfo(), str(reason)))
        return 1
        #print str(leg) + str(reason)
    
if __name__ == "__main__":
    from carmstd import report_generation as rg
    rg.reload_and_display_report("HTML")

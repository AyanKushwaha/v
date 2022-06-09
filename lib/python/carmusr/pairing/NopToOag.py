# !$CARMUSR/bin/python/carmusr/pairing/
#
# Script to add OAG legs to leg set.
# When trips with OAG legs are fetched to a database plan the OAG legs become NOP.
# This script adds all NOP OAG legs to the leg set.
#
# Created September 2007
# Anna Olsson, Jeppesen Systems AB
#

import Cui
#import sys
#import string
#import shutil
#import calendar
#import time
#import os
#import os.path
#import re
import carmensystems.rave.api as R

def nopToOag():
    """
    Adds NOP OAG legs to database legset
    """

    # Get the window the script is run from.
    currentArea = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)

    # Build RAVE expression 
    leg_expr = R.foreach(
        R.iter('iterators.leg_set', where = ('not_operating','leg.%is_oag%')),
        'leg_identifier',
        'leg.%flight_nr%',
        'leg.%flight_carrier%',
        'aircraft_owner',
        'leg.%ac_type%',
        'leg.%start_station%',
        'leg.%end_station%',
        'leg.%start_date_utc%',
        'leg.%start_od_utc%',
        'leg.%end_od_utc%',
        'crg_trip.%day_diff%',
        'leg.%start_weekday%'
        )
    
    # Evaluate RAVE expression
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, currentArea, "window")
    legs, = R.eval('default_context', leg_expr)
     
    #Keeps track of the legs that already have been added to the leg set
    processedLegs = {} 
    
    # Loop over all OAG NOP legs, SET PROPERTIES
    #Since fetched legs lacks some required properties,
    #set the propetries for the NOP leg before adding leg to leg set
    for (ix,uniqueLegId,flightNumber, flightCarrier, acOwner, acType, startStation,
         endStation, startDateUTC, startTimeUTC, endTimeUTC, arrivalOffset, weekday) in legs:

        #Pad flight number with zeroes 
        flNoLen = len(str(flightNumber))
       
        if flNoLen == 1:
            flightId = flightCarrier + "000" + str(flightNumber)
        elif flNoLen == 2: 
            flightId = flightCarrier + "00" + str(flightNumber)
        elif flNoLen == 3:
            flightId = flightCarrier + "0" + str(flightNumber)
        else:
            flightId = flightCarrier + str(flightNumber)
            
        # Change format of statTime and endTime to work in bypass        
        startTime = str(startTimeUTC)
        # Remove ':' and pad with '0'
        startTime = ''.join([a for a in startTime if a <> ':'])
        if len(startTime) == 3: startTime = '0' + startTime
        endTime =  str(endTimeUTC)
        # Remove ':' and pad with '0'
        endTime = ''.join([a for a in endTime if a <> ':'])
        if len(endTime) == 3: endTime = '0' + endTime

        #Set start and end of period, remove time
        startOfPeriod = endOfPeriod= str(startDateUTC)[:-6]
        
        Cui.CuiSetSelectionObject(Cui.gpc_info, currentArea, Cui.LegMode, str(uniqueLegId))

        #Since fetched legs lacks some required properties,
        #set the propetries for the NOP leg before adding leg to leg set
        bypass = {
            'FORM': 'DUMMY_FLIGHT',
            'FL_TIME_BASE': 'UDOP',
            'FLIGHT_ID': flightId, 
            'LEG_NUMBER': '1',
            'SERVICE_TYPE': 'J',
            'FREQUENCY': str(weekday), 
            'PERIOD_START':  startOfPeriod,
            'PERIOD_END':  endOfPeriod,
            'GDOR_OFFSET_DAYS':  '0',
            'DEPARTURE_TIME': startTime, 
            'ARRIVAL_TIME': endTime,
            'ARRIVAL_OFFSET_DAYS':  str(arrivalOffset),
            'DEPARTURE_AIRPORT': startStation,
            'ARRIVAL_AIRPORT':  endStation,
            'IATA_CODE':  acType,
            'CUSTOM_AC_TYPE': acType,
            'COC_EMP': flightCarrier, 
            'CAB_EMP': flightCarrier,
            'AC_OWNER': flightCarrier,
            'ONW_LEG_DEP': '0',
            'LEG_TYPE': 'No',
            'eobt': '01JAN1986 0:00',
            'eibt': '01JAN1986 0:00',
            'aobt': '01JAN1986 0:00',
            'aibt': '01JAN1986 0:00',
            'OK': '',
            }

        # Set leg properties given in bypass
        Cui.CuiLegSetProperties(bypass,Cui.gpc_info, currentArea, "object")


    # Loop over all OAG NOP legs, ADD TO LEG SET
    for (ix,uniqueLegId,flightNumber, flightCarrier, acOwner, acType, startStation,
         endStation, startDateUTC, startTimeUTC, endTimeUTC, arrivalOffset, weekday) in legs:
        
        #Pad flight number with zeroes 
        flNoLen = len(str(flightNumber))
       
        if flNoLen == 1:
            flightId = flightCarrier + "000" + str(flightNumber)
        elif flNoLen == 2: 
            flightId = flightCarrier + "00" + str(flightNumber)
        elif flNoLen == 3:
            flightId = flightCarrier + "0" + str(flightNumber)
        else:
            flightId = flightCarrier + str(flightNumber)
            
        # Change format of statTime and endTime to work in bypass        
        startTime = str(startTimeUTC)
        # Remove ':' and pad with '0'
        startTime = ''.join([a for a in startTime if a <> ':'])
        if len(startTime) == 3: startTime = '0' + startTime
        endTime =  str(endTimeUTC)
        # Remove ':' and pad with '0'
        endTime = ''.join([a for a in endTime if a <> ':'])
        if len(endTime) == 3: endTime = '0' + endTime

        #Set start and end of period, remove time
        startOfPeriod = endOfPeriod= str(startDateUTC)[:-6]
        
        Cui.CuiSetSelectionObject(Cui.gpc_info, currentArea, Cui.LegMode, str(uniqueLegId))

        bypass = {
            'FORM': 'DUMMY_FLIGHT',
            'FL_TIME_BASE': 'UDOP',
            'FLIGHT_ID': flightId, 
            'LEG_NUMBER': '1',
            'SERVICE_TYPE': 'J',
            'FREQUENCY': str(weekday), 
            'PERIOD_START':  startOfPeriod,
            'PERIOD_END':  endOfPeriod,
            'GDOR_OFFSET_DAYS':  '0',
            'DEPARTURE_TIME': startTime, 
            'ARRIVAL_TIME': endTime,
            'ARRIVAL_OFFSET_DAYS':  str(arrivalOffset),
            'DEPARTURE_AIRPORT': startStation,
            'ARRIVAL_AIRPORT':  endStation,
            'IATA_CODE':  acType,
            'CUSTOM_AC_TYPE': acType,
            'COC_EMP': flightCarrier, 
            'CAB_EMP': flightCarrier,
            'AC_OWNER': flightCarrier,
            'ONW_LEG_DEP': '0',
            'LEG_TYPE': 'No',
            'eobt': '01JAN1986 0:00',
            'eibt': '01JAN1986 0:00',
            'aobt': '01JAN1986 0:00',
            'aibt': '01JAN1986 0:00',
            'OK': '',
            }
        
        if (flightId,startDateUTC,startTimeUTC) not in processedLegs.keys():
            processedLegs[(flightId,startDateUTC,startTimeUTC)] = 1
            
            # Add leg to leg set     
            Cui.CuiCreateLegSet(bypass, Cui.gpc_info, currentArea, 8)


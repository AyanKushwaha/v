
# -*- coding: latin-1 -*-
# !$CARMUSR/bin/python/carmusr/pairing/
#
# Script to slice trips according to a 3/2/2 composition given in a csv file exported from Excel 
#
# Created September 2007
# Anna Olsson, Jeppesen Systems AB
#

import Cui
import Cfh
import tempfile
import sys
import string
import shutil
import calendar
import time
import os
import os.path
import re
import carmensystems.rave.api as R
import carmusr.trip_area_handler

############################## --------------------- ##############################
##############################  global declarations  ##############################
############################## --------------------- ##############################

#csvFilePath = "/users/annao/work/Customization/sk_cms_user/322_minitest2.csv"
csvFilePath = "/users/annao/work/Customization/sk_cms_user/322_Carmen.csv"
#csvFilePath = "/users/annao/work/Customization/sk_cms_user/322_Carmen2.csv"

gStrSeparatorCsv    = ';'

gReTrip = re.compile(r'^(?P<airport>\w{3}) *(?P<tripNr>\d{3,4})$') ### Vad gör det här? ###

gMapCountry = {'S':0,'N':1,'D':2}


############################## --------------------- ##############################
##############################      functions        ##############################
############################## --------------------- ##############################

# Read a file into a buffer and return the buffer
def readFile(filename):
    f = open(filename)
    buffer = map(lambda line: line.strip(), f.readlines())
    f.close()
    return buffer

# Get weeknumber for a specific date
def date_to_weeknr(year, month, day):
    # first, calculate julian day number J
    a = (14 - month)/12
    y = year + 4800 - a
    m = month + (12 * a) - 3

    J = day + (153 * m + 2)/5 + 365 * y + y/4 - y/100 + y/400 - 32045

    # calculate week number from julian day number
    d4 = (J + 31741 - (J % 7)) % 146097 % 36524 % 1461
    L = d4/1460
    d1 = ((d4 - L) % 365) + L
    weeknr = d1/7 + 1

    # get year week is in
    #if weeknr >= 52 and month == 1:
    #   year = year - 1
    return weeknr


# Get crew need for each country for a specific flight, base, week and weekday
def needPerCategoryAndBase(matrix, line, row):
    # Indata is a column representing the crew need for a singel day of a specific week
    # for a flight and base
   
    firstLine = line
    
    # [[AP S, AP N, AP D][AS S, AS N, AS D][AH S, AH N, AH D][Any S, Any N, Any D]]
    need = [[0,0,0],[0,0,0],[0,0,0],[-1,-1,-1]]

    # For each category in the need matrix
    for category in range(3):
        
        # Loop while token is a valid country code.
        # While loop terminates when an empty line is encountered and only one crew category is processed
	while matrix[line][row] in gMapCountry.keys():
            
            # If no crew need for country found yet
            if need[3][gMapCountry[matrix[line][row]]] == -1:
                # Set crew need for country to 1 
		need[3][gMapCountry[matrix[line][row]]] = 1
                need[category][gMapCountry[matrix[line][row]]] += 1
            else:
               # Add one more crew to the category and country position in the need matrix
               need[category][gMapCountry[matrix[line][row]]] += 1
            # Go to next line in the column
	    line += 1

         
        # Skip empty lines in data column after AP and AS data    
	while category < 2 and not line > firstLine + 11 and not (matrix[line][row] in gMapCountry.keys()):
	    line += 1
    return need


# read the csv file and return a map
# 7x7 week specifications per trip are assumed
def readCsv(filename):

    # Keep track of flights ???
    mapFlights = {}
    
    #???
    reWeekNr = re.compile(r'(?P<weekNr>\d{1,2})$')
    
    # Read csv file and split into lines, constructing a data matrix
    csvMatrix = map((lambda line: line.split(gStrSeparatorCsv)), readFile(filename))

    numLines = len(csvMatrix)
    numColumns = len(csvMatrix[0])

    #numWeeks = (numColumns - 83)/7
    #numWeeks = 1
    numWeeks = 7
    

    # For each line in the matrix
    for ixLine in range(numLines):
        
        # Match trip regexp with csv data
        tripMatch = gReTrip.match(csvMatrix[ixLine][0])
    
        # if they match
        if tripMatch:
            # create flight key
            tupKey = (tripMatch.group('tripNr'), getModifiedAircraftType(csvMatrix[ixLine][1]))
            
           
            
            #if flight key in dictionary
            if tupKey in mapFlights.keys():
                # ???
                mapWeekData = mapFlights[tupKey]
               
            else:
                # Create an entry for the flight in the mapFlights dictionary
                mapFlights[tupKey] = mapWeekData = {}

                # For each week in the csv file. (csv file contains seven weeks.)
		for ixWeek in range(numWeeks): #range(7)
                    
                    # Instatiate list to keep need data for each day in week
		    listWeek = []
                    
                    #For each day in week
		    for ixWeekDay in range(7):
                        
                        # Add day need to week list
			listWeek.append(needPerCategoryAndBase(csvMatrix, ixLine + 2, ixWeek * 7 + ixWeekDay + 1))
                        
                    # Cycle through matrix to find next week number   
                    for cycleWeek in range(1+ixWeek*7, 7+ixWeek*7):
                        
                        # Search for next week number 
                        weekMatch = reWeekNr.search(csvMatrix[ixLine][cycleWeek])
                        
                        # if week number found
                        if weekMatch:
                            # Cast week number to integer
                            tmpIntWeek = int(weekMatch.group('weekNr'))
                            
                            # If week number already in dictionary and  
                            if tmpIntWeek in mapWeekData.keys():
                                if mapWeekData[tmpIntWeek] != listWeek:
                                    print "Conflicting definition: Flight" + str(tupKey[0]) +\
                                          "with A/C-type" + str(tupKey[1]) + \
                                          "has week" +  str(tmpIntWeek) + "multiply defined." 
                            mapWeekData[tmpIntWeek] = listWeek
    return mapFlights


def getModifiedAircraftType(strAircraftType):
    strReturnAircraftType = strAircraftType[:2]
    if strReturnAircraftType == '33':
	return '34'
    else:
	return strReturnAircraftType


# Test functions


# Read csv file and split into lines, constructing a data matrix
def testReadCsv2():
    csvMatrix = map((lambda line: line.split(gStrSeparatorCsv)), readFile(csvFilePath))
    print csvMatrix

# Read data from csv file
def testReadCsv():
    map322 = readCsv(csvFilePath)
    print map322
    
############################## ---------------##############################
##############################      Forms     ##############################
############################## ---------------##############################

class csvFileSelection(Cfh.Box):
    def __init__(self, *args):
        """
        Creates a dialog to select a csv file

        """
        
        Cfh.Box.__init__(self, *args)

        # Field for csv file selection
        self.select_csv = Cfh.String(self,"CSV_FILES", 50)
        self.select_csv.setMenuOnly(True)
        self.select_csv.setMandatory(True)
 
        # OK and CANCEL buttons
        self.ok = Cfh.Done(self,"B_OK")
        self.quit = Cfh.Cancel(self,"B_CANCEL")

      
# Create form
        form_layout = """
FORM;CSVFILE_FORM;`Select csv file`
LABEL;`Csv Files:`
FIELD;CSV_FILES;
BUTTON;B_OK;`Ok`;`_Ok'
BUTTON;B_CANCEL;`Cancel`;`_Cancel`
"""
        
        csv_form_file = tempfile.mktemp()
        f = open(csv_form_file,"w")
        f.write(form_layout)
        f.close()
        self.load(csv_form_file)
        os.unlink(csv_form_file)

        
    def getValues(self):
        """
        Function returning the values set in the form. 
        """
        return(self.select_csv.valof())


    def setValues(self):
        """
        Function setting the values in the form.
        
        """
        
        # Find and list all the files in the CARMDATA/ETABLES/TRIP_COPY_CSV_FILES directory
        path = os.path.expandvars(os.path.join("$CARMDATA", "ETABLES", "TRIP_COPY_CSV_FILES/"))
        #path = "/nfs/vm/skcms/carmdata/ETABLES/TRIP_COPY_CSV_FILES/"
        #os.path.expandvars("$CARMDATA/ETABLES/TRIP_COPY_CSV_FILE/")
        print path
        files = ""
        try:
            dirList = os.listdir(path)
            for fname in dirList:
                if os.path.isfile(os.path.join(path, fname)):
                    files += ";" + fname
            self.select_csv.setMenuString(files)
            
        except OSError, err:
            import errno
            # check for "file not found errors", re-raise other cases
            if err.errno != errno.ENOENT: raise
            # handle the file not found error
            print "File: " + err.filename + " not found"



def selectCsvFile():
    """
    Creates a select form
    """
    try:
        csv_file_select_form == csv_file_select_form
    except:
        csv_file_select_form = csvFileSelection("Csv_File_Selection")

    # We need to do this every time since a new reference roster 
    # might have been created after the dialog was created
    csv_file_select_form.setValues()
    
    print "CsvFileSelection form created"

    # Show dialog
    csv_file_select_form.show(1)

    if csv_file_select_form.loop() == Cfh.CfhOk:
        # Ok button pressed, get the value
        csv_file = csv_file_select_form.getValues()
        print "Chosen csv file: " + csv_file

        # Check that the file exists
        #fname =os.path.join("/nfs/vm/skcms/carmdata/ETABLES/TRIP_COPY_CSV_FILES",csv_file)
        fname = os.path.expandvars(os.path.join("$CARMDATA", "ETABLES", "TRIP_COPY_CSV_FILES", csv_file))
        print "File path: " + fname
        print os.path.isfile(fname)
        #if os.path.isfile(fname):
        return fname
    else:
        return None
    
############################## ---------------##############################
############################## Main function  ##############################
############################## ---------------##############################

def copyTrips322():
    """Build new trip slices according to csv-file"""

    # Get the window the script is run from. Should contain the trips to slice
    currentArea = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    print currentArea


    # Display form for csv file selection
    csvFile = selectCsvFile()
    # print " csv file: " + csvFile 
    
    if csvFile:
        # Build RAVE expression for fetching information about the trips to build slices from.
        trip_expr = R.foreach(
            R.iter('iterators.trip_set', where = 'trip.%is_long_haul%'),
            'crg_trip.%long_haul_flight_id%',
            'crr_identifier',
            'crg_trip.%long_haul_ac_type%',
            'crg_trip.%long_haul_start_week_day%',
            'crg_trip.%long_haul_trip_base%',
            'crg_trip.%long_haul_year%',
            'crg_trip.%long_haul_month%',
            'crg_trip.%long_haul_day%')
        
       
       
        # Merge trips so there is only one slice of each trip
        Cui.CuiMergeIdenticalCrrs(Cui.gpc_info, currentArea, "window",Cui.CUI_MERGE_IDENTICAL_SILENT)
        # Evaluate RAVE expression
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, currentArea, "window")
        trips, = R.eval('default_context', trip_expr)
        
     
        # Read data from csv file.
        map322 = readCsv(csvFile)
        print map322
     
         ### Remove duplicate trips from plan ###
        # This should be unnecessary when trips are merged
 
##         mapKeysDone = {} # Used to check whether a trip is unique
    
##         for (ix,flightId,uniqueTripId,aircraftType,weekday,base,year,month,day) in trips:
##             print "Entered remove loop"
##             print ix,flightId,uniqueTripId,aircraftType,weekday,base,year,month,day
        
##             # Construct key to the data from the csv file
##             modifiedAircraftType = getModifiedAircraftType(aircraftType)
##             flightInfo = (flightId,modifiedAircraftType)  
        
##             #Get weeknumber for trip date
##             week = date_to_weeknr(int(year), int(month), int(day))
        
##             #Modify weekday number to use for indexing
##             weekday -= 1
        
##             # Check if trip is unique
##             flightUniqueKey = (flightId, modifiedAircraftType, week, weekday, base)
##             # If trip isn't a duplicate, add it to 
##             print "Duplicate ?: " + str(flightUniqueKey in mapKeysDone.keys())
##             if not flightUniqueKey in mapKeysDone.keys():
##                  mapKeysDone[flightUniqueKey] = 1
##                  trips2 =
##             # else add it to dictionary of existing trips
     

        ### Create new trip slices from the unique trips in the window ###
            
       ##  # Fetch trips from window after removing duplicates
##         trips2, = R.eval('default_context', trip_expr)

        # Got through all trips in window
        for (ix,flightId,uniqueTripId,aircraftType,weekday,base,year,month,day) in trips:
            print "Entered copy loop"
            print ix,flightId,uniqueTripId,aircraftType,weekday,base,year,month,day
            # Construct key to the data from the csv file
            modifiedAircraftType = getModifiedAircraftType(aircraftType)
            flightInfo = (str(flightId),modifiedAircraftType)  
        
            #Get weeknumber for trip date
            week = date_to_weeknr(int(year), int(month), int(day))
        
            #Modify weekday number to use for indexing
            weekday -= 1 

            # Make base a string
            if base == 0:
                base = "STO"
            elif base == 1:
                base = "OSL"
            else:
                base = "CPH"

            print base

            # if flight exists in cvs file
            if flightInfo in map322.keys() and week in map322[flightInfo].keys() :
            
                #Fetch information about required slices for trip. Gets output from needPerCategoryAndBase function. 
                complementMatrix = map322[flightInfo][week][weekday] 
            
                # Go through the need matrix and create a new trip slice with the appropriate base and complement
                for country in range(3):
                
                    #If slice required for country
                    if complementMatrix[3][country] != -1:
                    
                        # Get complement for slice
                        complement = '0/0/0/0//' + \
                                     str(complementMatrix[0][country]) + '/' + \
                                     str(complementMatrix[1][country]) + '/' + \
                                     str(complementMatrix[2][country]) + '/0//0/0'
                                       
                        # Get base name for slice
                        if country == 0:
                            base2 = "STO"
                            region = "SKS"
                        elif country == 1:
                            base2 = "OSL"
                            region = "SKN"
                        else:
                            base2 = "CPH"
                            region = "SKD"
                            
                        # Select original trip to copy    
                        Cui.CuiSetSelectionObject(Cui.gpc_info, currentArea, Cui.CrrMode, str(uniqueTripId))

                        bypass = {'FORM': 'CRR_FORM',
                                   'CRR_PBASE': base2,
                                   'CRR_CREW_COMP_TYPE': 'Each Trip'
                                   }
                        
                        Cui.CuiCrrProperties(bypass,Cui.gpc_info,currentArea,"Object")
                        
                        # Make a copy of the original trip
                        bypass2 = {'FORM': 'COPY_CHAIN',
                                   'FL_CC': complement,
                                   'FL_NR_COPIES': 1,
                                   'FL_REDUCE_CC': 'No',
                                   'FL_SPLIT_IMPLAUSIBLE_CC': 'No'
                                   }
                    
                        Cui.CuiDuplicateChains(bypass2, Cui.gpc_info, currentArea, "object", 2)

                        # Set reset properties for original trip
                      #  Cui.CuiSetSelectionObject(Cui.gpc_info, currentArea, Cui.CrrMode, str(uniqueTripId))
                        
                        bypass3 = {'FORM': 'CRR_FORM',
                                   'CRR_PBASE': base,
                                   'CRR_CREW_COMP_TYPE': 'Each Trip'
                                   }
                    
                        Cui.CuiCrrProperties(bypass3,Cui.gpc_info,currentArea,"Object")
                        
 #trip_area_handler.set_area(TRIP,region)

 
                    ## When using script in the database, original trips should be kept.
               ##  # When copies have been made for each country in the need matrix; remove original trip
##                 Cui.CuiSetSelectionObject(Cui.gpc_info, currentArea, Cui.CrrMode, str(uniqueTripId))        
##                 Cui.CuiRemoveCrr(Cui.gpc_info, currentArea, 3)
                  
                


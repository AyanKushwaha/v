#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#

#
# Basic SoftLock classes
#
# Created 2004-05-06 /Henrik Enstr�m
#

import os, re, types, sys, copy, time
#from Etab import *

#----------------------------- ===================== ------------------------------
#----------------------------- CarmTypes repl. start ------------------------------
#----------------------------- ===================== ------------------------------

# ------------------ ABSTIME CLASS ---------------------

class AbstimeFunctions:
    """
    A class that represents abstimes, as it is treated in Studio/RAVE.
    
    The internal int representation converts local timezone representation.
    """
    def __init__(self):
        self.validFormats=["%d%b%Y","%d%b%Y %H:%M","%d%m%Y","%d%m%Y %H:%M","%d %b %Y","%d %b %Y %H : %M","%d %m %Y","%d %m %Y %H : %M"]
        self.carmenOffset=int(time.mktime(time.strptime("1986 01 01","%Y %m %d"))) #Start of Abstime range
        self.outputFormat="%d%b%Y %H:%M"
        self.etabChar="A"

    def fromString(self,value,format=None):
        """Transforms an abstime (as a string) into an int (minutes from 1Jan1986)."""
        """fromString("1Jan1986 00:25") = 25"""
        if format:
            formats=[format]
        else:
            formats=self.validFormats
        for f in formats:
            try:
                intTime=int(
                    time.mktime(time.strptime(value,f))
                    - self.carmenOffset
                    ) /60
                if intTime < 0:
                    raise ValueError("Abstimes must be after 1jan1986")
                return intTime 
            except ValueError, TypeError:
                pass
        raise ValueError
        
    def toString(self,value,outputFormat=None):
        if not outputFormat: outputFormat=self.outputFormat
        if value<0: raise ValueError("Abstimes must be after 1jan1986")
        return time.strftime(outputFormat,
                             time.localtime(value*60+
                                         self.carmenOffset))
    def test(self,times,cases):
        """To perform a verifcation & cpu time test"""
        while times:
            times = times-1
            for c in cases:
                try:
                    c1 = self.fromString(c)
                    if not times: print c + "\t ==> " + self.toString(c1)
                except ValueError:
                   if not times: print c + "\t ==> ValueError"

abstimeFunctions = AbstimeFunctions()

class Abstime:
    """To create abstime instances"""
    def __init__(self,value,format=None):
        """Creates an instance of the class. The argument should be a
        string or an int"""
        global abstimeFunctions
        self.super=abstimeFunctions
        try:
            self.value=self.super.fromString(value,format)
        except:
            # print 'Tried format which did not match: %s' %(sys.exc_info()[0])
            self.value=int(value)
    def __str__(self):
        return self.super.toString(self.value)
    def format(self,formatString=None):
        return self.super.toString(self.value,formatString)
    def __int__(self):
        return self.value
    def __add__(self,other):
        try:
            return Abstime(self.value+other.value)
        except:
            return Abstime(self.value+other)        
    def __iadd__(self,other):
        try:
            self.value+=other.value
        except:
            self.value+=other
        return self
    def __sub__(self,other):
        try:
            return Abstime(self.value-other.value)
        except:
            return Abstime(self.value-other)        
    def __lt__(self,other):
        return int(self)<int(other)
    def __le__(self,other):
        return (int(self)-1)<int(other)
    def __gt__(self,other):
        return other<self
    def __ge__(self,other):
        return other<=self
    def __eq__(self,other):
        return int(other)==int(self)

# ----------------- PERIOD & FREQUENCY ----------------------

#----------------------------- ===================== ------------------------------
#-----------------------------  CarmTypes repl. end  ------------------------------
#----------------------------- ===================== ------------------------------


#----------------------------- ===================== ------------------------------
#-----------------------------  Etab replacem. start ------------------------------
#----------------------------- ===================== ------------------------------

import sys, os, re, string, time

############################## --------------------- ##############################
##############################  global declarations  ##############################
############################## --------------------- ##############################

gStrSeparator = ','
gStrUniqueTag = '==>>'
gReComment = re.compile(r'/\*.*?\*/', re.DOTALL)
gReNr = re.compile(r'^\s*(?P<nr>\d+)\s*$')
gReEtabColSpec = re.compile(r'^(?P<type>[SIARBCE])(?P<name>\w+)(\s(?P<colspec>.*)|\s*),\s*$')
gReEtabClosingBrackets = re.compile(r'^[^\[]*(\[[^\]]*\].*$|)$')
gReEtabRow = re.compile(r'^\s*[^\,].*,\s*$')
gReEtabString = re.compile(r'^"(?P<string>.*)"$')
gReEtabSplit = re.compile(r'\s*(".*?")\s*,\s*|\s*,\s*')
gReEtabFirstComment = re.compile(r'^\s*/\*(?P<firstComment>.*?)(\*/|%s)' % (gStrUniqueTag), re.DOTALL)

############################## --------------------- ##############################
##############################      functions        ##############################
############################## --------------------- ##############################

# read a file into a buffer and return the buffer
def readFile(filename):
    if not os.path.isfile(filename):
        return None
    f = open(filename)
    buffer = map(lambda line: line.replace(os.linesep, ''), f.readlines())
    f.close()
    return buffer

# write a file from a list of lines
def writeFile(filename, lines):
    outFile = open(filename, 'w')
    for line in lines:
        outFile.write(line + '\n')
    outFile.close

# print warning
def printWarning(strWarning):
    print '  --> Warning: %s' %(strWarning)
    sys.stdout.flush()

# write a general etab
def writeEtab(filename, etab):
    # This if should be removed eventually...
    if len(etab) > 2:
        (listEtabCols, listEtabRows, strFirstComment) = etab[0:3]
    else:
        (listEtabCols, listEtabRows) = etab[0:2]
        strFirstComment = ''

    strHeader = '/*\n%s %s was created %s\n' %(gStrUniqueTag, os.path.basename(filename), time.asctime(time.localtime(time.time())))
    strHeader += '     by the script "%s" and contains %i rows.\n' %(os.path.basename(sys.argv[0]), len(listEtabRows))
    strHeader += '     henrik.enstrom@carmensystems.com\n*/'
    listFirstEtabLines = [strFirstComment, strHeader, str(len(listEtabCols))]
    for tupCol in listEtabCols:
        # This if should be removed eventually...
        if tupCol[2]:
            listFirstEtabLines.append(tupCol[0] + tupCol[1] + ' ' + tupCol[2] + ',')
        else:
            listFirstEtabLines.append(tupCol[0] + tupCol[1] + ',')

    listLongest = [0] * len(listEtabCols)
    outputRows = listEtabRows[:]
    for ixRow in range(len(outputRows)):
        for ixCol in range(len(listEtabCols)):
            if listEtabCols[ixCol][0] in ['S', 'C', 'E']:
                outputRows[ixRow][ixCol] = '"' + outputRows[ixRow][ixCol] + '"'
            elif listEtabCols[ixCol][0] == 'I':
                matchNr = gReNr.match(outputRows[ixRow][ixCol])
                if matchNr:
                    outputRows[ixRow][ixCol] = matchNr.group('nr')
                else:
                    outputRows[ixRow][ixCol] = '0'
            elif (listEtabCols[ixCol][0] == 'A' and len(outputRows[ixRow][ixCol]) == 8) or (listEtabCols[ixCol][0] == 'R' and len(outputRows[ixRow][ixCol]) == 4):
                outputRows[ixRow][ixCol] = '0' + outputRows[ixRow][ixCol]
            if len(outputRows[ixRow][ixCol]) > listLongest[ixCol]:
                listLongest[ixCol] = len(outputRows[ixRow][ixCol])

    for ixRow in range(len(outputRows)):
        for ixCol in range(len(outputRows[ixRow])):
            outputRows[ixRow][ixCol] = string.rjust(str(outputRows[ixRow][ixCol]), listLongest[ixCol] + 1) + ','
        outputRows[ixRow] = ' '.join(outputRows[ixRow])

    writeFile(filename, listFirstEtabLines + outputRows)

# read a general etab
def readEtab(filename):
    listEtabCols = []
    listEtabRows = []
    allRowsWithComments = readFile(filename)
    if not allRowsWithComments:
        printWarning('The file "%s" does not exist' %(filename))
        return None
    (allRows, strFirstComment) = unComment(allRowsWithComments)
    if len(allRows) == 0:
        printWarning('The file "%s" is empty' %(filename))
        return None
    ixRow = 0
    while not gReNr.match(allRows[ixRow]):
        ixRow += 1
        if ixRow >= len(allRows):
            printWarning('The file "%s" has syntax errors (number of columns)' %(filename))
            return None
    intEtabCols = string.atoi(gReNr.match(allRows[ixRow]).group('nr'))
    while intEtabCols > 0:
        ixRow += 1
        if ixRow >= len(allRows):
            printWarning('The file "%s" has syntax errors (column definitions)' %(filename))
            return None
        matchClosingBrackets = gReEtabClosingBrackets.match(allRows[ixRow])
        if matchClosingBrackets:
            matchCol = gReEtabColSpec.match(allRows[ixRow])
            if matchCol:
                listEtabCols.append((matchCol.group('type'), matchCol.group('name'), matchCol.group('colspec')))
                intEtabCols -= 1
        else:
            allRows[ixRow] += allRows[ixRow + 1]
            del allRows[ixRow + 1]
            ixRow -= 1
    ixRow += 1
    while ixRow < len(allRows):
        matchRow = gReEtabRow.match(allRows[ixRow])
        if matchRow:
            listRow = []
            for strValue in gReEtabSplit.split(allRows[ixRow]):
                if strValue and len(strValue) > 0:
                    listRow.append(strValue)
            listValues = map(string.strip, listRow)
            for ixCol in range(len(listValues)):
                if listEtabCols[ixCol][0] in ['S', 'C', 'E']:
                    matchString = gReEtabString.match(listValues[ixCol])
                    if matchString:
                        listValues[ixCol] = matchString.group('string')
                    else:
                        printWarning('The string "%s" does not match' %(listValues[ixCol]))
            listEtabRows.append(listValues)
        ixRow += 1

    return (listEtabCols, listEtabRows, strFirstComment, os.path.basename(filename))

def getEtabColKeys(etabCols):
    return map((lambda t: (t[0], t[1])), etabCols)

def unComment(listLines):
    # The step is due to a problem in the maximum recursion limit
    intStep = 8000
    ixChar = 0
    oneLine = os.linesep.join(listLines)
    searchFirstComment = gReEtabFirstComment.search(oneLine)
    if searchFirstComment:
        strFirstComment = '/*%s*/' %(searchFirstComment.group('firstComment'))
    else:
        strFirstComment = ''
    while ixChar < len(oneLine):
        oneLine = oneLine[:ixChar] + gReComment.sub('', oneLine[ixChar:ixChar+intStep]) + oneLine[ixChar+intStep:]
        ixChar += intStep / 2
    listOut = oneLine.split('\n')
    return (listOut, strFirstComment)

def etabToListMap(etab):
    listMapEtab = []
    for ixRow in range(len(etab[1])):
        mapRow = {}
        for ixCol in range(len(etab[0])):
            mapRow[etab[0][ixCol][1]] = etab[1][ixRow][ixCol]
        listMapEtab.append(mapRow)
    return listMapEtab

def buildEtabRows(listEtabCols, listMap):
    listRows = []
    for mapRow in listMap:
        listCols = []
        for aCol in listEtabCols:
            if aCol[1] in mapRow.keys():
                listCols.append(mapRow[aCol[1]])
            elif aCol[1] in gEtabMappings.keys() and gEtabMappings[aCol[1]] in mapRow.keys():
                listCols.append(mapRow[gEtabMappings[aCol[1]]])
            elif aCol[1] in gMapDefault.keys():
                listCols.append(gMapDefault[aCol[1]])
            else:
                listCols.append('0')
        listRows.append(listCols)
    return listRows

def removeDuplicates(list):
    ix = 0
    while ix < len(list):
        if list[ix] in list[:ix]:
            del list[ix]
        else:
            ix += 1

#----------------------------- ===================== ------------------------------
#-----------------------------  Etab replacem. end   ------------------------------
#----------------------------- ===================== ------------------------------

############################## --------------------- ##############################
##############################  global declarations  ##############################
############################## --------------------- ##############################

gListSLEtabCols = [('E', 'Type', '"Type" [ "REQ_BASE" ; "NOT_BASE" ; "REQ_TRIPSTART" ; "REQ_TRIPEND" ; "NOT_TRIPSTART" ; "NOT_TRIPEND" ; "REQ_DUTYSTART" ; "REQ_DUTYEND" ;\t"NOT_DUTYSTART" ; "NOT_DUTYEND" ; "REQ_CXN_AFT" ; "NOT_CXN_AFT" ; "REQ_CXN_BEF" ; "NOT_CXN_BEF" ; "REQ_REST_AFT" ; "REQ_REST_BEF" ;\t"CXN_BUFFER" ] 30 / 20'), ('S', 'Carrier1', '"1st carrier" [ "AA" % "IB" % "ZZ" ] 2 / 13'), ('I', 'FlightNr1', '"1st flight nr" [ 0 % 0 % 9999999 ] 7 / 10'), ('S', 'DepArr1', '"1st DEP-ARR" 7 / 13'), ('S', 'ActiveOrDH1', '"1st Active/DH" [ "A" % "*" % "Z" ] 1 / 14'), ('S', 'TrafficDay', '"1st Traf. day (D, 1-7)" [ "A" % "D" % "Z" ] 7 / 16'), ('A', 'DateFrom', '"1st From (flight dep)" [ 01JAN2000 % 01JAN2000 % 01JAN2030 ] 15 / 17'), ('A', 'DateTo', '"1st To (flight dep)" [ 01JAN2000 % 01JAN2030 % 01JAN2030 ] 15 / 15'), ('S', 'Carrier2', '"2nd carrier" [ "AA" % "IB" % "ZZ" ] 2 / 13'), ('I', 'FlightNr2', '"2nd flight nr" [ 0 % 0 % 9999999 ] 7 / 10'), ('S', 'DepArr2', '"2nd DEP-ARR" 7 / 13'), ('S', 'ActiveOrDH2', '"2nd Active/DH" [ "A" % "*" % "Z" ] 1 / 14'), ('R', 'LimitMin', '"Min time limit" [ -999:00 % 0:00 % 999:00 ] 7 / 15'), ('R', 'LimitMax', '"Max time limit" [ -999:00 % 0:00 % 999:00 ] 7 / 15'), ('S', 'Base', '"Base" 7 / 7'), ('S', 'ACType', '"AC type" 7 / 7'), ('B', 'ACChange', '"If AC-chg" [ false % false % true ] 5 / 10'), ('I', 'Penalty', '"Penalty (1-9=Std, 0=Rule)" [ 0 % 0 % 9999999 ] 7 / 22'), ('B', 'Active', '"Active" [ false % true % true ] 5 / 10'), ('C', 'Comment', '"Comment" 50 / 15')]
gStrStdSLEtabComment = """/*
The SoftLocks module is meant to be a more flexible alternative to hard locks.
The following goals can be fulfilled by using this etable:
---
 Type             Description
 REQ_BASE:        Impose a flight being flown by the crew from a certain base.
 NOT_BASE:        Prohibit a flight being flown by the crew from a certain base.
 REQ_TRIPSTART:   Impose a flight starting a trip.
 REQ_TRIPEND:     Impose a flight ending a trip.
 NOT_TRIPSTART:   Prohibit a flight starting a trip.
 NOT_TRIPEND:     Prohibit a flight ending a trip.
 REQ_DUTYSTART:   Impose a flight starting a duty.
 REQ_DUTYEND:     Impose a flight ending a duty.
 NOT_DUTYSTART:   Prohibit a flight starting a duty.
 NOT_DUTYEND:     Prohibit a flight ending a duty.
 REQ_CXN_AFT:     Impose (lock) a connection after a flight or between two
                  flights, with or without a layover (of undefined or of
                  XX:XX-YY:YY length) in between.
 NOT_CXN_AFT:     Prohibit a connection after a flight or between two
                  flights, with or without a layover (of undefined or of
                  XX:XX-YY:YY length) in between.
 REQ_CXN_BEF:     Impose (lock) a connection before a flight or between two
                  flights, with or without a layover (of undefined or of
                  XX:XX-YY:YY length) in between.
 NOT_CXN_BEF:     Prohibit a connection before a flight or between two
                  flights, with or without a layover (of undefined or of
                  XX:XX-YY:YY length) in between.
 REQ_REST_AFT:    Impose at least XX:XX-YY:YY rest period after a flight.
 REQ_REST_BEF:    Impose at least XX:XX-YY:YY rest period before a flight.
 CXN_BUFFER:      XX:XX additional connection time before a flight and YY:YY
                  after. It is possible to specify that the buffer only should
                  be used when connecting to a certain flight. Use the Rave
                  variables %sl_cxn_buffer_after% and %sl_cxn_buffer_before% to
                  access this Reltime buffer.
---
Column descriptions:
E Type
  Type string in a predefined set, see above.
S Carrier1
  Carrier of leg 1. Mandatory for all SoftLock types.
I FlightNr1
  The flight number of leg 1, used in all soft lock types. May be empty if
  DepArr1 is used instead.
S DepArr1
  The departure and arrival airport of leg 1 on the format "DEP-ARR".
  May be used instead of FlightNr1. Only needed for multi-leg flights, may be
  empty otherwise.
S ActiveOrDH1
  String which limits the SoftLock to Active or DH flights for leg 1. Valid
  strings are "A" (active), "D" (deadhead) or "*" (any). "A" is the default
  value, which means that the SoftLock only applies to an active flight.
S TrafficDay
  D   = Daily
  1-7 = Traffic day on which leg 1 departs (in local time).
  Example string: "67" (weekend legs)
D DateFrom
  Start date for the soft lock.
  Date on which leg 1 departs (in local time).
D DateTo
  End date for the soft lock.
  Date on which leg 1 departs (in local time).
S Carrier2. Mandatory if FlightNr2 or DepArr2 is used.
  Carrier of leg 2.
I FlightNr2
  This flight number is used as leg 2 for soft lock types REQ_CXN_...
  and NOT_CXN_... (for ..._BEF types leg 2 is before leg 1, otherwise after.)
S DepArr2
  The departure and arrival airport of leg 2 on the format "DEP-ARR".
  May be used instead of FlightNr2. (for ..._BEF types leg 2 is before leg 1,
  otherwise after.)
S ActiveOrDH2
  String which limits the SoftLock to Active or DH flights for leg 2. Valid
  strings are "A" (active), "D" (deadhead) or "*" (any). "A" is the default
  value, which means that the SoftLock only applies to an active flight.
R LimitMin
  Reltime minimum limit used for SoftLock types REQ_CXN_AFT, NOT_CXN_AFT,
  REQ_CXN_BEF, NOT_CXN_BEF, REQ_REST_AFT and REQ_REST_BEF.
  Denoted as "XX:XX". 0:00 means that LimitMin will not be used.
R LimitMax
  Reltime maximum limit used for SoftLock types REQ_CXN_AFT, NOT_CXN_AFT,
  REQ_CXN_BEF, NOT_CXN_BEF, REQ_REST_AFT and REQ_REST_BEF.
  Denoted as "YY:YY". 0:00 means that LimitMax will not be used.
S Base
  Base in use for soft lock types 1 and 2.
S ACType
  Aircraft type for which the soft lock apply.
  Blank = All AC types
B ACChange
  If true, the SoftLock is only applied if there is an AC change.
  Can be used for REQ_CXN_... and NOT_CXN_...
I Penalty
   >10 = Penalty to use
  1-10 = Standard penalty from parameter set is used (1=low, 9=high)
     0 = The soft lock is to be regarded as a rule.
B Active
  true  = Use this soft lock
  false = Do not use this soft lock
C Comment
  All comments go here (ignored by the SoftLock package).
*/"""

gDebug = 0
gStrCARMUSR = os.getenv('CARMUSR')
gStrCARMSYS = os.getenv('CARMSYS')
gStrEtabDir = os.path.join(gStrCARMUSR, 'crc', 'etable')
gStrGroupPrefix = 'SLG'
gStrGroupSeparator = '_'
gStrGroupEnd = ':'
gReGroupIdentifier = re.compile(r'%s%s(?P<id>\d+)%s(?P<subId>\d+)(%s(?P<comment>.*)|)' %(gStrGroupPrefix, gStrGroupSeparator, gStrGroupSeparator, gStrGroupEnd))
gReSoftLockReqNotType = re.compile(r'(?P<reqOrNot>REQ|NOT)_(?P<lockType>\w+)')
gReStartEndLock = re.compile(r'(?P<tripOrDuty>TRIP|DUTY)(?P<startOrEnd>START|END)')
gReCxnRestLock = re.compile(r'(?P<cxnOrRest>CXN|REST)_(?P<aftOrBef>AFT|BEF)')
gReBool = re.compile(r'\W*((?P<true>1|true|y)|(?P<false>0|false|n))\W*', re.IGNORECASE)
gReSLCarrier = re.compile(r'^[A-Z0-9][A-Z]$|^[A-Z][A-Z][A-Z]$|^[A-Z][A-Z0-9]$')
gReSLDepArr = re.compile(r'^(?P<dep>[A-Z����]{1,5})-(?P<arr>[A-Z����]{1,5})$')
gReSLDate = re.compile(r'^[0123]\d(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[12]\d{3}$')
gReSLBase = re.compile(r'^[A-Z����]{1,5}$')
gReSLTrafficDay = re.compile(r'^D?X?[1-7]*$', re.IGNORECASE)
gReSLLimit = re.compile(r'^\d+:\d{2}$')
gReSLComment = re.compile(r'^[^"]*$')
gReNumber = re.compile(r'^\d+$')
gIntOneDay = 1440
gStrSeparator = ','
gTypeLeg1 = 1
gTypeLeg2 = 2
gStrArrowCxn =   ' -> '
gStrArrowNoCxn = ' || '
gNumSLGroupCxns = 6
gNumSLGroupLegs = 5
gListTypes = ['REQ_BASE',
              'NOT_BASE',
              'REQ_TRIPSTART',
              'REQ_TRIPEND',
              'NOT_TRIPSTART',
              'NOT_TRIPEND',
              'REQ_DUTYSTART',
              'REQ_DUTYEND',
              'NOT_DUTYSTART',
              'NOT_DUTYEND',
              'REQ_CXN_AFT',
              'NOT_CXN_AFT',
              'REQ_CXN_BEF',
              'NOT_CXN_BEF',
              'REQ_REST_AFT',
              'REQ_REST_BEF',
              'CXN_BUFFER']
gMapMonths = {'JAN' :  1,
              'FEB' :  2,
              'MAR' :  3,
              'APR' :  4,
              'MAY' :  5,
              'JUN' :  6,
              'JUL' :  7,
              'AUG' :  8,
              'SEP' :  9,
              'OCT' : 10,
              'NOV' : 11,
              'DEC' : 12}

gListTrueStrUpper = ['1', 'TRUE', 'T', 'YES', 'Y']
gIxType = 0
gIxCarrier1 = 1
gIxFlightNr1 = 2
gIxDepArr1 = 3
gIxActiveOrDH1 = 4
gIxTrafficDay = 5
gIxDateFrom = 6
gIxDateTo = 7
gIxCarrier2 = 8
gIxFlightNr2 = 9
gIxDepArr2 = 10
gIxActiveOrDH2 = 11
gIxLimitMin = 12
gIxLimitMax = 13
gIxBase = 14
gIxACType = 15
gIxACChange = 16
gIxPenalty = 17
gIxActive = 18
gIxComment = 19
gStrStdDateFrom = '01JAN1986'
gStrStdDateTo = '01JAN2030'
gStrStdLimit = '0:00'
gListStrUnsetLimit = ['', '0:00', '00:00', '999:00']

############################## --------------------- ##############################
##############################      functions        ##############################
############################## --------------------- ##############################

# read a file into a buffer and return the buffer
#def readFile(filename):
#    f = open(filename)
#    buffer = map(lambda line: line.replace(os.linesep, ''), f.readlines())
#    f.close()
#    return buffer

# write a file from a list of lines
#def writeFile(filename, lines):
#    outFile = open(filename, 'w')
#    for line in lines:
#        outFile.write(line + '\n')
#    outFile.close

def printDebug(strDebug):
    if gDebug:
        print strDebug
        sys.stdout.flush()

# print warning
#def printWarning(strWarning):
#    print '  *** Warning: %s' %(strWarning)
#    sys.stdout.flush()

def printError(strError):
    print '  *** Error: %s' %(strError)
    sys.stdout.flush()

def strToBool(strBool):
    if strBool in [0, 1]:
        return strBool
    matchBool = gReBool.match(strBool)
    if matchBool:
        if matchBool.group('true'):
            return 1
        return 0
    else:
        printError('strToBool called with faulty string: "%s"' %(strBool))
        return None

def any(listBool):
    return reduce(lambda a, b: bool(a) or bool(b), listBool, 0)

#def removeDuplicates(list):
#    ix = 0
#    while ix < len(list):
#        if list[ix] in list[:ix]:
#            del list[ix]
#        else:
#            ix += 1

def getAllAirports(listLegs):
    listAllAirports = []
    for aLeg in listLegs:
        listAllAirports += aLeg[2:4]
    removeDuplicates(listAllAirports)
    listAllAirports.sort()
    return listAllAirports

def getAllBases(listLegs):
    listAllBases = []
    for aLeg in listLegs:
        listAllBases += aLeg[7:8]
    removeDuplicates(listAllBases)
    listAllBases.sort()
    return listAllBases

def getAllACTypes(listLegs):
    listAllACTypes = []
    for aLeg in listLegs:
        listAllACTypes.append(aLeg[4])
    removeDuplicates(listAllACTypes)
    listAllACTypes.sort()
    return listAllACTypes

def getTupDataFromReport(strReportFilename):
    listReport = map(lambda line: line.split(gStrSeparator), readFile(strReportFilename))
    if len(listReport) == 0 or not listReport[0]:
        return None
    (timeMin, timeMax) = map(lambda s: int(s), listReport[0])
    # The 'dates' are given in minutes since 1986-01-01 00:00
    listDates = []
    ixLine = 2
    aLine = listReport[ixLine]
    while len(aLine) > 1:
        listDates.append(map(lambda s: int(s), aLine))
        ixLine += 1
        aLine = listReport[ixLine]
    listLegs = listReport[ixLine + 1:]
    listEtabRowsToUpper = []
    listAllACTypes = getAllACTypes(listLegs)
    listAllAirports = getAllAirports(listLegs)
    listAllBases = getAllBases(listLegs)    
    return [listLegs, listAllACTypes, listAllAirports, listAllBases, listDates, timeMin, timeMax]

def getStrDatePlusXDays(strDate, dayDiff):
    absTime = Abstime(strDate)
    absTime += gIntOneDay * dayDiff
    return ((str(absTime))[:9]).upper()

def getStrFlightNr(intFlightNr):
    try:
        strFlightNr = '%03d' %(intFlightNr)
        return strFlightNr
    except:
        pass
    return None

############################## --------------------- ##############################
##############################       classes         ##############################
############################## --------------------- ##############################

class SoftLockEtab:
    """
    The SoftLockEtab class represents a SoftLock etab,
    and is associated with a specific etab file name.
    The class also acts as a SoftLock handler

    """
    def __init__(self, strFilename=None, strReportFile=None):
        self.hasReportData = 0
        self.intHighestUniqueIdSL = 1
        self.intHighestUniqueIdSLGroup = 1
        self.strReportFile = strReportFile
        # mapSLId is: {intUniqueId => SoftLock}
        self.mapSLId = {}
        # listSLRow is: [intUniqueId_row1, intUniqueId_row2, ...]
        self.listSLRow = []
        # mapSLGroups is: {intUniqueId => SoftLockGroup}
        self.mapSLGroupId = {}
        # listSLGroupRow is: [intUniqueId_row1, intUniqueId_row2, ...]
        self.listSLGroupRow = []
        # Read report data (if any)
        self.mapCarrierOccurences = {}
        self.listCarrierOccurences = []
        if strReportFile and os.path.isfile(strReportFile):
            tupData = getTupDataFromReport(strReportFile)
            if tupData:
                self.hasReportData = 1
                [listLegs, listAllACTypes, listAllAirports, listAllBases, listDates, timeMin, timeMax] = tupData
                self.datePeriodStart = Abstime(timeMin)
                self.datePeriodEnd = Abstime(timeMax)
                for tupLeg in listLegs:
                    if tupLeg[0] not in self.mapCarrierOccurences.keys():
                        self.mapCarrierOccurences[tupLeg[0]] = 1
                    else:
                        self.mapCarrierOccurences[tupLeg[0]] += 1
                for strCarrier in self.mapCarrierOccurences.keys():
                    self.listCarrierOccurences.append((strCarrier, self.mapCarrierOccurences[strCarrier]))
                self.listCarrierOccurences.sort(lambda a, b: cmp(a[1], b[1]))
        if strFilename:
            self.strFilename = os.path.join(gStrEtabDir, strFilename)
            self.strDefaultDir = '%s/' %(os.path.dirname(self.strFilename))
            if os.path.isfile(self.strFilename):
                strProblems = self.readSoftLocksFromFile()
                if strProblems:
                    printWarning(strProblems)
                    self.strFilename = None
            else:
                self.strFilename = None
        else:
            self.strFilename = None
            self.strDefaultDir = None
        printDebug('SoftLockEtab file: "%s"' %(self.strFilename))
        self.hasChanged = 0
    def _getIntUniqueIdSL(self):
        self.intHighestUniqueIdSL += 1
        return self.intHighestUniqueIdSL
    def _getIntUniqueIdSLGroup(self):
        self.intHighestUniqueIdSLGroup += 1
        return self.intHighestUniqueIdSLGroup
    def registerIntUniqueIdSL(self, intId):
        if self.intHighestUniqueIdSL < intId:
            self.intHighestUniqueIdSL = intId
    def registerIntUniqueIdSLGroup(self, intId):
        if self.intHighestUniqueIdSLGroup < intId:
            self.intHighestUniqueIdSLGroup = intId
    def moveSoftLockUp(self, intUniqueId):
        if intUniqueId in self.listSLRow:
            intRow = self.listSLRow.index(intUniqueId)
            if intRow > 0:
                self.listSLRow[intRow - 1:intRow + 1] = [intUniqueId, self.listSLRow[intRow - 1]]
    def moveSoftLockDown(self, intUniqueId):
        if intUniqueId in self.listSLRow:
            intRow = self.listSLRow.index(intUniqueId)
            if intRow < len(self.listSLRow) - 1:
                self.listSLRow[intRow:intRow + 2] = [self.listSLRow[intRow + 1], intUniqueId]
    def toggleSLOnOff(self, intUniqueId):
        if intUniqueId not in self.mapSLId.keys():
            raise Exception('Cannot toggle SoftLock id "%d", it does not exist' %(intUniqueId))
        softLock = self.mapSLId[intUniqueId]
        softLock.setBoolActive(not softLock.getBoolActive())
    def getListSLRow(self):
        return self.listSLRow
    def getSoftLockInRow(self, intRow):
        if intRow < 1 or intRow > len(self.listSLRow):
            return None
        return self.mapSLId[self.listSLRow[intRow - 1]]
    def getSoftLockGroupInRow(self, intRow):
        if intRow < 1 or intRow > len(self.listSLGroupRow):
            return None
        return self.mapSLGroupId[self.listSLGroupRow[intRow - 1]]
    def moveSoftLockGroupUp(self, intUniqueId):
        if intUniqueId in self.listSLGroupRow:
            intRow = self.listSLGroupRow.index(intUniqueId)
            if intRow > 0:
                self.listSLGroupRow[intRow - 1:intRow + 1] = [intUniqueId, self.listSLGroupRow[intRow - 1]]
    def moveSoftLockGroupDown(self, intUniqueId):
        if intUniqueId in self.listSLGroupRow:
            intRow = self.listSLGroupRow.index(intUniqueId)
            if intRow < len(self.listSLGroupRow) - 1:
                self.listSLGroupRow[intRow:intRow + 2] = [self.listSLGroupRow[intRow + 1], intUniqueId]
    def getListSLGroupRow(self):
        return self.listSLGroupRow
    def getSoftLockGroupInRow(self, intRow):
        if intRow < 1 or intRow > len(self.listSLGroupRow):
            return None
        return self.mapSLGroupId[self.listSLGroupRow[intRow - 1]]
    def getHasChanged(self):
        return self.hasChanged
    def setHasChanged(self, boolHasChanged):
        self.hasChanged = boolHasChanged
    def getStrReportFile(self):
        if not self.hasReportData:
            return None
        return self.strReportFile
    def writeSoftLocksToFile(self):
        if not self.strFilename:
            printError('Cannot do writeSoftLocksToFile() - filename not set!')
            return
        listEtabRows = []
        # SoftLocks
        for slId in self.listSLRow:
            listStrValues = self.mapSLId[slId].getListStrValues()
            listStrValues[gIxDateTo] = getStrDatePlusXDays(listStrValues[gIxDateTo], 1)
            listEtabRows.append(listStrValues)
        # SoftLock groups
        for slgId in self.listSLGroupRow:
            listSoftLocks = self.mapSLGroupId[slgId].getListSoftLocks()
            for ixRow in range(len(listSoftLocks)):
                for softLock in listSoftLocks[ixRow]:
                    softLock.setStrComment('%s:%s' %(self.mapSLGroupId[slgId].getStrGroupIdentifier(ixRow + 1), softLock.getStrComment()))
                    listStrValues = softLock.getListStrValues()
                    listStrValues[gIxDateTo] = getStrDatePlusXDays(listStrValues[gIxDateTo], 1)
                    listEtabRows.append(listStrValues)
        # Write to file
        self.etab = [gListSLEtabCols, listEtabRows, gStrStdSLEtabComment, self.strFilename]
        self._writeTupEtab(self.etab)
        self.setHasChanged(0)
    # A tupEtab is (listEtabCols, listEtabRows, strEtabComment, strFilename)
    # This function corresponds to EtabHE.writeEtab(strFilename, tupEtab)
    def _writeTupEtab(self, tupEtab):
        return writeEtab(tupEtab[3], tupEtab)
    # Returns a tupEtab: (listEtabCols, listEtabRows, strEtabComment, strFilename)
    # This function corresponds to EtabHE.readEtab(strFilename)
    def _readTupEtab(self, strFilename):
        return readEtab(strFilename)
    # Returns string with problems if SoftLock etab could not be loaded
    def readSoftLocksFromFile(self):
        etabRead = self._readTupEtab(self.strFilename)
        if not etabRead:
            return 'The etab "%s" could not be read' %(self.strFilename)
        (listEtabCols, listEtabRows, strFirstComment, strFilename) = etabRead
        if not self.checkIfSLEtabCols(listEtabCols):
            return 'The columns of etab "%s" do not correspond to those of a SoftLock etab' %(self.strFilename)
        self.etab = [listEtabCols, listEtabRows, strFirstComment, strFilename]
        listSoftLocks = []
        mapSoftLockGroups = {}
        listSoftLockGroupId = []
        strCommentBest = ''
        for listCols in listEtabRows:
            listCols[gIxDateTo] = getStrDatePlusXDays(listCols[gIxDateTo], -1)
            (intId, intSubId, strComment) = SoftLockGroup.findIntIds(listCols[gIxComment])
            if strComment:
                strCommentBest = strComment
            if intId:
                if intId not in mapSoftLockGroups.keys():
                    mapSoftLockGroups[intId] = SoftLockGroup(self, intId)
                    listSoftLockGroupId.append(intId)
                    self.registerIntUniqueIdSLGroup(intId)
                if listCols[gIxType] == 'REQ_CXN_AFT':
                    softLock = SoftLock(listCols, parentEtab=self)
                    softLock.setIntUniqueId(self._getIntUniqueIdSL())
                    softLock.setStrComment(strCommentBest)
                    mapSoftLockGroups[intId].setDefaultSoftLock(softLock)
                    printDebug('Setting default SoftLock to "%s"' %(softLock))
                    tupLeg1 = listCols[gIxFlightNr1:gIxDepArr1 + 1] + [0]
                    tupLeg2 = listCols[gIxFlightNr2:gIxDepArr2 + 1] + [0]
                    mapSoftLockGroups[intId].addConnection(intSubId, tupLeg1, tupLeg2)
                elif listCols[gIxType] == 'REQ_DUTYSTART':
                    mapSoftLockGroups[intId].setBoolDutyStop(intSubId, len(mapSoftLockGroups[intId].getListCxnLegs(intSubId)) - 2, 1)
                elif listCols[gIxType] == 'REQ_TRIPSTART':
                    mapSoftLockGroups[intId].setBoolTripStart(intSubId, 1)
                elif listCols[gIxType] == 'REQ_TRIPEND':
                    mapSoftLockGroups[intId].setBoolTripEnd(intSubId, 1)
            else:
                listSoftLocks.append(SoftLock(listCols))
        self.setListSoftLocks(listSoftLocks)
        self.clearSoftLockGroups()
        for intId in listSoftLockGroupId:
            self.addSoftLockGroup(mapSoftLockGroups[intId])
        self.setHasChanged(0)
        return None
    def getMapSoftLocks(self):
        return self.mapSLId
    def clearSoftLocks(self):
        self.mapSLId = {}
        self.listSLRow = []
    def clearSoftLockGroups(self):
        self.mapSLGroupId = {}
        self.listSLGroupRow = []
    def getMapSoftLockGroups(self):
        return self.mapSLGroupId
    def setListSoftLocks(self, listSL):
        self.clearSoftLocks()
        for ixSL in range(len(listSL)):
            self.addSoftLock(listSL[ixSL])
    def addSoftLock(self, softLock):
        if not softLock.getIntUniqueId():
            softLock.setIntUniqueId(self._getIntUniqueIdSL())
        softLock.setParentEtab(self)
        self.mapSLId[softLock.getIntUniqueId()] = softLock
        self.listSLRow.append(softLock.getIntUniqueId())
    def deleteSoftLock(self, softLock):
        if not softLock.getIntUniqueId():
            raise Exception('Cannot remove SoftLock "%s", it has no id' %(softLock))
        if softLock.getIntUniqueId() in self.listSLRow:
            del self.mapSLId[softLock.getIntUniqueId()]
            self.listSLRow.remove(softLock.getIntUniqueId())
        else:
            raise Exception('Cannot remove SoftLock "%s", it does not exist in etab' %(softLock))
    def addSoftLockGroup(self, slGroup):
        intSLGId = slGroup.getIntUniqueId()
        if intSLGId in self.mapSLGroupId.keys():
            raise Exception('Trying to add SoftLock group with id %d, which already exist!' %(intSLGId))
        self.mapSLGroupId[intSLGId] = slGroup
        self.listSLGroupRow.append(intSLGId)
    def deleteSoftLockGroup(self, slGroup):
        if not slGroup.getIntUniqueId():
            raise Exception('Cannot remove SoftLock group "%s", it has no id' %(slGroup))
        if slGroup.getIntUniqueId() in self.listSLGroupRow:
            del self.mapSLGroupId[slGroup.getIntUniqueId()]
            self.listSLGroupRow.remove(slGroup.getIntUniqueId())
        else:
            raise Exception('Cannot remove SoftLock group "%s", it does not exist in etab' %(slGroup))
    def createNewSoftLock(self):
        softLock = SoftLock('REQ_CXN_AFT', self.getStrCarrierMaxOccurences(), parentEtab=self)
        self.addSoftLock(softLock)
        softLock.setIntFlightNr1(0)
        softLock.correctByType()
        return softLock
    def createNewSoftLockGroup(self):
        slGroup = SoftLockGroup(parentEtab=self, intUniqueId=self._getIntUniqueIdSLGroup())
        self.addSoftLockGroup(slGroup)
        slGroup.setStrCarrier(self.getStrCarrierMaxOccurences())
        slGroup.getDefaultSoftLock().correctByType()
        return slGroup
    def getStrFilename(self):
        return self.strFilename
    def setStrFilename(self, strFilename):
        self.strFilename = strFilename
    def getStrDefaultDir(self):
        return self.strDefaultDir
    def setStrDefaultDir(self, strDefaultDir):
        self.strDefaultDir = strDefaultDir
    def getStrName(self):
        return os.path.basename(self.strFilename)
    def getIntSLRowNum(self, intUniqueId):
        if intUniqueId in self.listSLRow:
            return self.listSLRow.index(intUniqueId)
        return None
    def getIntSLGroupRowNum(self, intUniqueId):
        if intUniqueId in self.listSLGroupRow:
            return self.listSLGroupRow.index(intUniqueId)
        return None
    def getStrCarrierMaxOccurences(self):
        if not self.hasReportData or not self.listCarrierOccurences:
            return ''
        return self.listCarrierOccurences[0][0]
    def getListCarrierOccurences(self):
        if not self.hasReportData:
            return None
        return self.listCarrierOccurences
    def getMapCarrierOccurences(self):
        if not self.hasReportData:
            return None
        return self.mapCarrierOccurences
    
##        return {'strRepr' : strRepr, 'intTypeLen' : intTypeLenOut,
##                'intFlightNr1RPos' : intFlightNr1RPosOut, 'intArrowPos' : intArrowPosOut,
##                'intFlightNr2RPos' : intFlightNr2RPosOut, 'intTotalLen' : intTotalLenOut}
    def getMapSLReprFixedWidth(self, maxLen=None, maxArrowPos=None):
        listKeys = ['intTypeLen', 'intFlightNr1RPos', 'intArrowPos', 'intFlightNr2RPos', 'intTotalLen']
        mapMaxValue = {'intArrowPos':maxArrowPos, 'intTotalLen':maxLen}
        listLocked = []
        showIfActive = any(map(lambda k: not self.mapSLId[k].getBoolActive(), self.listSLRow))
        while len(listLocked) < len(listKeys):
            strElem = listKeys[len(listLocked)]
            intMaxLen = 0
            for slKey in self.listSLRow:
                slReprFixedWidth = self.mapSLId[slKey].getCustomRepr(*listLocked, **{'showIfActive':showIfActive})
                intMaxLen = max(intMaxLen, slReprFixedWidth[strElem])
            if strElem in mapMaxValue.keys() and mapMaxValue[strElem] and mapMaxValue[strElem] < intMaxLen:
                intMaxLen = mapMaxValue[strElem]
            listLocked.append(intMaxLen)
        mapSLReprFixedWidth = {}
        for slKey in self.listSLRow:
            mapSLReprFixedWidth[slKey] = self.mapSLId[slKey].getCustomRepr(*listLocked, **{'showIfActive':showIfActive})
        return mapSLReprFixedWidth
    def getMapSLGroupListReprFixedWidth(self):
        mapSLGroupReprFixedWidth = {}
        for slgId in self.mapSLGroupId.keys():
            mapSLGroupReprFixedWidth[slgId] = self.mapSLGroupId[slgId].getListStrRepr()
        return mapSLGroupReprFixedWidth
    def strDateIsInPeriod(self, strDate):
        if not self.hasReportData:
            return None
        dateIn = Abstime(strDate)
        return dateIn > self.datePeriodStart and dateIn < self.datePeriodEnd
    def checkIfSLEtabCols(self, listEtabCols):
        return str(map(lambda t: t[:2], gListSLEtabCols)) == str(map(lambda t: t[:2], listEtabCols))
    checkIfSLEtabCols = classmethod(checkIfSLEtabCols)

# Implements the most often-used SoftLocks, i.e. "Connect the leg sequence 101-102-103"
class SoftLockGroup:
    def __init__(self, parentEtab, intUniqueId):
        self.parentEtab = parentEtab
        self.setDefaultSoftLock(SoftLock('REQ_CXN_AFT', self.parentEtab.getStrCarrierMaxOccurences(), parentEtab=self.parentEtab))
        self.setIntUniqueId(intUniqueId)
        # Cxn legs are not instances of SoftLockLeg, but rather a reduced representation of a leg,
        # consisting of: [intFlightNr, strDepArr, boolDutyStopAfter]
        # the tuple can have None in it, but cannot be [None, None, <bool>]
        
        # {listCxnLegs, boolTripStart, boolTripEnd}
        # {         [],             0,           0}
        self.mapCxn = {}
    def __repr__(self):
        return '\n'.join(self.getListStrRepr())
    def getListStrRepr(self):
        intExtraInfoPos = 35
        intTotalLen = 50
        listStrRepr = []
        for intId in self.mapCxn.keys():
            listStrRepr.append((self.getIdCustomRepr(intId, intExtraInfoPos, intTotalLen))['strRepr'])
        return listStrRepr
    def getIdCustomRepr(self, intId, intExtraInfoPos=None, intTotalLen=None):
        if intId not in self.mapCxn.keys():
            raise Exception('Invalid group id "%s"' %(intId))
        tupCxn = self.mapCxn[intId]
        listStrLegs = []
        for tupLeg in tupCxn[0]:
            listTupLeg = []
            if tupLeg[0]:
                try:
                    intFlightNr = int(tupLeg[0])
                    if intFlightNr > 0:
                        listTupLeg.append(getStrFlightNr(intFlightNr))
                except:
                    pass
            if tupLeg[1]:
                listTupLeg.append(tupLeg[1])
            if tupLeg[2]:
                listTupLeg.append('//')
            else:
                listTupLeg.append('->')
            listStrLegs += listTupLeg
        if listStrLegs:
            strRepr = ' '.join(listStrLegs[:-1])
            if self.getBoolTripStart(intId):
                strRepr = '|- ' + strRepr
            if self.getBoolTripEnd(intId):
                strRepr = strRepr + ' -|'
            return {'strRepr' : strRepr}
        return {'strRepr' : ''}
    def setParentEtab(self, slEtab):
        self.parentEtab = slEtab
    def getParentEtab(self):
        return self.parentEtab
    def getCopy(self):
        softLockGroup = SoftLockGroup(self.parentEtab, self.getParentEtab()._getIntUniqueIdSLGroup())
        softLockGroup.setDefaultSoftLock(self.getDefaultSoftLock().getCopy())
        softLockGroup.setMapCxn(copy.deepcopy(self.getMapCxn()))
        return softLockGroup
    def getStrGroupIdentifier(self, intId):
        if not hasattr(self, 'intUniqueId'):
            return None
        return gStrGroupSeparator.join([gStrGroupPrefix, str(self.intUniqueId), str(intId)])
    # Returns the tuple (intId, intSubId, strComment)
    def findIntIds(self, strComment):
        matchId = gReGroupIdentifier.search(strComment)
        if matchId:
            if 'comment' in matchId.groupdict().keys() and matchId.group('comment'):
                strCommentPart = matchId.group('comment')
            else:
                strCommentPart = None
            return (int(matchId.group('id')), int(matchId.group('subId')), strCommentPart)
        return (None, None, strComment)
    findIntIds = classmethod(findIntIds)
    def setIntUniqueId(self, intUniqueId):
        self.intUniqueId = int(intUniqueId)
        if hasattr(self, 'parentEtab') and self.parentEtab:
            self.parentEtab.registerIntUniqueIdSLGroup(intUniqueId)
    def getIntUniqueId(self):
        if not hasattr(self, 'intUniqueId'):
            return None
        return self.intUniqueId
    def setDefaultSoftLock(self, softLock):
        self.defaultSL = softLock
    def getDefaultSoftLock(self):
        return self.defaultSL
    def checkTupLeg(self, tupLeg):
        listStrProblems = []
        if len(tupLeg) != 3:
            listStrProblems.append('Wrong length of tupLeg "%s"' %(tupLeg))
        elif not tupLeg[0] and not tupLeg[1]:
            listStrProblems.append('Cxn leg "%s" not ok.' %(tupLeg))
        else:
            if tupLeg[0]:
                strFlightCheck = SoftLock.checkIntFlightNr(tupLeg[0])
                if strFlightCheck:
                    listStrProblems.append(strFlightCheck)
            if tupLeg[1]:
                strDepArrCheck = SoftLock.checkStrDepArr(tupLeg[1])
                if strDepArrCheck:
                    listStrProblems.append(strDepArrCheck)
        return listStrProblems
    checkTupLeg = classmethod(checkTupLeg)
    def addConnection(self, intId, tupLeg1, tupLeg2):
        listStrProblems = self.checkTupLeg(tupLeg1) + self.checkTupLeg(tupLeg2)
        if listStrProblems:
            raise Exception('\n'.join(listStrProblems))
        if intId not in self.mapCxn.keys():
            self.mapCxn[intId] = [[], 0, 0]
        if len(self.mapCxn[intId][0]) == 0:
            self.mapCxn[intId][0].append(tupLeg1)
        elif str(self.mapCxn[intId][0][-1][:2]) != str(tupLeg1[:2]):
            raise Exception('Connection mismatch in SoftLocksGroup, %s does not match %s' %(self.mapCxn[intId][0][-1][:2], tupLeg1[:2]))
        self.mapCxn[intId][0].append(tupLeg2)
    def getBoolDutyStop(self, intId, ixLeg):
        if intId not in self.mapCxn.keys():
            raise Exception('Invalid group id "%s"' %(intId))
        if len(self.mapCxn[intId][0]) <= ixLeg:
            raise Exception('Invalid leg index "%s"' %(ixLeg))
        return self.mapCxn[intId][0][ixLeg][2]
    def setBoolDutyStop(self, intId, ixLeg, boolDutyStart):
        if intId not in self.mapCxn.keys():
            raise Exception('Invalid group id "%s"' %(intId))
        if len(self.mapCxn[intId][0]) <= ixLeg:
            raise Exception('Invalid leg index "%s"' %(ixLeg))
        self.mapCxn[intId][0][ixLeg][2] = boolDutyStart
    def getBoolTripStart(self, intId):
        if intId not in self.mapCxn.keys():
            raise Exception('Invalid group id "%s"' %(intId))
        return self.mapCxn[intId][1]
    def setBoolTripStart(self, intId, boolTripStart):
        if intId not in self.mapCxn.keys():
            self.mapCxn[intId] = [[], 0, 0]
        self.mapCxn[intId][1] = boolTripStart
    def getBoolTripEnd(self, intId):
        if intId not in self.mapCxn.keys():
            raise Exception('Invalid group id "%s"' %(intId))
        return self.mapCxn[intId][2]
    def setBoolTripEnd(self, intId, boolTripEnd):
        if intId not in self.mapCxn.keys():
            self.mapCxn[intId] = [[], 0, 0]
        self.mapCxn[intId][2] = boolTripEnd
    def getMapCxn(self):
        return self.mapCxn
    def setMapCxn(self, mapCxn):
        self.mapCxn = mapCxn
    def getListCxnIds(self):
        return self.mapCxn.keys()
    def getListCxnLegs(self, intId):
        if intId not in self.mapCxn.keys():
            raise Exception('Invalid group id "%s"' %(intId))
        return self.mapCxn[intId][0]
    def emptyCxnLegs(self):
        self.mapCxn = {}
    def setListCxnLegs(self, intId, listCxnLegs):
        listStrProblems = []
        for tupLeg in listCxnLegs:
            listStrProblems += self.checkTupLeg(tupLeg)
        if listStrProblems:
            raise Exception('\n'.join(listStrProblems))
        else:
            if intId not in self.mapCxn:
                self.mapCxn[intId] = [listCxnLegs[:], 0, 0]
            else:
                self.mapCxn[intId][0] = listCxnLegs[:]
    def _getDefaultSoftLockCopy(self, tupLeg1, tupLeg2=None, strSLType='REQ_CXN_AFT'):
        slCopy = self.getDefaultSoftLock().getCopy()
        slCopy.setStrType(strSLType)
        # Stupidly enough, this is needed (why?):
        slCopy.setIntFlightNr1(0)
        slCopy.setStrDepArr1('')
        slCopy.setIntFlightNr2(0)
        slCopy.setStrDepArr2('')
        slCopy.setIntUniqueId(self.parentEtab._getIntUniqueIdSL())
        if tupLeg1[0]:
            slCopy.setIntFlightNr1(tupLeg1[0])
        if tupLeg1[1]:
            slCopy.setStrDepArr1(tupLeg1[1])
        if tupLeg2:
            if tupLeg2[0]:
                slCopy.setIntFlightNr2(tupLeg2[0])
            if tupLeg2[1]:
                slCopy.setStrDepArr2(tupLeg2[1])
        slCopy.correctByType()
        return slCopy
    def getListSoftLocks(self):
        listSL = []
        for intId in self.mapCxn.keys():
            listCxnLegs = self.getListCxnLegs(intId)
            if len(listCxnLegs) >= 2:
                lastLeg = listCxnLegs[0]
                listSL.append([])
                if self.getBoolTripStart(intId):
                    listSL[-1].append(self._getDefaultSoftLockCopy(lastLeg, strSLType='REQ_TRIPSTART'))
                boolLastHadDutyStop = listCxnLegs[0][2]
                if boolLastHadDutyStop:
                    listSL[-1].append(self._getDefaultSoftLockCopy(lastLeg, strSLType='REQ_DUTYEND'))
                for aLeg in listCxnLegs[1:]:
                    listSL[-1].append(self._getDefaultSoftLockCopy(lastLeg, aLeg))
                    if boolLastHadDutyStop:
                        listSL[-1].append(self._getDefaultSoftLockCopy(aLeg, strSLType='REQ_DUTYSTART'))
                    if aLeg[2]:
                        listSL[-1].append(self._getDefaultSoftLockCopy(aLeg, strSLType='REQ_DUTYEND'))
                        boolLastHadDutyStop = 1
                    else:
                        boolLastHadDutyStop = 0
                    lastLeg = aLeg
                if self.getBoolTripEnd(intId):
                    listSL[-1].append(self._getDefaultSoftLockCopy(lastLeg, strSLType='REQ_TRIPEND'))
        return listSL
    def getIntPenalty(self):
        return self.defaultSL.getIntPenalty()
    def setIntPenalty(self, intPenalty):
        self.defaultSL.setIntPenalty(intPenalty)
    def getStrCarrier(self):
        return self.defaultSL.getStrCarrier1()
    def setStrCarrier(self, strCarrier):
        self.defaultSL.setStrCarrier1(strCarrier)
        self.defaultSL.setStrCarrier2(strCarrier)
    def getStrACType(self):
        return self.defaultSL.getStrACType()
    def setStrACType(self, strACType):
        self.defaultSL.setStrACType(strACType)
    def getStrActiveOrDH(self):
        return self.defaultSL.getStrActiveOrDH1()
    def setStrActiveOrDH(self, strActiveOrDH):
        self.defaultSL.setStrActiveOrDH1(strActiveOrDH)
        self.defaultSL.setStrActiveOrDH2(strActiveOrDH)
    def getStrDateFrom(self):
        return self.defaultSL.getStrDateFrom()
    def setStrDateFrom(self, strDateFrom):
        self.defaultSL.setStrDateFrom(strDateFrom)
    def getStrDateTo(self):
        return self.defaultSL.getStrDateTo()
    def setStrDateTo(self, strDateTo):
        self.defaultSL.setStrDateTo(strDateTo)
    def getStrLimitMin(self):
        return self.defaultSL.getStrLimitMin()
    def setStrLimitMin(self, strLimitMin):
        self.defaultSL.setStrLimitMin(strLimitMin)
    def getStrLimitMax(self):
        return self.defaultSL.getStrLimitMax()
    def setStrLimitMax(self, strLimitMax):
        self.defaultSL.setStrLimitMax(strLimitMax)
    def getStrBase(self):
        return self.defaultSL.getStrBase()
    def setStrBase(self, strBase):
        self.defaultSL.setStrBase(strBase)
    def getStrComment(self):
        return self.defaultSL.getStrComment()
    def setStrComment(self, strComment):
        self.defaultSL.setStrComment(strComment)

#'EType', 'SCarrier1', 'IFlightNr1', 'SDepArr1', 'SActiveOrDH1', 'STrafficDay', 'ADateFrom', 'ADateTo', 'SCarrier2', 'IFlightNr2', 'SDepArr2', 'SActiveOrDH2', 'RLimitMin', 'RLimitMax', 'SBase', 'SACType', 'BACChange', 'IPenalty', 'BActive', 'CComment'
class SoftLock:
    def __init__(self, initArg, strCarrier1 = '', intFlightNr1 = 0,
                 strDepArr1 = '', strActiveOrDH1 = 'A', strTrafficDay = '',
                 strDateFrom = '', strDateTo = '', strCarrier2 = '',
                 intFlightNr2 = 0, strDepArr2 = '', strActiveOrDH2 = 'A',
                 strLimitMin = '0:00', strLimitMax = '0:00', strBase = '',
                 strACType = '', strACChange = 'false', intPenalty = 0,
                 strActive = 'true', strComment = '', parentEtab=None):
        if type(initArg) == types.ListType:
            self.__ConstructorList(initArg, parentEtab)
        elif type(initArg) == types.StringType:
            self.__ConstructorArgs(initArg, strCarrier1, intFlightNr1,
                                   strDepArr1, strActiveOrDH1, strTrafficDay,
                                   strDateFrom, strDateTo, strCarrier2,
                                   intFlightNr2, strDepArr2, strActiveOrDH2,
                                   strLimitMin, strLimitMax, strBase,
                                   strACType, strACChange, intPenalty,
                                   strActive, strComment, parentEtab)
        else:
            printWarning('class SoftLock initiated with faulty first argument: "%s"' %(initArg))
    def __ConstructorArgs(self, strType, strCarrier1, intFlightNr1, strDepArr1,
                          strActiveOrDH1, strTrafficDay, strDateFrom, strDateTo, strCarrier2,
                          intFlightNr2, strDepArr2, strActiveOrDH2, strLimitMin, strLimitMax,
                          strBase, strACType, strACChange, intPenalty, strActive, strComment,
                          parentEtab=None):
        self.__ConstructorList([strType, strCarrier1, intFlightNr1, strDepArr1, strActiveOrDH1,
                                strTrafficDay, strDateFrom, strDateTo, strCarrier2, intFlightNr2,
                                strDepArr2, strActiveOrDH2, strLimitMin, strLimitMax, strBase,
                                strACType, strACChange, intPenalty, strActive, strComment],
                               parentEtab)
    def __ConstructorList(self, listValues, parentEtab=None):
        self.parentEtab = parentEtab
        self.setListValues(listValues)
        self.mapGetFuncs = {'Type' : self.getStrType, 'Carrier1' : self.getStrCarrier1,
                            'FlightNr1' : self.getIntFlightNr1, 'DepArr1' : self.getStrDepArr1,
                            'ActiveOrDH1' : self.getStrActiveOrDH1,
                            'TrafficDay' : self.getStrTrafficDay, 'DateFrom' : self.getStrDateFrom,
                            'DateTo' : self.getStrDateTo, 'Carrier2' : self.getStrCarrier2,
                            'FlightNr2' : self.getIntFlightNr2, 'DepArr2' : self.getStrDepArr2,
                            'ActiveOrDH2' : self.getStrActiveOrDH2,
                            'LimitMin' : self.getStrLimitMin, 'LimitMax' : self.getStrLimitMax,
                            'Base' : self.getStrBase, 'ACType' : self.getStrACType,
                            'ACChange' : self.getBoolACChange, 'Penalty' : self.getIntPenalty,
                            'Active' : self.getBoolActive, 'Comment' : self.getStrComment}
    def __repr__(self):
        return (self.getCustomRepr())['strRepr']
    def getCustomRepr(self, intTypeLen=None, intFlightNr1RPos=None, intArrowPos=None,
                      intFlightNr2RPos=None, intTotalLen=None, showIfActive=1):
        """Returns the actual pos of the custom values.
        If a part was truncated, a negative value corresponding
        to the number of truncated characters is returned.
        Otherwise, the number of needed characters is returned.
        The custom representation is returned as 'strRepr' in
        the returned map.
        """
        strRepr = ''
        intTypeLenOut = intFlightNr1RPosOut = intArrowPosOut = intFlightNr2RPosOut = intTotalLenOut = 0
        if showIfActive:
            strRepr += ['(', ' '][self.getBoolActive()]
        if self.slType.getStrCxnOrRest() == 'CXN' and self.slType.getStrAftOrBef() == 'BEF':
            legFirst = self.leg2
            legSecond = self.leg1
        else:
            legFirst = self.leg1
            legSecond = self.leg2         
        if self.slType.getStrCxnOrRest() != 'CXN' or not legSecond.isComplete():
            if intTypeLen:
                strType = str(self.slType).ljust(intTypeLen)
            else:
                strType = str(self.slType)
            if intTypeLen and len(strType) > intTypeLen:
                intTypeLenOut = intTypeLen - len(strType)
                strType = strType[:intTypeLen]
            else:
                intTypeLenOut = len(str(self.slType))
            strRepr += strType + ' '
        elif intTypeLen:
            strRepr += ' ' * (intTypeLen + 1)
        if intFlightNr1RPos:
            if intFlightNr1RPos - len(strRepr) < 1:
                strRepr = strRepr[:intFlightNr1RPos - 2] + ' '
            mapLeg1Repr = legFirst.getCustomRepr(intFlightNr1RPos - len(strRepr))
        else:
            mapLeg1Repr = legFirst.getCustomRepr()
        if mapLeg1Repr['intFlightNrRPos'] >= 0:
            intFlightNr1RPosOut = len(strRepr) + mapLeg1Repr['intFlightNrRPos']
        else:
            intFlightNr1RPosOut = mapLeg1Repr['intFlightNrRPos']
        strRepr += mapLeg1Repr['strRepr']            
# {'strRepr' : '<INCOMPLETE LEG>', 'intFlightNrRPos' : 0, 'intTotalLen' : 0}
        if self.slType.getStrCxnOrRest() == 'CXN':
            if legSecond.isComplete():
                # Arrow
                if self.slType.getStrReqOrNot() == 'REQ':
                    strArrow = gStrArrowCxn
                else:
                    strArrow = gStrArrowNoCxn
                if intArrowPos and intArrowPos <= len(strRepr):
                    intArrowPosOut = intArrowPos - len(strRepr) - 1
                    strRepr = strRepr[:intArrowPos - 3] + '..'
                else:
                    intArrowPosOut = len(strRepr) + 1
                if intArrowPos:
                    strRepr += strArrow.rjust(intArrowPos - len(strRepr) - 1 + len(strArrow))
                else:
                    strRepr += strArrow
                # Leg 2
                if intFlightNr2RPos:
                    mapLeg2Repr = legSecond.getCustomRepr(intFlightNr2RPos - len(strRepr))
                else:
                    mapLeg2Repr = legSecond.getCustomRepr()
                if mapLeg2Repr['intFlightNrRPos'] >= 0:
                    intFlightNr2RPosOut = len(strRepr) + mapLeg2Repr['intFlightNrRPos']
                else:
                    intFlightNr2RPosOut = mapLeg2Repr['intFlightNrRPos']
                strRepr += mapLeg2Repr['strRepr']
        if self.getStrLimitMin() and self.getStrLimitMin() not in gListStrUnsetLimit:
            strRepr += ' ' + self.getStrLimitMin() + '-'
        elif self.getStrLimitMax() and self.getStrLimitMax() not in gListStrUnsetLimit:
            strRepr += ' -'
        if self.getStrLimitMax() and self.getStrLimitMax() not in gListStrUnsetLimit:
            strRepr += self.getStrLimitMax()
        if self.getStrBase():
            strRepr += ' [%s]' %(self.getStrBase())
        if self.getBoolACChange():
            strRepr += ' /A/'
        if showIfActive:
            strEndParen = [')', ' '][self.getBoolActive()]
        else:
            strEndParen = ''
        if self.getIntPenalty():
            strPenalty = ' %s' %self.getIntPenalty()
        else:
            strPenalty = ' rule'
        if intTotalLen:
            strRepr += strPenalty.rjust(intTotalLen - len(strRepr) - len(strEndParen)) + strEndParen
        else:
            strRepr += strPenalty + strEndParen
        if intTotalLen and len(strRepr) > intTotalLen:
            intTotalLenOut = intTotalLen - len(strRepr)
            strRepr = strRepr[:intTotalLen - 2 - len(strEndParen)] + '..' + strEndParen
        else:
            intTotalLenOut = len(strRepr)
        return {'strRepr' : strRepr, 'intTypeLen' : intTypeLenOut,
                'intFlightNr1RPos' : intFlightNr1RPosOut, 'intArrowPos' : intArrowPosOut,
                'intFlightNr2RPos' : intFlightNr2RPosOut, 'intTotalLen' : intTotalLenOut}
    def setParentEtab(self, slEtab):
        self.parentEtab = slEtab
    def getParentEtab(self):
        return self.parentEtab
    def getByTypeName(self, strName):
        if strName in self.mapGetFuncs.keys():
            return (self.mapGetFuncs[strName])()
        return None
    def getCopy(self):
        listStrValues = copy.deepcopy(self.getListStrValues())
        softLock = SoftLock(listStrValues, parentEtab=self.parentEtab)
        #softLock = self.parentEtab.createNewSoftLock()
        softLock.setIntUniqueId(self.getParentEtab()._getIntUniqueIdSL())
        return softLock
    def getListValues(self):
        listValues = [self.slType.getStrType(), self.leg1.getStrCarrier(),
                      self.leg1.getIntFlightNr(), self.leg1.getStrDepArr(),
                      self.leg1.getStrActiveOrDH(), self.leg1.getStrTrafficDay(),
                      self.leg1.getStrDateFrom(), self.leg1.getStrDateTo(),
                      self.leg2.getStrCarrier(), self.leg2.getIntFlightNr(),
                      self.leg2.getStrDepArr(), self.leg2.getStrActiveOrDH(),
                      self.strLimitMin, self.strLimitMax, self.strBase,
                      self.leg1.getStrACType(), self.boolACChange,
                      self.intPenalty, self.boolActive, self.strComment]
        return listValues
    def setListValues(self, listValues):
        [strType, strCarrier1, intFlightNr1, strDepArr1, strActiveOrDH1,
         strTrafficDay, strDateFrom, strDateTo, strCarrier2,
         intFlightNr2, strDepArr2, strActiveOrDH2, strLimitMin, strLimitMax,
         strBase, strACType, strACChange, intPenalty, strActive, strComment] = listValues
        self.slType = SoftLockType(strType)
        self.strLimitMin = strLimitMin
        self.strLimitMax = strLimitMax
        self.strBase = strBase
        self.boolACChange = strToBool(strACChange)
        self.intPenalty = int(intPenalty)
        self.boolActive = strToBool(strActive)
        self.strComment = strComment
        # Leg 1
        self.leg1 = SoftLockLeg(self, gTypeLeg1)
        self.leg1.setStrCarrier(strCarrier1)
        self.leg1.setIntFlightNr(intFlightNr1)
        self.leg1.setStrDepArr(strDepArr1)
        self.leg1.setStrActiveOrDH(strActiveOrDH1)
        self.leg1.setStrACType(strACType)
        self.leg1.setStrTrafficDay(strTrafficDay)
        self.leg1.setStrDateFrom(strDateFrom)
        self.leg1.setStrDateTo(strDateTo)
        # Leg 2
        self.leg2 = SoftLockLeg(self, gTypeLeg2)
        self.leg2.setStrCarrier(strCarrier2)
        self.leg2.setIntFlightNr(intFlightNr2)
        self.leg2.setStrDepArr(strDepArr2)
        self.leg2.setStrActiveOrDH(strActiveOrDH2)
        listProblems = self.correctByType()
        if listProblems:
            for strProblem in listProblems:
                printWarning(strProblem)
    def getListStrValues(self):
        listValues = self.getListValues()
        mapTranslateBool = {0 : 'false', 1 : 'true'}
        listValues[gIxACChange] = mapTranslateBool[listValues[gIxACChange]]
        listValues[gIxActive] = mapTranslateBool[listValues[gIxActive]]
        return map(lambda s: str(s), listValues)
    def correctGeneral(self):
        """Returns a list of strings with descriptions on things that could not be automatically corrected.
        If no problems, an empty list is returned."""
        listStrProblems = []
        if not gReSLCarrier.match(self.getStrCarrier1()):
            listStrProblems.append('Leg 1 carrier must hold a 2 to 3 letter uppercase string (not "%s")' %(self.getStrCarrier1()))
        if self.getStrActiveOrDH1() not in ['A', 'D', '*']:
            self.setStrActiveOrDH1('*')
        if (not gReSLCarrier.match(self.getStrCarrier2()) and
            (self.slType.getStrCxnOrRest() == 'CXN' and (self.getIntFlightNr2() or self.getStrDepArr2())
             or self.getStrCarrier2())):
            listStrProblems.append('Leg 2 carrier must hold a 2 to 3 letter uppercase string (not "%s")' %(self.getStrCarrier2()))
        if self.getStrActiveOrDH2() not in ['A', 'D', '*']:
            self.setStrActiveOrDH2('*')
        if not self.getStrLimitMin():
            self.setStrLimitMin(gStrStdLimit)
        if not self.getStrLimitMax():
            self.setStrLimitMax(gStrStdLimit)
        if not self.getStrDateFrom():
            self.setStrDateFrom(gStrStdDateFrom)
        if not self.getStrDateTo():
            self.setStrDateTo(gStrStdDateTo)
        return listStrProblems
    def correctByType(self):
        """Corrects the SoftLock according to its Type
        Returns a list of strings with descriptions on things that could not be automatically corrected.
        If no problems, an empty list is returned."""
        listStrProblems = self.correctGeneral()
        if self.slType.getStrType() == 'CXN_BUFFER':
            self.setStrActiveOrDH1('*')
            self.setStrTrafficDay('')
            self.setBoolACChange(0)
            self.setStrBase('')
            self.leg2 = SoftLockLeg(self, gTypeLeg2)
        elif self.slType.getStrLockType() in ['TRIPSTART', 'TRIPEND', 'DUTYSTART', 'DUTYEND', 'BASE']:
            self.setBoolACChange(0)
            self.setStrLimitMin(gStrStdLimit)
            self.setStrLimitMax(gStrStdLimit)
            self.leg2 = SoftLockLeg(self, gTypeLeg2)
        elif self.slType.getStrType() in ['REQ_REST_BEF', 'REQ_REST_AFT']:
            self.setBoolACChange(0)
            self.leg2 = SoftLockLeg(self, gTypeLeg2)
        return listStrProblems
    def getStrType(self):
        return self.slType.getStrType()
    def setStrType(self, strType):
        if strType != None:
            strTypeUpper = strType.upper()
            strCheckType = self.checkStrType(strTypeUpper)
            if strCheckType:
                raise Exception(strCheckType)
            self.slType = SoftLockType(strTypeUpper)
    def checkStrType(self, strType, strName='SoftLock type'):
        if strType not in gListTypes:
            return '%s "%s" does not exist' %(strName, strType)
        return ''
    checkStrType = classmethod(checkStrType)
    def getStrCarrier1(self):
        return self.leg1.getStrCarrier()
    def setStrCarrier1(self, strCarrier1):
        if strCarrier1 != None:
            strCarrier1Upper = strCarrier1.upper()
            strCheckCarrier = self.checkStrCarrier(strCarrier1Upper)
            if strCheckCarrier:
                raise Exception(strCheckCarrier)
            self.leg1.setStrCarrier(strCarrier1Upper)
    def checkStrCarrier(self, strCarrier, strName='Carrier'):
        if strCarrier and not gReSLCarrier.match(strCarrier):
            return '%s "%s" does not hold a 2 to 3 letter string' %(strName, strCarrier)
        return ''
    checkStrCarrier = classmethod(checkStrCarrier)
    def getStrFlightNr1(self):
        return self.leg1.getStrFlightNr()
    def getIntFlightNr1(self):
        return self.leg1.getIntFlightNr()
    def setIntFlightNr1(self, intFlightNr1):
        if intFlightNr1 != None:
            try:
                intFlightNr1Fixed = int(intFlightNr1)
            except ValueError:
                intFlightNr1Fixed = 0
            strCheckFlightNr = self.checkIntFlightNr(intFlightNr1Fixed)
            if strCheckFlightNr:
                raise Exception(strCheckFlightNr)
            self.leg1.setIntFlightNr(intFlightNr1Fixed)
    def checkIntFlightNr(self, intFlightNr, strName='Flight number'):
        try:
            intTest = int(intFlightNr)
            if intTest < 0 or intTest > 999999:
                return '%s "%s" must be a number from 1 to 999999' %(strName, intFlightNr)
        except ValueError:
            return '%s "%s" must be a number' %(strName, intFlightNr)
        return ''
    checkIntFlightNr = classmethod(checkIntFlightNr)
    def checkIntNonNeg(self, intFlightNr, strName=''):
        strNameFixed = ''
        if strName:
            strNameFixed += strName + ' '
        try:
            intTest = int(intFlightNr)
            if intTest < 0:
                return '%s"%s" must be a non-negative number' %(strNameFixed, intFlightNr)
        except ValueError:
            return '%s"%s" must be a number' %(strNameFixed, intFlightNr)
        return ''
    checkIntNonNeg = classmethod(checkIntNonNeg)
    def getStrDepArr1(self):
        return self.leg1.getStrDepArr()
    def setStrDepArr1(self, strDepArr1):
        if strDepArr1 != None:
            strDepArr1Upper = strDepArr1.upper()
            strCheckDepArr = self.checkStrDepArr(strDepArr1Upper)
            if strCheckDepArr:
                raise Exception(strCheckDepArr)
            self.leg1.setStrDepArr(strDepArr1Upper)
    def checkStrDepArr(self, strDepArr, strName='Dep-Arr'):
        if strDepArr and not gReSLDepArr.match(strDepArr):
            return '%s "%s" does not match the format "LHR-JFK"' %(strName, strDepArr)
        return ''
    checkStrDepArr = classmethod(checkStrDepArr)
    def getStrActiveOrDH1(self):
        return self.leg1.getStrActiveOrDH()
    def setStrActiveOrDH1(self, strActiveOrDH1):
        if strActiveOrDH1 != None:
            strActiveOrDH1Upper = strActiveOrDH1.upper()
            if strActiveOrDH1Upper == '':
                strActiveOrDH1Upper = '*'
            strCheckActiveOrDH = self.checkStrActiveOrDH(strActiveOrDH1Upper)
            if strCheckActiveOrDH:
                raise Exception(strCheckActiveOrDH)
            self.leg1.setStrActiveOrDH(strActiveOrDH1Upper)
    def checkStrActiveOrDH(self, strActiveOrDH, strName='Active or DH'):
        if strActiveOrDH not in ['A', 'D', '*']:
            return '%s "%s" is neither "A", "D" or "*"' %(strName, strActiveOrDH)
        return ''
    checkStrActiveOrDH = classmethod(checkStrActiveOrDH)
    def getStrTrafficDay(self):
        return self.leg1.getStrTrafficDay()
    def setStrTrafficDay(self, strTrafficDay):
        if strTrafficDay != None:
            strTrafficDayUpper = strTrafficDay.upper()
            strCheckTrafficDay = self.checkStrTrafficDay(strTrafficDayUpper)
            if strCheckTrafficDay:
                raise Exception(strCheckTrafficDay)
            self.leg1.setStrTrafficDay(strTrafficDayUpper)
    def checkStrTrafficDay(self, strTrafficDay, strName='Traffic day'):
        if strTrafficDay and not gReSLTrafficDay.match(strTrafficDay):
            return '%s "%s" does not match the format "D12345" or "DX67"' %(strName, strTrafficDay)
        return ''
    checkStrTrafficDay = classmethod(checkStrTrafficDay)
    def getStrDateFrom(self):
        return self.leg1.getStrDateFrom()
    def getIntDateFrom(self):
        absTimeFrom = Abstime(self.getStrDateFrom())
        return int(absTimeFrom)
    def setStrDateFrom(self, strDateFrom):
        if not strDateFrom:
            strDateFrom = gStrStdDateFrom
        strDateFromUpper = strDateFrom.upper()
        strCheckDate = self.checkStrDate(strDateFromUpper)
        if strCheckDate:
            raise Exception(strCheckDate)
        self.leg1.setStrDateFrom(strDateFromUpper)
    def getStrDateTo(self):
        return self.leg1.getStrDateTo()
    def getIntDateTo(self):
        absTimeTo = Abstime(self.getStrDateTo())
        return int(absTimeTo) + gIntOneDay
    def setStrDateTo(self, strDateTo):
        if not strDateTo:
            strDateTo = gStrStdDateTo
        strDateToUpper = strDateTo.upper()
        strCheckDate = self.checkStrDate(strDateToUpper)
        if strCheckDate:
            raise Exception(strCheckDate)
        self.leg1.setStrDateTo(strDateToUpper)
    def checkStrDate(self, strDate, strName='Date'):
        if not gReSLDate.match(strDate):
            return '%s "%s" does not match format "05JAN1999"' %(strName, strDate)
        return ''
    checkStrDate = classmethod(checkStrDate)
    def getStrCarrier2(self):
        return self.leg2.getStrCarrier()
    def setStrCarrier2(self, strCarrier2):
        if strCarrier2 != None:
            strCarrier2Upper = strCarrier2.upper()
            strCheckCarrier = self.checkStrCarrier(strCarrier2Upper)
            if strCheckCarrier:
                raise Exception(strCheckCarrier)
            self.leg2.setStrCarrier(strCarrier2Upper)
    def getStrFlightNr2(self):
        return self.leg2.getStrFlightNr()
    def getIntFlightNr2(self):
        return self.leg2.getIntFlightNr()
    def setIntFlightNr2(self, intFlightNr2):
        if intFlightNr2 != None:
            try:
                intFlightNr2Fixed = int(intFlightNr2)
            except ValueError:
                intFlightNr2Fixed = 0
            strCheckFlightNr = self.checkIntFlightNr(intFlightNr2Fixed)
            if strCheckFlightNr:
                raise Exception(strCheckFlightNr)
            self.leg2.setIntFlightNr(intFlightNr2Fixed)
    def getStrDepArr2(self):
        return self.leg2.getStrDepArr()
    def setStrDepArr2(self, strDepArr2):
        if strDepArr2 != None:
            strDepArr2Upper = strDepArr2.upper()
            strCheckDepArr = self.checkStrDepArr(strDepArr2Upper)
            if strCheckDepArr:
                raise Exception(strCheckDepArr)
            self.leg2.setStrDepArr(strDepArr2Upper)
    def getStrActiveOrDH2(self):
        return self.leg2.getStrActiveOrDH()
    def setStrActiveOrDH2(self, strActiveOrDH2):
        if strActiveOrDH2 != None:
            strActiveOrDH2Upper = strActiveOrDH2.upper()
            strCheckActiveOrDH = self.checkStrActiveOrDH(strActiveOrDH2Upper)
            if strCheckActiveOrDH:
                raise Exception(strCheckActiveOrDH)
            self.leg2.setStrActiveOrDH(strActiveOrDH2Upper)
    def getStrLimitMin(self):
        return self.strLimitMin
    def setStrLimitMin(self, strLimitMin):
        if not strLimitMin:
            strLimitMin = gStrStdLimit
        strCheckLimitMin = self.checkStrLimit(strLimitMin)
        if strCheckLimitMin:
            raise Exception(strCheckLimitMin)
        self.strLimitMin = strLimitMin
    def checkStrLimit(self, strLimit, strName='Limit'):
        if not gReSLLimit.match(strLimit):
            return '%s "%s" does not match format "10:30"' %(strName, strLimit)
        return ''
    checkStrLimit = classmethod(checkStrLimit)
    def getStrLimitMax(self):
        return self.strLimitMax
    def setStrLimitMax(self, strLimitMax):
        if not strLimitMax:
            strLimitMax = gStrStdLimit
        strCheckLimitMax = self.checkStrLimit(strLimitMax)
        if strCheckLimitMax:
            raise Exception(strCheckLimitMax)
        self.strLimitMax = strLimitMax
    def getStrBase(self):
        return self.strBase
    def setStrBase(self, strBase):
        if strBase != None:
            strCheckBase = self.checkStrBase(strBase)
            if strCheckBase:
                raise Exception(strCheckBase)
            self.strBase = strBase
    def checkStrBase(self, strBase, strName='Base'):
        if strBase and not gReSLBase.match(strBase):
            return '%s "%s" does not hold a 1- to 5-letter string' %(strName, strBase)
        return ''
    checkStrBase = classmethod(checkStrBase)
    def getStrACType(self):
        return self.leg1.getStrACType()
    def setStrACType(self, strACType):
        self.leg1.setStrACType(strACType)
    def getBoolACChange(self):
        if self.boolACChange:
            return 1
        return 0
    def setBoolACChange(self, boolACChange):
        boolACChangeFixed = 0
        if str(boolACChange).upper().strip() in gListTrueStrUpper:
            boolACChangeFixed = 1
        self.boolACChange = boolACChangeFixed
    def getStrPenalty(self):
        return str(self.intPenalty)
    def getIntPenalty(self):
        return self.intPenalty
    def setIntPenalty(self, intPenalty):
        if intPenalty != None:
            strCheckPenalty = self.checkIntNonNeg(intPenalty)
            if strCheckPenalty:
                raise Exception(strCheckPenalty)
            self.intPenalty = intPenalty
    def getBoolActive(self):
        return self.boolActive
    def setBoolActive(self, boolActive):
        if boolActive == bool(boolActive):
            self.boolActive = boolActive
        else:
            boolActiveFixed = 0
            if str(boolActive).upper().strip() in gListTrueStrUpper:
                boolActiveFixed = 1
            self.boolActive = boolActiveFixed
    def getStrComment(self):
        return self.strComment
    def setStrComment(self, strComment):
        strCheckComment = self.checkStrComment(strComment)
        if strCheckComment:
            raise Exception(strCheckComment)
        self.strComment = strComment
    def checkStrComment(self, strComment, strName='Comment'):
        if not gReSLComment.match(strComment):
            return "%s '%s' contains characters not allowed in comments (\")" %(strName, strComment)
        return ''
    checkStrComment = classmethod(checkStrComment)
    def getTitle(self):
        return '%s %s' %(self.slType.getStrType(), self.leg1)
    def setIntUniqueId(self, intUniqueId):
        self.intUniqueId = intUniqueId
        if hasattr(self, 'parentEtab') and self.parentEtab:
            self.parentEtab.registerIntUniqueIdSL(intUniqueId)
    def getIntUniqueId(self):
        if not hasattr(self, 'intUniqueId'):
            return None
        return self.intUniqueId
    def getIntRowNum(self):
        parentEtab = self.getParentEtab()
        if parentEtab:
            return parentEtab.getIntSLRowNum(self.getIntUniqueId())
        return None
    def getLeg1(self):
        return self.leg1
    def getLeg2(self):
        return self.leg2
    def getStrDepArrFromList(self, listIxDay):
        # MMM Make sure only unique ix:s
        # Empty list may be considered an exception
        if not listIxDay or len(listIxDay) >= 7:
            return 'D'
        if len(listIxDay) > 4:
            strTrafficDay = 'DX'
            listInverseIxDay = []
            for ixDay in range(1, 8):
                if ixDay not in listIxDay:
                    strTrafficDay += str(ixDay)
        else:
            listIxDay.sort()
            strTrafficDay = 'D' + ''.join(map(lambda i: str(i), listIxDay))
        return strTrafficDay
    def getListDepArrFromStr(self, strDepArr):
        if not strDepArr:
            # May be considered an exception
            return []
        if strDepArr.strip() in ['D', 'd']:
            return [i for i in range(1, 8)]
        listIxDay = []
        for ixDay in range(1, 8):
            if (('X' in strDepArr or 'x' in strDepArr) and str(ixDay) not in strDepArr or
                not ('X' in strDepArr or 'x' in strDepArr) and str(ixDay) in strDepArr):
                listIxDay.append(ixDay)
        return listIxDay

class SoftLockLeg:
    def __init__(self, parentSL, legType, strCarrier='', intFlightNr=0, strDepArr='', strActiveOrDH='*',
                 strACType='', strTrafficDay='', strDateFrom='', strDateTo=''):
        self.parentSL = parentSL
        self.setLegType(legType)
        self.setStrCarrier(strCarrier)
        self.setIntFlightNr(intFlightNr)
        self.setStrDepArr(strDepArr)
        self.setStrActiveOrDH(strActiveOrDH)
        if self.legType == gTypeLeg1:
            self.setStrACType(strACType)
            self.setStrTrafficDay(strTrafficDay)
            self.setStrDateFrom(strDateFrom)
            self.setStrDateTo(strDateTo)
    def __repr__(self):
        return (self.getCustomRepr())['strRepr']
    def getCustomRepr(self, intFlightNrRPos=None, intTotalLen=None):
        strRepr = ''
        mapActiveOrDHRepr = {'D' : 'DH', '*' : '*'}
        intFlightNrRPosOut = intTotalLenOut = 0
        mapCarrierOccurences = self.parentSL.getParentEtab().getMapCarrierOccurences()
        if not mapCarrierOccurences or len(mapCarrierOccurences.keys()) != 1 or self.strCarrier != (mapCarrierOccurences.keys())[0]:
            strRepr += self.strCarrier
        if self.isComplete():
            if self.intFlightNr > 0:
                intTempRPos = len(strRepr) + len(str(self.intFlightNr))
                if intFlightNrRPos and intTempRPos > intFlightNrRPos:
                    intFlightNrRPosOut = intFlightNrRPos - intTempRPos
                    strRepr = strRepr[:intFlightNrRPos - len(str(self.intFlightNr))] + str(self.intFlightNr)
                else:
                    intFlightNrRPosOut = intTempRPos
                    if intFlightNrRPos:
                        strRepr += str(self.getStrFlightNr()).rjust(intFlightNrRPos - len(strRepr))
                    else:
                        strRepr += str(self.getStrFlightNr())
            if self.strDepArr:
                if strRepr:
                    strRepr += ' '
                intTempLPos = len(strRepr) + 1
                if intFlightNrRPos and intTempLPos > intFlightNrRPos + 2:
                    intFlightNrRPosOut = intFlightNrRPos + 2 - intTempLPos
                    strRepr = strRepr[:intFlightNrRPos] + ' ' + self.strDepArr
                else:
                    intFlightNrRPosOut = intTempLPos - 2
                    if intFlightNrRPos:
                        strRepr += self.strDepArr.rjust(intFlightNrRPos - len(strRepr) + 1 + len(self.strDepArr))
                    else:
                        strRepr += self.strDepArr
            if self.strActiveOrDH in mapActiveOrDHRepr.keys():
                strRepr += ' %s' %(mapActiveOrDHRepr[self.strActiveOrDH])
            if self.legType == gTypeLeg1:
                if self.strACType:
                    strRepr += ' %s' %(self.strACType)
                if self.strTrafficDay and self.strTrafficDay not in ['D', 'd', '1234567']:
                    strRepr += ' %s' %(self.strTrafficDay)
                if self.strDateFrom and self.parentSL.parentEtab.strDateIsInPeriod(self.strDateFrom):
                    strRepr += ' %s-' %(self.strDateFrom[:5])
                elif self.strDateTo and self.parentSL.parentEtab.strDateIsInPeriod(self.strDateTo):
                    strRepr += ' -'
                if self.strDateTo and self.parentSL.parentEtab.strDateIsInPeriod(self.strDateTo):
                    strRepr += self.strDateTo[:5]
            if intTotalLen and len(strRepr) > intTotalLen:
                intTotalLenOut = intTotalLen - len(strRepr)
                strRepr = strRepr[:intTotalLen]
            else:
                # No space-padding at the end
                intTotalLenOut = len(strRepr)
            return {'strRepr' : strRepr, 'intFlightNrRPos' : intFlightNrRPosOut,
                    'intTotalLen' : intTotalLenOut}
        return {'strRepr' : '<INCOMPLETE LEG>', 'intFlightNrRPos' : 0, 'intTotalLen' : 0}
    def isComplete(self):
        return self.strCarrier and (self.intFlightNr or self.strDepArr)
    def getLegType(self):
        return self.legType
    def setLegType(self, legType):
        self.legType = legType
    def getStrCarrier(self):
        return self.strCarrier
    def setStrCarrier(self, strCarrier):
        self.strCarrier = strCarrier
    def getIntFlightNr(self):
        return self.intFlightNr
    def getStrFlightNr(self):
        return getStrFlightNr(self.intFlightNr)
    def setIntFlightNr(self, intFlightNr):
        self.intFlightNr = int(intFlightNr)
    def getStrDepArr(self):
        return self.strDepArr
    def setStrDepArr(self, strDepArr):
        self.strDepArr = strDepArr.upper()
    def getStrActiveOrDH(self):
        return self.strActiveOrDH
    def setStrActiveOrDH(self, strActiveOrDH):
        self.strActiveOrDH = strActiveOrDH
    def getStrACType(self):
        return self.strACType
    def setStrACType(self, strACType):
        self.strACType = strACType
    def getStrTrafficDay(self):
        return self.strTrafficDay
    def setStrTrafficDay(self, strTrafficDay):
        self.strTrafficDay = strTrafficDay
    def getStrDateFrom(self):
        return self.strDateFrom
    def setStrDateFrom(self, strDateFrom):
        self.strDateFrom = strDateFrom
    def getStrDateTo(self):
        return self.strDateTo
    def setStrDateTo(self, strDateTo):
        self.strDateTo = strDateTo

class SoftLockType:
    def __init__(self, strType):
        self.strType = strType
        self.strLockType = ''
        self.reqOrNot = ''
        self.tripOrDuty = ''
        self.startOrEnd = ''
        self.cxnOrRest = ''
        self.aftOrBef = ''
        matchSoftLockReqNot = gReSoftLockReqNotType.match(strType)
        if matchSoftLockReqNot:
            self.reqOrNot = matchSoftLockReqNot.group('reqOrNot')
            self.strLockType = matchSoftLockReqNot.group('lockType')
            matchStartEnd = gReStartEndLock.match(self.strLockType)
            if matchStartEnd:
                self.tripOrDuty = matchStartEnd.group('tripOrDuty')
                self.startOrEnd = matchStartEnd.group('startOrEnd')
            else:
                matchCxnRest = gReCxnRestLock.match(self.strLockType)
                if matchCxnRest:
                    self.cxnOrRest = matchCxnRest.group('cxnOrRest')
                    self.aftOrBef = matchCxnRest.group('aftOrBef')
        elif strType == 'CXN_BUFFER':
            self.strLockType = 'CXN_BUFFER'
        else:
            raise Exception('SoftLockType "%s" did not match' %(strType))
    def __repr__(self):
        return self.getStrType()
    def getStrType(self):
        return self.strType
    def getStrLockType(self):
        return self.strLockType
    def getStrReqOrNot(self):
        return self.reqOrNot
    def getStrStartOrEnd(self):
        return self.startOrEnd
    def getStrTripOrDuty(self):
        return self.tripOrDuty
    def getStrCxnOrRest(self):
        return self.cxnOrRest
    def getStrAftOrBef(self):
        return self.aftOrBef

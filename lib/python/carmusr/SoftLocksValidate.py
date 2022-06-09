#!/usr/local/bin/python
#

#
# Script which validates a SoftLock using subplan data
#
# Created 2003-09-01 /Henrik
#

from SoftLocksBasics import *
import sys, os, re, string, time, shutil

############################## --------------------- ##############################
##############################  global declarations  ##############################
############################## --------------------- ##############################

gReCarrier = re.compile(r'^[A-Z0-9][A-Z]$|^[A-Z][A-Z][A-Z]$|^[A-Z][A-Z0-9]$')

# MMM Check ActiveOrDH unset value in Rave code
# Done, should be '*', never '', but why??
gMapUnset = {
    'FlightNr1'   : [0, '0'],
    'DepArr1'     : [''],
    'ActiveOrDH1' : ['', '*'],
    'TrafficDay'  : [''],
    'Carrier2'    : [''],
    'FlightNr2'   : [0, '0'],
    'DepArr2'     : [''],
    'ActiveOrDH2' : ['', '*'],
    'LimitMin'    : ['0:00', '00:00'],
    'LimitMax'    : ['0:00', '00:00', '999:00'],
    'ACChange'    : [0, 'FALSE', 'F', 'NO', 'N'],
    'Base'        : [''],
    'ACType'      : [''],
    'Comment'     : ['']
    }

############################## --------------------- ##############################
##############################      functions        ##############################
############################## --------------------- ##############################

# read a file into a buffer and return the buffer
def readFile(filename):
    f = open(filename)
    buffer = map(lambda line: line.replace(os.linesep, ''), f.readlines())
    f.close()
    return buffer

def report(strReport, listReturn, ixRow=None):
    if ixRow:
        listReturn.append('Row %d: %s' %(ixRow + 1, strReport))
    else:
        listReturn.append(strReport)

def isSet(strColName, value):
    return not strColName in gMapUnset.keys() or not value in gMapUnset[strColName]

def matchesTrafficDay(strTrafficDay, charActualTrafficDay):
    if strTrafficDay.upper() in ['', 'D']:
        return 1
    if strTrafficDay.upper().find('X') > -1:
        return strTrafficDay.find(charActualTrafficDay) == -1
    else:
        return strTrafficDay.find(charActualTrafficDay) > -1

# Example leg:
# 0   1    2   3   4  5    6
# LH,3642,FRA,VIE,737,4,7501905
def leg1Exist(softLock, listLegs):
    # (strCarrier, strFlightNr, strDepArr, strACType, strTrafficDay, timeMin, timeMax) = aRow[1:8]
    # strACType = aRow[15]
    if not (isSet('FlightNr1', softLock.getIntFlightNr1()) or isSet('DepArr1', softLock.getStrDepArr1())):
        return 0
    for aLeg in listLegs:
        if softLock.getStrCarrier1() == aLeg[0] and (not isSet('FlightNr1', softLock.getIntFlightNr1()) or softLock.getIntFlightNr1() == int(aLeg[1])) and (not isSet('DepArr1', softLock.getStrDepArr1()) or softLock.getStrDepArr1() == '%s-%s' %(aLeg[2], aLeg[3])) and (not isSet('ACType', softLock.getStrACType()) or softLock.getStrACType() == aLeg[4]) and (not isSet('TrafficDay', softLock.getStrTrafficDay()) or matchesTrafficDay(softLock.getStrTrafficDay(), aLeg[5])) and int(aLeg[6]) >= softLock.getIntDateFrom() and int(aLeg[6]) <= softLock.getIntDateTo():
            return 1
    return 0

def leg2Exist(softLock, listLegs):
    # (strCarrier, strFlightNr, strDepArr) = aRow[8:11]
    if not (isSet('FlightNr2', softLock.getIntFlightNr2()) or isSet('DepArr2', softLock.getStrDepArr2())):
        return 0
    for aLeg in listLegs:
        if softLock.getStrCarrier2() == aLeg[0] and (not isSet('FlightNr2', softLock.getIntFlightNr2()) or softLock.getIntFlightNr2() == int(aLeg[1])) and (not isSet('DepArr2', softLock.getStrDepArr2()) or softLock.getStrDepArr2() == '%s-%s' %(aLeg[2], aLeg[3])):
            return 1
    return 0

def validateSetUnset(softLock, listSet, listUnset, listAny):
    listToReport = []
    for colSet in listSet:
        if not isSet(colSet, softLock.getByTypeName(colSet)):
            listToReport.append('%s should be set for type %s' %(colSet, softLock.getStrType()))
    for colUnset in listUnset:
        if isSet(colUnset, softLock.getByTypeName(colUnset)):
            listToReport.append('%s should not be set for type %s' %(colUnset, softLock.getStrType()))
    if len(listAny) > 1:
        boolAny = 0
        for colAny in listAny:
            if isSet(colAny, softLock.getByTypeName(colAny)):
                boolAny = 1
        if not boolAny:
            listToReport.append('At least one of %s and %s should be set for type %s' %(', '.join(listAny[:-1]), listAny[-1], softLock.getStrType()))
    return listToReport

def validateEtab(slEtab, strReportFileName):
    tupData = getTupDataFromReport(strReportFileName)
    mapSL = slEtab.getMapSoftLocks()
    listReturn = ['The following problems were found in SoftLocks etable "%s":' %(slEtab.getName()), '']
    for slId in mapSL.keys():
        # listEtabRowsToUpper.append(aRow[:16] + listEtabRows[ixRow][16:])
        softLock = SoftLock(aRow)
        listReturn += apply(validateSoftLock, [softLock] + tupData)
    if len(listReturn) == 2:
        listReturn = ['No problems found in SoftLocks etable "%s"' %(strFilename)]
    else:
        listReturn += ['', 'Consult the SoftLocks manual to find the unset value of a column etc.']
##    if listEtabRowsToUpper != listEtabRows:
##        listReturn += ['', 'The etab was re-written with some entries converted to upper-case.']
##        etabToWrite = (listEtabCols, listEtabRowsToUpper, strFirstComment, strFilename)
##        writeEtab(SOFTLOCK_ETAB, etabToWrite)
    return listReturn
        
def validateSoftLockFromReport(softLock, strReportFileName):
    tupData = getTupDataFromReport(strReportFileName)
    listReturn = apply(validateSoftLock, [softLock] + tupData)
    return listReturn
    
def validateSoftLock(softLock, listLegs, listAllACTypes, listAllAirports, listAllBases, listDates, timeMin, timeMax):
    listReturn = []
    ixRow = softLock.getIntRowNum()
    if not ixRow:
        ixRow = 0
    if isSet('Base', softLock.getStrBase()) and not softLock.getStrBase() in listAllBases:
        report('Base "%s" does not exist in plan' %(softLock.getStrBase()), listReturn, ixRow)
    if isSet('ACType', softLock.getStrACType()) and not softLock.getStrACType() in listAllACTypes:
        report('ACType "%s" does not exist in plan' %(softLock.getStrACType()), listReturn, ixRow)
    matchCarrier1 = gReCarrier.match(softLock.getStrCarrier1())
    if not matchCarrier1:
        report('Carrier1 must hold a 2- to 3-letter string ("%s" found)' %(softLock.getStrCarrier1()), listReturn, ixRow)
    if not (isSet('FlightNr1', softLock.getStrFlightNr1()) or isSet('DepArr1', softLock.getStrDepArr1())):
        report('None of FlightNr1 or DepArr1 set', listReturn, ixRow)
    if not softLock.getStrActiveOrDH1() in ['A', 'D', '*']:
        report('ActiveOrDH1 must be set to one of "A", "D" or "*"', listReturn, ixRow)
    if softLock.getStrActiveOrDH1() in ['A', '*']:
        if not leg1Exist(softLock, listLegs):
            report('Leg 1: %s does not exist in plan' %(str(softLock.getLeg1())), listReturn, ixRow)
    # MMM Fix this, should not look in report (listDates)!!!
    if softLock.getIntDateFrom() > softLock.getIntDateTo():
        report('Date interval %s to %s goes backward in time' %(softLock.getStrDateFrom(), softLock.getStrDateTo()), listReturn, ixRow)
    elif softLock.getIntDateFrom() == softLock.getIntDateTo():
        report('Date interval %s to %s has zero length' %(softLock.getStrDateFrom(), softLock.getStrDateTo()), listReturn, ixRow)
    elif softLock.getIntDateFrom() > timeMax or softLock.getIntDateTo() < timeMin:
        report('Date interval %s to %s does not overlap plan period' %(softLock.getStrDateFrom(), softLock.getStrDateTo()), listReturn, ixRow)
    strType = softLock.getStrType()
    if not strType in gListTypes:
        report('SoftLock type "%s" does not exist' %(strType), listReturn, ixRow)
    else:
        listToReport = []
        if strType.find('BASE') > -1:
            listToReport = validateSetUnset(softLock, ['Base'], ['FlightNr2', 'DepArr2', 'ActiveOrDH2', 'LimitMin', 'LimitMax', 'ACChange'], [])
        elif strType.find('TRIP') > -1 or strType.find('DUTY') > -1:
            listToReport = validateSetUnset(softLock, [], ['FlightNr2', 'DepArr2', 'ActiveOrDH2', 'LimitMin', 'LimitMax', 'ACChange'], [])
        elif strType.find('_CXN') > -1:
            listToReport = validateSetUnset(softLock, [], [], ['FlightNr2', 'DepArr2', 'LimitMin', 'LimitMax'])
            if not softLock.getStrActiveOrDH2() in ['A', 'D', '*']:
                report('ActiveOrDH2 must be set to one of "A", "D" or "*" for type %s' %(strType), listReturn, ixRow)
            if isSet('FlightNr2', softLock.getStrFlightNr2()) or isSet('DepArr2', softLock.getStrDepArr2()):
                matchCarrier2 = gReCarrier.match(softLock.getStrCarrier2())
                if not matchCarrier2:
                    report('Carrier2 must hold a 2- to 3-letter string ("%s" found)' %(softLock.getStrCarrier2()), listReturn, ixRow)
                else:
                    matchDepArr1 = gReSLDepArr.match(softLock.getStrDepArr1())
                    if matchDepArr1:
                        matchDepArr2 = gReSLDepArr.match(softLock.getStrDepArr2())
                        if matchDepArr2:
                            if matchDepArr1.group('arr') != matchDepArr2.group('dep'):
                                report('Leg 1 arrival "%s" does not match leg 2 departure "%s"' %(matchDepArr1.group('arr'), matchDepArr2.group('dep')), listReturn, ixRow)
                if softLock.getStrActiveOrDH2() in ['A', '*']:
                    if not leg2Exist(softLock, listLegs):
                        report('Leg 2: %s does not exist in plan' %(softLock.getLeg2()), listReturn, ixRow)
        elif strType.find('REST') > -1:
            listToReport = validateSetUnset(softLock, [], ['FlightNr2', 'DepArr2', 'ActiveOrDH2', 'ACChange'], ['LimitMin', 'LimitMax'])
        elif strType == 'CXN_BUFFER':
            listToReport = validateSetUnset(softLock, [], ['ActiveOrDH1', 'TrafficDay', 'ACType', 'Base', 'FlightNr2', 'DepArr2', 'ActiveOrDH2', 'ACChange'], ['LimitMin', 'LimitMax'])
        for aReportLine in listToReport:
            report(aReportLine, listReturn, ixRow)
    return listReturn

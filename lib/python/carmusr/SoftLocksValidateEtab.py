#!/opt/Carmen/carm_util/bin/python
#!/usr/local/bin/python
#

#
# Script which validates a SoftLock etable
#
# Created 2003-09-01 /Henrik
#

import sys, os, re, string, time, shutil

############################## --------------------- ##############################
##############################  global declarations  ##############################
############################## --------------------- ##############################

gStrSeparator = ','

gStrUniqueTag = '==>>'

gReComment = re.compile(r'/\*.*?\*/', re.DOTALL)

gReNumber = re.compile(r'^\s*(?P<nr>\d+)\s*$')

#gReEtabColSpec = re.compile(r'^(?P<type>[SIARBCE])(?P<name>\w+)(?P<colspec>(\s.*|\s*)),\s*$')
gReEtabColSpec = re.compile(r'^(?P<type>[SIARBCE])(?P<name>\w+)(\s(?P<colspec>.*)|\s*),\s*$')

gReEtabClosingBrackets = re.compile(r'^[^\[]*(\[[^\]]*\].*$|)$')

gReEtabRow = re.compile(r'^\s*[^\,].*,\s*$')

gReEtabString = re.compile(r'^"(?P<string>.*)"$')

gReEtabSplit = re.compile(r'\s*(".*?")\s*,\s*|\s*,\s*')

gReEtabFirstComment = re.compile(r'^\s*/\*(?P<firstComment>.*?)(\*/|%s)' % (gStrUniqueTag), re.DOTALL)

gReCarrier = re.compile(r'^[A-Z]{2,3}$')

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

#"NOT_BASE", "LH", 3558, "", "A", "D", 01JAN1999, 01JAN2030, "BA", 0, "", "A", 0:00, 999:00, "FRA", "", false, 3500, true, "",
gMapUnset = {
    'FlightNr1'   : [0, '0'],
    'DepArr1'     : [''],
    'ActiveOrDH1' : ['', '*'],
    'TrafficDay'  : [''],
    'Carrier2'    : [''],
    'FlightNr2'   : [0, '0'],
    'DepArr2'     : [''],
    'ActiveOrDH2' : ['*'],
    'LimitMin'    : ['0:00', '00:00'],
    'LimitMax'    : ['0:00', '00:00', '999:00'],
    'ACChange'    : ['FALSE'],
    'Base'        : [''],
    'ACType'      : [''],
    'Comment'     : ['']
    }

#    0        1     2    3    4    5      6          7        8    9  10  11    12     13     14    15   16     17    18   19
#"NOT_BASE", "LH", 3558, "", "A", "D", 01JAN1999, 01JAN2030, "BA", 0, "", "A", 0:00, 999:00, "FRA", "", false, 3500, true, "",
gMapEtabIx = {
    'Type'        : 0,
    'Carrier1'    : 1,
    'FlightNr1'   : 2,
    'DepArr1'     : 3,
    'ActiveOrDH1' : 4,
    'TrafficDay'  : 5,
    'DateFrom'    : 6,
    'DateTo'      : 7,
    'Carrier2'    : 8,
    'FlightNr2'   : 9,
    'DepArr2'     : 10,
    'ActiveOrDH2' : 11,
    'LimitMin'    : 12,
    'LimitMax'    : 13,
    'Base'        : 14,
    'ACType'      : 15,
    'ACChange'    : 16,
    'Penalty'     : 17,
    'Active'      : 18,
    'Comment'     : 19
    }


############################## --------------------- ##############################
##############################      functions        ##############################
############################## --------------------- ##############################


# print usage
def usage():
    print '\n   Usage: %s -validate soft_lock_etab validation_report' %(os.path.basename(sys.argv[0]))
    print """
   This is a validation script for SoftLock etables
   """

# read a file into a buffer and return the buffer
def readFile(filename):
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
    print '  *** Warning: %s' %(strWarning)

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
                matchNr = gReNumber.match(outputRows[ixRow][ixCol])
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
    (allRows, strFirstComment) = unComment(allRowsWithComments)
    if len(allRows) == 0:
        printWarning('The file "%s" is empty' %(filename))
        return None
    ixRow = 0
    while not gReNumber.match(allRows[ixRow]):
        ixRow += 1
        if ixRow >= len(allRows):
            printWarning('The file "%s" has syntax errors (number of columns)' %(filename))
            return None
    intEtabCols = string.atoi(gReNumber.match(allRows[ixRow]).group('nr'))
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

def report(strReport, listReturn, ixRow):
    listReturn.append('Row %d: %s' %(ixRow + 1, strReport))

def isSet(strColName, value):
    return not strColName in gMapUnset.keys() or not value in gMapUnset[strColName]

def matchesTrafficDay(strTrafficDay, charActualTrafficDay):
    if strTrafficDay.upper() in ['', 'D']:
        return 1
    if strTrafficDay.upper().find('X') > -1:
        return strTrafficDay.find(charActualTrafficDay) == -1
    else:
        return strTrafficDay.find(charActualTrafficDay) > -1

# 0   1    2   3   4  5    6
# LH,3642,FRA,VIE,737,4,7501905
def leg1Exist(aRow, listLegs, datesFromTo):
    (strCarrier, strFlightNr, strDepArr, strACType, strTrafficDay, timeMin, timeMax) = aRow[1:8]
    strACType = aRow[15]
    if not (isSet('FlightNr1', strFlightNr) or isSet('DepArr1', strDepArr)):
        return 0
    for aLeg in listLegs:
        if strCarrier == aLeg[0] and (not isSet('FlightNr1', strFlightNr) or strFlightNr == aLeg[1]) and (not isSet('DepArr1', strDepArr) or strDepArr == '%s-%s' %(aLeg[2], aLeg[3])) and (not isSet('ACType', strACType) or strACType == aLeg[4]) and (not isSet('TrafficDay', strTrafficDay) or matchesTrafficDay(strTrafficDay, aLeg[5])) and int(aLeg[6]) >= datesFromTo[0] and int(aLeg[6]) <= datesFromTo[1]:
            return 1
    return 0

def leg2Exist(aRow, listLegs, datesFromTo):
    (strCarrier, strFlightNr, strDepArr) = aRow[8:11]
    if not (isSet('FlightNr1', strFlightNr) or isSet('DepArr1', strDepArr)):
        return 0
    for aLeg in listLegs:
        if strCarrier == aLeg[0] and (not isSet('FlightNr2', strFlightNr) or strFlightNr == aLeg[1]) and (not isSet('DepArr2', strDepArr) or strDepArr == '%s-%s' %(aLeg[2], aLeg[3])):
            return 1
    return 0

def getLeg1Repr(aRow):
    strRepr = '%s' %(aRow[1])
    if isSet('FlightNr1', aRow[2]):
        strRepr += '%s' %(aRow[2])
    if isSet('DepArr1', aRow[3]):
        strRepr += ' %s' %(aRow[3])
    if isSet('ACType', aRow[15]):
        strRepr += ' %s' %(aRow[15])
    if isSet('TrafficDay', aRow[5]):
        strRepr += ' %s' %(aRow[5])
    strRepr += ' %s - %s' %(aRow[6], aRow[7])
    return strRepr

def getLeg2Repr(aRow):
    strRepr = '%s' %(aRow[8])
    if isSet('FlightNr1', aRow[9]):
        strRepr += '%s' %(aRow[9])
    if isSet('DepArr1', aRow[10]):
        strRepr += ' %s' %(aRow[10])
    return strRepr

def validateSetUnset(aRow, listSet, listUnset, listAny):
    listToReport = []
    for colSet in listSet:
        if not isSet(colSet, aRow[gMapEtabIx[colSet]]):
            listToReport.append('%s should be set for type %s' %(colSet, aRow[0]))
    for colUnset in listUnset:
        if isSet(colUnset, aRow[gMapEtabIx[colUnset]]):
            listToReport.append('%s should not be set for type %s' %(colUnset, aRow[0]))
    if len(listAny) > 1:
        boolAny = 0
        for colAny in listAny:
            if isSet(colAny, aRow[gMapEtabIx[colAny]]):
                boolAny = 1
        if not boolAny:
            listToReport.append('At least one of %s and %s should be set for type %s' %(', '.join(listAny[:-1]), listAny[-1], aRow[0]))
    return listToReport

#    0        1     2    3    4    5      6          7        8    9  10  11    12     13     14    15   16     17    18   19
#"NOT_BASE", "LH", 3558, "", "A", "D", 01JAN1999, 01JAN2030, "BA", 0, "", "A", 0:00, 999:00, "FRA", "", false, 3500, true, "",
def validateEtab(SOFTLOCK_ETAB, listLegs, listDates, timeMin, timeMax):
    (listEtabCols, listEtabRows, strFirstComment, strFilename) = readEtab(SOFTLOCK_ETAB)
    listReturn = ['The following problems were found in SoftLocks etable "%s":' %(strFilename), '']
    listEtabRowsToUpper = []
    listAllACTypes = getAllACTypes(listLegs)
    listAllAirports = getAllAirports(listLegs)
    listAllBases = getAllBases(listLegs)    
    for ixRow in range(len(listEtabRows)):
        aRow = map(lambda s: s.upper(), listEtabRows[ixRow])
        listEtabRowsToUpper.append(aRow[:16] + listEtabRows[ixRow][16:])
        (strType, strCarrier1, strFlightNr1, strDepArr1, strActOrDH1, strTrafficDay, dateFrom, dateTo, strCarrier2, strFlightNr2, strDepArr2, strActOrDH2, limitMin, limitMax, strBase, strACType, strOnlyIfACChg, strPenalty, strActive, strComment) = aRow
        if isSet('Base', strBase) and not strBase in listAllBases:
            report('Base "%s" does not exist in plan' %(strBase), listReturn, ixRow)
        if isSet('ACType', strACType) and not strACType in listAllACTypes:
            report('ACType "%s" does not exist in plan' %(strACType), listReturn, ixRow)
        matchCarrier1 = gReCarrier.match(strCarrier1)
        if not matchCarrier1:
            report('Carrier1 must hold a 2- to 3-letter string ("%s" found)' %(strCarrier1), listReturn, ixRow)
        if not (isSet('FlightNr1', strFlightNr1) or isSet('DepArr1', strDepArr1)):
            report('None of FlightNr1 or DepArr1 set', listReturn, ixRow)
        if not strActOrDH1 in ['A', 'D', '*']:
            report('ActiveOrDH1 must be set to one of "A", "D" or "*"', listReturn, ixRow)
        if strActOrDH1 in ['A', '*']:
            if not leg1Exist(aRow, listLegs, listDates[ixRow]):
                report('Leg 1: %s does not exist in plan' %(getLeg1Repr(aRow)), listReturn, ixRow)
        if listDates[ixRow][0] > listDates[ixRow][1]:
            report('Date interval %s to %s goes backward in time' %(dateFrom, dateTo), listReturn, ixRow)
        elif listDates[ixRow][0] == listDates[ixRow][1]:
            report('Date interval %s to %s has zero length' %(dateFrom, dateTo), listReturn, ixRow)
        elif listDates[ixRow][0] > timeMax or listDates[ixRow][1] < timeMin:
            report('Date interval %s to %s does not overlap plan period' %(dateFrom, dateTo), listReturn, ixRow)
        if not strType in gListTypes:
            report('SoftLock type "%s" does not exist' %(strType), listReturn, ixRow)
        else:
            listToReport = []
            if strType.find('BASE') > -1:
                listToReport = validateSetUnset(aRow, ['Base'], ['FlightNr2', 'DepArr2', 'ActiveOrDH2', 'LimitMin', 'LimitMax', 'ACChange'], [])
            elif strType.find('TRIP') > -1 or strType.find('DUTY') > -1:
                listToReport = validateSetUnset(aRow, [], ['FlightNr2', 'DepArr2', 'ActiveOrDH2', 'LimitMin', 'LimitMax', 'ACChange'], [])
            elif strType.find('_CXN') > -1:
                listToReport = validateSetUnset(aRow, [], [], ['FlightNr2', 'DepArr2', 'LimitMin', 'LimitMax'])
                if not strActOrDH2 in ['A', 'D', '*']:
                    report('ActiveOrDH2 must be set to one of "A", "D" or "*" for type %s' %(aRow[0]), listReturn, ixRow)
                if isSet('FlightNr2', strFlightNr2) or isSet('DepArr2', strDepArr2):
                    matchCarrier2 = gReCarrier.match(strCarrier2)
                    if not matchCarrier2:
                        report('Carrier2 must hold a 2- to 3-letter string ("%s" found)' %(strCarrier2), listReturn, ixRow)
                    if strActOrDH2 in ['A', '*']:
                        if not leg2Exist(aRow, listLegs, listDates[ixRow]):
                            report('Leg 2: %s does not exist in plan' %(getLeg2Repr(aRow)), listReturn, ixRow)
            elif strType.find('REST') > -1:
                listToReport = validateSetUnset(aRow, [], ['FlightNr2', 'DepArr2', 'ActiveOrDH2', 'ACChange'], ['LimitMin', 'LimitMax'])
            elif strType == 'CXN_BUFFER':
                listToReport = validateSetUnset(aRow, [], ['ActiveOrDH1', 'TrafficDay', 'ACType', 'Base', 'FlightNr2', 'DepArr2', 'ActiveOrDH2', 'ACChange'], ['LimitMin', 'LimitMax'])
            for aReportLine in listToReport:
                report(aReportLine, listReturn, ixRow)
    if len(listReturn) == 2:
        listReturn = ['No problems found in SoftLocks etable "%s"' %(strFilename)]
    else:
        listReturn += ['', 'Consult the SoftLocks manual to find the unset value of a column etc.']
    if listEtabRowsToUpper != listEtabRows:
        listReturn += ['', 'The etab was re-written with some entries converted to upper-case.']
        etabToWrite = (listEtabCols, listEtabRowsToUpper, strFirstComment, strFilename)
        writeEtab(SOFTLOCK_ETAB, etabToWrite)
    return listReturn

############################## --------------------- ##############################
############################## execution starts here ##############################
############################## --------------------- ##############################

if __name__== "__main__":
    
    # check command line arguments
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)
    
    FLAG = sys.argv[1]
    
    if FLAG == '-validate':
        if len(sys.argv) < 4:
            usage()
            sys.exit(1)
        (SOFTLOCK_ETAB, VALIDATION_REPORT) = sys.argv[2:4]
        listReport = map(lambda line: line.split(gStrSeparator), readFile(VALIDATION_REPORT))
        if len(listReport) == 0 or not listReport[0]:
            raise('Report "crg/hidden/SoftLocksValidation.output" empty. There must be trips in the window!')
        (timeMin, timeMax) = map(lambda s: int(s), listReport[0])
        listDates = []
        ixLine = 2
        aLine = listReport[ixLine]
        while len(aLine) > 1:
            listDates.append(map(lambda s: int(s), aLine))
            ixLine += 1
            aLine = listReport[ixLine]
        listLegs = listReport[ixLine + 1:]
        listResult = validateEtab(SOFTLOCK_ETAB, listLegs, listDates, timeMin, timeMax)
        print os.linesep.join(listResult)
    
    else:
        usage()
        sys.exit(1)

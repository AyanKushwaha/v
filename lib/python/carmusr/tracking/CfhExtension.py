
#
# Purpose: Contains functionality which is reoccurring for tracking cfh forms
#

import re

import Cfh
import modelserver as M
import Airport
from RelTime import RelTime
from AbsTime import AbsTime
from AbsDate import AbsDate
import Cui

def getPlanningGroupSet():
    """
    Returns a correctly formatted string containing all the available
    planning groups. The string is ended with a '*'
    """

    # Load the necessary table
    tm = M.TableManager.instance()
    tm.loadTables(["planning_group_set"])
    planning_group_set = tm.table("planning_group_set")

    planning_groups = []
    for row in planning_group_set:
        # Do not add doublets
        if not row.id in planning_groups:
            planning_groups.append(row.id)
        #end if
    #end for
    
    # The forms needs the options to be ";" seperated
    planning_groups = [planning_group + ";" for planning_group in planning_groups]

    # The ";" before the "*" has already been added.
    return ("Planning Groups;" + "".join(planning_groups) + "*")

def getHomeBaseSet():
    """
    Returns a correctly formatted string containing all the available
    home-bases the string is ended with a '*'
    """

    # Load the necessary table
    tm = M.TableManager.instance()
    tm.loadTables(["crew_base_set"])
    base_set = tm.table("crew_base_set")
    
    bases = []
    for row in base_set:
        # Do not add doublets
        if not row.id in bases:
            bases.append(row.id)
        #end if
    #end for
    
    # The forms needs the options to be ";" seperated.
    bases = [base + ";" for base in bases]
    
    # The ";" before the "*" has already been added.
    return ("Homebases;" + "".join(bases) + "*")

def getActivityCodes():
    """
    Returns a correctly formatted string containing all the available
    activities as well as activity groups and activity categories the
    string is ended with a '*'
    """

    #adding activity ids:
    tm = M.TableManager.instance()
    tm.loadTables(["activity_set"])
    ac_set = tm.table("activity_set")
    
    acs = set()
    for row in ac_set:
        acs.add(row.id)
        #end if
    #end for
    
    #adding activity groups and categories
    tm = M.TableManager.instance()
    tm.loadTables(["activity_group"])
    ag_set = tm.table("activity_group")
    
    for row in ag_set:
        acs.add(row.id)
        #end if
    #end for
    
    #adding activity groups and categories
    tm = M.TableManager.instance()
    tm.loadTables(["activity_group"])
    acat_set = tm.table("activity_category")
    
    for row in acat_set:
        acs.add(row.id)
        #end if
    #end for
    
    # The forms needs the options to be ";" seperated.
    string = [ac + ";" for ac in acs]
    
    # The ";" before the "*" has already been added.
    return ("Activities;" + "".join(string) + "*")


def getRankSet():
    """
    Returns a correctly formatted string containing all the available
    ranks and all the available main categories. The string is started
    with the main categories, followed by the specific ranks, followed
    by a '*'
    """

    tm = M.TableManager.instance()
    tm.loadTables(["crew_rank_set"])
    rank_set = tm.table("crew_rank_set")
    
    # The forms needs the options to be ";" seperated.
    dictCat = {}
    for row in rank_set:
        dictCat.setdefault(row.id[0], [row.id[0] + "*;"]).append(row.id + ";")
        
    rankList = []
    for cat in dictCat.keys():
        dictCat[cat].sort()
        rankList.extend(dictCat[cat])
        
    return ("Ranks;" + "".join(rankList) + "*")

def getAcQualSet():
    """
    Returns a correctly formatted cfh-MenuString containing all the available
    Air Craft qualifications. The string is started with a ';' to prevent the
    drop-down from having a label. The string is ended with a '*'
    """
    return getQual("ACQUAL")

def getAirportQualSet():
    """
    Returns a correctly formatted cfh-MenuString containing all the available
    Airport qualifications. The string is started with a ';' to prevent the
    drop-down from having a label. The string is ended with a '*'
    """
    return getQual("AIRPORT")

def getInstructorQualSet():
    """
    Returns a tuple consisting of a correctly formatted cfh-MenuString
    containing all the available Instructor qualification descriptions (short
    version) and a dictionary which translates the descriptions to the
    corresponding sub-type. The string is at position 0 in the tuple and the
    dictionary at position 1. The return value from the form can be used as a
    key in the dictionary.
    """
    return getQual("INSTRUCTOR")

def getQual(type):
    """
    Returns the necessary cfh-MenuString information depending on which
    qualification type is desired. See the wrapper functions for more
    information.
    """
    tm = M.TableManager.instance()
    tm.loadTables(["crew_qualification_set"])

    qualification_set = tm.table("crew_qualification_set")

    qual = []
    dict = {}
    for row in qualification_set.search("(typ=%s)" % type):
        # Find out what the drop-down should show.
        if type == "INSTRUCTOR":
            info = row.descshort
            dict[info] = row.subtype
        else:
            info = row.subtype
        # Add the information to the to-be menu-string. Do not add doublets.
        if not info in qual:
            # Add a ";" to provide the correct Cfh syntax
            qual.append(info + ";")
        #end if
    #end for

    # Return the correctly formatted information depending on type of
    # qualification. Add type as the label and end with a "*".
    if type == "INSTRUCTOR":
        dict["*"] = "*"
        return (type + ";" + "".join(qual) + "*", dict)
    else:
        return type + ";" + "".join(qual) + "*"

def getCrewQualSet():
    """
    Returns the necessary cfh-MenuString information about
    crew qualification. When evaluating input selected out of this
    string, some caution must be taken, as it does not always
    show what type of qualification it is.
    """
    tm = M.TableManager.instance()
    tm.loadTables(["crew_qualification_set"])

    qualification_set = tm.table("crew_qualification_set")

    retString = "Crew Qualification;" 
    curType = ""
    for row in qualification_set:
        # Find out what the drop-down should show.
        if not (row.typ == "ACQUAL" or row.typ == "AIRPORT"):
            if row.typ != curType:
                retString += ";;ALL " + row.typ
                curType = row.typ
            retString += ";" + row.subtype
        #end if
    #end for

    return retString + ";*"

class RestrictedString(Cfh.String):
    """
    This class provides a string field with value restrictions.
    
    Input are allowed to be separated by the characters listed in 'separators'.
    Each element in the input list is validated against a list of valid values.
    
    'menuString' is a ';'-separated list of valid names.
    
    If not None, characters in 'wildcards' are allowed in elements, and
      a leading '!' is allowed in each element (to ber interpreted as "not").
      Elements containing wildcard characters are not validated.
    As a special case, if 'wildcards' is an empty string, '!"' will be allowed
      even though there are no wildcard characters.
    """

    def __init__(self, box, name, maxLength,
                 initial_value= -1, menuString="", separator=",", wildcards=None):
        Cfh.String.__init__(self, box, name, maxLength, initial_value)
        
        # Convert the search criterias to a list
        self.menu_list = menuString.lower().split(";")
        
        # Regular expression to convert input string to element list
        self.re_separator = re.compile(r"\s*[%s]+\s*" % (separator or "$NOSEP$"))
        
        if wildcards is not None:
            self.wildcards = set(wildcards)
        else:
            self.wildcards = None

    def check(self, text):
        checkString = Cfh.String.check(self, text)
        if checkString:
            return checkString
        elif not self.menu_list or not self.menu_list[0]:
            return None
        else:
            # The search may contain one or more of the "menuString" options.

            for element in self.re_separator.split(text):
                if self.wildcards is not None:
                    element = element.lstrip("!").lstrip()
                if not element:
                    # The element is empty and thus not a valid search
                    return 'Search may not contain empty criterias'
                elif self.wildcards and (self.wildcards & set(element)):
                    pass
                elif not element.lower() in self.menu_list:
                    return "Not a valid input: " + element + "."
            return None

class RelTimeField(Cfh.String):
    """
    This class provides a field for input of a time in the
    format [-][HHHHH]H:MM. Managed values are only strings.
    assign() and valof() take and return strings,
    respectively. Changing valof() to return a reltime
    seemed to give strange errors.
    Empty string is also allowed as the input.
    """

    def __init__(self, box, name, maxLength, initial_value_str=None,
                 allow_negative=True, allow_hours_more_than_23=True):
        Cfh.String.__init__(self, box, name, maxLength, initial_value_str)
        self.allow_hours_more_than_23 = allow_hours_more_than_23
        self.allow_negative = allow_negative
        
    def check(self, text):
        """
            Tests if text represents a valid RelTime.
            Minutes are maximum 59.
        """
        errorMess = "Invalid time given. Format: " + \
                (self.allow_negative and "[-]" or "") + "[HHHHH]H:MM."
        if len(text) < 4:
            return errorMess
        if text[0] == "-" and len(text) > 10:
            return errorMess
        if text[0] != "-" and len(text) > 9:
            return errorMess
        if text[-3] != ":":
            return errorMess
        try:
            int(text[-2:])
        except:
            return errorMess + " Minutes not a number."
        if int(text[-2:]) > 59:
            return errorMess + " Minutes out of bounds."
        try:
            int(text[:-3])
        except:
            return errorMess + " Hours not a number."
        try:
            value = RelTime(text)
        except Exception, msg:
            return errorMess

        #the following are extra. Not needed for valid reltime.

        if not self.allow_hours_more_than_23 and \
                (int(text[:-3]) > 23 or int(text[:-3]) < -23):
            return errorMess + " Hours cannot be more than 23."
        if not self.allow_negative and int(text[:-3]) < 0:
            return errorMess + " Hours cannot be less than 0."

        return None

class CustomNumber(Cfh.String):
    """
    This class provides a field for input of an integer.
    Managed values are only strings. assign() and valof()
    take and return strings,
    respectively. Changing valof() to return a reltime
    seemed to give strange errors.
    Empty string is also allowed as the input.
    """

    def __init__(self, box, name, maxLength, initial_value_str=None,
            strictly_positive=False, minimum_value=None, maximum_value=None):
        Cfh.String.__init__(self, box, name, maxLength, initial_value_str)
        self.strictly_positive = strictly_positive
        self.minimum_value = minimum_value
        self.maximum_value = maximum_value
        
    def check(self, text):
        try:
            value = int(text)
        except Exception, msg:
            return "Invalid number given. Only integers are allowed."
        if self.strictly_positive and int(text) < 1:
            return "Invalid number given. Only strictly positive integers are allowed."
        if self.minimum_value != None and int(text) < self.minimum_value:
            return "Invalid number given. Input can be minimum " + \
                    str(self.minimum_value) + "."
        if self.maximum_value != None and int(text) > self.maximum_value:
            return "Invalid number given. Input can be maximum " + \
                    str(self.maximum_value) + "."
        return None

class AirportString(Cfh.String):
    def __init__(self, box, name, maxLength, initial_value= -1):
        Cfh.String.__init__(self, box, name, maxLength, initial_value)
        
    def check(self, text):
        if text == "*":
            return None
        else:
            airport = Airport.Airport(text)
            if not airport.isAirport():
                return "%s is not a valid airport" % text
            else:
                return
        
class AirportStringList(Cfh.String):
    # Accepts and verifies contents of a string. It must contain airport codes,
    # if more than 1, they must be separated by ",".
    def __init__(self, box, name, maxLength, initial_value= -1):
        Cfh.String.__init__(self, box, name, maxLength, initial_value)
        
    def check(self, text):
        if text == "*":
            return None
        else:
            
            text1 = text.replace("+", ",")
            list = text1.split(",")
        
            # Remove any " " in the beginning or end of each criteria. Then
            # make sure that each element in the list is a valid search
            # criteria
            for element in list:
                try: 
                    if element[0] == " ":
                        element = element[1:]
                    if element[-1] == " ":
                        element = element[:-1]
                    # if the element is now empty
                    element[0]
                except IndexError:
                    # The element is empty and thus not a valid search
                    return "Search may not contain empty criterias nor may " + \
                           'it end with ","'

                airport = Airport.Airport(element)
                if not airport.isAirport():
                    return "%s is not a valid airport" % element
            return
        
class CrewQualInfo(Cfh.String):
    # Get information related to the Crew qualifications, to be used in pull down menus
    def __init__(self, box, name, maxLength=40, initial_value= -1):
        Cfh.String.__init__(self, box, name, maxLength, initial_value)
        
        tm = M.TableManager.instance()
        tm.loadTables(["crew_qualification_set", "crew_qual_acqual_set"])    
        self.qualification_set = tm.table("crew_qualification_set")
        self.qual_acqual_set = tm.table("crew_qual_acqual_set")
        self.retString = name
        self.crewQualInfoDict = {}
        self.crewQualInfo = self.getCrewQualDict()
        
    def getCrewQualDict(self):
        for row in self.qualification_set:
            # Identify crew qualifications:
            if not (row.typ == "ACQUAL" or row.typ == "AIRPORT"):
                [listSubtypes, listShortDesc, listLongDesc] = \
                    self.crewQualInfoDict.setdefault(row.typ, [[], [], []])
                listSubtypes.append(row.subtype)
                listShortDesc.append(row.descshort)
                listLongDesc.append(row.desclong)
                self.crewQualInfoDict[row.typ] = [listSubtypes, listShortDesc, listLongDesc]
                
        for row in self.qual_acqual_set:
            # Identify crew qual acqual:
            if row.typ == "INSTRUCTOR":
                [listSubtypes, listShortDesc, listLongDesc] = \
                    self.crewQualInfoDict.setdefault(row.typ, [[], [], []])
                index = -1
                if row.subtype in listSubtypes:
                    index = listSubtypes.index(row.subtype)
                # Only allow unique values [subtype, descshort, desclong]
                if index == -1 or (listShortDesc[index] != row.descshort and listLongDesc[index] != row.desclong):
                    listSubtypes.append(row.subtype)
                    listShortDesc.append(row.descshort)
                    listLongDesc.append(row.desclong)
                self.crewQualInfoDict[row.typ] = [listSubtypes, listShortDesc, listLongDesc]
        return
    
    def getCrewQualTypesForSubType(self, subtype):
        
        retType = ""
        for types in self.crewQualInfoDict.keys():
            for values in self.crewQualInfoDict[types][0]:
                if values == subtype:
                    if retType != "":
                        print 'CfhExtension.py:: Two equal subtypes in table NOT allowed!', subtype
                        break
                    retType = types
        if retType == "":
            print 'CfhExtension.py:: Subtype not defined in table: ', subtype
        return retType
    
    def getCrewQualSubTypesList(self, maintype):
        """
        Returns a list of sub-types for the type specified as 'maintype'.
        """
        return self.crewQualInfoDict[maintype][0]

    def getCrewQualMenuString(self, subtype=""):
        
        menuString = self.retString + ";"
        valString = ""
        for mainType in self.crewQualInfoDict.keys():
            # Find out what the drop-down should show.
            valString += ";".join(self.crewQualInfoDict[mainType][0]) + ";"
            menuString += "  ;ALL " + mainType + ";"
            for idx, value in enumerate(self.crewQualInfoDict[mainType][0]):
                menuString += ("%-6s" % value) + " (" + \
                    (self.crewQualInfoDict[mainType][2][idx] or "").replace(",", "/") + ");"
        menuString += "  ;*"
        valString = valString + ";" + menuString.replace("  ;", "")
        return (menuString, valString)

    
class SpecialDate(Cfh.Date):
    def __init__(self, box, name, time=None):
        
        now = AbsTime(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, "None", "fundamental.%now%"))
        if time is None:
            time = now
            
        super(SpecialDate, self).__init__(box, name, time)
        yyyymmdd = now.yyyymmdd()
        self.year = int(yyyymmdd[:4])
        self.month = int(yyyymmdd[4:6])
        self.date = int(yyyymmdd[6:8])

        from re import compile
        self.day_month_pattern = compile("^[0-9]{2}[a-zA-Z]{3}$") # match {DAY}{MONTH}

    def check(self, text):
        if len(text) <= 2: #Only date
            day = int(text)
            self.assign(AbsDate(self.year, self.month, day))
        elif self.day_month_pattern.match(text):
            from time import strptime
            t = strptime(text, '%d%b')
            self.assign(AbsDate(self.year, t.tm_mon, t.tm_mday))

        super(SpecialDate, self).check(text)

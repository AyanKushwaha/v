#! /usr/bin/env python
# This Python file uses the following encoding: latin-1
#######################################################

#
# -----------------------------------------------------
#
#   This is the customization of the commandline interface
#   which can be found in the tracking gui. In this module
#   new commands can be created and existing modified.
#
#   This module will be used by the CARMSYS commandline
#   module.
#
# ------------------------------------------------------
# Created:    July 2005
# By:         Carmen Systems AB
#
#######################################################

import re
import Cui
import Errlog
import AbsTime
import RelTime
import carmensystems.rave.api as R
from carmstd.parameters import parameter, getCurrentRuleSet
import carmstd.rave as rave
import carmstd.area
from commandline.CommandLine import register, unregister
import carmusr.tracking.DateAndTime as DateAndTime
import carmusr.HelperFunctions as HF
import carmusr.application as application
import traceback
import operator
from tm import TM

# A select function making new selection at the top of the window.
# The function can only handle rave evaluations or pure ids (crr_crew_id,
# leg_identifier or crr_identifier). Pure ids needs to be given as a tuple
# with an id-identifier as the first object and a list of id:s as the second.
def select(selections, area, mode, method="REPLACE", sort="TRUE", date=False, datestring="01Jan1986 00:00"):
    Errlog.log("SELECTION with: selections=%s, area=%s, mode=%s, method=%s, sort=%s, date=%s, datestring=%s" %(str(selections), str(area), str(mode), method, sort, str(date), datestring))
    if not method:
        method = "REPLACE"
    # If selection is of the type tuple it should contain a list of identifiers.
    list_identifiers = False
    if type(selections) == type(tuple()):
        list_identifiers = True
        ids = selections[-1]
        if mode == "t":
            getChains = Cui.CuiGetTrips
        # Temporarily "l" is used as ac-rotation mode.
        elif mode == "l":
            getChains = Cui.CuiGetLegs
        else:
            getChains = Cui.CuiGetCrew
    else:
        chain_sel = []
        leg_sel = []
        for sel in selections:
            if len(sel) == 2:
                (v,s) = sel
                r_var = R.var(sel[0])
                lev = str(r_var.level()).split(".")[-1]
                if lev != "chain":
                    lev = "leg"
            else:
                (l,v,s) = sel
                lev = {"C":"chain", "R":"chain", "L":"leg"}.get(l.upper(), l.lower())
            if lev == "chain": chain_sel.append(v+s)
            elif lev == "leg": leg_sel.append(v+s)
        where_c = "false"
        if chain_sel:
            where_c = " and ".join(chain_sel)
        where_l = "false"
        if leg_sel:
            where_l = " and ".join(leg_sel)
        Errlog.log("COMMANDLINE: chain selection: " + where_c)
        Errlog.log("COMMANDLINE: leg selection:   " + where_l)
        if mode == "t":
            context = "sp_crrs"
            keyword_id = "crr_identifier"
            chain_iterator = "iterators.trip_set"
            getChains = Cui.CuiGetTrips
        # Temporarily "l" is used as ac-rotation mode.
        elif mode == "l":
            context = "ac_rotations"
            keyword_id = "leg_identifier"
            getChains = Cui.CuiGetLegs
        else:
            context = "sp_crew"
            keyword_id = "crr_crew_id"
            chain_iterator = "iterators.roster_set"
            getChains = Cui.CuiGetCrew

        if method == "SUBSELECT":
            print "Subselect is being done"
            context = "default_context"
            Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "window")

        if chain_sel and leg_sel:
            #
            # In cases of 'chain' AND 'leg' selections, the defined 'sort_by' statements must be
            # properly located in the 'R.foreach' option in order to avoid inconsistent 'level'
            # computations!! BZ 39747 (WP FAT-CCT 491)
            #
            selected_ids, = R.eval(context,
                                   R.foreach(R.iter(chain_iterator,
                                                    where=where_c),
                                             R.foreach(R.iter('iterators.leg_set',
                                                              where=where_l, sort_by=sort),
                                                       'leg_identifier'),
                                             keyword_id))
            ids = [id for (nr, legid, id) in selected_ids if legid]
        elif chain_sel:
            selected_ids, = R.eval(context,
                                   R.foreach(R.iter(chain_iterator,
                                                    where=where_c, sort_by=sort),
                                             keyword_id))
            ids = [id for (nr, id) in selected_ids]
        elif leg_sel:
            ids=[]
            default_bag = R.context(context).bag()
            for leg_bag in default_bag.iterators.leg_set(where=where_l, sort_by=sort):
                ids.append(leg_bag.crr_crew_id())

    doSelect(method, area, mode, ids, getChains, datestring)

def doSelect(method, area, mode, ids, getChains, datestring):
    any_chains_in_window = 0
    win_ids = []
    if method in ("ADD", "SUBSELECT"):

        any_chains_in_window = Cui.CuiGetNumberOfChains(Cui.gpc_info, area)

        if set_mode(mode) == carmstd.area.getAreaMode(area) and \
                any_chains_in_window:

            win_ids = getChains(Cui.gpc_info, area, "window")

            if (method == "ADD") and any_chains_in_window:
                for id in ids:
                    if id in win_ids:
                        win_ids.remove(id)
                ids += win_ids
            elif (method == "SUBSELECT") and any_chains_in_window:
                ids_to_keep = []
                for id in ids:
                    if id in win_ids:
                        ids_to_keep.append(id)
                ids = ids_to_keep

    # Different treatment in type id mode for 'rotations' command.
    set_type = set_mode(mode)
    if set_type == Cui.AcRotMode:
        set_type = Cui.LegMode

    string_ids = map(str, ids)

    try:
        HF.get_specific_area(area)
        #
        # Avoid Studio crash possible due to illegal/not valid crr_identifiers when calling:
        # "CuiDisplayGivenObjects". (i.e. include a crr_crew_id in list of crr_identifiers).
        # One case can be when a list of identifiers come directly from the command line.
        # (i.e. a 't' (trip) show mode is used with a 'crew' command).
        #
        if mode == 't' and list_identifiers == True:
            carmstd.area.promptPush("    Bad command use.")
        else:
            if Cui.CuiDisplayGivenObjects({'WRAPPER':Cui.CUI_WRAPPER_NO_EXCEPTION},
                                          Cui.gpc_info, area, set_mode(mode),
                                          set_type, string_ids) != 0:
                carmstd.area.promptPush("    No result found.")
            if datestring:
                zoom_to_date(area, datestring)
            if method == "ADD" or method == "REPLACE":
                HF.redrawAreaScrollHome(area)
    except:
        traceback.print_exc()
        carmstd.area.promptPush("    No result found.")

# Functions making sure the international characters are handled correctly

internationalChars = {"å":"Å","ä":"Ä","æ":"Æ","â":"Â","é":"É","è":"È","ñ":"Ñ","ü":"Ü","ö":"Ö","ø":"Ø"}

def toUpper(txt):
    for (low, up) in internationalChars.items():
        try:
            txt = txt.replace(low,up)
        except AttributeError:
            return txt
    return txt.upper()

def toLower(txt):
    for (low, up) in internationalChars.items():
        try:
            txt = txt.replace(up,low)
        except AttributeError:
            return txt
    return txt.lower()

# Function for setting the mode to the correct value.
# The letters are predefined in the carmsys commandline module.

def set_mode(given_mode, default_mode=Cui.CrewMode):
    if given_mode == "r": return Cui.CrewMode
    if given_mode == "t": return Cui.CrrMode
    #if given_mode == "l": return Cui.LegMode
# Temporarily "l" is used as ac-rotation mode.
    if given_mode == "l": return Cui.AcRotMode
    if given_mode == Cui.CrewMode or given_mode == Cui.CrrMode or \
           given_mode == Cui.AcRotMode:
        return given_mode
    return default_mode

# Function for setting the correct selection value based on the given flag.
# "REPLACE" is default if no flag is given.
def init_vars(flags, area = Cui.CuiArea0, mode = "r"):
    selections = {"A":"ADD", "R":"REPLACE", "S":"SUBSELECT"}
    try: flags = flags.upper()
    except: flags = "R"
    s = (([f for f in map(selections.get, flags) if f])+["REPLACE"])[0]
    if "M" in flags:
        m = "LEG"
    return s

# Function for detecting if a rule set is loaded or not
def ruleset_loaded():
    try: getCurrentRuleSet()
    except:
        carmstd.area.promptPush("    No ruleset loaded. Selection cannot be made.")
        return False
    return True

def zoom_to_date(area, datestring):
    date = AbsTime.AbsTime(datestring)
    Cui.CuiZoomTo(Cui.gpc_info, area, date.getRep() - 60*24, date.getRep() + 60*48)

def show_rotations((area, mode), (rotation_info, date, flag)):
    """
    Select rotations. Arguments are an aircraft registration or aircraft owner and an optional date
    """
    Errlog.log("COMMANDLINE: Running show_rotations with AC_reg/owner=%s, date=%s, flag=%s" %
               (rotation_info, date, flag))

    #mode = 'l'

    if ruleset_loaded():

        datestring = validateDate(date, "0.0")
        if not datestring: return

        method = init_vars(flag)
        selection = [('leg.%is_flight_duty%',"")]
        selection.append(('leg.%start_date_utc%',"="+datestring))
        sorting='TRUE'
        if len(rotation_info.strip()) == 2:
            selection.append(('leg.%aircraft_owner%', '="%s"' %rotation_info.upper().strip()))
        else:
            selection.append(('leg.%ac_reg%', '="%s"' %rotation_info.upper().strip()))

        select(selection, area, mode, method, sorting, date=date, datestring=datestring)

def show_flights((area, mode), (flight_info, date, flag)):
    """
    Select flights. Arguments are one or several flight numbers or a departure and an arrival airport and an optional date
    """
    Errlog.log("COMMANDLINE: Running show_flights with flight_info=%s, date=%s, flag=%s in area %s with mode %s" %
               (str(flight_info), str(date), str(flag), str(area), str(mode)))
    if ruleset_loaded():

        datestring = validateDate(date, "0.0")
        if not datestring: return

        selection = []
        method = init_vars(flag)
        sorting='TRUE'
        sortfli = []
        listFli = []
        extra = ""
        if flight_info.replace(",","").replace(" ", "").isdigit():
            sort1 = ['studio_select.%sort_crew_at_show_rosters%',sorting]
            for flight_nr in flight_info.split(","):
                listFli.append('leg.%%show_flight_crew_has_id%%(%s,%s)'%(datestring,flight_nr))
                sortfli.append('studio_process.%%sort_flight_select_dep%%(%s,%s)'%(flight_nr, datestring))
            selList = '('+' or '.join(listFli)+')'
            selection.append(('L',selList,""))
            sortfli.extend(sort1)
            sorting = tuple(sortfli)
        else:
            if flight_info.upper().startswith("DH "):
                selection.append(('leg.%is_deadhead%',""))
                flight_info = flight_info[2:].strip()
            stations = flight_info.upper().split()
            if stations:
                selection.append(('leg.%start_station%', '="%s"' %stations[0]))
                selection.append(('leg.%end_station%', '="%s"' %stations[1]))
            selection.append(('leg.%start_date_utc%',"="+datestring[0:9]))

        select(selection, area, mode, method, sorting, date=date, datestring=datestring)

def show_db_flights((area, mode), (flight_info, date, flag)):
    """
    Select  flights (db). Arguments are one or several flight numbers or a departure and an arrival airport and an optional date
    """
    Errlog.log("COMMANDLINE: Running show_db_flights with flight_info=%s, date=%s, flag=%s in area %s with mode %s" %
               (str(flight_info), str(date), str(flag), str(area), str(mode)))

    if not flight_info.replace(",","").replace(" ", "").isdigit():
        show_flights((area, mode), (flight_info, date, flag))
        return

    datestring = validateDate(date, "0.0")
    if not datestring: return


    if ruleset_loaded() and HF.isDBPlan():
        date_fmt, = R.eval('format_time(%s, "%%Y%%02m%%02d")'%(datestring))
        print "db_sel",str(date_fmt)
        method = init_vars(flag)
        found_flights = []
        selection = []
        res = []

        flight_nr_length = 6
        if flight_info.replace(",","").replace(" ", "").isdigit():
            search = '(leg=%s*)' % (date_fmt)
            for row in TM.crew_flight_duty.search(search):
                res.append((row.leg, row.pos.id, row.crew.id))
            for flight_nr in flight_info.split(","):
                flight_nr=flight_nr.strip()
                diff = flight_nr_length - len(flight_nr)
                flight_fmt = ''.join((diff*'0',flight_nr))
                for item in res:
                    if flight_fmt in str(item[0]):
                        appended = False
                        pos, = R.eval('studio_select.%%rank_sort_order%%("%s")' % (item[1]))
                        for seniority_row in TM.crew_seniority.search('(&(crew=%s)(validfrom<=%s)(validto>=%s))' % (item[2],datestring,datestring)):
                            selection.append((pos,seniority_row.seniority,item[2]))
                            appended = True
                        if not appended:#No seniority. Crew is NEW?
                            selection.append((pos,99999,item[2]))
                for sel in sorted(selection, key=operator.itemgetter(0,1)):
                    found_flights.append(sel[2])

        doSelect(method, area, mode, found_flights, Cui.CuiGetCrew, date_fmt)

def show_crew((area, mode), (crew_id, date, flag)):
    """
    Select crew. Arguments are the initial part of the crew last-name or one or several crew-ids with an optional date
    """
    Errlog.log("COMMANDLINE: Running show_crew with crew_id=%s, date=%s, flag=%s" %(crew_id, date, flag))
    if ruleset_loaded():

        if not date:
            pp_st, = R.eval('fundamental.%now%')
            pp_start = str(pp_st).split(' ')[0]

            try:
                DateAndTime.get_search_time(pp_start, "0.0")
            except DateAndTime.DateRangeException:
                pp_start, = R.eval('studio_process.%pp_start_fmt%')

            datestring = validateDate(pp_start, "0.0")
        else:
            datestring = validateDate(date, "0.0")

        if not datestring: return

        crew_in_area = []
        method = init_vars(flag, area)
        selection = []
        if crew_id.replace(",","").replace(" ", "").isdigit():
            ids = []
            for emp_nr in crew_id.split(","):
                if date:
                    id, = R.eval('studio_process.%%crew_employnr_to_crew_id%%("%s", %s)' %
                                 (emp_nr.strip(), datestring))
                else:
                    id, = R.eval('studio_process.%%crew_employnr_to_crew_id_no_date%%("%s")' %
                                 (emp_nr.strip()))
                if id:
                    ids.append(id)
            selection = ('crr_crew_id', ids)
        else:
            name_selection = []
            for name in [toUpper(name.strip()) for name in crew_id.split(",")]:
                for name in (name, name[:1] + toLower(name[1:])):
                    name_selection.append('studio_process.%%crew_name_start_with%%("%s")' % name)
            selection.append(("chain", " or ".join(name_selection), ""))
        select(selection, area, mode, method, date=date, datestring=datestring)

def show_standby((area, mode), (date, flag)):
    """
    Select standby crew. Argument is an optional date
    """
    Errlog.log("COMMANDLINE: Running show_standby with date=%s, flag=%s" %(date, flag))
    if ruleset_loaded():

        datestring = validateDate(date, "0.0")
        if not datestring: return

        datestring = datestring[:9]
        # Init add/replace selections
        method = init_vars(flag, area)
        selection = []
        #selection.append(('leg.%start_date%', '='+datestring))
        #selection.append(("leg.%is_standby_or_blank%",""))
        selection_activity = 'studio_select.%%activity_code%%("A*,R*,H*,SB,SB1,SB2,T", %s 00:00, %s 23:59)' % \
                             (datestring, datestring)
        selection_blank = 'studio_select.%%blank_day%%(%s 00:00, %s 23:59)' % \
                          (datestring, datestring)
        #Remove the empty production days.
        #selection.append(("C",selection_activity + " or " + selection_blank , ""))
        selection.append(("C",selection_activity, ""))
        select(selection, area, mode, method, date=date, datestring=datestring)

def show_checkedin((area, mode), (qual, flag)):
    """
    Select checked in crew. Argument is an optional qualification
    """
    Errlog.log("COMMANDLINE: Running show_checkedin with qual=%s, flag=%s" %
               (qual, flag))
    date = False
    if ruleset_loaded():

        datestring = validateDate(date, "0.0")
        if not datestring: return

        method = init_vars(flag, area)
        selection = []
        selection.append(("studio_select.%crew_checked_in_not_departed%",""))

        if qual:
            selection.append(("C", 'studio_process.%%has_airport_or_aircraft_qln%%("%s")' %
                              qual.upper(), ""))
        sortby = ("checkinout.%leg_checkin_utc%", "leg.%flight_nr%")
        select(selection, area, set_mode(mode), method, datestring=datestring, sort=sortby)

def show_qualification((area, mode), (qual, rank, date, flag)):
    """
    Select qualified crew. Arguments are a qualification code and/or a rank and an optional date
    """
    Errlog.log("COMMANDLINE: Running show_qualification with qual=%s, rank=%s, flag=%s" %
               (qual, rank, flag))
    if ruleset_loaded():

        datestring = validateDate(date, "0.0")
        if not datestring: return

        selection = []
        method = init_vars(flag, area)
        if rank:
            selection.append(("C", 'studio_process.%%has_rank_at_date%%("%s",%s)' %
                              (rank.upper(), datestring), ''))
        if not rank and len(qual) == 2 and re.findall("(?i)%s" %crewR, qual):
            selection.append(("C", 'studio_process.%%has_rank_at_date%%("%s",%s)' %
                              (qual.upper(), datestring), ''))
        elif qual:
            selection.append(("C", 'studio_process.%%has_airport_or_aircraft_qln%%("%s")' %
                              qual.upper(), ""))
        select(selection, area, mode, method, date=date, datestring=datestring)

def show_airport((area, mode), (airport, time, date, flag)):
    """
    Select on-duty crew on specified airport. Arguments are an airport and an optional time and/or date
    """
    Errlog.log("COMMANDLINE: Running show_airport with airport=%s, time=%s, date=%s, flag=%s" %
               (airport, time, date, flag))
    if ruleset_loaded():

        datestring = validateDate(date, time.replace(":", "."))
        if not datestring: return

        selection = []
        method = init_vars(flag, area)
        use_time = ("FALSE", "TRUE")[bool(time) or not bool(date)]
        selection.append(("C", 'studio_process.%%is_on_airport_now%%("%s", %s, %s)' %
                          (airport.upper(), datestring, use_time),""))
        select(selection, area, mode, method, 'studio_process.%%sort_airport_select%%("%s", %s, %s)' %
               (airport.upper(), datestring, use_time), date=date, datestring=datestring)

def show_cancelation_candidates((area, mode), (airport, time, date, flag)):
    """
    Select crew living near specified airport. Arguments are an airport and an optional time and/or date
    """
    Errlog.log("COMMANDLINE: Running show_station with airport=%s, time=%s, date=%s, flag=%s" %
               (airport, time, date, flag))
    if ruleset_loaded():

        datestring = validateDate(date, time.replace(":", "."))
        if not datestring: return

        selection = []
        method = init_vars(flag, area)
        use_time = ("FALSE", "TRUE")[bool(time) or not bool(date)]
        selection.append(("C", 'studio_process.%%is_cancelation_flight_now%%("%s", %s, %s)' %
                          (airport.upper(), datestring, use_time),""))
        select(selection, area, mode, method, 'studio_process.%%sort_cancelation_flight_select%%("%s", %s, %s)' %
               (airport.upper(), datestring, use_time), date=date, datestring=datestring)

def show_annotation((area, mode), (anno_code, anno_text, date, flag)):
    """
    Select crew having specified annotation values. Arguments are an annotation code, an optional annotation text and an optional date
    """

    def isnull(a, b):
        return b if a is None else a

    Errlog.log("COMMANDLINE: Running show_annotation with anno_code=%s, anno_text=%s, date=%s, flag=%s" %
        (anno_code, anno_text, date, flag))
    if ruleset_loaded():
        datestring = validateDate(date, "0.0")
        if not datestring: return

        method = init_vars(flag, area)

        search = "(& (validfrom<=%s) (validto>=%s))" % (datestring, datestring)
        found_crews = []
        for row in TM.crew_annotations.search(search):
            if (anno_code.upper() == row.code.code.upper()) and ((anno_text == "") or (anno_text.upper() == isnull(row.text, "").upper())):
                found_crews.append(row.crew.id)
        select(("C", found_crews), area, mode, method, date=date, datestring=datestring)

def show_help(a, b):
    """
    Displays what commands that exists for the commandline.
    """
    carmstd.area.promptPush(
      " Commands: ai, c, f, d, i, q, s, r, ac, k, an. "
      "Help for a command type: command followed by '?'. (i.e: f ?)")

def validateDate(date, time):
    """
    Validate the strings entered as time and date.
    """
    try:
        datestring = DateAndTime.get_search_time(date, time)
    except DateAndTime.DateFormatException:
        carmstd.area.promptPush("    Given date/time does not exist.")
        return ""
    except DateAndTime.DateRangeException:
        carmstd.area.promptPush("    Given date is outside opened period.")
        return ""
    return datestring

flagR = r'(a|r|s|$)\s*$'
crewR = r'FC|FP|FR|AP|AS|AH|AA|FA|FE|FO|FS|FD|CC'
dateR = r'\d{1,2}(?:(?:(?i)%s)(?:\s*?|[0-9][0-9]|[1-2][0-9][0-9][0-9])|\s*?)' %("|".join(DateAndTime.monthList()))
timeR = r'\d{0,2}[.:]\d{2,2}'
surnameR = r"[A-Za-zåÅäÄæÆâÂéÉèÈñÑüÜöÖøØ']+"
empnrR = r'\d{2,8}'
nameOrNrR = r'(%s(?:,\s*%s)*|%s(?:\s*,\s*%s)*)' %(surnameR, surnameR, empnrR, empnrR)
flightNr = r'\d{3,4}'
manyFlgNr = r'%s(?:\s*,\s*%s)*' % (flightNr, flightNr)

annotationCodeR = r'[A-Za-z0-9_\-]{2}'
annotationTextR = r'.*'

if application.isTracking or application.isDayOfOps:
    flight_function = show_db_flights
else:
    flight_function = show_flights

# To enable the use of commands with either lower or upper case letters,
# each command is registered in both a lower case and an uppercase version
# The dict has values of the form commandname:(regexp, function to run)
com = {"flight"  : (r'\s*((?:%s)|(?:DH\s*|\s*)[A-Za-z]{3,3}\s+[A-Za-z]{3,3})(?:\s*|$)(%s|\s*?|$)(?:\s+|$)%s' % (manyFlgNr, dateR, flagR), flight_function),
       "crew"    : (r'\s*%s(?:\s*|$)(%s|\s*?|$)(?:\s+|$)%s' % (nameOrNrR, dateR, flagR), show_crew),
       "qual"    : (r'\s*(\w{2,3})(?:\s*|$)(\s*?|%s)(?:\s*|$)(%s|\s*?|$)(?:\s*|$)%s' % (crewR, dateR, flagR), show_qualification),
       "airport" : (r'\s*([A-Za-z]{3,3})(?:\s+|$)(%s|\s*|$)(?:\s*|$)(%s|\s*?|$)(?:\s*|$)%s' % (timeR, dateR, flagR), show_airport),
       "k"      : (r'\s*([A-Za-z]{3,3})(?:\s+|$)(%s|\s*|$)(?:\s*|$)(%s|\s*?|$)(?:\s*|$)%s' % (timeR, dateR, flagR), show_cancelation_candidates),
       "help"    : (r'\s*', show_help),
       "in"      : (r'\s*((?:\w{2,3})|^)(?:\s+|^|$)%s' % flagR, show_checkedin),
       "standby" : (r'\s*(%s|\s*?|^)(?:\s+|^|$)%s' % (dateR, flagR), show_standby),
       "?"       : (r'\s*', show_help),
       "acrotation": (r'\s*([A-Za-z]{5,5}|[0-9|A-Za-z]{1,1}[A-Za-z]{1,1}\s*)(?:\s*|$)(%s|\s*?|$)(?:\s+|$)%s' % (dateR, flagR), show_rotations),
       "annotation": (r'(?i)([\w\-]{2})(?:\s*|$)([a-zA-Z]{3}|$|\s*)(?:\s*|$)((?:\d{1,2})?(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)(?:(?:[1-2][0-9][0-9][0-9])|\d{2}|\s*?)|\s*?)|\s*?|$|\s*?|$)?\s*(a|r|s)?', show_annotation)
    }

for (command, (regexp, function)) in com.items():
    register(command, regexp, function)

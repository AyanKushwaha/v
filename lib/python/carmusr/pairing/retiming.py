'''
Holds most GUI functions for retiming.

Created on Feb 19, 2010 for OTS

@author: Mattias Nolander

Adjusted to Standard Style etc.
by Stefan Hammar in October - December 2010. 

Adjusted for SAS in March 2012 by Stefan Hammar

'''

if __name__ == "__main__":
    raise NotImplementedError, "Do not execute as script"

import os
import tempfile

import Cui, Gui
import Cfh
import carmensystems.mave.etab as etab
from AbsTime import AbsTime
import Errlog

from carmstd.etab_ext import expand_etab_path
from carmstd import bag_handler
from carmstd.retiming_basics import get_retiming_array
from carmstd.retiming_basics import ret_alt_value_to_tuple

REMOVE_RET = "REMOVE"
ADD_RET = "ADD"
REPLACE_RET = "REPLACE"


def get_tbh(scope="Marked"):
    """
    @param scope
    @type string
    """
    if scope.upper() == "OBJECT":
        tbh = bag_handler.CurrentLeg()
    elif scope.upper() == "MARKED":
        tbh = bag_handler.MarkedLegsMain()
    elif scope.upper() == "WINDOW":
        tbh = bag_handler.WindowChains()
    else:
        raise ValueError, "Unsupported scope - %s" % scope

    if tbh.warning:
        Gui.GuiMessage(tbh.warning)
    if not tbh.bag:
        return None     
    
    if not [None for lbag in tbh.bag.atom_set() if lbag.active_in_sp()]:
        Gui.GuiMessage("Error. You have only other fleet deadheads in the scope.")
        return 
    
    ndh = len([None for lbag in tbh.bag.atom_set() if not lbag.active_in_sp()])
    if ndh: 
        Errlog.log("%s: Ignoring %s marked other fleet deadhead(s)." % (__name__, ndh))   

    return tbh


def open_table():
    etable_real_path = get_active_retiming_path()
    
    # If the e-table doesn't exist. Create it.
    if not os.path.exists(etable_real_path):
        etab_obj = _create_empty_table(etable_real_path)
    else:
        # The e-table exist. Load it.
        session = etab.Session()
        etab_obj = etab.load(session,etable_real_path)
    
    etab_obj.addIndex(("carrier","flight_number",
                       "flight_suffix","departure_station",
                       "departure_date"))
    
    return etab_obj

# Menu entry:
def replace_retiming_alternatives_with_current(scope="marked"):
    """
    Replace any retiming alternatives in the specified scope, with the currently used
    retiming. If no retiming is used, all retiming alternatives will be removed for the leg.
    @param scope
    @type string
    """
    set_retiming_alternatives("Not used", REPLACE_RET, True, scope)
    
        
# Menu entry:    
def set_retiming_alternatives(retiming_alt=None, retiming_option=REPLACE_RET, 
                              use_actual_retiming_as_alternative=False, scope="marked"):  
    """
    If no retiming_alternatives are given, a GUI will ask the planner for a retiming string, 
    and if this retiming string should be added to, removed from or replace
    any already existing retiming string in the retiming e-table.
    It will perform the actions on legs in the specified scope. 
    
    Note. The current retiming setting on a leg is always kept as retiming alternative. 
    
    @param retiming_str: A string of the retiming alternatives. If None, ask the planner. (default = None) 
    @type retiming_str: string
    @param retiming_option: A string of ADD, REMOVE or REPLACE. (default = REPLACE)
    @type retiming_option: string
    @param use_actual_retiming_as_alternative: If True, the actual retiming on the leg is used instead of 
        retiming_alt. Default False.
    @type use_actual_retiming_as_alternative: Boolean
    @param scope
    @type string
    """
    
    tbh = get_tbh(scope)    
    if not tbh:
        return 
    print "******************************"
    # Show a GUI form and ask the planner for the retiming alternatives.
    if retiming_alt == None:
        if not set_retiming_alternative_gui[0]:
            set_retiming_alternative_gui[0] = Set_retiming_alternative_gui()
        dlg = set_retiming_alternative_gui[0]
        dlg.show(1)
        val = dlg.loop()
        if val != Cfh.CfhOk:
            return
        dict = dlg.get_value_dict()
        retiming_alt = dict["retiming_alternative"]
        retiming_option = dict["retiming_option"]

    # Update the e-table with the given retiming_alt
    etab_obj = open_table()
    for leg in tbh.bag.retiming.unique_leg_set(where="active_in_sp"):
        _update_etable_with_leg(leg, etab_obj, retiming_alt, retiming_option, 
                                use_actual_retiming_as_alternative)
        
    etab_obj.save()
    Cui.CuiCrcRefreshEtabs(os.path.dirname(get_active_retiming_path()))
    # Refresh the GUI
    Gui.GuiCallListener(Gui.RefreshListener, "parametersChanged")
    

def get_filter_string():
    """
    Returns the filter string used when searching in an e-table.
    
    @return: Returns filter string.
    @rtype: String
    """
    return "(&(carrier=%s)(flight_number=%s)(flight_suffix=%s)(departure_station=%s)(departure_date=%s))"


def _create_empty_table(etable_real_path):
    """
    Creates an empty retiming e-table according to the location given in 'etable_real_path'
    
    @param etable_real_path: Full path to the e-table that should be created.
    @type etable_real_path: string
    @return: A new empty e-table object
    @rtype: carmensystems.mave.core.ETable
    """
    
    # If the dirs doesn't exit, create them.
    if not os.path.exists(os.path.dirname(etable_real_path)):
        os.makedirs(os.path.dirname(etable_real_path))
    
    # Create the e-table.
    session = etab.Session()
    etab_comment = "\n".join(("e-table used to store retiming alternatives per leg.",
                              "Maintained by scripts"))    
    e = etab.create(session, etable_real_path, etab_comment)
    
    # Create the e-table header.
    e.appendColumn("carrier", str)
    e.appendColumn("flight_number", int)
    e.appendColumn("flight_suffix", str)
    e.appendColumn("departure_station", str)
    e.appendColumn("departure_date", AbsTime)
    e.appendColumn("retiming_alternative", str)
    
    return e


def get_list_of_leg_rows(etab_obj, leg, date=None):
    """
    Return a list of all found e-table rows for the given leg.
    
    @param etab_obj: The e-table which the new row should be added to.
    @type etab_obj: carmensystems.mave.core.ETable
    @param leg: The data in the row comes from the given leg.
    @type leg: bag
    @param date: The date used in the new row. If None, the start date of the leg is used.
    @type date: AbsTime
    @return: List of found rows.
    @rtype: list
    """
    filter = get_filter_string()
    etab_rows =  etab_obj.search(filter,
                                 leg.leg.flight_carrier(),
                                 leg.leg.flight_nr(),
                                 leg.leg.flight_suffix(),
                                 leg.leg.start_station(),
                                 (date or leg.leg.normalized_scheduled_start_date_utc()))
 
    return list(etab_rows)


def get_list_of_rows_of_legs(etab_obj, row):
    """
    Given a row, return a list of all equal rows in the e-table.
    
    @param etab_obj: The e-table which the new row should be added to.
    @type etab_obj: carmensystems.mave.core.ETable
    @param row: The data in the row comes from the given row.
    @type row: carmensystems.mave.core.Tuple
    @return: List of found rows.
    @rtype: list
    """
    filter = get_filter_string()
    etab_rows =  etab_obj.search(filter,
                                 row.carrier,
                                 row.flight_number,
                                 row.flight_suffix,
                                 row.departure_station,
                                 row.departure_date)

    return list(etab_rows)


def add_leg(etab_obj, leg, retiming_alt, date=None):
    """
    Given a leg, add a row to the e-table, with the given retiming alternative.
    If no date is given, use the legs start date.
    
    @param etab_obj: The e-table which the new row should be added to.
    @type etab_obj: carmensystems.mave.core.ETable
    @param leg: The data in the row comes from the given leg.
    @type leg: bag
    @param retiming_alt: A string of the retiming alternatives that should be used in the row.
    @type retiming_alt: String
    @param date: The date used in the new row. If None, the start date of the leg is used.
    @type date: AbsTime
    """
    etab_obj.append([leg.leg.flight_carrier(),
                    leg.leg.flight_nr(),
                    leg.leg.flight_suffix(),
                    leg.leg.start_station(),
                    date or leg.leg.normalized_scheduled_start_date_utc(),
                    retiming_alt])


def add_row_of_leg(etab_obj, row, retiming_alt=None):
    """
    Given a row, add it to the e-table, with the given retiming alternative.
    If no retiming alternative is given, use the rows retiming alternatives.
    
    @param etab_obj: The e-table which the new row should be added to.
    @type etab_obj: carmensystems.mave.core.ETable
    @param row: The data in the row comes from the given row.
    @type row: carmensystems.mave.core.Tuple
    @param retiming_alt: A string of the retiming alternatives that should be used in the row. If None
        is given, the retiming alternative of the given row is used.
    @type retiming_alt: String
    """
    etab_obj.append([row.carrier,
                     row.flight_number,
                     row.flight_suffix,
                     row.departure_station,
                     row.departure_date,
                     retiming_alt or row.retiming_alternative])

    
def _update_etable_with_leg(leg, etab_obj,retiming_alt, retiming_option, 
                            use_actual_retiming_as_alternative=False):
    """
    Update the e-table for a specific leg.
    
    @param leg: a bag with one leg.
    @type leg: bag
    @param etab_obj: The e-table object.
    @type etab_obj: carmensystems.mave.core.ETable
    @param retiming_alt: A string of the retiming alternatives given by planner. 
        The retiming alternatives are separated using a comma.
    @type retiming_alt: string
    @param retiming_option: A string of ADD, REMOVE or REPLACE.
    @type retiming_option: string
    @param use_actual_retiming_as_alternative: If True, the actual retiming on the leg is used instead of 
        retiming_alt
    @type use_actual_retiming_as_alternative: Boolean
    """
    retiming_alt = retiming_alt.strip()
                                        
    if use_actual_retiming_as_alternative:
        # We ignore the given retiming_alt, and replaces it with the actual
        # retiming on the leg. 
        retiming_alt = get_actual_retiming_on_leg(leg)
    else:
        # Current retiming should always be kept as one alternative.
        retiming_alt = ",".join([it for 
                                 it in (retiming_alt, get_actual_retiming_on_leg(leg))
                                 if it])
        
    # Get list of rows found by the given the leg.
    rows = get_list_of_leg_rows(etab_obj, leg)
    if len(rows) > 0:
        # The row already exists in the etab.
        # Update the existing row.
        manipulate_the_rows(rows, etab_obj, retiming_alt, retiming_option)
                
    else:
        # The leg doesn't exist in the e-table.
        # If retiming alternative exist, add them.
        new_retiming_string = get_new_retiming_string(retiming_option,retiming_alt)
        if new_retiming_string:
            # Add the row if there are retiming alternatives.
            add_leg(etab_obj, leg, new_retiming_string)

            
def manipulate_the_rows(rows, etab_obj, retiming_alt, retiming_option, given_retiming_is_old=False):
    """
    Given a list of identical rows (which should only be a list with ONE row), if the row is found
    in the e-table update the retiming alternative on the found row.
    If the row is not found, add the row.
    
    Note: If the list contains more than one row, the remaining will be removed from the e-table.
    
    @param rows: a list of rows (carmensystems.mave.core.Tuple)
    @type rows: list
    @param etab_obj: The e-table object.
    @type etab_obj: carmensystems.mave.core.ETable
    @param retiming_alt: A string of the retiming alternatives given by planner. 
        The retiming alternatives are separated using a comma.
    @type retiming_alt: string
    @param retiming_option: A string of ADD, REMOVE or REPLACE.
    @type retiming_option: string
    @param given_retiming_is_old: If True, input retiming_alt is considered to be the old
        retiming string, when the new retimining string is constructed, based on the retiming_option.
        Default is False.
    @type given_retiming_is_old: Boolean
    """
    is_first_row = True
    for row in rows:
        # found a row with the leg
        # Update the retiming alternatives for it.
        row_index = etab_obj.getRowIndex(row)
        
        # If the table includes many row that match (should never happen)
        # Manipulate the first row. Remove the rest.
        if is_first_row:
            tmp_retiming_alt = etab_obj[row_index].retiming_alternative
            # Decide which of the 2 retiming strings that should be considered as new 
            # and which to be considered as old.
            # This is important depending on the retiming option.
            if given_retiming_is_old:
                old_retimings = retiming_alt
                new_retiming = tmp_retiming_alt
            else:
                old_retimings = tmp_retiming_alt
                new_retiming = retiming_alt

            new_retiming_string = get_new_retiming_string(retiming_option, new_retiming, old_retimings)
            
            if not new_retiming_string:
                # Remove the row if there are no retiming alternatives.
                etab_obj.remove(row_index)
            else:
                # Save the new retiming string
                etab_obj[row_index].retiming_alternative =  new_retiming_string
            is_first_row = False
        else:
            etab_obj.remove(row_index)

            
def get_actual_retiming_on_leg(leg):
    """
    Returns the actual retiming on the given leg.
    It returns a compressed form, i.e. 0:10 if the departure and arrival retiming is the same,
    else a retiming string with (hh:mm,hh:mm)
    
    @param leg: The given leg.
    @type leg: bag
    @return: retiming string.
    @rtype: string
    """
    v = leg.retiming.retiming_as_string()
    
    return v != "-" and v or "" 
   

def get_active_retiming_path():
    """
    Returns the full path to the retiming etab.
    @return: Full path to the retiming etab.
    @rtype: string
    """
    
    path = expand_etab_path('retiming.%leg_retiming_alternatives_table%')
    return path


def get_new_retiming_string(retiming_option, retiming_str, old_retiming_str=None):
    """
    Returns a new retiming string. The retiming_option decides if the new retiming string should be
    a concatenation between retiming_str and old_retiming_str (ADD),
    or if retiming_str should be removed from old_retiming_str (REMOVE),
    or if it should be replaced by retiming_str (REPLACE).
     
    @param retiming_option: A string of ADD, REMOVE or REPLACE.
    @type retiming_option: string
    @param retiming_str: A string of the retiming alternatives given by planner. 
        The retiming alternatives are separated using a comma.
    @type retiming_str: string
    @param old_retiming: The old string of retiming alternatives found in e-table. 
        The old retiming alternatives are separated using a comma.
    @type old_retiming: string
    @return: Returns a new string with the new retiming alternatives.
    @rtype: string
    """
    retiming_list = get_retiming_array(retiming_str)
    if not old_retiming_str == None:
        old_list = get_retiming_array(old_retiming_str)
    new_list = []
    
    if retiming_option == REMOVE_RET:
        if not old_retiming_str == None:
            new_list = remove_elements_from_list(old_list, retiming_list)
    elif retiming_option == ADD_RET:
        new_list = retiming_list
        if not old_retiming_str == None:
            new_list.extend(old_list)
    elif retiming_option == REPLACE_RET:
        new_list = retiming_list
    else:
        raise RuntimeError("Wrong input. retiming_option '%s' is not valid" % 
                           retiming_option)
    
    # Remove duplicates
    new_list = list(frozenset(new_list))

    # Concatenate the new_list into a retiming string
    separator = ","
    new_retiming_str = separator.join(sorted(new_list, key=ret_alt_value_to_tuple))
    return new_retiming_str


def remove_elements_from_list(input_list, remove_list):
    """
    Takes two lists as input. 'input_list' and 'remove_list'.
    All elements in the 'remove_list' is removed from the 'input_list'.
    
    @param input_list: A list of elements from which elements should be removed.
    @type input_list: list
    @param remove_array: A list of elements which should be removed.
    @type remove_list: list
    @return: Returns the 'input_list' without elements found in 'remove_list'
    @rtype: list
    """
    new_list = []
    for element in input_list:
        if not element in remove_list:
            #OK. The element should be in the new list
            new_list.append(element)
    return new_list

    
def clean_up_table():
    """
    Called from menu entry.
    
    Clean up (after roll out etc.).
    
    * Removes entries which do not exist in the plan.
    * Adds current retiming of each leg. 
    
    """
    etab_obj_org = open_table()
    etable_real_path = get_active_retiming_path()
    etab_obj_new = _create_empty_table(etable_real_path)
    tbh = bag_handler.PlanTrips()
    for leg in tbh.bag.retiming.unique_leg_set(where='active_in_sp'):
        # For every leg in the bag, check if it exist in the old_etab_obj.
        # If it exist, append the row to the new e-table.
        etab_rows = get_list_of_leg_rows(etab_obj_org, leg)
        for row in etab_rows:
            # Add actual retiming and copy the row to the new etab.
            row.retiming_alternative = get_new_retiming_string(ADD_RET,
                                                               row.retiming_alternative, 
                                                               get_actual_retiming_on_leg(leg))
            add_row_of_leg(etab_obj_new, row)
        
        if not etab_rows and leg.retiming.has_retiming():
            _update_etable_with_leg(leg, etab_obj_new, "", REPLACE_RET, True)
    
    etab_obj_new.save()

####################################################################
# Spread retiming alternatives to all legs in the retiming group.
####################################################################


def spread_alternatives_to_identical_legs(scope="marked"):
    """
    Called from menu entry.
    Merge and spread retiming alternatives to all 
    legs in retiming group. Legs must be marked.  
    """
    tbh = get_tbh(scope)
    if not tbh:
        return 
    
    etab_obj = open_table()
    
    for rg_bag in tbh.bag.retiming.retiming_group():
        
        ras = [bag.retiming.retiming_alternatives()
               for bag
               in rg_bag.studio_retiming.ret_alt_set()]
        if len(ras) == 1:
            continue  # all have the same retiming alts. 
        
        alts = []
        for ra in ras:    
            alts += get_retiming_array(ra)
        
        new_retiming_str = ",".join(sorted(list(set(alts)), key=ret_alt_value_to_tuple))
        
        for uleg_bag in rg_bag.retiming.unique_leg_set():
            _update_etable_with_leg(uleg_bag, etab_obj, new_retiming_str, REPLACE_RET)
    
    etab_obj.save()
    
    Cui.CuiCrcRefreshEtabs(os.path.dirname(etab_obj.getName()))
    # Refresh the GUI,
    Gui.GuiCallListener(Gui.RefreshListener, "parametersChanged")
        
######################################################################################
###############   GUI FORM USED FOR GETTING INFO FROM THE PLANNER   ##################
######################################################################################

class MyString(Cfh.String):
    
    def verify(self, val):
        val.value = val.value.replace("C", ":")

class Set_retiming_alternative_gui(Cfh.Box):
    """A form for inputting retiming strings with options of ADD/REMOVE/REPLACE.
    """
      
    def __init__(self):
        Cfh.Box.__init__(self, "Set_retiming_alternative_gui")

        default_retiming_alt = ""
        default_option = ADD_RET
        
        header = "Alternatives:"
        options = [header, REMOVE_RET, ADD_RET, REPLACE_RET]
        
        self.retiming_option = Cfh.String(self, "RETIMING_OPTION", 0, default_option)
        self.retiming_option.setMenu(options)
        self.retiming_option.setMandatory(1)
        self.retiming_option.setMenuOnly(1)
        
        self.valid_retiming_alternatives = MyString(self, "VALID_RETIMING_ALT", 100, 
                                                    default_retiming_alt)
        self.valid_retiming_alternatives.setMandatory(1)
        self.ok = Cfh.Done(self, "B_OK")
        self.quit = Cfh.Cancel(self, "B_CANCEL")

        # CFH Layout
        layout_form = """
FORM;RETIMING_ALT;Set retiming alternatives
COLUMN;41
FIELD;RETIMING_OPTION;Method:
MENU;Examples;-0C05,0C05:+-5;-0C10,0C10:+-10;-0C25,-0C15,-0C05,0C05,0C15,0C25:+-5,15,25;-0C35,-0C25,-0C15,-0C10,0C10,0C15,0C25,0C35:-+10,15,25,35;-0C45,-0C35,-0C25,-0C20,-0C15,-0C10,-0C05,0C05,0C10,0C15,0C20,0C25,0C35,0C45:many
FIELD;VALID_RETIMING_ALT;Retiming alternatives:
EMPTY
LABEL;Note: The real retiming of a leg is always kept as alternative
COLUMN
BUTTON;B_OK;Ok;_Ok
BUTTON;B_CANCEL;Cancel;_Cancel
"""

        filepath = tempfile.mkstemp()[1]
        f = open(filepath, "w")
        f.write(layout_form)
        f.close()
        self.load(filepath)
        os.unlink(filepath)

    def check(self, *args):
        """
        Check if the values in the form has the correct logic.
        """
        r = Cfh.Box.check(self, *args)
        if r: return r
        try:
            get_retiming_array(self.valid_retiming_alternatives.getValue())
        except ValueError, e:
            print e
            return "Must be comma-separated list with retiming alternatives on the format (hh:mm,hh:mm) or hh:mm."
        return None
    
    def get_value_dict(self):
        """Returns a dictionary containing the values set in the form.

        The dictionary contains the following keys:
        - retiming_option (any of the strings: ADD, REMOVE, REPLACE)
        - retiming_alternatives (string of retiming alternatives)

        @rtype: dict
        @return: A dictionary containing the field values
        """
        value_dict={}
        
        value_dict["retiming_option"] = self.retiming_option.valof()
        value_dict["retiming_alternative"] = self.valid_retiming_alternatives.valof()
        return value_dict

# Create one instance and use it each time to keep values in the form
# but not before Studio has been initiated.
set_retiming_alternative_gui = [None] 


################################
# Dynamic menus
################################

def mark_retiming_alternative_menu(menu_name):
    """
    Dynamic menu for marking legs with specific retiming alternatives.
    """
    tbh = bag_handler.WindowChains()
    
    if not tbh.bag: 
        return
    
    alts = {}
    tot = 0
    for leg_bag in tbh.bag.atom_set(where="retiming.has_possible_retiming"):
        key = leg_bag.retiming.retiming_alternatives()
        alts[key] = alts.get(key, 0) + 1
        tot += 1
     
    cmdall = """PythonEvalExpr("MenuCommandsExt.selectTrip({'retiming.%has_possible_retiming%':'true',""" + \
             """'FILTER_MARK':'LEG', 'FILTER_METHOD':'NONE'})")""" 
    
    Gui.GuiAddMenuButton(menu_name, "", "All  (%d)" % tot, 
                         "", "", "", cmdall, Gui.POT_REDO, 
                         Gui.OPA_OPAQUE, "All", 1, "")         
                        
    cmdone = ("""PythonEvalExpr("MenuCommandsExt.selectTrip({""" +
              """'studio_retiming.%%retiming_alternatives_selection_safe%%':""" +
              """'%s', 'FILTER_MARK':'LEG', 'FILTER_METHOD':'NONE'})")""")
    
    for key in sorted(alts):
        cmd = cmdone % key.replace(",", "_")
        Gui.GuiAddMenuButton(menu_name, "", key + "  (%d)" % alts[key], 
                             "", "", "", cmd, 
                             Gui.POT_REDO, Gui.OPA_OPAQUE, key, 1, "")


def filter_retiming_alternative_menu(menu_name):
    """
    Dynamic menu for filtering legs with specific retiming alternatives.
    """
    tbh = bag_handler.PlanTrips()  
    
    if not tbh.bag: 
        return
    
    alts = {}
    tot = 0
    for leg_bag in tbh.bag.atom_set(where="retiming.has_possible_retiming"):
        key = leg_bag.retiming.retiming_alternatives()
        alts[key] = alts.get(key, 0) + 1
        tot += 1
    
    cmdall = """PythonEvalExpr("MenuCommandsExt.selectTrip({'retiming.%has_possible_retiming%':'true'})")""" 
    
    Gui.GuiAddMenuButton(menu_name, "", "All  (%d)" % tot, 
                         "", "", "", cmdall, Gui.POT_REDO, 
                         Gui.OPA_OPAQUE, "All", 1, "")         
                       
    cmdone = ("""PythonEvalExpr("MenuCommandsExt.selectTrip({""" +
              """'studio_retiming.%%retiming_alternatives_selection_safe%%':""" +
              """'%s'})")""")
    for key in sorted(alts):
        cmd = cmdone % key.replace(",", "_")
        Gui.GuiAddMenuButton(menu_name, "", key + "  (%d)" % alts[key], 
                             "", "", "", cmd, 
                             Gui.POT_REDO, Gui.OPA_OPAQUE, key, 1, "")  
                

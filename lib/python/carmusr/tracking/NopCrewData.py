#$Header$
"""
NopCrewData

A module handling the temporary tables
for display and editing in nop crew form for APIS.

The file consists of one class with the following features:
- Creating temporary tables
- Filling temporary tables with values
- Save changes to the model

There is also a lot of wrapper functions for both adding/removing
rows in each temporary table.

"""

##############################################################################
#
#  Created:    Sep 2013
#  By:         Ulf Hansryd
#
#  Comments:   
#  By:         
#
##############################################################################

__version__ = "$Revision$"

import time
import Cui
import modelserver as M
from tm import TM
from AbsTime import AbsTime
import StartTableEditor
import carmensystems.services.dispatcher as CSD
import carmensystems.rave.api as R


class TableEditorTmpTables:
    """
    Class that contains all methods to set up the temporary tables needed for the form.

    """
    def __init__(self):
        """
        Set up the tablemanager instance,
        reset index counters
        and create all temporary tables.

        """
        
        # Store the pointer to the TableManager instance in the object for availability everywhere.
        self.tm = M.TableManager.instance()

        # Reset all index counters used for the temporary tables.
        # Also resets the list of already shown crew during this objects lifetime.
        self.resetCounters()

        # Creat temporary tables
        self.createTables()


        # The removeList contains information on all rows to remove upon save
        self.removeList = []

    def resetCounters(self):
        """
        Reset all index counters used as keys in the temporary tables.

        """

        # All index counters are reset.
        # These counters are used as keys in the temporary tables.
        # They all use this key instead of their normal key so that users
        # edit the keyvalues in a record.
        self.nopCrewRowNumber = 0
 


    def addDataToTables(self, flight_legs, leglisting, removeOld=True):
        """
        Load all data available about crew into the temporarytables.

        """
        
        print "NopCrewInfo::addDataToTables::Adding data for crew:"


        # Load data for each temporary table.
        self.createNopCrewTable(flight_legs, removeOld)
        self.createFlightInfoTable(flight_legs, removeOld)
        self.createLeglistingTable(leglisting, removeOld)
 
    def createTables(self):
        """
        Create all temporary tables needed.
        """

        # All temporary tables are created within try statements.
        # This means that if it already exists an exception will
        # be thrown and actions will be taken.
        #
        # This can give weird behaviour though if exceptions happen
        # in the creation of one certain table then it might be missing
        # forever without noticing immediately.

        try:
            self.t_modcom_non_op_crew_info = self.tm.table("modcom_non_op_crew_info")
            print "Table exists: modcom_non_op_crew_info"
            self.t_modcom_non_op_crew_info.removeAll()
        except M.TableNotFoundError:
            self.t_modcom_non_op_crew_info = self.tm.createTable("modcom_non_op_crew_info",
                                [M.IntColumn('rownr','')],
                                [M.StringColumn('leg_info','')
                                 ])
            print "Table created: modcom_non_op_crew_info"
        

        # The tmp_flight_info should contain one row with the currently chosen flight
        try:
            self.flightInfo = self.tm.table("tmp_flight_info")
            print "Table exists: tmp_flight_info"
        except M.TableNotFoundError:
            self.flightInfo = self.tm.createTable("tmp_flight_info",
                                [M.IntColumn("rno", "Row number")],
                                [M.StringColumn("udor", "udor"),
                                 M.StringColumn("fd", "udor"),
                                 M.StringColumn("adep", "udor")])
            print "Table created: tmp_flight_info"
        try:
            self.nopCrew = self.tm.table("tmp_nop_crew")
            print "Table exists: tmp_nop_crew"
        except M.TableNotFoundError:
            self.nopCrew = self.tm.createTable("tmp_nop_crew",
                                 [M.IntColumn("rno", "Row number")],
                                 [M.StringColumn("id", "UUID"),
                                 M.BoolColumn("assigned", "assigned"),
                                 M.RefColumn("position", "nop_crew_position_set"),
                                 M.StringColumn("crew_id", "crew id"),
                                 M.StringColumn("sn", "surname"),
                                 M.StringColumn("gn", "given name"),
                                 M.StringColumn("gender", "gender"),
                                 M.RefColumn("nationality", "country"),
                                 M.DateColumn("birthday", "birthday"),
                                 M.StringColumn("birth_place", "birth place"),
                                 M.StringColumn("birth_state", "birth state"),
                                 M.RefColumn("birth_country", "country"),
                                 M.StringColumn("res_street", "res street"),
                                 M.StringColumn("res_city", "res city"),
                                 M.StringColumn("res_postal_code", "res postal code"),
                                 M.RefColumn("res_country", "country"),

                                 M.StringColumn("phone", "phone"),
                                 M.StringColumn("email", "email"),

                                 M.StringColumn("passport", "passport number"),
                                 M.RefColumn("passport_issuer", "country"),
                                 M.DateColumn("passport_validto", "passport expiry"),

                                 M.StringColumn("visa_type", "visa type"),
                                 M.StringColumn("visa_number", "visa number"),
                                 M.RefColumn("visa_country", "country"),
                                 M.DateColumn("visa_validto", "visa expiry"),

                                 M.BoolColumn("on_mcl", "on mcl"),
                                 M.StringColumn("si", "si"),
                                 M.BoolColumn("add_", "Added"),
                                 M.BoolColumn("removed_", "Removed")])

            print "Table created: tmp_nop_crew"
                                 

    def loadDBTables(self):
        """
        Make sure all needed tables are loaded and create handles to all database tables used.

        """

        # Load the interesting tables from DB to the Table Manager.
        self.tm.loadTables(["nop_crew_position_set", "nop_crew", "nop_crew_asmt"])

        # Get handles to all used database tables.
        self.crew = self.tm.table("crew")
        self.country = self.tm.table("country")
        self.flight_leg = self.tm.table('flight_leg')
        self.airport = self.tm.table('airport')

        # self.crew_traveldoc = self.tm.table("crew_traveldoc")
        self.nop_crew = self.tm.table("nop_crew")
        self.nop_crew_mcl = self.tm.table("nop_crew_mcl")
        self.nop_crew_asmt = self.tm.table("nop_crew_asmt")
        self.nop_crew_position_set = self.tm.table('nop_crew_position_set')


    def createLeglistingTable(self, leglisting, removeOld=True):
        """
        Add flight info to the table t_modcom_non_op_crew_info
        """
        MAXCOLSTRING = 200

        # Need only one row in info table
        self.r_modcom_non_op_crew_info = self.t_modcom_non_op_crew_info.create((0,))                   

        if len(leglisting) > MAXCOLSTRING:
            leglisting = cutLines(leglisting, MAXCOLSTRING)
        self.r_modcom_non_op_crew_info.leg_info = leglisting  
            
    def createFlightInfoTable(self, flight_legs, removeOld=True):
        """
        Add flight info to the table tmp_flight_info
        """
        for ix in range(len(flight_legs)):
            try:
                info_row = self.flightInfo.create((ix,))
            except:
                info_row = self.flightInfo[(ix,)]

            print "--- DEBUG: NopCrewData:createFlightInfoTable:flight_legs: ", flight_legs
            info_row.udor = str(flight_legs[ix]["UDOR"])
            info_row.fd = flight_legs[ix]["FD"]
            info_row.adep = flight_legs[ix]["ADEP"]
        
    def createNopCrewTable(self, flight_legs, removeOld=True):
        """
        Add document info to the table tmp_nop_crew
        """

        assigned_crew = {}
        num_legs = len(flight_legs)
        assigned_nop_crew = set()

        for flight_leg in flight_legs:
            flight_leg_tuple = (flight_leg["UDOR"], flight_leg["FD"], flight_leg["ADEP"])
            for row in self.nop_crew_asmt.search("(&(leg.udor=%s)(leg.fd=%s)(leg.adep=%s))" %(flight_leg_tuple)):
                try:
                    assigned_crew[row.nop_crew.id] += 1
                except KeyError:
                    assigned_crew[row.nop_crew.id] = 1

        # Crew must be assigned to all legs!
        for nop_crew_id in assigned_crew.keys():
            if assigned_crew[nop_crew_id] == num_legs:
                assigned_nop_crew.add(nop_crew_id)
        
        if removeOld:
            self.nopCrew.removeAll()
        for row in self.nop_crew:
            try:
                record = self.nopCrew.create((self.nopCrewRowNumber,))

                # Copy all document attributes
                record.id = row.id

                if row.id in assigned_nop_crew:
                    record.assigned = True
                else:
                    record.assigned = False
                
                record.position = row.position
                record.crew_id = row.crew_id
                record.gn = row.gn
                record.sn = row.sn
                record.gender = row.gender
                record.nationality = row.nationality
                record.birthday = row.birthday
                record.birth_place = row.birth_place
                record.birth_state = row.birth_state
                record.birth_country = row.birth_country
                record.res_street = row.res_street
                record.res_city = row.res_city
                record.res_postal_code = row.res_postal_code
                record.res_country = row.res_country

                record.phone = row.phone
                record.email = row.email

                record.passport = row.passport
                record.passport_issuer = row.passport_issuer
                record.passport_validto = row.passport_validto

                record.visa_type = row.visa_type
                record.visa_number = row.visa_number
                record.visa_country = row.visa_country
                record.visa_validto = row.visa_validto

                record.on_mcl = row.on_mcl
                record.si = row.si
                record.add_ = False
                record.removed_ = False

                # Make sure our index key counter gets incremented so the next time
                # a row is created we don't have any problems with duplicate keys.
                self.nopCrewRowNumber += 1
            except M.ReferenceError:
                print "NopCrewInfo::Reference missing for documentrow. Row left out"
                record.remove()
                
    def nop_crew_edit_save_tables(self):
        """
        Submit changes done to the temporary tables to the real model.

        """
        print "CrewInfo::Saving changes..."
        for row in self.nopCrew:
            if row.removed_ and row.id:
                a_nop_crew = self.nop_crew[(row.id,)]
                for row_ref in self.nop_crew_asmt.search("(nop_crew.id=%s)" %row.id):
                    row_ref.remove()
                a_nop_crew.remove()
                continue
            
            if row.add_:
                if row.id == "" or row.id == None: # New crew, no uuid
                    new_id = self.tm.createUUID()
                    a_nop_crew = self.nop_crew.create((new_id,))
                else:
                    a_nop_crew = self.nop_crew[(row.id,)]
                # Update data
                a_nop_crew.position = row.position
                a_nop_crew.crew_id = row.crew_id
                a_nop_crew.gn = row.gn
                a_nop_crew.sn = row.sn
                if row.gender:
                    a_nop_crew.gender = row.gender[0:2]
                else:
                    a_nop_crew.gender = row.gender
                a_nop_crew.nationality = row.nationality
                a_nop_crew.birthday = row.birthday
                a_nop_crew.birth_place = row.birth_place
                a_nop_crew.birth_state = row.birth_state
                a_nop_crew.birth_country = row.birth_country
                a_nop_crew.res_street = row.res_street
                a_nop_crew.res_city = row.res_city
                a_nop_crew.res_postal_code = row.res_postal_code
                a_nop_crew.res_country = row.res_country

                a_nop_crew.phone = row.phone
                a_nop_crew.email = row.email

                a_nop_crew.passport = row.passport
                a_nop_crew.passport_issuer = row.passport_issuer
                a_nop_crew.passport_validto = row.passport_validto

                a_nop_crew.visa_type = row.visa_type
                a_nop_crew.visa_number = row.visa_number
                a_nop_crew.visa_country = row.visa_country
                a_nop_crew.visa_validto = row.visa_validto

                a_nop_crew.on_mcl = row.on_mcl
                a_nop_crew.si = row.si

                #----------------------------
                # Assign or deassign all legs
                #----------------------------
                for flight_info in self.flightInfo:
                    udor_str = flight_info.udor
                    fd = flight_info.fd
                    adep_str = flight_info.adep
                    # print udor_str+ "---"+fd+"---"+adep_str
                    udor = AbsTime(udor_str)
                    adep = self.airport[(adep_str,)]
                    flight_leg = self.flight_leg[(udor, fd, adep)]

                    if row.assigned:
                        try:
                            # Check if already assigned
                            asmt = self.nop_crew_asmt[(flight_leg,a_nop_crew)]
                        except:    
                            self.nop_crew_asmt.create((flight_leg,a_nop_crew))
                    else:
                        # Remove assigned
                        try:
                            asmt = self.nop_crew_asmt[(flight_leg,a_nop_crew)]
                            asmt.remove()
                        except:
                            pass

        refresh(["nop_crew", "nop_crew_asmt"])

def refresh(tables):
    """
    Pass a list of tables to reload and then refresh Studio.
    """
    import Gui
    for table in tables:
        Cui.CuiReloadTable(table)
    Gui.GuiCallListener(Gui.RefreshListener, "parametersChanged")
    Gui.GuiCallListener(Gui.ActionListener)

def okOrExcept(message):
    """
    Displays warning dialog. Raises exception if user presses 'Cancel'.
    """
    if warning(message): raise Exception('Cancelled by user')


def warning(message, title = "Warning", form_name = "MESSAGE_BOX"):
    """
    Shows a box with the specified message and title as a warning
    message. There is an Ok button and a Cancel button.
    The function returns 0 if Ok is pressed, and 1
    if Cancel is pressed
    """
    import Cfh
    box = Cfh.Box(form_name, title)

    p = Cfh.Label(box,"PICTURE","xm_warning.pm")
    p.setLoc(Cfh.CfhLoc(1,1))

    l = Cfh.Label(box,"MESSAGE",message)
    l.setLoc(Cfh.CfhLoc(1,4))

    ok = Cfh.Done(box,"OK")
    ok.setText("OK")
    ok.setMnemonic("_OK")
    cancel = Cfh.Cancel(box,"CANCEL")
    cancel.setText("Cancel")
    cancel.setMnemonic("_Cancel")

    box.build()
    box.show(1)
    return box.loop()



            
# The object theTables is used as a global object to store all needed handles and methods.
theTables = None

# def initTempTables(flight_leg_tuple, crewId = 'NO CREW'):
def initTempTables(legs, leglisting):
    """
    Initiate the temporary tables needed for the crew information form to work.

    """
    
    global theTables

    print "NopCrewInfo::Creating new instance of tables"

    # Create the object.
    theTables = TableEditorTmpTables()

    # Load all needed database tables and get their handles.
    theTables.loadDBTables()

    # Add non-crew specific information the form needs
    # theTables.addTempInfo()

    # Load all crew specific information to the temporary tables.
    theTables.addDataToTables(legs, leglisting)


def getLegs():
    #------------------------------
    # Load marked legs from rave
    #------------------------------
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiGetCurrentArea(Cui.gpc_info), "window")
    legs, = R.eval('default_context',
                   R.foreach(R.iter('iterators.leg_set',where='marked and flight_duty'),
                            'leg.%udor%',
                            'leg.%flight_descriptor%',
                            'leg.%start_station%',
                            'leg.%activity_scheduled_start_time_UTC%'))
    print "--- DEBUG: NopCrewData:getLegs:legs: ",legs
    # ----------------------
    # Remove duplicates
    # ----------------------
    legTupleList =[]
    for (ix, udor_str, flight_desc, start_station, start_sch_utc) in legs:
        legTupleList.append((udor_str,flight_desc,start_station,start_sch_utc))
    #legTupleList = [(l['UDOR'],l['FD'],l['ADEP'],l['DEP']) for l in legs]
    uniqueLegs = list(frozenset(legTupleList))
    legs = []
    for leg in uniqueLegs:
        legs.append({'UDOR': leg[0],
                     'FD':   leg[1],
                     'ADEP': leg[2],
                     'DEP':  leg[3]})

    # ---------------------------------------------------------------
    # If selected legs are more than MAXSELLEGS, show warning dialog
    # Exit on Cancel
    # ---------------------------------------------------------------
    MAXSELLEGS = 10
    if len(legs) > MAXSELLEGS:
        msg = 'More than %d (%d) legs selected! Do you want to continue?'\
              % (MAXSELLEGS, len(legs))
        try:
            okOrExcept(msg)
        except:
            raise "Open form cancelled"
    return legs

def addLegsInfoString(legs):
    # ---------------------------------------------
    # Sort legs for proper display in form
    # ---------------------------------------------
    print "Leeeegs: ",legs
    temp_tuple_list = [(leg['DEP'],leg) for leg in legs]
    temp_tuple_list.sort()
    legs[:] = [tup[1] for tup in temp_tuple_list]
        
    #-----------------------------------------
    # Get table manager flight leg references
    #-----------------------------------------
    #tm = M.TableManager.instance()
    #t_flight_leg = tm.table("flight_leg")
    #t_airport = tm.table("airport")
    
    for leg in legs:
        udor = leg["UDOR"]
        fd = leg["FD"]
        adep = leg["ADEP"]

    #-------------------------------------------------------
    # Create a string listing legs for info display in form
    #-------------------------------------------------------
    first = True
    leglisting = ''
    for leg in legs:
        if not first:
            leglisting += '\n'
        leglisting += "%s %s %s" % (leg['ADEP'],leg['DEP'],leg['FD'])
        first = False
    return leglisting

def nopCrew():

    legs = getLegs()
    leglisting = addLegsInfoString(legs)
    

    initTempTables(legs, leglisting)

    # Start the java form.
    StartTableEditor.StartTableEditor(['-f', '$CARMUSR/data/form/nop_crew_select.xml'], "Nop Crew")

def cutLines(oldstr, maxlen):
    """Cut lines to meet max lenght constraints."""
    newstr = ''
    addtoend = '...'
    lines = oldstr.splitlines(True)
    for l in lines:
        if len(newstr) + len(l) < maxlen - len(addtoend):
            newstr += l
        else:
            newstr += addtoend
            return newstr

def nop_crew_edit_save(plan):
    """
    Save the temporary tables into the real model tables.

    """

    print "NopCrew::Save"

    # Use the global instance of theTables that contains all methods needed.
    global theTables

    # Call the save method.
    theTables.nop_crew_edit_save_tables()

# Register the function so that it can be found from the java environment.
CSD.registerService(nop_crew_edit_save, "nopCrewEdit.nop_crew_edit_save")

def nop_crew_validate_doc_date(plan, doc, valid_to_str):
    global theTables
    print "--- DEBUG: NopCrewData:nop_crew_validate_doc_date:doc: ", doc
    print "--- DEBUG: NopCrewData:nop_crew_validate_doc_date:valid_to_str: ", valid_to_str

    if valid_to_str == "NULL":
        return {"actions":'valiDateSave(cs_crew_src, ${cs_crew_id[-1]}, "%s", "%s", "%s")' % (doc, valid_to_str, "False")}

    valid_to = time.strptime(valid_to_str, '%d%b%Y %H:%M')
    print "--- DEBUG: NopCrewData:nop_crew_validate_doc_date:valid_to: ", valid_to

    for flight_info in theTables.flightInfo:
        print "--- DEBUG: NopCrewData:nop_crew_validate_doc_date:flight_info: ", flight_info
        flight_time = time.strptime(flight_info.udor, '%d%b%Y %H:%M')
        return {"actions":'valiDateSave(cs_crew_src, ${cs_crew_id[-1]}, "%s", "%s", "%s")' % (doc, valid_to_str, str(valid_to > flight_time))}

# Register the function so that it can be found from the java environment.
CSD.registerService(nop_crew_validate_doc_date, "nopCrewEdit.nop_crew_validate_doc_date")


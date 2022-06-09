#####################################################

# A module for Bid ratio selection filter functionality in rostering
#
# Contains:
#     Selection and sort from crew margin
#     Selection filter dialog for bid ratio
#     Selection dialog for bid reference roster
#     Function for creating a bid reference etab
#     Functions for installing a new default bid file
#      and creating bid rudobs for all bids in a bid file
#
# Created: January 2007
# By: Jonas Carlsson, Jeppesen
#
import fileinput
import os
import time
import tempfile
import shutil
import sys
import datetime

# Sys imports
import Cui
import Cfh
import carmstd.cfhExtensions as cfhExtensions
import Errlog
import Variable as PYV
import carmensystems.rave.api as R
import Etab as Etab
import AbsDate as AbsDate
import carmusr.HelperFunctions as HelperFunctions
# old parameter API
from carmstd.parameters import parameter

# User imports
import Select
import MenuCommandsExt


##################################################################
# Selection and sort of trips from crew margin
#

def selectTripsMatchingBid(bid_nr):
    currentArea = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    crewId = Cui.CuiCrcEvalString(Cui.gpc_info, currentArea, "object", "crew.%id%")

    Errlog.log("Bids.py::in selectTripsMatchingBid, bid = %i and crewId = %s"%(bid_nr, crewId))
    parameter["bid.filter_crew_id_override_p"] = crewId
    parameter["bid.filter_bid_number_p"] = bid_nr

    # Area toggles between 0 and 1, if not open, throws exception
    selectArea = Cui.CuiArea1
    if currentArea == Cui.CuiArea1:
        selectArea = Cui.CuiArea0
    # BZ26718 planning_area.%trip_is_in_planning_area%=true added. 2008-06-24 Janne C
    Select.select({'bid.%filter_trip_match_bid%':'true','planning_area.%trip_is_in_planning_area%':'true'}, selectArea, Cui.CrrMode)

    parameter["bid.filter_crew_id_override_p"] = ""
    parameter["bid.filter_bid_number_p"] = 0

def sortTripsByGenerationCost():
    currentArea = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    crewId = Cui.CuiCrcEvalString(Cui.gpc_info, currentArea, "object", "crew.%id%")

    Errlog.log("Bids.py::in sortTripsByGenerationCost, crewId = %s"%(crewId))
    parameter["bid.filter_crew_id_override_p"] = crewId

    # Area toggles between 0 and 1, if not open, throws exception
    selectArea = Cui.CuiArea1
    if currentArea == Cui.CuiArea1:
        selectArea = Cui.CuiArea0
    Select.sortParam('bid.%generation%', windowArea=selectArea)


##################################################################
# Class and functions for selecting crew with bids
#

class BidLevelSelection(Cfh.Box):
    def __init__(self, *args):
        Cfh.Box.__init__(self, *args)

        self.default_values = {}

        self.valid_ref_ratio = ";*;0;10;20;30;40;50;60;70;80;90;100"

        # Fields for bid ratio selection
        self.select_ratio_upper = Cfh.String(self,"BIDS_RATIO_UPPER",8,"*")
        self.select_ratio_upper.setMandatory(True)
        self.select_ratio_upper.setMenuString(self.valid_ref_ratio)

        self.select_ratio_lower = Cfh.String(self,"BIDS_RATIO_LOWER",8,"*")
        self.select_ratio_lower.setMandatory(True)
        self.select_ratio_lower.setMenuString(self.valid_ref_ratio)

        # Field for selection filter method
        self.valid_selection = ";ADD;SUBSELECT;REPLACE"
        self.selection_type = Cfh.String(self,"BIDS_SELECTION",10,"REPLACE")
        self.selection_type.setMandatory(1)
        self.selection_type.setMenuOnly(1)
        self.selection_type.setMenuString(self.valid_selection)

        # OK, CANCEL and RESET buttons
        self.ok = Cfh.Done(self,"B_OK")
        self.quit = Cfh.Cancel(self,"B_CANCEL")
        # Old Comment: Investigate the use of a default button
        self.reset = Cfh.Reset(self, "B_RESET")

        # Creating the form
        form_layout = """
FORM;BIDLEVELS_FORM;`Select bid levels`

EMPTY;
LABEL;`Bid ratio level`
LABEL;`Filter method`

COLUMN;
LABEL;`From`
FIELD;BIDS_RATIO_LOWER;
FIELD;BIDS_SELECTION;

COLUMN;
LABEL;`To`
FIELD;BIDS_RATIO_UPPER;

BUTTON;B_OK;`Ok`;`_Ok`
BUTTON;B_CANCEL;`Cancel`;`_Cancel`
BUTTON;B_RESET;`Reset`;`_Reset`

"""

        bids_form_file = tempfile.mktemp()
        f = open(bids_form_file,"w")
        f.write(form_layout)
        f.close()
        self.load(bids_form_file)
        os.unlink(bids_form_file)

    def getValues(self):
        """
        Function returning the values set in the form.
        """
        return(self.selection_type.valof(),
               self.select_ratio_upper.valof(),
               self.select_ratio_lower.valof())

    def setValues(self):
        self.select_ratio_upper.setMenuString(self.valid_ref_ratio)
        self.select_ratio_lower.setMenuString(self.valid_ref_ratio)
        self.selection_type.setMenuString(self.valid_selection)



##################################################################
# Class and functions for selecting which bid file to use
#
class BidFileSelection(Cfh.Box):
    def __init__(self, *args):
        """
        Creates the a BidSelection dialog
        """

        Cfh.Box.__init__(self, *args)

        # Field for bid reference roster selection
        self.select_bid_file = Cfh.String(self,"BID_FILES", 50)
        self.select_bid_file.setMenuOnly(True)
        self.select_bid_file.setMandatory(True)

        # OK and CANCEL buttons
        self.ok = Cfh.Done(self,"B_OK")
        self.quit = Cfh.Cancel(self,"B_CANCEL")

        # Create the label with the current reference roster
        current_bid_file = self.getCurrentBidFile()
        bid_file = "No bid file currently selected"
        if current_bid_file:
            bid_file = "Current bid file: %s" % current_bid_file

        # Creating the form
        form_layout = """
FORM;BID_FILES_FORM;`Select bid file`
LABEL;`%s`
LABEL;`Available bid files:`
FIELD;BID_FILES;
BUTTON;B_OK;`Ok`;`_Ok`
BUTTON;B_CANCEL;`Cancel`;`_Cancel`
""" % bid_file

        bids_form_file = tempfile.mktemp()
        f = open(bids_form_file,"w")
        f.write(form_layout)
        f.close()
        self.load(bids_form_file)
        os.unlink(bids_form_file)

    def getCurrentBidFile(self):
        """
        Function returning the currently selected bid file, if any.
        Return None if no bid file is selected
        """
        bid_file, = R.eval('default_context', 'bid.%table_para%')

        if not bid_file:
            return None
        else:
            return bid_file

    def getValues(self):
        """
        Function returning the values set in the form.
        """
        return(self.select_bid_file.valof())


    def setValues(self):
        """
        Function setting the values in the form.

        Outstanding: Communicate to the user if, for whatever reason,
                     there are no available reference rosters. (No ref
                     rosters have been created or maybe the bid.%ref_table_location_p
                     parameter is wrong and does not point to a directory
        """

        # Find and list all the files in the CARMDATA/ETABLES/rave:bid.%reference_path% directory
        rave_path, = R.eval('default_context', 'bid.%bids_path%')
        path = os.path.expandvars(os.path.join("$CARMDATA/ETABLES", rave_path))
        files = ""
        try:
            dirList = os.listdir(path)
            for fname in dirList:
                if os.path.isfile(os.path.join(path, fname)):
                    files += ";" + fname
            self.select_bid_file.setMenuString(files)

        except OSError, err:
            import errno
            # check for "file not found errors", re-raise other cases
            if err.errno != errno.ENOENT: raise
            # handle the file not found error
            Errlog.log("BIDS: BidFileSelection.setValues() - file: " + err.filename + " not found")

def selectBidFile(isForCrew=True, area=Cui.CuiWhichArea):
    """
    Creates a select form
    """
    # If the dialog is global it does not seem to handle changes to
    # rave parameters, in particular bid.%ref_table_location_p%
    #global bid_reference_select_form
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, area)
    try:
        bid_file_select_form == bid_file_select_form
    except:
        bid_file_select_form = BidFileSelection("BidFile_Selection")

    # We need to do this everytime since a new bid file
    # might have been created since the dialog was created
    bid_file_select_form.setValues()

    Errlog.log("BIDS: BidFileSelection form created")

    # Show dialog
    bid_file_select_form.show(1)

    if bid_file_select_form.loop() == Cfh.CfhOk:
        # Ok button pressed, get the value
        bid_file = bid_file_select_form.getValues()

        # Check that the file exists
        rave_path, = R.eval('default_context', 'bid.%bids_path%')
        fname = os.path.expandvars(os.path.join("$CARMDATA/ETABLES", rave_path, bid_file))
        if os.path.isfile(fname):
            # Set parameter
            buf = PYV.Variable(bid_file)
            Cui.CuiCrcSetParameterFromString("bid.%table_para%", buf.value)


##################################################################
# Class and functions for selecting which bid reference file to use
#
class BidReferenceRosterSelection(Cfh.Box):
    def __init__(self, *args):
        """
        Creates the a BidReferenceRosterSelection dialog
        """

        Cfh.Box.__init__(self, *args)

        # Field for bid reference roster selection
        self.select_bid_ref_rosters = Cfh.String(self,"BID_REF_ROSTERS", 50)
        self.select_bid_ref_rosters.setMenuOnly(True)
        self.select_bid_ref_rosters.setMandatory(True)

        # OK and CANCEL buttons
        self.ok = Cfh.Done(self,"B_OK")
        self.quit = Cfh.Cancel(self,"B_CANCEL")

        # Create the label with the current reference roster
        current_ref_roster = self.getCurrentReferenceRoster()
        ref_roster = "No reference roster currently selected"
        if current_ref_roster:
            ref_roster = "Current reference roster: %s" % current_ref_roster

        (pa_files, other_files) = self.getAvailableReferenceRosters()
        if not pa_files:
            available = "No reference rosters available for the planning area and period"
            self.files = other_files
        else:
            available = "Available reference rosters"
            self.files = pa_files

        # Creating the form
        form_layout = """
FORM;BIDLEVELS_FORM;`Select bid reference roster`
LABEL;`%s`
LABEL;`%s:`
FIELD;BID_REF_ROSTERS;
BUTTON;B_OK;`Ok`;`_Ok`
BUTTON;B_CANCEL;`Cancel`;`_Cancel`
""" % (ref_roster, available)

        bids_form_file = tempfile.mktemp()
        f = open(bids_form_file,"w")
        f.write(form_layout)
        f.close()
        self.load(bids_form_file)
        os.unlink(bids_form_file)

    def getCurrentReferenceRoster(self):
        """
        Function returning the currently selected reference roster, if any.
        Return None if no reference roster is selected
        """
        ref_roster, = R.eval('default_context', 'bid.%maxroster_table_p%')

        if not ref_roster:
            return None
        else:
            return ref_roster

    def getValues(self):
        """
        Function returning the values set in the form.
        """
        return(self.select_bid_ref_rosters.valof())

    def getAvailableReferenceRosters(self):
        # Find and list all the files in the CARMDATA/ETABLES/rave:bid.%reference_path% directory
        rave_path, = R.eval('default_context', 'bid.%reference_path%')
        path = os.path.expandvars(os.path.join("$CARMDATA/ETABLES", rave_path))
        planning_area = getPlanningAreaForReference()
        pa_files = ""
        other_files = ""
        try:
            dirList = os.listdir(path)
            for fname in dirList:
                if os.path.isfile(os.path.join(path, fname)):
                    if fname.find(planning_area) > -1:
                        pa_files += ";" + fname
                    else:
                        other_files += ";" + fname
            return (pa_files, other_files)
        except OSError, err:
            import errno
            # check for "file not found errors", re-raise other cases
            if err.errno != errno.ENOENT: raise
            # handle the file not found error
            Errlog.log("BIDS: BidReferenceRosterSelection.setValues() - file: " + err.filename + " not found")

    def setValues(self):
        """
        Function setting the values in the form.

        """
        self.select_bid_ref_rosters.setMenuString(self.files)

def selectBidReferenceRoster(isForCrew=True, area=Cui.CuiWhichArea):
    """
    Creates a select form
    """
    # If the dialog is global it does not seem to handle changes to
    # rave parameters, in particular bid.%ref_table_location_p%
    #global bid_reference_select_form
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, area)
    try:
        bid_reference_select_form == bid_reference_select_form
    except:
        bid_reference_select_form = BidReferenceRosterSelection("BidReference_Selection")

    # We need to do this everytime since a new reference roster
    # might have been created since the dialog was created
    bid_reference_select_form.setValues()

    Errlog.log("BIDS: BidReferenceSelection form created")

    # Show dialog
    bid_reference_select_form.show(1)

    if bid_reference_select_form.loop() == Cfh.CfhOk:
        # Ok button pressed, get the value
        ref_roster = bid_reference_select_form.getValues()

        # Check that the file exists
        rave_path, = R.eval('default_context', 'bid.%reference_path%')
        fname = os.path.expandvars(os.path.join("$CARMDATA/ETABLES", rave_path, ref_roster))
        if os.path.isfile(fname):
            # Set parameter
            buf = PYV.Variable(ref_roster)
            Cui.CuiCrcSetParameterFromString("bid.%maxroster_table_p%",buf.value)



##################################################################
# Function for creating a reference roster etab
#
def createBidReferenceEtab():
    """
    Function to create a reference roster etab from the current plan
    The script places the reference roster in
    $CARMDATA/ETABLES/rave:bid.%reference_path%
    """
    if HelperFunctions.isDBPlan():
        cfhExtensions.show("createBidReferenceEtab(): Should not run in Database!")
        Errlog.log("Bids.createBidReferenceEtab(): Should not run in Database!")
        return

    Errlog.log("Bids.createBidReferenceEtab(): Entering")
    try:
        rave_path, = R.eval('default_context', 'bid.%reference_path%')
        path = os.path.expandvars(os.path.join("$CARMDATA/ETABLES", rave_path))

        planning_area = getPlanningAreaForReference()
        fname = planning_area + time.strftime("%Y%m%d_%H%M") + "_" + os.environ['USER']
        fpath = os.path.join(path, fname)

        MenuCommandsExt.report2etab("CreateBidReference.output", fpath)

        # Show a dialog with the name of the currently created reference roster
        cfhExtensions.show("Reference roster created: %s" % fname)

    except:
        cfhExtensions.show("Error when creating the reference roster")

    Errlog.log("Bids.createBidReferenceEtab(): Leaving")

def getPlanningAreaForReference():
    (cat, pg, sta, qual, pp_start) = R.eval("planning_area.%planning_area_crew_category%",
                                             "planning_area.%crew_planning_group%",
                                             "planning_area.%planning_area_crew_station%",
                                             "planning_area.%planning_area_crew_qualification%",
                                             "fundamental.%pp_start%")

    # Crew category
    if cat == "F": cat = "FC"
    elif cat == "C": cat = "CC"
    if cat != "ANY": category = cat + "_"
    else: category = ""

    # Crew planning group
    if pg != "ANY": planning_group = pg + "_"
    else: planning_group = ""

    # Crew station
    if sta != "ANY": station = sta + "_"
    else: station = ""

    # Crew qualification
    if qual != "ANY": qualification = qual + "_"
    else: qualification = ""

    # Period
    period = "%04d-%02d_" % pp_start.split()[:2]

    return category + planning_group + station + qualification + period


def convertBidFile(bid_file_path, tmp_file_name):
    """
    Administrator script that takes as argument a bid file and converts
    it from the Interbids export format to a format better suitable for
    integration with the SAS CMS data model.

    Column names are changed and the crew id data is changed from
    "SK  12345" to "12345".
    """

    Errlog.log("Bids.convertBidFile(): Copying %s to %s" % (bid_file_path, bid_file_path+'.before_conversion'))
    shutil.copy(bid_file_path, bid_file_path+'.before_conversion')

    o_file_name = os.path.expandvars("$CARMTMP/%s" % tmp_file_name)
    Errlog.log("Bids.convertBidFile(): Temporary file is %s" % o_file_name)
    output_file = open(o_file_name, 'w')
    for line in fileinput.input(bid_file_path, True):
        # Does it begin with a '"SK'? If so remove the SK part
        if line[:5] == '"SK  ':
            output_file.write('"' + line[5:])
        else:
            # Part of the header, replace column names
            if line[0] in ("S", "I", "R", "A", "B"):
                if line[1:5] == "Type":
                    output_file.write(line[0] + "bid" + line[1:].lower())
                else:
                    output_file.write(line[0] + line[1:].lower())
            else:
                output_file.write(line)

    fileinput.close()
    output_file.close()
    Errlog.log("Bids.convertBidFile(): Copying %s to %s" % (o_file_name, bid_file_path))
    shutil.copy(o_file_name, bid_file_path)
    Errlog.log("Bids.convertBidFile(): Removing %s" % o_file_name)
    os.remove(o_file_name)

def installBids(bid_file_name, period):
    """
    Administrator script that takes as argument a bid file and a period
    expressed as the first date in the bid period (pp_start), creates the
    corresponding bid rudobs and create soft links to the default bid and
    bid rudob tables. The script expects the bid file to be place in
    $CARMDATA/ETABLES/rave:bid.%bids_path%

    It is intended for execution from the command line and will exit the
    studio process when it is done
    """
    Errlog.log("Bids.installBids(): Installing bids")

    # Load rule set, any Rostering rule set will do
    Cui.CuiCrcLoadRuleset(Cui.gpc_info, "Rostering_FC")
    # Set pp_start so that Rave evaluations are correct
    Cui.CuiCrcSetParameterFromString("fundamental.start_para", period)

    # Get paths to common bid and bid_rudob directories from Rave
    rave_bids_path, = R.eval('default_context', 'bid.%bids_path%')
    rave_rudob_path, = R.eval('default_context', 'bid.%rudob_path%')
    common_path = os.path.expandvars("$CARMDATA/ETABLES/")
    common_bid_path = os.path.join(common_path, rave_bids_path)
    common_rudob_path = os.path.join(common_path, rave_rudob_path)

    # Path to bid file
    bid_file_path = os.path.join(common_bid_path, bid_file_name)
    Errlog.log("Bids.installBids(): Bid file is %s" % bid_file_path)
    # Verify that bid file exists
    if not os.path.exists(bid_file_path):
        Errlog.log("Bids.installBids(): Bid file %s not found, exiting" % bid_file_path)
        sys.exit()

    # Verify that the bid file can be read with Etab
    try:
        sanity_read = Etab.Etable(bid_file_path)
    except:
        Errlog.log("Bids.installBids(): Bid file %s is corrupt, exiting" % bid_file_path)
        os.rename(bid_file_path, bid_file_path + '.corrupt-' + datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        try:
            os.rename(bid_file_path + '.old', bid_file_path)
        except:
            Errlog.log("Bids.installBids(): No old file to revert to (%s)" % bid_file_path + '.old')
        sys.exit()

    # Set up rudob file path based on bid file path
    rudob_file_name = bid_file_name + "_rudobs"
    rudob_file_path = os.path.join(common_rudob_path,
                                   rudob_file_name)#bid_file_name + "_rudobs")
    Errlog.log("Bids.installBids(): Rudob file is %s" % rudob_file_path)

    # Symlink paths
    link_file_name = '_'.join(bid_file_name.split('_')[0:-1])
    bid_sym_link_path = os.path.join(common_bid_path, link_file_name)

    Errlog.log("Bids.installBids(): Bids table for rave is %s" % link_file_name)
    Cui.CuiCrcSetParameterFromString("bid.table_para", link_file_name)

    # Convert the bid file header and crew id format
    convertBidFile(bid_file_path, 'tmp_' + link_file_name)

    # Set up soft link to bid file
    if os.path.lexists(bid_sym_link_path):
        os.remove(bid_sym_link_path)
    os.symlink(bid_file_name, bid_sym_link_path)

    # Done, exit the system
    Errlog.log("Bids.installBids(): Finished")
    sys.exit()



# End of file


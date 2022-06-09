#####################################################

# A module for creating annotations/messages for
# specific crew and for selecting crew
# with a specific annotation.
#
import modelserver as M
from carmusr.crewinfo.CrewInfoClasses import *
import StartTableEditor
import Cui
import Cfh
from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime
import Errlog
import utils.Names as Names
import Select
import carmusr.HelperFunctions as HF
from carmusr.tracking.CfhExtension import SpecialDate
import Gui
import carmstd.rave as R
import os
import re
import tempfile
import Select

# Set the following to true to get verbose messages in the
# error log.
debugOutput = 0

class Annotations:
    def __init__(self):
        # Collect information for detection of user and product
        self.username = Names.username()
        self.product = os.environ.get("PRODUCT")

        # Create and connect the table manager
        self.tm = M.TableManager.instance()

        # Load tables needed for annotations
        self.tm.loadTables(["annotation_set", "crew_annotations", "crew"])
        self.annotation_set = self.tm.table("annotation_set")
        self.crew_annotations = self.tm.table("crew_annotations")
        self.crew = self.tm.table("crew")

        # Variables for selection when displaying annotations for the user
        self.crewId = None
        self.crewEmpno = None
        self.form_id = self.tm.createUUID()

        # Information about the annotations saved to detect changes and to
        # generate keys for the different tables. 
        self.used_seq_nrs = None
        
        # All temporary tables are created inside a try-statement making sure
        # no error is generated if the table already exist.

        # Clear/set error message table
        self.validCode = ValidCode()
        # Creates a table used to store the different annotation codes
        try:
            self.tmp_ann_codes = self.tm.table("tmp_ann_codes")
        except: 
            self.tm.createTable("tmp_ann_codes",
                                [M.RefColumn("code", "annotation_set","Code")],
                                [M.StringColumn("descript", "Description"),
                                 M.BoolColumn("hasprop", "Has Property")])
            self.tmp_ann_codes = self.tm.table("tmp_ann_codes")

        # Creates a table used to store the annotations valid for the specific
        # selection
        self.tmp_annotation_table = self.createAnnotationTable("tmp_annotation_table")
        
        # Creates a table used to store static information used to display correct
        # information in the form
        try:
            self.tmp_ann_form_data = self.tm.table("tmp_ann_form_data")
        except: 
            self.tm.createTable("tmp_ann_form_data", [M.StringColumn("form_id", "")],
                                [M.StringColumn("username", ""),
                                 M.StringColumn("forminfo", ""),
                                 M.DateColumn("date","")])
            self.tmp_ann_form_data = self.tm.table("tmp_ann_form_data")

    def createAnnotationTable(self, tableName):
        """
        Function creating the temporary annotation table. This is the table
        visualized in the XML-form presented to the users.
        """
        try:
            return self.tm.table(tableName)
        except:
            self.tm.createTable(tableName,
                                [M.StringColumn("form_id", ""),
                                 M.IntColumn("rownr", "Sequence Number")],
                                [M.TimeColumn("entrytime", "Entry Date"), 
                                 M.RefColumn("code", "tmp_ann_codes", "Annotation Code"),
                                 M.IntColumn("property", "Property"),
                                 M.DateColumn("validfrom","Start Date"),
                                 M.DateColumn("validto", "End Date"),   
                                 M.StringColumn("text", "Annotation Text"),
                                 M.StringColumn("username", "User Name"),
                                 M.IntColumn("seqnr",""),
                                 M.BoolColumn("deleted","")])
        return self.tm.table(tableName)

    def rowForProduct(self, row):
        """
        Function testing if a row in the annotation_set table is for the used
        product.
        The product environment variable is set to 'Cct' for a tracking system
        and 'Cas' for a rostering system.
        """
        return (re.findall("(?i)^cct$",self.product) and row.incct) or \
               (re.findall("(?i)^cas$",self.product) and row.inccr)
    
    def getAnnotationCodes(self):
        """
        Copies crew annotation codes from the annotation_set table to the
        annotation code table.
        If the codes are relevant is decided from what product is running.
        """
        self.tmp_ann_codes.removeAll()
        now_time = getNowtimeAsInt()
        for row in self.annotation_set:
            valid_start = AbsDate(row.validfrom).getRep()
            valid_end = AbsDate(row.validto).getRep()
            if valid_start <= now_time and valid_end > now_time and \
                   self.rowForProduct(row) and row.forcrew:
                code_ref = self.annotation_set.getOrCreateRef((row.code,))
                record = self.tmp_ann_codes.create((code_ref,))
                record.descript = row.descript
                record.hasprop = row.hasprop
       
    def populate(self):
        """
        Resets the tables and populates them with the correct data,
        based on what is set to the crewId member.
        Only valid annotations are returned.
        """
        self.getAnnotationCodes()
        self.used_seq_nrs = []
        text_record = self.tmp_ann_form_data.create((self.form_id,))
        text_record.username = self.username
        text_record.date = AbsTime(AbsDate(getNowtimeAsInt()))
        crew_row = self.crew[(self.crewId,)]
        text_record.forminfo = crew_row.name + ", " + crew_row.forenames + \
                                 " (" + self.crewEmpno + ")"
        rows = self.crew_annotations.search("(crew.id=%s)" % self.crewId)
        now_time = getNowtimeAsInt()
        # Creates an empty row, making sure there is always one row in the table.
        # This is because the XML-form does not handle empty tables to well. 
        record = self.tmp_annotation_table.create((self.form_id, 0))
        record.deleted = True
        row_nr = 1
        for row in rows:
            try:
                tmpcode = self.tmp_ann_codes[(row.code,)]
            except:
                continue
            record = self.tmp_annotation_table.create((self.form_id, row_nr))
            row_nr += 1
            record.seqnr = row.seqnr
            self.used_seq_nrs.append(row.seqnr)
            record.entrytime = row.entrytime
            record.code = tmpcode
            record.text = row.text
            if record.code.code.hasprop:
                record.property = row.property
            else:
                record.property = -1
            record.validfrom = row.validfrom
            record.validto = row.validto - RelTime(24,0)
            record.username = row.username
            record.deleted = 0
            
    def getNewSeqNr(self):
        """
        Function used to create a new sequence number to store annotations with. 
        """
        for i in range(1,len(self.used_seq_nrs)+2):
            if  i in self.used_seq_nrs:
                continue 
            self.used_seq_nrs.append(i)
            return i
        return max(self.used_seq_nrs)+1

    def deleteRow(self, row, id):
        """
        Deletes the row from the annotations table.
        Returns True if the row was found and deleted, otherwise False.
        """
        try:
            row_to_delete = self.crew_annotations[(id, row.seqnr)]
        except:
            Errlog.log("ANNOTATIONS: deleteRow() could not find row " + str(row)
                       + " in crew annotations")
            return False
        row_to_delete.remove()
        Errlog.log("ANNOTATIONS: saveChanges() deleted row " + str(row))
        return True

    def testRowsForChange(self, row_tmp, row_real):
        """
        Test if tmp_row and real_row have equal values in the fields 'code', 'text',
        'validfrom', 'validto', 'property' and 'username'.
        """
        if row_tmp.username != row_real.username:
            return True
        if row_tmp.code.code.code != row_real.code.code:
            return True
        if  row_tmp.text != row_real.text:
            return True
        if row_tmp.property != row_real.property:
            return True
        # Since you can not compare an AbsTime with None the if-statements are a bit uggly. 
        if (row_real.validfrom and not row_tmp.validfrom) \
        or (row_tmp.validfrom and not row_real.validfrom) \
        or (row_tmp.validfrom != row_real.validfrom):
            return True
        tmp_validto = (row_tmp.validto and row_tmp.validto+RelTime(24,0)) or None
        if (row_real.validto and not tmp_validto) \
        or (tmp_validto and not row_real.validto) \
        or (tmp_validto != row_real.validto):
            return True
        return False
        
    def saveChanges(self):
        """
        Saves the changes made to the annotations. If no times are set in
        the validto and validfrom fields, a large time range is added.
        For a row to be saved an annotation code must be selected.
        The function returns True if any changes have been made.
        """
        # Fetch current time. This will be used as a key for new entries.
        now_time = getNowtimeAsInt()
        changes_done = False
        # Creates a reference to the correct crew, to be used when accessing
        # the real annotations tables.
        if self.crewId:
            id_ref = self.crew.getOrCreateRef((self.crewId,))
        # Adds changes to the annotations. Creates new entries or edits the old ones.
        for row in self.tmp_annotation_table.search("(form_id=%s)" %self.form_id):
            row_changed = False
            # If the row is marked for deletion, the row should be removed from
            # the annotations_tables saved in the database.
            if debugOutput:
                Errlog.log("ANNOTATIONS: saveChanges() working with row " + str(row))
            if row.deleted:
                changes_done |= self.deleteRow(row, id_ref)
                continue
            # The data is moved from the temporary tables to the real tables.
            if not row.seqnr:
                if row.code: 
                    row_changed = True
                    row.seqnr = self.getNewSeqNr()
                    if debugOutput:
                        Errlog.log("ANNOTATIONS: saveChanges() adds the new row with sequence number " \
                                   + str(row.seqnr))
                else:
                    if debugOutput:
                        Errlog.log("ANNOTATIONS: Row not saved, no code set in row " + str(row))
                        Errlog.log("Code: "+str(row.code))
                    continue
            # The record is fetched from the database table. If the the row_changed
            # variable is set, the row is new and a new record will be created. 
            if self.crewId:
                try: 
                    if row_changed:
                        record = self.crew_annotations.create((id_ref, row.seqnr))
                    else:
                        record = self.crew_annotations[(id_ref, row.seqnr)]
                except:
                    try:
                        record = self.crew_annotations[(id_ref, row.seqnr)]
                    except: 
                        record = self.crew_annotations.create((id_ref, row.seqnr))
            if not row_changed: 
                row_changed = self.testRowsForChange(row, record)
            changes_done |= row_changed
            # If the row is not changed, we continue to the next row
            if not row_changed:
                if debugOutput:
                    Errlog.log("ANNOTATIONS: row was not changed " +str(row)) 
                continue

            # If validfrom and/or validto are empty it is treated as if the period should
            # be for ever. Thus the times are set from 0 (1jan1986 0:00) to a large number
            # (31dec2029  0:00). This is because there are no AbsTime max and min variables. 
            if not row.validfrom:
                row.validfrom = AbsTime(AbsDate(0))
            if not row.validto:
                row.validto = AbsTime(AbsDate(23142240))
            # The info has been changed, sets all fields in record to the values in row
            record.code = self.annotation_set.getOrCreateRef((row.code.code.code,))
            record.isvisible = record.code.isvisible
            record.property = row.property
            record.validfrom = row.validfrom
            record.validto = row.validto + RelTime(24,0)
            record.text = row.text
            # Sets username to the current user and entrytime to the current time
            record.entrytime = AbsTime(now_time)
            record.username = self.username
            if debugOutput:
                Errlog.log("ANNOTATIONS: changes saved into annotations table "+str(record))
        if changes_done:
            Gui.GuiCallListener(Gui.ActionListener)
            if self.crewId:
                Cui.CuiReloadTable("crew_annotations", 1)
                HF.redrawAllAreas(Cui.CrewMode)
        return changes_done
    
    def cleanUp(self, uuid):
        """
        Removes the rows for the specific form_id from all the temporary tables
        """
        tmp_tables = [self.tmp_ann_form_data, self.tmp_annotation_table]
        for table in tmp_tables: 
            for row in table.search("(form_id=%s)" %uuid):
                row.remove()

def isValidCode(plan, form_id, form_code, prop_value):
    """
    Function used by the created XML-form to set the error message table.
    """
    global annot_forms
    annot_forms[form_id].validCode.checkValidCode(form_code, prop_value)

def saveChanges(plan, form_id):
    """
    Function used by the created XML-form to save changes to the tables. This is just a
    wrapper for the in the Annotations class built in save-function. 
    """
    global annot_forms
    annot_forms[form_id].saveChanges()
    cleanUp("", form_id)

def cleanUp(plan, form_id):
    """
    Function used by the created XML-form to clean up the temporary tables. This is just a
    wrapper for the in the Annotations class built in cleanUp-function. 
    """
    global annot_forms
    annot_forms[form_id].cleanUp(form_id)
    del annot_forms[form_id]

# Register functions to make it possible for the XML-form to access them. 
from utils.wave import LocalService, unicode_args_to_latin1 as u2l
class annotations_save_changes(LocalService): func = saveChanges
class annotations_clean_up(LocalService):     func = cleanUp
class annotations_valid_info(LocalService):   func = u2l(isValidCode)

def getNowtimeAsInt():
    """
    Function returning the current time, as set in the parameter
    fundamental.%now% in CARMUSR, as an integer.
    """
    return Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, "None", "fundamental.%now%")

global annot_forms

def startAnnotations(formname="Annotation"):
    """
    Opens a form for viewing and editing annotations. If a formname is given, that is what is
    set as name for the form when displayed to the user. Otherwise the form is named 'Annotations'.
    """
    # Creates a global instance of the form
    global annot_forms
    try:
        annot_forms == annot_forms
    except:
        annot_forms = {}
    annot_form = Annotations()
    annot_forms[annot_form.form_id] = annot_form
    
    annot_form.area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    annot_form.crewId = Cui.CuiCrcEvalString(
        Cui.gpc_info, Cui.CuiWhichArea, "object", "crr_crew_id")
    annot_form.crewEmpno = Cui.CuiCrcEvalString(
        Cui.gpc_info, Cui.CuiWhichArea, "object", "crew.%employee_number%")
    annot_form.populate()
    StartTableEditor.StartTableEditor(['-P', 'form_id=%s' %annot_form.form_id,
                                       '-P', 'form_name=%s' % formname,
                                       '-f', '$CARMUSR/data/form/annotations.xml'],
                                      "Annotations")
    
##################################################################
# Functions for setting the same annotation on all marked crew at
# the same time
#

class BatchAnnotations(Cfh.Box):
    def __init__(self, *args):
        Cfh.Box.__init__(self, *args)

        # Get tablemanager and load tables
        self.tm = M.TableManager.instance()
        self.tm.loadTables(["annotation_set", "crew_annotations", "crew"])
        self.annotation_set = self.tm.table("annotation_set")
        self.crew_annotations = self.tm.table("crew_annotations")
        self.crew = self.tm.table("crew")
        
        # Field for annotation code
        rows = self.annotation_set.search(
                   "(&(incct=true)(forcrew=true)(!(hasprop=true)))")
        maxlen = max((len(row.code) + 3 + len(row.descript)) for row in rows)
        self.ann_code = Cfh.String(self,"ANN_CODE",maxlen)
        self.ann_code.setMenuOnly(1)
        self.ann_code.setMandatory(True)

        # Field for descriptive text
        self.ann_text = Cfh.String(self,"ANN_TEXT",200)

        # Field for start date
        self.period_start = SpecialDate(self, "ANN_START")
        self.period_start.setMandatory(True)

        # Field for end date
        self.period_end = SpecialDate(self, "ANN_END")
        self.period_end.setMandatory(True)

        # OK and CANCEL buttons
        self.ok = Cfh.Done(self,"B_OK")
        self.quit = Cfh.Cancel(self,"B_CANCEL")

        # Creating the form
        form_layout = """
FORM;BATCH_ANNOTATION;Set Annotation on Marked Crew;
COLUMN;%s
FIELD;ANN_CODE;`Code:`
GROUP
COLUMN;50
FIELD;ANN_TEXT;`Text:`
FIELD;ANN_START;`Period Start:`
FIELD;ANN_END;`Period End:`

BUTTON;B_OK;`Ok`;`_Ok`
BUTTON;B_CANCEL;`Cancel`;`_Cancel`
""" % (maxlen/2 + 2)
        annot_form_file = tempfile.mktemp()
        f = open(annot_form_file,"w")
        f.write(form_layout)
        f.close()
        self.load(annot_form_file)
        os.unlink(annot_form_file)

    def getValues(self):
        """
        Function returning the values set in the form. 
        """
        anncode = self.ann_code.valof()
        try:
            anncode = anncode.split(' - ')[0]
        except:
            pass
        return (anncode,
                self.ann_text.valof(),
                self.period_start.valof(),
                self.period_end.valof())

    def setValues(self):
        """
        Set available codes in the menu and default date values in the
        form. The default period is the current day as defined by
        fundamental.%now%.
        """
        now = Cui.CuiCrcEval(Cui.gpc_info, Cui.CuiNoArea, "None", "fundamental.%now%")
        now = now.ddmonyyyy(True)
        # Note: "(!(hasprop=true))" -> false or null
        rows = self.annotation_set.search("(&(incct=true)(forcrew=true)"+
                                          "(!(hasprop=true))(validto>%s))" % now)
        codes = sorted(["%s - %s" % (row.code, row.descript) for row in rows])
        self.ann_code.setMenuString("Codes;" + ";".join(codes))
        self.period_start.assign(now)
        self.period_end.assign(now)

    def createSeqNr(self, crew_ref):
        """
        """
        rows = self.crew_annotations.search("(crew=%s)" % str(crew_ref))
        seq_nrs = []
        for row in rows:
            seq_nrs.append(row.seqnr)
        if len(seq_nrs) == 0:
            return 1
        for nr in range(1, len(seq_nrs)+2):
            if nr in seq_nrs:
                continue
            return nr
        return max(seq_nrs)+1

    def saveValues(self, code, text, start_date, end_date, area):
        """
        """
        context = R.Context("window", area)
        crew_ids = context.getCrewIdentifiers("marked_crew")
        for crew_id in crew_ids:
            Errlog.log("BATCH ANNOTATIONS: creating annotation for crew " + str(crew_id))
            crew_ref = self.crew.getOrCreateRef((crew_id,))
            seqnr = self.createSeqNr(crew_ref)
            row = self.crew_annotations.create((crew_ref, seqnr))
            row.code = self.annotation_set.getOrCreateRef((code,))
            row.isvisible = row.code.isvisible
            row.text = text
            row.validfrom = AbsTime(start_date)
            row.validto = AbsTime(end_date) + RelTime(24,0)
            row.property = -1
            row.username = Names.username()
            row.entrytime = Cui.CuiCrcEval(Cui.gpc_info, Cui.CuiNoArea, \
                                           "None", "fundamental.%now%")
        Cui.CuiReloadTable("crew_annotations", 1)
        HF.redrawAllAreas(Cui.CrewMode)

global batch_annot_form

def startBatchAnnotations(area=Cui.CuiWhichArea):
    """
    """
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, area)    
    global batch_annot_form
    try:
        batch_annot_form == batch_annot_form
    except:
        batch_annot_form = BatchAnnotations("batch_annot_form")
        Errlog.log("BATCH ANNOTATIONS: Annotations form created")
    batch_annot_form.setValues()
    batch_annot_form.show(1)
    if batch_annot_form.loop() == Cfh.CfhOk:
        (code, text, start, end) = batch_annot_form.getValues()
        print "SAVE",start,end,type(start),type(end)
        batch_annot_form.saveValues(code, text, start, end, area)
        Gui.GuiCallListener(Gui.ActionListener)


##################################################################
# Class and functions for selecting crew with specific annotations
#
    
class AnnotationSelection(Cfh.Box):
    def __init__(self, *args):
        Cfh.Box.__init__(self, *args)
        
        self.product = os.environ.get("PRODUCT")
        self.valid_codes = None
        # Field for annotation code
        self.select_code = Cfh.String(self,"ANN_CODE",6)
        self.select_code.setMenuOnly(1)
        self.select_code.setMandatory(True)
        # Field for start date
        self.period_start = Cfh.Date(self, "ANN_START")
        self.period_start.setMandatory(True)
        # Field for end date
        self.period_end = Cfh.Date(self, "ANN_END")
        self.period_end.setMandatory(True)
        # Field for selection filter method 
        self.selection_type = Cfh.String(self,"ANN_SELECTION",10,"ADD")
        self.selection_type.setMandatory(1)
        self.selection_type.setMenuOnly(1)
        # OK and CANCEL buttons
        self.ok = Cfh.Done(self,"B_OK")
        self.quit = Cfh.Cancel(self,"B_CANCEL")
        # Creating the form
        form_layout = """
FORM;ANNOTATION_FORM;Select Annotations;

FIELD;ANN_CODE;`Code:`
MENU;Filter Method;ADD;SUBSELECT;REPLACE
FIELD;ANN_SELECTION;`Selection:`;ADD

COLUMN
FIELD;ANN_START;`Period Start:`
FIELD;ANN_END;`Period End:`

BUTTON;B_OK;`Ok`;`_Ok`
BUTTON;B_CANCEL;`Cancel`;`_Cancel`
"""
        annot_form_file = tempfile.mktemp()
        f = open(annot_form_file,"w")
        f.write(form_layout)
        f.close()
        self.load(annot_form_file)
        os.unlink(annot_form_file)

    def getValues(self):
        """
        Function returning the values set in the form. 
        """
        return(self.select_code.valof(),
               self.period_start.valof(),
               self.period_end.valof(),
               self.selection_type.valof())

    def setValues(self):
        """
        Calculates the values to set in the select form, depending on product
        and what type of annotations the search is for. 
        """
        self.select_code.setMenuString(self.valid_codes)
        if re.findall("(?i)^cct$",self.product):
            p_start = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, \
                                            "None", "fundamental.%now%")
            p_end = p_start
        elif re.findall("(?i)^cas$",self.product):
            p_start = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, \
                                            "None", "fundamental.%pp_start%")
            p_end = Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea, \
                                          "None", "fundamental.%pp_end%")
        self.period_start.assign(p_start)
        self.period_end.assign(p_end)

global annot_select_form

def selectAnnotations(area=Cui.CuiWhichArea):
    """
    Creates a select form and set default values, depending on the product.
    """
    global annot_select_form
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, area)
    try:
        annot_select_form == annot_select_form
    except:
        annot_select_form = AnnotationSelection("annot_select_form")
        Errlog.log("ANNOTATIONS: Selection form created")

    select_codes = []
    if HF.isDBPlan():
        tm = M.TableManager.instance()
        tm.loadTables(["annotation_set"])
        annotation_set = tm.table("annotation_set")
        forproductcolumn = ("in"+annot_select_form.product).lower()
        if forproductcolumn == "incas":
            forproductcolumn = "inccr"
        rows = annotation_set.search("(&(%s=true)(forcrew=true))" \
                                     %(forproductcolumn))
        for row in rows:
            select_codes.append(row.code)
    else:
        # When running on file-plans we can only use the hard-coded list
        select_codes = ["FX","NS","RC","JN","FQ","SW","IE","OL","J4","--"]
    
    if select_codes:
        # Add the "*" search option to be able to search for all crew with
        # any annotation set.
        select_codes.append("*")
        annot_select_form.valid_codes = "Codes;"+";".join(sorted(select_codes))
        Errlog.log("ANNOTATIONS: Codes collected from table and sent to the form")
        annot_select_form.setValues()
        annot_select_form.show(1)
    else:
        Errlog.log("ANNOTATIONS: There where no Annotation Codes available. No form is displayed.")
        Errlog.set_user_message("There are no Annotation Codes available.")
        return
    if annot_select_form.loop() == Cfh.CfhOk:
        (code, period_start, period_end, filter_method) = annot_select_form.getValues()
        period_end = AbsTime(period_end)
        period_start = AbsTime(period_start)

        # Check for database-plan
        if HF.isDBPlan():
            tm.loadTables(["crew_annotations", "crew"])
            annotations = tm.table("crew_annotations")

            crew_to_show = []

            rows = annotations.search("(&(code.code=%s)(validfrom<=%s)(validto>%s)(code.%s=true))"  \
                                      %(code, period_end.yyyymmdd(), period_start.yyyymmdd(),forproductcolumn))
            Errlog.log("ANNOTATIONS: The valid annotations have been collected from the table.")
            for row in rows:
                try:
                    if crew_to_show.count(row.crew.id) > 0:
                        continue                        
                    crew_to_show.append(row.crew.id)
                except modelserver.ReferenceError:
                    pass

            if filter_method == "ADD":
                crew_in_window = Cui.CuiGetCrew(Cui.gpc_info, area, "window")
                for crew in crew_to_show:
                    if crew in crew_in_window:
                        crew_in_window.remove(crew)
                crew_to_show.extend(crew_in_window)
            elif filter_method == "SUBSELECT":
                crew_in_win = Cui.CuiGetCrew(Cui.gpc_info, area, "window")
                crew_to_show = [crew for crew in crew_to_show if crew in crew_in_win]
            Cui.CuiDisplayGivenObjects(Cui.gpc_info, area, Cui.CrewMode, Cui.CrewMode, crew_to_show)
        else:
            # We are selecting in file-based plans
            print period_start.yyyymmdd()
            print period_end.yyyymmdd()
            dt = {'studio_select.csl_string_1':code,
                  'studio_select.csl_abstime_1':str(period_start), \
                  'studio_select.csl_abstime_2':str(period_end)}
            print dt
            Select.selectParam({'FILTER_METHOD':filter_method, 'studio_select.crew_has_annotation_in_period':'true', \
                                'planning_area.crew_is_in_planning_area':'true'}, \
                                {'studio_select.csl_string_1':code,
                                 'studio_select.csl_abstime_1':str(period_start), \
                                 'studio_select.csl_abstime_2':str(period_end)}, area, Cui.CrewMode)  
            
        # Zooms the window to the selected period plus one day before and one day after. 
        Cui.CuiZoomTo(Cui.gpc_info, area, period_start.getRep() - 60*24, period_end.getRep() + 60*48)
        HF.redrawAreaScrollHome(area)

class ValidCode(CrewInfoTempTable):
    """
    Class to validate the annotation code.
    """

    def __init__(self):
        tableName = "tmp_ann_valid_info"
        cols = [M.BoolColumn("err_status", "err_status")]
        CrewInfoTempTable.__init__(self, tableName, cols)
        self.populateTab(0)
        
        tm = M.TableManager.instance()
        tm.loadTables(["annotation_set"])
        self.annotation_set = tm.table("annotation_set")

    def populateTab(self,idx):
        self.clear()
        row = self.create((idx,))
        row.err_status = False        

    def checkValidCode(self,code="", prop=0):
        tm = M.TableManager.instance()
        tm.loadTables(["annotation_set"])
        found = True
        try:
            self.annotation_set[(code,)]
            if code == 'ST' and int(prop) < 0:
                found = False
        except:
            found = False

        for rec in self:
            rec.err_status = found
            break
      

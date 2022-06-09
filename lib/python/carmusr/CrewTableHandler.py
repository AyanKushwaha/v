#####################################################

#
# CrewTableHandler:: Module for functions related to updating various crew tables
#
# (Rewrite of the TrainingLogHandler module)
#
# Created by: Erik Gustafsson 2008-04-14
#
# Sections:
# 1. crew_training_log
# 2. crew_document
# 3. lifetime_block_hours

import Cui
import Gui
import Errlog
import carmensystems.rave.api as R
import traceback
import HelperFunctions as HF
import carmusr.modcrew as modcrew
import utils.time_util as time_util
import time
import AbsTime
import RelTime
import re
import Attributes
import application
import datetime
import adhoc.fixrunner as fixrunner
import carmusr.AuditTrail2

from carmusr.VirtualQualification import real_to_virtual_qual
from operator import itemgetter

### This functionality only works while on DB-plans
try:
    import modelserver
    from tm import TM
    from modelserver import EntityError, ReferenceError, EntityNotFoundError
    from utils.TimeServerUtils import now
except:
    # This handles when the script is called when product=cas and
    # modelserver isn't available
    pass

MODULE = "CrewTableHandler:: "
DOCUMENT_BLACKLIST = ['LC', 'PC', 'PCA3', 'PCA3A5', 'PCA4','PCA5','OPC', 'OPCA3', 'OPCA3A5', 'OPCA4','OPCA5', 'CRM', 'CRMC']

########################################################################
#
# Section 1: Functions related to updating crew_training_log
#
########################################################################

def update_ctl_changed_crew():
    """
    Function to update crew_training_log only for crew that has been changed.
    Will be called at Save in Studio.
    """
    crew_list = modcrew.get()
    if crew_list:
        Errlog.log(MODULE + "update_ctl_changed_crew:: Updating modified crew")
        update_ctl(crew_list)
    else:
        Errlog.log(MODULE + "update_ctl_changed_crew:: No changed crew")


def update_ctl_all_crew():
    """
    Function to update  crew_training_log and crew_training_need for all
    loaded crew.
    To be called automatically by nightjob.
    """
    

    crew_list = _get_crew_list_from_rave()
    Errlog.log(MODULE + "update_ctl_all_crew:: Updating all crew in plan")

    change_log_ctl = []
    change_log_courses = []

    ppstart = Cui.CuiCrcEval(Cui.gpc_info, Cui.CuiArea0, "object", "fundamental.%plan_start%")
    ppend   = Cui.CuiCrcEval(Cui.gpc_info, Cui.CuiArea0, "object", "fundamental.%plan_end%")

    Errlog.log(MODULE + "Will update CTL for period %s - %s" % (str(ppstart), str(ppend)))

    #Since we are doing it for all loaded crew, fetch and cache all training log entries
    crew_cache = {}
    for entry in TM.crew_training_log.search("(&(tim>=%s)(tim<%s))" %(ppstart, ppend)):
        try:
            crew_cache[str(entry.crew.id)].append(entry)
        except KeyError:
            crew_cache[str(entry.crew.id)] = [entry]
        except:
            continue
            
    change_log_ctl = update_ctl(crew_list, crew_cache)

    # Check if any flight need for course blocks was met:
    try:
        change_log_courses = update_completed_courses(crew_list)
    except Exception, err:
        Errlog.log(MODULE + \
                   "update_ctl_all_crew: "+"Error updating courses:%s"%err)
        
    change_log = change_log_ctl
    change_log += change_log_courses
    if change_log:
        if not application.isServer:
            Gui.GuiMessage("\n".join(change_log))
        else:
            for log in change_log:
                Errlog.log(MODULE + "update_ctl_all_crew: "+log)

def update_ctl(crew_list, crew_cache = None):
    """
    This function updates the crew_training_log table for the given crew.
    """
    FUNCTION = MODULE + "update_ctl:: "
    try:
        assert HF.isDBPlan()
    except:
        Errlog.log(FUNCTION + "Only available in database plans")
            
    Errlog.log(FUNCTION + "Updating %s crew" %len(crew_list))
    
    verbose, = R.eval('fundamental.%debug_verbose_mode%')
    no_change, = R.eval('fundamental.%debug_no_change_mode%')

    output = _update_ctl(crew_list, verbose=verbose, no_change=no_change, crew_cache = crew_cache)
    
    (reload, changed_crew, added_rows, removed_rows, change_log) = output
    
    if reload:
        Errlog.log(FUNCTION + "%s changed crew, %s/%s added/removed rows"
                   %(changed_crew, added_rows, removed_rows))
    Errlog.log(FUNCTION + "Done")
    return change_log

def _update_ctl(crew_list, verbose=False, no_change=False, crew_cache = None):
    verbose=True
    FUNCTION = MODULE + "_update_ctl:: "
    reload = False
    changed_crew = 0
    added_rows = 0
    removed_rows = 0
    loggable_expr = R.foreach(
        R.iter("iterators.leg_set",
               where = 'training_log.%leg_is_valid%',),
        'leg.%start_utc%',
        'training_log.%leg_type%',
        'training_log.%leg_type2%',
        'training_log.%leg_code%',
        'training_log.%leg_attr%'
        )
    ppstart = Cui.CuiCrcEval(Cui.gpc_info, Cui.CuiArea0, "object",
                             "fundamental.%plan_start%")
    ppend = Cui.CuiCrcEval(Cui.gpc_info, Cui.CuiArea0, "object",
                           "fundamental.%plan_end%")
    eval_area = Cui.CuiScriptBuffer
    Cui.CuiDisplayGivenObjects(Cui.gpc_info,
                               eval_area,
                               Cui.CrewMode,
                               Cui.CrewMode,
                               crew_list,
                               0)
    
    start_time = time.time()
    crew_change_log = []
    for crew_id in crew_list:
        try:
            crew = TM.crew[(crew_id,)]
        except EntityError, err:
            Errlog.log(FUNCTION + "Exception: %s"%err)
            continue
        if verbose:
            Errlog.log(FUNCTION + "Crew id %s will be updated" %crew_id)
            
        crew_object = HF.CrewObject(crew_id, eval_area)
        crew_is_changed = False

        # Build temp table with all ctl for crew in plan_start > plan_end
        if crew_cache:
            try:
                existing_rows = crew_cache[str(crew_id)]
                if verbose:
                    print "Using crew_cache"
            except KeyError:
                if verbose:
                    print "Not found in crew_cache, returning empty list"
                existing_rows = []
        else:
            existing_rows = []
            for row in crew.referers('crew_training_log', 'crew'):
                if row.tim >= ppstart and row.tim < ppend:
                    existing_rows.append(row)
                            
        # Find ALL ctl activities on roster
        loggable_items, = crew_object.eval(loggable_expr)

        # Loop through roster activities and check rows in temp table
        for (ix, tim, type, type2, code, attr) in loggable_items:
            for typ in (type, type2):
                if typ:
                    if verbose:
                        print typ, code, tim, attr
                    exists = False
                    # Check if it exists
                    for row in existing_rows:
                        try:
                            rtyp = row.typ.typ
                            rcode = row.code
                            rtim = row.tim
                            rattr = row.attr
                            if (rtim == tim and rcode == code and rtyp == typ):
                                # The key is the same
                                exists = True
                                existing_rows.remove(row)
                                if verbose:
                                    print "Found row, removing from temp"
                                if (rattr == attr or (not rattr and not attr)):
                                    # The attr is the same, nothing happens
                                    pass
                                else:
                                    # The attr has changed, we need to create
                                    # the row
                                    exists = False
                                break
                        except ReferenceError:
                            # This means row.typ.typ failed and we have old data
                            continue
                    # The row didn't exist, we create it
                    if not exists:
                        try:
                            _create_ctl(crew, typ, code, tim, attr, verbose)
                            crew_is_changed = True
                            added_rows += 1
                        except:
                            Errlog.log(" ERROR: Skipped ctl row %s, %s, %s, %s" %(crew_id, typ, tim, code))
                            traceback.print_exc()


        # Loop through temp table and remove all unmarked rows    
        for row in existing_rows:
            rcrew = row.crew
            crewid = row.crew.id
            rtyp = row.getRefI("typ")
            rcode = row.code
            rtim = row.tim
            key = (rcrew, rtyp, rcode, rtim)
            entry = TM.crew_training_log[key]
            if verbose:
                Errlog.log(FUNCTION + \
                           "%s, %s, %s, %s removed" %(crewid, rtyp, rcode, rtim))
            print "#"*80
            print "removing ctl row for ", str(crewid)
            print "code:", str(rcode)
            print "tim:", str(rtim)
            print "#"*80
                                
            entry.remove()
            crew_is_changed = True
            removed_rows += 1
        if crew_is_changed:
            changed_crew += 1
                
    if changed_crew > 0:
        reload = True
        Cui.CuiReloadTable("crew_training_log", 1)
    exec_time = time.time() - start_time
    Errlog.log(FUNCTION + "Finished in %.2f s" %exec_time)
    return (reload, changed_crew, added_rows, removed_rows, crew_change_log)


def _create_ctl(crew_ref, type, code, tim, attr, verbose=False):
    typ = TM.training_log_set[(type,)]
    key = (crew_ref, typ, code, tim)
    try:
        entry = TM.crew_training_log.create(key)
    except EntityError:
        entry = TM.crew_training_log[key]
    entry.attr = attr
    if verbose:
        Errlog.log("CrewTableHandler::_create_ctl: %s, %s, %s, %s, %s created" %(crew_ref.id, type, code, tim, attr))
    

########################################################################
#
# Section 2: Functions related to updating crew_document
#
########################################################################

def _get_rec_crew(context, today):
    crew, = R.eval(context,
                   R.foreach(R.iter('iterators.roster_set',
                                    where='training_log.%%crew_has_planned_recurrent%%(%s)' %today),
                             'crew.%id%',
                             'report_common.%crew_string%'))
    return crew

def _merge_outlist(rec_docs_for_period):
    """
    Merge list of lists of crew/updated documents to one list.
    """

    # First generate a dict containing lists of updated recurrent documents, with crew id/name tuple as key
    rec_doc_dict = {}
    for rec_docs_for_day in rec_docs_for_period:
        for (crew_id, crew_name, rec_doc_list) in rec_docs_for_day:
            if (crew_id, crew_name) in rec_doc_dict:
                rec_doc_dict[(crew_id, crew_name)] = rec_doc_dict[(crew_id, crew_name)] + rec_doc_list
            else:
                rec_doc_dict[(crew_id, crew_name)] = rec_doc_list

    # Then transform the dict into a list for crew id/name/recurrent documents tuples, sorted by crew name
    merged_list = []
    crew_list = sorted(rec_doc_dict, key=itemgetter(1)) # Sort crew by name
    for (crew_id, crew_name) in crew_list:
        merged_list.append((crew_id, crew_name, rec_doc_dict[(crew_id, crew_name)]))

    return merged_list
    
def update_rec(today=None, scope='ALL', area=None, extraction_date=None):
    """
    Function to update documents for crew.

    To be called by automatically by nightjob, with 'scope' set to 'ALL'
    Can also be called with 'scope' set to 'WINDOW' to simulate update.
    """
    FUNCTION = MODULE + "update_rec:: "
    try:
        assert HF.isDBPlan()
    except AssertionError, ex:
        # traceback.print_exc()
        Errlog.log(FUNCTION + "Only available in database plans")
        raise
    if today is None:
        today, = R.eval('fundamental.%now%')

    if extraction_date is not None:
        # Will only tag performed
        only_tag = True
    else:
        only_tag = False

    if scope == 'ALL':
        if only_tag:
            Errlog.log(FUNCTION + "Tagging legs before %s performed, updating legs between %s and %s" %(extraction_date, extraction_date, today))
        else:
            Errlog.log(FUNCTION + "Updating all crew in plan until %s" %today)
        context = 'sp_crew'
        update_table = True
    elif scope == 'WINDOW':
        Errlog.log(FUNCTION + "Simulating update of all crew in window until %s" %today)
        context = 'default_context'
        update_table = False
    else:
        raise ValueError, "Function called with illegal argument"

    crew = _get_rec_crew(context, today)

    if not update_table:
        TM.newState()

    acc_to, = R.eval('default_context', 'fundamental.%pp_start%')
    outlist = []
    while acc_to < today:
        acc_to = acc_to.adddays(1)
        contrib = _update_rec(crew, context, area, acc_to, extraction_date)
        outlist.append(contrib)

    if not update_table:
        TM.undo()
        Cui.CuiReloadTable("crew_document", 1)
        _reload_attr_tables()

    Errlog.log(FUNCTION + "Finished")
    if not update_table:
        output = _merge_outlist(outlist)
        return output
    else:
        _reload_attr_tables()
        return 0


def _update_rec(crew, context, area, today, extraction_date):
    verbose, = R.eval('fundamental.%debug_verbose_mode%')
    crew_list = []
    for (ix, crew_id, cs) in crew:
        crew_list.append(crew_id)
    if area is None:
        # We're called by nightjob, so let's put crew in script buffer
        area = Cui.CuiScriptBuffer
        Cui.CuiDisplayGivenObjects(Cui.gpc_info,
                                   area,
                                   Cui.CrewMode,
                                   Cui.CrewMode,
                                   crew_list,
                                   0)
    reload = False
    output = []
    for (ix, crew_id, crew_string) in crew:
        rec_rows = _update_rec_one_crew(crew_id, area, today, verbose, extraction_date)
        if rec_rows:
            reload = True
            output.append((crew_id, crew_string, rec_rows))
    if reload:
        Cui.CuiReloadTable("crew_document", 1)
        _reload_attr_tables()
    return output

def update_rec_test(crew_id):
    print "CrewTableHandler test of ",crew_id
    pp_end, = R.eval('default_context', 'fundamental.%pp_end%')
    _update_rec_one_crew(crew_id, Cui.CuiArea0, pp_end, True, None)
    _reload_attr_tables()
    
def _update_rec_one_crew(crew_id, area, today, verbose, extraction_date):
    crew = TM.crew[(crew_id,)]
    if verbose:
        Errlog.log("Crewid %s will be checked for update" %crew_id)
        # _disp_documents(crew_id)
    crew_object = HF.CrewObject(crew_id, area)
    rec_expr = R.foreach(
        R.iter("iterators.leg_set",
               sort_by = 'leg.%start_utc%',
               where = ('training_log.%%leg_extends_any_recurrent_doc%%(%s)' % str(today),
            'training_log.%%rec_docs_updated_by_leg%%(%s) > 0' % str(today),
                        'leg.%%end_date%% + 48:00 < %s' % str(today))),
        # These values are keys in the attr tables
        'training_log.%rec_leg_type%',
        'training_log.%rec_leg_time%',
        'training_log.%rec_leg_code%',
        'leg.%start_station%',
        # These values are needed for display purposes
        'training_log.%leg_date%',
        'training_log.%leg_code%',
        'leg.%start_utc%',
        #R.foreach(R.times('training_log.%%rec_docs_updated_by_leg%%(%s)' % str(today)),
        R.foreach(R.times(4),
                  'training_log.%leg_doc_ix%',
                  'training_log.%leg_doc_validto_ix%',
                  'training_log.%leg_doc_acqual_ix%',
                  'training_log.%leg_doc_init_ix%'))

    rec_activities, = crew_object.eval(rec_expr)

    rec_rows = []
    if verbose:
        print "activities: ", len(rec_activities)
    for (ix, leg_type, leg_time, leg_code, adep, leg_date, code, start_utc, docs) in rec_activities:
        leg_key = (crew_id, leg_type, leg_time, leg_code, adep)
        if docs:
            rec_rows.append("%s, %s" %(start_utc, code))
            main_doc = False
            #If this is a document that is updated from TPMS
            #we continue to the next activity without doing anything
            for (jx, doc, validto, ac_qual, init) in docs:
                if doc in DOCUMENT_BLACKLIST:
                     if verbose: 
                         print "TPMS Blacklisted: ", doc, crew_id, leg_time
                     continue
                if verbose:
                    print "doc", doc, validto, ac_qual, init
                if not validto is None:
                    try:
                        if not main_doc:
                            main_doc = doc
                        if extraction_date is None or extraction_date <= leg_date:
                            # In installation mode extraction date will have a value
                            # and we will only tag legs performed before this date
                            # TODO: Remove this if else statment after TPMS import has been activated (SKCMS-1194)
                            # TODO: and make sure that only _extend_doc_with_tpms_import_activated is being called
                            # TODO: What should be done as part of SKCMS-1194
                            # TODO: 1. Replace the if else so only _extend_doc_with_tpms_import_activated is used
                            # TODO: 2. Remove _extend_doc since it should not be used
                            # TODO: 3. Rename _extend_doc_with_tpms_import_activated to _extend_doc
                            # TODO: 4. Also, in module training_log, code can be removed so leg_doc_ix etc don't match REC affecting legs. 
                            #          until then an agreement validity will set 'validto' to void, hindering updates of crew_document the wrong way, but the crew_ground_duty_attributes (unneeded) will still be active for the legs.
                            if verbose:
                                print "calling _extend_doc"
                            if True:
                                result = _extend_doc(crew, leg_date, doc, validto, ac_qual, init, verbose)
                            else:
                                result = _extend_doc_with_tpms_import_activated(crew, leg_date, doc, validto, ac_qual, init, verbose)
                            rec_rows.append(result)
                            if verbose:
                                Errlog.log(" " + result)
                    except:
                        traceback.print_exc()
                        Errlog.log(" Skipped document %s, %s, %s" % (crew_id, doc, validto))
                        continue
            _tag_leg_performed(leg_key, main_doc)
    return rec_rows


def _extend_doc(crew_ref, validfrom, doc, validto, ac_qual, init, verbose):
    # TODO: This function should be removed when TPMS import has been activated (SKCMS-1194) and be replaced
    # TODO: with the function _extend_doc_with_tpms_import_activated
    if doc == 'Temp PC':
        print "_extend_doc, 'Temp PC'"
        doc_ref = TM.crew_document_set[("LICENCE", doc)]
    else:
        print "_extend_doc, 'REC'"
        doc_ref = TM.crew_document_set[("REC", doc)]

    # Find existing document
    rec_doc = None
    for entry in TM.crew_document.search(
        "(&(crew.id=%s)(doc.typ=REC)(doc.subtype=%s)(validfrom<=%s))" %(crew_ref.id, doc, validfrom)):
        if rec_doc is None or entry.validto > rec_doc.validto:
            rec_doc = entry

            

    if rec_doc is None:
        cur_validto = AbsTime.AbsTime("1Jan1986")
        cur_acqual = ""
    else:
        cur_validto = rec_doc.validto
        cur_acqual = rec_doc.ac_qual

    #ac_qual on non ac specific docs is None
    #while the ac_qual argument is ""
    cur_acqual_comp = cur_acqual if cur_acqual else ""
    validfrom_str = validfrom.ddmonyyyy(True)
    validto_str = validto.ddmonyyyy(True)
    create = False
    replace = False
    extend = False
    if (cur_validto < validfrom):
        # Document didn't exist or had expired
        action = "Will try to create %s, valid from: %s, " %(doc, validfrom_str)
        create = True

    elif (init and cur_acqual_comp != ac_qual):
        # Valid document exists, but changes acqual
        action = "Replaced %s, valid from: %s, " %(doc, validfrom_str)
        replace = True

    elif rec_doc:
        # Valid document
        action = "Extended %s: " %doc
        extend = True
    else:
        Errlog.log("%s %s %s: Invalid assignment, no action" %(crew_ref.id, doc, validfrom))
        return "Invalid assignment, no action"

    output = action + "valid to: %s, acqual: %s" %(validto_str, ac_qual)
    print output
    new_key = (crew_ref, doc_ref, validfrom)
    if replace:
        rec_doc.validto = validfrom
    if create or replace:
        if doc == 'Temp PC':

            document_exists = False
            for _ in TM.crew_document.search(
                    "(&(crew.id=%s)(doc.typ=LICENCE)(doc.subtype=Temp PC)(validfrom=%s))" %(crew_ref.id, validfrom)):
                document_exists = True

            if document_exists:
                print "Temp PC document already existed, will not create a new one."
            else:
                # Check if record has previously existed,
                # in that case it must have been deleted since it wasn't found in the previous search.
                previous_document_found = carmusr.AuditTrail2.AuditTrail2().search(
                    'crew_document', {'crew': crew_ref.id,
                                      'doc_typ': 'LICENCE',
                                      'doc_subtype': 'Temp PC',
                                      'validfrom': int(validfrom)})
                if previous_document_found:
                    print "Document has been removed previously and will not be recreated."
                else:
                    # Record has not been deleted previously and can be created
                    rec_doc = TM.crew_document.create(new_key)
                    print "Created new Temp PC document for crew: ", crew_ref.id, new_key

        else:
            #Document not of type Temp PC
            rec_doc = TM.crew_document.create(new_key)   
            print "Created new document ", new_key
        
    if not rec_doc is None:
        rec_doc.validto = validto
        rec_doc.ac_qual = ac_qual
    return output
                        
                        
                        
def _extend_doc_with_tpms_import_activated(crew_ref, validfrom, doc, validto, ac_qual, init, verbose):
    # TODO: This function should be used instead of _extend_doc when TPMS import has been activated (SKCMS-1194)
    if doc != 'Temp PC':
        return "REC will by ignored by default, none Temp PC will not be accepted. Ignoring %s" % doc

    validfrom_str = validfrom.ddmonyyyy(True)
    validto_str = validto.ddmonyyyy(True)

    new_key = (crew_ref, TM.crew_document_set[("LICENCE", doc)], validfrom)
    rec_doc = TM.crew_document.create(new_key)
    rec_doc.validto = validto
    rec_doc.ac_qual = ac_qual if ac_qual else ""

    action = "Created %s, valid from: %s, " % (doc, validfrom_str)
    output = action + "valid to: %s, acqual: %s" % (validto_str, ac_qual)
    return output


def _tag_leg_performed(leg_key, main_doc):
    """
    This function is used to primarily to tag a leg so that CMS knows it has
    updated a document (by having the RECURRENT attribute).
    It also sets a value to indicate which document was primarily updated
    (typically PC if more than one).
    """
    (crew_id, leg_type, leg_time, leg_code, adep) = leg_key
    attr_vals = {"str":main_doc}
    if leg_type == "FD":
        Attributes.SetCrewFlightDutyAttr(crew_id, leg_time, leg_code, adep,
                                         "RECURRENT", refresh=False,
                                         **attr_vals)
    elif leg_type == "GD":
        Attributes.SetCrewGroundDutyAttr(crew_id, leg_time, leg_code,
                                         "RECURRENT", refresh=False,
                                         **attr_vals)
    elif leg_type == "ACT":
        Attributes.SetCrewActivityAttr(crew_id, leg_time, leg_code,
                                       "RECURRENT", refresh=False,
                                       **attr_vals)
    else:
        Errlog.log("Tagging recurrent performed failed, unknowd leg type", main_doc, leg_key)
        
        
def _reload_attr_tables():
    Attributes._refresh("crew_flight_duty_attr")
    Attributes._refresh("crew_ground_duty_attr")
    Attributes._refresh("crew_activity_attr")
    
def _disp_documents(crew_id):
    print "crew_document (REC only) for crew %s" %crew_id
    for entry in TM.crew_document.search(
        "(&(crew.id=%s)(doc.typ=REC))" %crew_id):
        print entry
        
def _get_crew_list_from_rave():
    """
    Rave-iter through context sp_crew and return  crew_ids
    """
    crew, = R.eval("sp_crew",
                   R.foreach(R.iter('iterators.roster_set'),
                                    # Old comment: Select only crew with valid emp
                             'crew.%id%'))
    return [crew_id for (ix,crew_id) in crew]


########################################################################
#
# Section 3: Functions related to updating attributes tables
#
########################################################################

def clean_attributes_tables(crew_list=None, dnp_period_dict=None):
    """
    Removes attributes for activity that has been removed.
    Attributes are not automatically removed by carmsys.
    This function is normally called as part of a Studio pre-save operation.
    """
    
    # dnp_period_dict: Contains per-crew lists of periods that are marked
    #   as do-not-publish in Studio. Attributes related to activity that has 
    #     been removed within a dnp-period must NOT be removed.
    #   The reason for this is that the activity still remains in the PUBLISHED
    #     roster revision. Attributes are not related to a specific roster
    #     revision, so the attribute must remain for PUBLISHED mode lookup.
    #   Dnp_period_dict is typically specified at Tracking-Studio-Save only,
    #     where the contents are set by carmusr.tracking.Publish::publishPreSave
    
    verbose, = R.eval('fundamental.%debug_verbose_mode%')
    if not crew_list:
        crew_list = modcrew.get()
    tables = {"cfd":["crew_flight_duty_attr",-1,0,0],
              "cgd":["crew_ground_duty_attr",-1,0,0],
              "ca": ["crew_activity_attr",-2,0,0],
              "leg":["flight_leg_attr",None,0,0],
              "task":["ground_task_attr",-1,0,0]}
    Cui.CuiSyncModels(Cui.gpc_info)
    # For each table, check each reference
    for key in tables:
        crewid_ix = tables[key][1]
        for row in TM.table(tables[key][0]):
            try:
                row.getRef(key)
            except ReferenceError:
                if verbose:
                    Errlog.log('Found unused row: %s' % row)
                safetoremove = True
                if crewid_ix and dnp_period_dict:
                    keyitems = str(row.getRefI(key)).split("+")
                    st = AbsTime.AbsTime(keyitems[0])
                    crewid = keyitems[crewid_ix]
                    for pst,pen in dnp_period_dict.get(crewid, []):
                        if pst <= st < pen:
                            if verbose:
                                Errlog.log('  NOT removed: do-not-publish')
                            safetoremove = False
                            break
                if safetoremove:
                    row.remove()
                    tables[key][2] += 1
                else:
                    tables[key][3] += 1
    # crew rest is not normal attr
    tables['crew_rest'] = ['crew_rest',None,0,0]
    for crew_id in crew_list:
        for row in TM.crew[(crew_id,)].referers("crew_rest","crew"):
            try:
                TM.crew_flight_duty[(row.flight,row.crew)]
            except (EntityNotFoundError,ReferenceError):
                if verbose:
                    Errlog.log('Found unused row: %s' % row)
                safetoremove = True
                if dnp_period_dict:
                    for st,en in dnp_period_dict.get(crew_id, []):
                        if st <= row.flight.udor < en:
                            if verbose:
                                Errlog.log('  NOT removed: do-not-publish')
                            safetoremove = False
                            break
                if safetoremove:
                    row.remove()
                    tables['crew_rest'][2] += 1
                else:
                    tables['crew_rest'][3] += 1
    Cui.CuiSyncModels(Cui.gpc_info)
    return 'Cleaned: '+' / '.join(['%s:%s(%s)'%(r[0],r[2],r[2]+r[3])
                                   for (_,r) in tables.items() if r[2:4]>[0,0]])


########################################################################
#
# Section 4: Functions related to updating crew training need table
#
########################################################################

def update_completed_courses(crew_list=[]):
    verbose, = R.eval('fundamental.%debug_verbose_mode%')
    no_change, = R.eval('fundamental.%debug_no_change_mode%')

    # Regards legs older than now-24h as flown!
    check_date, = R.eval('fundamental.%now%-24:00')
    
    # Loop through crew_training_need once only,
    # cache rows by crew_id and filter out completed course-blocks
    if not crew_list:
        crew_list = _get_crew_list_from_rave()
    crew_list = set(crew_list)
    change_log = []
    # Loop through crew_training_need once only,
    # cache rows by crew_id and filter out completed course-blocks
    crew_training_need_cache = {} 
    errors = set()
    for crew_id in crew_list:
        try:
            for training_need in TM.crew[(crew_id,)].referers('crew_training_need','crew'):
                crew_id = training_need.crew.id
                # Adds a completion date to outdated courses with no attribute.
                #     This is done to not show outdated information in crew info. A more
                #     complicated solution, using the table course_content, probably should
                #     be implemented in the future.
                if training_need.attribute.id == "NO ATTRIBUTE" and training_need.completion is None:
                    if training_need.validto <= check_date:
                        training_need.completion = check_date
                        message = "Crew %s completed course %s, due to the course expiring"%\
                                  (crew_id, training_need.course.id)
                        Errlog.log(MODULE+"update_completed_courses: "+  message)
                        change_log.append(message)
                # Update unfinished course activities
                elif training_need.validfrom <= check_date and \
                       training_need.completion is None:
                    if crew_training_need_cache.has_key(crew_id):
                        crew_training_need_cache[crew_id].append(training_need)
                    else:
                        crew_training_need_cache[crew_id] = [training_need]
        except (EntityError,ReferenceError), err:
            message = MODULE+"_update_completed_courses; Error: %s"%err
            errors.add(message)
    for error in errors:
        Errlog.log(error)
        
    Errlog.log(MODULE + "ctl_update_completed_courses:: "+\
               "Updating courses completed until %s"%str(check_date))
    for crew_id, courses in crew_training_need_cache.items():
        result = _update_completed_courses(crew_id,courses, check_date,
                                           verbose=verbose, no_change=no_change)
        if result:
            change_log += result
    #print len(crew_training_need_cache)
    return change_log

def _update_completed_courses(crew_id, incomplete_courses, check_date, verbose=False,
                              no_change=False):
    
    crew_object = HF.CrewObject(crew_id, Cui.CuiArea0)
    crew_change_log = []

    course_sets = {}
    # Collect program course blocks
    for course in incomplete_courses:
        try:
            key = course.course.id+'+'+str(course.validfrom)
        except ReferenceError, err:
            Errlog.log(MODULE+"_update_completed_courses; Error: %s; crew id %s not updated"%(err,crew_id))
            return []
        if course_sets.has_key(key):
            course_sets[key]['courses'].append(course)
        else:
            course_sets[key] = {'flag':True,'courses':[course]} #Assume all courses completed
    # Loop through and check each block
    for key in course_sets:
        courses = course_sets[key]['courses'] # First item is completed flag!
        for course in courses:
            trng_start_date = course.validfrom 
            needed_flights = course.flights or 0
            needed_type = course.attribute.id or ""
            needed_code = course.acqual or ""
            _rave_expr ='training.%%nr_acts_of_type_and_code_in_ival%%("%s","%s",%s,%s)'%\
                         (needed_type,needed_code,trng_start_date, check_date)
            
            perf_flights, = crew_object.eval(_rave_expr)
            if perf_flights < needed_flights:
                course_sets[key]['flag'] &= False #this block not finished
        if course_sets[key]['flag']: #All blocks finished
            message = "Crew %s completed all flight need for course program %s on the %s"%\
                      (crew_id, key.split('+')[0],str(check_date).split()[0])
            Errlog.log(MODULE+"::_update_completed_courses: "+  message)
            for course in courses:
                if no_change:
                    if verbose:
                        crew_change_log.append(message)
                        # Pass if not verbose
                else:
                    course.completion = check_date
                    
    return crew_change_log

            
##################################################################
# Function for updating airport qualifications

# SASCMS-4081
def createAirportQualifications(today):
    """
    This function creates airport qualifications for crew after completed
    LIFUS and RELEASE flights.
    """

    # Get all training flights to restricted airports for FC
    restrictedLandingTrainings, = R.eval("sp_crew",
                                         R.foreach(R.iter("iterators.leg_set",
                                                          sort_by='leg.%start_utc%',
                                                          where=('training_log.%training_leg_should_create_apt_qual%',
                                                                 'leg.%%end_date%% + 24:00 <= %s' % str(today))),
                                                   'crew.%id%',
                                                   'leg.%place%(leg.%end_station%)',
                                                   'training_log.%airport_qual_ac_qual_code%',
                                                   'leg.%start_date%',
                                                   'qualification.%extended_qual_date_at_airport%(leg.%end_station%)'))

    # Create airport qualifications
    for _, crewid, apt, acqual, validfrom, validto in restrictedLandingTrainings:
        try:
            qual_set = TM.crew_qualification_set[('ACQUAL', acqual)]
        except EntityNotFoundError:
            Errlog.log('CrewTableHandler::update airport qualification ACQUAL+%s was not found'% acqual)
            continue

        try:
            acqqual_set = TM.crew_qual_acqual_set[('AIRPORT', apt)]
        except EntityNotFoundError:
            Errlog.log('CrewTableHandler::update airport acqual qualification AIRPORT+%s was not found'% apt)
            continue

        crew = TM.crew[(crewid,)]
        Errlog.log("Creating airport qualifications for %s, %s, %s, %s, %s at date %s." % (str(crew), str(apt), str(acqual), str(validfrom), str(validto), str(today)))
        try:
            entity = TM.crew_qual_acqual.create((crew, qual_set, acqqual_set, validfrom))
            entity.validto = validto
        except EntityError:
            Errlog.log("Entity already exists in table crew_qualification")
            continue

        Errlog.log('CrewTableHandler::update airport qualification: '+\
                   'Creating qualification ACQUAL+%s AIRPORT+%s to %s for crewid %s'%\
                   (acqual, apt, validto, crewid))

        # Add crew as modified so that Studio will update the training log
        modcrew.add(crewid)

def extendAirportQualifications():
    """
This function extends or creates airport qualifications for crew
"""
    
    Errlog.log("CrewTableTableHandler.py::in extendAirportQualifications")
    currentArea = Cui.CuiScriptBuffer
    # Check if in database plan
    try:
        assert HF.isDBPlan()
    except:
        Errlog.log("CrewTableHandler.py:: Only available in database plans")
        return
    
    today = Cui.CuiCrcEvalAbstime(Cui.gpc_info, currentArea, "chain", "fundamental.%now%")
    today = AbsTime.AbsTime(today).day_floor()

    # Create airport qualifications for training flights
    createAirportQualifications(today)

    leg_expr = R.foreach(
        R.iter("iterators.leg_set",
               sort_by = 'leg.%start_utc%',
               where = ('training_log.%leg_extends_airport_qual% <> ""',
                        'leg.%%end_date%% + 48:00 < %s' % str(today))),
        'leg.%start_date%',
        'training_log.%leg_airport_qual_validfrom%',
        'training_log.%leg_extends_airport_qual%',
        'training_log.%leg_extends_airport_qual_extension%',
        'training_log.%airport_qual_ac_qual_code%')
    
    restrictedLandingEvents, = R.eval("sp_crew",
                                      R.foreach(R.iter("iterators.roster_set",
                                                       where="training_log.%crew_has_leg_extending_airport%"),
                                                leg_expr,
                                                'crew.%id%'))

    reload_flag = False
    # Loop through landings
    for ix, extensions, crewid in restrictedLandingEvents:
        if extensions:
            Errlog.log("Starting extension of airport qualifications for %s, %s, %s at date %s." % (str(ix), str(extensions), str(crewid), str(today)))
            # Find last leg for each qual
            crew_qual_events = {}
            for ix, leg_start_date, apt_validfrom, apt_qual, extendto, acqual in extensions:
                acqual = real_to_virtual_qual(acqual)
                if crew_qual_events.has_key((acqual, apt_qual)):
                    (current_apt_validfrom,
                     current_legdate,
                     current_extendto) = crew_qual_events[(acqual, apt_qual)]
                    if  leg_start_date > current_legdate:
                        crew_qual_events[(acqual, apt_qual)] = (apt_validfrom, leg_start_date, extendto)
                else:
                    crew_qual_events[(acqual, apt_qual)] = (apt_validfrom, leg_start_date, extendto)
            # Loop through legs and update matching quals
            for acqual, apt_qual in crew_qual_events:
                try:
                    (apt_validfrom, leg_date, extendto_date) = crew_qual_events[(acqual, apt_qual)]
                    if apt_validfrom == AbsTime.AbsTime('1jan1986'):
                        Errlog.log('CrewTableHandler::update airport qualification: '+\
                                   'Did not find valid qualification '+\
                                   'ACQUAL+%s AIRPORT+%s for Crewid %s for leg starting %s'%\
                                   (acqual, apt_qual, crewid, leg_date))
                        continue
                    crew = TM.crew[(crewid,)]
                    qual_set = TM.crew_qualification_set[('ACQUAL', acqual)]
                    acqqual_set = TM.crew_qual_acqual_set[('AIRPORT', apt_qual)]
                    airport_qual = TM.crew_qual_acqual[(crew, qual_set, acqqual_set, apt_validfrom)]
                    if airport_qual.validto >= extendto_date:
                        continue
                    elif leg_date < airport_qual.validto and \
                             leg_date >= airport_qual.validfrom:
                        Errlog.log('CrewTableHandler::update airport qualification: '+\
                                   'Extending qualification ACQUAL+%s AIRPORT+%s to %s for crewid %s'%\
                                   (acqual, apt_qual, extendto_date, crewid))
                        airport_qual.validto = extendto_date
                        reload_flag |= True
                except (EntityError, ReferenceError), err:
                    Errlog.log('CrewTableHandler::update airport qualification: %s'%err)


    if reload_flag:
        Cui.CuiReloadTable("crew_qual_acqual", 1)
    Errlog.log("CrewTableHandler.py::leaving  extendAirportQualifications")
    return

##################################################################
# Function for updating lifetime block hours
# SASCMS-6437

def _build_crew_search_string(acc_date):
    crew_ranks_in_cockpit = ["FA", "FC", "FE", "FO", "FP", "FR", "FS"]
    return \
        "(%s) AND validfrom<=%i AND validto>=%i" % (
            " OR ".join(
                map(lambda rank: "crewrank='%s'" % rank, crew_ranks_in_cockpit)),
            int(acc_date),
            int(acc_date)
        )


def _build_blockhour_searchstring(crew_id, acc_date):
#    return "crew='%s' AND typ='blockhrs' AND tim<=%i" % (str(crew_id), acc_date)
    return "crew='%s' AND typ='blockhrs'" % (str(crew_id))

    
def _get_crew_ids(dave_connector, searchstring):
    crew_ids = []
    crew_list = fixrunner.dbsearch(dave_connector, 'crew_employment', searchstring)

    for crew in crew_list:
        current_crew_id = crew['crew']
        if current_crew_id not in crew_ids:
            crew_ids.append(current_crew_id)
    return crew_ids


@fixrunner.run
def update_lifetime_block_hours_orig(dave_connector, *a, **_):

    if len(a) > 0:
        accumulate_date = AbsTime.AbsTime(a[0])
    else:
            #AbsTime.AbsTime(str(datetime.datetime.now().strftime("%d%b%Y"))).month_floor() \
        accumulate_date = \
            AbsTime.AbsTime(str(datetime.datetime.now().strftime("%d%b%Y"))) \
            - RelTime.RelTime("00:01")

    #hi = now().day_floor()
    #latest_month = hi.month_floor()
    crew_searchstring = _build_crew_search_string(accumulate_date)
    crewids = _get_crew_ids(dave_connector, crew_searchstring)
    
    ops = []

    for current_crew_id in crewids:

        block_time_per_acfamily = {}
        last_tim_per_acfamily = {}

        block_hour_search_string = _build_blockhour_searchstring(current_crew_id, accumulate_date)

        block_hour_entities_1 = fixrunner.dbsearch(dave_connector, 'crew_log_acc', block_hour_search_string)
        block_hour_entities_mod = fixrunner.dbsearch(dave_connector, 'crew_log_acc_mod', block_hour_search_string)

        for block_hour_entities in [block_hour_entities_1, block_hour_entities_mod]:
            for b in block_hour_entities:
     
                ac_family = b['acfamily']
                blockhours = b['accvalue']
                last_tim = b["tim"]

                if ac_family not in block_time_per_acfamily.keys():
                    block_time_per_acfamily[ac_family] = 0
                block_time_per_acfamily[ac_family] += blockhours

                if ac_family not in last_tim_per_acfamily.keys():
                    last_tim_per_acfamily[ac_family] = last_tim
                else:
                    last_tim_per_acfamily[ac_family] = max(last_tim_per_acfamily[ac_family], last_tim)

        for ac_family in block_time_per_acfamily.keys():
            total_block_hours = int(RelTime.RelTime(block_time_per_acfamily[ac_family]))

            if len(fixrunner.dbsearch(dave_connector, 'lifetime_block_hours', "crew='%s' and acfamily='%s'" % (current_crew_id, ac_family))) > 0:
                opsType = 'U'
            else:
                opsType = 'N'
            ops.append(
                fixrunner.createop(
                    'lifetime_block_hours',
                    opsType,
                    dict(
                        crew=current_crew_id,
                        acfamily=ac_family,
                        #tim=int(latest_month) - 1,
                        #tim=int(accumulate_date) - 1,
                        tim=int( last_tim_per_acfamily[ac_family]) - 1,
                        accvalue=total_block_hours
                    )))

    return ops


# this version of this function:
#   by Terje Dahl @ HiQ 2014-09
#   It utilizing same function as "Crew Block Hours" application, rather than basing itself on other accumulators.
def update_lifetime_block_hours():
    import os
    from carmensystems.dig.framework.dave import DaveConnector
    dc = DaveConnector(os.environ['DB_URL'], os.environ['DB_SCHEMA'])

    import utils.crewlog as cl
    from utils.TimeServerUtils import now
    from tm import TM

    AT = AbsTime.AbsTime
    RT = RelTime.RelTime

    def int_interval(a, b):
        return cl.Interval(int(a), int(b))
        
    hi = now().day_floor()
    latest_month = hi.month_floor()
    lifetime_key = int_interval(0, hi)
    this_month_key = int_interval(latest_month, hi.month_ceil())

    crew_ids = _get_crew_ids(dc, _build_crew_search_string(latest_month))
    #crew_ids = ["fake_id"]+crew_ids
    print "len(crew_ids): %s" % len(crew_ids)

    for crew_id in crew_ids:
    #for crew_id in crew_ids[:5]:
    #for crew_id in ["27737"]:
        print crew_id,

        bh_m = cl.stat_1_90_6_12_life(crew_id).get("blockhrs")
        # There may not be any blockhours for a given crew!
        if not bh_m:
            print "(no blockhrs found)",
            continue

        blockhrs = bh_m.get(crew_id)

        crw = TM.crew[(crew_id,)]

        for ac_family in blockhrs.keys():
        #for ac_family in ["A320"]:
            # print "ac_family: %s" % ac_family

            stats = blockhrs[ac_family] 
            total_block_hours = int(RelTime.RelTime(stats[lifetime_key] - stats.get(this_month_key, 0)))

            entries = list(TM.lifetime_block_hours.search("(&(crew=%s)(acfamily=%s))" % (crew_id, ac_family)))
            entry = TM.lifetime_block_hours.create((crw, ac_family)) if len(entries) == 0 else entries[0]

            # If all new parameter-values are the same as old,
            # then they entry doesn't get updated when state is committed.
            entry.tim = AT(int(latest_month)-1)
            entry.accvalue = RT(total_block_hours)

    # Calling save() explicitly is not necessary, as updates get saved by Accumulators.py's savePlan()
    #print "saving: %s " % TM.save("accumulator update")

    print

def main():
    update_rec_test("13235")


#main()



# end of file

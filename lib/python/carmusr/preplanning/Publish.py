#######################################################
#
#   Publish
#
# -----------------------------------------------------
#
# Created:      2007-11-01
# By:           Yaser Mohamed
#
# ------------------------------------------------------
#
# Description:
#
# Publishing is done automatically when saving the 
# plan exept for those intervals which should not be
# informed. The following is the procedure for
# publishing:
#
# 1. Get the difference between the current roster and
#    the latest published. Exlude "not inform"
# 2. Get the published intervals (published interval
#    excluding all that is "not inform").
# 3. Create the notifications to crew and remember
#    which notifications were added
# 4. Attempt to save the plan.
# 5. If there are any conflicts, remove the
#    notifications that was added in step 3.
# 6. Publish all rosters. Exclude "not inform".
# 7. Save (the publish table needs to be saved).
#
#######################################################

import copy
import re
import time

import carmensystems.rave.api as R
import carmstd.cfhExtensions
import carmusr.HelperFunctions as HF
import carmusr.modcrew as modcrew
import carmusr.tracking.CrewNotificationFunctions as CNF
import carmusr.tracking.Rescheduling as Rescheduling
from carmensystems.basics.CancelException import CancelException
import Cui
import modelserver as M
import utils.Names as Names

from utils.performance import log, timing, clockme, T

from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime
from Airport import Airport
from tm import TM, TempTable
from utils.rave import RaveIterator
from utils.rave import RaveEvaluator
from utils.guiutil import UpdateManager
from utils.time_util import IntervalSet, TimeInterval
from carmusr.tracking.informedtemptable import InformedTempTable, \
                                               InformedTempTableRowCreator

RE_NON_ESCAPED_PLUS = re.compile(r'(?<!\\)\+')

# These are the possible 'pubtype' values that can exist in 'published_roster'.
# Note: There are corresponding Rave constants in 'publish'. Keep in sync!!!
PUBLICATION_TYPES = (
    ROSTERING_PUBLISHED_TYPE,
    TRACKING_PUBLISHED_TYPE,
    TRACKING_INFORMED_TYPE,
    TRACKING_DELIVERED_TYPE,
    ) = (
    "SCHEDULED",
    "PUBLISHED",
    "INFORMED",
    "DELIVERED",
    )

ONE_DAY = RelTime(24, 0)
ONE_MINUTE = RelTime(0, 1)

class PublishInformation(RaveEvaluator):
    """
    Publishing from Studio is performed as a part of the save-plan process.
    This class is populated in a pre-save operation, and operated upon in a
    post-save operation.

    Pre-save:
      - Get a list of locally modified crew (plus additional crew that have
        been "tagged" as modified, for example when a do-not-publish period has
        been removed.)
      - "Display" the crew rosters in the ScriptBuffer area.
      - Evaluate period start/end in utc for each crew.
    """
    crew = {}
    startDate = None
    endDate = None

    @classmethod
    def cls_init(cls):
        cls.rEvalCls(startDate='fundamental.%loaded_data_period_start%',
                     endDate='round_up(fundamental.%loaded_data_period_end%, 24:00)')
         
        cls.set_default_context_to_crew(modcrew.get())
        cls.load_crew_roster_data()
    
    @classmethod
    def set_default_context_to_crew(cls, crew=None):
        Cui.CuiDisplayGivenObjects(Cui.gpc_info,
                                   Cui.CuiScriptBuffer,
                                   Cui.CrewMode,
                                   Cui.CrewMode,
                                   crew or cls.crew.keys())
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, "window")
        
    @classmethod
    def load_crew_roster_data(cls):
        cls.crew = {}
        for roster in RaveIterator(R.iter('iterators.roster_set'), {
                'crewid':        'crew.%id%',
                'home_airport':  'crew.%homeairport%',
                'ldp_start_utc': 'publish.%crew_loaded_data_start_utc%',
                'ldp_end_utc':   'publish.%crew_loaded_data_end_utc%',
                'ldp_splits':    'publish.%crew_loaded_month_ends_utc%',
                'pub_end_utc':   'publish.%crew_rostering_published_end%',
                }).eval('default_context'):
            if roster.home_airport is None:
                log("Publish WARNING: Crew %s has no home airport, defaulting to CPH" % roster.crewid)
                roster.home_airport = "CPH"
            cls.crew[roster.crewid] = {
                'home_airport': roster.home_airport,
                'start_utc':    roster.ldp_start_utc,
                'end_utc':      roster.ldp_end_utc,
                'split_utc':    roster.ldp_splits.rstrip(','),
                'pub_end_utc':  roster.pub_end_utc,
                'dnp_periods':  [],
                }
        
    @classmethod
    def split_pacts_at_month_ends(cls):
        """
        For locally modified crew about to be saved:
        Splits month-end-crossing pacts at month ends (homebase time).
        
        Assumes cls_init() has been called, so that all modified crew
        already are "displayed" in the script buffer.
        """

        if not cls.crew:
            log("Publish::split_pacts_at_month_ends: No modified rosters")
            return

        Cui.CuiSetCurrentArea(Cui.gpc_info, Cui.CuiScriptBuffer)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, 'WINDOW')
    
        # Get some useful info regarding the pacts to split.
        # The info will be used to recreate the pacts in split format.
        
        pact_iter = RaveIterator(
            R.iter('iterators.leg_set',
                   where="publish.%split_pact_at_month_ends%"),{
            'crew_id':        'crew.%id%',
            'task_code':      'leg.%code%',
            'start_station':  'leg.%start_station%',
            'start_hb':       'leg.%start_hb%',
            'end_hb':         'leg.%end_hb%',
            }).eval('default_context')

        if not pact_iter:
            log("Publish::split_pacts_at_month_ends: No splits are required")
            return
            
        log("Publish::split_pacts_at_month_ends: %d pacts." % len(pact_iter))
        
        # Update end time of the original pact, and create new one(s) up to the
        # original end, spliting at month end(s) (midnight homebase time).
        # Note that all resulting pacts must touch the loaded data period.

        must_touch = cls.rEvalDict(
            start_hb='fundamental.%loaded_data_period_start%',
            end_hb=('fundamental.%loaded_data_period_end%', AbsTime.day_ceil))
        #print "must_touch",must_touch['start_hb'],must_touch['end_hb']
        
        for pact in pact_iter:
            #print "%-5s%s"%(pact.task_code,pact.crew_id),pact.start_hb,pact.end_hb
            crew = TM.crew[pact.crew_id]
            home = cls.crew[pact.crew_id]['home_airport']
            activity = TM.activity_set[pact.task_code]
            location = TM.airport[pact.start_station]
            sth = pact.start_hb
            while sth < pact.end_hb:
                eth = (sth + ONE_MINUTE).month_ceil()
                while eth <= must_touch['start_hb']:
                    eth = (eth + ONE_MINUTE).month_ceil()
                if eth > pact.end_hb or eth >= must_touch['end_hb']:
                    eth = pact.end_hb
                utc = cls.rEvalDict(
                    st='station_utctime("%s",%s)' % (home, sth),
                    et='station_utctime("%s",%s)' % (home, eth))
                if sth == pact.start_hb:
                    #print "    update",utc['st'],utc['et']
                    ca = TM.crew_activity[(utc['st'], crew, activity)]
                else:
                    #print "    create",utc['st'],utc['et']
                    ca = TM.crew_activity.create((utc['st'], crew, activity))
                ca.et = utc['et']
                ca.adep = ca.ades = location
                sth = eth
                
        # Sync to update Studio.
        Cui.CuiSyncModels(Cui.gpc_info)
        
        # Re-calculate rave values (one or more rosters have been changed).
        cls.load_crew_roster_data()
        
    @classmethod
    def load_do_not_publish_periods(cls):
        """
        For each crew, set the 'dnp_periods' item to a sorted list of periods
        marked as do-not-publish.
        
        Each period contains the attributes 'start_utc' and 'end_utc'.
        
        The periods initially cover whole hb days, but they are adjusted
        according to legs on the roster, so that only legs that are fully within
        the inital periods will be counted as do-not-publish.
        """
        Cui.CuiDisplayGivenObjects(Cui.gpc_info,
                                   Cui.CuiScriptBuffer,
                                   Cui.CrewMode,
                                   Cui.CrewMode,
                                   sorted(cls.crew))
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, "window")
        for crewid in cls.crew:
            crew = TM.crew[(crewid,)]
            cls.crew[crewid]['dnp_periods'] = []
            # Handle adjacent or overlapping periods.
            periods = IntervalSet()
            for e in crew.referers("do_not_publish", "crew"):
                periods.add(TimeInterval(e.start_time, e.end_time))
            periods.merge()
            # Populate crew's 'dnp_periods' list.
            # Adjustments are calculated made using rave evaluation.
            for dnp in sorted(periods):
                for p in RaveIterator(R.iter('iterators.roster_set', where='crew.%%id%%="%s"' % crewid), {
                         'start_utc':  'publish.%%crew_adjusted_period_start_utc%%(%s)' % dnp.first,
                         'end_utc':    'publish.%%crew_adjusted_period_end_utc%%(%s)' % dnp.last,
                         'start_orig': 'crew.%%utc_time%%(%s)' % dnp.first,
                         'end_orig':   'crew.%%utc_time_end%%(%s)' % dnp.last,
                         }).eval('default_context'):
                    if p.start_utc is None or p.end_utc is None:
                        log("*** Crew %s: DO-NOT-PUBLISH [%s - %s] utc" % (crewid, p.start_utc, p.end_utc))
                        log("  * Derived from marked [%s - %s] hb. Crew unavailable? SKIPPED." % (dnp.first, dnp.last))
                    else:
                        if (p.start_utc < p.end_utc
                        and p.start_utc < cls.crew[crewid]['end_utc']
                        and p.end_utc > cls.crew[crewid]['start_utc']):
                            cls.crew[crewid]['dnp_periods'].append(p)
                        if (str(p.start_utc),str(p.end_utc)) != (str(p.start_orig),str(p.end_orig)):
                            log(("** Crew %s: DO-NOT-PUBLISH [%s - %s] hb adjusted to [%s - %s] utc %s"
                            % (crewid, dnp.first, dnp.last, p.start_utc, p.end_utc,
                               ((p.start_utc >= p.end_utc) and "EMPTY: SKIPPED") or "")))

    @classmethod
    def get_publish_periods(cls, crewid):
        """
        Calculate a sorted list of publish-now periods (2-tuple, utc time)
        within the planning period. No empty periods will be returned. Periods:
        - are not covered by do-not-publish periods, and
        - are covered by previously SCHEDULED data.
        
        Do-not-publish data must be pre-initialized:
            see load_do_not_publish_periods().
        """
        #print "### GET_PP",crewid,"###"
        pub_per_start = cls.crew[crewid]['start_utc']
        pub_end = min(cls.crew[crewid]['end_utc'],
                      cls.crew[crewid]['pub_end_utc'])
        pub_per_ends = [AbsTime(month_end) for month_end
                        in cls.crew[crewid]['split_utc'].split(',')]
        if (not pub_per_ends) or pub_end > pub_per_ends[-1]:
            pub_per_ends.append(pub_end)
        #print "  START",pub_per_start
        #print "    END",pub_end
        #print "  SPLIT",[str(e) for e in pub_per_ends]
        pub_periods = []
        for pub_per_end in pub_per_ends:
            if pub_per_start >= pub_end:
                break
            pub_per_end =  min(pub_per_end, pub_end)
            pub_periods.append([pub_per_start, pub_per_end])
            for dnp in cls.crew[crewid]['dnp_periods']:
                if dnp.start_utc >= pub_per_end:
                    break
                if dnp.end_utc <= pub_per_start:
                    continue
                if dnp.start_utc <= pub_per_start:
                    # dnp covers period start
                    if dnp.end_utc >= pub_per_end:
                        # dnp covers complete period -> remove it
                        del pub_periods[-1]
                        break
                    else:
                        # dnp cuts start of period -> later period start
                        pub_per_start = pub_periods[-1][0] = dnp.end_utc
                else:
                    # dnp starts within period -> earlier period end
                    pub_periods[-1][1] = dnp.start_utc
                    if dnp.end_utc < pub_per_end:
                        # dnp ends within period -> keep period tail
                        pub_periods.append([dnp.end_utc, pub_per_end])
            pub_per_start = pub_per_end
        #for s,e in pub_periods: print " PERIOD",s,"-",e
        #print "### GET_PP DONE"
        return pub_periods    

    @classmethod
    def get_inform_periods(cls, crewid):
        """
        Calculate a sorted list of inform-now periods (2-tuple, utc time)
        within the planning period. No empty periods will be returned.
        
        The initial data resides in InformedTempTable(). 
        It is assumed that the periods in the table:
        - do not overlap with any do-not-publish periods, and
        - are covered by previously PUBLISHED data.
        
        The periods initially cover whole hb days, but they are adjusted
        according to legs on the roster, so that only legs that are fully within
        the inital periods will be counted as inform-now.
        """
        inf_periods = []
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, "window")
        for inf in sorted(InformedTempTable(), key=lambda r: r.start_time):
            if inf.crew == crewid:
                for p in RaveIterator(R.iter('iterators.roster_set', where='crew.%%id%%="%s"' % crewid), {
                         'start_utc':  'publish.%%crew_adjusted_period_start_utc%%(%s)' % inf.start_time,
                         'end_utc':    'publish.%%crew_adjusted_period_end_utc%%(%s)' % inf.end_time,
                         'start_orig': 'crew.%%utc_time%%(%s)' % inf.start_time,
                         'end_orig':   'crew.%%utc_time_end%%(%s)' % inf.end_time,
                         }).eval('default_context'):
                    if p.start_utc is None or p.end_utc is None:
                        log("*** Crew %s: INFORM-NOW [%s - %s] utc" % (crewid, p.start_utc, p.end_utc))
                        log("  * Derived from marked [%s - %s] hb. Crew unavailable? SKIPPED." % (inf.start_time, inf.end_time))
                    else:
                        if p.start_utc < p.end_utc:
                            inf_periods.append([p.start_utc,p.end_utc])
                        if (str(p.start_utc),str(p.end_utc)) != (str(p.start_orig),str(p.end_orig)):
                            log(("** Crew %s:INFORM-NOW [%s - %s] hb adjusted to [%s - %s] utc %s"
                                 % (crewid, inf.start_time, inf.end_time, p.start_utc, p.end_utc,
                                    ((p.start_utc >= p.end_utc) and "EMPTY: SKIPPED") or "")))
        return inf_periods    

    @classmethod
    def update_rescheduling_info(cls):
        if cls.crew:
            t = time.time()
            UpdateManager.start()
            log("--- UPDATE RESCHEDULING INFO FOR %d CREW." % len(cls.crew))
            Rescheduling.publish(crew_list=cls.crew.keys(),
                                 start_date=cls.startDate,
                                 end_date=cls.endDate,
                                 sel_mode=Rescheduling.ONLY_INFORM_SELECTION)        
            UpdateManager.done(noguiupdate=True)
            t = time.time() - t
            log("--- RESCHEDULING UPDATED, %d: %.2fs" % (len(cls.crew), t))


class DoNotPublishTableRowCreator:
    """
    Handle updates and iterations of 'do_not_publish' table.
    """
    def __init__(self, crew):
        self.crew = crew
        self.crewref = TM.crew[(crew,)]
        self.table = TM.do_not_publish

    def __iter__(self):
        return iter(self.crewref.referers(self.table.table_name(), 'crew'))

    def create(self, st, et):
        rec = self.table.create((self.crewref, st))
        rec.end_time = et
        return rec

    def reload(self):
        Cui.CuiReloadTable(self.table.table_name(), Cui.CUI_RELOAD_TABLE_SILENT)

class RosterAttributeTableRowCreator:
    """
    Handle updates and iterations of 'roster_attr' table.
    """
    def __init__(self, attr, crew):
        self.crew = crew
        self.attr = TM.roster_attr_set[(attr,)]
        self.crewref = TM.crew[(crew,)]
        self.table = TM.roster_attr

    def __iter__(self):
        return iter(self.crewref.referers(self.table.table_name(), 'crew'))

    def create(self, st, et):
        rec = self.table.create((self.attr, self.crewref, st))
        rec.end_time = et
        return rec

    def reload(self):
        Cui.CuiReloadTable(self.table.table_name(), Cui.CUI_RELOAD_TABLE_SILENT)

        
class InformedTableRowCreator:
    """
    Handle updates and iterations of 'informed' table.
    """
    
    def __init__(self, crew):
        self.crew = crew
        self.crewref = TM.crew[(crew,)]
        self.table = TM.informed

    def __iter__(self):
        return iter(self.table.search('(crew=%s)' % self.crewref))

    def create(self, st, et):
        try:
            rec = self.table.create((self.crewref, st))
        except M.EntityError:
            rec = self.table[(self.crewref, st)]
        rec.enddate = et
        rec.informedby = Names.username()
        rec.informtime = AbsTime(*time.gmtime()[:5])
        
        return rec

    def reload(self):
        Cui.CuiReloadTable(self.table.table_name(), Cui.CUI_RELOAD_TABLE_SILENT)


def publishAll(marked=False):
    """
    This is a substitution for the rostering-publish process,
    to be used during the test phase only.
    """
    UpdateManager.start()

    # 'pp' is expressed in homebase time. CuiPublishRosters wants utc time.
    # In "real life" there should be separate CuiPublishRosters calls for crew
    # with different homebase times, but for now we'll assume all crew is
    # scandinavian (so CPH time will do for all of them)...
    # NOTE: The extended pp is NOT used here, since rostering uses standard pp.

    start_hb, = R.eval('fundamental.%pp_start%')
    start_utc, = R.eval('station_utctime("CPH", fundamental.%pp_start%)')
    end_hb, = R.eval('round_up(fundamental.%pp_end%, 24:00)')        
    end_utc, = R.eval('station_utctime("CPH", round_up(fundamental.%pp_end%, 24:00))')

    # Do a part of what would be performed at rostering-publish.
    # (Update the published_roster and crew_publish_info tables.)

    if marked:
        crewlist = Cui.CuiGetCrew(Cui.gpc_info, Cui.CuiWhichArea, 'MARKEDLEFT')
    else:
        crewlist = [crew.id for crew in TM.crew]

    if not crewlist:
        raise Exception("No crew selected")
    
    publist = [(crew, ptype, int(start_utc), int(end_utc))
               for crew in crewlist
               for ptype in PUBLICATION_TYPES]

    log("CuiPublishedRosters: %s %s crew" % (repr([ptype for ptype in PUBLICATION_TYPES]), len(crewlist)))
    Cui.CuiPublishRosters(Cui.gpc_info,
                          publist,
                          "SIMULATED ROSTER PUBLISH",
                          Cui.CUI_PUBLISH_ROSTER_SKIP_MODIFIED_CHECK
                          | Cui.CUI_PUBLISH_ROSTER_SKIP_SAVE)
    UpdateManager.setDirtyTable("published_roster")
    
    Rescheduling.publish(crew_list=crewlist,
                     start_date=start_hb,
                     end_date=end_hb,
                     sel_mode=Rescheduling.ROSTER_PUBLISH)
                     
    UpdateManager.done()
    setPublishedAttr(crewlist)
    return 0


def setPublishedAttr(crewlist):
    """
    This is run as part of publishAll,
    to be used during the test phase only.
    """
    UpdateManager.start()
    user = Names.username()
    # [acosta:10/018@10:41] Should we not use the time server instead??
    publ_time = AbsTime(*time.gmtime()[:5])
    si_string = "Last published by %s at %s" %(user, publ_time)
    end_hb, = R.eval('round_up(fundamental.%pp_end%, 24:00)')        
    t_set = TM.table("crew_attr_set")
    set = t_set["PUBLISHED"]
    t_attr = TM.table("crew_attr")
    try:
        for crewid in crewlist:
            crew = TM.crew[(crewid,)]
            try:
                _attr = t_attr[(crew, AbsTime("01JAN1986"), set)]
            except:
                _attr = t_attr.create((crew, AbsTime("01JAN1986"), set))
            _attr.value_abs = end_hb
            _attr.si = si_string
        UpdateManager.setDirtyTable("crew_attr")
    except M.TableNotFoundError:
        log("Publish: PUBLISHED attribute could not be set due to missing table")
    except M.EntityNotFoundError:
        log("Publish: PUBLISHED attribute could not be set due to old table data (crew_attr_set) or crew missing in crew table.")
    UpdateManager.done()

    
@clockme
def publishPreSave(dnp_period_dict=None):
    """
    Called by Studio before the actual save (to database) is performed.
    
    dnp_period_dict: if this argument is a dict instance, it is populated with
    per-crew lists of periods that are marked as do-not-publish in Studio.
    """
    # HACK-TO-HANDLE-SAVEBUTTON-DIMMING-CORRECTLY: 1 line
    _remove_dummy_publish_periods()
    
    # Populate CuiScriptBuffer with modified crew. 
    # Set the default rave context.
    # Extract some crew data from rave.
    PublishInformation.cls_init()
    
    # Adjust crew_activity that has been created/modified.
    PublishInformation.split_pacts_at_month_ends()
    
    # Adjust crew_activity_attr CALLOUT entries.
    #
    # When a callout is performed in Studio (see Standby.py), a CALLOUT
    # attribute is attached to the standby activity. On this attribute, the
    # value_rel is set to the transport time associated with the callout.
    #
    # Since attributes are not revision controlled the same way as activities,
    # the same crew_activity_attr instance is attached to all revisions of the
    # corresponding crew_activity, i.e. both the latest and the PUBLISHED
    # roster will look at the same crew_activity_attr instance.
    #
    # This presents a special situation when a callout is marked do-not-publish.
    # In the latest roster revision, it's a callout, in the PUBLISHED it's not.
    # (The oppsite can of course also exist;
    # a PUBLISHED callout that is not a callout in the latest revision.)
    #
    # Therefore, we need to store two values - a "latest" and a "PUBLISHED".
    # The "PUBLISHED" transport time is stored in value_int of the attribute.
    #
    # This code section will check and adjust CALLOUT attributes for modified
    # crew, so that the rel and int values are correctly set according to the
    # do-not-publish periods at hand at save time.
    
    #PublishInformation.load_do_not_publish_periods()
    for crew in PublishInformation.crew:
        # Get a list of do-not-publish periods for this crew.
        dnp = sorted((p.start_utc,p.end_utc)
                     for p in PublishInformation.crew[crew]['dnp_periods'])
        if isinstance(dnp_period_dict, dict):
            dnp_period_dict[crew] = dnp
            
        # Get a list of "calloutable" standbys in the latest roster.
        sby = [s for s in RaveIterator(R.iter('iterators.leg_set',
               where='crew.%%id%%="%s" and leg.%%is_standby%%' % crew),
               {'st':       'leg.%start_utc%',
                'activity': 'leg.%code%',
               }).eval('default_context')]
        
        # For each of the crew's CALLOUT attributes, check if the corresponding
        # standby activity is on the roster, and if it is within a dnp period.
        # Adjust the rel and int values accordingly.
        caa_table = TM.crew_activity_attr
        for caa in caa_table.search("(&(ca.crew=%s)(attr=CALLOUT))" % crew):
            caa_ca = str(caa.getRefI("ca")).split("+")
            caa_ca_st = AbsTime(caa_ca[0])
            caa_ca_activity = caa_ca[-1]
            on_latest_roster = False
            for s in sby:
                if s.st == caa_ca_st and s.activity == caa_ca_activity:
                    on_latest_roster = True
                    break
            chgstr = None
            logstr = "CALLOUT %s on %s %s (rel=%s,int=%s). Latest roster: %s." % (
                crew, caa_ca_st, caa_ca_activity, caa.value_rel, caa.value_int, on_latest_roster)
            for st,en in dnp:
                if st <= caa_ca_st < en:
                    logstr += " DNP: %s-%s." % (st,en)
                    if not on_latest_roster:
                        if caa.value_rel is not None:
                            caa.value_rel = None
                            chgstr = logstr + " Change: REL(latest)<-None."
                    break
            else:
                logstr += " DNP: No."
                if on_latest_roster:
                    if caa.value_rel is None:
                        if caa.value_int is not None:
                            caa.value_int = None
                            chgstr = logstr + " Change: INT(published)<-None."                           
                    else:
                        if int(caa.value_rel) != caa.value_int:
                            caa.value_int = int(caa.value_rel)
                            chgstr = logstr + " Change: INT(published)<- REL(latest)."                           
                else:
                    if caa.value_int is not None:
                        caa.value_int = None
                        chgstr = logstr + " Change: INT(published)<-None."                           
                        
            # If not a CALLOUT in any revision, remove the attribute instance.
            if caa.value_rel is None and caa.value_int is None:
                caa.remove()
                chgstr = (chgstr or logstr) + " REMOVE!" 
            
            if chgstr:
                log("    publishPreSave(): %s" % chgstr)
            else:
                log("    publishPreSave():(%s)" % logstr)  
    return 0

@clockme
def publishPostSave():
    """
    Called by Studio after the actual save (to database) has taken place.
    """
    if PublishInformation.crew:
        import carmensystems.studio.Tracking.OpenPlan as OpenPlan
        for _ in timing("OpenPlan._planMonitor.refresh"):
            OpenPlan._planMonitor.refresh(0, 0, 0, 0)
            
        PublishInformation.set_default_context_to_crew()
        PublishInformation.load_do_not_publish_periods()
        update_published_roster_periods()
        update_automatic_notifications()
        itt = InformedTempTable()
        if len(itt):
            for _ in timing("PublishInformation.update_rescheduling_info"):
                PublishInformation.update_rescheduling_info()
            insertInformedData()
            itt.clear()

    modcrew.clear()

    if PublishInformation.crew:
        for _ in timing("TM.save()"):
            TM.save()
            
    return 0


@clockme
def update_automatic_notifications():
    """
    Create automatic assignment notifications corresponding to roster changes.
    """
    revised_rosters = get_revised_rosters(PublishInformation.crew)
    change_descriptions = get_change_descriptions(TRACKING_INFORMED_TYPE)
    
    PublishInformation.set_default_context_to_crew()

    # Contains periods that are marked as "inform-now" on rosters.
    informed_table = InformedTempTable()
    
    # Create notifications per crew

    for crewid in PublishInformation.crew:
        # Legs that were added, removed or modified according to CuiDiff
        # Note that multi-day legs already are broken down to day level.
        
        changed_legs = change_descriptions.pop(crewid, [])

        # Find crew's all legs currently on the roster.
        # Multi-day activity is broken down to day-size legs.
        
        roster_legs = []
        for roster in revised_rosters:
            if roster.crew == crewid:
                for leg in roster.chain():
                    if (leg.arrivalTime - leg.departureTime <= ONE_DAY):
                        roster_legs.append(leg)
                    else:
                        dep = AbsTime(leg.departureTime)
                        arr_end = AbsTime(leg.arrivalTime)
                        while dep < arr_end:
                            dayleg = copy.copy(leg)
                            dayleg.departureTime = dep
                            dayleg.arrivalTime = min(dep + ONE_DAY, arr_end)
                            roster_legs.append(dayleg)
                            dep = AbsTime(dayleg.arrivalTime)
                break
                
        # Add changed_legs entries for changes detected on the roster.
        # Ignore roster legs that are informed at the current save operation.

        for leg in roster_legs:
            if not informed_table.is_informed(crewid, leg.departureTime):
                if leg.changed_checkin or leg.changed_checkout:
                    for chg in changed_legs:
                        if chg.key == leg.key:
                            break
                    else:
                        chg = copy.copy(leg)
                        chg.changeType = "modified"
                        chg.changed_checkin = None
                        chg.changed_checkout = None
                        changed_legs.append(chg)

        # And finally create the notifications...
        
        CNF.create_automatic_assignment_notifications(
                crewid,
                PublishInformation.crew[crewid]['home_airport'],
                PublishInformation.crew[crewid]['start_utc'],
                PublishInformation.crew[crewid]['end_utc'],
                PublishInformation.crew[crewid]['dnp_periods'],
                roster_legs,
                changed_legs)


@clockme
def update_published_roster_periods():
    """
    Publish-tags the whole roster, except do-not-publish periods, as PUBLISHED.
    Additionally, periods marked as "INFORM" are publish-tagged as INFORMED.
    
    Note that this function performs a save (made by CuiPublishRosters).
    This is required, because the CuiDiffPublishedRosters that follows (see
    get_change_descriptions) operates on saved revisions.
    """

    publist = []
    for crewid in PublishInformation.crew:
        for start_utc, end_utc in PublishInformation.get_publish_periods(crewid):
            publist.append((crewid,
                            TRACKING_PUBLISHED_TYPE,
                            int(start_utc),
                            int(end_utc)))
        for start_utc, end_utc in PublishInformation.get_inform_periods(crewid):
            publist.append((crewid,
                            TRACKING_INFORMED_TYPE, 
                            int(start_utc), 
                            int(end_utc)))

    if not publist:
        return
        
    log("CuiPublishRosters: %s crew, %s entries" % (
        len(PublishInformation.crew), len(publist)))
    for c,d,s,e in publist[:10]:
        print "%s %10.10s %s %s" % (c,d,AbsTime(s),AbsTime(e))
    if len(publist) > 10: print "... (logged 10 of",len(publist),"entries)"
    
    # Here, published_roster periods are updated, using CuiPublishRosters().
    #
    # Internally, CuiPublishRosters starts with a refresh.
    # It then updates the periods, and saves. Between refresh and save, external
    # conflicting updates may have been performed.
    #
    # Using flags, we can ask CuiPublishRoster to handle conflicts either by:
    # a) ignoring them; which may lead to gaps or overlaps in the table.
    # b) rolling back local changes (leaving the external ones in the model),
    #    and report the conflict to the caller (this function).
    #
    # The below code tries to recover from these situations.
    # There may still be inconsistencies; but only if *several*
    # conflicting external updates are performed during a short time.
    #
    # The Cui.CUI_PUBLISH_ROSTER_CHECK_CONFLICT flag required to support this
    # will be available in CMS1SP8+. If we run in an older sys than that,
    # conflicts are always ignored (see a above). 
    
    msg = "TRACKING-STUDIO PUBLISH/INFORM"
    flags = Cui.CUI_PUBLISH_ROSTER_SKIP_MODIFIED_CHECK
    try:
        flags |= Cui.CUI_PUBLISH_ROSTER_CHECK_CONFLICT
        cmode = "IMPROVED CONFLICT HANDLING"
    except:
        cmode = "COMPATIBILITY"
            
    T.start("CuiPublishRosters (%s in %s mode)" % (msg,cmode))
    try:
        if Cui.CuiPublishRosters(Cui.gpc_info, publist, msg, flags) == 0:
            log("CuiPublishRosters: OK")                
            return

        if cmode == "COMPATIBILITY":
            log("CuiPublishRosters: DONE")
            return
            
        log("CuiPublishRosters: Failed due to conflict(s). Retry once.")
        if Cui.CuiPublishRosters(Cui.gpc_info, publist, msg, flags) == 0:
            log("CuiPublishRosters: OK on first retry.")                
            return
                                              
        log("CuiPublishRosters: Failed again. Retry with per-crew calls.")
        fail_pl = []
        for crewid in sorted(set(pp[0] for pp in publist)):
            crew_pl = [pp for pp in publist if pp[0] == crewid]
            if Cui.CuiPublishRosters(Cui.gpc_info, crew_pl, msg, flags) > 0:
                fail_pl.extend(crew_pl)
        if not fail_pl:
            log("CuiPublishRosters: OK on per-crew retry.")                
        else:
            # Note: By performing this final CuiPublishRosters call, we force
            # this Studio session to "win" the conflict. This means that
            # current changes will be published, but at the cost of potential
            # inconsistency in the published_roster table.
            log("CuiPublishRosters: Per-crew conflicts: %s. For these crew, "
                "inconsistent data may exist in published_roster."
                % sorted(set(pp[0] for pp in fail_pl)))            
            flags &= ~Cui.CUI_PUBLISH_ROSTER_CHECK_CONFLICT
            Cui.CuiPublishRosters(Cui.gpc_info, fail_pl, msg, flags)
        
    finally:
        T.stop()


### Collecting rosters functions ######################             
@clockme                     
def get_revised_rosters(crewDict):
    """
    Extract leg information from the current roster.
    """
    PublishInformation.set_default_context_to_crew(crewDict.keys())
    rosters = RaveIterator(RaveIterator.iter('iterators.roster_set'),
                          {'crew': 'crew.%id%'})
    legs = RaveIterator(RaveIterator.iter('iterators.leg_set',
                       sort_by='leg.%start_hb%'), CNF.FlightDescriptor.fields)
    rosters.link(legs)
    return rosters.eval('default_context')

@clockme
def get_change_descriptions(publishedType):
    """
    Get difference between current roster and "reference" roster with a specific
    publish type tag (see PUBLICATION_TYPES). Returns a dictionary with a list
    of changed activities (legs) for each crew in 'PublishInformation.crew'.
    """

    T.start("CuiSyncModels(getchd)")
    Cui.CuiSyncModels(Cui.gpc_info)

    #---------------------------------------------------------------------------                                     
    # Find out what the roster used to look like
    #---------------------------------------------------------------------------    

    T.restart("CuiDiffPublishedRoster(getchd)")
    diffdict = Cui.CuiDiffPublishedRoster(Cui.gpc_info,
                                          PublishInformation.crew.keys(),
                                          0,
                                          0, 
                                          publishedType)
    T.restart("Analyze CuiDiffPublishRoster result")

    # The loop below populates each crew's []-list with leg change info.
    changed_rows = dict((crewid,[]) for crewid in PublishInformation.crew)
    
    # Go through all diffs in added-modified-removed order, in order to
    # correctly handle overlapping leg changes.
    # For example, if an original roster contains:
    #   VA 1Jan-5Jan                      1  2  3  4  5  6  7  8  9 10
    #   VA 7Jan-9Jan                    [VA VA VA VA -- -- VA VA -- --]
    # and that is changed to:          
    #   VA 1Jan-3Jan                      1  2  3  4  5  6  7  8  9 10 
    #   VA 6Jan-11Jan                   [VA VA -- -- -- VA VA VA VA VA]
    # then the CuiDiff will contain:
    #   modified: VA 1-5 (to VA 1-3)    [ m  m  m  m  -  a ra ra  a  a]
    #   removed:  VA 7-9
    #   added:    VA 6-11 (overlaps with the removed activity)
    # With the sorting, it's easier to get the desired result:
    #   removed:  VA 3-5                [ -  -  r  r  -  a  -  -  a  a]
    #   added:    VA 6-7
    #   added:    VA 9-11
    
    ct_keys = [M.Change.ADDED, M.Change.MODIFIED, M.Change.REMOVED]
    
    attributes_of_interest = (
        "st", "et", "adep", "ades", "activity", "pos")
    attribute_aliases = {
        "sobt":"st", "sibt":"et"}

    for crewid, diffset in diffdict.items():
        for c in sorted(diffset, key=lambda c: ct_keys.index(c.getType())):
            table = c.getTableName()
            if not table.startswith("crew_"):
                continue
        
            db_row = c.getEntityI()
            entity_key = str(db_row)
            
            c_dtl = {}
            for (attr,org,rev) in c:
                attr = attribute_aliases.get(attr, attr)
                if attr in attributes_of_interest:
                    c_dtl[attr] = (org,rev)

            legtable = ((table == "crew_ground_duty" and "ground_task") or
                        (table == "crew_flight_duty" and "flight_leg") or
                        None)
            if legtable:
                for leg in [d for d in diffset if d.getTableName() == legtable]:
                    if entity_key.startswith(str(leg.getEntityI())):
                        for (attr,org,rev) in leg:
                            attr = attribute_aliases.get(attr, attr)
                            if attr in attributes_of_interest:
                                c_dtl[attr] = (org,rev)
                        break
        
            changeType = {M.Change.ADDED:    "added",
                          M.Change.MODIFIED: "modified",
                          M.Change.REMOVED:  "removed" }[c.getType()]
            
            #print "--DIFF",changeType,c.uxm().strip()
            #print " ","\n  ".join(["%s: %s->%s" % (k,v[0],v[1]) for (k,v) in c_dtl.items()])
            #print "  --",c.getTableName(),changeType,"db_row(%s)" % type(db_row),db_row,"crewid",crewid
            
            if len(c_dtl) == 0:
                #print "** Publish::get_change_descriptions: CuiDiffPublishRoster()"
                #print "** Ignored: No interesting attributes were changed."
                #print "** crew %s, diff: %s %s" % (crewid, changeType, c.uxm().strip())
                continue            
            
            def attrvalue(name, orig=True):
                v = c_dtl.get(name, [None, None])[1-bool(orig)]
                if isinstance(v, str):
                    return v.lstrip() or None
                else:
                    return v
                    
            dep_time = attrvalue("st")
            dep_stn  = attrvalue("adep")
            arr_time = attrvalue("et")
            arr_stn  = attrvalue("ades")
            pos      = attrvalue("pos")
            actcode  = attrvalue("activity")
            split    = False
        
            if table == "crew_activity":
                # Note regarding modification of an existing crew leg: 
                #   Primary key is (st, crew, activity), so if departure time or
                #   activity code has been changed, there will be both a REMOVED
                #   and a ADDED entry, instead of just a single MODIFIED entry.
                
                dt, crew, ac = RE_NON_ESCAPED_PLUS.split(entity_key)
                dep_time = dep_time or AbsTime(dt)
                actcode = actcode or ac
                crewleg = db_row.getCurrentP()
                if crewleg:
                    dep_stn = dep_stn or str(crewleg.getRefI("adep"))
                    arr_stn = arr_stn or str(crewleg.getRefI("ades"))
                    arr_time = arr_time or AbsTime(crewleg.et)
                arr_time = arr_time or (dep_time + ONE_MINUTE)
                arr_stn = arr_stn or dep_stn
                if changeType == "modified":
                    mod_arr_time = attrvalue("et", False) or arr_time
                    if mod_arr_time <= arr_time - ONE_DAY:
                        # The actual modification is that a +1day tail was REMOVED
                        changeType = "removed"
                        dep_time = mod_arr_time
                    elif mod_arr_time >= arr_time + ONE_DAY:
                        # The actual modification is that a +1day tail was ADDED
                        changeType = "added"
                        dep_time = arr_time
                        arr_time = mod_arr_time
                split = (arr_time - dep_time) > ONE_DAY
                
            elif table == "crew_flight_duty":
                udor, ac, ds, crew = RE_NON_ESCAPED_PLUS.split(entity_key)
                udor = AbsTime(udor)
                actcode = actcode or ac
                dep_stn = dep_stn or ds
                if c.getType() != M.Change.REMOVED:
                    if not (pos and dep_time and arr_stn and arr_time):
                        crewleg = db_row.getCurrentP()
                        pos = pos or str(crewleg.getRefI("pos"))
                        leg = crewleg.leg
                        dep_time = dep_time or AbsTime(leg.sobt)
                        arr_stn = arr_stn or str(leg.getRefI("ades"))
                        arr_time = arr_time or AbsTime(leg.sibt)
                else:
                    if not (dep_time and arr_stn and arr_time):
                        dep_stn_ref = TM.airport.getOrCreateRef(dep_stn)
                        try:
                            leg = TM.flight_leg[(udor, actcode, dep_stn_ref)]
                            dep_time = dep_time or AbsTime(leg.sobt)
                            arr_stn = arr_stn or str(leg.getRefI("ades"))
                            arr_time = arr_time or AbsTime(leg.sibt)
                        except M.EntityNotFoundError, e:
                            print "?Flight was removed instead of marked as canceled?",e
                    dep_time = dep_time or udor
                    arr_time = arr_time or (dep_time + ONE_MINUTE)
                    arr_stn = arr_stn or dep_stn
                    
            elif table == "crew_ground_duty":
                # Note regarding modification of an existing leg: 
                #   Primary key is (udor,uuid). Modification of "st" will *not*
                #   affect udor of an existing entry, so there will always be
                #   just a single MODIFIED entry.
                
                udor, task_id, crew = RE_NON_ESCAPED_PLUS.split(entity_key)
                udor = AbsTime(udor)
                if c.getType() != M.Change.REMOVED:
                    if not (pos and dep_stn and dep_time and arr_stn and arr_time and actcode):
                        crewleg = db_row.getCurrentP()
                        pos = pos or str(crewleg.getRefI("pos"))
                        leg = crewleg.task
                        dep_stn = dep_stn or str(leg.getRefI("adep"))
                        dep_time = dep_time or AbsTime(leg.st)
                        arr_stn = arr_stn or str(leg.getRefI("ades"))
                        arr_time = arr_time or AbsTime(leg.et)
                        actcode = actcode or str(leg.getRefI("activity") or "???")
                else:
                    if not (dep_stn and dep_time and arr_stn and arr_time and actcode):
                        task_id = task_id.replace('\\', '')
                        try:
                            row = TM.ground_task[(udor, task_id)]
                            dep_stn = dep_stn or str(row.getRefI("adep"))
                            dep_time = dep_time or AbsTime(row.st)
                            arr_stn = arr_stn or str(row.getRefI("ades"))
                            arr_time = arr_time or AbsTime(row.et)
                            actcode = str(row.getRefI("activity"))
                        except M.EntityNotFoundError, e:
                            print "?Task was removed instead of marked as canceled?",e
                    dep_stn = dep_stn or "???" 
                    dep_time = dep_time or udor
                    arr_time = arr_time or (dep_time + ONE_MINUTE)
                    arr_stn = arr_stn or dep_stn
                    actcode = actcode or "???"
            else:
                raise UnsupportedTableException("Table %s not supported"
                                                % c.getTableName)
                                                
            entity_key = entity_key.replace('\\', '')
            change = CNF.FlightDescriptor(entity_key,
                                          actCode=actcode,
                                          departureTime=dep_time,
                                          departureStation=dep_stn, 
                                          arrivalTime=arr_time,
                                          arrivalStation=arr_stn, 
                                          pos=pos,
                                          changeType=changeType, 
                                          table=table,
                                          split=split)
                            
            crew_period_start = PublishInformation.crew[crewid]['start_utc']
            crew_period_end = PublishInformation.crew[crewid]['pub_end_utc']

            if change.split:
                #print "SPLIT",change
                change.departureTime = max(change.departureTime, crew_period_start)
                end_time = min(change.arrivalTime, crew_period_end)
                while change.departureTime < end_time:
                    change.arrivalTime = AbsTime(change.departureTime + ONE_DAY)
                    #print "    +",change
                    if change.changeType != "removed":
                        #print "     ","xAPPEND"
                        changed_rows[crewid].append(change)
                    else:
                        # Ignore activity that is both added and removed.
                        for ix,leg in enumerate(changed_rows[crewid]):
                            if leg.isidenticalpact(change):
                                #print "     ","rREMOVE",leg
                                del changed_rows[crewid][ix]
                                break
                        else:
                            #print "     ","rAPPEND"
                            changed_rows[crewid].append(change)
                    change = copy.copy(change)
                    change.departureTime = AbsTime(change.arrivalTime)
            elif crew_period_start <= change.departureTime < crew_period_end:
                #print "    +",change
                if change.changeType != "removed":
                    #print "     ","xAPPEND"
                    changed_rows[crewid].append(change)
                else:
                    # Ingore activity that is both added and removed.
                    for ix,leg in enumerate(changed_rows[crewid]):
                        if leg.isidenticalpact(change):
                            #print "     ","rREMOVE",leg
                            del changed_rows[crewid][ix]
                            break
                    else:
                        changed_rows[crewid].append(change)
        
    # Now merge single-full-day changes to multi-day changes.
    # This means, together with the split performed above, that we'll handle
    # add/remove of adjacent pacts as single change events, disregarding if they
    # were performed on separate or single legs (I.e. remove of
    # two legs [VA 1-2jan + VA 2-3jan] will be regarded the same as remove of
    # a single [VA 1-3jan] leg.)
    
    for changes in changed_rows.values():
        changes.sort(key=lambda c: c.departureTime)
        ix = 0
        while ix < len(changes):
            if changes[ix].table == "crew_activity":
                mix = ix + 1
                while mix < len(changes):
                    if (changes[mix].table        == changes[ix].table
                    and changes[mix].changeType   == changes[ix].changeType
                    and changes[mix].actCode      == changes[ix].actCode
                    and changes[mix].arrivalTime  == changes[ix].departureTime):
                        changes[ix].arrivalTime = changes[mix].arrivalTime
                        del changes[mix]
                    else:
                        mix += 1
            ix += 1
                      
    #for crew, changes in changed_rows.items():
    #    print "CREW:",crew,"CHANGES---------------------------------------"
    #    for c in changes:
    #        print "    -",c
    #print "------------------------------------------------------------"
    
    T.stop()    
    return changed_rows
    
    
### Handling inform-now and do-not-publish periods ################

def markDoNotPublish(doNotPublish=True):
    """
    Called from Studio.
    Select crew and time periods that are to be marked as 'Do Not Publish'.
    """
    try:
        sel = HF.RosterDateSelection(validate_func=validate_mark_time_selection)
    except Exception, e:
        log("Publish::markDoNotPublish: Exception: %s" % e)
        return -1

    correct_any_period_inconsistency(sel.area, sel.crew)
    
    if doNotPublish:
        if not validate_pubnotinf_overlap(sel):
            log("Publish::markDoNotPublish: user cancelled")
            return -1
        add_do_not_publish_period(sel.crew, sel.st, sel.et)
    else:
        remove_do_not_publish_period(sel.crew, sel.st, sel.et)

    HF.redrawAllAreas(Cui.CrewMode)
    return 0


def markInformed(add=True):
    """
    Called from Studio.
    Select crew and time period that will be INFORMED at next save.
    If 'add' is False, the operation is reversed; any mark within the selected
    period will be unmarked.
    
    NOTE: When a period is marked for INFORM, any 'do_not_publish' mark in
          the selected period will be removed.
    """
    try:
        sel = HF.RosterDateSelection(validate_func=validate_mark_time_selection)
    except Exception, e:
        log("Publish::markInformed: Exception: %s" % e)
        return -1

    correct_any_period_inconsistency(sel.area, sel.crew)

    if add:
        add_informed_period(sel.crew, sel.st, sel.et)
    else:
        remove_informed_period(sel.crew, sel.st, sel.et)

    HF.redrawAllAreas(Cui.CrewMode)
    return 0


def validate_pubnotinf_overlap(sel):
    """
    Warn user if there are any published-not-informed changes in the given
    crosshair selection. For use in mark-do-not-inform.
    Return 'False' if the user is warned and chooses to cancel the operation. 
    """
    v = RaveEvaluator(sel.area, Cui.CrewMode, sel.crew,
        any_pubnotinf='publish.%%any_pubnotinf_in_period_hb%%(%s,%s)'
                      % (sel.st, sel.et))
                      
    if  v.any_pubnotinf:
        log("Publish::validate_pubnotinf_overlap: overlap exists")
        return carmstd.cfhExtensions.confirm("WARNING:"
            "\nThere are published changes that not yet have been informed."
            "\nThose changes will remain published!"
            "\nDo-Not-Publish only affects later changes." 
            "\n\nContinue?")
    
    return True
            
        
def validate_mark_time_selection(clicked_area, clicked_crew, clicked_time):
    """
    RosterDateSelection validation callback for markDoNotPublish/markInformed.
    Checks that the clicked-on time point lies between
      pp_start and the end of crew's SCHEDULED data
    """
   
    v = RaveEvaluator(clicked_area, Cui.CrewMode, clicked_crew,
        crew_empno=('crew.%extperkey%', lambda s: s or '?????'),
        release_end='publish.%crew_rostering_published_end%',
        pp_start_utc='publish.%crew_loaded_data_start_utc%',
        crew_stn='crew.%%station_at_date%%(%s)' % clicked_time)
    
    if not (v.crew_stn or "").strip():
        return (
            "You clicked on %s (UTC).\n"
            "\n"
            "Crew %s (%s) has no home base defined for that point in time.\n"
            "Please select another time point.\n"
            % (clicked_time, v.crew_empno, clicked_crew))

    if clicked_time >= v.release_end:
        if v.release_end <= AbsTime("1Jan1901"):
            return (
                "For crew %s (%s), there is no released data.\n"
                % (v.crew_empno, clicked_crew))
        else:
            return (
                "You clicked on %s (UTC).\n"
                "\n"
                "For crew %s (%s), there is only released data until %s.\n"
                "Please select a time point before that.\n"
                % (clicked_time, v.crew_empno, clicked_crew, v.release_end))
        
    if clicked_time < v.pp_start_utc:
        return (
            "You clicked on %s (UTC).\n"
            "\n"
            "For crew %s (%s), the plannable period starts at %s.\n"
            "Please select a time point after that.\n"
            % (clicked_time, v.crew_empno, clicked_crew, v.pp_start_utc))
        
    return None

def correct_any_period_inconsistency(area, crew):
    """
    When the plan is refreshed, inconsistencies may be created in the
    tables containing periods for do-not-publish and inform-now marks.
    
    - Conflicting concurrent updates may result in period overlaps.
    - Also, is some cases the rave and studio model are unsynched after refresh.
    
    Such an inconsistency can lead to problems when the user manipulates the
    markings. In order to prevent that, this function is called before the
    actual table updates are performed when the user edits a mark.
    
    The outcome will be a studio model that is up-to-date according to rave,
    and with no overlapping periods.
    
    Note that both types of marks are handled in this function, since the
    marking of one may affect the other. (A period can't be both dnp and inf.)
    """
    def get_rave(crew):
        """
        Get do-not-publish and inform-now periods as Rave sees them.
        """
        rv = RaveEvaluator(area, Cui.CrewMode, crew).rEval(
             *(['fundamental.%loaded_data_period_start%']
              +['publish.%%do_not_publish_start%%(%d)' % i for i in range(1,11)]
              +['publish.%%do_not_publish_end%%(%d)' % i for i in range(1,11)]
              +['publish.%%inform_start%%(%d)' % i for i in range(1,11)]
              +['publish.%%inform_end%%(%d)' % i for i in range(1,11)])
              )
        return (rv[0],
                sorted((s,e) for s,e in [(rv[i],rv[i+10]) for i in range( 1,11)]
                             if s is not None),
                sorted((s,e) for s,e in [(rv[i],rv[i+10]) for i in range(21,31)]
                             if s is not None),
                )
                
    def get_mdl(creator, period_start):
        """
        Get do-not-publish or inform-now periods from the model.
        """
        return sorted((row.start_time, row.end_time) for row in creator
                      if row.end_time > period_start)
                        
    def check_reload_rave(creator, mdl_periods, rave_periods):
        """
        For do-not-publish or inform-now periods, compare rave and model.
        Correct in case of differencies; Rave "wins".
        """
        if mdl_periods == rave_periods:
            return False
        print "Publish::correct_any_period_inconsistency: crew '%s' WARNING" % creator.crew
        print " ",creator.table.table_name(),"inconsistency. Rave/model mismatch."
        print "  rave: ",[(str(s),str(e)) for s,e in rave_periods]
        print "  model:",[(str(s),str(e)) for s,e in mdl_periods]
        print "  Updating model according to Rave..."
        for row in creator:
            for st,et in mdl_periods:
                if row.start_time == st and row.end_time == et:
                    row.remove()
                    break
        for st,et in rave_periods:
            creator.create(st, et)
        modcrew.add(creator.crew)
        creator.reload()
        return True
        
    def check_resolve_overlaps(creator, mdl_periods):
        """
        For do-not-publish or inform-now periods, check for overlaps in model.
        Correct if needed.
        """
        for i,(st,en) in enumerate(mdl_periods[:-1]):
            if en > mdl_periods[i+1][0]:
                break
        else:
            return False
        print "Publish::correct_any_period_inconsistency: crew '%s' WARNING" % creator.crew
        print " ",creator.table.table_name(),"inconsistency. Overlapping entries."
        print " ",[(str(s),str(e)) for s,e in mdl_periods]
        print "  Removing overlaps in model..."
        for st,en in mdl_periods:
            add_period(creator, st, en)
        creator.reload()
        modcrew.add(creator.crew)
        return True
        
    # Correct any inconsistencies in do-not-publish and inform-now periods.
    # Do detailed debug logging in case of errors.
                        
    t = time.time()

    period_start, rave_dnp, rave_inf = get_rave(crew)

    dnp_creator = DoNotPublishTableRowCreator(crew)
    inf_creator = InformedTempTableRowCreator(crew)
    mdl_dnp = get_mdl(dnp_creator, period_start)
    mdl_inf = get_mdl(inf_creator, period_start)
    
    mod_dnp = mod_inf = False
    if check_reload_rave(dnp_creator, mdl_dnp, rave_dnp):
        mdl_dnp = get_mdl(dnp_creator, period_start)
        mod_dnp = True
    if check_reload_rave(inf_creator, mdl_inf, rave_inf):
        mdl_inf = get_mdl(inf_creator, period_start)
        mod_inf = True
            
    if check_resolve_overlaps(dnp_creator, mdl_dnp):
        mod_dnp = True
    if check_resolve_overlaps(inf_creator, mdl_inf):
        mod_inf = True
    
    if mod_dnp or mod_inf:
        print "Publish::correct_any_period_inconsistency: Result after correction:"
        period_start, rave_dnp, rave_inf = get_rave(crew)
        if mod_dnp:
            mdl_dnp = get_mdl(dnp_creator, period_start)
            print "  dnp rave: ",[(str(s),str(e)) for s,e in rave_dnp]
            print "  dnp model:",[(str(s),str(e)) for s,e in mdl_dnp]
        if mod_inf:
            mdl_inf = get_mdl(inf_creator, period_start)
            print "  inf rave: ",[(str(s),str(e)) for s,e in rave_inf]
            print "  inf model:",[(str(s),str(e)) for s,e in mdl_inf]
        
    t = time.time() - t
    print "Publish::correct_any_period_inconsistency: %0.02f" % t
        

def add_do_not_publish_period(crew, st, et):
    try:
        _check_informed_period(InformedTempTableRowCreator(crew), st, et)
    except HF.RosterSelectionError, se:
        carmstd.cfhExtensions.show(str(se), title=se.title)
        return 1
    print "Publish::add_do_not_publish_period:",st,et,"crew:",crew
    add_period(DoNotPublishTableRowCreator(crew), st, et)
    modcrew.add(crew)


def remove_do_not_publish_period(crew, st, et):
    print "Publish::remove_do_not_publish_period:",st,et,"crew:",crew
    remove_period(DoNotPublishTableRowCreator(crew), st, et)
    modcrew.add(crew)
    
def set_roster_attribute(attr, crew, st, et, string=None, reltime=None, abstime=None, integer=None):
    print "Publish::set_roster_attribute:",attr,st,et,"crew:",crew
    if not string  is None: print "   string:",string
    if not reltime is None: print "  reltime:",reltime
    if not abstime is None: print "  abstime:",abstime
    if not integer is None: print "  integer:",integer
    add_period(RosterAttributeTableRowCreator(attr, crew), st, et)

def remove_roster_attribute(attr, crew, st, et):
    print "Publish::remove_roster_attribute:",attr,st,et,"crew:",crew
    remove_period(RosterAttributeTableRowCreator(attr, crew), st, et)

def roster_attribute_overlaps(attr, crew, st, et):
    print "Publish::roster_attribute_overlaps:",attr,st,et,"crew:",crew
    overlaps = set()
    for row in sorted(RosterAttributeTableRowCreator(attr, crew), key=lambda row: row.start_time):
        if row.start_time < et and row.end_time > st:
            added = False
            for prow in overlaps:
                if row.start_time <= prow.end_time:
                    prow.end_time = max(row.end_time, prow.end_time)
                    added = True
            if not added: overlaps.add(row)
    print "Publish::roster_attribute_overlaps:",len(overlaps),"overlap(s)"
    return overlaps

def add_informed_period(crew, st, et):
    """
    Add 'Informed' period. NOTE: If this period overlaps a 'Do Not Publish'
    period then the 'Do Not Publish' period will be adjusted, so the 'Informed'
    information also gets published.
    Note: HACK-TO-HANDLE-SAVEBUTTON-DIMMING-CORRECTLY:
        The dimming of Studio's save-button depends on updates on persistent
        tables. In order for updates in the temporary informed-table to be
        correctly reflected as save dimming/undimming, we maintain shadow
        entries in the persistent do_not_publish table. These entries will
        be removed before save (see _remove_dummy_publish_periods).
    """
    print "Publish::add_informed_period:",st,et,"crew:",crew
    add_period(InformedTempTableRowCreator(crew), st, et)
    remove_do_not_publish_period(crew, st, et)
    modcrew.add(crew)
    # HACK-TO-HANDLE-SAVEBUTTON-DIMMING-CORRECTLY: 2 lines
    delta = RelTime(1440*30000)
    add_period(DoNotPublishTableRowCreator(crew), st - delta, et - delta)


def remove_informed_period(crew, st, et):
    """
    Remove 'Informed' marker.
    """
    print "Publish::remove_informed_period:",st,et,"crew:",crew
    remove_period(InformedTempTableRowCreator(crew), st, et)
    # HACK-TO-HANDLE-SAVEBUTTON-DIMMING-CORRECTLY: 2 lines
    delta = RelTime(1440*30000)
    remove_period(DoNotPublishTableRowCreator(crew), st - delta, et - delta)

    
# HACK-TO-HANDLE-SAVEBUTTON-DIMMING-CORRECTLY: 1 funcdef
# This function is called from publishPostSave in order to get rid of 
# the dummy entries managed by add_informed_period/remove_informed_period.
def _remove_dummy_publish_periods():
    itt = InformedTempTable()
    delta = RelTime(1440*30000)
    for row in itt:
        remove_period(DoNotPublishTableRowCreator(row.crew),
                       row.start_time - delta,
                       row.end_time - delta)

        
def _check_informed_period(creator, st, et):
    """
    Check that no 'Informed' marker is set in selected period.
    """
    for row in creator:
        if st < row.end_time and row.start_time < et: # Overlap
            raise HF.RosterSelectionError(
                    'A period that has been marked "Informed"'
                    ' can not be set to "Do Not Publish".')


def add_period(creator, st, et):
    """
    Overlap handling:

        selection:        |===|     or    |===|

    A:  row:            |--------|      |---|
        result:         |--------|      |-----|     (adjust end time)

    B:  row:               |-|              |-----|
        result:           |---|           |-------| (new record)
    """
    overlap_rows = []
    for row in creator:
        if st <= row.end_time and row.start_time <= et: # Overlap
            overlap_rows.append(row)
    if overlap_rows:
        _min, _max = None, None
        for row in overlap_rows:
            if _min is None or row.start_time < _min:
                _min = row.start_time
            if _max is None or row.end_time > _max:
                _max = row.end_time
            row.remove()
        creator.create(min(st, _min), max(et, _max))
    else:
        creator.create(st, et)
    creator.reload()


def remove_period(creator, st, et):
    """
    Overlap handling:

        selection:        |===|

    A1: row:            |-xxxxx--|
        result:         |-|   |--|   (split)

    A2: row:               xxxx--|
        result:               |--|   (adjusted start time)

    B1: row:            |-xxx|
        result:         |-|          (adjusted end time)

    B2: row:               |x|
        result:                      (removal)
    """
    overlaps = False
    for row in creator:
        if st <= row.end_time and row.start_time <= et: # Overlap
            if row.end_time > et:
                row_end_time = row.end_time
                if row.start_time < st: # (A1)
                    row.end_time = st
                else:                   # (A2)
                    row.remove()
                creator.create(et, row_end_time)
            else:
                if row.start_time < st: # (B1)
                    row.end_time = st
                else:                   # (B2)
                    row.remove()
            overlaps = True
    if overlaps:
        creator.reload()

def insertInformedData():
    """
    Copy information from temporary table to persistent table
    for audit trail reasons.
    """
    itt = InformedTempTable()
    ct = 0
    for row in itt:
        ct += 1
        InformedTableRowCreator(row.crew).create(row.start_time,
                       row.end_time)
        InformedTableRowCreator(row.crew).reload()
    log('insertInformedData:: Data inserted in persistent table. Rows: %d' % ct)
    
#########################################################################
### Display roster revision (SCHEDULED/PUBLISHED/INFORMED/DELIVERED). ###
### Note: Studio can only show an old revision for one crew at a time ###
#########################################################################

def showOriginallyPublishedRoster():
    return _showPublishedRoster(ROSTERING_PUBLISHED_TYPE)

def showLatestPublishedRoster():
    return _showPublishedRoster(TRACKING_PUBLISHED_TYPE)

def showLatestInformedRoster():
    return _showPublishedRoster(TRACKING_INFORMED_TYPE)

def showLatestDeliveredRoster():
    return _showPublishedRoster(TRACKING_DELIVERED_TYPE)

def hidePublishedRoster():
    Cui.CuiHidePublishedRosters(Cui.gpc_info)
    return 0

def _showPublishedRoster(ptype):
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    crew = Cui.CuiCrcEvalString(Cui.gpc_info, area, "object", "crew.%id%")
    plabel = "%s Roster" % ptype.capitalize()
    Cui.CuiShowPublishedRoster(Cui.gpc_info, area, crew, ptype, plabel)
    return 0

if __name__ == '__main__':
    pass

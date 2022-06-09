
# [acosta:08/105@22:06] Created.

"""
Common actions and logic for PreRostering publication.

The end user can see periods that were published in Studio.  By allowing end
user to mark additional start and end points, this interval can be extended.

Upon save all modified crew will be identified, and their publication periods
will be published again, together with those new periods that were marked by
the user.
"""

import Cui
import Gui
import carmensystems.rave.api as rave
import carmusr.preplanning.Publish
import carmusr.HelperFunctions as HF
import carmusr.modcrew as modcrew
import carmusr.tracking.informedtemptable
import traceback
from tm import TM
from AbsTime import AbsTime
from Variable import Variable
from utils.guiutil import UpdateManager
from utils.rave import RaveIterator
from utils.rave import RaveEvaluator
from utils.time_util import IntervalSet, TimeInterval
from modelserver import EntityNotFoundError 

# globals ================================================================{{{1
# Rave parameter used for temporary table (for Rudobs).
temp_table_param = 'studio_config.%tmp_publish_this_table%'

# Used for passing information between pre- and post- save steps.
__publication_list = None


# Help classes ==========================================================={{{1

# RosterIter -------------------------------------------------------------{{{2
class RosterIter(RaveIterator):
    """Iterate all crew."""
    def __init__(self):
        iterator = RaveIterator.iter('iterators.roster_set')
        fields = {'id': 'crew.%id%'}
        RaveIterator.__init__(self, iterator, fields)


# PubPeriodIter ----------------------------------------------------------{{{2
class PubPeriodIter(RaveIterator):
    """Iterate publish periods for crew member."""
    def __init__(self, ptype=carmusr.preplanning.Publish.TRACKING_PUBLISHED_TYPE):
        iterator = RaveIterator.times(10000,
            where=(
                'not void(publish.%%t_pubcid%%(crew.%%id%%, "%s"))' % ptype,
                'publish.%%t_pubend%%(crew.%%id%%, "%s") > fundamental.%%pp_start%%' % ptype))
        fields = {
            'pubstart': 'publish.%%t_pubstart%%(crew.%%id%%, "%s")' % ptype,
            'pubend': 'publish.%%t_pubend%%(crew.%%id%%, "%s")' % ptype,
        }
        RaveIterator.__init__(self, iterator, fields)


# PublishThisTempTableRowCreator -----------------------------------------{{{2
class PublishThisTempTableRowCreator:
    """Handle updates and iterations of temporary table."""
    def __init__(self, crew):
        self.crew = crew
        self.table = init()

    def __iter__(self):
        return iter(self.table.search('(crew=%s)' % self.crew))

    def create(self, st, et):
        rec = self.table.create((self.crew, st))
        rec.end_time = et
        return rec

    def reload(self):
        Cui.CuiReloadTable(self.table.table_name(), Cui.CUI_RELOAD_TABLE_SILENT)


# functions =============================================================={{{1

# init -------------------------------------------------------------------{{{2
def init():
    """
    Return TempTable object (which will create temporary table on first call).
    """
    return carmusr.tracking.informedtemptable.InformedTempTable(
            temp_table_param)


# mark4publish -----------------------------------------------------------{{{2
def mark4publish(mark=False, mode=""):
    """
    Called from Studio menu.

    Mark period in roster for publication. If mark is 'False', then remove
    publication period.
    Mode = MARKED will publish all marked legs in window
    """

    publish_list = []
    if mode.upper() == "MARKED":
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        marked_legs = Cui.CuiGetLegs(Cui.gpc_info, area, 'marked')
        for markeg_leg in marked_legs:
            leg = HF.LegObject(str(markeg_leg),area)
            (crew_id, start_t, end_t,
             employed, empno)= leg.eval('crew.%id%',
                                        'publish.%pre_studio_publish_leg_start_time%',
                                        'publish.%pre_studio_publish_leg_end_time%',
                                        'crew.%has_employment_for_leg%',
                                        'crew.%extperkey%')
            if not employed:
                Gui.GuiMessage('Crew %s has no employment for leg %s (UTC)'%(empno,start_t))
            else:
                publish_list.append((crew_id, start_t, end_t))
    else:
        try:
            sel = HF.RosterDateSelection(hb=True)
            publish_list.append((sel.crew, sel.st, sel.et))
        except Exception, e:
            print "mark4publish: Exception:", e
            return -1
    for crew_id, start_t, end_t in publish_list:
        row = PublishThisTempTableRowCreator(crew_id)
        
        if mark:
            carmusr.preplanning.Publish.add_period(row, start_t, end_t)
            modcrew.add(crew_id)
        else:
            carmusr.preplanning.Publish.remove_period(row, start_t, end_t)
    _mark_dirty(True)
    HF.redrawAllAreas(Cui.CrewMode)
    return 0

def _get_time_str(start=True):
    """
    Start = True makes function use leg.%start_utc% and round_down
    """
    #Stolen from hb2utc and utc2hb in HelperFunctions, same as RosterDateSelect
    time = ('%end_utc%','%start_utc%')[start]
    updown = ('up','down')[start]
    local = 'round_%s(station_localtime(fundamental.%%base2station%%('%updown+\
            'crew.%%base_at_date%%(leg.%s)),leg.%s),24:00)'%(time, time)    
    return 'station_utctime('+\
           'fundamental.%%base2station%%(crew.%%base_at_date%%(%s)), %s)'%(local, local)


# pre_save_published -----------------------------------------------------{{{2
def pre_save_publish():
    """
    Called from FileHandlingExt before actual save operation.

    Build list of crew members and their publication intervals.
    """
    ptype = carmusr.preplanning.Publish.TRACKING_PUBLISHED_TYPE
    crew_list = modcrew.get()
    Cui.CuiDisplayGivenObjects(Cui.gpc_info, Cui.CuiScriptBuffer, Cui.CrewMode,
            Cui.CrewMode, crew_list)
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, 'WINDOW')

    ri = RosterIter()
    pi = PubPeriodIter()
    ri.link(pi)

    cmap = {}
    cmap_dnp = {}
    for crew in ri.eval('default_context'):
        cmap[crew.id] = IntervalSet()
        cmap_dnp[crew.id] = IntervalSet()
        for period in crew:
            cmap[crew.id].add(TimeInterval(period.pubstart, period.pubend))

        # Read do_not_publish periods
        for period in TM.crew[(crew.id,)].referers("do_not_publish", "crew"):
            re = RaveEvaluator(Cui.CuiScriptBuffer, Cui.CrewMode, crew.id,
                               start_dnp = 'crew.%%utc_time%%(%s)' % period.start_time,
                               end_dnp = 'crew.%%utc_time%%(%s)' % period.end_time,)

            cmap_dnp[crew.id].add(TimeInterval(re.start_dnp, re.end_dnp))

        cmap[crew.id] = cmap[crew.id] - cmap_dnp[crew.id]

    for rec in init():
        i = TimeInterval(rec.start_time, rec.end_time)
        if rec.crew in cmap:
            cmap[rec.crew].add(i)
        else:
            cmap[rec.crew] = IntervalSet([i])

    # Compress intervals, maybe unnecessary??
    for crew in cmap:
        cmap[crew].merge()

    global __publication_list
    __publication_list = []
    for crew in cmap:
        for interval in sorted(cmap[crew]):
            __publication_list.append((crew, ptype, int(interval.first),
                int(interval.last)))
    if __publication_list:
        hidePublished()


# post_save_publish ------------------------------------------------------{{{2
def post_save_publish():
    """
    Called from FileHandlingExt after actual save has been done.

    Iterate list of crew to be published and run CuiPublishRosters.
    """
    global __publication_list
    if __publication_list is None:
        raise ValueError("No crew to publish, pre_save_publish() was not called.")

    UpdateManager.start()
    if __publication_list:
        _mark_dirty(False)
        Cui.CuiPublishRosters(Cui.gpc_info, __publication_list, 
                "PRE-ROSTERING PUBLISH",
                Cui.CUI_PUBLISH_ROSTER_SKIP_MODIFIED_CHECK)
        UpdateManager.setDirtyTable('published_roster')
        t_table = init()
        t_table.clear()
        UpdateManager.setDirtyTable(t_table.table_name())
    modcrew.clear()
    UpdateManager.done()
    __publication_list = None


# hidePublished ----------------------------------------------------------{{{2
# Use function defined in carmusr.preplanning.Publish.
hidePublished = carmusr.preplanning.Publish.hidePublishedRoster


# showScheduled ----------------------------------------------------------{{{2
def showScheduled():
    """
    Called from Studio menu.
    Show Roster as published from Rostering.
    """
    return _show(carmusr.preplanning.Publish.ROSTERING_PUBLISHED_TYPE)


# showPublished ----------------------------------------------------------{{{2
def showPublished():
    """
    Called from Studio menu.
    Show Roster as published from Tracking (and PreRostering).
    """
    return _show(carmusr.preplanning.Publish.TRACKING_PUBLISHED_TYPE)


# private functions ======================================================{{{1

# _mark_dirty ------------------------------------------------------------{{{2
def _mark_dirty(on=True):
    """
    Create dummy entry in todo, to trigger the menu mode ^SavePlan.
    See Bugzilla #26468.
    """
    key = "DuMmY"
    def remove():
        try:
            rec = TM.todo[key]
            rec.remove()
        except EntityNotFoundError:
            pass
    try:
        if on:
            remove()
            try: 
                TM.todo.create(key)
            except:
                TM.todo[key].si += "Y"
        else:
            remove()
    except Exception, e:
        print e


# _show ------------------------------------------------------------------{{{2
def _show(ptype):
    """
    Identify selected crew and load Roster with publication tag 'ptype'.
    """
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    crew_var = Variable("", 30)
    Cui.CuiGetSelectionObject(Cui.gpc_info, area, Cui.CrewMode, crew_var)
    # Set a parameter in order to inform the user of which type of published
    # roster is being viewed
    plabel= "%s Roster" % ptype.capitalize()
    Cui.CuiShowPublishedRoster(Cui.gpc_info, area, crew_var.value, ptype, plabel)
    return 0


# __main___ =============================================================={{{1
if __name__ == '__main__':
    """Basic tests only."""
    pre_save_publish()
    post_save_publish(True)


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof

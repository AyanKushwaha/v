

"""
To keep track of crew changes (that are not necessarily related to changes in
assignments).

This could for instance be that the publish information for a crew member has
changed.
"""

import os
import Cui, Gui
import carmensystems.studio.plans.LocallyModifiedCrew as LMC
import modelserver as M
import tm
from AbsTime import AbsTime

class AdditionalModifiedCrew:

    
    # Class to keep modified crew that are not marked as modified by studio.
    # basically just a wrapper for a temp table of crew ids"""

    @property
    def tmp_modcrew(self):

        try:
            return  tm.TM.tmp_modcrew
        except M.TableNotFoundError:
            tm.TM.createTable("tmp_modcrew",
                              [M.StringColumn("crew", "Crew")],
                              [])
            return tm.TM.tmp_modcrew
        
    def add(self, crew):
        try:
            tmp = self.tmp_modcrew[crew,]
        except M.EntityNotFoundError:
            tmp = self.tmp_modcrew.create((crew,))
            
    def force(self, crew):
        self.add(crew.id)
        try:
            inf = tm.TM.informed[(crew, AbsTime("17Jan1917"))]
            inf.enddate = AbsTime(int(inf.enddate) + 1)
        except:
            inf = tm.TM.informed.create((crew, AbsTime("17Jan1917")))
            inf.enddate = inf.startdate
        print "modcrew::force_cct: crew",crew.id,"set as locally modified"

    def clear(self):
        for mod in self.tmp_modcrew:
            try:
                crew = tm.TM.crew[(mod.crew,)]
                tm.TM.informed[(crew, AbsTime("17Jan1917"))].remove()
            except:
                pass
        self.tmp_modcrew.removeAll()

    def get(self):
        return [str(res.crew) for res in  self.tmp_modcrew]

# additionally_modified_crew ============================================={{{1
# Instance of the wrapper object.
additionally_modified_crew = AdditionalModifiedCrew()

# get ===================================================================={{{1
def get():
    """Return unsorted list of crew that has been modifed, either known by
    Studio, or, by using the add() function below."""

    print "modcrew::get(): The following crew has manually been added to modified crew: %s" % (additionally_modified_crew.get())

    if bool(os.environ.get('EXTERNAL_PUBLISH')):
        # ExtPublishServer must be imported from the main namespace
        # to guarantee one unique class instance...
        # ...but it is only available when running SAS_EXT_PUBLISH_SERVER
        # ...and no, it is not available when modcrew is initially loaded
        from __main__ import ExtPublishServer
        return ExtPublishServer.getExtPublishCrew()
    elif bool(os.environ.get('EXTERNAL_PUBLISH_STANDALONE')): 
        from dig.extpublishserver import ExtPublishServer
        return ExtPublishServer.getExtPublishCrew(cache=True)    

    return list(set(additionally_modified_crew.get() + list(Cui.CuiGetLocallyModifiedCrew(Cui.gpc_info)))) # Create set inbetween to make list unique


# add ===================================================================={{{1
def add(crewid):
    """Add one additional crew member to be marked as modified."""
    print "modcrew::add(): Adding %s" % (crewid)
    additionally_modified_crew.add(crewid)

    
    
# force =================================================================={{{1
def force(studio_area=Cui.CuiWhichArea):
    """Add marked crew members in Studio to be marked as modified.
    Force Studio to regard these crew as "dirty" to enable save button.
    This is done by adding dummy rows to the 'informed' table.
    These rows are removed at clear(), which must be called before save."""
    for crewid in Cui.CuiGetCrew(Cui.gpc_info, studio_area, "MARKEDLEFT"):
        crew = tm.TM.crew[(crewid,)]
        additionally_modified_crew.force(crew)
force_cct = force


# force_in_plan =========================================================={{{1
def force_in_plan():
    studioarea = Cui.CuiScriptBuffer
    Cui.CuiDisplayObjects(Cui.gpc_info, studioarea, Cui.CrewMode, Cui.CuiShowAll)
    force(studio_area=studioarea)


# clear =================================================================={{{1
def clear():
    """Clear additionally modified crew."""

    additionally_modified_crew.clear()

    print "modcrew::clear(): Clearing modified crew"

    if bool(os.environ.get('EXTERNAL_PUBLISH')):
        from __main__ import ExtPublishServer
        ExtPublishServer.clearExtPublishCrew()
    elif bool(os.environ.get('EXTERNAL_PUBLISH_STANDALONE')): 
        from dig.extpublishserver import ExtPublishServer
        ExtPublishServer.clearExtPublishCrew()
    


# show_modified_rosters =================================================={{{1
def show_modified_rosters():
    """Used by button 'Show locally modified crew.'"""

    lmc = LMC.LocallyModifiedCrew()
    crew = []
    crew = get()
    if not crew:
        Gui.GuiNotice("There are no Locally Modified Crew")
        return

    newArea = lmc.initShowArea()
    Cui.CuiDisplayGivenObjects(Cui.gpc_info, lmc.showArea, Cui.CrewMode,
                               Cui.CrewMode, crew, 0)
    Gui.GuiCallListener(Gui.RefreshListener)
    

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

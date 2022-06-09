'''
Created on 23 sep 2010

@author: rickard.petzall
'''

from carmtest.framework import *

class tracking_001_StandbyCallout(MacroTestFixture):
    "Standby Callout"
    def setUp(self):
        self.setNowTime(self.raveExpr('fundamental.%pp_start%'))

    @REQUIRE("PlanLoaded","Tracking")
    @REQUIRE("NotMigrated")
    def __init__(self):
        MacroTestFixture.__init__(self)
        self.crew = self.getCrew(cat="F", max_crew=100).keys()
        self.trips = [str(x[1]) for x in self.getTrips(('trip.%start_utc%>fundamental.%now%',
                                                        'trip.%num_active_legs%>0',
                                                        'trip.%num_legs%>1',
                                                        'trip.%is_open_pilot_trip%',
                                                        'trip.%has_only_flight_duty%'), eval=('crr_identifier'))[0]]
        
        self.log("Potential trips: %d" % len(self.trips))
        
    def test_001_Callout(self):
        import Cui
        assert self.crew, "No crew found"
        assert self.trips, "No trips found"
        self.select(0, self.crew)
        self.select(-1, trip=self.trips)
        for _,crew,id,start,end,hb in self.getLegs('leg.%in_pp% and leg.%is_standby_at_home% and not duty.%is_standby_callout%', 
                           area=0,
                           eval=('crew.%id%','leg_identifier','leg.%start_utc%','leg.%end_utc%','leg.%homebase%')):
            print "Looking at crew",crew
            for _, crr_identifier,start in self.getLegs(('trip.%%start_utc%%>%s' % start,
                                 'trip.%%end_utc%%<%s'% end,
                                 'trip.%%homebase%%="%s"'% hb),
                                 area=-1,
                                 eval=('crr_identifier', 'trip.%start_utc%+trip.%check_in%')):
                l = list(self.table("crew_notification").search("(&(crew=%s)(st<%s)(st>%s))" %(crew, start, start+RelTime(-24,0))))
                if len(l) > 0:
                    print "Already have notification, skip this"
                else:
                    self.log("Taking crew %s, trip UDOR %s" % (crew, start))
                    self.select(0, crew)
                    self.select(1, trip=crr_identifier)
                    self.doStandbyCallout(start+RelTime(1))
                    import carmusr.ConfirmSave as cs
                    old_dialog_value = cs.skip_confirm_dialog
                    cs.skip_confirm_dialog = True
                    Cui.CuiSavePlans(Cui.gpc_info, Cui.CUI_SAVE_DONT_CONFIRM+Cui.CUI_SAVE_SILENT+Cui.CUI_SAVE_FORCE)
                    cs.skip_confirm_dialog = cs
                    l = list(self.table("crew_notification").search("(&(crew=%s)(st<%s)(st>%s))" %(crew, start, start+RelTime(-24,0))))
                    assert len(l) == 1, "Notification was not created"
                    self.log("Notification deadline: %s" % l[0].deadline)
                    return
        self.dataError("Unable to find a standby and open trip that could be assigned")
        #assert len(crew) == 1, "Incorrect number of crew"
        #self._load(crew)
    def doStandbyCallout(self, startUtc, calloutTimeOverride=None):
        bp = ['<FormData name="Standby Form">']
        if calloutTimeOverride:
            pass
        bp.append('<FormInput  name="B_OK" value="" type="Done" />')
        bp.append('</FormData>') 
        return self.dragDropAssign(True, fromArea=1, toArea=0, dragTime=startUtc, dropTime=startUtc, bypass='\n'.join(bp))
        
    # Candidate for a base class
    def dragDropAssign(self, wholeTrip, fromArea, toArea, dragTime, dropTime, dragRow=0, dropRow=0, bypass=""):
        f = """<All>
<Command label="Select" script="GuiProcessInteraction(&quot;SelectInteractor&quot;, &quot;&quot;)" level="0">
<AreaId id=""/>
<Object position="" identity=""/>
<InteractionData type="SelectInteractor" id="">
<InteractionItem key="Area" value="%(fromArea)s" />
<InteractionItem key="Elevation" value="46" />
<InteractionItem key="Operation" value="2" />
<InteractionItem key="Row" value="%(dragRow)s" />
<InteractionItem key="Subwindow" value="2" />
<InteractionItem key="Time" value="%(dragTime)s" />
</InteractionData>
<CommandAttributes label="Select" script="GuiProcessInteraction(&quot;SelectInteractor&quot;, &quot;&quot;)" level="0" returnVal="0" />
</Command>
<Command label="Select" script="GuiProcessInteraction(&quot;SelectInteractor&quot;, &quot;&quot;)" level="0">
<AreaId id=""/>
<Object position="" identity=""/>
<InteractionData type="SelectInteractor" id="">
<InteractionItem key="Area" value="%(fromArea)s" />
<InteractionItem key="Elevation" value="46" />
<InteractionItem key="Operation" value="0" />
<InteractionItem key="Row" value="%(dragRow)s" />
<InteractionItem key="Subwindow" value="2" />
<InteractionItem key="Time" value="%(dragTime)s" />
</InteractionData><CommandAttributes label="Select" script="GuiProcessInteraction(&quot;SelectInteractor&quot;, &quot;&quot;)" level="0" returnVal="0" />
</Command>"""
        if wholeTrip:
            f += """<Command label="Select" script="GuiProcessInteraction(&quot;SelectInteractor&quot;, &quot;&quot;)" level="0">
<AreaId id=""/>
<Object position="" identity=""/>
<InteractionData type="SelectInteractor" id="">
<InteractionItem key="Area" value="%(fromArea)s" />
<InteractionItem key="Elevation" value="46" />
<InteractionItem key="Operation" value="5" />
<InteractionItem key="Row" value="%(dragRow)s" />
<InteractionItem key="Subwindow" value="2" />
<InteractionItem key="Time" value="%(dragTime)s" />
</InteractionData><CommandAttributes label="Select" script="GuiProcessInteraction(&quot;SelectInteractor&quot;, &quot;&quot;)" level="0" returnVal="0" />
</Command>"""
            f += """<Command label="Select" script="GuiProcessInteraction(&quot;SelectInteractor&quot;, &quot;&quot;)" level="0">
<AreaId id=""/>
<Object position="" identity=""/>
<InteractionData type="SelectInteractor" id="">
<InteractionItem key="Area" value="%(fromArea)s" />
<InteractionItem key="Elevation" value="46" />
<InteractionItem key="Operation" value="5" />
<InteractionItem key="Row" value="%(dragRow)s" />
<InteractionItem key="Subwindow" value="2" />
<InteractionItem key="Time" value="%(dragTime)s" />
</InteractionData><CommandAttributes label="Select" script="GuiProcessInteraction(&quot;SelectInteractor&quot;, &quot;&quot;)" level="0" returnVal="0" />
</Command>"""
        f += """

<Command label="Assign" script="CuiExecuteDrop(&quot;carmusr.tracking.DragDrop.AssignMarkedTrips&quot;)" level="0">
<AreaId id=""/>
%(bypass)s
<InteractionData type="CommandState" id="">
<InteractionItem key="areaId" value="0" />
<InteractionItem key="button" value="0" />
<InteractionItem key="row" value="%(dragRow)s" />
<InteractionItem key="subWinId" value="2" />
<InteractionItem key="tim" value="%(dropTime)s" />
</InteractionData>
<InteractionData type="DragDropFromAction" id="">
<InteractionItem key="DragDropCtrlParam" value="0" />
<InteractionItem key="areaId" value="%(fromArea)s" />
<InteractionItem key="row" value="%(dragRow)s" />
<InteractionItem key="subWinId" value="2" />
<InteractionItem key="tim" value="%(dragTime)s" />
</InteractionData>
<InteractionData type="DragDropToAction" id="">
<InteractionItem key="areaId" value="%(toArea)s" />
<InteractionItem key="button" value="1" />
<InteractionItem key="row" value="%(dropRow)s" />
<InteractionItem key="subWinId" value="2" />
<InteractionItem key="tim" value="%(dropTime)s" />
</InteractionData>

<CommandAttributes label="Assign" script="CuiExecuteDrop(&quot;carmusr.tracking.DragDrop.AssignMarkedTrips&quot;)" level="0" returnVal="0" />
</Command>
</All>"""
        f = f % {'fromArea':fromArea, 'toArea':toArea,'dragTime':dragTime,'dropTime':dropTime,'dragRow':dragRow,'dropRow':dropRow,'bypass':bypass}
        print f
        return self.macro(f)
    

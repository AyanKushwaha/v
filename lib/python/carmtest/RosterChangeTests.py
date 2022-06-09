#

#
__version__ = "$Revision: 1.10 $"
"""
<module name>
Module for doing:
<xyz>
@date:16Mar2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""

import os
import sys
import traceback
import Cui
import tempfile
import AbsTime
import RelTime

import modelserver
import carmensystems.rave.api as R
import Errlog
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator
from carmtest.GuiTests import GuiTest
import TestUtils as TU
import unittest
# Change here if macro-time changes!


class BasicRosterTest(GuiTest):
    def __init__(self,*args):
        GuiTest.__init__(self, *args)
        self.filter = ()
        self.crew = None
        self.trip = None
        self.marked_legs = {}
        self.pre_count = 0
        self.deassigned = 0
        

    def get_nr_crrs(self):
        Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiScriptBuffer,
                              Cui.CrrMode, Cui.CuiShowAll)
        count = Cui.CuiGetNumberOfChains(Cui.gpc_info, Cui.CuiScriptBuffer)
        return count
    
    def get_nr_legs(self):
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, Cui.CuiScriptBuffer,
                                   Cui.CrewMode, Cui.CrewMode, [self.crew])
        CuiContextLocator(Cui.CuiScriptBuffer,
                          "object",
                          Cui.CrewMode, self.crew).reinstate()
        legs, = R.eval(R.selected('levels.chain'),
                       R.foreach(R.iter('iterators.leg_set'),
                                 'leg_identifier'))
        return len(legs)
    
    def mark_trip(self, roster_bag, area, trip_filter):

        crew_id = roster_bag.crew.id()
        self.log('Trying for crew %s'%crew_id)
        self.log('    trip filter %s'%str(trip_filter))
        for trip_bag in roster_bag.iterators.trip_set(where=trip_filter):
            trip_id = trip_bag.crr_identifier()
            self.log('        found trip %s'%trip_id)
                    
            legs = [str(leg_bag.leg_identifier()) for \
                    leg_bag in trip_bag.iterators.leg_set() if \
                    not leg_bag.studio_select.trip_has_variant()]
            if len(legs) == 0:
                continue
            
            marked_legs = []
            try:
                self.mark_legs_by_ids(legs, area)
                marked_legs = [str(id) for id in Cui.CuiGetLegs(Cui.gpc_info,
                                                                area,
                                                                "marked")]

                if len(marked_legs) != len(legs):
                    raise Exception('Not all legs marked, try with next crew')
            except Exception, err:
                self.log(err)
                return False
            self.crew = crew_id
            self.trip = trip_id
            self.marked_legs = {area:marked_legs}
            self.log('Selected crew_id=%s'%crew_id)
            self.log('Marked legs=%s'%str(marked_legs))
            return True
        return False
        
    def mark_legs_by_ids(self, leg_ids, area=Cui.CuiArea0):
        ids_str = ','.join([str(id) for id in leg_ids])
        if len(ids_str) > 1024:
            raise ValueError('To long markstring, mark fewer legs!')
        mark_leg_bypass = {
            'FORM': 'form_mark_leg_filter',
            'FL_TIME_BASE': 'RDOP',
            'FILTER_MARK': 'LEG',
            'CRC_VARIABLE_0': 'leg_identifier',
            'CRC_VALUE_0': ids_str,
            'CRC_VARIABLE_1': '*',
            'CRC_VALUE_1': '*',
            'CRC_VARIABLE_2': '*',
            'CRC_VALUE_2': '*',
            'OK': ''}
        Cui.CuiMarkLegsWithFilter(mark_leg_bypass,
                                  Cui.gpc_info, area, 0)   


class BuyDaysTest(BasicRosterTest):

    CREW_TO_TRY = 2000
    def __init__(self, *args):
        BasicRosterTest.__init__(self,*args)
        self.values = {'START_TIME':'', 'END_TIME':'', 'BUY_DAYS':''}
        self.tmp_macro_class = BuyDaysMacroTmpclass
        
        self._START_TIME = AbsTime.AbsTime('1oct2009') + RelTime.RelTime('05:00')
        self._END_TIME = AbsTime.AbsTime('30NOV2009') - RelTime.RelTime('05:00') 
        
        self.filter=('trip.%%start_hb%%>=%s'%(self._START_TIME-RelTime.RelTime(5*24*60)),
                     'trip.%%end_hb%%<=%s'%self._END_TIME,
                     'trip.%is_pact%=true',
                     'trip.%is_locked% = false',
                     )
    def setUp(self):
        self.assertTrue(self.is_tracking(),'Testcase only avalilable in tracking')
        BasicRosterTest.setUp(self)

        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiArea0, "window")
        default_bag = R.context('default_context').bag()

        crew_nr = 0
        period = []
        for roster_bag in default_bag.iterators.roster_set():
            # only try 100 time
            period = self.get_buy_period(roster_bag)
            if period:
                self.values['START_TIME'] = str(period[0])
                self.values['END_TIME'] = str(period[1])
                self.values['BUY_DAYS'] = 'True'
                self.log('Found period %s for crew %s to buy.'%(period,roster_bag.crew.id()))
                Cui.CuiDisplayGivenObjects(Cui.gpc_info, Cui.CuiArea0,
                                           Cui.CrewMode, Cui.CrewMode, [str(roster_bag.crew.id())])                
                break
            crew_nr += 1
            if crew_nr > BuyDaysTest.CREW_TO_TRY:
                self.fail('Found no trips to buy, tried %s crew without match, redesign test'%BuyDaysTest.CREW_TO_TRY)
                return

        self.log("Found period %s"%str([str(_) for _ in period]))
        self.pre_count = len(modelserver.TableManager.instance().table('bought_days'))
        self.set_macro(self.get_macro_file(self.values))
        
    def get_buy_period(self, roster_bag):

        if roster_bag.bought_days.bought_days_in_period(self._START_TIME-RelTime.RelTime(5*24*60),self._END_TIME) > 0:
            return []
        freeday_trip_shb = None
        freeday_trip_ehb = None
        vacation_trip_shb = None
        vacation_trip_ehb = None 
        for trip_bag in roster_bag.iterators.trip_set(where=self.filter):
            if not trip_bag.bought_days.code_is_buyable(trip_bag.trip.code()):
                continue
            if trip_bag.task.is_freeday(trip_bag.trip.code()) and freeday_trip_shb is None:
                freeday_trip_shb = trip_bag.trip.start_hb()
                freeday_trip_ehb = trip_bag.trip.end_hb()
            if trip_bag.task.is_vacation(trip_bag.trip.code()) and vacation_trip_shb is None:
                vacation_trip_shb = trip_bag.trip.start_hb()
                vacation_trip_ehb = trip_bag.trip.end_hb()
                
            if (not freeday_trip_shb is None) and (not vacation_trip_shb is None) and \
                   abs(int(freeday_trip_ehb)-int(vacation_trip_shb))<=1:
                return [min(freeday_trip_shb,vacation_trip_shb),
                        max(freeday_trip_ehb,vacation_trip_ehb)]

        return []

    def tearDown(self):
        BasicRosterTest.tearDown(self)
        post_count = len(modelserver.TableManager.instance().table('bought_days'))
        self.log('Bought %s days'%(post_count-self.pre_count))
        if (post_count-self.pre_count) < 1:
            self.fail('Could not buy any days')

class UnBuyDaysTest(BuyDaysTest):

    def setUp(self):
        BuyDaysTest.setUp(self)
        self.run_impl() #run buy macro
        self.log('Days bought')
        self.values['BUY_DAYS'] = 'False'
        print [str(self.values[_]) for _ in self.values]
        self.set_macro(self.get_macro_file(self.values))
        self.pre_count = len(modelserver.TableManager.instance().table('bought_days'))

    def tearDown(self):
        BasicRosterTest.tearDown(self)
        post_count = len(modelserver.TableManager.instance().table('bought_days'))
        self.log('UnBought %s days'%(self.pre_count-post_count))
        if (self.pre_count-post_count) < 1:
            self.fail('Could not unbuy any days')
            
class DeassignSmallTest(BasicRosterTest):

    _LOWER_LIMIT = 3
    _UPPER_LIMIT = 10
    def __init__(self, *args):
        BasicRosterTest.__init__(self, *args)
        # Get crew and deassign trip and marked deassigned trip!
        self.filter = ('trip.%%start_hb%%>=%s'%self._START_TIME,
                       'trip.%%end_hb%%<=%s'%self._END_TIME,
                       'trip.%has_only_flight_duty%=true',
                       'trip.%is_locked% = false',
                       'trip.%%num_legs%% >= %s'%DeassignSmallTest._LOWER_LIMIT,
                       'trip.%%num_legs%% <= %s'%DeassignSmallTest._UPPER_LIMIT)
        
    def setUp(self):
        BasicRosterTest.setUp(self)
        self.show_and_clear()
        self.pre_count = self.get_nr_crrs()
        self.pre_impl()
        
        
        
    def pre_impl(self):
        Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiArea0,
                              Cui.CrewMode, Cui.CuiShowLegal) # Prevent legality issue
        Cui.CuiUnmarkAllLegs(Cui.gpc_info, Cui.CuiArea0, 'WINDOW')
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiArea0, "window")
        default_bag = R.context('default_context').bag()

        crew_nr = 0

        for roster_bag in default_bag.iterators.roster_set():
            # only try 100 time
            if self.mark_trip(roster_bag, Cui.CuiArea0, self.filter):
                return True
            crew_nr += 1
            if crew_nr > 1000:
                self.fail('Found no trip to deassign, tried 1000 crew without match, redesign test')
                return
        return 
    


    def run_impl(self):
        if self.is_tracking():
            import carmensystems.studio.manipulate.DragDrop as DnD_SYS
            DnD_SYS.DeassignMarkedTrip(Cui.CuiArea0, Cui.CuiArea1)
        else:
            Cui.CuiRemoveAssignments(Cui.gpc_info,Cui.CuiArea0,"",0,[]) 
            
    def tearDown(self):
        post_count = self.get_nr_crrs()
        self.deassigned = post_count-self.pre_count
        self.log("Deassigned %s trips!"%self.deassigned)
        if self.deassigned <1:
            self.fail("Deassigned NO  trips! (%s)"%self.deassigned)
        
        # No post action
        return 0


    
class AssignSmallTest(DeassignSmallTest):

    def __init__(self, *args):
        DeassignSmallTest.__init__(self, *args)

        
    def pre_impl(self):
        for _ in range(0,20):
            self.log(self.__class__.__name__+' Trying %d time'%_)
            if Cui.CuiGetAreaMode(Cui.gpc_info, Cui.CuiArea1) != Cui.CrrMode:
                Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiArea1,
                                      Cui.CrrMode, Cui.CuiShowAll)
            #unmark
            Cui.CuiUnmarkAllLegs(Cui.gpc_info, Cui.CuiArea1, 'WINDOW')
            org_crrs = set([str(id) for id in Cui.CuiGetTrips(Cui.gpc_info,
                                                              Cui.CuiArea1,
                                                              "window")])

            try:
                DeassignSmallTest.pre_impl(self)
                DeassignSmallTest.run_impl(self) # Deassign trip
                
                self.pre_count = self.get_nr_legs()
                self.log('Legs before assign=%s'%self.pre_count)
            except Exception, err:
                self.log(err)
                continue
            new_crrs = set([str(id) for id in Cui.CuiGetTrips(Cui.gpc_info,
                                                              Cui.CuiArea1,
                                                              "window") if \
                            str(id) not in org_crrs])

            if len(new_crrs) != 1: 
                continue
            self.new_crr = list(new_crrs)[0]
            self.log('Deassigned trip_id=%s'%self.new_crr)

            # Fetch the data from rave
            CuiContextLocator(Cui.CuiArea1, "object", Cui.CrrMode, self.new_crr).reinstate()
            start_utc,legs = R.eval(R.selected('levels.trip'),
                                    'trip.%start_utc%',
                                    R.foreach(R.iter('iterators.leg_set'),
                                              'leg_identifier'))
            self.trip_start_utc = start_utc
            leg_ids = [str(id) for _,id in legs]
            self.mark_legs_by_ids(leg_ids, Cui.CuiArea1)
            break
        else:
            self.fail('Could not find suitable crew and trip to test on')
       
        
    def run_impl(self):
        if self.is_tracking():
            import carmusr.tracking.DragDrop as DnD
            DnD.AssignMarkedTrips(Cui.CuiArea1, Cui.CuiArea0,
                                  self.new_crr, self.crew, 
                                  int(self.trip_start_utc),
                                  ctrlPressed=0, pos=None)
        else:
            Cui.CuiAssignCrrById(Cui.gpc_info, self.crew, self.new_crr, 0)


    def tearDown(self):
        after_assign = self.get_nr_legs()
        self.log('Legs after assign=%s'%after_assign)
        self.log('Assigned %s legs!'%(after_assign-self.pre_count))
        if (after_assign-self.pre_count) < 1:
            self.fail("Assigned NO  legs!")
        # No post action
        return 0
    


class DeassignLargeTest(BasicRosterTest):
    """
    And by large, we mean all!
    """
    _ROSTERS_TO_CLEAR = 500
    def setUp(self):
        BasicRosterTest.setUp(self)
        self.pre_impl()
        
    def pre_impl(self):
        
        self.pre_count =  self.get_nr_legs(mode='window')
        shown_crew = [str(id) for id in Cui.CuiGetCrew(Cui.gpc_info,Cui.CuiArea0, 'window')][:DeassignLargeTest._ROSTERS_TO_CLEAR]
        Cui.CuiDisplayGivenObjects(Cui.gpc_info, Cui.CuiArea0,
                                   Cui.CrewMode, Cui.CrewMode, shown_crew)
        
        mark_leg_bypass = {
            'FORM': 'form_mark_leg_filter',
            'FL_TIME_BASE': 'RDOP',
            'FILTER_MARK': 'LEG',
            'CRC_VARIABLE_0': 'leg.%start_hb%',
            'CRC_VALUE_0': '>=%s'%(self._START_TIME-RelTime.RelTime(7*24*60)),
            'CRC_VARIABLE_1': 'leg.%start_hb%',
            'CRC_VALUE_1': '<=%s'%self._END_TIME,
            'CRC_VARIABLE_2': 'leg.%is_locked%',
            'CRC_VALUE_2': '*',
            'OK': ''}
        Cui.CuiMarkLegsWithFilter(mark_leg_bypass,
                                  Cui.gpc_info, Cui.CuiArea0, 0)  
            

    def run_impl(self):
        """
        actual test
        """
        Cui.CuiRemoveAssignments(Cui.gpc_info,Cui.CuiArea0,"",0,[])
        
    def tearDown(self):
        post_count = self.get_nr_legs(mode='window')
        self.log('Rostered legs after deassign=%s'%post_count)
        self.log('Deassigned legs=%s'%(self.pre_count-post_count))
        self.deassigned = self.pre_count-post_count
        if self.deassigned <1:
            self.fail("Deassigned NO  trips! (%s)"%self.deassigned)
            
    def get_nr_legs(self, mode='window'):
        self.log('Getting nr of legs')
        Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiArea0,
                              Cui.CrewMode, Cui.CuiShowAll)
        legs = [str(id) for id in Cui.CuiGetLegs(Cui.gpc_info,Cui.CuiArea0, mode)]
        return len(legs)


class RemovePactTest(BasicRosterTest):
    def __init__(self, *args):
        BasicRosterTest.__init__(self, *args)
        self.filter = ('trip.%%start_hb%%>=%s'%self._START_TIME,
                       'trip.%%end_hb%%<=%s'%self._END_TIME,
                       'trip.%is_pact%=true',
                       'trip.%is_locked% = false',
                       'trip.%%code%% = "%s"'%self.get_code())
        self.removed_legs = []
        

    def get_code(self):
        return 'F'
    
    def setUp(self):
        BasicRosterTest.setUp(self)
        self.pre_impl()
        
    def pre_impl(self):
        _ , self.crew = self.find_and_display_1st_match_crew_leg(leg_filter=self.filter)
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiArea0, "window")
        default_bag = R.context('default_context').bag()

        for leg_bag in default_bag.iterators.leg_set(where=self.filter):
            start = leg_bag.trip.start_hb()
            end = leg_bag.trip.end_hb()
            station = leg_bag.leg.start_station()
            leg_id = str(leg_bag.leg_identifier())
            self.removed_legs.append([leg_id, start, end, station])
            
        self.mark_legs_by_ids([leg[0] for leg in  self.removed_legs])
        self.log('Marked legs %s'% self.removed_legs)
        if len(self.removed_legs)<1:
            self.fail('No marked pacts to remove!')
        self.pre_count = self.get_nr_legs()
        

    def run_impl(self):
        Cui.CuiRemoveAssignments(Cui.gpc_info,Cui.CuiArea0,"",0,[])

    def tearDown(self):
        BasicRosterTest.tearDown(self)
        self.post_impl()
        
    def post_impl(self):
        post_count = self.get_nr_legs()
        self.deassigned = self.pre_count-post_count
        if self.deassigned <1:
            self.fail("Removed no  pacts! (%s)"%self.deassigned)
        elif self.deassigned != len(self.removed_legs):
            self.fail("Removed to few pacts no  pacts! (%s)"%self.deassigned) 
        else:
            self.log("Removed %s pacts! ("%self.deassigned)
            
class RemoveVAPactTest(RemovePactTest):
    def get_code(self):
        return 'VA'
     
class CreatePactTest(RemovePactTest):

    def __init__(self, *args):
        RemovePactTest.__init__(self, *args)
        self.created = 0
        
    def setUp(self):
        RemovePactTest.setUp(self)
        Cui.CuiRemoveAssignments(Cui.gpc_info,Cui.CuiArea0,"",0,[])
        self.pre_count = self.get_nr_legs()

    def get_new_code(self):
        return self.get_code()
    
    def run_impl(self):
        for leg in self.removed_legs:
            Cui.CuiCreatePact(Cui.gpc_info,
                              self.crew,
                              self.get_new_code(),
                              "",
                              leg[1],
                              leg[2],
                              leg[3],
                              Cui.CUI_CREATE_PACT_REMOVE_OVERLAPPING_LEGS |
                              Cui.CUI_CREATE_PACT_DONT_CONFIRM |
                              Cui.CUI_CREATE_PACT_SILENT |
                              Cui.CUI_CREATE_PACT_NO_LEGALITY |
                              Cui.CUI_CREATE_PACT_TASKTAB)
    def tearDown(self):
        
        BasicRosterTest.tearDown(self)
        post_count = self.get_nr_legs()
        self.created = post_count-self.pre_count
        self.log('Created %s pacts!'%self.created)
        if self.created < 1:
            self.fail("Created no pacts!")


class CreateRPactTest(CreatePactTest):

    def __init__(self, *args):
        CreatePactTest.__init__(self,*args)
        self.start_time = RelTime.RelTime('06:00')
        self.length = RelTime.RelTime('08:00')
        
    def get_new_code(self):
        return 'R'
        
    def setUp(self):
        CreatePactTest.setUp(self)
        for leg in self.removed_legs:
            leg[1] = leg[1] + self.start_time
            leg[2] = leg[1] + self.length

class CreateVAPactTest(CreatePactTest):
    def get_new_code(self):
        return 'VA'



########################## GUI TEST #####################################

class BuyDaysMacroTmpclass(TU.TmpMacro):
    XML = """<?xml version="1.0" encoding="UTF-8"?>
<All>

<Command label="Buy Day" script="PythonEvalExpr(&quot;carmusr.tracking.BuyDays.markDaysAsBought(&apos;BUY_DAYS&apos;)&quot;)" level="0">
<AreaId id=""/>
<FormData name="Buy_Day_Form">
<FormInput  name="COMMENT" value="buy days test" height="1" length="20" style="1" type="String" width="20" />
<FormInput  name="OK" value="" type="Done" />
</FormData>
<InteractionData type="SelectionAction" id="">
<InteractionItem key="Cancelled" value="0" />
<InteractionItem key="areaId" value="0" />
<InteractionItem key="button" value="1" />
<InteractionItem key="lineNo" value="0" />
<InteractionItem key="row" value="0" />
<InteractionItem key="subWinId" value="2" />
<InteractionItem key="tabIx" value="0" />
<InteractionItem key="tim" value="START_TIME" />
</InteractionData>
<InteractionData type="SelectionAction" id="">
<InteractionItem key="Cancelled" value="0" />
<InteractionItem key="areaId" value="0" />
<InteractionItem key="button" value="1" />
<InteractionItem key="lineNo" value="0" />
<InteractionItem key="row" value="0" />
<InteractionItem key="subWinId" value="2" />
<InteractionItem key="tabIx" value="0" />
<InteractionItem key="tim" value="END_TIME" />
</InteractionData>
<CommandAttributes label="Buy Day"
                   script="PythonEvalExpr(&quot;carmusr.tracking.BuyDays.markDaysAsBought(&apos;BUY_DAYS&apos;)&quot;)"
                   level="0" returnVal="0" />
</Command>
</All>
"""   


##########################################################################

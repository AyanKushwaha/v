#

#
__version__ = "$Revision: 1.2 $"
"""
<module name>
Module for doing:
<xyz>
@date:11Dec2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""

import unittest

import Cui
import modelserver
import RelTime
import carmensystems.rave.api as R

import carmtest.TestBaseClass as TBC
import carmtest.RosterChangeTests as RCT
import carmtest.GuiTests as GT
import carmtest.TestUtils as TU

class modelchange(object):

        def __init__(self, crew, table, change):
            self.crew = crew
            self.change = change
            self.table = table
            self.pre_count = self.get_rows()

        def get_rows(self):
            count = 0
	    if self.crew:
		    count = len(modelserver.TableManager.instance().table('crew')[(self.crew,)].referers(self.table,
													 'crew'))
	    else:
		    count = len(modelserver.TableManager.instance().table(self.table))
			    
            return count

        def test(self):
            return self.change == (self.get_rows()-self.pre_count)
        
class AccountHandlerTest(TBC.PerformanceTest):

    """
    Test that account handler updates works.
    First it runs 1 udpate to make sure everything is up to date
    Then it deassigns some VA and creates some VA for another crew
    Then run update
    Finally see if changes to modelrows match expected results
    """


    def __init__(self, *args):
	    TBC.PerformanceTest.__init__(self, *args)
	    
	    self.add_crew = None
	    self.remove_crew = None
        

    def setUp(self):
        TBC.PerformanceTest.setUp(self)
        import carmusr.modcrew
        import carmusr.AccountHandler
        carmusr.AccountHandler.updateChangedCrew([crew.id for crew in modelserver.TableManager.instance().table('crew')])
        
        result = unittest.TestResult()
        remove_va = RCT.RemoveVAPactTest('testRun')
        remove_va.run(result)

        add_va = RCT.CreateVAPactTest('testRun')
        filter = list(add_va.filter)
        filter.append('crew.%%id%% <> "%s"'%remove_va.crew)
        add_va.filter = tuple(filter)
        add_va.run(result)
        
        if not result.wasSuccessful():
            self.fail('Could not remove and/or add VA')

     

        self.log('Removed %s VA for crew %s'%(remove_va.deassigned, remove_va.crew))
        self.log('Created %s VA for crew %s'%(add_va.created, add_va.crew))

        self.add_crew = modelchange(add_va.crew, 'account_entry', add_va.created)
        self.remove_crew = modelchange(remove_va.crew, 'account_entry', -remove_va.deassigned)
        carmusr.modcrew.add(remove_va.crew)
        carmusr.modcrew.add(add_va.crew)

    def testRun(self):
        import carmusr.AccountHandler
        self.performance_test(carmusr.AccountHandler.updateChangedCrew)

    def tearDown(self):
        TBC.PerformanceTest.tearDown(self)
        if not self.add_crew.test():
            self.fail('Error updating added vacations')
        if not self.remove_crew.test():
            self.fail('Error updating removed vacations')
        

class CreateTrainingAttributeTest(GT.GuiTest):
	"""
	Test to set training attribute to a certain trip
	GuiTest is a baseclass which holdssome neat functions to find things in plan.
	GuiTests inherits from MacroTest, so by setting the tmp_macro class we choose which macro to run

	The test-method is called
	testRun which will performace test the run_impl-method 
	"""
	def __init__(self, *args):
		GT.GuiTest.__init__(self, *args)
		# Look for a leg inside desired period which doesn't have any attribute but can have
		self.filter=('leg.%%start_hb%%>=%s'%self._START_TIME,
			     'leg.%%end_hb%%<=%s'%self._END_TIME,
			     'not trip.%has_training_code%',
			     'not trip.%is_locked%',
			     'leg.%can_have_attribute%',
			     'leg.%is_flight_duty%',
			     'crew_pos.%assigned_function% = "AH" or crew_pos.%assigned_function% = "FP"'
			     )
		# These options will be replaced in macro template
		self.values = {'RANGE_OPTION':'Entire trip',
			       'ATTRIBUTE_VALUE':'RELEASE',
			       'LEG_TIME':None
			       }
		# Which class to use for macro template
		self.tmp_macro_class = SetTrainingAttributeTmpMacro

		
	def setUp(self):
		# Set up is run before test, it checks for loaded plan and clears windows 
		GT.GuiTest.setUp(self)
		# use filter to find a matching leg
		(leg_id, crew) = self.find_and_display_1st_match_crew_leg(self.filter)
		
		# look up start time and nr_legs which will get attibute
		Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiArea0, "window")
		default_bag = R.context('default_context').bag()
		for leg_bag in default_bag.iterators.leg_set(where='leg_identifier=%s'%leg_id):
			leg_start_utc = leg_bag.leg.start_utc()
			nr_legs = leg_bag.trip.num_active_legs()
			#trip_id = leg_bag.crr_identifier()
			self.log('Found LEG starting %s with %s legs in trip'%(leg_start_utc,nr_legs))
			break
		else:
			self.fail("Cound not find leg start utc")

		# Store number of model rows before testRun, nr_legs is expected change
		self.modelchange_test = modelchange(None, 'crew_flight_duty_attr', nr_legs)
		# Set the x-coordinate in macro template to leg_start_utc + 5 min 
		self.values['LEG_TIME'] = str(leg_start_utc + RelTime.RelTime('00:05'))
		# Create and set macro xml file
		self.set_macro(self.get_macro_file(self.values))

	# Method run by test and performance of it is logged in test result! 
	def run_impl(self):
		GT.GuiTest.run_impl(self)
		# Check that we actually got the number of rows expected
		self.failUnless(self.modelchange_test.test(),'Unexpected number of attributes in model!')
		
	def tearDown(self):
		# Run baseclass tear down (added for show)
		GT.GuiTest.tearDown(self)
		




########## Tmp Macro Test ############
class SetTrainingAttributeTmpMacro(TU.TmpMacro):
	"""
	Macro for setting using set training attribute form
	Baseclass will replace variables in template with values and
	write it to a tmp file and then remove tmp-file on delete of object
	"""
	XML="""<?xml version="1.0" encoding="UTF-8"?>
<All>
<Command label="Select" script="GuiProcessInteraction(&quot;SelectInteractor&quot;, &quot;&quot;)" level="0">
<AreaId id=""/>
<Object position="" identity=""/>
<InteractionData type="SelectInteractor" id="">
<InteractionItem key="Area" value="0" />
<InteractionItem key="Elevation" value="51" />
<InteractionItem key="Operation" value="0" />
<InteractionItem key="Row" value="0" />
<InteractionItem key="Subwindow" value="2" />
<InteractionItem key="Time" value="LEG_TIME" />
</InteractionData>
<CommandAttributes label="Select" script="GuiProcessInteraction(&quot;SelectInteractor&quot;, &quot;&quot;)"
                   level="0" returnVal="0" />
</Command>
<Command label="Set Training Attribute"
         script="PythonEvalExpr(&quot;carmusr.training_attribute_handler.set_training_attribute()&quot;)"
	 level="0">
<AreaId id=""/>
<FormData name="ATTRIBUTES_FORM">
<FormInput  name="ATTRIBUTE_FIELD" value="ATTRIBUTE_VALUE" height="3" length="11"
            menu=";AP TRAINING;NEW;X SUPERNUM;RELEASE;AS TRAINING;SUPERNUM;NONE"
	    menuOnly="True" style="1" toUpper="True" type="String" width="10" />
<FormInput  name="RANGE_FIELD" value="RANGE_OPTION" height="3" length="16"
            menu=";Clicked leg only;Entire trip;All marked" menuOnly="True" style="1" type="String" width="10" />
<FormInput  name="OK" value="" type="Done" />
</FormData>

<Object position="" identity=""/>
<InteractionData type="CommandState" id="">
<InteractionItem key="areaId" value="0" />
<InteractionItem key="button" value="0" />
<InteractionItem key="lineNo" value="0" />
<InteractionItem key="row" value="0" />
<InteractionItem key="subWinId" value="2" />
<InteractionItem key="tabIx" value="0" />
<InteractionItem key="tim" value="LEG_TIME" />
</InteractionData>

<CommandAttributes label="Set Training Attribute"
                   script="PythonEvalExpr(&quot;carmusr.training_attribute_handler.set_training_attribute()&quot;)"
		   level="0" returnVal="0" />
</Command>
</All>
"""
######################################

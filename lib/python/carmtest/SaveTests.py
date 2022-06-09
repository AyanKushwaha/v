import os
import tempfile
import sys
import Errlog
import time

import carmensystems.dave.tools.MaxCommitId as MaxCommitId
import carmensystems.dave.tools.prune_schema as PruneSchema
import RelTime
import AbsTime
import Cui
import carmtest.RosterChangeTests as RCT
from carmtest.GuiTests import GuiTest
import carmensystems.studio.MacroRecorder.PlayMacro as PM
import tm
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator
import carmensystems.rave.api as R
import Variable
import unittest
import TestUtils as TU

class NotPrunedException(Exception):
	pass

class DataModTest(GuiTest):
	def __init__(self, *args):
		GuiTest.__init__(self, *args)

	def setUp(self):
		GuiTest.setUp(self)
		if not bool(os.environ.get('CARMTMP',False)) or \
		   not bool(os.environ.get('CARMSYS',False)) or \
		   not bool(os.environ.get('DATABASE',False)) or \
		   not bool(os.environ.get('DB_SCHEMA',False)) or \
		   not bool(os.environ.get('CARMUSR',False)):
			self.fail('One or more environ variable not set!')
		self._tmpFilename = 'TestRevid.log'
		self._tmpFilePath = os.path.join(os.environ['CARMTMP'],
						 'logfiles',
						 self._tmpFilename)
		self._carmsysPath = os.environ['CARMSYS']
		connstr = Variable.Variable("")
		schema = Variable.Variable("")
		Cui.CuiGetSubPlanDBPath(Cui.gpc_info, connstr, schema)
		self._dbconn = connstr.value
		self._dbschema = schema.value
		self.set_macro(self.get_macro_file())
		if not os.path.exists(self.macro):
			self.fail('Could not find test macro!!')

		try:
			self.writeRevidToTmpFile()
		except NotPrunedException, err:
			self.log(err)
			self.log("Will prune schema and remove file")
			self.pruneToRevidFromTmpFile()
			self.fail("Error in pre due to not pruned db , aborting test")
		self.loadEtabs()


		
	def run_impl(self):
		try:
			PM.PlayMacroFile(self.macro)
		except Exception ,err:
			self.log(err)
			self.pruneToRevidFromTmpFile()
			self.fail("Error in run, aborting test")
		

	def tearDown(self):
		GuiTest.tearDown(self)
		self.pruneToRevidFromTmpFile()
		
	def writeRevidToTmpFile(self):
		if os.path.isfile(self._tmpFilePath):
			raise NotPrunedException(self._tmpFilePath +' exists. This means that a test that includes a save has been cancelled. Please prune the database to the revid from the file. You can delete the file but the save tests will not work anymore.')
		
		maxCommitId = MaxCommitId.MaxCommitId()
		maxCommitId.conn = self._dbconn
		maxCommitId.schema = self._dbschema
		maxCommitId.quiet = True

		saveout = sys.stdout
		fsock = open(self._tmpFilePath, 'w')
		sys.stdout = fsock
		maxCommitId.run()
		sys.stdout = saveout
		fsock.close()
		self.log('writeRevidToTmpFile: wrote revid to file!')
		if not os.path.isfile(self._tmpFilePath):
			self.fail('Could not create tmp file with revid: ' +  self._tmpFilePath)
			
	def loadEtabs(self):
		Cui.CuiCrcEval(Cui.gpc_info, Cui.CuiNoArea,
			       "PLAN", "compdays.%transaction_crew%(\"0\")")
		Cui.CuiCrcEval(Cui.gpc_info, Cui.CuiNoArea, "PLAN",
			       "compdays.%_online_transaction_entry_check%(\"0\",\"0\",0,01Jan1986)")
		



	def readRevidFromTmpFile(self):
		if not os.path.isfile(self._tmpFilePath):
			self.fail('tmp file with revid does not exist: ' + self._tmpFilePath)

		fsock = open(self._tmpFilePath, 'r')
		revid = fsock.readline().rstrip("\n")
		fsock.close()
		return revid
	
	def removeRevidTmpFile(self):
		os.remove(self._tmpFilePath)

	def pruneToRevidFromTmpFile(self):
		revid = self.readRevidFromTmpFile()
		pruneCommand = self._carmsysPath +\
			       '/bin/dave_prune_schema -c ' +\
			       self._dbconn + ' -s ' +\
			       self._dbschema + ' -C ' + revid +\
			       ' -R published_roster:pubcid'
		self.log(pruneCommand)
		os.system(pruneCommand)
		self.removeRevidTmpFile()


#Test not working			
#class SaveSmallTest(DataModTest):
#
#	def __init__(self, *args):
#		DataModTest.__init__(self, *args)
#		self.tmp_macro_class = SaveTmpMacro
#		
#	def setUp(self):
#		DataModTest.setUp(self)
#		deassigner = RCT.DeassignSmallTest('testRun')
#		deassigner._START_TIME = self._START_TIME
#		deassigner._END_TIME = self._END_TIME
#		pre_count = deassigner.get_nr_crrs()
#		deassigner.pre_impl()
#		deassigner.run_impl()
#		post_count = deassigner.get_nr_crrs()
#		self.log("Deassigned %s trips!"%(post_count-pre_count))
#		if abs(post_count-pre_count) < 1:
#			self.removeRevidTmpFile()
#			self.fail('Deassigned no trip')
		

class SaveSmall5TimesTest(DataModTest):

	def __init__(self, *args):
		DataModTest.__init__(self, *args)
		self.tmp_macro_class = SaveTmpMacro
		self.runs = 5
		
	def testRun(self):
		tmp_macro = self.tmp_macro_class()
		for i in range(0,self.runs):
			deassigner =  RCT.DeassignSmallTest('testRun')
			deassigner._START_TIME = self._START_TIME
			deassigner._END_TIME = self._END_TIME
			pre_count = deassigner.get_nr_crrs()
			deassigner.pre_impl()
			deassigner.run_impl()
			post_count = deassigner.get_nr_crrs()
			self.log("Deassigned %s trips!"%(post_count-pre_count))
			self.performance_test(PM.PlayMacroFile, [tmp_macro.generate_tmp()])

			


			
class SaveLargeTest(DataModTest):

	def __init__(self, *args):
		DataModTest.__init__(self, *args)
		self.tmp_macro_class = SaveTmpMacro
		
	def setUp(self):
		DataModTest.setUp(self)
		deassigner = RCT.DeassignLargeTest('testRun')
		deassigner._START_TIME = self._START_TIME
		deassigner._END_TIME = self._END_TIME
		pre_count = deassigner.get_nr_legs()
		deassigner.pre_impl() # Deassigns hundereds of rosters trip
		deassigner.run_impl()
		post_count = deassigner.get_nr_legs()
		self.log("Deassigned %s legs!"%abs(post_count-pre_count))
		if abs(post_count-pre_count) < 1:
			self.removeRevidTmpFile()
			self.fail('Deassigned no legs')
	

class RefreshSmallTest(DataModTest):
	def __init__(self, *args):
		DataModTest.__init__(self, *args)
		self.tmp_macro_class = RefreshTmpMacro
		self._new_crews = []
		self.pre_count = 0
		
	def setUp(self):
		"""
		First add a new crew, refresh him in and show data, then referesh some flights for him!
		"""
		DataModTest.setUp(self)
		self._crewDataPath = os.path.join(os.environ.get('CARMUSR',''),
						  'Testing',
						  'perftests',
						  'crew_test_data.digxml')
		self._assignmentDataPath = os.path.join(os.environ.get('CARMUSR',''),
							'Testing',
							'perftests',
							'assig_test_data_template.digxml')
		if  not os.path.isfile(self._crewDataPath):
			self.fail('Unable to locate crew data for refresh')

		if  not os.path.isfile(self._assignmentDataPath):
			self.fail('Unable to locate assignment data for refresh')

		self._pre_set = self.__get_crew_ids()
		crewCommand = self._carmsysPath + \
			      '/bin/carmrunner loadDigXml  -c ' +\
			      self._dbconn + ' -s ' + self._dbschema + ' ' + self._crewDataPath
		os.system(crewCommand)
		PM.PlayMacroFile(self.macro)
		for crew in tm.TM.crew:
			if crew.id not in self._pre_set:
				self.log("Refreshed %s crew to model"%str(crew))
				self._new_crews.append(crew)
		if len(self._new_crews) == 0:
			self.fail('Refresh no new crew to model!')
		Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiArea0,
				      Cui.CrewMode, Cui.CuiShowAll)
		Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiArea1,
				      Cui.CrrMode, Cui.CuiShowAll)
		self.pre_count = self.__count_crew_legs()
		date1 = self._START_TIME+RelTime.RelTime(10*24)
		date1 = date1.split()
		date2 = self._START_TIME+RelTime.RelTime(11*24)
		date2 = date2.split()
		date3 = self._START_TIME+RelTime.RelTime(12*24)
		date3 = date3.split()
		date4 = self._START_TIME+RelTime.RelTime(13*24)
		date4 = date4.split()
		in_t =  None
		out = 0
		(out, file )= tempfile.mkstemp()
		try:
			in_t = open(self._assignmentDataPath,'r')
			for line in in_t:
				line = line.replace('DATE1',"%s-%.2d-%.2d"%(date1[0],date1[1],date1[2]))
				line = line.replace('DATE2',"%s-%.2d-%.2d"%(date2[0],date2[1],date2[2]))
				line = line.replace('DATE3',"%s-%.2d-%.2d"%(date3[0],date3[1],date3[2]))
				line = line.replace('DATE4',"%s-%.2d-%.2d"%(date4[0],date4[1],date4[2]))
				os.write(out,line)
		finally:
			if in_t:
				in_t.close()
			os.close(out)
		

				
				
		# ok, we got the crew member, not lets add some assignments to database
		assignCommand = self._carmsysPath +\
				'/bin/carmrunner loadDigXml  -c ' +\
				self._dbconn + ' -s ' +\
				self._dbschema + ' ' +\
				file
		self.log(assignCommand)
		os.system(assignCommand)
		
     	def tearDown(self):
		DataModTest.tearDown(self)
		post_count =  self.__count_crew_legs()
		if (post_count - self.pre_count) < 1:
			self.fail('Refreshed no activties (%s)!'%(post_count - self.pre_count))

		
	def __get_crew_ids(self):
		return set([crew.id for crew in tm.TM.crew])

	def __count_crew_legs(self):
		nr_legs = 0
		for crew in self._new_crews:
			CuiContextLocator(Cui.CuiArea0, "object", Cui.CrewMode, crew.id).reinstate()
			legs,= R.eval(R.selected('levels.chain'),
				      R.foreach(R.iter('iterators.leg_set'),
						'leg_identifier'))
			leg_ids = [str(id) for _,id in legs]
			self.log('Crew %s has legs %s'%(crew.id, ':'.join(leg_ids)))
			nr_legs += len(leg_ids)
		return nr_legs
			
			
class RefreshEmptyTest(DataModTest):
	
	def __init__(self, *args):
		DataModTest.__init__(self, *args)
		self.tmp_macro_class = RefreshTmpMacro
		
	def setUp(self):
		GuiTest.setUp(self)
		
	def tearDown(self):
		GuiTest.tearDown(self)

############ GUI MACROS DEFINED HERE ##########################
class SaveTmpMacro(TU.TmpMacro):
    XML = """<?xml version="1.0" encoding="UTF-8"?>
<All>
<Command label="Save" script="PythonEvalExpr(&quot;carmensystems.studio.Tracking.OpenPlan.savePlan()&quot;)" level="0">
<FormData name="CONFIRM_BOX">
<FormInput  name="YES" value="" type="Done" />
</FormData>
<CommandAttributes label="Save"
                   script="PythonEvalExpr(&quot;carmensystems.studio.Tracking.OpenPlan.savePlan()&quot;)" level="0" returnVal="0" />
</Command>
</All>
"""


class RefreshTmpMacro(TU.TmpMacro):
    XML = """<?xml version="1.0" encoding="UTF-8"?>
<All>
<Command label="Refresh" script="PythonEvalExpr(&quot;carmensystems.studio.Tracking.OpenPlan.refreshGui()&quot;)" level="0">
<CommandAttributes label="Refresh" script="PythonEvalExpr(&quot;carmensystems.studio.Tracking.OpenPlan.refreshGui()&quot;)" level="0" returnVal="0" />
</Command>
</All>
"""
#############################################################

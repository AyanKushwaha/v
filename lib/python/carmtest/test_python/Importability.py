'''
Tests that verifies that all python modules in CARMUSR/lib/python can be imported
'''

from carmtest.framework import *

import os, os.path, sys

class python_001_Importability(TestFixture):
    """
    Test that python modules can be imported
    """

    #BLOCKED_DIRS = ['adhoc', 'contrib', 'carmtest', 'tests', 'cmsadm']

    PYTHON_MODULES = []
    PYTHON_DIRS = ['carmstd',
                   'carmusr']

    STUDIO_DIRS = ['carmstd.studio',
                   'carmstd.report',
                   'carmstd.rave',
                   'carmstd.planning',
                   'carmstd.cfhExtensions',
                   'carmstd.area',
                   'carmstd.parameters',
                   'carmstd.matador',
                   'carmdata',
                   'carmusr.preplanning',
                   'carmusr.rostering',
                   'carmusr.pairing',
                   'carmusr.planning',
                   'carmusr.tracking',
                   'carmusr.AuditTrail',
                   'carmusr.paxlst',
                   'carmusr.fatigue',
                   'carmusr.application',
                   'carmusr.ground_duty_handler',
                   'carmusr.menues',
                   'carmusr.modcrew',
                   'carmusr.upd_dbl_qual',
                   'carmusr.trip_area_handler',
                   'carmusr.training_attribute_handler',
                   'carmusr.sim_exception_handler',
                   'carmusr.resolve_overlaps',
                   'carmusr.activity_set',
                   'carmusr.TOR_create',
                   'carmusr.TOR_activate',
                   'carmusr.StartStudio',
                   'carmusr.StartFilteredTableEditor',
                   'carmusr.SoftLocksStartGUI',
                   'carmusr.SelectCrewForm',
                   'carmusr.SelectCrew',
                   'carmusr.SKLegAuditTrail',
                   'carmusr.rule_exceptions',
                   'carmusr.MiniSelect',
                   'carmusr.LegAuditTrail',
                   'carmusr.HelperFunctions',
                   'carmusr.FlightAttributes',
                   'carmusr.FileHandlingExt',
                   'carmusr.CrewTableHandler',
                   'carmusr.CrewRest',
                   'carmusr.ConfirmSave',
                   'carmusr.BuildAcRotations',
                   'carmusr.AttributesForm',
                   'carmusr.AccumulateBaseline']
    
    MIRADOR_DIRS = ['carmusr.manpower',
                    'carmusr.crewinfo',
                    'carmusr.TableEditorFilter',
                    'carmusr.check_recurrent_docs',
                    'carmusr.OptRemover',
                    'carmusr.NightlyCleanups',
                    'carmusr.TripAuditTrail',
                    'carmusr.DaveFilterTool',
                    'carmusr.CrewTraining',
                    'carmusr.CrewBlockHours',
                    'carmusr.CrewAuditTrail']
    
    def __init__(self):
        self._pythonpath = os.path.join(os.getenv('CARMUSR'), 'lib', 'python')
    
    def test_001_PythonDirAvailability(self):
        assert os.path.isdir(self._pythonpath), "Can not find Python source dir (%s)" % self._pythonpath

    @REQUIRE("NotMigrated")
    def test_002_ImportAllModules(self):
        errors = 0
        imported = 0
        for root, dir, files in os.walk(self._pythonpath):
            for file in files:
                if file.endswith(".py"):
                    mod = '.'.join(os.path.join(root, file).replace(self._pythonpath+"/",'').split('/'))[:-3]
                    try:
                        if self._validPythonModule(mod):
                            if (not self._validStudioModule(mod)) and (not self._validMiradorModule(mod)):
                                print " *** About to import:", mod
                                __import__(mod)
                                imported += 1
                    except:
                        print " Exception:", mod
                        print sys.exc_info()[1]
                        self.log("Failed to import %s: %s" % (mod, sys.exc_info()[1]), severity="Error")
                        errors += 1
        print "Imported: ", imported
        self.log("Imported %d modules" % imported)
        assert errors == 0, "Failed to load at least %d modules, see above" % errors

    @REQUIRE("Mirador")
    def test_003_ImportAllMiradorModules(self):
        errors = 0
        for root, dir, files in os.walk(self._pythonpath):
            for file in files:
                if file.endswith(".py"):
                    mod = '.'.join(os.path.join(root, file).replace(self._pythonpath+"/",'').split('/'))[:-3]
                    try:
                        if self._validMiradorModule(mod):
                            print " *** About to import:", mod
                            __import__(mod)
                    except:
                        print "Exception:", mod
                        print sys.exc_info()[1]
                        self.log("Failed to import %s: %s" % (mod, sys.exc_info()[1]), severity="Error")
                        errors += 1
        assert errors == 0, "Failed to load at least %d modules, see above" % errors


    @REQUIRE("Studio")
    @REQUIRE("NotMigrated")
    def test_004_ImportAllStudioModules(self):
        errors = 0
        for root, dir, files in os.walk(self._pythonpath):
            for file in files:
                if file.endswith(".py"):
                    mod = '.'.join(os.path.join(root, file).replace(self._pythonpath+"/",'').split('/'))[:-3]
                    try:
                        if self._validStudioModule(mod):
                            #print "About to import:", mod
                            __import__(mod)
                    except:
                        print "Exception:", mod
                        #print sys.exc_info()[1]
                        self.log("Failed to import %s: %s" % (mod, sys.exc_info()[1]), severity="Error")
                        errors += 1
        assert errors == 0, "Failed to load at least %d modules, see above" % errors

    def _validPythonModule(self, mod):
        for dir in self.PYTHON_DIRS:
            if mod.startswith(dir):
                return True
        return False

    def _validStudioModule(self, mod):
        for dir in self.STUDIO_DIRS:
            if mod.startswith(dir):
                return True
        return False

    def _validMiradorModule(self, mod):
        for dir in self.MIRADOR_DIRS:
            if mod.startswith(dir):
                return True
        return False

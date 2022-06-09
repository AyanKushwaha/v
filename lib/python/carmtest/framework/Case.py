'''
Created on Feb 11, 2010

@author: rickard
'''

import unittest
import os,sys
import subprocess
try:
    from AbsTime import AbsTime
    from RelTime import RelTime
    from AbsDate import AbsDate
except:
    def AbsDate(*args, **kwargs):
        raise "AbsDate is not supported"
    def AbsTime(*args, **kwargs):
        raise "AbsTime is not supported"
    def RelTime(*args, **kwargs):
        raise "RelTime is not supported"

class TestFixture(unittest.TestCase):
    """
    The base class for all test suites. Derived from the unittest package.
    
    This base class contains a number of utility methods to simplify the
    definition of tests.
    """
    def __init__(self):
        self._performance = os.environ.get("TEST_PERFORMANCE", "") != ""
        self._rave = None
        
    def log(self, msg, severity="Info"):
        """
        Stores a string message in the test log.
        """
        import carmtest.framework.TestFunctions as F
        if severity.lower() == "warning":
            severity = "Warning"
        elif severity.lower() == "debug":
            severity = "Debug"
        else:
            severity = "Info"
        F.logfile().log(msg, severity)
        print >>sys.stderr, "TEST %-10s: %s" % (severity, msg)
                
    def dataError(self, msg):
        """
        Raises a data error, used when the test case can not be run due
        to missing data.
        """
        raise ValueError("DATA: %s" % msg)
    
    def fail(self, msg):
        """
        Fails the test. Alternatively, the 'assert' keyword can be used.
        """
        raise ValueError(msg)
                        
    def rave(self):
        """
        Returns the Rave API, or fails the test if it can not be used from here.
        """
        if not self._rave:
            try:
                import carmensystems.rave.api as R
                self._rave = R
            except:
                self.fail("Can not use Rave API from this context")
        return self._rave
        
    def raveParam(self, parameter):
        """
        Returns the value of a named Rave parameter.
        """
        return self.rave().param(parameter).value()
        
    def setRaveParam(self, parameter, value):
        """
        Sets a Rave parameter to a specific value
        """
        self.rave().param(parameter).setvalue(value)
        
    def getNowTime(self):
        """
        Returns the Now time as an AbsTime
        """
        return self.rave().eval("fundamental.%now%")[0]
        
    def setNowTime(self, value):
        """
        Changes Now time
        """
        self.setRaveParam("fundamental.%use_now_debug%", True)
        self.setRaveParam("fundamental.%now_debug%", AbsTime(value))
        
    def getLoadedRegion(self):
        """
        Returns the planning area that is currently loaded,
        or ALL if all areas are loaded.
        """
        return self.rave().eval("planning_area.%filter_company_p%")[0]
        
    def raveExpr(self, expression, crew=None):
        """
        Evaluates a constant Rave expression, or a Rave expression
        on a particular crew, and returns the result.
        Note: An exception will occur if the expression can not be
        evaluated on the const/roster level.
        """
        import Cui
        if crew:
            Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiNoArea, "internal_object")
            if self.isReportWorker() and self.getReportServerPublishType():
                Cui.gpc_set_one_published_crew_chain(Cui.gpc_info, crew)
            else:
                Cui.gpc_set_one_crew_chain(Cui.gpc_info, crew)
            return self.rave().eval("default_context", expression)[0]
        else:
            return self.rave().eval(expression)[0]
        
    def getMarkedLegs(self, eval=None):
        """
        Returns a list of marked legs. The default is to return a bag iterator, but if 
        eval is set, it returns a list of tuples with the evaluation results.
        Note: If eval is "leg_identifier", there is an internal optimization.
        """
        import Cui
        legs = []
        area = 0
        for a in range(4):
            ids = [str(id) for id in Cui.CuiGetLegs(Cui.gpc_info, a, "marked")]
            if len(ids) > len(legs):
                area = a
                legs = ids
        if type(eval) is str:
            eval = (eval, )
        if isinstance(eval, tuple) and len(eval) == 1: eval = eval[0]
        if len(legs) == 0 or eval == "leg_identifier": return [(1,x) for x in legs]
        return self.getLegs("leg_identifier=" + " or leg_identifier=".join(legs),area=area,eval=eval)
        #for id in legs:
        #    Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, id)
        #    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "object")
        #    legbags.append(self.rave().selected(self.rave().Level.atom()).bag())
        #return legbags
        
    def select(self, area=-1, crew=None, trip=None):
        """
        Sets the contents of the window to the specified crew or trip
        """
        import Cui
        if area < 0: 
            area = Cui.CuiScriptBuffer
        
        if crew and trip:
            raise ValueError("Both crew and trip can not be specified")
        
        if crew:         
            if isinstance(crew, str): 
                crew = [crew]
            elif isinstance(crew, tuple): 
                crew = list(crew)
            elif isinstance(crew, int): 
                crew = [str(crew)]

            Cui.CuiDisplayGivenObjects(Cui.gpc_info, area, Cui.CrewMode, Cui.CrewMode, crew)
        else:
            raise ValueError("not implemented")
        
    def markLegs(self, spec, area=-1):
        """
        Marks the specified legs. The specification can be a list of ids,
        a Rave filter expression (or a tuple of such), or a bag iterator
        of legs. 
        """
        import Cui
        if area < 0: area = Cui.CuiScriptBuffer
        if isinstance(spec, str):
            if spec == "":
                spec = None
            elif spec.isdigit() or spec[:1] == '-' and spec[1:].isdigit():
                spec = int(spec)
            
        if isinstance(spec, str) or isinstance(spec, tuple):
            spec = [x[1] for x in self.getLegs(spec, eval="leg_identifier")]
            
        if isinstance(spec, int):
            spec = [spec]
        if hasattr(spec, '__class__') and spec.__class__.__name__ == '_BoundIter':
            spec = [x.leg_identifier() for x in spec]
        elif hasattr(spec, '__class__') and spec.__class__.__name__ == '_Bag':
            spec = spec.leg_identifier()
        self._markLegsByIds(Cui, spec, area)
            
    def _markLegsByIds(self, Cui, leg_ids, area):
        ids_str = ','.join([str(id) for id in leg_ids])
        if len(ids_str) > 1024:
            raise ValueError('To long markstring, mark fewer legs!')
        mark_leg_bypass = {
            'FORM': 'form_mark_leg_filter',
            'FL_TIME_BASE': 'RDOP',
            'FILTER_MARK': 'LEG',
            'FILTER_METHOD': 'REPLACE',
            'CRC_VARIABLE_0': 'leg_identifier',
            'CRC_VALUE_0': ids_str,
            'CRC_VARIABLE_1': '*',
            'CRC_VALUE_1': '*',
            'CRC_VARIABLE_2': '*',
            'CRC_VALUE_2': '*',
            'OK': ''}
        Cui.CuiMarkWithFilter(mark_leg_bypass, Cui.gpc_info, area, 0, 'form_mark_leg_filter')   
        
    def getLegs(self, conditions, sort=None, area=-1, eval=None):
        """
        Evaluates Rave on the leg level, or returns a bag (if eval is not set).
        """
        import Cui
        if isinstance(conditions, str): conditions = (conditions,)
        if area < 0: area = Cui.CuiScriptBuffer
        if type(eval) is str:
            eval = (eval, )
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "window")
        bag = self.rave().context("default_context").bag()
        if not eval:
            return bag.iterators.leg_set(where=conditions, sort_by=sort)
        else:
            return self.rave().eval(bag, self.rave().foreach(self.rave().iter("iterators.leg_set", where=conditions, sort_by=sort), *eval))
    
    def getRosters(self, conditions, sort=None, area=-1, eval=None):
        """
        Evaluates Rave on the roster level, or returns a bag (if eval is not set).
        """
        import Cui
        if isinstance(conditions, str): conditions = (conditions,)
        if area < 0: area = Cui.CuiScriptBuffer
        if type(eval) is str:
            eval = (eval, )
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "window")
        bag = self.rave().context("default_context").bag()
        if not eval:
            return bag.iterators.roster_set(where=conditions, sort_by=sort)
        else:
            return self.rave().eval(bag, self.rave().foreach(self.rave().iter("iterators.roster_set", where=conditions, sort_by=sort), *eval))
    
    def getTrips(self, conditions, sort=None, area=-1, eval=None):
        """
        Evaluates Rave on the trip level, or returns a bag (if eval is not set).
        """
        import Cui
        if isinstance(conditions, str): conditions = (conditions,)
        if area < 0: area = Cui.CuiScriptBuffer
        if type(eval) is str:
            eval = (eval, )
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "window")
        bag = self.rave().context("default_context").bag()
        if not eval:
            return bag.iterators.trip_set(where=conditions, sort_by=sort)
        else:
            return self.rave().eval(bag, self.rave().foreach(self.rave().iter("iterators.trip_set", where=conditions, sort_by=sort), *eval))
    
    def getCrewRoster(self, id=0, empno=0):
        """
        Returns crew with the given ID or empno
        """
        assert id or empno, "Invalid test: Either crew or empno must be specified"
        crew = list(self.getRosters('crew.%%id%% = "%s"' % id).bag())
        assert crew and len(crew) == 1, "Crew %s not found" % id
        return crew[0]
        
    def getCrewInWindow(self, area=-1):
        """
        Returns a list of all the crew in a given window. The return value is a dictionary of crew id and empno, same 
        way as getCrew.
        """
        import Cui
        if area < 0: area = Cui.CuiScriptBuffer
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "window")
        c, = self.rave().eval("default_context", self.rave().foreach(self.rave().iter("iterators.roster_set"), "crew.%id%", "crew.%extperkey%"))
        dict = {}
        print c
        for _, id, ep in c:
            dict[id] = ep
        return dict
    
    def getCrew(self, homebases=None, extsys=None, region=None, date=None, cat=None, crewemployment=False, crewcontract=False, max_crew=0):
        """
        Return a dictionary of crew id and crew entities for crew matching
        certain conditions.
        The crewemployment flag allows returning of crew_employment entities
        instead of crew entities.
        This function is useful for quickly finding e.g. the empno of a SKN CC. 
        """
        dict = {}
        if not date:
            date = self.getNowTime()
        else:
            date = AbsTime(date)
        if not cat: cat = None
        elif cat.upper() in ["FD","FC"]: cat = "F"
        elif cat.upper() in ["CC"]: cat = "C"
        if homebases:
            if isinstance(homebases, str): homebases = [homebases]
            elif isinstance(homebases, tuple): homebases = list(homebases)
        if extsys:
            homebases = [x.region for x in self.table('salary_region').search('(&(extsys=%s)(validfrom<%s)(validto>=%s))' % (extsys, date, date)) if not homebases or x.region in homebases]            
        if homebases != None and len(homebases) == 0: return dict
        valid='(validfrom<=%s)(validto>%s)' % (date,date)
        Q = [valid]
        if homebases:
            Q.append('(|%s)' % ''.join(['(base.id=%s)' % x for x in homebases]))
        if region:
            Q.append("(region=%s)" % region.upper())
        # Fill the dict([(id1, perkey1), (id2, perkey2), ...])
        query = '(&%s)' % ''.join(Q)
        for ce in self.table('crew_employment').search(query):
            #try:
                if cat is None or ce.titlerank.maincat.id == cat:
                    id = ce.crew.id
                    if crewemployment:
                        dict[id] = ce
                    elif crewcontract:
                        dict[id] = None
                        for cc in ce.crew.referers("crew_contract", "crew"):
                            if cc.validfrom <= date and cc.validto >= date:
                                dict[id] = cc
                                break 
                    else:
                        dict[id] = ce.crew
                if max_crew and max_crew > 0:
                    if len(dict) >= max_crew:
                        return dict
            #except Exception, e:
            #    print "Reference error in 'crew_employment': %s (%s)" % (ce, e)
        return dict

    
    def displayRosters(self, *conds, **kwargs):
        import Cui
        area = kwargs.get('area', 0)
        assert isinstance(area, int) and area >=-1 and area <= 3, "Invalid test: Incorrect area specified"
        if area < 0: area = Cui.CuiWhichArea(Cui.gpc_info, area)
        
                
    def table(self, tablename):
        """
        Returns a table from the model.
        """
        try:
            from tm import TM
        except:
            self.fail("The table manager is not available in this context")
        return getattr(TM, tablename)
    
    def cleanupFiles(self, *files):
        "Removes any files that exist. Never fails."
        for f in files:
            try:
                os.unlink(f)
            except:
                pass
            
    
    def shellcommand(self, command, stdin=""):
        p = subprocess.Popen(command, shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        
        (stdout, stderr) = p.communicate(stdin)
        if p.returncode != 0:
            self.log(stdout, "Info")
            self.fail("Command failed\n%s" % stderr)
        return stdout
    def validateXML(self, xml, schema=None):
        "Check XML for well-formedness or XSD schema validation"
        if not schema:
            cmdline = "xmllint --noout"
        else:
            cmdline = "xmllint --noout --schema '%s' -" % schema
        p = subprocess.Popen(cmdline,
                             shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        
        (stdout, stderr) = p.communicate(xml)
        if p.returncode != 0:
            self.fail("'xmllint' failed.\n(stdout):\n%s(stderr):\n%s\n" % (stdout, stderr))
        return stderr
    
    ######################################################
    # PREREQUISITES
    # Below are some class methods required to implement 
    # the prerequisites checking. This logic us used to
    # determine if a test is even possible to run.
    ######################################################
    
    @classmethod
    def hasPrerequisites(cls, funcname, outPrereq=None):
        "Returns True if the test function's prerequisites are met. See also available()."
        if not hasattr(cls, funcname): return False
        func = getattr(cls, funcname)
        if not hasattr(func, '_prerequisite'): return True
        for req in getattr(func, '_prerequisite'):
            assert hasattr(cls, 'is'+req),  "Unknown prerequisite '%s'" % req
            if not getattr(cls, 'is'+req)():
                if not outPrereq == None:
                    outPrereq.append(req)
                else:
                    return False
        if not outPrereq == None:
            return len(outPrereq) == 0
        return True
    
    @classmethod
    def available(cls, outPrereq=None):
        "Returns True if all the test's prerequisites are met"
        return cls.hasPrerequisites('__init__', outPrereq)

    @classmethod
    def isStudio(cls):
        """
        Returns True if running in Studio, False otherwise.
        """
        try:
            # This import succeeds in Studio, but fails
            # in carmrunner scripts
            import Gui
            return True
        except ImportError:
            return False 
        
    @classmethod
    def isExtensiveTestsEnabled(cls):
        """
        Returns True if extensive tests should be run
        """
        return os.environ.get("RUN_EXSTENSIVE_TESTS","0").lower() in ["1","true","t"]
        
    @classmethod
    def isNotMigrated(cls):
        """
        Always returns false
        """
        return False

    
    @classmethod
    def isNotStudio(cls):
        """
        Returns True if not running inside Studio.
        """
        return not cls.isStudio()

    @classmethod
    def isMirador(cls):
        """
        Returns True if running inside Mirador.
        """
        try:
            import modelserver
            return cls.isNotStudio()
        except:
            return False
    
    @classmethod
    def isPlanLoaded(cls):
        try:
            import MenuState
            if MenuState.theStateManager.getVal("SubPlanRuleSetLoaded"):
                return True
            return False
        except:
            return False
    
    @classmethod
    def isNoPlanLoaded(cls):
    	return not cls.isPlanLoaded()

    @classmethod
    def isTracking(cls):
        """
        Returns True if running in Tracking Studio, False otherwise.
        """
        if not cls.isStudio(): return False
        try:
            import carmusr.application as application
            if application.isTracking: return True
            return False
        except ImportError, err:
            raise err

    @classmethod
    def isPlanning(cls):
        """
        Returns True if running in Planning Studio, False otherwise.
        """
        if not cls.isStudio(): return False
        try:
            import carmusr.application as application
            if application.isPlanning: return True
            return False
        except ImportError, err:
            raise err 

    @classmethod
    def isReportWorker(cls):
        """
        Returns True if running in a report server, False otherwise.
        """
        if not cls.isStudio(): return False
        try:
            import carmusr.application as application
            if application.isReportWorker: return True
            return False
        except ImportError, err:
            raise err
        
    @classmethod
    def isDangerousDatabaseOperations(cls):
        """
        Returns True if potentially descructive tests should be run
        """
        return os.environ.get("RUN_DANGEROUS_DATABASE_TESTS","0").lower() in ["1","true","t"]
            
    @classmethod
    def getReportServerPublishType(cls):
        try:
            import carmensystems.common.reportWorker as reportWorker
            publishType = reportWorker.ReportGenerator().getPublishType()
            if not publishType:
                return ''
        except:
            return None
        
class DaveTestFixture(TestFixture):
    def __init__(self):
        TestFixture.__init__(self)

    @classmethod
    def isDatabase(cls):
        """
        Returns True if DAVE is available
        """
        try:
            from carmensystems.dig.framework.dave import DaveSearch, createOp, DaveConnector, DaveStorer
        except ImportError, err:
            return False 
        if not 'DB_URL' in os.environ:
            return False
         
        if not 'DB_SCHEMA' in os.environ:
            return False
        return True
        
    def db(self):
        """
        Returns a Dave connector to the configured schema.
        """
        from carmensystems.dig.framework.dave import DaveConnector
        dc = DaveConnector(os.environ['DB_URL'], os.environ['DB_SCHEMA'])
        print os.environ['DB_URL']
        print os.environ['DB_SCHEMA']
        print dc
        #dc.getConnection().setProgram("UnitTest")
        return dc
        
    def sql(self, query):
        from carmensystems.dig.framework.dave import DaveConnector
        dc = DaveConnector(os.environ['DB_URL'], os.environ['DB_SCHEMA'])
        try:
            conn = dc.getL1Connection()
            conn.rquery(query, None)
            rv = []
            while True:
                a = conn.readRow()
                if a == None: break
                rv.append(a.valuesAsList())
            conn.endQuery()
            return rv
        finally:
            dc.close()
        
    def sqlRow(self, query):
        from carmensystems.dig.framework.dave import DaveConnector
        dc = DaveConnector(os.environ['DB_URL'], os.environ['DB_SCHEMA'])
        try:
            conn = dc.getL1Connection()
            conn.rquery(query, None)
            rv = []
            a = conn.readRow()
            if a: a = a.valuesAsList()
            conn.endQuery()
            return a
        finally:
            dc.close()
        
class MacroTestFixture(TestFixture):
    """A test fixture for unit tests that uses macro templates a la Per Gronberg"""
    def __init__(self):
        TestFixture.__init__(self)

    def run_macro(self, macro, values={}):
        import carmensystems.studio.MacroRecorder.PlayMacro as PM
        f = None
        try:
            f = self._expand_macro(macro, values)
            PM.PlayMacroFile(f)
        finally:
            try:
                if f: os.unlink(f)
            except:
                pass
            
    
    def _expand_macro(self, macro, values):
        import tempfile
        (fd_out, file )= tempfile.mkstemp()
        try:
            for line in macro.split("\n"):
                for val in values:
                    line = line.replace(val,values[val])
                os.write(fd_out, line)
        finally:
            os.close(fd_out)     
        self.log('Created macro file, %s'%file)
        return file
        
        

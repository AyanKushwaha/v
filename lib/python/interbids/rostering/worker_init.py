"""
worker_init
main entry for rostering report server
Module for doing:
answer replyes from the crew portal

Registers the implemented functions as xmlrpc services!
Done in bottom of file

Currently implemented

1. get_rosters
2. get_trips
3. version
3. get_all_trips
4. get_roster_carryout

@date:07Feb2012
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""

import inspect
import cProfile, pstats
import os, os.path
import traceback
import time
import sys

from interbids.rostering.xml_handler.constants import VERSION, GET_ROSTERS,\
    GET_ALL_TRIPS, GET_TRIPS, GET_AVAILABLE_DAYS_OFF, CREATE_REQUEST,\
    CANCEL_REQUEST, GET_ROSTER_CARRYOUT, LIST_MODULES, RELOAD_MODULES
import carmensystems.rave.api as rave
#import carmensystems.common.worker as RW #@UnresolvedImport
import interbids.rostering.worker as RW
import AbsTime
# speed up things by early imports
import carmusr.AccountHandler #@UnusedImport
import tm #@UnusedImport
import modelserver #@UnusedImport
import Cui #@UnusedImport

class RequestError(Exception):
    
    def __init__(self, err, crewid, traceback):
        self._err = err
        self._crewid = crewid
        self._traceback = traceback
        self._timestamp = '%s-%s-%s %s:%s'%time.localtime()[:5]
        
    @property
    def crewid(self):
        '''
        return crewid
        '''
        return self._crewid
    
    def __str__(self):
        '''
        Pretty print message
        '''
        return os.linesep.join(['## Timestamp: %s :: Error: %s ##'%(self._timestamp, self._err),
                                self._traceback])
    
def handle_request(*args, **kwds):
    '''
    Handle the the request by checking request and calling response creator module
    adding cancel_request=True will tigger cancel request handling instead of create request
    '''
    parser = None
    try:
        sXml = args[0]
        cancel_request  = kwds.get('cancel_request',False)
        # leave the parsing to class ParseAndServiceRequest
        import interbids.rostering.request_parser_and_service as  request_parser_and_service
        # reload(request_parser_and_service)
        if cancel_request:
            parser = request_parser_and_service.ParseAndServiceCancelRequest(sXml)
        else:
            parser = request_parser_and_service.ParseAndServiceRequest(sXml)
        # call parser to service request
        return parser()
    except Exception, err:
        # wrapper will log error, let's prepare some info
        crewid = 'Unknown_crew' 
        err = str(err)
        if parser is not None:
            crewid = parser.get_crewid()
        # return traceback and all for debugging purposes
        raise RequestError(err, crewid, traceback.format_exc())
       
    
def version():
    """
    return version,
    Return 0
    Crew portal also uses version request as a ping
    """
    return 0


def list_modules():
    """
    List the python modules that are currently loaded
    """
    return '\n'.join(sorted(sys.modules.keys()))


def reload_modules(modules):
    """
    Reload the python modules specified in modules
    """
    for module in modules:
        print "Reloading module %s" % module
        reload(sys.modules[module])
    return 0


def cancel_request(*args, **kwds):
    """
    Use handle request but add the cancel flag
    """
    kwds['cancel_request']=True
    return handle_request(*args, **kwds)

def setup():
    '''
    Do some things on init of report worker
    Needs to be done before first fork if it is to majke anty difference!
    Currently:
        1. preload rave tables
    '''
    # preload rave by calling legality checks for a selection of crew
    all_crew_bag = rave.context("sp_crew").bag()
    for crewid in ('10033','10034','10066'):
        where_filter = 'interbids.%%roster_crewid%%="%s"'%crewid
        # get subtrees for all crew (or just the one
        for crew_bag in all_crew_bag.iterators.chain_set(where=where_filter):
            # return subtree with all roster
            for f_bag, fail in crew_bag.rulefailures():
                pass
            # force rave eval of compdays
            crew_bag.compdays.preload_account_entry_transaction_table()
            crew_bag.compdays.preload_account_entry_search_table()
            crew_bag.compdays.preload_account_entry_check_table()
            crew_bag.compdays.preload_leave_account_entry_count()
            crew_bag.freedays.half_freeday_in_history(AbsTime.AbsTime('1jan1986'))
            
def toggle_call_log():
    if is_log_enabled("call_log_enabled"):
        remove_log_file("call_log_enabled")
    else:
        create_log_file("call_log_enabled")
    return is_log_enabled("call_log_enabled")

def toggle_profiling():
    if is_log_enabled("profiling_enabled"):
        remove_log_file("profiling_enabled")
    else:
        create_log_file("profiling_enabled") 
    return is_log_enabled("profiling_enabled")

def registerWorkerMethod(func, name, *args, **kwargs):
    """
    Register a wrapped verions of a function in the worker.
    The wrapped version has support for:
       * Better error handling
       * Logging of:
           * Execution time
           * Request and response (call toggle_call_log XMLRPC function)
           * Profiling data       (call toggle_profiling XMLRPC function)
       * Reload of Python code    (call reload_python XMLRPC function)
    """

    # Store qualified name of function instead of function itself.
    # This allows reload of Python modules
    func_qname = get_qname(func)
    resolve_qname(func_qname)  # Resolve it at init to trigger any lookup error

    def wrapped(*args, **kwargs):
        call_id = "%.10f"%time.time()
        resp = None
        try:
            call_log_enabled = is_log_enabled("call_log_enabled")
            profiling_enabled = is_log_enabled("profiling_enabled")

            if call_log_enabled: write_log_file(call_id, name, "req", 'w', *args, **kwargs)
            func = resolve_qname(func_qname)
            if profiling_enabled:
                prof = cProfile.Profile()
                t1 = time.time()
                resp = prof.runcall(func, *args, **kwargs)
                t2 = time.time()
                prof.dump_stats(get_log_file(call_id, name, "prof"))

                fd = open(get_log_file(call_id, name, "prof.txt"), "w")
                fd.write("Serving XMLRPC-call %s %s. Elapsed time=%.5fs.\n"%(name, call_id, t2-t1))
                stats = pstats.Stats(prof, stream=fd)
                stats.strip_dirs().sort_stats(-1).print_stats()
                fd.close()
            else:
                t1 = time.time()
                resp = func(*args, **kwargs)
                t2 = time.time()
            if call_log_enabled: write_log_file(call_id, name, "resp", 'w', resp)
        except RequestError, err:
            t2 = time.time()
            print "Error in XMLRPC-call %s %s"%(name, call_id)
            traceback.print_exc()
            write_log_file('crew-%s'%err.crewid, name, "req", 'w', *args, **kwargs)
            write_log_file('crew-%s'%err.crewid, name, "error", 'a', str(err))
            raise
        except:
            t2 = time.time()
            print "Error in XMLRPC-call %s %s"%(name, call_id)
            traceback.print_exc()
            write_log_file(call_id, name, "req", 'w', *args, **kwargs)
            fd = open(get_log_file(call_id, name, "exc"), "w")
            traceback.print_exc(file=fd)
            fd.close()
            raise
        finally:
            print "Served XMLRPC-call %s %s in %.5fs."%(name, call_id, t2-t1)
        return resp

    RW.registerWorkerMethod(wrapped, name, *args, **kwargs)

def get_log_file(call_id, method_name, log_type):
    file_name = os.path.join(os.environ.get("CARMTMP"),
                             "logfiles",
                             "xmlrpc",
                             "%s-%s.%s"%(call_id, method_name, log_type))
    if not os.path.exists(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name))
    return file_name

def is_log_enabled(name):
    return os.path.exists(os.path.join(os.environ.get("CARMTMP"),
                                       "logfiles",
                                       "xmlrpc",
                                       name))
def create_log_file(name):
    open(os.path.join(os.environ.get("CARMTMP"),
                      "logfiles",
                      "xmlrpc",
                      name), 'w').close()

def remove_log_file(name):
    os.remove(os.path.join(os.environ.get("CARMTMP"),
                           "logfiles",
                           "xmlrpc",
                           name))

def write_log_file(call_id, method_name, log_type, filemode, *args, **kwargs):
    fd = open(get_log_file(call_id, method_name, log_type), filemode)
    for x in args:
        fd.write(unicode(x))
        fd.write("\n")
    if kwargs:
        fd.write("{\n")
        for (x, y) in kwargs.iteritems():
            fd.write(unicode(x))
            fd.write(": ")
            fd.write(unicode(y))
            fd.write("\n")
        fd.write("}\n")
    fd.close()

def get_qname(x):
    if inspect.ismodule(x):
        return x.__name__
    elif inspect.isclass(x):
        # TODO: may not be defined directly in module
        return get_qname(inspect.getmodule(x)) + "." + x.__name__
    elif inspect.ismethod(x):
        if x.__self__ is None:
            raise Exception("Method not bound to an object.")
        return get_qname(x.__self__.__class__) + "." + x.__name__
    elif inspect.isfunction(x):
        # TODO: may not be defined directly in module
        return get_qname(inspect.getmodule(x)) + "." + x.__name__
    else:
        raise Exception("Can not determine qualified name for object: %s"%x)

def resolve_qname(name):
    """
    Resolve a named Python function.
    """
    path = name.split(".")
    i = 1
    module = None
    while i <= len(path):
        module_name = ".".join(path[0:i])
        try:
            module = __import__(module_name, globals(), locals(), [module_name])
        except ImportError:
            if module is None:
                raise
            else:
                # We found the deepest module, continue resolving inside module.
                break
        i = i+1

    try:
        return resolve_name_in_object(module, path[i-1:])
    except AttributeError:
        raise AttributeError("Can not find qname %s"%name)

def resolve_name_in_object(x, path):
    if path == []:
        return x
    else:
        y = getattr(x, path[0])
        return resolve_name_in_object(y, path[1:])

# Register services
# function and name in xmlrpc list of functions
registerWorkerMethod(version, VERSION)
registerWorkerMethod(list_modules, LIST_MODULES)
registerWorkerMethod(reload_modules, RELOAD_MODULES)
registerWorkerMethod(handle_request, GET_ROSTERS, alwaysRefresh=True)  # Always refresh so that get_rosters call immediately after create_request has correct data.
registerWorkerMethod(handle_request, GET_ROSTER_CARRYOUT)
registerWorkerMethod(handle_request, GET_ALL_TRIPS)
registerWorkerMethod(handle_request, GET_TRIPS)
registerWorkerMethod(handle_request, GET_AVAILABLE_DAYS_OFF)
registerWorkerMethod(handle_request, CREATE_REQUEST, writeDave=True, checkConflicts=RW.SpecifiedOnly)
registerWorkerMethod(cancel_request, CANCEL_REQUEST)
registerWorkerMethod(toggle_call_log, "toggle_call_log")
registerWorkerMethod(toggle_profiling, "toggle_profiling")


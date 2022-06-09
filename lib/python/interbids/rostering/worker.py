'''
Created on May 29, 2012

@author: pergr
'''
import os, sys, traceback
from xmlrpclib import Fault
from carmensystems.common.reportWorker import loginfo, logdebug, logerror
import modelserver
from carmensystems.common.dave_utils import EC, RW
from utils.dave import txninfo
from carmensystems.common.clockrequest import clockrequest

RETRY_FAULT_CODE = 9010
MAX_RETRIES_FAULT_CODE = 9009

# Conflict handling
CONFLICTHANDLING = (No, All, SpecifiedOnly) = (False,True,-1)
# Conflict response
CONFLICTRESPONSE = (Fail, Retry) = (None,1)
# Retry handling
RETRYHANDLING = (Again,Refresh) = (None,1)
# Max retries handling
MAXRETRIESHANDLING = (Fail,) = (None,)

_RetryCount = 0

def getretrycount():
    return _RetryCount

def registerWorkerMethod(func, name=None, writeDave=False, alwaysRefresh=False, checkConflicts=No, onConflict=Retry, onRetry=Refresh, maxRetries=1, onMaxRetries=Fail, reloadModule=False):
    """
    Registers a worker method within the report worker.
    Arguments:
    func -- The function to register
    name -- XMLRPC name of the function (default is the function name)
    writeDave -- If true, model deltas are written with Dave. Default is False.
    alwaysRefresh -- If true, model is always refreshed first
    checkConflicts -- One of (No, All, SpecifiedOnly).
       No -- Does not perform any conflict handling whatsoever (default)
       All -- All modified entities are checked for conflicting updates
       SpecifiedOnly -- Only the specified entities are checked for conflicting updates. In this
                        mode, func expects to return a tuple, the second item being the entities
                        or table names to conflict handle.
                        If None is returned as conflict spec, nothing is written to the database.
    onConflict -- Action to perform on conflict. A function that takes the exception as a parameter.
                  Special values are Retry, which tells the portal to retry the operation, and Fail,
                  which just passes on the exception. Default is Retry.
    onRetry -- Action to perform before calling func when a retry is encountered. A function that takes
               the retry count and the original arguments. Special values are Refresh, which forces a
               model refresh before, and Again, which does nothing. Default is Refresh.
    maxRetries -- Maximum number of retries. <=0 means retry is not allowed. Default is 1.
    onMaxRetries -- Action to perform when maximum number of retries has been exceeded. A function that
                    takes the retry count and the original arguments. Special value is Fail, which raises
                    a Fault. Default is Fail.
    reloadModule -- A debug option to force reload of the Python module containing func before running it.
    """
    import carmensystems.studio.webserver.XMLRPCDispatcher as XD
    
    state = {'Refresh':alwaysRefresh}
    
    if name is None:
        name = func.__name__
    retryName = "portal.retry.%s" % name
    if not checkConflicts in CONFLICTHANDLING:
        raise ValueError("Incorrect value for checkConflicts")
    if onConflict == Retry:
        def __retry(e):
            raise Fault(RETRY_FAULT_CODE, "Try again, %s" % e)
        onConflict = __retry
    if onConflict and not hasattr(onConflict, '__call__'):
        raise ValueError("Incorrect value for onConflict")
    if onRetry == Refresh:
        def __refresh(retryCount, *args):
            loginfo("In refresh, forcing refresh")
            state['Refresh'] = True
        onRetry = __refresh
    if onRetry and not hasattr(onRetry, '__call__'):
        raise ValueError("Incorrect value for onRetry")
    if onMaxRetries and not hasattr(onMaxRetries, '__call__'):
        raise ValueError("Incorrect value for onMaxRetries")
    tm = modelserver.TableManager.instance()
    
    implementation_func = func
    
    def rpcEntryPoint(*args):
        writeDaveLocal = writeDave
        logdebug("In RPC entry point for %s" % name)
        if state['Refresh']:
            loginfo("Refreshing from cid=%s"%tm.getCid())
            tm.reopen()
            tm.reopenRaveStorage()
            tm.refresh()
            tm.reloadRaveTables()
            loginfo("Refreshed to cid=%s"%tm.getCid())
        if writeDaveLocal:
            begin = tm.newState()
            tm.newState()
            tm.lock()
        func = implementation_func
        if reloadModule:
            try:
                func = getattr(reload(sys.modules[func.__module__]),func.__name__)
            except:
                traceback.print_exc()
                logerror('Failed to reload module for %s' % func)
        if checkConflicts == SpecifiedOnly:
            logdebug('Calling %s, expect conflict handling spec' % func)
            result, conflictspec = func(*args)
            if conflictspec is None:
                writeDaveLocal = False
        else:
            logdebug('Calling %s' % func)
            if checkConflicts == All:
                conflictspec = ["*"]
            else:
                conflictspec = None
            result = func(*args)
        if writeDaveLocal:
            logdebug('Will write dave')
            try:
                _applyDaveDelta(tm, begin, conflictspec)
            except Exception, e:
                loginfo("Conflict: %s" % e)
                loginfo(traceback.print_exc())
                if onConflict:
                    return onConflict(e)
                else:
                    raise
        return result
    def retryEntryPoint(retryCount, *args):
        global _RetryCount
        retryCount = int(retryCount)
        _RetryCount = retryCount
        loginfo('Retrying(%s) %s' % (retryCount, func))
        if retryCount > maxRetries:
            if onMaxRetries:
                return onMaxRetries(retryCount, *args)
            else:
                raise Fault(MAX_RETRIES_FAULT_CODE, "Max retries exceeded")
        if onRetry:
            onRetry(retryCount, *args)
        return rpcEntryPoint(*args)
    logdebug("Registering %s as %s" % (func, name))
    ret = XD.xmlrpc_registerfunction(rpcEntryPoint, name)
    XD.xmlrpc_registerfunction(retryEntryPoint, retryName)
    return ret

@clockrequest
def _connect(connectString, dbschema):
    logdebug("DB Connect '%s' schema '%s'" % (connectString, dbschema))
    # here , using sasusr test code , change for real dave code???
    entityConnection = EC(connectString, dbschema)
    recWriter = RW(entityConnection)
    return recWriter, entityConnection

@clockrequest
def _apply(recWriter, entityConnection):
    revid = recWriter.apply()
    return txninfo(entityConnection, revid).commitid

@clockrequest    
def _applyDaveDelta(tm, begin, conflicthandling):
    logdebug("in _applyDaveDelta (begin=%s)" % begin)
    tm.unlock()
    modelDiff = tm.difference(begin)
    conflicttables = set()
    conflictentities = set()

    for ent in (conflicthandling or []):
        if hasattr(ent, 'getI'):
            pk = str(ent.getI())
            revid = ent.getI().revId()
            table = ent.getI().desc().name()
            print "C",pk,revid,table
            conflictentities.add((table, pk))
        elif isinstance(ent, str):
            conflicttables.add(ent)
    logdebug("Conflict Tables: %s" % conflicttables)
    logdebug("Conflict Entities: %s" % conflictentities)
    if not modelDiff:
        logdebug("ModelDiff is empty")
        return

    """
    open a connection, it was lost at the last fork ??
    """
    dbschema = tm.getSchemaStr()
    connectString = tm.getConnStr()
    recWriter, entityConnection = _connect(connectString, dbschema)
    try:
        from reportWorkerMS import msEncoding
    except:
        msEncoding = 'latin-1'

    # to handle publish roster in call, we need to 
    # have a second step in apply that gets the cid from
    # first save
    publish_roster_data_dict = []
    for c in modelDiff:
        try:
            logdebug("ModelDiff item: " + str(vars(c.getEntityI())))
            pk = str(c.getEntityI())
            revid = c.getEntityI().revId()
        except Exception:
            loginfo(traceback.print_exc())
            raise
        op = {modelserver.Change.ADDED:'new',
              modelserver.Change.MODIFIED:'update',
              modelserver.Change.REMOVED:'delete'}[c.getType()]
        entity_name = c.getTableName()
        print "pk , current revid , table_name: ", (pk,revid,entity_name)
        useConflict = ("*" in conflicttables) or (entity_name in conflicttables) or ((entity_name,pk) in conflictentities)
        data_dict = c.toDave()
        if useConflict:
            data_dict["revid"] = revid
        for i in data_dict:
            if isinstance(data_dict[i], str):
                global msEncoding
                data_dict[i] = unicode(data_dict[i], msEncoding)
        # save these changes later on
        if entity_name == 'published_roster':
            publish_roster_data_dict.append((op,  data_dict))
            continue

        print "Dave call: op, entity_name , data_dict ", (op, entity_name , data_dict) 
        
        if op == 'new':
            getattr(recWriter, entity_name).dbwrite(data_dict)
            print "inserting new record"
        elif op == 'update':
            getattr(recWriter, entity_name).dbwrite(data_dict)
            print "updating record"
        elif op == 'delete':
            getattr(recWriter, entity_name).dbdelete(data_dict)
            print "deleting record"
                
    cid = _apply(recWriter, entityConnection)
    print "new cid from db= ", cid


    # handle publish roster
    # if we have operations here, we use the
    # new cid, otherwise return
    if not publish_roster_data_dict:
        return
    recWriter, entityConnection = _connect(connectString, dbschema)
    
    for op, data_dict in publish_roster_data_dict:
        print "Will use pubcid = ", cid
        # reset pubcid to correct
        data_dict['pubcid'] = cid

        print "Dave call: op, entity_name , data_dict ", (op, 'published_roster' , data_dict) 
        if op == 'new':
            getattr(recWriter, 'published_roster').dbwrite(data_dict)
            print "inserting new record"
        elif op == 'update':
            getattr(recWriter, 'published_roster').dbwrite(data_dict)
            print "updating record"
        elif op == 'delete':
            getattr(recWriter, 'published_roster').dbdelete(data_dict)
            print "deleting record"   
    newcid = _apply(recWriter, entityConnection)

    print "new cid from db after publ= ", newcid 

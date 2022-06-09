

"""
INTERFACES TO THE REPORT SERVER.


External interfaces
===================
These are the public interfaces to the Report Server.

Report Server V1 (Classic)
--------------------------
Signature:
    filename = save(t, d)

Indata:
    t        (tuple)  : Positional arguments.
    d        (dict)   : Keyword (named) arguments.

Return value:
    filename (string) : Name of a temporary file that contains the report.
                         
The report server is responsible of deleting this file.

Error handling:
    Faulty conditions will result in an Exception.

This interface suffers from a number of limitations:
 l. No way of returning several deliverables (e.g. a report and a status
    message).
 2. The report itself has to take care of committing changes to the data model,
    since there is no way of sending a valid report (with a fault message) and
    at the same time signal that updates of data model should be rolled back.


Report Server V2
----------------
Signature:
    reports, use_delta = generate(arg)

Indata:
    arg      (tuple)  : Positional arguments and keyword arguments.

        arg = (t, d) 
        t   = (arg1, ...)
        d   = {'kwarg1': value1, ...}

Return values:
    reports    (list) : List of dictionaries with content and destinations.

        reports = [reportN, ...]

        reportN (dict): {'content-type': content_type, 'content': content,
                        'destination': dest}
        -*- or -*- 
        reportN (dict): {'content-location': content_location, 'destination': dest}

            content_type (string) : MIME-type of the message
            content      (string) : The result.
            dest         (list)   : List of Tuples with destination specific data.

                dest = [(pnameN, pdataN), ...]

                pnameN   (string) : Protocol identifier.
                pdataN   (dict)   : Protocol specific data.

    use_delta  (bool) : Signals if data changes should be committed to the data
                        model.


Internal interfaces
===================
These interfaces are used internally. The benefit of having private internal
interfaces in addition to the public external, is that the report could have
many different uses. Example: the same report could be used by the Report
Server and, internally, by a dialog in Studio. This would allow the Tracker to
see the same output as the Crew got in the report interface.


Internal interface 1 (report)
-----------------------------
These reports will result one deliverable unit (a report) per invokation.
They could, as a side-effect, also update the model.


1. Simple report with no updates of model (report)
--------------------------------------------------
    Signature:
        report_string = report(*args, **kwargs)

    Indata:
        *args    : Variable number of positional arguments.
        **kwargs : Variable number of keyword (named) arguments.

    Return value:
        report_string : (string) containing the result.

    Error handling:
        Faulty conditions will result in an Exception.


2. Simple report with updates of model (report)
-----------------------------------------------
Same signature as above:

    report_string = report(*args, **kwargs)

The difference is that this report has "side effects" (updates data in the model).

In case of faults, an exception is raised, which will prevent updates of the
data model, but no usable return value is returned.

The error handling or return value has to be handled by another component (e.g.
DIG).


Internal interface 2 (report_delta)
-----------------------------------
Simple report with updates of model (report_delta).

Signature:
    report_string, use_delta  = report_delta(*args, **kwargs)

Indata:
    *args    : Variable number of positional arguments.
    **kwargs : Variable number of keyword (named) arguments.

Return values:
    report_string (string) : String containing the result.
    use_delta     (bool)   : Signals if model changes should be committed.

Error handling:
    Anticipated errors (e.g. the flight did not exist) would *NOT* result in an
    Exception. The report is responsible of formatting a valid 'report_string'
    (possibly containing references to the failing condition).
    In this case the report would set the 'use_delta' flag to 'False'.

    Non-anticipated faults *could* (but, not necessarily) result in the report
    raising an exception. In this case (of course) no updates are done.


Internal interface 3 (report_file)
----------------------------------
Simple report with updates of model.

Signature:
    filename, use_delta  = report_file(*args, **kwargs)

Indata:
    *args    : Variable number of positional arguments.
    **kwargs : Variable number of keyword (named) arguments.

Return values:
    filename      (string) : String containing the pathname of the resulting report.
    use_delta     (bool)   : Signals if model changes should be committed.

Error handling:
    See 1.3 above.


Complex reports - internal interface equals the external interface
==================================================================
These reports result in several deliverable units (reports) per invokation.
They could, as a side-effect, also update the model.

Since these reports can have many different sources, and can result in any
number of reports, there is *NO* defined internal interface.

The report itself is responsible for collecting and formatting the data.


USE OF DECORATORS (Examples)
============================

##    # -- In case of internal interface 1 and the classic Report Server V1:
##    from my.module import report
##    from report_sources.report_server.rs_if import RSv1_report
##    
##    @RSv1_report
##    def save(*a, **k):
##        return report(*a, **k)
##    
##    # -- In the case of internal interface 1 and the Report Server V2.
##    from my.module import report
##    from report_sources.report_server.rs_if import RSv1_report
##    
##    @argfix
##    @RSv2_report()            # Note the parentheses
##    def generate(*a, **k):
##        return report(*a, **k)
##    
##    # ...or if the report should update the model
##    @argfix
##    @RSv2_report(use_delta=True)
##    def generate(*a, **k):
##        return report(*a, **k)
##    
##    # -- Internal interface 2 and Report Server V2
##    @argfix
##    @RSv2_report_delta()
##    def generate(*a, **k):
##        return report(*a, **k)
##    
##    # ... same as above but with alternate destination
##    @argfix
##    @RSv2_report_delta(destination=alt_dest)
##    def generate(*a, **k):
##        return report(*a, **k)
##    
##    # -- Internal interface 3 and Report Server V2
##    @argfix
##    @RSv2_report_file()
##    def generate(*a, **k):
##        return report(*a, **k)
##    

FOR MORE EXAMPLES SEE: ../../tests/report_sources/hidden/test_rs_if.py
"""

# imports ================================================================{{{1
import os
import traceback
from tempfile import mkstemp
from dig.constants import default_destination, default_content_type, error_content_type


# globals ================================================================{{{1
__all__ = [ 'RSv1_report', 'RSv2_report', 'RSv2_report_delta',
    'RSv2_report_file', 'argfix', 'add_reportprefix', 'save' ]


# Decorators ============================================================={{{1

# RSv1_report ------------------------------------------------------------{{{2
def RSv1_report(func):
    """Decorator for the Report Server V1 interface, expects a tuple and a dict
    and returns the pathname of a temporary file.

    Converts Report Server V1 requests to calls to Internal interface 1 (report).
    """
    def wrapper(t=(), d={}):
        prefix = func.__module__.split('.')[-1] + '_'
        fd, fn = mkstemp(suffix='.tmp', prefix=prefix,
                dir=os.environ['CARMTMP'], text=True)
        f = os.fdopen(fd, 'w')
        f.write(func(*t, **d))
        f.close()
        return fn
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__dict__ = func.__dict__
    return wrapper


# RSv2_report ------------------------------------------------------------{{{2
def RSv2_report(use_delta=False, content_type=default_content_type,
        destination=default_destination):
    """Decorator for reports that return one single report as a plain string.

    Converts calls from Report Server V2 to Internal interface 1 (report).
    """
    def decorator(func):
        def wrapper(*a, **k):
            report = func(*a, **k)
            if report is None or report == "":
                return [], use_delta
            return [
                {
                    'content': report,
                    'content-type': content_type,
                    'destination': destination,
                }
            ], use_delta
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__dict__ = func.__dict__
        return wrapper
    return decorator


# RSv2_report_delta ------------------------------------------------------{{{2
def RSv2_report_delta(content_type=default_content_type, destination=default_destination):
    """Decorator for reports that return a tuple containg the report as string
    and a boolean that signals that the database should be updated.

    Converts calls from Report Server V2 to Internal interface 2 (report_delta).
    """
    def decorator(func):
        def wrapper(*a, **k):
            report, use_delta = func(*a, **k)
            return [
                {
                    'content': report,
                    'content-type': content_type,
                    'destination': destination,
                }
            ], use_delta
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__dict__ = func.__dict__
        return wrapper
    return decorator


# RSv2_report_file -------------------------------------------------------{{{2
def RSv2_report_file(use_delta=False, content_type=default_content_type, 
        destination=default_destination):
    """Decorator for reports that will result in one single file.

    Converts calls from Report Server V2 to Internal interface 3 (report_file).
    """
    def decorator(func):
        def wrapper(*a, **k):
            return [
                {
                    'content-location': func(*a, **k),
                    'content-type': content_type,
                    'destination': destination,
                }
            ], use_delta
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__dict__ = func.__dict__
        return wrapper
    return decorator


# argfix -----------------------------------------------------------------{{{2
def argfix(func):
    """
    Report Server v.2 will supply one argument: ((), {}), a tuple of a tuple
    and a dict or (if called from scheduler) a single dict.
    This decorator will try to convert this single argument to the standard
    (*args, **kwargs).
    """
    def wrapper(*a, **k):
        if (
                len(a) == 1
                and isinstance(a[0], (tuple, list))
                and len(a[0]) == 2
                and isinstance(a[0][0], (tuple, list))
                and isinstance(a[0][1], dict)
            ): 
            # The "standard" case
            return func(*a[0][0], **a[0][1])
        elif (
                len(a) == 1
                and isinstance(a[0], dict)
            ):
            # Called from scheduler
            return func(**a[0])
        else:
            return func(*a, **k)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__dict__ = func.__dict__
    return wrapper


# add_reportprefix -------------------------------------------------------{{{2
def add_reportprefix(func):
    """
    One of the named arguments 'reportprefix' is a prefix that should be
    prepended to all destination names.
    """
    def wrapper(*a, **k):
        if 'reportprefix' in k:
            rlist, delta = func(*a, **k)
            for r in rlist:
                D = []
                for name, params in r['destination']:
                    if name=='default':
                        name = ''
                    D.append((k['reportprefix'] + name, params))
                r['destination'] = D
            return rlist, delta
        else:
            return func(*a, **k)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__dict__ = func.__dict__
    return wrapper


# wrapper for Report Server V1 ==========================================={{{1

# save -------------------------------------------------------------------{{{2
def save(report, t=(), d={}):
    """
    OBSOLETE - use RSv1_report instead!

    't' is a tuple (positional arguments).
    'd' is a dictionary (named arguments).

    save() returns the name of a temporary file, which contains the result.
    
    The temporary file will have to be removed after it has been used.

    The Report Server will delete the file after it's contents has been
    returned.
    """
    prefix = report.__module__.split('.')[-1] + '_'
    (fd, fn) = mkstemp(suffix='.tmp', prefix=prefix,
            dir=os.environ['CARMTMP'], text=True)
    f = os.fdopen(fd, 'w')
    f.write(report(*t, **d))
    f.close()
    return fn


# fallback handling ======================================================{{{1

# fallback ---------------------------------------------------------------{{{2
def fallback(exc, *args, **kwargs):
    """
    Create an 'error' report, that can be handled by a FallBackHandler in DIG.
    See '$CARMUSR/lib/python/dig/xhandlers.py'.
    """
    return {
        'content': str(exc),
        'error-content': {
            'name': exc.__class__.__name__,
            'args': args,
            'kwargs': kwargs,
            'traceback': traceback.format_exc(),
            'string': str(exc),
        },
        'content-type': error_content_type,
        'destination': default_destination,
    }


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

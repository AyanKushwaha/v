
# [acosta:08/094@17:22] Created.

"""
Tools to be used from the server (model) side of Wave forms.

These are the prerequisites:

    1. The directory '$CARMUSR/lib/www' is accessible as 'http://<modelserver>/user'
    2. The directory '$CARMTMP/www' is accessible as 'http://<modelserver>/tmp'


For examples, see bottom of this file.

Things to do:
    - How handle errors? (Suggestion, create and return HTML document
      describing the error.)
    - Client lib (XML-inclusion, imports from Jython code, ...?)
"""

import os
import socket
import urlparse
import types
import traceback
from tempfile import mkstemp
import modelserver as M

from tm import TM, TempTable
from AbsTime import AbsTime
from RelTime import RelTime
from AbsDate import AbsDate


# globals ================================================================{{{1
# The directory where generated files, reports, etc. will land (on the server).
# NOTE: Will raise exception if env. CARMTMP is not there (and that's ok).

# Determine if running standalone or from within a Studio session.
try:
    import Cui
    import Gui
    print "Wave: STUDIO mode"
    STANDALONE = False
except:
    print "Wave: STANDALONE mode"
    STANDALONE = True

# Physical location of the web shares
tmp_dir = os.path.join(os.environ['CARMTMP'], "www")
user_dir = os.path.join(os.environ['CARMUSR'], "lib", "www")

# Corresponding locations.
# i.e. the directories above will be accessible from:
# http://server:port/user/... and http://server:port/tmp/...
tmp_location = 'tmp'
user_location = 'user'
    
# decorators ============================================================={{{1

# urlize -----------------------------------------------------------------{{{2
def urlize(func):
    """Decorator, return action to open an URL given as return value from
    function, using the Wave action 'openURL'."""
    def wrapper(*a, **k):
        return {'actions': 'openURL(%s);' % func(*a, **k)}
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__dict__ = func.__dict__
    return wrapper


# XML-RPC methods ========================================================{{{1

import carmensystems.services.dispatcher
class Service(carmensystems.services.dispatcher.StatelessService):
    componentName = "mirador.tablemanager"
    signature = "token, *args ->"
    
class ModelChangeService(Service):
    func = None    
    def work(self, *args):
        if self.func is None:
            raise Exception("Programming Fault: Service %s - func def missing."
                            % self.__class__.__name__)
        print "<ModelChangeService>%s%s" % (self.__class__.__name__, args)
        ret = self.__class__.__dict__['func'](*args)
        if not STANDALONE:
            Gui.GuiCallListener(Gui.ActionListener)
        return ret

class LocalService(Service):
    func = None    
    def work(self, *args):
        if self.func is None:
            raise Exception("Programming Fault: Service %s - func def missing."
                            % self.__class__.__name__)
        print "<LocalService>%s%s" % (self.__class__.__name__, args)
        return  self.__class__.__dict__['func'](*args)

def unicode_args_to_latin1(func):
    def wwrapper(*args, **kwds):
        def u2s(a):
            if isinstance(a, unicode):
                a = a.encode("latin-1")
                print "unicode_args_to_latin1: Unicode argument '%s' converted to latin-1" % a
            return a
        def wrapper(func, *args, **kwds):
            args = tuple(u2s(a) for a in args)
            kwds = dict((k,u2s(v)) for (k,v) in kwds.items())
            print "unicode_args_to_latin1: Calling %s(%s)" \
                  % (func.__name__, ",".join(tuple(str(a) for a in args) + 
                                             tuple("%s=%s" % (k,v) for (k,v) in kwds.items())))
            return func(*args, **kwds)
        return wrapper(func, *args, **kwds)
    print "unicode_args_to_latin1: Unicode arguments when calling function '%s' will be re-encoded to latin-1" % func.__name__
    return wwrapper


# show_document ----------------------------------------------------------{{{2
@urlize
def show_document(token, url, path):
    """
    XML-RPC method - show document in web browser.

      1. Show file in the 'tmp' tree.
      2. if not found there, show file in the 'user' tree.
      3. if not found there, symlink file to 'tmp' tree, and send url back.
    """
    def err_file(msg):
        fd, fn = mkstemp(prefix="utils_wave_", suffix=".html", dir=tmp_dir)
        f = os.fdopen(fd, "w")
        f.write("<html><head><title>File not found</title></head>\n"
                "<body><p>%s</p></body></html>\n" % msg)
        f.close
        return os.path.basename(fn)

    if path.startswith('/'):
        if os.path.exists(path):
            return normalize(url, make_link(path), tmp_location)
        else:
            # ERROR condition file did not exist
            return normalize(url, err_file("The file '%s' does not exist." % path), tmp_location)
    elif os.path.exists(os.path.join(tmp_dir, path)):
        return normalize(url, path, tmp_location)
    elif os.path.exists(os.path.join(user_dir, path)):
        return normalize(url, path, user_location)
    else:
        carmusr_source = os.path.join(os.environ['CARMUSR'], path)
        if os.path.exists(carmusr_source):
            return normalize(url, make_link(carmusr_source), tmp_location)
        else:
            return normalize(url, err_file("The file '%s' does not exist in the CARMUSR directory." % path), tmp_location)


# run_report -------------------------------------------------------------{{{2
@urlize
def run_report(token, url, report, format, *report_args):
    """
    XML-RPC method, launch report in client's web browser.

    report_args: ('CREW=1234', 'xyz=True')
    """
    import carmensystems.publisher.api as prt
    if format.upper() == 'HTML':
        format = prt.HTML
        suffix = '.html'
    else:
        format = prt.PDF
        suffix = '.pdf'
    fd, fn = mkstemp(suffix=suffix, prefix="utils_wave_", dir=tmp_dir)
    args = {}
    for arg in report_args:
        try:
            k, v = arg.split("=")
            args[k] = v
        except Exception, e:
            pass
    ofn = prt.generateReport(report, fn, format, args)
    return normalize(url, os.path.basename(ofn), tmp_location)
    

# refresh_wave_values ----------------------------------------------------{{{2
class WaveValuesTable(TempTable):
    """
    Temporary table for global settings used in Wave forms.
    Contains one entry only.
    
    In the <on-loaded> section of a Wave form, perform:
        model("carmensystems.mirador.tablemanager.refresh_wave_values")
    which performs an implicit 'refreshClient()' action.
    
    After that, values are accessible through:
        ${tmp_wave_values[FIELD,v]}
    where FIELD is one of:
        tm_mode:
            To determine tablemanager access mode: "STUDIO" or "STANDALONE"
        save_label/exit_label:
            For use as menu/button label: "_A_pply" or "_S_ave"
                                          "_C_lose" or "_E_xit"
        now_utc:
            Current system time in UTC.
        now_date_utc:
            Current system date in UTC.
            
    In order to get up-to-date values of time/date, perform:
        model("carmensystems.mirador.tablemanager.refresh_wave_values")
    before accessing the now_utc or now_date_utc fields.

    In server code, time/date values are accessible through:
        utils.wave.refresh_wave_values()
        utils.wave.get_now_utc()
        utils.wave.get_now_date_utc()
    Values that have been updated in the server will be seen in the Wave form
    after it has performed a refreshClient().
    """
    __name = 'tmp_wave_values'
    __keys = [M.StringColumn('key','')]
    __cols = [M.StringColumn('v', ''),
              M.TimeColumn('abs_v'),
              M.RelTimeColumn('rel_v'),
              M.IntColumn('int_v'),
              M.BoolColumn('bool_v')]
    timeserver = None
             
    def __init__(self):
        print "WaveValuesTable::__init__"
        TempTable.__init__(self, self.__name, self.__keys, self.__cols)
        self.refresh()
        
    def __setitem__(self, key, v):
        if isinstance(v, bool):
            value = str(v).lower()
        else:
            value = str(v)
        try:
            row = self[key]
        except M.EntityNotFoundError:
            row = self.create((key,))
        row.v = value
        try:
            if isinstance(v, bool):
                row.bool_v = v
            elif isinstance(v, AbsTime):
                row.abs_v = v
            elif isinstance(v, RelTime):
                row.rel_v = v
            elif isinstance(v, AbsTime):
                row.abs_v = v
            elif isinstance(v, int):
                row.int_v = v    
        except M.WrongTypeError, err:
            print "WaveValuesTable::__setitem__: Error setting typed column for key"+\
                  " %s, %s"%(key, err)
    def refresh(self):
        try:
            self['tm_mode']
            print "WaveValuesTable::refresh: already initialized"
        except:
            self['tm_mode'] = ("STUDIO", "STANDALONE")[STANDALONE]
            if STANDALONE:
                self['save_label'] = "_S_ave"
                self['exit_label'] = "_E_xit"
                if self.__class__.timeserver is None:
                    from utils import TimeServerUtils
                    self.__class__.timeserver = TimeServerUtils.TimeServerUtils(
                        useSystemTimeIfNoConnection=True)
            else:
                self['save_label'] = "_A_pply"
                self['exit_label'] = "_C_lose"
            print "WaveValuesTable::refresh: initialized:\n ", "\n  ".join(
                  [str(self[f]) for f in ('tm_mode','save_label','exit_label')])
        if STANDALONE:
            utc = AbsTime(*self.timeserver.getTime().timetuple()[0:5])
        else:
            utc = AbsTime(Cui.CuiCrcEvalAbstime(
                Cui.gpc_info, Cui.CuiNoArea, "none", "fundamental.%now%"))
        self['now_utc'] = utc
        self['now_date_utc'] = AbsTime(AbsDate(utc))
        self['save_count'] = 0
        #Used by period selection form
        self['period_start'] = utc.month_floor().addmonths(-3)
        self['period_end'] = utc.month_ceil()
        print "WaveValuesTable::refresh:\n ", "\n  ".join(
              [str(self[f]) for f in ('now_utc','now_date_utc','save_count')])
    
def init_wave_values():
    global wave_values_table
    try:
        wave_values_table.refresh()
        return False
    except:
        wave_values_table = WaveValuesTable()
        return True

def get_now_utc(refresh=False):
    global wave_values_table
    if refresh:
        refresh_wave_values()
    return AbsTime(wave_values_table['now_utc'].v)
    
def get_now_date_utc(refresh=False):
    global wave_values_table
    if refresh:
        refresh_wave_values()
    return AbsTime(wave_values_table['now_date_utc'].v)
    
def update_save_count():
    global wave_values_table
    try:    v = int(wave_values_table['save_count'].v)
    except: v = 0
    wave_values_table['save_count'] = v + 1
        
# init_wave_client -------------------------------------------------------{{{2
        
class init_wave_client(Service):
    def work(self, token, *service_and_args):
        print "wave::init_wave_client(%s)" % token
        first_time = init_wave_values()
        if STANDALONE:
            actions = ['submitClient()']
        else:
            actions = (first_time and ['refreshClient()']) or []
            actions += [
                'model("carmensystems.mirador.modelserversubmit.setTrans")',
                'submitClientStateless()']
        if service_and_args:
            actions += [
                'model(%s)' % ",".join(['"%s"' % s for s in service_and_args])]
        actions += ['refreshClient()']
        print "--> %s" % ("\n    ".join(actions))
        return {'actions': ";".join(actions)}

class refresh_wave_values(Service):
    def work(self, token):
        print "wave::refresh_wave_values(%s)" % token
        init_wave_values()
        return {'actions': 'refreshClient()'}

class submit_trans(Service):
    def work(self, token):
        if STANDALONE:
            actions = ['submitClient()']
        else:
            actions = ['submitClientStateless()']
        print "wave::submit_trans --> %s" % "\n                 ".join(actions)
        return {'actions': ";".join(actions)}

class submit_opaq(Service):
    _tt = unicode("".join([chr(c) for c in range(128)]) + 128*'?')
    def work(self, token, label):
        if STANDALONE:
            actions = ['submitClient()']
        else:
            label = label.translate(submit_opaq._tt)
            actions = [
               'model("carmensystems.mirador.modelserversubmit.setLabel","%s")' % label,
               'submitClient()',
               'model("carmensystems.mirador.modelserversubmit.setTrans")',
               ]
        print "wave::submit_opaq --> %s" % "\n                ".join(actions)
        return {'actions': ";".join(actions)}

    
# register ---------------------------------------------------------------{{{2
def register():
    """Register the XML-RPC functions."""
    global __register_done
    try:
        __register_done
    except:
        __register_done = True
        from carmensystems.services.dispatcher import registerService as RS
        prefix = "carmensystems.mirador.tablemanager"
        RS(show_document, "%s.%s" % (prefix, "show_document"))
        RS(run_report, "%s.%s" % (prefix, "run_report"))


# private functions ======================================================{{{1

# is_symlink -------------------------------------------------------------{{{2
def is_symlink(file1, file2):
    """Return if file1 is symlink to file2"""
    try:
        # If file1 is already symlink, does it point to file2?
        return os.path.join(os.path.dirname(file1), os.readlink(file)) == file2
    except:
        # Not a symlink at all
        return False


# make_link --------------------------------------------------------------{{{2
def make_link(path):
    """Create a link to path in tmp_dir.  If file already exists, check if
    it points to correct location, otherwise create symlink."""
    basename = os.path.basename(path)
    tmp_target = os.path.join(tmp_dir, basename)
    if is_symlink(tmp_target, path):
        return basename
    elif os.path.lexists(tmp_target):
        os.unlink(tmp_target)
    os.symlink(path, tmp_target)
    return basename


# normalize --------------------------------------------------------------{{{2
def normalize(url, relpath, location):
    """Merge XML-RPC URL with relpath to create new URL to document."""
    # Throw away the /RPC2 part.
    # Keep first part of 'url' and merge with 'url_path' and 'relpath'
    scheme, netloc = urlparse.urlparse(url)[:2]
    if ':' in netloc:
        host, port = netloc.split(':')
        if host == 'localhost':
            # Can't send 'localhost' to client.
            # [acosta:08/096@21:10] Improvement?: What about multihomed hosts or multiple IF's?
            netloc = "%s:%s" % (socket.gethostbyname(socket.gethostname()), port)
    elif netloc == 'localhost':
        # See comment above.
        netloc = socket.gethostbyname(socket.gethostname())
    return urlparse.urlunsplit(
            (scheme, netloc, os.path.join(location, relpath), '', ''))


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    """Basic test."""
    print show_document('dummy', 'http://sulaco:9999/RPC2', 'data/doc/CrewInfo.pdf')


# Examples ==============================================================={{{1

# Server -----------------------------------------------------------------{{{2
## Add this code to the server part of the Wave implementation.

# import utils.wave as wave
# wave.register()


# Client -----------------------------------------------------------------{{{2
#<!-- Add this code to the XML views definition. -->

# <!-- Run a report and return actions (openURL) -->
# <action name="run_report" args="report,format,args"><![CDATA[
# context.action('model', 'run_report', '${connection.properties[modelserver.url, value]}', report, format, args)
# ]]></action>
# 
# <!-- Open document in web browser -->
# <action name="show_document" args="path"><![CDATA[
# context.action('model', 'show_document', '${connection.properties[modelserver.url, value]}', path)
# ]]></action>
# 
#   ...
# 
# <on-click>
#    ...
#    show_document("data/doc/CrewInfo.pdf");
#    ...
# </on-click>
# 
# - or -
# 
# <on-click>
#    ...
#    run_report("report_sources.hidden.CrewProfile", "PDF", "CREW=10353");
#    ...
# </on-click>

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

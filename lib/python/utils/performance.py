'''
Created on Nov 9, 2009

Some common performance monitoring utilities.

Profiling: ('profileme' annotation)
Some common profiling utilities. Import this module and annotate functions
with @profileme to profile them. Files are written to $CARMTMP/profiling
and labelled with function name, time taken in ms, timestamp and machine name
(in that order).
Change between pure (Python) profiler, hotspot (low overhead but inaccurate and buggy), 
or to just time the functions. This is done by changing the PROF variable towards
the end of the file.

Function timing: ('clockme' annotation)
In addition to profiling, timers are available. To time a function, annotate it with
@clockme. To time a block of code, several syntax variants are available (depending
on preference, they are functionally equivalent).
Timers measure both CPU time and real time.

Note: By setting the environment variable CARMUSR_PROFILE to something other than
the empty string, all 'clockme' annotations will be treated as 'profileme'. Note that this
variable has to be set BEFORE this module is loaded.

The timers can have a name, but if no name is specified, the Python file name and line
number will be the name of the timer.

1. Block style: ('timing' function)

for t in timing("My timer"):
  ...
  t.lap("Mellantid")
  ...
this code is outside of the timer

2. Stack style: ('T' object)

T.start("My timer")
...
T.start("Suboperation 1")
...
T.lap("Mellantid)
...
T.restart("Suboperation 2") # stop "Suboperation 1" and start "Suboperation 2"
...
T.stop() # stop "Suboperation 2"
...
T.stop() # Stop "My timer"

3. Raw style ('Timer' class)
t = Timer("My timer").start()
...
t.lap()
...
t.stop()

Logging: ('log' function) 
This function is a replacement for 'print' that prints to stdout but includes
a timestamp and a special sequence (below) to allow these printouts to be easily
extracted from logs.

The output functions in this file is formatted for easy extraction. Every function
timing is prefixed with '$$', both at start and end of function. Timestamped
printouts are prefixed with '@@' and timers are prefixed with '&&' (lap times
are prefixed with '&>'). 

@author: rickard
'''

import os, os.path, time

from RelTime import RelTime
from AbsTime import AbsTime
from AbsDate import AbsDate
def rt_repr(self): return "RelTime('" + str(self) + "')"
def at_repr(self): return "AbsTime('" + str(self) + "')"
def ad_repr(self): return "AbsDate('" + str(self) + "')"
RelTime.__repr__ = rt_repr # To make readable printouts
AbsTime.__repr__ = at_repr
AbsDate.__repr__ = ad_repr

__profiling = False
__cxxprofiling = False

def rawlog(prefix, str):
    "All output go through this function."
    print "%s %s: %s" % (prefix, time.ctime(), str)

def PROF_py(func, *args, **kwargs):
    "Standard 'profile' profiler"
    try:
        import cProfile as profile
    except ImportError:
        import profile
    global __profiling
    
    pth = os.path.expandvars("$CARMTMP/profiling/")
    if not os.path.exists(pth):
        os.makedirs(pth)
    ms = time.time() 
    c1 = time.clock() 
    basename = "%s.__PENDING__.%s.%s.prof" % (func.__name__, int(1000*ms), os.environ['HOST'])
    #tempfilename = pth + basename
    p = profile.Profile()
    rawlog("$$","Begin %s %s %s" % (func.__name__,args,kwargs))
    dp = False
    try:
        if not __profiling:
            dp = True
            __profiling = True
            return p.runcall(func, *args, **kwargs)
        else:
            return func(*args, **kwargs)
    finally:
        if dp:
            __profiling = False
            #p.close()
            ms = int((time.time() - ms) * 1000)
            c1 = int((time.clock() - c1) * 1000)
            newfilename = pth + basename.replace('__PENDING__', "%07d" % ms)
            #os.rename(tempfilename, newfilename)
            p.dump_stats(newfilename)
            rawlog("$$","End   %s : real= %d ms, cpu= %d ms ; %s" % (func.__name__, ms, c1, newfilename)) 
        
def PROF_google(func, *args, **kwargs):
    "Google CPU profile"
    try:
        import ctypes
    except:
        rawlog("$@","Cannot profile. ctypes is not available")
        return func(*args, **kwargs)
    
    global __cxxprofiling
    
    pth = os.path.expandvars("$CARMTMP/profiling/")
    if not os.path.exists(pth):
        os.makedirs(pth)
    ms = time.time() 
    c1 = time.clock() 
    basename = "%s.%s.%s.cpuprof" % (func.__name__, int(1000*ms), os.environ['HOST'])
    filename = os.path.join(pth, basename)
    rawlog("$$","Begin %s %s %s" % (func.__name__,args,kwargs))
    dp = False
    dll = None
    try:
        if not __cxxprofiling:
            try:
                dll = ctypes.CDLL(os.path.expandvars("$CARMUSR/lib/$ARCH/libprofiler.so"))
            except:
                rawlog("$@","Cannot profile. libprofiler is not available")
                dll = None
            
            if dll:
                if not dll.ProfilerStart(filename):
                    rawlog("$@","Warning: ProfilerStart failed")
                dp = True
                __cxxprofiling = True
        return func(*args, **kwargs)
    finally:
        if dp:
            dll.ProfilerStop()
            __cxxprofiling = False
            
            ms = int((time.time() - ms) * 1000)
            c1 = int((time.clock() - c1) * 1000)
            rawlog("$$","End   %s : real= %d ms, cpu= %d ms ; %s" % (func.__name__, ms, c1, filename)) 
        
        
def PROF_hotshot(func, *args, **kwargs):
    "'hotshot' profiler, faster but buggier"
    import hotshot
    global __profiling
    
    pth = os.path.expandvars("$CARMTMP/profiling/")
    if not os.path.exists(pth):
        os.makedirs(pth)
    ms = time.time() 
    c1 = time.clock() 
    basename = "%s.__PENDING__.%s.%s.profhs" % (func.__name__, int(1000*ms), os.environ['HOST'])
    tempfilename = pth + basename
    p = hotshot.Profile(tempfilename)
    rawlog("$$", "Begin %s %s %s" % (func.__name__, args, kwargs))
    dp = False
    try:
        if not __profiling:
            dp = True
            __profiling = True
            return p.runcall(func, *args, **kwargs)
        else:
            return func(*args, **kwargs)
    finally:
        if dp: __profiling = False
        p.close()
        ms = int((time.time() - ms) * 1000)
        c1 = int((time.clock() - c1) * 1000)
        newfilename = pth + basename.replace('__PENDING__', "%07d" % ms)
        os.rename(tempfilename, newfilename)
        rawlog("$$","End   %s : real= %d ms, cpu= %d ms ; %s" % (func.__name__, ms, c1, newfilename))
        
def PROF_none(func, *args, **kwargs):
    "No profiler, just timing"
    ms = time.time()
    c1 = time.clock() 
    rawlog("$$","Begin %s %s %s" % (func.__name__,args,kwargs))
    try:
        return func(*args, **kwargs)
    finally:
        ms = int((time.time() - ms) * 1000)
        c1 = int((time.clock() - c1) * 1000)
        rawlog("$$","End   %s : real= %d ms, cpu= %d ms" % (func.__name__, ms, c1))
        

def log(msg):
    rawlog("@@",msg)
    
def timing(name=''):
    "Use the syntax 'for timimg():' to time the specified block"
    if not name: name = -1
    t = Timer(name)
    yield t.start()
    t.stop()

class Timer(object):
    def __init__(self, name=''):
        self._prev = None
        if not name or name==-1 or name==-2 or name==-3:
            import inspect
            frame = inspect.currentframe()
            try:
                if name==-1: frame=frame.f_back
                elif name==-2: frame=frame.f_back.f_back
                elif name==-3: frame=frame.f_back.f_back.f_back
                t = inspect.getframeinfo(frame.f_back)
                name = "%s(%s:%d)" % (t[2], os.path.basename(t[0]), t[1])
            finally:
                del frame
        self.name = str(name)
        self.started = False
    
    def start(self):
        if self.started: return
        self.realt = time.time()
        self.cput = time.clock()
        self.started = True
        return self
        
    def lap(self, msg=''):
        if not self.started: return
        r = int(1000*(time.time() - self.realt))
        c = int(1000*(time.clock() - self.cput)) 
        rawlog("&>","%s: real= %d ms, cpu= %d ms: %s" % (self.name, r, c, msg))
        return self
    
    def stop(self):
        if not self.started: return
        r = int(1000*(time.time() - self.realt))
        c = int(1000*(time.clock() - self.cput)) 
        rawlog("&&","%s: real= %d ms, cpu= %d ms" % (self.name, r, c))
        self.started = False
        return self
    
class TimerStack(object):
    def __init__(self):
        self._timer = None
        
    def start(self, name=''):
        if not name: name = -1
        tim = Timer(name)
        if self._timer:
            tim._prev = self._timer
        self._timer = tim
        tim.start()
        
    def stop(self):
        if self._timer:
            self._timer.stop()
            self._timer = self._timer._prev 
    
    def restart(self, name=''):
        if not name: name = -2
        if self._timer:
            self.stop()
        self.start(name)
        
    def lap(self, msg=''):
        if self._timer:
            self._timer.lap(msg)
    
T = TimerStack()
# Here is where the profiler is set
PROF = PROF_py
    
def clockme(func):
    "Set this annotation to a function to time"
    def pfunc(*a, **kw):
        return PROF_none(func, *a, **kw)
    return pfunc

def profileme(func):
    "Set this annotation to a function to profile"
    def pfunc(*a, **kw):
        return PROF(func, *a, **kw)
    return pfunc

def profilenativecode(func):
    "Set this annotation to a function to profile"
    def pfunc(*a, **kw):
        return PROF_google(func, *a, **kw)
    return pfunc

if os.environ.get("CARMUSR_PROFILE"):
    if os.environ["CARMUSR_PROFILE"].lower() == "hotshot":
        PROF = PROF_hotshot
    elif os.environ["CARMUSR_PROFILE"].lower() == "google":
        PROF = PROF_google
    else:
        PROF = PROF_py
    clockme = profileme
    
    
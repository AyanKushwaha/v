

"""
Toolbox for profiling support (debugging etc).
"""

import hotshot
import hotshot.stats
from tempfile import mkstemp
import os
import sys
import time


def timeit(func):
    def wrapper(*a, **k):
        ttime = time.time()
        tclock = time.clock()
        result = func(*a, **k)
        tdiff = time.time() - ttime
        cdiff = time.clock() - tclock
        print ">>> timeit %s (time) %s (clock)" % (tdiff, cdiff)
        return result
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__dict__ = func.__dict__
    return wrapper


def profileit(profiler=hotshot, filename=None, restrictions=()):
    """
    'profiler'   is the profiler module to use.
    'filename'   is an optional file with profile data.
    'restrictions' (hotspot only) print stats that matches (see manual).
    """
    def decorator(func):
        def wrapper(*args, **kargs):
            if profiler == hotshot:
                if filename is None:
                    try:
                        tmpdir = os.environ['CARMTMP']
                    except:
                        tmpdir = '/tmp'
                    fd, fn = mkstemp(dir=tmpdir, prefix='prof_', suffix='.tmp')
                    print >>sys.stderr, ">>> profileit - Using temporary file '%s'." % fn
                else:
                    fn = filename
                prof = profiler.Profile(fn)
                rc = prof.runcall(func, *args, **kargs)
                prof.close()
                stats = profiler.stats.load(fn)
                stats.strip_dirs()
                stats.sort_stats('time', 'calls')
                print ">>> profileit begin stats"
                stats.print_stats(*restrictions)
                print ">>> profileit end stats"
                return rc
            else:
                prof = profiler.Profile()
                rc = prof.runcall(func, *args, **kargs)
                if filename is not None:
                    prof.dump_stats(filename)
                prof.print_stats()
                return rc
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__dict__ = func.__dict__
        return wrapper
    return decorator


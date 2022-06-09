import adhoc.fixrunner as fixrunner
import adhoc.migrate_table as migrate_table
import AbsTime
import RelTime

__version__ = '2016_09_07'



def print_hello():
    print "Hello.  This is an empty script. "


# TODO: uncomment the tag bellow to ensure only run once!
#@fixrunner.once

@fixrunner.run

def fixit(dc, *a, **k):
    ops = []
    print_hello()
    return ops


fixit.program = 'skcms_1176.py (%s)' % __version__

if __name__ == '__main__':
    fixit()

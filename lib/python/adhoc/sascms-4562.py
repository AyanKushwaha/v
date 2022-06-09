import sys, os, re
from AbsTime import AbsTime
from datetime import datetime
import adhoc.fixrunner as fixrunner


__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    p = re.compile(r"(\w)\w+\((\w+)\)\[[\{\}\]\(]*(\{.+?\})")
    m = None
    entry = None
    ops = []
    fname = k['filename']
    try:
        f = open(fname, 'r')
    except:
        print "File %s not found!" % fname
        return
    for line in f.readlines():
        m = p.match(line)
        if m:
            #print m.group(2), m.group(1), m.group(3)
            entry = eval(m.group(3))
            ops.append(fixrunner.createop(m.group(2), m.group(1), entry))
    f.close()
    return ops
    
fixit.program = 'sascms-4562.py (%s)' % __version__

if __name__ == '__main__':
    fixit(filename=sys.argv[2])

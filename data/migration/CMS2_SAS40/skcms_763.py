import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2016_09_21_b'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):

    ops = []

    # Updating nop crew positions
    ops.append( fixrunner.createOp("nop_crew_position_set", "W", { "id":      "Mechanic",
                                                                   "cockpit": False,
                                                                   "si":      "" }))

    ops.append( fixrunner.createOp("nop_crew_position_set", "W", { "id":      "Security officer",
                                                                   "cockpit": True,
                                                                   "si":      "" }))
    return ops

fixit.program = 'skcms_763.py (%s)' % __version__

if __name__ == '__main__':
    try:
        fixit()
    except fixrunner.OnceException:
        print "    - migration already run with key ",__version__

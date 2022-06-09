import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = '2016-11-04.0'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):

    contracts = ["F00555", "F00556", "F00557", "F00558", "F00559", "F00560"]
    ops = []

    for contract in contracts:
        ops.append(fixrunner.createOp('crew_contract_set', 'U', {
            "id": contract,
            "dutypercent": 59,
        }))

    print "done"
    return ops


fixit.program = 'skcms_1060.py (%s)' % __version__

if __name__ == '__main__':
    try:
        fixit()
    except fixrunner.OnceException:
        print "    - migration already run with key ",__version__


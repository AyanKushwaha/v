

import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = '2014-12_02_'

timestart = int(AbsTime.AbsTime('01JAN1986'))/60/24
timeend =   int(AbsTime.AbsTime('31DEC2036'))/60/24

OCCRMS = ['OCCRM4','OCCRM5','OCCRM6']
CRMS =   ['CR4','CR5','CR6']

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('crew_recurrent_set', 'N', {
        'typ':              'OCCRM',
        'validfrom':        timestart,
        'validto':          timeend,
        'maincat':          'F',
        'acquals':          '',
        'aoc_sk':           'Y',
        'aoc_bu':           'Y',
        'validity':         12,
        'season1_start':    0,
        'season2_start':    0,
        'assignment_ival':  3,
        'si':               ''
    }))

    for row in fixrunner.dbsearch(dc,'activity_set'):
        if row['id'] in OCCRMS:
            row['recurrent_typ'] = 'OCCRM'
        elif row['id'] in CRMS:
            row['recurrent_typ'] = 'CRM'
        else:
            row['recurrent_typ'] = ''

        ops.append(fixrunner.createOp('activity_set','U', row))

    print "done"
    return ops


fixit.program = 'skcms_393.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



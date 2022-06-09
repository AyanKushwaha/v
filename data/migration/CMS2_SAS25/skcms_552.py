

import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = '2015-04_16_'

timestart = int(AbsTime.AbsTime('01JAN1986'))/24/60
timeend =   int(AbsTime.AbsTime('31DEC2035'))/24/60

DIC = {
    'F,STO' : 'SKS_FD_AG',
    'C,STO' : 'SKS_CC_AG',
    'F,CPH' : 'SKD_FD_AG',
    'C,CPH' : 'SKD_CC_AG',
    'F,OSL' : 'SKN_FD_AG',
    'F,SVG' : 'SKN_FD_AG',
    'F,TRD' : 'SKN_FD_AG',
    'C,OSL' : 'SKN_CC_AG',
    'C,SVG' : 'SKN_CC_AG',
    'C,TRD' : 'SKN_CC_AG',
    'C,BJS' : 'SKK_CC_AG',
    'C,SHA' : 'SKK_CC_AG',
    'C,NRT' : 'SKJ_CC_AG'
}

RETIRED_AG = "RETIRED_AG"

def addRow(ops, id, desc):
    ops.append(fixrunner.createOp('agmt_group_set', 'N', {
        'id': id,
        'validfrom': timestart,
        'validto': timeend,
        'si': desc
    }))

def ag(comp,maincat,base):
    if comp=='QA':
        if maincat=='F':
            return 'QA_FD_AG'
        elif maincat=='C':
            return 'QA_CC_AG'
    elif not maincat is None and not base is None:
        k = maincat+','+base
        if k in DIC:
            return DIC[k]
    return ''



@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    for row in fixrunner.dbsearch(dc,'agmt_group_set'):
        ops.append(fixrunner.createOp('agmt_group_set','D', row))

    addRow(ops,'SKS_FD_AG','Flightdeck SH SAS SE')
    addRow(ops,'SKS_CC_AG','Cabin Crew SAS SE')
    addRow(ops,'SKD_FD_AG','Flightdeck SH SAS DK')
    addRow(ops,'SKD_CC_AG','Cabin Crew SAS DK')
    addRow(ops,'SKN_FD_AG','Flightdeck SH SAS NO')
    addRow(ops,'SKN_CC_AG','Cabin Crew SAS NO')
    addRow(ops,'SKI_FD_AG','Flightdeck LH SAS')
    addRow(ops,'SKK_CC_AG','Cabin Crew SAS CN')
    addRow(ops,'SKJ_CC_AG','Cabin Crew SAS JP')
    addRow(ops,'QA_FD_AG','Flightdeck Cimber')
    addRow(ops,'QA_CC_AG','Cabin Crew Cimber')
    addRow(ops,RETIRED_AG,'Retired')


    grps = {}
    for row in fixrunner.dbsearch(dc,'crew_contract_valid'):
        res = ag(row['company'], row['maincat'],row['base'])
        if len(res)>0:
            grps[row['contract']] = res
    for row in fixrunner.dbsearch(dc,'crew_contract_set'):
        if row['id'] in grps:
            row['agmtgroup'] = grps[row['id']]
        else:
            row['agmtgroup'] = RETIRED_AG
        ops.append(fixrunner.createOp('crew_contract_set','U', row))

    print "done"
    return ops


fixit.program = 'skcms_552.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



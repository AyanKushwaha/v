
import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = '2015-04_28_'


def addRow(ops, id, desc):
    ops.append(fixrunner.createOp('agmt_group_set', 'N', {
        'id': id,
        'validfrom': timestart,
        'validto': timeend,
        'si': desc
    }))




@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    for row in fixrunner.dbsearch(dc,'dave_entity_select', "(selection='period' and entity='crew_log_acc_mod' and tgt_entity='crew_log_acc_mod')"):
        #print row
        row[ 'wtempl']= '$.tim>=%:3 - 1051200 and $.tim<=%:4'
        ops.append(fixrunner.createOp('dave_entity_select','U', row))

#    ops.append(fixrunner.createOp('crew_log_acc_set', 'N', {
#        'acc_type': "oagblkhrs",
#        'is_reltime':True,
#        'si': "Block Time Other Airlines"
#    }))
    print "done"
    return ops


fixit.program = 'skcms_598.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



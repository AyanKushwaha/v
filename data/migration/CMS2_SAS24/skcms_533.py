import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2015_03_31_'

timestart = int(AbsTime('01JAN1986 00:00'))
timeend = int(AbsTime('31DEC2035 00:00'))
cutoff = int(AbsTime('01MAY2015 00:00'))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    for cnj in fixrunner.dbsearch(dc, 'crew_need_jarops'):
        if cnj['acfamily'] == 'A330' or cnj['acfamily'] == 'A340':
            ops.append(fixrunner.createOp('crew_need_jarops_period', 'N', {
                            'acfamily' : cnj['acfamily'],
                            'actype' : cnj['actype'],
                            'validfrom' : timestart,
                            'validto': cutoff,
                            'pos1' : cnj['pos1'],
                            'pos2' : cnj['pos2'],
                            'pos3' : cnj['pos3'],
                            'pos4' : cnj['pos4'],
                            'pos5' : cnj['pos5'],
                            'pos6' : cnj['pos6'],
                            'pos7' : cnj['pos7'],
                            'pos8' : cnj['pos8'],
                            'pos9' : cnj['pos9'],
                            'pos10' : cnj['pos10']
                        }))
            ops.append(fixrunner.createOp('crew_need_jarops_period', 'N', {
                            'acfamily' : cnj['acfamily'],
                            'actype' : cnj['actype'],
                            'validfrom' : cutoff,
                            'validto': timeend,
                            'pos1' : cnj['pos1'],
                            'pos2' : cnj['pos2'],
                            'pos3' : cnj['pos3'],
                            'pos4' : cnj['pos4'],
                            'pos5' : cnj['pos5'],
                            'pos6' : 2,
                            'pos7' : 3,
                            'pos8' : cnj['pos8'],
                            'pos9' : cnj['pos9'],
                            'pos10' : cnj['pos10']
                        }))
        else:
            ops.append(fixrunner.createOp('crew_need_jarops_period', 'N', {
                            'acfamily' : cnj['acfamily'],
                            'actype' : cnj['actype'],
                            'validfrom' : timestart,
                            'validto': timeend,
                            'pos1' : cnj['pos1'],
                            'pos2' : cnj['pos2'],
                            'pos3' : cnj['pos3'],
                            'pos4' : cnj['pos4'],
                            'pos5' : cnj['pos5'],
                            'pos6' : cnj['pos6'],
                            'pos7' : cnj['pos7'],
                            'pos8' : cnj['pos8'],
                            'pos9' : cnj['pos9'],
                            'pos10' : cnj['pos10']
                        }))
    #end for
    
    ops.append(fixrunner.createOp('cms_view_objects', 'N', {
                        'cms_view' : 'upd_superuser',
                        'cms_object_type' : 'TABLE',
                        'cms_object_name' : 'crew_need_jarops_period'
                    }))
    ops.append(fixrunner.createOp('cms_view_objects', 'N', {
                        'cms_view' : 'read_all',
                        'cms_object_type' : 'TABLE',
                        'cms_object_name' : 'crew_need_jarops_period'
                    }))

    print "done"
    return ops


fixit.program = 'skcms_533.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



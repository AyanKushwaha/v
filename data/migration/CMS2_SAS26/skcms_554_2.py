import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = '2015_06_03_a'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    #New trip areas fo
    for row in fixrunner.dbsearch(dc,'dave_selparam'):
        if row['selection'] == 'crew_user_filter_cct':
            if row['pind'] == 3:
                row['name'] = 'rank_planning_group_1'
                row['lbl'] = 'Rank+planning group 1'
                ops.append(fixrunner.createOp('dave_selparam','U',row))
            elif row['pind'] == 4:
                row['name'] = 'rank_planning_group_2'
                row['lbl'] = 'Rank+planning group 2'
                ops.append(fixrunner.createOp('dave_selparam','U',row))
        elif row['selection'] == 'crew_user_filter_employment':
            if row['pind'] == 3:
                row['name'] = 'rank_planning_group'
                row['lbl'] = 'Rank+planning group'
                ops.append(fixrunner.createOp('dave_selparam','U',row))
        elif row['selection'] == 'trip_area_planning':
            if row['pind'] == 1:
                row['name'] = 'area_planning_group'
                row['lbl'] = 'Trip area planning group'
                ops.append(fixrunner.createOp('dave_selparam','U',row))
            elif row['pind'] == 2:
                row['lbl'] = 'Trip area planning group with qual'
                ops.append(fixrunner.createOp('dave_selparam','U',row))
                
    print "done"
    return ops


fixit.program = 'skcms_554_2.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



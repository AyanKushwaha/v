import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
__version__ = '2021_12_20_a'


valid_from = int(AbsTime("01Jan2022"))
valid_to= int(AbsTime("31Jan2022"))


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    for row in fixrunner.dbsearch(dc,'agreement_validity',"id='web_training_pc_22'"):
        ops.append(fixrunner.createop('agreement_validity','D',row))
        agr_valid_from = int(AbsTime("01Jan2022")) / 24 / 60
        agr_valid_to = int(AbsTime("31Dec2035")) / 24 / 60
        ops.append(
            fixrunner.createOp(
                "agreement_validity",
                "N",
                {
                    "id": "web_training_pc_22",
                    "validfrom": agr_valid_from,
                    "validto": agr_valid_to,
                    "si": "New name standard for web training at PC, SKCMS-2751",
                },
            )
        )
    for row in fixrunner.dbsearch(dc,'crew_activity',"st>=%s and (activity='WTA11' or activity='WTB11')"% (valid_from)):
        ops.append(fixrunner.createop('crew_activity','D',row))
        ops.append(fixrunner.createOp('crew_activity', 'N',
                                        {'st': row['st'],
                                        'crew': row['crew'],
                                        'activity': 'WT11',
                                        'et': row['et'],
                                        'adep': row['adep'],
                                        'ades': row['ades'],
                                        'statcode': row['statcode'],
                                        'trip_udor': row['trip_udor'],
                                        'trip_id': row['trip_id'],
                                        'locktype': row['locktype'],
                                        'si': row['si'],
                                        'urmtrail': row['urmtrail'],
                                        'annotation': row['annotation'],
                                        'personaltrip': row['personaltrip'],
                                        'bookref': row['bookref'],
                                        'est': row['est'],
                                        'eet': row['eet'],
                                        'ast': row['ast'],
                                        'aet': row['aet'],
                                        }))
    for row in fixrunner.dbsearch(dc,'ground_task',"st>=%s and (activity='WTA11' or activity='WTB11')"% (valid_from)):
        ops.append(fixrunner.createOp('ground_task', 'D', row))
        ops.append(fixrunner.createOp('ground_task', 'N',
                                        {'udor': row['udor'],
                                        'id': row['id'],
                                        'st': row['st'],
                                        'et': row['et'],
                                        'adep': row['adep'],
                                        'ades': row['ades'],
                                        'statcode': row['statcode'],
                                        'activity': 'WT11',
                                        'si': row['si'],
                                        'est': row['est'],
                                        'eet': row['eet'],
                                        'ast': row['ast'],
                                        'aet': row['aet'],
                                        'cancellock': row['cancellock'],
                                        'delaylock': row['delaylock'],
                                        }))
    for row in fixrunner.dbsearch(dc,'crew_training_log',"tim>=%s and code='WTB11'"% (valid_from)):
        ops.append(fixrunner.createOp('crew_training_log', 'D', row))
        ops.append(fixrunner.createOp('crew_training_log', 'N',
                                        {'code': 'W11B3',
                                        'attr': row['attr'],
                                        'crew': row['crew'],
                                        'tim': row['tim'],
                                        'typ': row['typ'],
                                        }))
    for row in fixrunner.dbsearch(dc,'crew_training_log',"tim>=%s and code='WTA11'"% (valid_from)):
        crew_quals = []
        for  trow in fixrunner.dbsearch(dc,'crew_qual_acqual',"crew=%s"%(row['crew'])):
            if trow['validto'] >= valid_from:
                if trow['qual_subtype'] == 'A2' or trow['qual_subtype'] == 'A3' or trow['qual_subtype'] == 'A5':
                    if trow['qual_subtype'] not in crew_quals:
                        crew_quals.append(trow['qual_subtype'])
        new_code=''
        if 'A5' in crew_quals and 'A3' in crew_quals:
            new_code = 'W11LH'
        elif 'A5' in crew_quals and 'A2' in crew_quals:
            new_code = 'W11M5'
        elif 'A3' in crew_quals and 'A2' in crew_quals:
            new_code = 'W11M3'
        elif 'A5' in crew_quals:
            new_code = 'W11A5'
        elif 'A3' in crew_quals:
            new_code = 'W11A3'
        else:
            new_code = 'W11A2'
        ops.append(fixrunner.createOp('crew_training_log', 'D', row))
        ops.append(fixrunner.createOp('crew_training_log', 'N',
                                        {'code': new_code,
                                        'attr': row['attr'],
                                        'crew': row['crew'],
                                        'tim': row['tim'],
                                        'typ': row['typ'],
                                        }))

    print "done"
    return ops


fixit.program = 'skcms_2851_118.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



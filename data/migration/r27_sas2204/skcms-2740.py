import adhoc.fixrunner as fixrunner


__version__ = '2022_04_1_a'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_activity', 'where_condition':'$.st<=%:11*1440 and $.et>=%:10*1440'}))
    print ("done")
    return ops


fixit.program = 'skcms_2740_1.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



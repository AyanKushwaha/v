import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    validfrom = int(AbsTime('01Jan2013'))
    validto = int(AbsTime('31Dec2035'))
    ops = []

    if len(fixrunner.dbsearch(dc, 'salary_article', "extsys='DK' and extartid='9419' and validfrom=%i"%validfrom)) == 0:
        ops.append(fixrunner.createOp('salary_article', 'N', {'extsys':'DK',
                                                              'extartid':'9419',
                                                              'validfrom':validfrom,
                                                              'validto':validto,
                                                              'intartid':'BOUGHT_8_CC',
                                                              'note':'Bought day (<= 6 hours) CC'}))
    else:
        print "DK, 9419, %s already exist. Updating instead."%AbsTime(validfrom)
        ops.append(fixrunner.createOp('salary_article', 'U', {'extsys':'DK',
                                                              'extartid':'9419',
                                                              'validfrom':validfrom,
                                                              'validto':validto,
                                                              'intartid':'BOUGHT_8_CC',
                                                              'note':'Bought day (<= 6 hours) CC'}))

    if len(fixrunner.dbsearch(dc, 'salary_article', "extsys='DK' and extartid='9495' and validfrom=%i"%validfrom)) == 0:
        ops.append(fixrunner.createOp('salary_article', 'N', {'extsys':'DK',
                                                              'extartid':'9495',
                                                              'validfrom':validfrom,
                                                              'validto':validto,
                                                              'intartid':'BOUGHT_8_FC',
                                                              'note':'Bought day (<= 6 hours) FC'}))
    else:
        print "DK, 9495, %s already exist. Updating instead."%AbsTime(validfrom)
        ops.append(fixrunner.createOp('salary_article', 'U', {'extsys':'DK',
                                                              'extartid':'9495',
                                                              'validfrom':validfrom,
                                                              'validto':validto,
                                                              'intartid':'BOUGHT_8_FC',
                                                              'note':'Bought day (<= 6 hours) FC'}))

    if len(fixrunner.dbsearch(dc, 'salary_article', "extsys='NO' and extartid='4564' and validfrom=%i"%validfrom)) == 0:
        ops.append(fixrunner.createOp('salary_article', 'N', {'extsys':'NO',
                                                              'extartid':'4564',
                                                              'validfrom':validfrom,
                                                              'validto':validto,
                                                              'intartid':'BOUGHT_8_CC',
                                                              'note':'Bought day (<= 6 hours) CC'}))
    else:
        print "NO, 4565, %s already exist. Updating instead."%AbsTime(validfrom)
        ops.append(fixrunner.createOp('salary_article', 'U', {'extsys':'NO',
                                                              'extartid':'4564',
                                                              'validfrom':validfrom,
                                                              'validto':validto,
                                                              'intartid':'BOUGHT_8_CC',
                                                              'note':'Bought day (<= 6 hours) CC'}))

    if len(fixrunner.dbsearch(dc, 'salary_article', "extsys='NO' and extartid='4525' and validfrom=%i"%validfrom)) == 0:
        ops.append(fixrunner.createOp('salary_article', 'N', {'extsys':'NO',
                                                              'extartid':'4525',
                                                              'validfrom':validfrom,
                                                              'validto':validto,
                                                              'intartid':'BOUGHT_8_FC',
                                                              'note':'Bought day (<= 6 hours) FC'}))
    else:
        print "NO, 4525, %s already exist"%AbsTime(validfrom)
        ops.append(fixrunner.createOp('salary_article', 'U', {'extsys':'NO',
                                                              'extartid':'4525',
                                                              'validfrom':validfrom,
                                                              'validto':validto,
                                                              'intartid':'BOUGHT_8_FC',
                                                              'note':'Bought day (<= 6 hours) FC'}))

    return ops

fixit.program = 'sascms-5529.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from carmensystems.basics.uuid import uuid

__version__ = '2022_03_1_a'


valid_from = int(AbsTime("01Jan2022"))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    for row in fixrunner.dbsearch(dc,'account_entry',"tim>=%s and (account='F0' or account='F36') and reasoncode!='OUT Roster'"% (valid_from)):
        ops.append(fixrunner.createOp('account_entry', 'U',
                                        {'id': row['id'],
                                        'crew': row['crew'],
                                        'tim': row['tim'],
                                        'account': row['account'],
                                        'source': row['source'],
                                        'amount': 0,
                                        'man': row['man'],
                                        'si': 'SKCMS-2738-Decommission F0 and F36 calc from CMS',
                                        'published': row['published'],
                                        'rate': row['rate'],
                                        'reasoncode': row['reasoncode'],
                                        'entrytime': row['entrytime'],
                                        'username': row['username'],
                                        }))
    crew = set()
    for row in fixrunner.dbsearch(dc,'account_entry',"tim<%s and account='F0'"% (valid_from)):
        crew.add(row['crew'])
    for tmpcrew in crew:
        balance = 0
        for accrow in fixrunner.dbsearch(dc, 'account_entry', ''.join((
            "tim<%s" % (valid_from),
            " and account='F0'",
            " and crew=%s" % (tmpcrew),
        ))):
            balance += accrow['amount']
        if balance < 0:
            ops.append(fixrunner.createOp('account_entry', 'N', {'id': uuid.makeUUID64(),
                                                             'crew': tmpcrew,
                                                             'tim': valid_from,
                                                             'account': 'F0',
                                                             'source': 'IN Correction',
                                                             'amount': int(-balance),
                                                             'man': False,
                                                             'si': 'SKCMS-2738: Correcting negative balance from 2021',
                                                             'published': True,
                                                             'rate': 100,
                                                             'reasoncode': 'IN Correction',
                                                             'entrytime': valid_from,
                                                             'username': 'hiq'}))


    print ("done")
    return ops


fixit.program = 'skcms_2738_105.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



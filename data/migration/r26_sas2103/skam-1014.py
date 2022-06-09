"""

Script to add deleted F3 entries

"""

import adhoc.fixrunner as fixrunner
from carmensystems.basics.uuid import uuid
from AbsTime import AbsTime
import csv
__version__ = '2021-02-22b'

def format_time(date):
    return int(AbsTime(date.replace('-', '')))


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()
    entrylist = []
    with open('./skam-1014.csv') as csvFile:
        data = csv.reader(csvFile, delimiter=',')
        for row in data:
            entrylist.append(dict(
                {'crew' : row[0], 'tim' : row[1], 'account' : row[2], 'source' : row[3], 'amount' : row[4], 'man' : row[5],
                 'si' : row[6], 'published' : row[7], 'rate' : row[8], 'reasoncode' : row[9], 'entrytime' : row[10], 'username' : row[11] }))

    for entry in entrylist:
        ops.append(fixrunner.createOp('account_entry', 'N', {'id': uuid.makeUUID64(),
                                                             'crew': entry['crew'],
                                                             'tim': format_time(entry['tim']),
                                                             'account': entry['account'],
                                                             'source': entry['source'],
                                                             'amount': int(entry['amount']),
                                                             'man': entry['man'],
                                                             'si': 'hiq_correction_20210226',
                                                             'published': entry['published'],
                                                             'rate': int(entry['rate']),
                                                             'reasoncode': entry['reasoncode'],
                                                             'entrytime': format_time(entry['entrytime']),
                                                             'username': entry['username']}))

    return ops


fixit.program = 'skam-1014.py (%s)' % __version__


if __name__ == '__main__':
    fixit()

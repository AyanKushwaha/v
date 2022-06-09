

"""
CR 435 - Calculation of Convertible Crew

* Add a new account 'F0_BUFFER' to 'account_entry'.
* Add a new attribute type 'CONVERTIBLE_OVERTIME' to 'crew_attr_set'.
* Add attributes to 'crew_attr' for crew in 'salary_convertable_crew'.
* Copy totals from 'salary_convertable_crew' to 'account_entry'.
"""

import datetime
import getpass
import fixrunner
from carmensystems.basics.uuid import uuid
from salary.reasoncodes import REASONCODES


__version__ = '$Revision$'


EPOCH = datetime.datetime(1986, 1, 1)


def to_dave_time(dt):
    """Return now as DAVE time."""
    timestamp = dt - EPOCH
    return timestamp.days * 1440 + timestamp.seconds / 60


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    now = to_dave_time(datetime.datetime.now())
    username = getpass.getuser()

    ops = [
        fixrunner.createOp('account_set', 'N', {
            'id': 'F0_BUFFER',
            'si': 'Remaining minutes for convertible crew',
        }),
        fixrunner.createOp('crew_attr_set', 'N', {
            'id': 'CONVERTIBLE_OVERTIME',   
            'category': 'Salary',
            'si': 'Crew is valid for convertible overtime (F0).',
        }),
    ]
    for rec in fixrunner.dbsearch(dc, 'salary_convertable_crew', 
            "deleted = 'N' and next_revid = 0"): 
        if rec['totaltime'] is not None and rec['totaltime'] != 0:
            ops.append(fixrunner.createop('account_entry', 'N', {
                'id': uuid.makeUUID64(),
                'crew': rec['crew'],
                'account': 'F0_BUFFER',
                'source': 'Migration for CR435',
                'amount': rec['totaltime'] * 100,
                'man': 'Y',
                'published': 'Y',
                'rate': 100 * (1, -1)[rec['totaltime'] < 0],
                'reasoncode': REASONCODES['IN_MAN'],
                'tim': now,
                'entrytime': now,
                'username': username,
            }))
        ops.append(fixrunner.createop('crew_attr', 'N', {
            'crew': rec['crew'],
            'attr': 'CONVERTIBLE_OVERTIME',
            'validfrom': rec['validfrom'] / 1440,
            'validto': rec['validto'] / 1440,
            'si': 'Migration for CR435',
        }))

    return ops


fixit.program = 'cr435.py (%s)' % __version__


if __name__ == '__main__':
    fixit()

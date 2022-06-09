#!/bin/env python


"""
CR 435 - Calculation of Convertible Crew

Migration of manually entered data.

Read data originating from Excel sheet and update 'salary_extra_data'
and accounts.
"""

import datetime
import getpass
import os
import adhoc.fixrunner as fixrunner
import salary.conf as conf
import utils.dt

from carmensystems.basics.uuid import uuid
from salary.reasoncodes import REASONCODES
from Etab import Etable
from AbsTime import AbsTime


__version__ = '$Revision$'
username = getpass.getuser()
source = 'cr435_03_migrate.py'
si = 'Converted (%s)'
corr_time = int(AbsTime(2010, 4, 1, 0, 0))


# This mapping has to be revised before the first run.
# The date should be the month for which the salary run was intended.
runs = {
    AbsTime(2009, 9, 1, 0, 0): 3725,
    AbsTime(2009, 10, 1, 0, 0): 3776,
    AbsTime(2009, 11, 1, 0, 0): 3814,
    AbsTime(2009, 12, 1, 0, 0): 3859,
    AbsTime(2010, 1, 1, 0, 0): 3904,
}


now = utils.dt.dt2m(datetime.datetime.now())


def add2account(crew, amount, account, ts, runid):
    """Return an 'account_entry' dictionary."""
    entrytime = now
    si = "Converted (%s)" % runid
    if account == 'F0':
        reasoncode = REASONCODES['IN_CONV']
    else:
        if amount < 0:
            reasoncode = REASONCODES['OUT_CONV']
        else:
            # Let the Convertible OT entry come before the conversion
            entrytime = now - 1
            si = "Convertible OT (%s)" % runid
            reasoncode = REASONCODES['IN_ADMIN']
    if amount is not None and amount != 0:
        return [{
            'id': uuid.makeUUID64(),
            'crew': crew,
            'account': account,
            'source': source,
            'amount': amount * 100,
            'rate': (100, -100)[amount < 0],
            'reasoncode': reasoncode,
            'man': 'Y',
            'published': 'Y',
            'tim': ts,
            'entrytime': entrytime,
            'username': username,
            'si': si,
        }]
    return []


def add2account_corr(crew, amount):
    """Return an 'account_entry' dictionary."""
    if amount is not None and amount != 0:
        return [{
            'id': uuid.makeUUID64(),
            'crew': crew,
            'account': 'F0',
            'source': source,
            'amount': amount * 100,
            'rate': (100, -100)[amount < 0],
            'reasoncode': REASONCODES['OUT_CORR'],
            'man': 'Y',
            'published': 'Y',
            'tim': corr_time,
            'entrytime': now,
            'username': username,
            'si': 'Nullify (migration CR435)',
        }]
    return []


def get_balances(dc):
    """Return mapping where the key is a crew id and the value is a list of
    'account_entry' dictionaries."""
    balances = {}
    for ae in fixrunner.dbsearch(dc, 'account_entry', "account = 'F0_BUFFER'"):
        balances.setdefault(ae['crew'], []).append(ae)
    for crew in balances:
        L = [(x['tim'], x) for x in balances[crew]]
        L.sort()
        balances[crew] = [x for (_, x) in L]
    return balances


def get_initdata(etable):
    """Read etable with "expected" data and return list of 'account_entry'
    mappings."""
    idata = []
    et = Etable(etable)
    for row in et:
        try:
            tim = int(AbsTime(row[et.getColumnPos('tim') - 1]))
        except:
            continue
        crewid = row[et.getColumnPos('crewid') - 1]
        amount = to_value(row[et.getColumnPos('convot') - 1])
        if amount:
            idata.append({
                'id': uuid.makeUUID64(),
                'crew': crewid,
                'account': 'F0_BUFFER',
                'source': source,
                'amount': amount * 100,
                'rate': (100, -100)[amount < 0],
                'reasoncode': REASONCODES['IN_ADMIN'],
                'man': 'Y',
                'published': 'Y',
                'tim': tim,
                'entrytime': now,
                'username': username,
                'si': 'Migrated (CR435)',
            })
    return idata


def get_salary_extra_data(etable):
    """Read etable with overtime data and return list of 'salary_extra_data'
    mappings."""
    ed = {}
    et = Etable(etable)
    for row in et:
        try:
            runmonth = row[et.getColumnPos('startdate') - 1]
            runid = runs[AbsTime(runmonth)]
        except:
            continue
        crewid = row[et.getColumnPos('crewid') - 1]
        amount = to_value(row[et.getColumnPos('convot') - 1])
        if amount:
            ed.setdefault(crewid, []).append({
                'intartid': 'X_CONVERTIBLE_OT',
                'runid': runid,
                'crewid': crewid,
                'amount': amount,
            })
    return ed


def get_starttime(dc, runid):
    """Return the 'starttime' value from a salary run id."""
    for row in fixrunner.dbsearch(dc, 'salary_run_id', "runid = '%s'" % runid):
        return row['starttime']
    raise ValueError("Could not get starttime for run with id (%s)." % runid)


def print_ops(ops):
    """DEBUG: print out id, (account,) and value."""
    for op in ops:
        if op.entity == 'salary_extra_data':
            print "%(crewid)s %(amount)6d" % op.values
        elif op.entity == 'account_entry':
            print "%(crew)s %(account)-10.10s %(amount)6d" % op.values
        else:
            raise ValueError('Internal Error, update of wrong table.')


def to_value(s):
    """Return integer value if 's' is an integer, else 0."""
    try:
        return int(s)
    except:
        return 0


#@fixrunner.once
@fixrunner.run
def fixit(dc, etable_changes, etable_initial, *a, **k):
    """Update 'account_entry' and 'salary_extra_data'."""
    ops = []
    account_ops = []

    # Mapping of new 'salary_extra_data' entries
    extradata = get_salary_extra_data(etable_changes)

    # Large mapping of crew -> account_entries for F0_BUFFER
    balances = get_balances(dc)

    # Update balances with initial values
    initdata = get_initdata(etable_initial)
    for idata in initdata:
        balances.setdefault(idata['crew'], []).append(idata)

    annul = {}
    for runid in sorted(runs.values()):
        z = get_starttime(dc, runid)
        for crew in extradata:
            for entry in extradata[crew]:
                if entry['runid'] == runid:
                    balance = sum([x['amount'] for x in balances.get(crew, []) if x['tim'] < z]) / 100
                    f0days, remain = divmod(entry['amount'] + balance, conf.convertible_time)
                    account_ops.extend(add2account(crew, f0days, 'F0', z, runid))
                    f0b = []
                    f0b.extend(add2account(crew, entry['amount'], 'F0_BUFFER', z, runid))
                    f0b.extend(add2account(crew, -conf.convertible_time * f0days, 'F0_BUFFER', z, runid))
                    if f0days:
                        annul[crew] = annul.get(crew, 0) - f0days
                    if f0b:
                        account_ops.extend(f0b)
                        balances.setdefault(crew, []).extend(f0b)

    for crew in annul:
        account_ops.extend(add2account_corr(crew, annul[crew]))

    for crew in extradata:
        for entry in extradata[crew]:
            ops.append(fixrunner.createop('salary_extra_data', 'N', entry))

    for a in initdata + account_ops:
        ops.append(fixrunner.createop('account_entry', 'N', a))

    for op in ops:
        if k.get('debug', False):
            print_ops(ops)
            return ops
    return ops


fixit.program = 'cr435_03_migrate.py (%s)' % __version__


if __name__ == '__main__':
    import __main__
    assert hasattr(__main__, 'runs'), "Update the value in the mapping 'xruns' and rename it to 'runs'."
    fixit()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

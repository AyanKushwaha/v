#!/bin/env python


"""
Small script that lists all runs for Overtime and DK.
"""

import adhoc.fixrunner as fixrunner
import utils.dt as dt


def fmt(e):
    e['starttime'] = dt.m2dt(e['starttime']).strftime("%Y-%m-%d %H:%M")
    for x in ('firstdate', 'lastdate'):
        e[x] = dt.d2dt(e[x]).strftime("%Y-%m-%d")
    e['note'] = e['note'] or ''
    return "%(runid)5.5s %(runtype)10.10s %(extsys)s %(admcode)s %(firstdate)s %(note)s" % e


@fixrunner.run
def fixit(dc, runtype, extsys, **k):
    entries = []
    for entry in fixrunner.dbsearch(dc, 'salary_run_id', ' AND '.join((
            "runtype = '%s'" % runtype,
            "extsys = '%s'" % extsys,
            ))):
        entries.append((entry['firstdate'], entry['runid'], entry))
    entries.sort()
    for _, _, entry in entries:
        print fmt(entry)
    return []


if __name__ == '__main__':
    fixit("OVERTIME", "DK")


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof



"""
Adhoc script used for locating account problems in connection with SASCMS-1800.
"""

import logging
import utils.mdor
utils.mdor.start(__name__)

import os
import salary.batch as batch

from tm import TM
from AbsTime import AbsTime
import utils.dave

from utils.davesupport import run as ds_run
from utils.davesupport import dbsearch


commit = False

# Got this from:
# select distinct revid
# from account_entry 
# where source = 'salary.compconv.Convert_F3_to_F3S and deleted = 'N' and next_revid = 0;
revid = 7866652
now = AbsTime("20100512")


class SimpleChangeDict(dict):
    def __init__(self, change):
        # a => attribute, o => original value, r => revised value
        dict.__init__(self, [(a, r) for (a, o, r) in change])

    def __getattr__(self, k):
        return self[k]


class AccountTuple(tuple):
    def __new__(cls, d):
        return tuple.__new__(cls, (d['crew'], d['account']))

    def __str__(self):
        return "%s\t%s\t%s" % (self[0], self[1], self.amount)

    @classmethod
    def from_entityi(cls, d):
        d['crew'] = d['crew'].str()
        d['account'] = d['account'].str()
        return cls(d)

    def __init__(self, d):
        self.amount = d['amount']


class ChangeVisitor(list):
    def visit(self, change):
        if change.getTableName() != 'account_entry':
            raise ValueError("batch job should only change account_entry")
        if change.getType() != change.ADDED:
            raise ValueError("batch job should not modified or remove records")
        scd = SimpleChangeDict(change)
        self.append(AccountTuple.from_entityi(scd))


class PrintVisitor:
    def __init__(self):
        self.f = open("/tmp/f3s.tmp", "w")

    def __del__(self):
        if self.f:
            self.f.close()

    def visit(self, change):
        if change.getTableName() != 'account_entry':
            raise ValueError("batch job should only change account_entry")
        if change.getType() != change.ADDED:
            raise ValueError("batch job should not modified or remove records")
        scd = SimpleChangeDict(change)
        print >>self.f, AccountTuple.from_entityi(scd)


class ChangeMonitor:
    def accept(self, visitor):
        for change in TM.difference(self.pre_ctx, self.post_ctx):
            visitor.visit(change)

    def pre(self):
        self.pre_ctx = TM.currentState()

    def post(self):
        self.post_ctx = TM.currentState()


def run_batch(conversion, rundate):
    cm = ChangeMonitor()
    cdm = batch.CompDaysMain(os.environ['DB_URL'], os.environ['DB_SCHEMA'])
    batch.log.setLevel(logging.DEBUG)
    cdm.commit = commit
    cdm.chgmon = cm
    cdm.run(conversion, rundate)
    cv = ChangeVisitor()
    cm.accept(cv)
    return cv


@ds_run(readonly=True)
def get_prev_job2(dc, revid):
    return [AccountTuple(d) for d in dbsearch(dc, 'account_entry', 'revid = %d' % revid)]


def run(revid, conversion, rundate, filename):
    crew = set()
    oldvals = {}
    for record in get_prev_job2(revid):
        crew.add(record[0])
        oldvals[record] = record.amount

    newvals = {}
    for record in run_batch(conversion, AbsTime(rundate)):
        crew.add(record[0])
        newvals[record] = record.amount

    added = []
    changed = []
    removed = []
    same = []
    for r in sorted(newvals):
        if r in oldvals:
            if newvals[r] != oldvals[r]:
                changed.append(r)
            else:
                same.append(r)
        else:
            added.append(r)
    for r in sorted(oldvals):
        if not r in newvals:
            removed.append(r)

    f = open(filename, "w")
    print >>f, '\t'.join(("CREWID", "EXTPERKEY", "BASE", "STATION", "QUAL",
        "CURR_F3", "CURR_F3S", "NEW_F3_CORR", "NEW_F3S_CORR", "RM_F3",
        "RM_F3S"))
    for crewid in sorted(crew):
        print >>f, '\t'.join((
            p_crew_info(crewid),
            p_f3x_info(oldvals, crewid),
            p_f3x_info(newvals, crewid),
            p_rm_info(newvals, oldvals, crewid)
        ))
    f.close()


def p_f3x_info(vals, crew):
    return "%s\t%s" % (vals.get((crew, 'F3'), "N/A"), 
            vals.get((crew, 'F3S'), "N/A"))


def p_rm_info(new, old, crew):
    def get_corr(account):
        if (crew, account) in old and (crew, account) not in new:
            return -old[(crew, account)]
        return "N/A"
    return "%s\t%s" % (get_corr("F3"), get_corr("F3S"))


def p_crew_info(crew):
    cref = TM.crew[crew,]
    extperkey = None
    base = None
    station = None
    quals = []
    TM('crew_employment', 'crew_qualification')
    for rec in cref.referers('crew_employment', 'crew'):
        if rec.validfrom <= now < rec.validto:
            extperkey = rec.extperkey
            base = rec.base.id
            station = rec.station
            break

    if extperkey is None:
        # not employed
        L = [(z.validto, z) for z in cref.referers('crew_employment', 'crew')]
        L.sort()
        for _, rec in L:
            extperkey = "*%s" % rec.extperkey
            base = "*%s" % rec.base.id
            station = "*%s" % rec.station
            break
            
    for rec in cref.referers('crew_qualification', 'crew'):
        if rec.qual.typ == 'ACQUAL' and rec.validfrom <= now < rec.validto:
            quals.append(rec.qual.subtype)
    quals.sort()
    return '\t'.join((crew, extperkey, base, station, ' '.join(quals)))


if __name__ == '__main__':
    run(revid, "F3S", "20100101", "f3s.csv")
    #run_batch("F3S", AbsTime("20091112"))


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

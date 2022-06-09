

"""
Interface 43.5 Vacation days

This module handles Vacation-related data.
See:
    43.5.1.1
    43.5.1.1.2
    43.5.2
    43.5.3
    43.5.4
"""

import salary.conf as conf
import salary.run as run
import salary.accounts as accounts

from AbsTime import AbsTime
from RelTime import RelTime
from salary.api import SalaryException, warn
from salary.reasoncodes import REASONCODES
from utils.TimeServerUtils import TimeServerUtils
from utils.rave import RaveIterator
import carmensystems.rave.api as r 
from tm import TM


# module variables ======================================================={{{1
va_remaining_accounts = ('VA', 'VA_SAVED1', 'VA_SAVED2', 'VA_SAVED3',
    'VA_SAVED4', 'VA_SAVED5')


# CrewSalarySystemDict ==================================================={{{1
class CrewSalarySystemDict(dict):
    """
    Mapping crew <-> crew_employment for crew that belongs to a given salary
    system.  The mapping can be limited to crew beloning to a certain crew
    category.

    {'crewid1': 'crew_employment1', 'crewid2': 'crew_employment2', ...}
    """
    def __init__(self, extsys, searchdate, cat=None):
        """The optional argument 'cat' will limit the mapping to only include
        crew that has the main category 'cat'."""
        dict.__init__(self)
        # there is no region called S3
        if extsys == 'S3':
            extsys = 'SE'
        # Locate homebase names, given a salary system id
        homebases = [x.region for x in TM.salary_region.search(
            '(&(extsys=%s)(validfrom<%s)(validto>=%s))' % (
                extsys, searchdate, searchdate))]
        excluded = {}
        
        searchdateTime = AbsTime(searchdate)
        for ec in TM.rave_paramset_set.find("salary_exclude_crew").referers("rave_string_paramset","ravevar"):
            if ec.validfrom >= searchdateTime or ec.validto < searchdateTime: continue
            excluded[ec.val] = True
        
        if extsys == 'SE':
            # Exclude SKS Resource Pool Crew
            crewIter = RaveIterator(RaveIterator.iter('iterators.roster_set',where='studio_select.%%is_resource_crew%%(%s, "%s")' % (searchdateTime, 'SKS')), {'id': 'crew.%id%'})
            rosters = crewIter.eval('sp_crew')

            for roster in rosters:
                excluded[roster.id] = True

        Q = ['(validfrom<=%s)' % (searchdate,), '(validto>%s)' % (searchdate,)]
        hl = len(homebases)
        if hl == 1:
            # One base (e.g. DK, SE) 
            Q.append('(base.id=%s)' % homebases[0])
        elif hl:
            # Several bases (NO)
            Q.append('(|%s)' % ''.join(['(base.id=%s)' % x for x in homebases]))

        # Fill the dict([(id1, perkey1), (id2, perkey2), ...])
        for ce in TM.crew_employment.search('(&%s)' % ''.join(Q)):
            try:
                if cat is None or ce.titlerank.maincat.id == cat:
                    id = ce.crew.id
                    if not ce.crewrank.id in conf.validVacationRanks:
                        print "skipping",id,ce.crewrank
                        continue
                    if id in excluded: continue
                    self[id] = ce
            except Exception, e:
                warn("Reference error in 'crew_employment': %s (%s)" % (ce, e))


# Performed VA ==========================================================={{{1

# PerformedVacBalanceDict ------------------------------------------------{{{2
class PerformedVacBalanceDict(dict):
    """ Compare with accounts.AccountBalanceDict. """
    def __init__(self, account, map, hi, lo=None):
        dict.__init__(self)
        for ae in accounts.AccountQuery(account=account, hi=hi, lo=lo):
            if ae.reasoncode == REASONCODES['OUT_ROSTER']:
                try:
                    crewid = ae.crew.id
                except Exception, e:
                    warn("Reference error in 'account_entry': %s (%s)" % (ae, e))
                    continue
                if crewid in self:
                    self[crewid] += ae.amount
                elif crewid in map:
                    self[crewid] = ae.amount


# PerformedVacRun --------------------------------------------------------{{{2
class PerformedVacRun(run.GenericRun):
    """
    Performed Vacation (sum of entries with reasoncode "Out Roster") within
    time interval.
    """
    def rosters(self):
        self.crew_map = CrewSalarySystemDict(self.rundata.extsys, self.rundata.lastdate)
        self.va_performed = PerformedVacBalanceDict('VA', self.crew_map,
                hi=self.rundata.lastdate, lo=self.rundata.firstdate)
        #[acosta:09/323@11:15] Put on hold.
        #self.va1_performed = PerformedVacBalanceDict('VA1', self.crew_map,
        #        hi=self.rundata.lastdate, lo=self.rundata.firstdate)
        #if len(self.va_performed) + len(self.va1_performed) == 0:
        #    raise SalaryException("No crew found with VA/VA1 within the search interval.")
        #return sorted(set(list(self.va_performed) + list(self.va1_performed)))
        if len(self.va_performed) == 0:
            raise SalaryException("No crew found with VA within the search interval.")
        return sorted(set(list(self.va_performed)))

    def save(self, id, type, value):
        self.data.append(id, self.crew_map[id].extperkey, self.articleCodes[type], value)

    def VA_PERFORMED(self, id):
        # [acosta:09/013@16:46] TDO: This value should probably be negated
        # before sending back.  Jep Buch at SAS will return with instructions.
        # [acosta:09/330@15:47] Negating this value according to SASCMS-744
        return -self.va_performed.get(id, 0)

    # [acosta:09/323@11:15] not activated
    #def VA1_PERFORMED(self, id):
    #    return self.va1_performed.get(id, 0)


# Remaining VA ==========================================================={{{1

# RemainingBalanceDict ---------------------------------------------------{{{2
class RemainingBalanceDict(dict):
    """
    Compare with acccounts.AccountBalanceDict.
   
    mapping: {'crewid1': 'balance1', 'crewid2': 'balance2', }
    where balance is sum at querydate from minus infinity.
    """
    def __init__(self, map, hi):
        dict.__init__(self)
        self.map = map
        for account in va_remaining_accounts:
            abd = accounts.AccountBalanceDict(account, hi, filter=self.filter)
            for crewid in abd:
                if crewid in self:
                    self[crewid] += abd[crewid]
                else:
                    self[crewid] = abd[crewid]

    def filter(self, crew_entry):
        """Callback. Only include crew members that are in the mapping."""
        return crew_entry.crew.id in self.map 


# RemainingVacRun --------------------------------------------------------{{{2
class RemainingVacRun(run.GenericRun):
    """ Remaining VA, balance at "lastdate". """
    def rosters(self):
        self.crew_map = CrewSalarySystemDict(self.rundata.extsys, self.rundata.lastdate)
        self.remaining = RemainingBalanceDict(self.crew_map, hi=self.rundata.lastdate)
        return self.remaining

    def save(self, id, type, value):
        self.data.append(id, self.crew_map[id].extperkey, self.articleCodes[type], value)

    def VA_REMAINING(self, id):
        return self.remaining[id]


# Vacation Year =========================================================={{{1

# VacYearMap -------------------------------------------------------------{{{2
class VacYearMap(dict):
    """Find VA year given crew_employment record."""

    default_date = AbsTime(1986, 1, 1, 0, 0)

    def __init__(self, querydate, account="VA"):
        self.default = self.moddate(self.default_date, querydate)
        leaveent = {('F', 'OSL', 'SK', '20100101'): AbsTime('01JAN2010 00:00'), ('C', 'CPH', 'SK', '20210901'): AbsTime('01SEP2021 00:00'), ('F', 'CPH', 'SK', '20100501'): AbsTime('01MAY2010 00:00'), ('C', 'OSL', 'BU', '20120101'): AbsTime('01JAN2012 00:00'), ('F', 'OSL', 'SK', '20110101'): AbsTime('01JAN2011 00:00'), ('C', 'SVG', 'BU', '19860101'): AbsTime('01JAN1986 00:00'), ('C', 'TRD', 'BU', '20120101'): AbsTime('01JAN2012 00:00'), ('C', 'OSL', 'BU', '20130101'): AbsTime('01JAN2013 00:00'), ('F', 'SVG', 'SK', '19860601'): AbsTime('01JUN1986 00:00'), ('F', 'OSL', 'BU', '20110101'): AbsTime('01JAN2011 00:00'), ('C', 'STO', 'SK', '20130601'): AbsTime('01JUN2013 00:00'), ('F', 'CPH', 'QA', '20160501'): AbsTime('01MAY2016 00:00'), ('C', 'TRD', 'BU', '20130101'): AbsTime('01JAN2013 00:00'), ('C', 'TRD', 'BU', '19860101'): AbsTime('01JAN1986 00:00'), ('F', 'OSL', 'BU', '20100101'): AbsTime('01JAN2010 00:00'), ('F', 'OSL', 'SK', '19860601'): AbsTime('01JUN1986 00:00'), ('C', 'CPH', 'SK', '20110501'): AbsTime('01MAY2011 00:00'), ('C', 'SVG', 'SK', '20130101'): AbsTime('01JAN2013 00:00'), ('F', 'SVG', 'BU', '20100101'): AbsTime('01JAN2010 00:00'), ('C', 'STO', 'BU', '19860601'): AbsTime('01JUN1986 00:00'), ('C', 'CPH', 'SK', '19860501'): AbsTime('01MAY1986 00:00'), ('F', 'TRD', 'BU', '20100101'): AbsTime('01JAN2010 00:00'), ('C', 'NRT', 'SK', '19860401'): AbsTime('01APR1986 00:00'), ('F', 'CPH', 'SK', '19860601'): AbsTime('01JUN1986 00:00'), ('C', 'SVG', 'BU', '20130101'): AbsTime('01JAN2013 00:00'), ('F', 'TRD', 'SK', '19860601'): AbsTime('01JUN1986 00:00'), ('F', 'STO', 'SK', '19860601'): AbsTime('01JUN1986 00:00'), ('F', 'CPH', 'SK', '20090501'): AbsTime('01MAY2009 00:00'), ('F', 'OSL', 'BU', '19860601'): AbsTime('01JUN1986 00:00'), ('C', 'TRD', 'SK', '19860101'): AbsTime('01JAN1986 00:00'), ('F', 'SVG', 'BU', '19860601'): AbsTime('01JUN1986 00:00'), ('F', 'STO', 'BU', '19860601'): AbsTime('01JUN1986 00:00'), ('F', 'TRD', 'BU', '19860601'): AbsTime('01JUN1986 00:00'), ('F', 'SVG', 'SK', '20100101'): AbsTime('01JAN2010 00:00'), ('F', 'CPH', 'SK', '20200501'): AbsTime('01MAY2020 00:00'), ('C', 'OSL', 'SK', '20120101'): AbsTime('01JAN2012 00:00'), ('C', 'OSL', 'SK', '19860101'): AbsTime('01JAN1986 00:00'), ('F', 'TRD', 'SK', '20100101'): AbsTime('01JAN2010 00:00'), ('C', 'CPH', 'SK', '20210501'): AbsTime('01MAY2021 00:00'), ('C', 'STO', 'SK', '19860601'): AbsTime('01JUN1986 00:00'), ('F', 'TRD', 'SK', '20110101'): AbsTime('01JAN2011 00:00'), ('F', 'TRD', 'BU', '20110101'): AbsTime('01JAN2011 00:00'), ('C', 'SVG', 'SK', '19860101'): AbsTime('01JAN1986 00:00'), ('F', 'SVG', 'BU', '20110101'): AbsTime('01JAN2011 00:00'), ('C', 'CPH', 'SK', '20200901'): AbsTime('01SEP2020 00:00'), ('F', 'CPH', 'SK', '20110501'): AbsTime('01MAY2011 00:00'), ('C', 'OSL', 'BU', '19860101'): AbsTime('01JAN1986 00:00'), ('F', 'CPH', 'SK', '20200901'): AbsTime('01SEP2020 00:00'), ('C', 'TRD', 'SK', '20130101'): AbsTime('01JAN2013 00:00'), ('C', 'CPH', 'QA', '20160501'): AbsTime('01MAY2016 00:00'), ('C', 'SVG', 'SK', '20120101'): AbsTime('01JAN2012 00:00'), ('F', 'CPH', 'SK', '20210501'): AbsTime('01MAY2021 00:00'), ('C', 'TRD', 'SK', '20120101'): AbsTime('01JAN2012 00:00'), ('C', 'BJS', 'SK', '19860101'): AbsTime('01JAN1986 00:00'), ('C', 'SVG', 'BU', '20120101'): AbsTime('01JAN2012 00:00'), ('C', 'CPH', 'SK', '20200501'): AbsTime('01MAY2020 00:00'), ('C', 'SHA', 'SK', '20130101'): AbsTime('01JAN2013 00:00'), ('F', 'CPH', 'SK', '20210901'): AbsTime('01SEP2021 00:00'), ('C', 'HKG', 'SK', '20160701'): AbsTime('01JUL2016 00:00'), ('C', 'OSL', 'SK', '20130101'): AbsTime('01JAN2013 00:00'), ('F', 'SVG', 'SK', '20110101'): AbsTime('01JAN2011 00:00')}
        m = {}
        for x in leaveent:
            key = (x[0], x[1], x[2])
            if leaveent[x] <= querydate:
                v = m.setdefault(key, leaveent[x])
                if v < leaveent[x]:
                    m[key] = leaveent[x]
 
        for k in m:
            self[k] = self.moddate(m[k], querydate)

    def moddate(self, date1, date2):
        y1, m1, d1 = date1.split()[:3]
        y2 = date2.split()[0]
        return AbsTime(y2, m1, d1, 0, 0)

    def vacation_year(self, ce):
        """Return vacation year given crew_employment record."""
        return self.get((ce.titlerank.maincat.id, ce.base.id, ce.company.id), self.default)

def employmentdate(extsys, lastdate):
    y,m,d,H,M = lastdate.split()
    d = 1
    if extsys in ("SE", "S3"):
        m = 6
    elif extsys == "DK":
        m = 5
    elif extsys == "NO":
        m = 1
    return AbsTime(y,m+1,d,H,M)

# RemainingVacYearRun ----------------------------------------------------{{{2
class RemainingVacYearRun(run.GenericRun):
    """ Remaining VA at start of Vacation Year. """
    cat = None
    def rosters(self):
        rdate = employmentdate(self.rundata.extsys, self.rundata.lastdate)
        self.crew_map = CrewSalarySystemDict(self.rundata.extsys, rdate.addmonths(-1), self.cat)
        self.remaining = {}
        for account in va_remaining_accounts:
            vym = VacYearMap(rdate.addmonths(12), account)
            acd = accounts.AccountDict(account, rdate, lo=rdate.addmonths(-12), filter=self.filter)
            for crewid in acd:
                ce = self.crew_map[crewid]
                vacyear = vym.vacation_year(ce)
                r = 0
                for e in acd[crewid]:
                    if e.tim < vacyear:
                        r += int(e)
                self.remaining[crewid] = self.remaining.get(crewid, 0) + r
        return self.remaining

    def filter(self, crew_entry):
        """Callback. Only include crew members that are in the mapping."""
        return crew_entry.crew.id in self.crew_map and crew_entry.reasoncode == REASONCODES['IN_ENTITLEMENT']

    def save(self, id, type, value):
        self.data.append(id, self.crew_map[id].extperkey, self.articleCodes[type], value)

    def VA_REMAINING_YR(self, id):
        return self.remaining[id]



# RemainingVacYearRunFD --------------------------------------------------{{{2
class RemainingVacYearRunFD(RemainingVacYearRun):
    cat = 'F'


# RemainingVacYearRunCC --------------------------------------------------{{{2
class RemainingVacYearRunCC(RemainingVacYearRun):
    cat = 'C'


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof

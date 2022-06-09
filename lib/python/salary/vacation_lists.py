

"""
44.6   Vacation lists STO
44.6.2 Vacation lists OSL

These reports are run at the beginning of each month, showing VA and VA1 for
crew the gone month.
"""

# imports ================================================================{{{1
import logging
import salary.api as api
import salary.conf as conf
import salary.run as run
import salary.fmt

from utils.rave import RaveIterator
from utils.time_util import IntervalSet, TimeInterval
from tm import TM
from AbsTime import AbsTime
from salary.rpt import EmailReport


# logging ================================================================{{{1
log = logging.getLogger('salary.vacation_lists')


# help classes ==========================================================={{{1

# VacationRecord ----------------------------------------------------------{{{2
class VacationRecord(run.SalaryRecord):
    """Vacation lists differs slightly since they use start and
    end dates."""
    def write(self, empno, extartid, start, end):
        self.runfiles.write(self.recordformatter.record(empno, extartid, start, end))


# VacationReport ---------------------------------------------------------{{{2
class VacationReport(EmailReport):
    def __init__(self, rundata):
        dict.__init__(self)
        self.rundata = rundata

    def add(self, extartid, interval):
        (count, sum) = self.get(extartid, (0, 0))
        count += 1
        # Times 100 to make EmailReport happy.
        sum += 100 * salary.fmt.utils.days(interval.first, interval.last)
        self[extartid] = (count, sum)


# vacation() ============================================================={{{1
def vacation(country, start=None, end=None):
    """ country is "NO" or "SE", start and end are of type AbsTime
    - SKCMS-1636: F22 activites should be added to vacation list for all (FC/CC) Norweigan crew"""

    if start is None or end is None:
        tt = api.Times()
        if start is None:
            start = tt.month_start
        if end is None:
            end = tt.month_end
    log.debug("vacation(%s, %s, %s)" % (country, start, end))

    if country == 'SE':
        crew_group = 'salary.%%salary_system%%(%s) = "SE" and crew.%%is_cabin%%' % start
    elif country == 'NO':
        crew_group = 'salary.%%salary_system%%(%s) = "NO" and crew.%%is_cabin%%' % start
        crew_group_f22 = 'salary.%%salary_system%%(%s) = "NO" and (crew.%%is_pilot%% or crew.%%is_cabin%%)' % start
    else:
        raise api.SalaryException('Country can only be one of ("NO", "SE")')

    rd = run.RunData(runtype='VACATION_P')
    rd.extsys = country
    rd.exportformat = "VACATION_FLAT"
    rd.runid = api.getNextRunId()

    exp = VacationRecord(run.RunFiles(rd))

    if country == 'SE':
        is_vacation = 'leg.%code% = "VA" or leg.%code% = "VA1"'
    if country == 'NO':
        is_vacation = 'leg.%code% = "VA" or leg.%code% = "VA1"'
        is_f22 = 'leg.%code% = "F22"'
    in_interval = 'leg.%%end_date%% >= %s and leg.%%start_hb%% < %s' % (start, end)

    ri = RaveIterator(
        RaveIterator.iter('iterators.roster_set', where=crew_group),
        {'empno': 'crew.%employee_number%', 'id': 'crew.%id%'}
    )
    li = RaveIterator(
        RaveIterator.iter('iterators.leg_set', where=(is_vacation, in_interval)),
        {
            'activity': 'leg.%code%',
            'start': 'leg.%start_hb%', 
            'end': 'leg.%end_hb%'
        }
    )
    ri.link(li)
    rosters = ri.eval(conf.context)

    #SKCMS-1636: Create rave iterator for norweigan crew and f22 activies
    if country == 'NO':
        ri_f22 = RaveIterator(
            RaveIterator.iter('iterators.roster_set', where=crew_group_f22),
            {'empno': 'crew.%employee_number%', 'id': 'crew.%id%', 'rank': 'crew.%rank%'}
        )
        li_f22 = RaveIterator(
            RaveIterator.iter('iterators.leg_set', where=(is_f22, in_interval)),
            {
                'activity': 'leg.%code%',
                'start': 'leg.%start_hb%',
                'end': 'leg.%end_hb%'
            }
        )
        ri_f22.link(li_f22)
        rosters_f22 = ri_f22.eval(conf.context)

    if country == 'SE':
        va_artid = api.getExternalArticleId(rd, "VA_PERFORMED")
        va1_artid = va_artid
    elif country == 'NO':
        va_artid = api.getExternalArticleId(rd, "VA_PERFORMED")
        va1_artid = api.getExternalArticleId(rd, "VA1_PERFORMED")
        f22cc_artid = api.getExternalArticleId(rd, "SOLD_CC")
        f22fc_artid = api.getExternalArticleId(rd, "SOLD_FC")

    # Afstemningsunderlag (see CR 475)
    au = VacationReport(rd)

    # Used to truncate entries so that they will not exceed start or end
    mask = IntervalSet([TimeInterval(start, end)])
    exp.write_pre()
    for crew in rosters:
        VA = IntervalSet()
        VA1 = IntervalSet()
        for leg in crew.chain():
            if leg.activity == 'VA':
                VA.add(TimeInterval(leg.start, leg.end))
            elif leg.activity == 'VA1':
                VA1.add(TimeInterval(leg.start, leg.end))
        for x in get_bought_days(crew.id, 'VA', start, end):
            VA.add(TimeInterval(x.start_time, x.end_time))
        for x in get_bought_days(crew.id, 'VA1', start, end):
            VA1.add(TimeInterval(x.start_time, x.end_time))
        # Merge periods
        VA.merge()
        VA1.merge()
        # Cut of time periods outside interval (start, end)
        VA &= mask
        VA1 &= mask
        for x in sorted(VA):
            exp.write(crew.empno, va_artid, x.first, x.last)
            au.add(va_artid, x)
        for x in sorted(VA1):
            exp.write(crew.empno, va1_artid, x.first, x.last)
            au.add(va1_artid, x)
    #Adding F22 activities to export material for Norweigan crew.
    if country == 'NO':
        for crew in rosters_f22:
            F22FC = IntervalSet()
            for leg in crew.chain():
                if leg.activity == 'F22':
                    F22FC.add(TimeInterval(leg.start, leg.end))
            for x in get_bought_days(crew.id, 'F22', start, end):
                F22FC.add(TimeInterval(x.start_time, x.end_time))
            # Merge periods
            F22FC.merge()
            # Cut of time periods outside interval (start, end)
            F22FC &= mask
            for x in sorted(F22FC):
                if "A" in crew.rank:
                    exp.write(crew.empno, f22cc_artid, x.first, x.last)
                    au.add(f22cc_artid, x)
                elif "F" in crew.rank:
                    exp.write(crew.empno, f22fc_artid, x.first, x.last)
                    au.add(f22fc_artid, x)
    exp.write_post()
    exp.close()

    log.info("vacation() - filename is '%s'" % (exp.runfiles.name))
    reports = [{
        'content-type': 'text/plain',
        'content-location': exp.runfiles.name,
        'destination': [("SALARY_EXPORT", {'subtype':'VAC_LISTS', 'rcpttype':rd.extsys})],
    }]
    if country == 'NO':
        # CR 475 - add 'Afstemningsunderlag' for SKN
        reports.append({
            'content-type': 'text/plain',
            'content': au.report(),
            'destination': [("BALANCING_REPORT", {'subtype':'VAC_LISTS', 'rcpttype':rd.extsys})],
        })
    return (reports, False)


# vacation_fn ------------------------------------------------------------{{{2
def vacation_fn(country, start=None, end=None):
    """For testing purposes, only return filename."""
    return vacation(country, start, end)[0][0]['content-location']


# vacation_rpt -----------------------------------------------------------{{{2
def vacation_rpt(country, start=None, end=None):
    """For testing purposes, only return the balancing report."""
    return vacation(country, start, end)[0][1]['content']


# get_bought_days --------------------------------------------------------{{{2
def get_bought_days(crewid, day_type, start_time, end_time):
    return TM.bought_days.search("(&(crew.id=%s)(day_type=%s)(start_time<%s)(end_time>%s))" % (
        crewid, day_type, end_time, start_time))


# main ==================================================================={{{1
if __name__ == '__main__':
    # Basic test
    from AbsTime import AbsTime
    start = "20090601"
    end = "20090701"
    se = vacation("SE", AbsTime(start), AbsTime(end))
    no = vacation("NO", AbsTime(start), AbsTime(end))
    print "Vacation STO: ", se
    print "Vacation OSL: ", no


# Output formats ========================================================={{{1
# For Vacation lists STO see rec/SE_VACATION_FLAT.py
# For Vacation lists OSL see rec/NO_VACATION_FLAT.py


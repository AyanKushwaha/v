#!/bin/env python

# [acosta:07/005@16:13] First version
# [acosta:07/166@14:12] Added options to start from within mirador
# [acosta:07/338@11:53] Fix for Bugzilla #21982 (depending on Bugzilla #14598).

"""
Vacation Trade Snapshot, interface X3
"""

script = 'replication.X3'

import utils.mdor
utils.mdor.start(__name__, script)

import sys
import logging
import time
import getopt
from copy import copy

from carmensystems.dig.jmq import jmq
from AbsTime import AbsTime
# Bugzilla #14598 Airport module not accessible from Mirador
# from Airport import Airport
from utils.airport_tz import Airport
from tm import TM, TMC
import utils.xmlutil as xml
from utils.xmlutil import XMLDocument, XMLElement


# exports================================================================={{{1
__all__ = ['main', 'report']


# logging ================================================================{{{1
log = logging.getLogger(script)
logging.basicConfig(format='%(asctime)s: %(module)s: %(levelname)s: %(message)s', level=logging.INFO)


# Exceptions ============================================================={{{1

# UsageException ---------------------------------------------------------{{{2
class UsageException(Exception):
    """ Raised for usage errors (wrong name/type of arguments, etc.). """
    msg = ''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


# help functions ========================================================={{{1
def _b2ap(base):
    """ Converts a base to an equivalent airport """
    if base == "STO":
        return "ARN"
    return base


# help classes ==========================================================={{{1

# ATime ------------------------------------------------------------------{{{2
class ATime:
    """
    Class for conversion between time in UTC and local time.
    """
    def __init__(self, timeUTC, locality):
        """ timeUTC (AbsTime), locality (airport) """
        self.timeUTC = timeUTC
        self.locality = locality

    def __str__(self):
        """ Return time as UTC in ISO-8601 format """
        return "%04d-%02d-%02dT%02d:%02d:00Z" % self.timeUTC.split()

    def asLocalTime(self, lex24=False):
        """ Return local time in ISO-8601 format """
        t = Airport(self.locality).getLocalTime(self.timeUTC)
        (yy, mm, dd, HH, MM) = t.split()
        #(yy, mm, dd, HH, MM) = Airport(self.locality).getLocalTime(self.timeUTC).split()
        from RelTime import RelTime
        if lex24 and HH == 00 and MM == 00:
            t2 = t - RelTime(0,1)
            (y, mo, d) = t2.split()[:3]
            h = 23
            mi = 59
            return "%04d-%02d-%02dT%02d:%02d:59" % (y, mo, d, h, mi)
                
        return "%04d-%02d-%02dT%02d:%02d:00" % (yy, mm, dd, HH, MM)

    def asLocalDate(self):
        """ Return time as local date in ISO-8601 format """
        return "%04d-%02d-%02d" % Airport(self.locality).getLocalTime(self.timeUTC).split()[:3]

    def __int__(self):
        return int(self.timeUTC)

    def __eq__(self, other):
        return int(self) == int(other)

    def __ge__(self, other):
        return int(self) >= int(other)

    def __gt__(self, other):
        return int(self) > int(other)

    def __le__(self, other):
        return int(self) <= int(other) 

    def __lt__(self, other):
        return int(self) < int(other)

    def __ne__(self, other):
        return int(self) != int(other)


# Activity ---------------------------------------------------------------{{{2
class Activity:
    """
    Activity object contains data for an activity.
    """
    def __init__(self, act):
        # Start and end times
        try:
            self.taskCode = act.activity.id
        except:
            self.taskCode = act.getRefI('activity')
        try:
            self.adep = act.adep.id
        except:
            self.adep = str(act.getRefI('adep'))
        try:
            self.ades = act.ades.id
        except:
            self.ades = str(act.getRefI('ades'))

        self.st = ATime(act.st, self.adep)
        self.et = ATime(act.et, self.ades)

    def __str__(self):
        return "<Activity " + ' '.join(['%s="%s"' % (k, v) for (k, v) in self.__dict__.iteritems() if not k.startswith("_")]) + ">"

    def getPeriods(self):
        return Periods((self.st.timeUTC, self.et.timeUTC))


# VacationGroup ----------------------------------------------------------{{{2
class VacationGroup:
    """Vacation group object"""
    def __init__(self, base, rank, qual, start, end):
        self.activities = []
        self.name = "%s-%s-%s" % (base, rank, qual)
        self.start = ATime(start, _b2ap(base))
        self.end = ATime(end, _b2ap(base))

    def __str__(self):
        return "%s [%s-%s]" % (self.name, self.start.asLocalDate(), self.end.asLocalDate())

    def hasActivities(self):
        return len(self.activities) > 0

    def append(self, name, start, end):
        """ Append a vacation activity """
        self.activities.append((name,start,end))

    def getPeriods(self):
        return Periods((self.start.timeUTC, self.end.timeUTC))


# Qualification ----------------------------------------------------------{{{2
class Qualification:
    """ Qualification object """
    def __init__(self, qrec):
        self.name = qrec.qual.subtype
        self.validfrom = qrec.validfrom
        self.validto = qrec.validto


# Periods ----------------------------------------------------------------{{{2
class Periods:
    """ Class for managing validity periods 
        As new periods are added they are merged with existing ones such
        that the resulting list of periods never contains overlapping
        or adjacent periods.
    """
    def __init__(self, p=None):
        self.periods = []
        if p is not None:
            self.add(p)

    def __str__(self):
        res = ""
        for (s,e) in self.periods:
            res = "%s,[%s-%s]" % (res, str(s)[:9], str(e)[:9])
        return res

    def getOverlapsWith(self, p):
        """ Return periods (or fragments of periods) in common with p """
        overlaps = Periods()
        for (s0, e0) in self.periods:
            for (s1, e1) in p.periods:
                if s0 < e1 and e0 > s1:
                    start = max(s0,s1)
                    end = min(e0,e1)
                    overlaps.add((start,end))
        return overlaps

    def add(self, (start, end)):
        """ Add a period and merge with existing if necessary 
            ++ Example1: ++++++++++++++++++++++++++++++++++++++++++++++++
            +   Existing periods: |----------|         |----------|     +
            +   Add period:           |---------|                       +
            +   ======================================================= +
            +   Result:           |-------------|      |----------|     +
            +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            ++ Example2: ++++++++++++++++++++++++++++++++++++++++++++++++
            +   Existing periods: |----------|         |----------|     +
            +   Add period:                  |---------|                +
            +   ======================================================= +
            +   Result:           |-------------------------------|     +
            +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        """
        lc = copy(self.periods)
        lc.append((start,end))
        idx = 0
        while idx < len(lc):
            len0 = len(lc)
            p = lc.pop(idx)
            lc = self._merge(lc, p)
            if len(lc) == len0:
                idx += 1
        self.periods = lc

    def _merge(self, l, (start,end)):
        """ Merge overlapping periods """
        lc = []
        overlap = False
        for (s0, e0) in l:
            if start <= e0 and end >= s0:
                overlap = True
                if start < s0:
                    s0 = start
                if end > e0:
                    e0 = end
            lc.append((s0, e0))
        if not overlap:
            lc.append((start, end))
        return lc


# XML formatting classes ================================================={{{1

# crewMessage ------------------------------------------------------------{{{2
class crewMessage(XMLElement):
    def __init__(self, m):
        XMLElement.__init__(self)
        #self['xlmns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
        #self['xsi:noNamespaceSchemaLocation'] = "crewVacationTradeSnapshot.xsd"
        # using crew1.8.zip
        self['version'] = "1.8"
        self.append(XMLElement('messageName', 'CrewVacationTradeSnapshot'))
        self.append(XMLElement('messageBody', crewVacationTradeSnapshot(m)))


# crewVacationTradeSnapshot ----------------------------------------------{{{2
class crewVacationTradeSnapshot(XMLElement):
    def __init__(self, m):
        XMLElement.__init__(self)
        self['version'] = "1.00"
        # Sort by extperkey
        L = [extperkey for extperkey in m.keys()]
        L.sort()
        for extperkey in L:
            self.append(crew(m, extperkey))


# crew -------------------------------------------------------------------{{{2
class crew(XMLElement):
    def __init__(self, m, extperkey):
        XMLElement.__init__(self)
        self.append(XMLElement("crewId", "SK  %s" % extperkey))
        self.append(vacGrps(m[extperkey]))


# vacGrps ----------------------------------------------------------------{{{2
class vacGrps(XMLElement):
    def __init__(self, vgs):
        XMLElement.__init__(self)
        # Sort vacation groups by startDate
        L = [ (vg.start.asLocalDate(), vg) for vg in vgs ]
        L.sort()
        for vg in [ x[1] for x in L ]:
            if vg.hasActivities():
                self.append(vacGrp(vg))


# vacGrp -----------------------------------------------------------------{{{2
class vacGrp(XMLElement):
    def __init__(self, vg):
        XMLElement.__init__(self)
        self.append(XMLElement('name', vg.name))
        self.append(XMLElement('startDate', vg.start.asLocalDate()))
        self.append(XMLElement('endDate', vg.end.asLocalDate()))
        self.append(vacActs(vg.activities))


# vacActs ----------------------------------------------------------------{{{2
class vacActs(XMLElement):
    def __init__(self, acts):
        XMLElement.__init__(self)
        for a in acts:
            self.append(vacAct(a))


# vacAct -----------------------------------------------------------------{{{2
class vacAct(XMLElement):
    def __init__(self, (name,start,end)):
        XMLElement.__init__(self)
        self.append(XMLElement('taskCode', name))
        self.append(XMLElement('std', start.asLocalTime()))
        self.append(XMLElement('sta', end.asLocalTime(lex24=True)))
        
# functions =============================================================={{{1

# report -----------------------------------------------------------------{{{2
def report(verbose=False, now=None):
    """
    Returns the message as a long string.
    """

    # Build something to iterate over

    if now is None: 
        now = time.gmtime(time.time())
        nowAbsTime = AbsTime(*now[:5])
    else:
        nowAbsTime = now


    # Structure of ca is:
    # ca = { crew1: [act11, act12, ...], crew2: [act21, act22, ...], ... }
    if verbose:
        log.info("Looking for activities")
    ca = {}
    for act in TM.crew_activity.search('(&(et>%s)(|(activity=F7)(activity=VA)(activity=VA1)))' % (nowAbsTime)):
        try:
            crewid = act.crew.id
        except:
            log.warning("Cannot find crew with id '%s' in entity 'crew'." % act.getRefI('crew'))
            continue

        if crewid in ca:
            ca[crewid].append(Activity(act))
        else:
            ca[crewid] = [ Activity(act) ]

    if verbose:
        log.info("Looking for qualifications...")
        counter = 1
    # Structure of quals is:
    # quals = { 
    #    crew1: [qual11, qual12, ...], 
    #    crew2: [qual21, qual22, ...], 
    #    ... 
    # }
    # where qualNN is object of type Qualification
    quals = {}
    for q in TM.crew_qualification.search('(&(qual.typ=ACQUAL)(validto>%s))' % (nowAbsTime)):
        if verbose:
            if counter % 1000 == 0:
                log.info("Looking for qualifications... (%d)" % (counter))
            counter += 1
        try:
            crewid = q.crew.id
        except:
            log.warning("Cannot find crew with id '%s' in entity 'crew'." % q.getRefI('crew'))
            continue
        if not crewid in quals:
            quals[crewid] = []
        quals[crewid].append(Qualification(q))

    if verbose:
        log.info("Looking for ranks etc...")
        counter = 1
    empmap = {}
    qualmap = {}
    idmap = {}
    # Create hash tables empmap and qualmap
    #
    # The structure of empmap is:
    # empmap = {
    #    empno1: {(base11,rank11): periods11, (base12,rank12): periods12, ...},
    #    empno2: {(base21,rank21): periods21, (base22,rank22): periods22, ...},
    #    ...
    # }
    # ,where periodsNN is object of type Periods which holds a list of
    # periods (from, to) where crew has a certain compination of base
    # and rank.
    #
    # The structure of qualmap is:
    # qualmap = {
    #    empno1: {qual11: periods11, qual12: periods12, ...},
    #    empno2: {qual21: periods21, qual22: periods22, ...},
    #    ...
    # }
    # ,where periodsNN is object of type Periods which holds a list of
    # periods (from, to) where crew has a certain qualification.
    # 
    # Also create idmap which is a dictionary of empno->crewid
    for e in TM.crew_employment.search('(validto>%s)' % (nowAbsTime)):
        if verbose:
            if counter % 1000 == 0:
                log.info("Looking for ranks etc... (%d)" % (counter))
            counter += 1
        try:
            crewid = e.crew.id
        except:
            log.warning("Cannot find crew with id '%s' in entity 'crew'." % e.getRefI('crew'))
            continue
        if not crewid in quals:
            log.warning("Cannot find any qualifications for crew %s" % (crewid))
            continue

        # Get extperkey from first entry in crew_employment, which by definition is the SAS internal crewId
        ceItr = TM.crew_employment.search('(crew=%s)' % (crewid))
        for ce in ceItr:
            SASinternalId = ce.extperkey
            break
        else:
            SASinternalId = crewid
        log.debug('crewid: %s SAS id: %s extperkey: %s' % (crewid, SASinternalId, e.extperkey))
        if not SASinternalId in empmap:
            empmap[SASinternalId] = {}
        if not (e.base.id, e.crewrank.id) in empmap[SASinternalId]:
            empmap[SASinternalId][(e.base.id, e.crewrank.id)] = Periods()
        empmap[SASinternalId][(e.base.id, e.crewrank.id)].add((e.validfrom, e.validto))
        idmap[SASinternalId] = crewid

        for q in quals[crewid]:
            if not SASinternalId in qualmap:
                qualmap[SASinternalId] = {}
            if not q.name in qualmap[SASinternalId]:
                qualmap[SASinternalId][q.name] = Periods()
            qualmap[SASinternalId][q.name].add((q.validfrom, q.validto))

    # Create the groups of each employee. A group is a combination
    # of properties in crew_employment (base and rank) and 
    # crew_qualification (qual. sybtype). Since records in these tables
    # have their own independent validity periods, the aggregated
    # validity period of the group must be calculated by looking at
    # overlapping periods. An example is given below:
    #
    # crew_employment:  (base and rank is denoted b1,b2,... r1,r2,...)
    # t1     t3
    # |------|                                              b1,r1
    #              t4
    #        |-----|                                        b1,r1
    #                        t6
    #              |---------|                              b1,r2
    #                                               t10
    #                        |----------------------|       b2,r2
    #
    # crew_qualification:  (qual. subtypes are denoted q1, q2,...)
    #     t2            t5
    #     |-------------|                                   q1
    #                        t6
    #                   |----|                              q2
    #                              t7
    #                        |-----|                        q3
    #                                  t8    t9
    #                                  |-----|              q3
    #                                               t10
    #                                        |------|       q3
    # The resulting groups would be:
    # Group name     fromDate     toDate
    # ======================================
    # b1-r1-q1       t2           t4
    # b1-r2-q1       t4           t5
    # b1-r2-q2       t5           t6
    # b2-r2-q3       t6           t7
    # b2-r2-q3       t8           t10
    #
    crewgroups = {}
    # Structure of crewgroups is:
    # crewgroups = {
    #   empno1: [vg11, vg12, ...],
    #   empno2: [vg11, vg12, ...],
    #   ...
    # }
    # where vgNN is object of type VacationGroup.
    for empno in empmap:
        for (base, rank) in empmap[empno]:
            pemp = empmap[empno][(base, rank)]
            for qual in qualmap[empno]:
                pqual = qualmap[empno][qual]
                grpPeriods = pemp.getOverlapsWith(pqual)
                for (start, end) in grpPeriods.periods:
                    grp = VacationGroup(base, rank, qual, start, end)
                    if not empno in crewgroups:
                        crewgroups[empno] = []
                    # Group start dates must be unique per crew.
                    # Before adding the group, check that there isn't already
                    # a group with the same start date. If so, keep the one
                    # with the highest end date.
                    duplicate = False
                    for g in crewgroups[empno]:
                        if grp.start.asLocalDate() == g.start.asLocalDate():
                            if grp.end.asLocalDate() >= g.end.asLocalDate():
                                crewgroups[empno].remove(g)
                            else:
                                duplicate = True
                            break
                    if not duplicate:
                        crewgroups[empno].append(grp)

    # Add vacation activities to the groups
    for empno in crewgroups:
        for grp in crewgroups[empno]:
            crewid = idmap[empno]
            if crewid in ca:
                for act in ca[crewid]:
                    actPeriods = grp.getPeriods().getOverlapsWith(act.getPeriods())
                    for (start, end) in actPeriods.periods:
                        grp.append(act.taskCode, ATime(start,act.adep), ATime(end,act.ades))

    return XMLDocument(crewMessage(crewgroups))


# functions =============================================================={{{1

# dictTranslate ----------------------------------------------------------{{{2
def dictTranslate(d, t):
    """
    The dictionary 'd' will be translated using dictionary 't'.
    Example:
        d = {'verbose': False, 'mqhost': 'taramajima', 'mqport': 1415 }
        t = {'mqhost': 'host', 'mqport': 'port' }
        x = translate(d, t)
    will result in:
        x => {'host': 'taramajima', 'port': 1415}
    """
    r = {}
    for (k, v) in d.iteritems():
        if k in t:
            r[t[k]] = v
    return r


# main -------------------------------------------------------------------{{{2
def main(*argv, **options):
    """
    X3 -c connect -s schema [-d date] [-o output_file] [-v] [-h]
        [-n mqserver -p mqport -k mqchannel -m mqmanager -q mqqueue
        [-a mqaltuser]]

    usage:
        -c  connect_string
        --connect connect_string
            Use this connect string to connect to database.

        -s  schema
        --schema schema
            Use this schema.

        -d  date
        --date date
            Show activities after this date. Default is to use current
            system time.

        -o  output_file
        --output output_file
            Print output to this file. (If no filename given the result
            will be printed to stdout).

        -n  mqhost
        --mqhost mqhost

        -p  mqport
        --mqport mqport

        -k  mqchannel
        --mqchannel mqchannel

        -m  mq queue manager
        --mqmanager mqmanager

        -q  queue
        --mqqueue queue
            MQ output queue (overrides option -o)

        -a altuser
        --mqaltuser altuser
            Alternate MQ user.

        -v
        --verbose
            Print verbose messages.

        -h
        --help
            This help text.
    """
    if len(argv) == 0:
        argv = sys.argv[1:]
    try:
        try:
            (opts, args) = getopt.getopt(argv, "a:c:d:ho:s:vn:p:k:m:q:",
                [
                    "connect=",
                    "date=",
                    "help",
                    "mqaltuser="
                    "mqchannel=",
                    "mqhost=",
                    "mqmanager=",
                    "mqport=",
                    "mqqueue=",
                    "output=",
                    "schema=",
                    "verbose",
                ])
        except getopt.GetoptError, msg:
            raise UsageException(msg)

        for (opt, value) in opts:
            if opt in ('-h', '--help'):
                print __doc__
                print main.__doc__
                return 0
            if opt in ('-v', '--verbose'):
                options['verbose'] = True
            elif opt in ('-c', '--connect'):
                options['connect'] = value
            elif opt in ('-d', '--date'):
                options['date'] = value
            elif opt in ('-o', '--output'):
                options['output'] = value
            elif opt in ('-s', '--schema'):
                options['schema'] = value
            elif opt in ('-n', '--mqhost'):
                options['mqhost'] = value
            elif opt in ('-p', '--mqport'):
                options['mqport'] = int(value)
            elif opt in ('-k', '--mqchannel'):
                options['mqchannel'] = value
            elif opt in ('-m', '--mqmanager'):
                options['mqmanager'] = value
            elif opt in ('-q', '--mqqueue'):
                options['mqqueue'] = value
            elif opt in ('-a', '--mqaltuser'):
                options['mqaltuser'] = value
            else:
                pass

        try:
            connect = options['connect']
            schema = options['schema']
        except:
            raise UsageException("The arguments '-c connect' and '-s schema' are mandatory.")

        verbose = 'verbose' in options

        global TM
        if utils.mdor.started:
            TM = TMC(connect, schema)

        if 'date' in options:
            date = AbsTime(options['date'])
        else:
            date = None

        if 'mqqueue' in options:
            if verbose:
                log.info("Output to MQ queue '%s'." % (options['mqqueue']))

            if 'mqport' in options:
                options['mqport'] = int(options['mqport'])

            mqm = jmq.Connection(**dictTranslate(options, {
                'mqhost': 'host',
                'mqport': 'port',
                'mqmanager': 'manager',
                'mqchannel': 'channel',
            }))
            if 'mqaltuser' in options:
                mqq = mqm.openQueue(queueName=options['mqqueue'], altUser=options['mqaltuser'], mode='w')
            else:
                mqq = mqm.openQueue(queueName=options['mqqueue'], mode='w')

            try:
                msg = jmq.Message(content=report(verbose, date))
                mqq.writeMessage(msg)
                mqm.commit()
            except:
                mqm.rollback()
                mqq.close()
                mqm.disconnect()
                raise

            mqq.close()
            mqm.disconnect()

        elif 'output' in options:
            of = open(options['output'], 'w')
            if verbose:
                log.info("Output to file '%s'." % (options['output']))
            print >>of, report(verbose, date)
            of.close()

        else:
            if verbose:
                log.info("Output to stdout.")
            print report(verbose, date) 

        if verbose:
            log.info("Finished.")

    except UsageException, err:
        log.error(str(err))
        log.info("for help use --help")
        return 2
    except SystemExit, err:
        pass
    except Exception, e:
        log.error(str(e))
        return 2

    return 0


# main ==================================================================={{{1
if __name__ == '__main__':
    #sys.exit(main())
    main()


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof

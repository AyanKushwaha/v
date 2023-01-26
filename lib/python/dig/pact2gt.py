# [acosta:08/280@15:38] Copied from a script in adhoc and adapted to DIG.

"""
Convert all PACTs that are either SIM, courses or recurrent training into
ground tasks (they have a grp within category 'SIM', 'EDU', or 'REC'.
Assign these ground tasks.

Convert all SIMs with activity codes starting with 'Z' or 'Y' into
activities starting with 'S', keep the number that signals aircraft family,
but remove the last digit, thus: Y43 -> S4, Z37 -> S3, ZO32 -> SO3.

If the activity code of the PACT started with a 'Z', then set the
attribute: 'TRAINING' - 'SKILL TEST'.

Move all attributes that are linked to the PACT to the newly created ground
task.

The position is by default the crew rank at the time of the activity,

These attributes in 'crew_activity_attr' will affect the assignments:

    SIM INSTR               Assign in position 4, 'FU'.
    SIM INSTR SUPERVIS      ditto

These activities will lead to an attribute 'RECURRENT' with the following
string values:
    Activity                value_str

    (Y|Z)6.*                LPCA3
    S6.*                    OPCA3
    S6.*                    OTSA3
    (Y|Z)4.*                LPCA4
    S4*                     OPCA4
    S4*                     OTSA4
    (Z|Y)[^6^4].*           LPC
    S[^6^4].*               OPC
    S[^6^4].*               OTS
"""

# Notes: see usage notes last in this file.
#   dc - dave connector object from DIG

# imports ================================================================{{{1
import logging
import re
import sys

import carmensystems.dig.framework.dave as dave
import utils.spinner as spinner

from optparse import OptionParser

from utils.rave import RaveEvaluator
from AbsTime import AbsTime
from carmensystems.basics.uuid import uuid
from utils.dutycd import rank2pos
from utils.exception import locator


# exports ================================================================{{{1
__all__ = ['run', 'main', 'pact_converter', 'training_activities', 'Result']

my_package = 'dig'
my_name = 'pact2gt'


# logging ================================================================{{{1
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("%s.%s" % (my_package, my_name))


# module variables ======================================================={{{1
dutycd2cgdattr = {
    'A': 'SIM ASSIST',
    'I': 'SIM INSTR',
    'IU': 'SIM INSTR SUPERVIS',
    'L': 'SIM LOWER',
    'S': 'SIM SUPERVIS',
    'U': 'SIM SUPERNUM',
    'Z': 'SIM INSTR SUPERVIS',
}


# PACT2GTError ==========================================================={{{1
class PACT2GTError(Exception):
    """User-defined Exception in 'pact2gt' module."""
    msg = ''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)


# Help classes ==========================================================={{{1

# ActivityGroupCategory --------------------------------------------------{{{2
class ActivityGroupCategory(dict):
    """Dictionary that contains all activities with group and category.  Upon
    first access, the dictionary will be filled from the database."""

    def __init__(self):
        dict.__init__(self)
        self.__filled = False

    def __call__(self, dc):
        log.debug("%s(%s)" % (locator(self), dc))
        if not self.__filled:
            log.debug("...filling data.")
            self.clear()
            c = {}
            for x in dbsearch(dc, 'activity_group'):
                c[x['id']] = x['cat']
            for x in dbsearch(dc, 'activity_set'):
                self[x['id']] = x['grp'], c.get(x['grp'])
        self.__filled = True
        return self

    def cat(self, act_id):
        """Get activity category for activity with id 'act_id'."""
        return self._get(act_id)[1]

    def grp(self, act_id):
        """Get activity group for activity with id 'act_id'."""
        return self._get(act_id)[0]

    def _get(self, act_id):
        if not self.__filled:
            raise PACT2GTError("Programming error: ActivityGroupCategory() was never filled with data.")
        return self.get(act_id, (None, None))


# Result -----------------------------------------------------------------{{{2
class Result(dict):
    """Keep result of operations."""
    def __init__(self, converted=0, removed=0, failed=0):
        dict.__init__(self, converted=converted, removed=removed, failed=failed)

    def __getattr__(self, key):
        return self.get(key, 0)

    def add_converted(self, num=1):
        self['converted'] += num

    def add_removed(self, num=1):
        self['removed'] += num

    def add_failed(self, num=1):
        self['failed'] += num


# Classes representing some basic entities. =============================={{{1

# CA2GT ------------------------------------------------------------------{{{2
class CA2GT(tuple):
    """Help class. Keeps identity of ground task (as tuple) so that activities
    that start on the same time, at the same place and with the same name will
    be treated as one."""
    def __new__(cls, dc, ca):
        """ca - crew_activity record."""
        return tuple.__new__(cls, (ca.short_name(), ca['st'], ca['et'],
            ca['adep'], ca['ades']))

    def __init__(self, dc, ca):
        """ca - crew_activity record."""
        self.dc = dc
        self.ca = ca

    def __str__(self):
        return "<%s %s>" % (self.__class__.__name__, 
                str(tuple([str(x) for x in self])))

    def find(self):
        """Try to locate a ground_task in the database."""
        log.debug("%s: searching for %s in 'ground_task'." % (locator(self), self))
        for x in dbsearch(self.dc, 'ground_task',
                "activity = '%s' AND st = %d AND et = %d AND adep = '%s' AND ades = '%s'" % self):
            log.debug("... found - %s" % gt2str(x))
            return x
        log.debug("... not found")
        raise PACT2GTError("Could not find any ground_task matching %s." % str(self))

    def ground_task(self):
        """Return 'ground_task' record."""
        code, st, et, adep, ades = self
        uuid = uuid.makeUUID64()
        gt = dict(udor=(st / 1440), id=uuid, st=st, et=et, adep=adep,
                ades=ades, activity=code, statcode="A", si=my_name)
        log.debug("%s(): returning <ground_task %s> record." % (locator(self), task2str(gt)))
        return gt


# Crew -------------------------------------------------------------------{{{2
class Crew(dict):
    """Representation of a crew member."""
    def __init__(self, dc, ca):
        dict.__init__(self, ca)
        self.dc = dc

    def __str__(self):
        return "<%s %s>" % (self.__class__.__name__, self['crew'])

    def get_rank_at_date(self, date):
        """Return crewrank at specified date."""
        for c in dbsearch(self.dc, 'crew_employment', "crew = '%s'" % self['crew']):
            if c['validfrom'] <= date and date < c['validto']:
                return c['crewrank']
        # Not good, no valid rank found.
        raise PACT2GTError("Could not find any valid rank for crew with id '%s'." % self['crew'])

    def get_position(self, ca, dutycd=None):
        """Return a position that is valid when activity starts.  'ca' is a
        'CrewActivity' object."""
        got_lower = False
        if ca.is_simulator():
            attr = dutycd2cgdattr.get(dutycd)
            if attr is None:
                for caa in ca.attributes('TRAINING'):
                    attr = caa['value_str']
                    break
            if attr is not None:
                if attr.startswith('SIM'):
                    if attr in ('SIM INSTR SUPERNUM', 'SIM INSTR SUPERVIS', 'SIM SUPERNUM'):
                        return "FU"
                    if attr in ('SIM INSTR', 'SIM SUPERVIS'):
                        return "TR"
                    if attr == 'SIM LOWER':
                        got_lower = True
        if ca.is_tl():
            return 'TL'
        rank = self.get_rank_at_date(ca['st'])
        if rank == "FC" and got_lower:
            return "FP"
        if rank == "FR" and ca.is_lpc_opc_ots():
            # Assign as FP if LPC or OPC/OTS
            return "FP"
        # The call to rank2pos will make sure that only valid positions are
        # returned, e.g. AA -> AH, FS -> FU
        return rank2pos(rank)


# CrewActivity -----------------------------------------------------------{{{2
class CrewActivity(dict):
    """Representation of a crew_activity record."""
    activity_regexp = re.compile(r'([A-Z])([A-Z]?)([0-9])([0-9]?)')
    _acqual_code_map = {
        "36": "3",
        "37": "9",
        "38": "3",
        "A2": "2",
        "A3": "6",
        "A4": "4",
        "CJ": "7",
        "M8": "8",
        "M0": "0", # Not used
    }

    def __init__(self, dc, ca_raw):
        dict.__init__(self, ca_raw)
        self.dc = dc
        self.grp = act_grp_cat.grp(self['activity'])
        self.is_skill_test = ca_raw['activity'].startswith('Z')
        self.__recurrent_attr = None
        self.__recurrent_attr_done = False
        self.__pc_attr = None
        self.__pc_attr_done = False

    def __str__(self):
        return "<%s %s>" % (self.__class__.__name__, task2str(self))

    def attributes(self, attr=None):
        """Return list of 'crew_activity_attr' dicts linked to this
        activity."""
        log.debug("%s(%s)" % (locator(self), attr))
        s = "ca_st = %(st)d AND ca_crew = '%(crew)s' AND ca_activity = '%(activity)s'" % self
        if not attr is None:
            s += "AND attr = '%s'" % (attr,)
        return dbsearch(self.dc, 'crew_activity_attr', s)

    def short_name(self):
        """Convert activities of group 'LPC', 'OPC' or 'OTS', e.g.:
        'Z43' to 'S4' (skill test)
        'Y31' to 'S3' (LPC)
        'YE31' to 'S3' (LPC)
        """
        if self.grp in ('LPC', 'OPC', 'OTS', 'AST', 'ASF', 'SIM'):
            m = self.activity_regexp.match(self['activity'])
            if m:
                main_grp, sub_grp, ac_type, time_slot = m.groups()
                if self.grp == 'ASF':
                    main_grp = 'CH'
                elif self.grp == 'SIM':
                    main_grp = 'CG'
                elif main_grp in ('Z', 'Y'):
                    main_grp = 'S'
                return ''.join((main_grp, ac_type))
        return self['activity']

    @property
    def recurrent_attr(self):
        """Look for the newest document in 'crew_document', and see if it has a
        qualification other than the simulator."""
        if not self.__recurrent_attr_done:
            self.__recurrent_attr = self.__get_recurrent_attr()
            self.__recurrent_attr_done = True
        return self.__recurrent_attr

    def __get_recurrent_attr(self):
        """Return the RECURRENT attribute for the act_id, or None if not SIM."""
        m = self.activity_regexp.match(self['activity'])
        if m:
            main_grp, sub_grp, ac_type, time_slot = m.groups()
            if main_grp in ('Z', 'Y'):
                return {'4': 'LPCA4', '6': 'LPCA3'}.get(ac_type, 'LPC')
            elif main_grp == 'S':
                if RaveEvaluator.rEval('fundamental.%use_link_tracking_ruleset%') is True:
                    return {'4': 'OPCA4', '6': 'OPCA3'}.get(ac_type, 'OPC')
                else:
                    return {'4': 'OTSA4', '6': 'OTSA3'}.get(ac_type, 'OTS')
            elif main_grp == 'E':
                return 'PGT'
            elif main_grp == 'N':
                return 'REC'
            elif main_grp == 'C':
                return 'CRM'

    @property
    def pc_attr(self):
        """Look for the newest document in 'crew_document', and see if it has a
        qualification other than the simulator."""
        if not self.__pc_attr_done:
            self.__pc_attr = self.__get_pc_attr()
            self.__pc_attr_done = True
        return self.__pc_attr

    def __get_pc_attr(self):
        """Return 'LPC FORCED' if latest document matches sim, else 'LPC CHANGE'.
        Return None if no match."""
        m = self.activity_regexp.match(self['activity'])
        if m:
            main_grp, sub_grp, ac_type, time_slot = m.groups()
            if main_grp == 'Y':
                L = []
                for doc in dbsearch(self.dc, 'crew_document', (
                        "crew = '%s' AND doc_typ = 'REC'"
                        " AND doc_subtype like 'LPC%%'") % self['crew']):
                    # Add tuple (validfrom, subtype)
                    L.append((doc['validfrom'], doc['validto'], doc['ac_qual']))
                L.sort()
                for validfrom, validto, ac_qual in L[::-1]:
                    if self._acqual_code_map.get(ac_qual) == ac_type:
                        # latest a/c qual doc is same as simulator a/c type
                        if self['st'] - validto > 6 * 30 * 1440: # Approx 6mths
                            # Long period of inactivity
                            return 'LPC CHANGE'
                        return 'LPC FORCED'
                    break
                return 'LPC CHANGE'

    def is_tl(self):
        """Activities that should be assigned as 'TL'."""
        return ((self.grp == 'CRM')
            or (self.grp in ('ASF', 'AST', 'FFS', 'SIM'))
            or (self['activity'][:2] in ('EH', 'EJ', 'EK', 'EX')))

    def is_own_position(self):
        """Activities thas should be assigned in own position."""
        return ((self['activity'] in ('CX7', 'CX8'))
            or (self['activity'][:2] in ('NP', 'NS' , 'NW')))

    def is_lpc_opc_ots(self):
        return self.grp in ('LPC', 'OPC', 'OTS')

    def is_simulator(self):
        return self.grp in ('LPC', 'OPC', 'OTS', 'ASF', 'AST', 'FFS', 'SIM')

    def is_convertable(self):
        return self.is_pc_opc() or self.is_tl() or self.is_own_position()

    def is_removable(self):
        return self.grp in ('SIB',)


# PACTConverter =========================================================={{{1
class PACTConverter(list):
    """Convert one crew_activity to ground_task and assign.  The preferred way
    to use this object is to call pact_converter."""
    def __init__(self, dc, date=None):
        list.__init__(self)
        self.dc = dc
        if not date is None:
            self.date = int(AbsTime(date))
        else:
            self.date = date
        self.ground_tasks = {}

    def __call__(self, ca_raw, result=Result(), dutycd=None):
        """ca is a crew_activity dict (not a CrewActivity object)."""
        log.debug("%s(<crew_activity %s>)" % (locator(self), task2str(ca_raw)))
        ca = CrewActivity(self.dc, ca_raw)
        if ca.is_convertable():
            try:
                self.conv(ca, dutycd)
                self.remove(ca)
                result.add_converted()
            except Exception, e:
                result.add_failed()
                log.error(str(e))
        elif ca.is_removable():
            try:
                self.remove(ca)
                result.add_removed()
            except Exception, e:
                result.add_failed()
                log.error(str(e))
        return result

    def is_convertable(self, act):
        """Note: called from TI3. 'act' is a string."""
        return CrewActivity(self.dc, {'activity': act}).is_convertable()

    def is_removable(self, act):
        """Note: called from TI3. 'act' is a string."""
        return CrewActivity(self.dc, {'activity': act}).is_removable()

    def conv(self, ca, dutycd=None):
        """Convert PACT to ground_task and assign."""
        log.debug("%s(%s, %s)" % (locator(self), ca, dutycd))
        ca2gt = CA2GT(self.dc, ca)
        crew = Crew(self.dc, ca)
        if ca2gt in self.ground_tasks:
            gt = self.ground_tasks[ca2gt]
        else:
            try:
                gt = ca2gt.find()
                self.ground_tasks[ca2gt] = gt
            except PACT2GTError:
                gt = ca2gt.ground_task()
                self.ground_tasks[ca2gt] = gt
                self.append(dave.createOp('ground_task', 'W', gt))
        try:
            self.assign(ca, gt, crew, dutycd)
        except Exception, e:
            log.error("Failed creating assignment [%s, %s] - %s" % (ca, crew, e))
            raise

    def assign(self, ca, gt, crew, dutycd=None):
        """Assign ground task to crew member."""
        log.debug("%s(%s, <ground_task %s>, %s, %s)" % (locator(self), ca,
            gt2str(gt), crew, dutycd))
        cgd = dict(
            task_udor=gt['udor'], 
            task_id=gt['id'], 
            crew=crew['crew'],
            pos=crew.get_position(ca, dutycd), 
            personaltrip=uuid.makeUUID64(), 
            si=(ca['si'] or my_name))
        log.debug("... creating <crew_ground_duty %s>" % cgd2str(cgd))
        self.append(dave.createOp('crew_ground_duty', 'W', cgd))
        has_training_attribute = False
        for caa in ca.attributes():
            log.debug("... moving attribute %s" % caa2str(caa))
            value_str = caa['value_str']
            try:
                if caa['attr'] == 'TRAINING':
                    value_str = caa['value_str'].replace('SIM INSTR SUPERNUM', 
                            'SIM INSTR SUPERVIS')
            except:
                pass
            self.append(dave.createOp('crew_ground_duty_attr', 'W', dict(
                cgd_task_udor=gt['udor'],
                cgd_task_id=gt['id'],
                cgd_crew=crew['crew'],
                attr=caa['attr'],
                value_rel=caa['value_rel'],
                value_abs=caa['value_abs'],
                value_str=value_str,
                si=caa['si'])))
            if caa['attr'] == 'TRAINING':
                has_training_attribute = True
        if dutycd is not None:
            cgd_dutycd_attr = dutycd2cgdattr.get(dutycd)
            if cgd_dutycd_attr is not None:
                log.debug("... adding TRAINING attribute '%s', based on dutycd '%s'" % (
                    cgd_dutycd_attr, dutycd))
                self.append(dave.createOp('crew_ground_duty_attr', 'W', dict(
                    cgd_task_udor=gt['udor'],
                    cgd_task_id=gt['id'],
                    cgd_crew=crew['crew'],
                    attr="TRAINING",
                    value_str=cgd_dutycd_attr,
                    si="Added by %s, based on duty code '%s'." % (my_name, 
                        dutycd))))
                has_training_attribute = True
        if ca.is_skill_test and not has_training_attribute:
            log.debug("... adding 'TRAINING', 'SKILL TEST'")
            self.append(dave.createOp('crew_ground_duty_attr', 'W', dict(
                cgd_task_udor=gt['udor'],
                cgd_task_id=gt['id'],
                cgd_crew=crew['crew'],
                attr="TRAINING",
                value_str="SKILL TEST",
                si="Added by %s, old activity was %s." % (my_name,
                    ca['activity']))))
        if not has_training_attribute and not ca.pc_attr is None:
            log.debug("... adding 'TRAINING', '%s'" % ca.pc_attr)
            self.append(dave.createOp('crew_ground_duty_attr', 'W', dict(
                cgd_task_udor=gt['udor'],
                cgd_task_id=gt['id'],
                cgd_crew=crew['crew'],
                attr="TRAINING",
                value_str=ca.pc_attr,
                si="Added by %s, old activity was %s." % (my_name,
                    ca['activity']))))
        # RECURRENT ATTR, only run stand-alone (not TI3).
        if (not self.date is None and gt['udor'] < (self.date / 1440) 
                and not ca.recurrent_attr is None):
            log.debug("... adding 'RECURRENT', '%s'" % ca.recurrent_attr)
            self.append(dave.createOp('crew_ground_duty_attr', 'W', dict(
                cgd_task_udor=gt['udor'],
                cgd_task_id=gt['id'],
                cgd_crew=crew['crew'],
                attr="RECURRENT",
                value_str=ca.recurrent_attr,
                si="Added by %s, old activity was %s." % (my_name,
                    ca['activity']))))

    def remove(self, ca):
        """Remove PACT."""
        log.debug("%s(%s)" % (locator(self), task2str(ca)))
        self.append(dave.createOp('crew_activity', 'D', ca))
        self.append(dave.createOp('crew_activity_attr', 'D', dict(
            ca_st=ca['st'], 
            ca_crew=ca['crew'],
            ca_activity=ca['activity'])))

    def store(self, *a, **kw):
        """Commit changes to database and return commitid."""
        return dave.DaveStorer(self.dc).store(self, *a, **kw)


# Main ==================================================================={{{1
class Main:
    """Convert all PACTs that are either SIM, courses or recurrent training
    into ground tasks.  'crew_activity' is scanned for "convertable"
    activities.
    This class is used when run as batch job."""

    def __init__(self):
        pass

    def __call__(self, connect, schema, date=None, branch=None, debug=False,
            verbose=False, commit=False):
        """Convert all records in 'crew_activity', this is the main entry
        when run as a batch job."""
        if debug:
            log.setLevel(logging.DEBUG)
        dave_connector = dave.DaveConnector(connect, schema, branch)
        log.debug("Searching for activities to convert/remove.")
        pc = pact_converter(dave_connector, date)
        result = Result()
        log.info("Working on activities from 'crew_activity'.")
        all_activities = dbsearch(dave_connector, 'crew_activity')
        if verbose:
            s = spinner.Spinner()
            p = spinner.ProgressBar(len(all_activities))
            x = 0
        for ca in all_activities:
            if verbose:
                if x % 1000 == 0:
                    p(x).write()
                if x % 100 == 0:
                    s.write()
                x += 1
            pc(ca, result)
        if verbose:
            p(x).final()

        if commit:
            cid = pc.store(returnCommitId=True)
            log.info("Stored with commitid = %d" % cid)

        dave_connector.close()
        log.info("%(converted)d records converted, %(removed)d records removed." % result)
        if result['failed'] > 0:
            log.error("%(failed)d failures recorded!" % result)
        return result

    def main(self, *argv):
        """Handle command line arguments and call __call__."""
        try:
            if len(argv) == 0:
                argv = sys.argv[1:]
            parser = OptionParser()
            parser.add_option('-d', '--debug', 
                    dest="debug", 
                    action="store_true",
                    default=False, 
                    help="Print out extensive messages for debugging purposes.")
            parser.add_option('-v', '--verbose', 
                    dest="verbose", 
                    action="store_true",
                    default=False, 
                    help="Show progress bar.")
            parser.add_option('-c', '--connect', 
                    dest="connect", 
                    help="Database connect string.")
            parser.add_option('-s', '--schema', 
                    dest="schema", 
                    help="Database schema string.")
            parser.add_option('-b', '--branch', 
                    dest="branch", 
                    help="Database branch.")
            parser.add_option('-D', '--date', 
                    dest="date", 
                    help="Extract date.")
            parser.add_option('-n', '--nocommit', 
                    dest="commit",
                    action="store_false",
                    default=True,
                    help="Don't commit any changes to database.")
            parser.add_option('-l', '--log', 
                    dest="log", 
                    help="Name of optional log file.")
            opts, args = parser.parse_args(list(argv))
            if opts.schema is None:
                parser.error("Must supply option 'schema'.")
            if opts.connect is None:
                parser.error("Must supply option 'connect'.")
            if opts.date is None:
                parser.error("Must supply option 'date'.")
            if opts.log is not None:
                for h in logging.getLogger('').handlers:
                    # Don't send debugging info to console if we have a file.
                    h.setLevel(logging.INFO)
                f_handler = logging.FileHandler(opts.log)
                f_handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
                log.addHandler(f_handler)
            try:
                date = int(AbsTime(opts.date))
            except:
                parser.error("The 'date' argument is in wrong format.")

            self(opts.connect, opts.schema, date, branch=opts.branch,
                    debug=opts.debug, verbose=opts.verbose, commit=opts.commit)

        except SystemExit, e:
            log.info("Finished: rc=%s" % str(e))

        except Exception, e:
            log.error("%s: Exception: %s" % (locator(self), e))
            raise
        return 0


# act_grp_cat ============================================================{{{1
act_grp_cat = ActivityGroupCategory()


# functions (internal use) ==============================================={{{1

# dbsearch ---------------------------------------------------------------{{{2
def dbsearch(dc, entity, expr=[]):
    """Search entity and return list of DCRecord objects."""
    if isinstance(expr, str):
        expr = [expr]
    return dc.runSearch(dave.DaveSearch(entity, expr))


# caa2str ----------------------------------------------------------------{{{2
def caa2str(caa):
    """For debug printouts (crew_activity_attr)."""
    return "ca_crew=%(ca_crew)s ca_st=%(ca_st)s ca_activity=%(ca_activity)s attr=%(attr)s" % caa


# cgd2str ----------------------------------------------------------------{{{2
def cgd2str(cgd):
    """For debug printouts (crew_ground_duty)."""
    return "crew=%(crew)s pos=%(pos)s task_id=%(task_id)s task_udor=%(task_udor)s" % cgd


# task2str ---------------------------------------------------------------{{{2
def task2str(gt):
    """For debug printouts (ground_task, crew_activity)."""
    return "activity=%(activity)s st=%(st)s et=%(et)s adep=%(adep)s" % gt


# task2str ---------------------------------------------------------------{{{2
def gt2str(gt):
    """For debug printouts ground_task."""
    return "udor=%(udor)s id=%(id)s activity=%(activity)s st=%(st)s et=%(et)s adep=%(adep)s" % gt


# pact_converter ========================================================={{{1
def pact_converter(dc, date=None):
    """Return PACTConverter object."""
    act_grp_cat(dc)
    return PACTConverter(dc, date)


# run ===================================================================={{{1
run = Main()


# main ==================================================================={{{1
main = run.main


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    main()


# Usage examples: ========================================================{{{1

### Convert a few codes from list
# convert_these = ['A34', 'B99']
# pc = pact_converter(dave_connector, date)
# result = Result()
# for x in crew_activity_list:
#    pc(x, result)
# print pc # print DIG ops (can be a long, long list)
# pc.store()
# print result

### Convert training activities
# pc = pact_converter(dave_connector, date)
# for x in ca_list:
#    if pc.is_convertable(x):
#       pc(x, dutycd=<duty_code>)
# pc.store()

### Run batch job (but with different driver than this)
# result = run(connect_string, schema_string, date, commit=True)

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

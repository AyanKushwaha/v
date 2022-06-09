#!/bin/env python

# [acosta:06/245@12:18] created

"""
Batch engine for the salary system.

Runs functions from within Mirador.

NOTE:
    These functions are not (probably forever) available from a command line
    environment:

        Salary runs involving Rave, e.g. PERDIEM, OVERTIME, ...

    This is because they use Rave evaluations, that are not available from
    within Mirador (it would be too much work to convert all rules.)

"""

# imports ================================================================{{{1
import logging
import utils.mdor
utils.mdor.start(__name__)

import os
import re
import sys
import time
from utils.TimeServerUtils import now
import utils.time_util as time_util

import salary.conf as conf

from optparse import OptionParser

from AbsTime import AbsTime
from tm import TM, TMC
from utils.exception import locator


__version__ = '$Revision$'


# exports ================================================================{{{1
__all__ = ['main', 'run', 'export', 'cancel', 'compdays', 'reset', 'undo']


# logging ================================================================{{{1
log = logging.getLogger('salary.batch')
log.setLevel(logging.INFO)


# UsageException ========================================================={{{1
class UsageException(Exception):
    msg = ''
    def __init__(self, msg):
        log.error("UsageException: %s", msg)
        self.msg = msg

    def __str__(self):
        return str(self.msg)

    def __repr__(self):
        return repr(self.msg)


# MyOptionParser ========================================================={{{1
class MyOptionParser(OptionParser):
    def __init__(self, additional_help=None, *a, **k):
        self.additional_help = additional_help
        OptionParser.__init__(self, *a, **k)

    def format_help(self, formatter=None):
        result = OptionParser.format_help(self, formatter)
        if self.additional_help:
            return result + self.additional_help
        else:
            return result


# BatchRunnerBase ========================================================{{{1
class BatchRunnerBase:
    def __init__(self, connect=None, schema=None, commit=True):
        self.connect = connect
        self.schema = schema
        self.commit = commit

    def __call__(self, *a, **k):
        if a:
            return self.main(*a)
        else:
            return self.run(**k)

        
# ExportMain ============================================================={{{1
class ExportMain(BatchRunnerBase):

    def main(self, *a):
        try:
            usage = (
                "batch {batch_opts} export [--help] [--format {CSV|HTML|FLAT|...}] "
                "[--spooldir directory] runid(s)"
            )
            description = "Create export file(s) for the given runid(s)."
            parser = OptionParser(usage=usage, description=description)
            parser.add_option("-f", "--format", dest="format", metavar="format",
                    help="Use the the selected output format (one of {%s}." % (', '.join(conf.allowedExportFormats)))
            parser.add_option("-s", "--spooldir", dest="spooldir", metavar="spooldir",
                    help="Directory to put output file(s) in. Default is $CARMDATA/EXPORT.")
            (opts, args) = parser.parse_args(list(a))
            if not args:
                log.error("%s: Incorrect number of arguments." % (locator(self),))
                parser.error("Incorrect number of arguments.")

            self.run(args, format=opts.format, spooldir=opts.spooldir)
        except Exception, e:
            log.error("%s: Exception: %s" % (locator(self), e))
            raise

    def run(self, runids, format=None, spooldir=None):
        do_connect(self.connect, self.schema)
        import salary.run as run

        if not format is None and format not in conf.allowedExportFormats:
            raise UsageException("Chosen export format is not allowed, can be one of %s." % (conf.allowedExportFormats,))

        for runid in runids:
            r = run.RunData.fromRunId(runid)
            if not spooldir is None:
                r.spooldir = spooldir
            if not format is None:
                r.format = format
            filename = run.export(r)
            log.info("Export file created - '%s'." % (filename,))


# CancelMain ============================================================={{{1
class CancelMain(BatchRunnerBase):

    def main(self, *a):
        try:
            usage = (
                "batch {batch_opts} cancel [--help] [-comment comment] "
                "[--export [--format {CSV|HTML|FLAT|...}] [--spooldir directory]]"
                "runid(s)"
            )
            description = "Cancel salary run by creating a new run with all entries negated."
            parser = OptionParser(usage=usage, description=description)
            parser.add_option("-c", "--comment", dest="comment", metavar="comment",
                    help= "Save the comment together with the run.")
            parser.add_option("-e", "--export", dest="export", action="store_true",
                    metavar="export", help= "Create an export file with the canceled run.")
            parser.add_option("-f", "--format", dest="format", metavar="format",
                    help=(
                        "Use the the selected output format (one of {%s}. "
                        "This option is only meaningful together with the --export option."
                        ) % ', '.join(conf.allowedExportFormats))
            parser.add_option("-s", "--spooldir", dest="spooldir", metavar="spooldir",
                    help=(
                        "Directory to put output file(s) in. Default is $CARMDATA/EXPORT. "
                        "This option is only meaningful together with the --export option."))
            (opts, args) = parser.parse_args(list(a))
            if not args:
                parser.error("Incorrect number of arguments.")

            return self.run(args, comment=opts.comment, export=opts.export, format=opts.format, spooldir=opts.spooldir)
        except SystemExit, se:
            pass
        except Exception, e:
            log.error("%s: Exception: %s" % (locator(self), e))
            raise

    def run(self, a, comment=None, export=False, format=None, spooldir=None):
        do_connect(self.connect, self.schema)
        # Notorious bug, tables must be loaded before newState()!
        TM(['salary_run_id', 'salary_basic_data'])
        import salary.run as run

        for runid in a:
            r = run.RunData.fromRunId(runid)
            try:
                if self.commit:
                    TM.newState()
                new_run_id = run.create_and_negate(r)
                if export:
                    filename = ExportMain().run(format=Format,
                            spooldir=spooldir, runids=(new_run_id,))
                    log.info("Export file created - '%s'" % (filename,))
                if self.commit:
                    TM.save()
            except:
                log.error("%s - failed." % (locator(self),))
                if self.commit:
                    TM.undo()
                raise


# CompDaysMain ==========================================================={{{1
class CompDaysMain(BatchRunnerBase):
    # NOTE: Since 090101 (see CR 249) no more F7S should go to payment for pilots.
    #chgmon = None # Monitor changes

    def main(self, *a):
        try:
            usage = (
                "usage: batch {batch_opts} compdays [--help] [--lastdate date]"
                " {F33GAIN|F7SGAIN|F31|F3S|RESET}"
            )
            description = "Convert different leave accounts."
            extra_help = '\n'.join((
                "",
                "One of the following arguments must be entered:",
                "F33GAIN",
                "    Increment 'F33', run monthly for all SKD/SKS pilots in VG.",
                "F7SGAIN",
                "    Increment 'F7S', run yearly for all cabin crew.",
                "F31",
                "    Convert 'F3' days to 'F31' days for long haul pilots. (Pilots with A330 or ",
                "    A340 qualification.)  Five 'F31' days will be given for each three 'F3' ",
                "    days.  At least two 'F3' days must remain after conversion.",
                "F3S",
                "    Convert 'F3' to 'F3S' for all pilots, to be run yearly. The conversion will ",
                "    stop when the level of the 'F3S' account becomes more than or equal to two ",
                "    days.",
                "RESET",
                "    Reset 'BOUGHT' and 'SOLD' accounts. This job will be run monthly.",
                "",
                "example:",
                "    batch.py compdays F33GAIN -l 20100501",

                "",
            ))
            parser = MyOptionParser(usage=usage, 
                    description=description, additional_help=extra_help)
            parser.add_option("-l", "--lastdate", dest="lastdate", metavar="lastdate",
                    help=(
                        "Use 'lastdate' as the highest date to convert to. "
                        "Default is the first day of next month."
                    ))
            parser.add_option("-a", "--accountdate", dest="accountdate", metavar="accountdate",
                    help=(
                        "Use 'accountdate' as the 'tim' value for account entries. "
                        "Overrides default value. Currently only valid for F33GAIN"
                    ))
            (opts, args) = parser.parse_args(list(a))
            if opts.lastdate:
                try:
                    lastdate = AbsTime(opts.lastdate)
                except:
                    parser.error("Incorrect format of lastdate.")
            else:
                lastdate = None
            if opts.accountdate:
                try:
                    accountdate = AbsTime(opts.accountdate)
                except:
                    parser.error("Incorrect format of accountdate.")
            else:
                accountdate = None
            if not args:
                parser.error("incorrect number of arguments.")

            self.run(conversion=args[0], hi=lastdate, accountdate=accountdate)
        except SystemExit, se:
            pass
        except Exception, e:
            log.error("%s: Exception: %s" % (locator(self), e))
            raise

    def run(self, conversion=None, **kwargs):
        if not self.commit:
            log.info("Will not save to DB (no-commit flag was given).")
            
        import salary.compconv

        if conversion is None:
            raise UsageException("no conversion given.")
        if conversion == 'F3S':
            convfunc = salary.compconv.F3_to_F3S
        elif conversion == 'F31':
            convfunc = salary.compconv.F3_to_F31
        elif conversion == 'F33GAIN':
            convfunc = salary.compconv.F33_gain
        elif conversion == 'F7SGAIN':
            convfunc = salary.compconv.F7S_gain
        elif conversion == 'RESET':
            convfunc = salary.compconv.bought_sold_reset
        else:
            raise UsageException("Conversion must be one of {F31, F3S, F33GAIN, F7SGAIN, RESET}.")

        do_connect(self.connect, self.schema)
        # Notorious bug, tables must be loaded before newState()!
        TM('account_entry', 'crew_employment', 'crew_qualification',
                'crew_contract', 'account_baseline', 'activity_set')
        try:
            #if self.chgmon:
            #    self.chgmon.pre()
            TM.newState()
            r = convfunc(**kwargs)
            #if self.chgmon:
            #    self.chgmon.post()
            if self.commit:
                log.debug("...saving") 
                TM.save()
                revid = TM.getSaveRevId()
                if revid > 0:
                    log.info("...saved with revid = '%s'." % revid)
                else:
                    log.info("...NOT saved - no changes were found!")
            else:
                log.info("...NOT saving (no-commit flag) was given.")
        except Exception, e:
            log.error("%s - failed. reason = %s" % (locator(self), e))
            if self.commit:
                TM.undo()
            raise

class ResetAccountMain(BatchRunnerBase):

    def main(self, *a):
        try:
            usage = (
                "usage: batch {batch_opts} reset [--help] [--lastdate date] [--reason text] "
                " [--region <rgn>] [--base <base>] [--maincat {F|C} [--subcat RP]] ACCOUNT1 ACCOUNT2 ..."
            )
            description = "Resets specific account balances on a specific date."
            parser = MyOptionParser(usage=usage, 
                    description=description)
            parser.add_option("-l", "--lastdate", dest="lastdate", metavar="lastdate",
                    help=(
                        "Use 'lastdate' as the highest date to convert to. "
                        "Default is the first day of the month."
                    ))
            parser.add_option("--region",
                dest="region",
                default=None,
                help="Crew region (e.g. SKN, SKD, SKS, SKI)")
            parser.add_option("--maincat",
                dest="maincat",
                default=None,
                help="Crew region (F or C)")
            parser.add_option("--subcat",
                              dest="subcat",
                              default=None,
                              help="Crew sub category (RP)")
            parser.add_option("--base",
                dest="base",
                default=None,
                help="Crew base (e.g. CPH)")
            parser.add_option("--reason",
                dest="reason",
                default=None,
                help="Reasoncode value for reset entries.")
            (opts, args) = parser.parse_args(list(a))
            if opts.lastdate:
                try:
                    lastdate = AbsTime(opts.lastdate)
                except:
                    parser.error("Incorrect format of lastdate.")
            else:
                lastdate = now().month_floor()
            if not args:
                parser.error("incorrect number of arguments.")
                
            if len(args) < 1:
                raise UsageException("Need at least one account")
            
            log.info("Will reset %s for maincat %s, subcat %s, region %s, base %s", ', '.join(args), opts.maincat or "all", opts.subcat or "all", opts.region or "all", opts.base or "all")
                
            filter = None
            stats = {'count':0, 'total':0}
            if opts.maincat or opts.region or opts.base:
                if opts.maincat and not opts.maincat in ("F","C"):
                    raise UsageException("Maincat must be either F or C")
                if opts.subcat:
                    if not opts.subcat in ["RP"]:
                        raise UsageException("Subcat must be RP")
                    if not opts.maincat in ["C"]:
                        raise UsageException("Subcat can only be RP when maincat is C")

                def is_in_subcat(ent):
                    if not opts.subcat:
                        return True
                    elif opts.subcat == "RP":
                        for crew_contract in ent.crew.referers('crew_contract', 'crew'):
                            ti = time_util.TimeInterval(crew_contract.validfrom, crew_contract.validto)
                            if ti.includes(lastdate):
                                if "Temp" in crew_contract.contract.desclong.split(' '):
                                    return True
                    else:
                        raise UsageException("Subcat must be RP")
                    return False

                def filter(ent):
                    stats['total'] += 1
                    for crew_emp in ent.crew.referers('crew_employment', 'crew'):
                        ti = time_util.TimeInterval(crew_emp.validfrom, crew_emp.validto)
                        if ti.includes(lastdate):
                            if not opts.maincat or (",%s,"%crew_emp.crewrank.maincat.id) in (",%s,"%opts.maincat):
                                if not opts.region or (",%s,"%crew_emp.region.id) in (",%s,"%opts.region):
                                    if not opts.base or (",%s,"%crew_emp.base.id) in (",%s,"%opts.base):
                                        if is_in_subcat(ent):
                                            stats['count'] += 1
                                            return True
                    return False

            self.run(lastdate=lastdate, accounts=args, reason=opts.reason, filter=filter)
            if stats['count'] or stats['total']:
                log.info("Filter applied: Processed %d out of %d entries", stats['count'], stats['total'])
        except SystemExit, se:
            pass
        except Exception, e:
            log.error("%s: Exception: %s" % (locator(self), e))
            raise

    def run(self, lastdate=None, accounts=None, reason=None, filter=filter):
        import salary.compconv

        log.info("Connecting to schema %s", self.schema)
        do_connect(self.connect, self.schema)
        # Notorious bug, tables must be loaded before newState()!
        log.info("Preloading tables")
        TM('account_entry', 'crew_employment', 'crew_qualification',
                'crew_contract', 'account_baseline', 'activity_set')
        try:
            #if self.chgmon:
            #    self.chgmon.pre()
            TM.newState()
            r = salary.compconv.reset_accounts(accounts, hi=lastdate, reason=reason, filter=filter)
            #if self.chgmon:
            #    self.chgmon.post()
            if self.commit:
                log.debug("...saving") 
                TM.save()
                revid = TM.getSaveRevId()
                if revid > 0:
                    log.info("...saved with revid = '%s'." % revid)
                else:
                    log.info("...NOT saved - no changes were found!")
            else:
                log.info("...NOT saving (no-commit flag) was given.")
        except Exception, e:
            log.error("%s - failed. reason = %s" % (locator(self), e))
            if self.commit:
                TM.undo()
            raise

class UndoAccountRunMain(BatchRunnerBase):

    def main(self, *a):
        try:
            usage = (
                "usage: batch {batch_opts} undo [--help] --date date"
                " [--source <src>] ACCOUNT1 ACCOUNT2 ..."
            )
            description = "Undo a specific account run."
            parser = MyOptionParser(usage=usage, 
                    description=description)
            parser.add_option("-d", "--date", dest="rundate", metavar="rundate",
                    help="The date of the original run")
            parser.add_option("--source",
                dest="source",
                default=None,
                help="Source text to match for (i.e. run name)")
            (opts, args) = parser.parse_args(list(a))
            if opts.rundate:
                try:
                    rundate = AbsTime(opts.rundate)
                except:
                    parser.error("Incorrect format of lastdate.")
            else:
                raise UsageException("Must specify run date")
            if not args:
                parser.error("incorrect number of arguments.")
                
            if len(args) < 1:
                raise UsageException("Need at least one account")
            
            log.info("Will undo run")
            stats = {'count':0, 'total':0}
            self.run(date=rundate, source=opts.source, accounts=args[1:])
            if stats['count'] or stats['total']:
                log.info("Filter applied: Processed %d out of %d entries", stats['count'], stats['total'])
        except SystemExit, se:
            pass
        except Exception, e:
            log.error("%s: Exception: %s" % (locator(self), e))
            raise

    def run(self, date=None, accounts=None, source=None):
        if not accounts:
            raise UsageException("No accounts specified")
        
        print date, accounts, source

        log.info("Connecting to schema %s", self.schema)
        do_connect(self.connect, self.schema)
        # Notorious bug, tables must be loaded before newState()!
        log.info("Preloading tables")
        src = ""
        if source:
            src = "(source=%s)" % source
        flt = "(&(|(account=%s))(tim=%s)%s)" % (')(account='.join(accounts), str(date), src)
        log.info("Using LDAP filter: %s" % flt)
        TM('account_entry')
        handled = 0
        TM.newState()
        for row in TM.account_entry.search(flt):
            row.remove()
            handled += 1
        log.info("Undid %d records" % handled)
        if self.commit:
            log.debug("...saving") 
            TM.save()
            revid = TM.getSaveRevId()
            if revid > 0:
                log.info("...saved with revid = '%s'." % revid)
            else:
                log.info("...NOT saved - no changes were found!")
        else:
            log.info("...NOT saving (no-commit flag) was given.")

# Main ==================================================================={{{1
class Main(object):
    commands = ['compdays', 'cancel', 'export', 'reset', 'undo']
    compdays = CompDaysMain
    cancel = CancelMain
    export = ExportMain
    reset = ResetAccountMain
    undo = UndoAccountRunMain

    def __init__(self, commit=True, debug=False):
        self.commit = commit
        self.debug = debug

    def __call__(self, connect, schema, command, *a, **k):
        if 'commit' in k:
            self.commit = k['commit']
        if 'debug' in k:
            self.debug = k['debug']
        if self.debug:
            log.setLevel(logging.DEBUG)
        if hasattr(self, command):
            return getattr(self, command)(connect=connect, schema=schema, commit=self.commit)(*a)
        raise UsageException("No such command: '%s'. Must be one of: %s" % (command, self.commands))

    def main(self, *argv):
        try:
            if len(argv) == 0:
                argv = sys.argv[1:]
            # Move global long options to the beginning
            if "--debug" in argv:
                del argv[argv.index("--debug")]
                argv.insert(0, "--debug")
            if "--nocommit" in argv:
                del argv[argv.index("--nocommit")]
                argv.insert(0, "--nocommit")
            _main_usage = """usage: batch --connect connect --schema schema SUBCOMMAND [subcommand_opts]"""
            _main_description = ("Start batch job with job parameters."
                "SUBCOMMAND can be one of %s." % (tuple(self.commands),))

            parser = OptionParser(usage=_main_usage, version="%%prog %s" % self.version,
                    description=_main_description)
            parser.add_option("-c", "--connect",
                dest="connect",
                help="Connect string to the database e.g. 'oracle:user/pass@service'.",
                metavar="connect")
            parser.add_option("-s", "--schema",
                dest="schema",
                help="Database schema to use.",
                metavar="schema")
            parser.add_option("-n", "--nocommit",
                action="store_false",
                dest="commit",
                default=not bool(os.environ.get("CMS_SALARY_NOCOMMIT", False)),
                help="Do not commit any changes.")
            parser.add_option("-d", "--debug",
                action="store_true",
                dest="debug",
                default=bool(os.environ.get("CMS_SALARY_DEBUG", False)),
                help="Show debug messages.")

            parser.disable_interspersed_args()
            (opts, args) = parser.parse_args(argv)
            self.debug = bool(os.environ.get("CMS_SALARY_DEBUG", False))
            self.commit = not bool(os.environ.get("CMS_SALARY_NOCOMMIT", False))
            self.debug = opts.debug
            self.commit = opts.commit

            if opts.connect is None or opts.schema is None:
                parser.error("Must give connection options 'connect' and 'schema'.")

            if not args:
                parser.error("incorrect number of arguments.")

            subfunc, subargs = args[0], args[1:]
            if not subfunc in self.commands:
                parser.error("First argument must be one of {%s}." % ', '.join(self.commands))
            self(opts.connect, opts.schema, subfunc, *subargs)

        except SystemExit, se:
            pass
        except UsageException, e:
            log.error("%s" % e)
            log.error("Run with --help for usage")

        except Exception, e:
            log.error("%s: Exception: %s" % (locator(self), e))

    @property
    def version(self):
        regexp = re.compile('\$' + 'Revision: (.*)' + '\$$')
        m = regexp.match(__version__)
        if m:
            return m.groups(0)
        else:
            return "0.0"


#-------------------------------------------------------------------------{{{2
def do_connect(connect, schema):
    global TM
    TM = TMC(connect, schema)


# run ===================================================================={{{1
run = Main()


# main ==================================================================={{{1
main = run.main


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    # Don't use sys.exit since this process will be run by Mirador.
    #sys.exit(main())
    main()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

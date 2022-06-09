#!/bin/env carmpython

# [acosta:07/088@09:35] upgrading fly-above or fly-below
# [acosta:07/334@16:45] Modified and modernized old script.

"""
Make some corrections of flight duties (below or above rank).

Usage:

$ carmpython above_below.py -v -c oracle:<schema>/<schema>@<database> -s <schema> <file.csv>

"""

script = "adhoc.above_below"

import logging

import os, sys, re
from optparse import OptionParser

from AbsTime import AbsTime

from utils.dave import EC, RW, txninfo
from utils.divtools import fd_parser
from utils.dutycd import dutycd2pos


# module variables ======================================================={{{1
__version__  = '$Revision$'


# exports ================================================================{{{1
__all__ = ['main', 'run']


# logging ================================================================{{{1
log = logging.getLogger(script)
logging.basicConfig(format="[%(levelname)-8s] %(message)s", level=logging.INFO)


# Main ==================================================================={{{1
class Main:
    def __init__(self):
        self.verbose = False
        self.nocommit = True
        self.altdate = False
        self.crewre = re.compile(r'SK\s*(\d+)')
        self._duties = {}
        self._firstdate = 0
        self._lastdate = 0
        self._warnings = 0

    def __call__(self, connect=None, schema=None, branch=None, verbose=False,
            nocommit=True, altdate=False, *a, **k):
        self.connect = connect
        self.schema = schema
        self.branch = branch
        self.verbose = verbose
        self.nocommit = nocommit
        self.altdate = altdate
        return self.run(*a, **k)

    def main(self, *argv):
        try:
            if len(argv) == 0:
                argv = sys.argv[1:]
            parser = OptionParser(version="%%prog %s" % self.version, 
                description=(
                    "Import CSV file with SAS dutycodes into Dave schema. "
                    "The CSV file has to use semicolon (;) as field separator."
                )
            )
            parser.add_option("-c", "--connect",
                dest="connect",
                help="Database connect string e.g. 'oracle:user/pass@service'.",
                metavar="connect")
            parser.add_option("-s", "--schema",
                dest="schema",
                help="Database schema.",
                metavar="schema")
            parser.add_option("-a", "--alternate-date",
                dest="altdate",
                help="Alternate date format: YYYY-MM-DD instead of default DD-MM-YYYY.",
                action="store_true")
            parser.add_option("-b", "--branch",
                dest="branch",
                help="Database branch.",
                metavar="schema")
            parser.add_option("-n", "--no-commit",
                dest="nocommit",
                help="Don't save any changes (no-commit).",
                action="store_true")
            parser.add_option("-v", "--verbose",
                dest="verbose",
                help="Verbose output.",
                action="store_true")
            (opts, args) = parser.parse_args(argv)
            log.debug("... (opts, args) = (%s, %s)" % (opts, args))
            if not args:
                parser.error("Incorrect number of arguments, must supply name of CVS file.")

            self.connect = opts.connect
            self.schema = opts.schema
            self.branch = opts.branch
            self.nocommit = opts.nocommit
            self.verbose = opts.verbose
            self.altdate = opts.altdate
            if self.connect is None or self.schema is None:
                parser.error("Must give connection options 'connect' and 'schema'.")

            # Call method that makes the changes.
            self.run(args)

        except SystemExit, s:
            pass
        except Exception, e:
            log.error("%s: Exception: %s" % (_locator(self), e))
            raise
        return 0

    def run(self, filenames):
        if self.verbose:
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.INFO)

        log.info("%s Rev %s - starting." % (script, self.version))
        try:
            for fn in filenames:
                self.read_file(fn)
            self.update_duties()
        except Exception, e:
            log.error(e)
            raise
        log.info('Finished.')

    def update_duties(self):
        L = [self.connect, self.schema]
        if not self.branch is None:
            L.append(self.branch)
        ec = EC(*L)
        rw = RW(ec)
        for cfd in ec.crew_flight_duty.search("leg_udor >= %d and leg_udor <= %d" % (
                self._firstdate, self._lastdate)):
            key = cfd['leg_udor'], cfd.leg_fd, cfd.leg_adep, cfd.crew
            if key in self._duties:
                z = cfd.copy()
                dutycode = self._duties[key][1]
                z['pos'] = dutycd2pos(cfd.pos, dutycode)
                rw.crew_flight_duty.dbupdate(z)
                fmt = "udor: %(leg_udor)s, fd: %(leg_fd)s, adep: %(leg_adep)s, crew: %(crew)s, pos: %(pos)s"
                log.debug('%s -> (%s) -> %s' % (fmt % cfd, dutycode, fmt % z))
        log.info("Previous commitid = %s." % ec.cid)
        revid = rw.apply()
        txn = txninfo(ec, revid)
        log.info("Saved with revid = %s and commitid = %s." % (revid, txn.commitid))

    def read_file(self, fn):
        log.debug("Reading file '%s'." % (fn,))
        line_counter = 0
        file = open(fn, 'r')
        for line in file:
            line_counter += 1
            # discard first line
            if line_counter == 1:
                continue
            try:
                (f, u, a, e, r, d) = line.split(';')
            except Exception, e:
                self.warning("Not enough fields", e, line_counter, line)
                continue
            d = d.rstrip(' \t\r\n')

            try:
                ff = fd_parser(f)
            except Exception, e:
                self.warning("Not a flight '%s'" % f, e, line_counter, line)
                continue
            fd = ff.flight_descriptor

            if self.altdate:
                (yy, mm, dd) = u.split("-")
            else:
                (dd, mm, yy) = u.split("-")

            udor = int(AbsTime(int(yy), int(mm), int(dd), 0, 0)) / 1440
            adep = a.strip()

            mo = self.crewre.match(e)
            if mo:
                crewid = mo.group(1)
            else:
                self.warning("Could not use crew '%s'" % e, None, line_counter, line)
                continue

            key = (udor, ff.flight_descriptor, adep, crewid)
            if  key in self._duties:
                self.warning("Duplicate key.", None, line_counter, line)
            self._duties[key] = r, d
            if udor > self._lastdate:
                self._lastdate = udor
            if self._firstdate == 0 or udor < self._firstdate:
                self._firstdate = udor

        file.close()

    def warning(self, txt, exc, lineno, line):
        self._warnings += 1
        log.warning(txt + " - skipping line %d [%s]" % (lineno, line))
        if exc is not None:
            log.warning("\t Exception: %s" % str(exc))

    @property
    def version(self):
        regexp = re.compile('\$' + 'Revision: (.*)' +  '\$$')
        m = regexp.match(__version__)
        if m:
            return m.group(1)
        else:
            return "0.0"


# _locator ==============================================================={{{1
def _locator(o):
    return "%s.%s.%s" % (o.__class__.__module__, o.__class__.__name__,
            sys._getframe(1).f_code.co_name)


# run ===================================================================={{{1
run = Main()


# main ==================================================================={{{1
main = run.main


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    main()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

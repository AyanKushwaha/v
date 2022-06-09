

"""
Convert up to 'max_entries' from crew_log_acc in one schema to new format of
crew_log_acc in another schema.
"""

import logging
import os
import subprocess

from optparse import OptionParser

from AbsTime import AbsTime
from Etab import Etable

from utils.dave import EC, RW


logging.basicConfig()
log = logging.getLogger('rfi51_converter')


TABLES = ('crew_log_acc', 'crew_log_acc_mod')


class MyIter:
    class Record:
        def __init__(self, parent, row):
            self.typ = row[parent.coldict['typ']]
            self.crew = row[parent.coldict['crew']]
            self.acfamily = row[parent.coldict['acfamily']]
            self.accyear = int(row[parent.coldict['accyear']])
            self.accmonth = int(row[parent.coldict['accmonth']])
            self.accvalue = int(row[parent.coldict['accvalue']])

    def __init__(self, etab):
        self.etab = etab
        self.coldict = {}
        for col in ('typ', 'crew', 'acfamily', 'accyear', 'accmonth',
                'accvalue'):
            self.coldict[col] = etab.getColumnPos(col) - 1

    def __iter__(self):
        for row in self.etab:
            yield self.Record(self, row)


class Main:
    def __call__(self, opts, *args):
        if opts.debug:
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.INFO)
        if opts.connect is None:
            raise ValueError("Must give option connect.")
        if opts.schema is None:
            raise ValueError("Must give option schema.")
        if int(opts.do_import) + int(opts.do_export) + int(opts.do_pass) > 1:
            raise ValueError("Only one of the options 'export', 'import' and 'pass-thru' can be used.")
        if opts.do_import:
            import_(opts.connect, opts.schema, opts.dir, opts.old_format)
        elif opts.do_export:
            export_(opts.connect, opts.schema, opts.dir)
        elif opts.do_pass:
            if opts.from_connect is None:
                raise ValueError("Must give option from-connect with pass-thru operation.")
            if opts.from_schema is None:
                raise ValueError("Must give option from-schema with pass-thru operation.")
            pass_thru(opts.connect, opts.schema, opts.from_connect, opts.from_schema)
        else:
            raise ValueError("No operation specified, can be one of 'export', 'import' and 'pass-thru'.")

    def main(self, *argv):
        rc = 0
        try:
            if len(argv) == 0:
                argv = sys.argv[1:]
            usage = '%prog {-i|-e|-p --from-schema=FROM_SCHEMA --to-schema=TO_SCHEMA}\n --connect=CONNSTR --schema=SCHEMA'
            parser = OptionParser(version='%%prog %s' % '$Revision$', usage=usage,
                    description=("RFI 51 support script. Move data from one schema to another"
                        "or dump crew_log_acc and crew_log_acc_mod and import."))
            parser.add_option("-c", "--connect",
                    dest="connect",
                    help=("Connect string to database to where data will be written."
                        " e.g. 'oracle:user/pass@service'."))
            parser.add_option("-s", "--schema",
                    dest="schema",
                    help="Database schema to use for import.")
            parser.add_option("--from-connect",
                    dest="from_connect",
                    help=("[pass-thru only] Connect string to database from where data will be read."
                        " e.g. 'oracle:user/pass@service'."))
            parser.add_option("--from-schema",
                    dest="from_schema",
                    help="[pass-thru only] Database schema to use for export.")
            parser.add_option("-d", "--debug",
                    action="store_true",
                    dest="debug",
                    default=False,
                    help="Show debug messages.")
            parser.add_option("-D", "--directory",
                    dest="dir",
                    default=".",
                    help="Etab file directory.")
            parser.add_option("-i", "--import",
                    action="store_true",
                    dest="do_import",
                    default=False,
                    help="Import from Etables.")
            parser.add_option("-e", "--export",
                    action="store_true",
                    dest="do_export",
                    default=False,
                    help="Export to Etables.")
            parser.add_option("-o", "--old-format",
                    action="store_true",
                    dest="old_format",
                    default=False,
                    help="Use old format.")
            parser.add_option("-p", "--pass-thru",
                    action="store_true",
                    dest="do_pass",
                    default=False,
                    help="Copy from one schema to another.")
            opts, args = parser.parse_args(argv)
            try:
                rc = self(opts, args)
            except ValueError, e:
                parser.error(str(e))
        except SystemExit, se:
            return rc
        except Exception, e:
            raise
            log.error("%s: Exception: %s" % ('RFI51 convert', e))
            return 2
        return rc


def export_(connect, schema, dir="."):
    carmrunner = os.path.join(os.environ['CARMSYS'], 'bin', 'carmrunner')
    pid = os.getpid()
    tmp_xml_name = "/tmp/rfi51.%d.xml" % pid
    f = open(tmp_xml_name, "w")
    print >>f, '<?xml version="1.0"?>'
    print >>f, '<etabdump version="0.8" defmode="ignore">'
    for table in TABLES:
        print >>f, '<map entity="%s" etab="%s"/>' % (table, table)
    print >>f, '</etabdump>'
    f.close()
    log.info("Creating Etables.")
    log.info("Using output dir '%s'." % dir)
    proc = subprocess.Popen([carmrunner, "etabdump", "-c", connect, "-s", schema,
        "-f", tmp_xml_name, dir])
    status = os.waitpid(proc.pid, 0)
    os.unlink(tmp_xml_name)
    log.info("Export finished.")


def import_(connect, schema, dir=".", old_format=False):
    log.info("Connecting to '%s' with schema '%s'." % (connect, schema))
    ec = EC(connect, schema)
    for table in TABLES:
        etab = Etable(os.path.join(dir, table + ".etab"))
        process(table, MyIter(etab), ec, old_format)
    log.info("Import finished.")


def pass_thru(to_connect, to_schema, from_connect, from_schema):
    to_ec = EC(to_connect, to_schema)
    from_ec = EC(from_connect, from_schema)
    log.info("Converting '%s' -> '%s'." % (from_schema, to_schema))
    for table in TABLES:
        process(table, getattr(from_ec, table), to_ec)
    log.info("Operation finished.")


def process(table, iterable, to_ec, old_format=False, max_nr=None):
    #max_nr = 1000
    log.info("Processing table '%s'." % table)
    rw = RW(to_ec)
    i = 0
    for e in iterable:
        if not max_nr is None and i > max_nr:
            break
        if old_format:
            new_rec = dict(
                crew=e.crew,
                typ=e.typ,
                acfamily=e.acfamily,
                accvalue=e.accvalue,
                accyear=e.accyear,
                accmonth=e.accmonth,
            )
        else:
            tim = int(AbsTime(e.accyear, e.accmonth, 1, 0, 0))
            new_rec = dict(
                crew=e.crew,
                typ=e.typ,
                acfamily=e.acfamily,
                accvalue=e.accvalue,
                tim=tim
            )
        getattr(rw, table).dbwrite(new_rec)
        i += 1
        if i % 1000 == 0:
            log.debug("...%07d records. (%s)" % (i, table))
    #if iterable.ec.inReadTxn():
    #    iterable.ec.endReadTxn()
    log.debug("Total: %07d records. (%s)" % (i, table))
    log.debug("Saving ...")
    cid = rw.apply()
    log.info("Saved with CID = (%s), (%d records)" % (cid, i))


run = Main()
main = run.main


if __name__ == '__main__':
    sys.exit(main())


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

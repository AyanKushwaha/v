
# [acosta:08/253@12:33] Created

"""
Update entity 'country' with updated ISO-3166 country codes.
"""

# imports ================================================================{{{1
import logging
import re
import sys
from tm import TM
from optparse import OptionParser


# module variables ======================================================={{{1
__version__ = '$Revision$'
console = logging.StreamHandler()
console.setFormatter(logging.Formatter('%(name)s: [%(levelname)-8s]: %(message)s'))
logging.getLogger('').handlers = []
log = logging.getLogger('adhoc.iso3166')
log.addHandler(console)
log.setLevel(logging.INFO)


# Main ==================================================================={{{1
class Main:
    def __init__(self):
        pass

    def __call__(self, filename):
        f = open(filename, 'r')
        for line in f:
            if line.startswith('#'):
                continue
            if line.strip() == '':
                continue
            id, long_id, nr_id, comment, name = [x.strip() for x in line.split('\t')]
            name = name[:48]

            try:
                rec = TM.country[(id,)]
                if rec.long_id != long_id:
                    log.info("Changing '%s' (long_id) '%s' -> '%s'." % (id, rec.long_id, long_id))
                    rec.long_id = long_id
                if rec.nr_id != nr_id:
                    log.info("Changing '%s' (nr_id) '%s' -> '%s'." % (id, rec.nr_id, nr_id))
                    rec.nr_id = nr_id
                if rec.name != name:
                    log.info("Changing '%s' (name) '%s' -> '%s'." % (id, rec.name, name))
                    rec.name = name
            except Exception, e:
                log.info("Adding country '%s, %s, %s, %s'." % (id, long_id, nr_id, name))
                rec = TM.country.create((id,))
                rec.long_id = long_id
                rec.nr_id = nr_id
                rec.name = name
        f.close()

    def main(self, *argv):
        try:
            if len(argv) == 0:
                argv = sys.argv[1:]
            parser = OptionParser(version="%%prog %s" % self.version,
                    description="Script to update country entity")
            parser.add_option('-f', '--file',
                    dest='file',
                    help='name of file with ISO-3166 codes')
            (opts, args) = parser.parse_args(list(argv))

            if opts.file is None:
                parser.error("The 'file' option is mandatory.")
            self(opts.file)

        except SystemExit, e:
            log.debug("Finished: %s" % str(e))
        except Exception, e:
            log.error("%s: Exception: %s" % (_locator(self), e))
            raise

    @property
    def version(self):
        regexp = re.compile('\$' + 'Revision: (.*)' + '\$$')
        m = regexp.match(__version__)
        if m:
            return m.groups(0)
        else:
            return "0.0"


# _locator ---------------------------------------------------------------{{{2
def _locator(o):
    return "%s.%s.%s" % (o.__class__.__module__, o.__class__.__name__,
            sys._getframe(1).f_code.co_name)


# run ===================================================================={{{1
run = Main()


# main ==================================================================={{{1
main = run.main


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    main('-f', '/users/acosta/iso3166-actual.txt')


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

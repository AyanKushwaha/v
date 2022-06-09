
# changelog {{{2
# [acosta:07/082@12:48] First version
# [acosta:07/127@15:23] Adapted for Mirador.
# }}}

"""
Interface X1/X2. Replicate Perkey and Name.
"""

import utils.mdor
utils.mdor.start(__name__, "replication.X12")


# imports ================================================================{{{1
import getopt
import logging
import os
import sys

from carmensystems.dig.jmq import jmq
from tm import TM, TMC
from utils.xmlutil import XMLDocument, XMLElement
from RelTime import RelTime


# exports ================================================================{{{1
__all__ = ['main', 'report']


# logging ================================================================{{{1
logging.basicConfig(format='%(asctime)s: %(module)s: %(levelname)s: %(message)s', level=logging.INFO)


# Classes ================================================================{{{1

# ACrew ------------------------------------------------------------------{{{2
class ACrew(list):
    def __init__(self, id, name, tup):
        list.__init__(self)
        self.id = id
        self.name = name
        self.append(tup)


# UsageException ---------------------------------------------------------{{{2
class UsageException(Exception):
    msg = ''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


# XML formatting classes ================================================={{{1
class crewMessage(XMLElement):
    def __init__(self, c):
        XMLElement.__init__(self)
        self['version'] = "1.8"
        self.append(XMLElement('messageName', "Replicate crew basic"))
        self.append(XMLElement('messageBody', crewEmpnoNameSnapshot(c)))


class crewEmpnoNameSnapshot(XMLElement):
    def __init__(self, crewlist):
        XMLElement.__init__(self)
        self['version'] = "1.8"
        for c in crewlist.keys():
            self.append(crew(crewlist[c]))


class crew(XMLElement):
    def __init__(self, ac):
        XMLElement.__init__(self)
        self.append(XMLElement('crewId', 'SK  ' + str(ac.id)))
        self.append(XMLElement('name', ac.name))
        self.append(crewEmpnoPeriods(ac))


class crewEmpnoPeriods(XMLElement):
    def __init__(self, ac):
        XMLElement.__init__(self)
        for period in ac:
            self.append(crewEmpnoPeriod(period))


class crewEmpnoPeriod(XMLElement):
    def __init__(self, p):
        XMLElement.__init__(self)
        (start, end, extperkey) = p
        self.append(XMLElement('startDate', "%04d-%02d-%02d"  % start.split()[:3]))
        if end is None:
            self.append(XMLElement('endDate'))
        else:
            # WP FAT-INT 127 - Exclusive validity periods
            end = end - RelTime(1)
            self.append(XMLElement('endDate', "%04d-%02d-%02d"  % end.split()[:3]))
        if extperkey is None:
            self.append(XMLElement('empno'))
        else:
            self.append(XMLElement('empno', extperkey))


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
    X12 -c connect_string -s schema [-b branch] [-o output_file] [-v] [-h]
        [-n mqserver -p mqport -k mqchannel -m mqmanager -q mqqueue
        -a [mqaltuser]]

    usage:
        -c  connect_string
        --connect connect_string
            Use this connect string to connect to database.

        -s  schema
        --schema schema
            Use this schema.

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
            Alternate user id for the MQ connection.

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
            (opts, args) = getopt.getopt(argv, "a:c:ho:s:vn:p:k:m:q:",
                [
                    "connect=",
                    "help",
                    "mqaltuser="
                    "mqchannel=",
                    "mqhost=",
                    "mqmanager=",
                    "mqport=",
                    "mqqueue="
                    "output=",
                    "schema=",
                    "verbose",
                ])
        except getopt.GetoptError, msg:
            raise UsageException(msg)

        for (opt, value) in opts:
            if opt in ('-h','--help'):
                print __doc__
                print main.__doc__
                return 0
            elif opt in ('-v', '--verbose'):
                options['verbose'] = True
            elif opt in ('-c', '--connect'):
                options['connect'] = value
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

        if 'mqqueue' in options:
            if verbose:
                logging.info("Output to MQ queue '%s'." % (options['mqqueue']))

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
                msg = jmq.Message(content=report(verbose))
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
                logging.info("Output to '%s'." % (options['output']))
            print >>of, report(verbose)
            of.close()

        else:
            if verbose:
                logging.info("Output to stdout.")
            print report(verbose)

        if verbose:
            logging.info("Finished.")

    except UsageException, err:
        logging.error(str(err))
        logging.info("for help use --help")
        return 2
    except Exception, e:
        logging.error(str(e))
        return 2

    return 0


# report -----------------------------------------------------------------{{{2
def report(verbose=False):
    """
    Returns the message as a long string.
    """

    #
    # Data structure:
    #
    # C = { ACrew1, ACrew2, ..., ACrewN }
    # The ACrew objects are "lists"
    #

    C = {}

    if verbose:
        logging.info("X1/X2 looking for crew...")
        counter = 1

    for crew in TM.crew_employment:
        if verbose:
            if counter % 1000 == 0:
                logging.info("crew_employment ... (%d)" % (counter))
            counter += 1
        T = (crew.validfrom, crew.validto, crew.extperkey)
        if C.has_key(crew.crew.id):
            C[crew.crew.id].append(T)
        else:
            C[crew.crew.id] = ACrew(crew.crew.id, crew.crew.logname, T)

    xdoc = XMLDocument(crewMessage(C))
    xdoc.encoding = 'iso-8859-1'
    return str(xdoc)


# main ==================================================================={{{1
if __name__ == '__main__':
    # sys.exit(main())
    main()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

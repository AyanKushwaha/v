"""
40.2 Passengers Prognosis Flown.

Reads IATA LDM message (AHM583) and updates flight_leg_pax.
"""

import re
from datetime import datetime
import time

import carmensystems.dig.framework.carmentime as carmentime
import carmensystems.dig.framework.dave as dave
from carmensystems.dig.framework.handler import MessageHandlerBase, CallNextHandlerResult
from carmensystems.dig.framework import errors
from carmensystems.dig.messagehandlers.dave import DaveContentType

# globals ================================================================{{{1
regex_line = re.compile(r'\r?\n')
regex_fd = re.compile(r'^([A-Z]{2,3}|[0-9][A-Z]{1,2}|[A-Z][0-9][A-Z]?)([0-9]{3,4})([A-Z]?)(/([0-2][0-9]|3[0-9]))?')
regex_fd_non_std = re.compile(r'^LDM\s+([A-Z]{2,3}|[0-9][A-Z]{1,2}|[A-Z][0-9][A-Z]?)([0-9]{3,4})([A-Z]?)(/([0-2][0-9]|3[0-9]))?')
regex_pax = re.compile(r'^-([A-Z]{3}).*(\.PAX/([^\.]+)).*$')
svc_classes = ('C', 'M', 'Y')


class LDMHandler(MessageHandlerBase):
    """ Handles 'LDM' messages from SAS PCI system. """
    def __init__(self, name=None):
        super(LDMHandler, self).__init__(name)

    def handle(self, message):
        try:
            self._services.logger.debug("Received message of type %s" % (message.contentType))
            p = LDMParser(message.content, self._services.getDaveConnector(), self._services.now(), self._services.logger)
        except Exception, e:
            raise errors.MessageError("Failed parsing LDM message: %s" % e)
        message.setContent((None, None, p.operations()), DaveContentType())
        return CallNextHandlerResult()


class LDMParser:
    """ Separated code to make basic tests a little easier. """
    def __init__(self, data, connector, now, logger):
        self.ops = []
        self.lineno = 0
        self.lines = regex_line.split(data)
        self.now = now
        # WP FAT-INT 272: Some messages seem to be split up in a non-standard
        # fashion. Concatenate lines starting with "." with the previous line.
        for idx in range(len(self.lines)):
            while idx+1<len(self.lines) and self.lines[idx].startswith("-") and self.lines[idx+1].startswith("."):
                self.lines[idx] = self.lines[idx] + self.lines[idx+1]
                logger.debug("Concatenated line %s" % self.lines[idx+1])
                del self.lines[idx+1]

        if not self.lines[self.lineno].startswith('LDM'):
            raise errors.MessageError("Not an LDM message (does not start with 'LDM').%s" % self._line())

        if self.lines[self.lineno].strip() == 'LDM':
            self.lineno += 1
            udor, fd = self.get_match(regex_fd)
        else:
            # Try non-standard SAS "extension" to AHM 583, i.e. LDM is *not* on
            # a line of it's own.
            try:
                udor, fd = self.get_match(regex_fd_non_std)
            except:
                # BZ 37725: Try to resolve 'LDM     COR*' type of messages
                self.lineno += 1
                if len(self.lines) > self.lineno:
                    udor, fd = self.get_match(regex_fd)
                else:
                    raise

        for line in self.lines[self.lineno:]:
            if not line:
                break
            if line.startswith("SI"):
                # Discard supplementary information block
                break
            if line.startswith("-"):
                # PAX info could come on this line
                m = regex_pax.match(line)
                if m:
                    (ades, _, pax) = m.groups()
                    # Get ADEP for the leg.
                    search = dave.DaveSearch('flight_leg', [
                        ('fd', 'LIKE', fd[:9] + '_'),
                        ('udor', '=', udor),
                        ('ades', '=', ades),
                    ])
                    for leg in connector.runSearch(search):
                        adep = leg['adep']
                        if leg['fd'] != fd:
                            logger.debug("Found diverted leg %s" % (leg['fd']))
                            fd = leg['fd']
                        break
                    else:
                        logger.error("Could not find any flight with fd='%s', udor='%s' and ades='%s'.%s" % (fd, carmentime.fromCarmenDate(udor), ades, self._line()))
                        break

                    # Get PAX info
                    svcs = {}
                    i = 0
                    for s in pax.split("/"):
                        try:
                            svcs[svc_classes[i]] = int(s)
                        except:
                            if i >= len(svc_classes):
                                raise errors.MessageError("[PAX/%s] Got too many service classes, expected no more than '%d'.%s" % (pax, len(svc_classes), self._line()))
                            else:
                                raise errors.MessageError("[PAX/%s] The PAX value (%s) for service class '%s' is not a valid number.%s" % (pax, s, svc_classes[i], self._line()))
                        i += 1

                    # Add info for all classes even if there are no passengers
                    for svc in svc_classes:
                        self.ops.append({
                            'leg_udor': udor,
                            'leg_fd': fd,
                            'leg_adep': adep,
                            'svc': svc,
                            'apax': svcs.get(svc, 0),
                        })
            self.lineno += 1

    def __str__(self):
        """ for basic tests """
        return '\n'.join(
            ['\n'.join(
                (
                    '---',
                    'udor  :  %d (%s)' % (x['leg_udor'], carmentime.fromCarmenDate(x['leg_udor'])),
                    'fd    :  [%(leg_fd)s]' % (x),
                    'adep  :  [%(leg_adep)s]' % (x),
                    'svc   :  [%(svc)s]' % (x),
                    'apax  :  [%(apax)s]' % (x),
                )) for x in self.ops])

    def get_match(self, regex):
        m = regex.match(self.lines[self.lineno])
        if m:
            (carrier, number_, suffix, _, udor_) = m.groups()
            number = int(number_)
            if udor_ is None:
                raise errors.MessageError("The LDM message does not contain any valid UDOR, cannot continue.%s" % self._line())
            dd_udor = int(udor_)
            fd = "%-3.3s%06d%-1.1s" % (carrier, number, suffix)
            yy_udor = self.now.year
            mm_udor = self.now.month
            dd = self.now.day
            if dd < dd_udor:
                if mm_udor == 1:
                    mm_udor = 12
                    yy_udor -= 1
                else:
                    mm_udor -= 1
            try:
                udor = carmentime.toCarmenDate(datetime(yy_udor, mm_udor, dd_udor))
            except:
                raise errors.MessageError("Invalid day of month '%d' found in message.%s" % (dd_udor, self._line(),))
        else:
            raise errors.MessageError("Could not find flight descriptor in message.%s" % (self._line(),))
        return udor, fd

    def operations(self):
        return [dave.createOp('flight_leg_pax', 'W', x) for x in self.ops]

    def _line(self):
        return "\n%06d [%s]" % (self.lineno + 1, self.lines[self.lineno])


# notes =================================================================={{{1
# [acosta:07/179@15:20] This is how I interpret IATA AHM 583:
#
# The message must start with a line on it's own with the letters LDM.
#
# The flight number will come on the second line, hopefully followed by the
# date of origin (as day-of-month). (e.g. SK345/12)
#
# NOTE: To send the UDOR is not mandatory (and will crash the import if not
# there).
#
# Each line containing (possible) PAX information will start with '-'. The
# following three letters are the airport of destination (ADES).  The PAX info
# starts with the combination '.PAX' and contains any group of service class
# info preceded by '/' (e.g. -BKK[...].PAX/0/12/32.[...])
#
# A line starting with 'SI' will tell that supplementary information will
# follow. No Last Minute Change records (LMC) are read.
#
# Example:
#
#LDM
#SK973/23.OYKBA.3433A.2/7
#-SIN.126/5/0.T23022.1/3423.2/5750.3/8120.4/4464.5/1265.PAX/17/3/111.PAD/4/0/0.HEA/12LR/290.HEA/14P/525.HEA/32P/1660.PER/33P.RMD/42LR.RMD/42LR.RMD/42LR.RMD/42LR
#SI SIN    C  6634  M      0  B 104/   1560  O      0  T  13046       BP   43L/33/495 43R/22/330                                     
#BP CAN EX. CPH IS AT PSN 43R
#BP CAN EX. BKK IS AT PSN 43L

# Bugzilla #21160 brought to attention that SAS probably uses non-standard LDM messages, these will start with
# LDM, but not on a line of its own.


"""
Various dig handlers for flight leg extended suffix handling
"""
__docformat__ = 'restructuredtext en'
__metaclass__ = type

# imports ================================================================{{{1
import re
import carmensystems.dig.framework.dave as dave
from carmensystems.dig.framework.handler import MessageHandlerBase, CallNextHandlerResult
from carmensystems.dig.framework import errors, utils, carmentime

metaNewRerouteLegs = "carmensystems.dig.messagehandlers.aircrew.NewRerouteLegs"

# Message Handlers ======================================================={{{1
# AttributeRemover ======================================================={{{2
class AttributeRemover(MessageHandlerBase):
    """
    Removes flight duty attributes from rerouted legs. (See BZ 32578)
    This handler depends on rerouted leg information stored as channel
    metadata in key metaNewRerouteLegs. This info is filled in by the
    SSIM parser. For more information on SSIM parser and extended suffix
    handling see standard DIG documentation.

    Arguments:
        attributes      Comma separated list of attributes to be removed.
                        Default "TRAINING"
    """
    def __init__(self, attributes="TRAINING", name=None):
        super(AttributeRemover, self).__init__(name)
        self.attributes = attributes.split(",")

    def handle(self, message):
        if metaNewRerouteLegs in message.metadata:
            if len(message.metadata[metaNewRerouteLegs]) > 0:
                udor, fd, adep = message.metadata[metaNewRerouteLegs][0]
                for attr in self.attributes:
                    search = dave.DaveSearch("crew_flight_duty_attr", [
                        ("cfd_leg_udor", "=", udor),
                        ("cfd_leg_fd", "=", fd),
                        ("cfd_leg_adep", "=", adep),
                        ("attr", "=", attr),
                    ])
                    nAttr = 0
                    for attr_rec in self._services.getDaveConnector().runSearch(search):
                        message.content[2].append(dave.createOp('crew_flight_duty_attr', 'D', attr_rec))
                        nAttr += 1
                    if nAttr > 0:
                        self._services.logger.info("Removed %d crew flight duty %s attributes from fd=%s udor=%d adep=%s" % (nAttr, attr, fd, udor, adep))

        return CallNextHandlerResult()


# DigxmlSuffixBlaster ===================================================={{{2
class DigxmlSuffixBlaster(MessageHandlerBase):
    """
    Extended suffix handler for digxml (introduced for BZ 32636)
    Replaces original suffix in flight descriptor with extended suffix for 
    diverted legs.
    """
    def __init__(self, name=None):
        super(DigxmlSuffixBlaster, self).__init__(name)

        self.entrex = re.compile(r'<([a-z]*) entity=\"(\w*)\".*?</\1>', re.DOTALL)
        self.fdrex = re.compile(r'leg_fd\">\s*<string>(.*)</string>')
        self.adeprex = re.compile(r'leg_adep\">\s*<string>(.*)</string>')
        self.adesrex = re.compile(r'<value name=\"leg_ades\">\s*<string>(.*)</string>\s*</value>')
        self.udorrex = re.compile(r'leg_udor\">\s*<date>(.*)</date>')

    def handle(self, message):
        self.seqno = -1
        self.skipidx = []

        self.adep = self.adeprex.findall(message.content)
        self.ades = self.adesrex.findall(message.content)
        self.udor = self.udorrex.findall(message.content)
        self.fd = self.fdrex.findall(message.content)

        if len(self.ades) == 0:
            self._services.logger.debug("Suffix replacement not possible - attribute 'leg_ades' not available")
            # Skip updating flight_leg_message if referred leg does not exist
            msgrep = self.entrex.sub(self.skipMessage, message.content)
            message.setContent(msgrep, message.contentType)
            return CallNextHandlerResult()
        if len(self.ades) <> len(self.adep):
            self._services.logger.warning("Suffix replacement not possible - attribute 'leg_ades' not found in all records")
            return CallNextHandlerResult()
        
        # Replace flight descriptor
        msgrep = self.fdrex.sub(self.repl, message.content)
        # Remove attribute 'leg_ades' from the digxml
        msgrep = self.adesrex.sub("", msgrep)
        # Skip updating if referred leg does not exist
        self.seqno = -1
        msgrep = self.entrex.sub(self.skipPax, msgrep)

        message.setContent(msgrep, message.contentType)
        return CallNextHandlerResult()

    def repl(self, mo):
        self.seqno += 1
        # Do lookup here to get all legs matching the fd regardless of suffix
        try:
            fd = mo.group(1)
            search = dave.DaveSearch("flight_leg", [
                     ('fd', 'LIKE', fd[:9] + '_'),
                     ('udor', '=', carmentime.convertDate(self.udor[self.seqno])),
                     ('adep', '=', self.adep[self.seqno]), ])
            legfound = False
            for leg in self._services.getDaveConnector().runSearch(search):
                # Use suffix of leg matching the ades
                if leg['ades'] == self.ades[self.seqno]:
                    if leg['fd'] != fd:
                        self._services.logger.info("Found diverted leg %s" % (leg['fd']))
                    fd = leg['fd']
                    legfound = True
                    break
            if not legfound:
                self._services.logger.warning("Leg not found fd=%s adep=%s udor=%s ades=%s" % (fd, self.adep[self.seqno], self.udor[self.seqno], self.ades[self.seqno]))
                self.skipidx.append(self.seqno)
        except Exception, e:
            raise errors.MessageError("Failed replacing fd: %s" % str(e))
        return mo.group(0).replace(mo.group(1), fd)

    def skipPax(self, mo):
        self.seqno += 1
        try:
            if mo.group(2) == 'flight_leg_pax' and self.seqno in self.skipidx:
                self._services.logger.info("Skipping flight_leg_pax for %s/%s %s-%s" % (self.fd[self.seqno],self.udor[self.seqno],self.adep[self.seqno],self.ades[self.seqno]))
                return ""
        except Exception, e:
            raise errors.MessageError("Failed skipping flight_leg_pax: %s" % str(e))
        return mo.group(0)

    def skipMessage(self, mo):
        self.seqno += 1
        try:
            if mo.group(2) == 'flight_leg_message':
                search = dave.DaveSearch("flight_leg", [
                        ('fd', '=', self.fd[self.seqno]),
                        ('udor', '=', carmentime.convertDate(self.udor[self.seqno])),
                        ('adep', '=', self.adep[self.seqno]), ])
                legfound = False
                for leg in self._services.getDaveConnector().runSearch(search):
                    legfound = True
                    break
                if not legfound:
                    self._services.logger.warning("Leg not found fd=%s adep=%s udor=%s" % (self.fd[self.seqno], self.adep[self.seqno], self.udor[self.seqno]))
                    self._services.logger.info("Skipping flight_leg_message for %s/%s %s" % (self.fd[self.seqno],self.udor[self.seqno],self.adep[self.seqno]))
                    return ""
        except Exception, e:
            raise errors.MessageError("Failed skipping flight_leg_message: %s" % str(e))
        return mo.group(0)

# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=0:
# eof

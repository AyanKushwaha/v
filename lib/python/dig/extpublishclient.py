"""
This module contains functionality for re-publishing crew affected by
certain events reported by external interfaces:
    * Flight schedule time changes
    * Rotation changes that might affect meal stop calculations.
    * Rerouted legs
    * Arrived legs
For more information about this functionality please refer to RFI 54.

The process of re-publishing crew is designed as a client-server
solution where this module contains components used by the client side
only. The client issues re-publication orders to the batch studio server 
process by means of the PublicationHandler, adding entries to table 
crew_ext_publication. 

The batch studio process removes the crew_ext_publication entries when 
publication is committed. It uses the modcrew module to get the list of
crew to publish.
"""
__author__ = "Kenneth A, Jeppesen Systems"
__docformat__ = 'restructuredtext en'
__metaclass__ = type

# imports ================================================================{{{1
import datetime, time
from AbsTime import AbsTime
from carmensystems.dig.framework.handler import MessageHandlerBase, CallNextHandlerResult
from carmensystems.dig.framework import errors, utils, carmentime, dave
from carmensystems.dig.messagehandlers.dave import DaveContentType
from carmensystems.dig.messagehandlers.aircrew import metaNewRerouteLegs
from carmensystems.dig.messagehandlers.ssim import SSIMHandler
from dig.opusxmlparser import OPUSParser, metaRotationChangeLegs, metaArrivalLegs
from dig.dispatchers import metaDispatchedHandler

# Message Handlers ======================================================={{{1
# PublicationHandler ====================================================={{{2
class PublicationHandler(MessageHandlerBase):
    """ This handler issues re-publication orders for crew affected by the
        following flight events:
          * Flight schedule time changes
          * Rotation changes that might affect meal stop calculations.
          * Rerouted legs
          * Arrived legs
        Re-publication orders are issued by creating entries in table
        crew_ext_publication. The handler should be placed in the DIG 
        channel between the handler that detects the events and a DaveWriter.
    """
    def __init__(self, name=None):
        super(PublicationHandler, self).__init__(name)

    def handle(self, message):
        if not isinstance(message.contentType, DaveContentType):
            raise errors.MessageError("Expected message of DaveContentType")

        pubEntries = set(self._getScheduleTimeEntries(message) + \
                         self._getRotationEntries(message) + \
                         self._getArrivalEntries(message) + \
                         self._getRerouteEntries(message))

        src, trid, ops = message.content
        for crew,udor in pubEntries:
            op = createPubOrder(crew, udor, self._services)
            if not op is None:
                ops.append(op)

        return CallNextHandlerResult()

    def _getScheduleTimeEntries(self, message):
        """ Lookup and return crew affected by legs with changed schedule
            time.
        """
        entries = []
        # Schedule time changes is only recorded by the SSIM parser 
        parser = message.metadata.get(metaDispatchedHandler, None)
        if parser != SSIMHandler.__name__:
            return []
        self._services.logger.debug("Looking for schedule time changes")
        # Extract legs with updated sobt/sibt from list of dave operations
        # written by the SSIMParser. A more sophisticated implementation
        # would be to communicate a list of legs through message metadata
        # in analogy with rerouted legs, however that would require changes
        # to the CARMSYS.
        src, trid, ops = message.content
        for op in ops:
            # Here we catch updates from any ASM/TIM and SSM/TIM message
            # that may have changed scheduled times.
            if op.entity == "flight_leg" and \
               (isinstance(op, dave.UpdateDaveOperation) or isinstance(op, dave.WriteDaveOperation)) and \
               (op.values.has_key('sobt') or op.values.has_key('sibt')):
                # Skip if activity is not within tracking period
                if not isWithinTrackingPeriod(op.values['udor'], self._services):
                    self._services.logger.info("Skipping publication for fd=%s adep=%s udor=%s - outside tracking period" % (op.values['fd'], op.values['adep'], carmentime.fromCarmenTime(op.values['udor']*1440).strftime("%Y%m%d")))
                    continue
                # Check if scheduled time has changed
                leg = self.__getLegFromDb(op.values['udor'], op.values['fd'], op.values['adep'])
                if not leg is None:
                    if op.values.has_key('sobt') and op.values['sobt'] != leg['sobt'] or \
                       op.values.has_key('sibt') and op.values['sibt'] != leg['sibt']:
                        for crew in self.__searchCrewByLeg(op.values['udor'], op.values['fd'], op.values['adep']):
                            entries.append((crew, op.values['udor']))
        return entries

    def _getRotationEntries(self, message):
        """ Lookup and return crew affected by rotation changes. """
        entries = []
        # Rotation changes is only recorded by the OPUS parser 
        parser = message.metadata.get(metaDispatchedHandler, None)
        if parser != OPUSParser.__name__:
            return []
        self._services.logger.debug("Looking for rotation changes")

        if not metaRotationChangeLegs in message.metadata:
            raise errors.MessageError("Expected metadata key metaRotationChangeLegs")

        for udor,fd,adep in message.metadata[metaRotationChangeLegs]:
            # Skip if activity is not within tracking period
            if not isWithinTrackingPeriod(udor, self._services):
                self._services.logger.info("Skipping publication for fd=%s adep=%s udor=%s - outside tracking period" % (fd, adep, carmentime.fromCarmenTime(udor*1440).strftime("%Y%m%d")))
                continue
            for crew in self.__searchCrewByLeg(udor,fd,adep):
                entries.append((crew,udor))
        return entries

    def _getArrivalEntries(self, message):
        """ Lookup and return crew affected by arrivals. """
        entries = []
        # Leg arrivals are only recorded by the OPUS parser 
        parser = message.metadata.get(metaDispatchedHandler, None)
        if parser != OPUSParser.__name__:
            return []
        self._services.logger.debug("Looking for leg arrivals")

        if not metaArrivalLegs in message.metadata:
            raise errors.MessageError("Expected metadata key metaArrivalLegs")

        for udor,fd,adep in message.metadata[metaArrivalLegs]:
            for crew in self.__searchCrewByLeg(udor,fd,adep):
                entries.append((crew,udor))
        return entries

    def _getRerouteEntries(self, message):
        """ Lookup and return crew affected by return-to-ramp and
            diversions. 
        """
        entries = []
        self._services.logger.debug("Looking for reroute changes")
        if not metaNewRerouteLegs in message.metadata:
            self._services.logger.debug("Metadata key metaNewRerouteLegs not found")
            return []

        if len(message.metadata[metaNewRerouteLegs]) > 0:
            udor, fd, adep = message.metadata[metaNewRerouteLegs][0]
            # Skip if activity is not within tracking period
            if not isWithinTrackingPeriod(udor, self._services):
                self._services.logger.info("Skipping publication for fd=%s adep=%s udor=%s - outside tracking period" % (fd, adep, carmentime.fromCarmenTime(udor*1440).strftime("%Y%m%d")))
                return entries
            for crew in self.__searchCrewByLeg(udor,fd,adep):
                entries.append((crew,udor))
        return entries

    def __searchCrewByLeg(self, udor, fd, adep):
        crewlist = []
        search = dave.DaveSearch("crew_flight_duty", [
                ("leg_fd", "=", fd),
                ("leg_udor", "=", udor),
                ("leg_adep", "=", adep),
        ])
        for cfd in self._services.getDaveConnector().runSearch(search):
            crewlist.append(cfd["crew"])
        self._services.logger.info("Found crew for fd=%s adep=%s udor=%d : %s" % (fd,adep,udor,crewlist))
        return crewlist

    def __getLegFromDb(self, udor, fd, adep):
        search = dave.DaveSearch("flight_leg", [
                ("fd", "=", fd),
                ("udor", "=", udor),
                ("adep", "=", adep),
        ])
        for leg in self._services.getDaveConnector().runSearch(search):
            return leg
        return None


# Functions =============================================================={{{1
# createPubOrder ========================================================={{{2
def createPubOrder(crew, udor, services):
    """ Returns a crew publication order in the form of a Dave operation.
        This function is designed to be used from any DIG message handler
        from which external crew publication orders should be issued.
    """
    logtime = carmentime.toCarmenTime(services.now())
    conn = services.getDaveConnector()
    id = conn.getL1Connection().getNextSeqValue('seq_ext_pub')
    services.logger.debug("Publication order for crew=%s udor=%d id=%d" % (crew,udor,id))
    op = dave.createOp('crew_ext_publication', 'W', {
        'id': id,
        'crew': crew,
        'udor': udor,
        'logtime': logtime,
    })
    return op

# isWithinTrackingPeriod ================================================={{{2
def isWithinTrackingPeriod(udor, services=None):
    """ Returns True if activity udor is not greater than end of tracking
        period. End of tracking period as end of current month if date is
        1-15, else end of next month.
    """
    if services is None:
        now = datetime.datetime.utcnow()
    else:
        now = services.now()
    tnow = AbsTime(carmentime.toCarmenTime(now))
    tend = tnow.month_ceil()
    if tnow.split()[2] > 15:
        tend = tend.addmonths(1)
    return (AbsTime(udor*1440) <= tend)


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=0:
# eof

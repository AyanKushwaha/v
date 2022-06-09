"""
SAS OPUS (MVT/ROT) XML message parser
"""
from utils.divtools import fd_parser
from carmensystems.basics.uuid import uuid
from xml.sax import handler, parseString
from carmensystems.dig.framework.handler import MessageHandlerBase,CallNextHandlerResult
from carmensystems.dig.framework import dave
from carmensystems.dig.framework import carmentime
from carmensystems.dig.framework import errors
from carmensystems.dig.framework import utils
from carmensystems.dig.messagehandlers.aircrew import metaNewRerouteLegs
from carmensystems.dig.messagehandlers.dave import DaveContentType

metaRotationChangeLegs = "dig.externalpublish.RotationChangeLegs"
metaArrivalLegs = "dig.externalpublish.ArrivalLegs"

readDateTime=carmentime.convertIsoTime
readDate=carmentime.convertDate

def readYYMMDD(date):
    return carmentime.convertDate("%d-%02d-%02d" % (2000+int(date[0:2]),int(date[2:4]),int(date[4:6])))

# Read all flights with 
def readFlightLeg(parser, legKey):
    # Read flight from DB (required for suffix generation)
    search = dave.DaveSearch("flight_leg",
         [("udor", '=', legKey["udor"]),
          ("fd", '=', legKey["fd"]),
          ("adep", '=', legKey["adep"])])
    for result in parser._services.getDaveConnector().runSearch(search):
        return result
    return None

# --- Message handlers ---

class TypeFoundException(Exception):
    def __init__(self,name):
        self.name = name

class MsgVerifier(handler.ContentHandler):
    def __init__(self):
        handler.ContentHandler.__init__(self)

    def startElement(self, name, attrs):
        raise TypeFoundException(name)


class OPUSMVTHandler(handler.ContentHandler):
    def __init__(self, parser):
        handler.ContentHandler.__init__(self)
        self.parser = parser
        self.alwaysCreateFlightLegs = False
        self.RTRSuffixes = ("M","N","O","P","Q","R","T","U","V","X","Y")

        # mappings
        self.leg = None
        self.duty = None
        self.legDelay = None
        self.legRTR = None
        self.parser.legOrg = None
        self.lastFlightLeg = None
        self.trainingInfo = None
        self.crewLandingInfo = None
        self.legRef = {}

        # flags
        self.delayedDepActive = False

        self.actionId = None
        self.subAction = None
        self.skip = False

    def startElement(self, name, attrs):
        self.currElement = name
        #for aname in attrs.getNames():
        #    pass
        if name == "mvt" or self.skip:
            # Top node
            # Improvement?: Read version attribute
            pass

        elif name == "flightLeg":
            # Create new leg/duty
            self.leg = {}
            self.duty = {}
            self.legRTR = {}
            self.parser.legOrg = None
            # Special handling, depending on actionId
            if self.actionId == "DEP":
                if self.subAction != "COR":
                    self.leg["statcode"] = "D"
            elif self.actionId in ("ARR", "TRA", "NRD"):
                self.leg["statcode"] = "A"
            elif self.actionId == "RTR" and self.subAction != "COR":
                self.leg["statcode"] = "S" # This leg get status S - scheduled, a new leg is created with status R and adep=ades, later
            elif self.actionId == "DIV":
                self.leg["statcode"] = "I"
            elif self.actionId == "DAD": # Delete Actual Data
                if self.subAction == "ATD":
                    self.leg["statcode"] = "S"
                    self.leg["aobt"] = None
                    self.leg["atot"] = None
                elif self.subAction == "ATA":
                    self.leg["statcode"] = "D"
                    self.leg["aibt"] = None
                    self.leg["aldt"] = None
                elif self.subAction == "RTR":
                    self.leg["aibt"] = None
                    self.leg["aobt"] = None

        elif name == "delays":
            # delays will contain 0-n 'delayedDeparture' nodes
            # delete all previous delay information.
            legDelayKey = {
                "leg_udor": self.leg["udor"],
                "leg_fd": self.leg["fd"],
                "leg_adep": self.leg["adep"],
            }
            self.parser._services.logger.debug("deleting legDelay %s record" % legDelayKey)
            self.parser.makeRecord("flight_leg_delay", "D", legDelayKey)

        elif name == "delayedDeparture":
            self.delayedDepActive = True
            self.legDelay = {}

        elif name == "student":
            self.crewLandingInfo = {}

        elif name == "trainingInfo":
            self.trainingInfo = {}

    def endElement(self, name):
        self.currElement = ""
        if name == "mvt":
            # End of message
            if self.skip:
                self.parser._services.logger.debug("Leg skipped - clearing database operations")
                self.parser.ops = []

        elif name == "flightLeg":
            # [acosta:07/033@13:17] Save last leg for training block
            self.lastFlightLeg = {
                "leg_udor": self.leg["udor"],
                "leg_fd": self.leg["fd"],
                "leg_adep": self.leg["adep"],
            }

            if self.actionId == "DEL" and self.parser.legOrg is not None:
                etd = self.leg["eobt"]
                # Update eta with delay in case of DEL, ie. new etd + (sta - std).
                self.leg["eibt"] = etd + (self.parser.legOrg["sibt"] - self.parser.legOrg["sobt"])
                                                                                                                  
            # BZ 29289 KA: Check first that leg exists, before attempt to update
            legKey = { "udor": self.leg["udor"],
                       "fd": self.leg["fd"],
                       "adep": self.leg["adep"],
            }
            self.legRef = readFlightLeg(self.parser, legKey)
            if self.legRef is None:
                self.skip = True
                self.parser._services.logger.warning("%s: Unable to find original flight: %s" % (self.actionId, legKey))
                return

            if self.actionId == "RTR": 
                if self.subAction == "COR":
                    self.leg["aobt"] = self.legRTR["aobt"]
                    self.leg["aibt"] = self.legRTR["aibt"]
                else:
                    self.leg["eobt"] = self.legRTR["aibt"] #set estimate to end of RTR leg, to avoid overlaps.
                    self.leg["aobt"] = None

            # WP FAT-INT 374: A DAD should not change statcode if leg is canceled
            if self.actionId == "DAD" and self.legRef['statcode'] == "C":
                self.leg.pop('statcode',None)

            self.parser.makeRecord("flight_leg", "U", self.leg)

            if self.actionId == "ARR":
                # Append flight to make crew on flt published.
                self.parser.arrivalLegs.append((self.leg['udor'],self.leg['fd'],self.leg['adep']))

            if self.actionId == "RTR" and self.subAction != "COR":
                self.legRTR.update(legKey)
                # Make a copy of original flight
                self.parser._services.logger.info("RTR: original flight %s" % self.legRef)
                legRTR = self.legRef.copy()
                suffix = self.generateSuffix(legKey)
                self.parser.newRerouteLegs.append((self.leg['udor'],self.leg['fd'],self.leg['adep']))
                legRTR["fd"] = self.leg["fd"][0:9] + suffix
                legRTR["ades"] = self.leg["adep"] # Make a new flt with same dep and arr station
                legRTR["statcode"] = "R"
                legRTR["aobt"] = self.legRTR["aobt"]
                legRTR["aibt"] = self.legRTR["aibt"]
                # BZ 24474: Save the original suffix
                if self.legRef["fd"][9] not in self.RTRSuffixes:
                    # The original flight was not RTR
                    legRTR["origsuffix"] = self.legRef["fd"][9]
                else:
                    # The original flight was already RTR and
                    # therefore has a generated suffix (and thus
                    # also origsuffix should already be stored
                    # for the original flight).
                    legRTR["origsuffix"] = self.legRef["origsuffix"]
                if legRTR["origsuffix"] in self.RTRSuffixes:
                    # This should never occur...
                    raise errors.MessageError("RTR: Cannot create leg record with invalid original suffix '%s'" % legRTR["origsuffix"])

                # Protect against duplicate mvt/RTR msgs (WP FAT-INT 314)
                rrt_exists = False
                search = dave.DaveSearch("flight_leg",
                                 [("udor", '=', legRTR["udor"]),
                                  ("fd", 'LIKE', self.leg["fd"][0:9] + '_'),
                                  ("adep", '=', legRTR["adep"]),
                                  ("aobt", '=', legRTR["aobt"]),
                                  ("aibt", '=', legRTR["aibt"])])
                for res in self.parser._services.getDaveConnector().runSearch(search):
                    rrt_exists = True
                    self.parser._services.logger.warning("RTR leg already exists %s" % (res))

                if not rrt_exists:
                    self.parser._services.logger.info("RTR: creating leg record %s " % legRTR)
                    self.parser.makeRecord("flight_leg", "I", legRTR)
                    self.parser.newRerouteLegs.append((legRTR['udor'],legRTR['fd'],legRTR['adep']))

                    if legRTR.get('ac'):
                        self.set_ac(legRTR['udor'],
                                    legRTR['fd'],
                                    legRTR['adep'],
                                    legRTR['ac'])
                    self.legRTR = None

            self.leg = None

        elif name == "arrStation":
            # Find fd used in our database, due to we add a suffix for ASM/RRT and MVT/RTR
            fd,_ = self.parser.readFlightLegSuffix({ "udor": self.leg["udor"],
                       "fd": self.leg["fd"],
                       "adep": self.leg["adep"],
            }, self.leg['ades'])
            if fd is not None:
                self.leg["fd"] = fd

        elif name == "delayedDeparture":
            self.delayedDepActive = False
            if self.legDelay is not None:
                legDelayKey = {
                    "leg_udor": self.leg["udor"],
                    "leg_fd": self.leg["fd"],
                    "leg_adep": self.leg["adep"],
                    "seq": uuid.makeUUID64(),
                }
                self.legDelay.update(legDelayKey)
                self.parser._services.logger.debug("writing flight_leg_delay: %s" % self.legDelay)
                self.parser.makeRecord("flight_leg_delay", "W", self.legDelay)
                self.legDelay = None

        elif name == "student":
            # BZ 38935: MVT/TRA can contain several students with landings for each student.
            # If crewLandingInfo is None, then we have other problems.
            if not (self.trainingInfo is None or self.lastFlightLeg is None):
                # Copy last flight descriptor from last 'flightLeg' element.
                self.crewLandingInfo.update(self.lastFlightLeg)
                self.crewLandingInfo.update(self.trainingInfo)
                # Always true...
                self.crewLandingInfo["activ"] = True
                self.parser.makeRecord("crew_landing", "W", self.crewLandingInfo)
            self.crewLandingInfo = None

        elif name == "trainingInfo":
            self.trainingInfo = None


    def characters(self, data):
        data = data.strip() # Possibly use lstrip instead?
        if len(data) == 0:
            return # Ignore whitespace between tags

        if self.currElement == "actionIdentifier":
            self.actionId = data
            return
        elif self.currElement == "subAction":
            self.subAction = data
            return

        nodeHandler = "handle_leg_"+self.currElement
        if (hasattr(self, nodeHandler) and self.leg is not None and self.duty is not None):
            getattr(self, nodeHandler)(data)

        nodeHandler = "handle_training_" + self.currElement
        if hasattr(self, nodeHandler) and self.trainingInfo is not None:
            getattr(self, nodeHandler)(data)

    def handle_leg_flightId(self, data):
        fd = fd_parser(data)
        self.leg["fd"] = fd.flight_descriptor
        self.duty["leg_fd"] = fd.flight_descriptor

    def handle_leg_originDate(self, data):
        udor = readDate(data)
        self.leg["udor"] = udor
        self.duty["leg_udor"] = udor

    def handle_leg_depStation(self, data):
        self.leg["adep"] = data
        self.duty["leg_adep"] = data

    def handle_leg_arrStation(self, data):
        #if self.alwaysCreateFlightLegs:
        self.leg["ades"] = data
        self.legRTR["ades"] = data

    # Don't update leg scheduled times from MVT messages
    def handle_leg_std(self, data):
        if self.alwaysCreateFlightLegs:
            self.leg["sobt"] = readDateTime(data)

    def handle_leg_sta(self, data):
        if self.alwaysCreateFlightLegs or (self.actionId=='ARR' and self.leg['ades']==self.leg['adep']):
            self.leg["sibt"] = readDateTime(data)

    # aircraft
    def handle_leg_acRegShort(self, data):
        if self.alwaysCreateFlightLegs:
            self.duty["ac"] = data
        if self.actionId == "RTR":
            self.legRTR["ac"] = data

    def handle_leg_aircraftOwner(self, data):
        if self.alwaysCreateFlightLegs:
            self.leg["aco"] = data

    # aircraft/acType
    # Don't use IATA subtype in MVT messages
    #def handle_leg_IATASubType(self, data):
    #    self.leg["actype"] = data
    #
    # aircraft/acVersion
    #def handle_leg_acConfigOrVersion(self, data):
    #    pass

    # flightLegStatus
    def handle_leg_etd(self, data):
        if self.actionId in ("DEL", "TRA", "ETD", "RTR"):
            self.leg["eobt"] = readDateTime(data)

    def handle_leg_eta(self, data):
        if self.actionId in ("DEP", "DTO", "ETA"):
            self.leg["eibt"] = readDateTime(data)

    def handle_leg_atd(self, data):
        if self.actionId in ("DEP", "TRA", "NRD", "ATD", "DTO"):
            self.leg["aobt"] = readDateTime(data)
        if self.actionId == "RTR":
            self.legRTR["aobt"] = readDateTime(data)

    def handle_leg_ata(self, data):
        if self.actionId in ("ARR", "TRA", "NRD"):
            self.leg["aibt"] = readDateTime(data)
        if self.actionId == "RTR":
            self.legRTR["aibt"] = readDateTime(data)

    def handle_leg_takeOff(self, data):
        if self.actionId == "DEP":
            self.leg["atot"] = readDateTime(data)
        elif self.actionId == "DTO":
            self.leg["etot"] = readDateTime(data)

    def handle_leg_touchDown(self, data):
        if self.actionId in ("ARR", "TRA", "NRD"):
            self.leg["aldt"] = readDateTime(data)
        elif self.actionId == "DEP":
            self.leg["eldt"] = readDateTime(data)

    # delays/delayedDeparture
    def handle_leg_reasonCode(self, data):
        if self.delayedDepActive:
            self.legDelay["code"] = data
        # Improvement?: Handle diversion reason codes as well.

    def handle_leg_subReasonCode(self, data):
        if self.delayedDepActive:
            self.legDelay["subcode"] = data

    def handle_leg_duration(self, data):
        if self.delayedDepActive:
            self.legDelay["duration"] = data

    def handle_leg_delayReasonText(self, data):
        if self.delayedDepActive:
            self.legDelay["reasontext"] = data

    # diversion
    def handle_leg_originalArrStation(self, data):
        self.leg["ades"] = data

    def handle_leg_newArrStation(self, data):
        self.leg["eades"] = data

    # training
    def handle_training_station(self, data):
        # [acosta:07/033@09:49] crew_landing.airport
        # NOTE: Only the last training station (in case of several cycles) will be used.
        # AFAIK there are no ways of finding out which crew landed on which airport [acosta:09/215@15:20]
        self.trainingInfo["airport"] = data

    def handle_training_perkey(self, data):
        # [acosta:07/033@09:49] crew_landing.crew
        # In the case of <instructor>...</instructor> crewLandingInfo will be None
        if not self.crewLandingInfo is None:
            # Lookup perkey -> crewid in crew_employment
            stime = self.lastFlightLeg['leg_udor'] * 1440
            search = dave.DaveSearch('crew_employment', [
                ('extperkey', '=', data),
                ('validfrom', '<=', stime),
                ('validto', '>', stime),
            ])
            for rec in self.parser._services.getDaveConnector().runSearch(search):
                data = rec['crew']
            self.crewLandingInfo["crew"] = data

    def handle_training_landings(self, data):
        # [acosta:07/033@09:51] crew_landing.nr_landings
        self.trainingInfo["nr_landings"] = int(data)

    def drop_ac(self, udor, fd, adep):
        self.make_record(
            'aircraft_flight_duty', 'D',
            {'leg_udor':udor, 'leg_fd':fd, 'leg_adep':adep})

    def set_ac(self, udor, fd, adep, ac):
        self.drop_ac(udor, fd, adep)
        self.make_record(
            'aircraft_flight_duty', 'I',
            {'leg_udor':udor, 'leg_fd':fd,
             'leg_adep':adep, 'ac':ac})

    def generateSuffix(self, legKey):
        # RTL 31MAY2007
        # Generate a suffix, starting from M, if suffix already exists, then N etc....
        for suffix in self.RTRSuffixes :
            fd = legKey["fd"][0:9] + suffix
            legKey["fd"] = fd
            aleg = readFlightLeg(self.parser, legKey)
            if aleg is None:
                return suffix
        # All suffixes used - report error ?
        return "*"


class OPUSROTHandler(handler.ContentHandler):
    def __init__(self, parser):
        handler.ContentHandler.__init__(self)
        self.parser = parser
        self.acRef = {}
        self.dutyRef = [] 
        self.ac = {}
        self.rot = {}
        self.rotLeg = {}
        self.leg = None
        self.duty = None
        self.mode = ""
        self.alwaysCreateFlightLegs = True
        self.RTRSuffixes = ("M","N","O","P","Q","R","T","U","V","X","Y")

    def startElement(self, name, attrs):
        self.currElement = name
        #for aname in attrs.getNames():
        #    pass
        if name == "rot":
            # Top node
            # Improvement?: Read version attribute
            pass
        elif name == "rotationDay":
            self.mode = "rot"
        elif name == "flightLeg":
            self.mode = "leg"
            # Create new leg/duty
            self.leg = self.rotLeg.copy()
            self.duty = {}

    def endElement(self, name):
        self.currElement = ""
        if name == "rot":
            # End of message
            pass
        elif name == "rotationDay":
            # Store AC if new/modified
            if self.ac.get("id") is not None:
                refAC = self.findInList(self.acRef, self.ac, ["id"])
                if refAC is None or refAC.get("actype") != self.ac.get("actype") \
                     or refAC.get("owner") != self.ac.get("owner"):
                    self.parser._services.logger.debug("creating aircraft record %s " % self.ac)
                    self.parser.makeRecord("aircraft", "W", self.ac)

            # Store rotation
            self.parser._services.logger.debug("creating rotation record %s " % self.rot)
            self.parser.makeRecord("rotation", "W", self.rot)

            # Read all duties for this rotation and check against the new ones, if they are not there, atleast those legs
            # should not be in this rotation. Try and use rot_udor and ac to identoy legs in rotation. Backup plan is to use
            # the ID for the rotation if aircraft is unknown (like empty rotation messages)
            if self.ac.get('id'):
                search = dave.DaveSearch('aircraft_flight_duty',[("rot_udor", '=', self.rot["udor"]), ("ac", '=', self.ac['id'])])
            else:
                search = dave.DaveSearch('aircraft_flight_duty',[("rot_id", '=', self.rot["id"])])

            old_duties = self.parser._services.getDaveConnector().runSearch(search)
            for old_duty in old_duties:
                # If there exists a RTR leg (identified by it's suffix) then keep it, cuase it actually did happen
                if old_duty['leg_fd'][9] in self.RTRSuffixes:
                    continue

                # Search amongst the legs created by the message, if it isn't in that set, remove it from the rotation
                # or if it is there, let's keep the previous choice of the parser
                refDuty = self.findInList(self.dutyRef, old_duty,
                                          ["leg_udor","leg_fd","leg_adep","ac"])
                if refDuty is None:
                    old_duty["_keep"] = False
                    self.dutyRef.append(old_duty)
                    self.parser._services.logger.info("ROT: removing duty %s " % str(old_duty))

            # Remove old duties, if '_keep' isn't set to true, this will delete the duty
            for duty in self.dutyRef:
                if duty.get("_keep") != True:
                    self.parser.makeRecord("aircraft_flight_duty", "D",
                         { "leg_udor" : duty["leg_udor"],
                           "leg_fd"   : duty["leg_fd"],
                           "leg_adep" : duty["leg_adep"],
                           "ac"       : duty["ac"] })
                    # RFI 54 - We need to catch rotation changes here as well
                    # in order to trigger re-publication for all relevant
                    # changes while at the same time avoiding re-publication
                    # when completely new rotations are built.
                    self.parser.rotationChangeLegs.append((duty["leg_udor"],duty["leg_fd"],duty["leg_adep"]))

            self.ac.clear()
            self.rot.clear()
            self.rotLeg.clear()
            self.acRef[:] = []
            self.dutyRef[:] = []
            self.mode = ""
        elif name == "flightLeg":
            # Add rotation info to duty
            self.duty["rot_udor"] = self.rot["udor"]
            self.duty["rot_id"] = self.rot["id"]

            # Find fd used in our database, due to we add a suffix for ASM/RRT and MVT/RTR
            fd,legRef = self.parser.readFlightLegSuffix({ "udor": self.leg["udor"],
                       "fd": self.leg["fd"],
                       "adep": self.leg["adep"],
            }, self.leg['ades'])
            if fd is not None:
                self.leg["fd"] = fd
                self.duty["leg_fd"] = fd
            # Leg/duty complete - send to storage
            self.parser._services.logger.debug("updating leg record %s " % self.leg)
            
            if legRef == None:
                self.parser._services.logger.warning("%s: Unable to find original leg: %s" % (name, { "udor": self.leg["udor"],
                                                                                                         "fd": self.leg["fd"],
                                                                                                         "adep": self.leg["adep"]}))
            else:
                dbref = self.readReferenceFltData(self.leg["fd"], self.leg["udor"], self.leg["adep"])
                self.dutyRef.extend(dbref)
                # Do not update flt data, from a ROT msg, robertt/21Dec08
                #self.parser.makeRecord("flight_leg", "U", self.leg)
                self.parser._services.logger.debug("creating duty record %s " % self.duty)
                self.parser.makeRecord("aircraft_flight_duty", "W", self.duty)
                refDuty = self.findInList(self.dutyRef, self.duty,
                                           ["leg_udor","leg_fd","leg_adep","ac"])
                if refDuty is not None:
                    refDuty["_keep"] = True
                elif len(dbref) > 0:
                    # RFI 54 - A change to an aircraft rotation might affect
                    # meal stop calculations, therefore put leg in a special
                    # metadata list for a subsequent handler to process it
                    # and re-publish affected crew.
                    #
                    # Example: Last leg of a rotation switches ac:
                    #   R1 (orig)  a b c    =>  a b
                    #   R2 (new)            =>  c
                    self.parser.rotationChangeLegs.append((self.duty["leg_udor"],self.duty["leg_fd"],self.duty["leg_adep"]))

            self.leg = None
            self.duty = None
            self.mode = "rot"

    # quick hack -- replace by having searches return key'ed dicts
    def findInList(self,listOfDicts,dict,keys):
        for d in listOfDicts:
            for k in keys:
                if dict[k] != d[k]:
                    break
            else:
                return d
        return None


    def characters(self, data):
        data = data.strip() # Possibly use lstrip instead?
        if (len(data) == 0): return # Ignore whitespace between tags

        nodeHandler = "handle_"+self.mode+"_"+self.currElement
        if (hasattr(self, nodeHandler) and
             (self.mode != "leg" or (self.leg is not None and self.duty is not None))):
            getattr(self, nodeHandler)(data)

    def readReferenceData(self, rotationId):
        # Read aircraft and rotation duties from DB (required for later handling)
        search = dave.DaveSearch('aircraft', [])
        self.acRef = self.parser._services.getDaveConnector().runSearch(search)
        #search2 = dave.DaveSearch('aircraft_flight_duty',[("rot_id", '=', self.rot["id"])])
        #self.dutyRef = self.parser._services.getDaveConnector().runSearch(search2)

    def readReferenceFltData(self, fd, udor, adep):
        # Read aircraft and rotation duties from DB (required for later handling)
        search = dave.DaveSearch('aircraft_flight_duty',[("leg_fd", '=', fd),
                                                         ("leg_udor", '=', udor),
                                                         ("leg_adep", '=', adep)])
        return self.parser._services.getDaveConnector().runSearch(search)

    # --- Rotation and aircraft info on rotationDay level ---
    def handle_rot_rotationId(self, data):
        self.rot["udor"] = readYYMMDD(data)
        self.rot["id"] = data
        self.readReferenceData(self.rot["id"]) # Read existing rotation data
        #self.clearRotationData(self.rot["id"]) # Remove existing rotation data

    def handle_rot_aircraftOwner(self, data):
        self.ac["owner"] = data
        #self.rotLeg["aco"] = data robertt: 28Nov2007, aco is either SKI,SKD,SKN or SKS, should not be updated here.

    def handle_rot_acTypeCode(self, data):
        self.ac["actype"] = data
        self.rot["actype"] = data
        self.rotLeg["actype"] = data

    # --- Flight info ---
    def handle_leg_flightId(self, data):
        fd = fd_parser(data)
        self.leg["fd"] = fd.flight_descriptor
        self.duty["leg_fd"] = fd.flight_descriptor

    def handle_leg_originDate(self, data):
        udor = readDate(data)
        self.leg["udor"] = udor
        self.duty["leg_udor"] = udor

    def handle_leg_depStation(self, data):
        self.leg["adep"] = data
        self.duty["leg_adep"] = data

    def handle_leg_arrStation(self, data):
        self.leg["ades"] = data

    def handle_leg_std(self, data):
        pass
        # Should not be updated here, only from an ASM/SSM
        #if self.alwaysCreateFlightLegs:
        #    self.leg["sobt"] = readDateTime(data)

    def handle_leg_sta(self, data):
        pass
        # Should not be updated here, only from an ASM/SSM
        #if self.alwaysCreateFlightLegs:
        #    self.leg["sibt"] = readDateTime(data)

    # aircraft
    # Improvement?: Handle anonymous rotations/duties
    def handle_leg_acRegShort(self, data):
        self.ac["id"] = data
        self.duty["ac"] = data

    # aircraft/acVersion
    def handle_leg_acConfigOrVersion(self, data):
        pass

    # flightLegStatus
    def handle_leg_etd(self, data):
        pass
        #self.leg["eobt"] = readDateTime(data)

    def handle_leg_eta(self, data):
        pass
        #self.leg["eibt"] = readDateTime(data)

    # Improvement?: Handle actual times together with departureStatus/arrivalStatus.
    # Only use actual times if the corresponding status is ACT.
    def handle_leg_atd(self, data):
        pass
        #self.leg["aobt"] = readDateTime(data)

    def handle_leg_ata(self, data):
        pass
        #self.leg["aibt"] = readDateTime(data)

    def handle_leg_takeOff(self, data):
        pass
        #self.leg["atot"] = readDateTime(data)

    def handle_leg_touchDown(self, data):
        pass
        #self.leg["aldt"] = readDateTime(data)

    # delays/delayedDeparture
    def handle_leg_reasonCode(self, data):
        pass

    def handle_leg_duration(self, data):
        pass

    # diversion
    #def handle_leg_reasonCode(self, data):
    #    # Collision! If we are to handle reason codes, we need to store some context info.
    #    pass

    # paxFigures/paxFigure
    # [acosta:07/036@15:53] PAX figures are not handled here.


class OPUSParser(MessageHandlerBase):
    """Handles 'mvt' and 'rot' messages from SAS OPUS system.

        Options:
            onlyRot - If "True" only rotation messages will be handled.
                      Default "False"
    """
    def __init__(self, onlyRot="False", name=None):
        super(OPUSParser,self).__init__(name)
        self.onlyRot = utils.convertToBoolean(onlyRot)

    def handle(self,message):
        self.ops = []
        self.newRerouteLegs = []
        self.rotationChangeLegs = []
        self.arrivalLegs = []
        xmldoc = message.content
        try:
            parseString(xmldoc, MsgVerifier())
        except TypeFoundException,e:
            msgType = e.name
        except Exception,esax:
            raise errors.MessageError("Unable to parse message: %s" % esax)
        try:
            if msgType == 'mvt':
                if not self.onlyRot:
                    parseString(xmldoc, OPUSMVTHandler(self))
            elif msgType == 'rot':
                parseString(xmldoc, OPUSROTHandler(self))
            else:
                raise errors.MessageError('Unknown message type "%s", expected "mvt" or "rot"' % msgType)
        except Exception,ex:
            raise errors.MessageError(str(ex))

        # We have no transaction safety here ... no source/id available. The DaveWriter must
        # be configured with ignoreOutOrder set to True
        message.setContent((None,None,self.ops), DaveContentType()) # (sourceId, transactionId, operations)
        message.metadata.update({ metaNewRerouteLegs : self.newRerouteLegs })
        message.metadata.update({ metaRotationChangeLegs : self.rotationChangeLegs })
        message.metadata.update({ metaArrivalLegs : self.arrivalLegs })
        return CallNextHandlerResult()


    def makeRecord(self, entity, op, map):
        self.ops.append(dave.createOp(entity,op,map.copy()))

    # Read all flights for fd without suffix
    def readFlightLegSuffix(self, legKey, ades):
        # Read flight from DB (required for suffix generation)
        search = dave.DaveSearch("flight_leg",
             [("udor", '=', legKey["udor"]),
              ("fd", 'LIKE', legKey["fd"][:9] + '_'),
              ("adep", '=', legKey["adep"])])
        leg = None
        for result in self._services.getDaveConnector().runSearch(search):
            if result['ades'] == ades:
                # Avoid returning a cancelled leg, if possible
                if leg is None or \
                   leg['statcode'] == 'C' or \
                   (result['fd'] > leg['fd'] and result['statcode'] != 'C'):
                    self.legOrg = result.copy()
                    leg = result
        if leg:
            return (leg['fd'], leg.copy())
        return (None,None)

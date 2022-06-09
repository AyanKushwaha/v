"""
Customized parser for Crew personal information imported from HR SAP system. 
Incoming personnel no is matched against crew_employment[extperkey] to find the 
cms crew id key. If the crew does not yet exist (new empoyee or changed employee
 country) the crew is added to table crew_unknown. For more information
about the procedure to manually resolve unknown crew, please refer to the
Functional Refrence manual.

Two different types of messages are treated - Crew Personal Info and
Cerw Address info. The format of these messages are defined in interface 43.6
specification.
The following information is updated in the database:
    Crew Personal Info:
        crew            - most recent crew names
        crew_extra_info - names, nationality and marital status incl history
        crew_contact    - most recent email address
    Crew Address Info:
        crew_address    - crew main and secondary address data incl history
        crew_relatives  - contact info for relatives/friends/neighbors etc.
        crew_contact    - most recent telephone numbers
The program only makes an update to the database if incoming data actually
differs from what is in the database, thus avoid creating unnecessary
Dave revisions.
"""

# imports ================================================================{{{1
import struct, datetime
import smtplib
import socket
from copy import copy
from AbsDate import AbsDate
from AbsTime import AbsTime
from RelTime import RelTime
from carmensystems.dig.framework.carmentime import fromCarmenTime, toCarmenTime
from carmensystems.dig.framework.handler import MessageHandlerBase,CallNextHandlerResult
from carmensystems.dig.framework import errors
from carmensystems.dig.framework import dave
from carmensystems.dig.messagehandlers.dave import DaveContentType
from carmensystems.dig.notifiers.mail import Transport
from dig.intgutils import IntgServiceConfig


# Global constants ======================================================={{{1
MSGTYP_PERS = 'Personal Info'
MSGTYP_ADDR = 'Address Info'

# classes ================================================================{{{1

# CrewPersonalInfo -------------------------------------------------------{{{2
class CrewPersonalInfo:

    # Definition of the fixed record format.
    # The 'fieldstarts' list defines the start of each field and
    # the 'fieldsizes' list defines their fixed length
    #
    # Using a C type struct here is not a good option since we want to handle
    # UTF-8 encoded fields.
    fieldstarts = [0, 8, 16, 24, 26, 66, 106, 146, 147, 159, 167, 170, 173, 174, 254]
    fieldsizes  = [8, 8,  8,  2, 40, 40,  40,   1,  12,   8,   3,   3,   1,  80, 8]
    # Kept for historical reasons to be able to calculate record size
    format = "8s 8s 8s 2s 40s 40s 40s 1s 12s 8s 3s 3s 1s 80s 8s"

    def __init__(self, f):
        # Each field which safely can be encoded in ASCII format (default for 'encode' method)
        # are encoded as such to e.g. make the normal comparisons work
        # without resorting to Unicode string syntax.
        self.pnr = f[0].lstrip('0').encode()
        self.validDateFrom = validDate(f[1].encode())
        self.validDateTo = validDate(f[2].encode())
        self.empCountry = f[3].encode()
        self.lastName = f[4]
        self.firstName = f[5]
        self.sasName = f[6]
        self.gender = f[7].encode()
        self.personnelId = f[8].encode()
        self.birthDate = f[9].encode()
        self.nationality = f[10].encode()
        self.nationality2 = f[11].encode()
        self.maritalstatus = f[12].encode()
        self.email = f[13].encode()
        self.retirementDate = validDate(f[14].encode())

    def __str__(self):
        return "%s" % self.__dict__

    def validate(self,logger):
        # 09=DK, 20=NO, 23=SV, 99=International
        if not self.empCountry in ('09', '20', '23', '99'):
            raise ParseException(self.pnr, self.__class__.__name__ + \
                    ": Invalid EmpCountry: " + self.empCountry + \
                    " Valid values are 09=DK, 23=SV, 20=NO, 99=International ")
        if not self.maritalstatus in ('0','1', '2', '3', ''):
            raise ParseException(self.pnr, self.__class__.__name__ + \
                    ": Invalid Civilstand: " + self.maritalstatus + \
                    " Valid values are 0-3 ")
        if not self.gender in ('1', '2'):
            raise ParseException(self.pnr, self.__class__.__name__ + \
                    ": Invalid Gender: " + self.gender + \
                    " Valid values are 1-2 ")
        if self.validDateFrom > self.validDateTo:
            raise ParseException(self.pnr, self.__class__.__name__ + \
                    ": Valid-date-from (%s) larger than Valid-date-to (%s)" % (self.validDateFrom, self.validDateTo))
        try:
            # Correct incredibly ancient Valid-date-from
            if self.validDateFrom < CrewDb.MINDATE:
                self.validDateFrom = CrewDb.MINDATE
            AbsDate(self.validDateFrom)
        except:
            raise ParseException(self.pnr, self.__class__.__name__ + \
                    ": Invalid Valid-date-from: " + self.validDateFrom)
        try:
            # We cannot handle dates beyond 20351231
            if self.validDateTo > CrewDb.MAXDATE:
                self.validDateTo = CrewDb.MAXDATE
            else:
                # The whole validDateTo day should count
                self.validDateTo = fromCarmenTime(int(AbsDate(self.validDateTo)) + 1440).strftime("%Y%m%d")
        except:
            raise ParseException(self.pnr, self.__class__.__name__ + \
                    ": Invalid Valid-date-to: " + self.validDateTo)
        try:
            AbsDate(self.birthDate)
        except:
            raise ParseException(self.pnr, self.__class__.__name__ + \
                    ": Invalid Birth date: " + self.birthDate)
        try:
            if self.retirementDate.strip() == '':
                # If no retirement date - use MAXDATE for generic handling
                self.retirementDate = CrewDb.MAXDATE
            AbsDate(self.retirementDate)
        except:
            raise ParseException(self.pnr, self.__class__.__name__ + \
                    ": Invalid Retirement date: " + self.retirementDate)


# CrewAddressInfo --------------------------------------------------------{{{2
class CrewAddressInfo:

    # Definition of the fixed record format.
    # The 'fieldstarts' list defines the start of each field and
    # the 'fieldsizes' list defines their fixed length
    #
    # Using a C type struct here is not a good option since we want to handle
    # UTF-8 encoded fields.
    fieldstarts = [  0,   8,  16,  24,  28,  31,  33,  73, 133, 143, 183, 
                   186, 200, 240, 300, 340, 350, 390, 430, 444, 448, 452, 
                   456, 460, 480, 500, 520, 540]
    fieldsizes  = [  8,   8,   8,   4,   3,   2,  40,  60,  10,  40,   3, 
                    14,  40,  60,  40,  10,  40,  40,  14,   4,   4,   4, 
                     4,  20,  20,  20,  20,   8]
    # Kept for historical reasons to be able to calculate record size
    format = "8s 8s 8s 4s 3s 2s 40s 60s 10s 40s 3s 14s 40s 60s 40s 10s \
              40s 40s 14s 4s 4s 4s 4s 20s 20s 20s 20s 8s"

    def __init__(self, f):
        # Each field which safely can be encoded in ASCII format (default for 'encode' method)
        # are encoded as such to e.g. make the normal comparisons work
        # without resorting to Unicode string syntax.
        self.pnr = f[0].lstrip('0').encode()
        self.validDateFrom = validDate(f[1].encode())
        self.validDateTo = validDate(f[2].encode())
        self.subtype = f[3].encode()
        self.seqno = f[4].encode()
        self.empCountry = f[5].encode()
        self.co = f[6]
        self.street = f[7]
        self.postalCode = f[8]
        self.city = f[9][0:30] # max 30 in db
        self.country = f[10].encode()
        self.phone = f[11].encode()
        self.c_co = f[12]
        self.c_street = f[13]
        self.c_address2 = f[14]
        self.c_postalCode = f[15]
        self.c_city = f[16]
        self.c_stadsdel = f[17]
        self.c_phone = f[18].encode()
        self.c_comTyp1 = f[19].encode()
        self.c_comTyp2 = f[20].encode()
        self.c_comTyp3 = f[21].encode()
        self.c_comTyp4 = f[22].encode()
        self.c_comNumber1 = f[23]
        self.c_comNumber2 = f[24]
        self.c_comNumber3 = f[25]
        self.c_comNumber4 = f[26]
        self.retirementDate = validDate(f[27].encode())

    def __str__(self):
        return "%s" % self.__dict__

    def getInterval(self):
        return (strToTime(self.validDateFrom), strToTime(self.validDateTo))
    
    def sendemail(self, logger, message):
        config = IntgServiceConfig()
        
        (key, mailhost) = config.getProperty("dig_settings/mail/host")
        (key, mailport) = config.getProperty("dig_settings/mail/port")
        (key, mailfrom) = config.getProperty("dig_settings/mail/from")
        (key, mailto) = config.getProperty("dig_settings/mail/to")

        try:
            conn = smtplib.SMTP(mailhost, mailport)
            if not mailhost:
                conn.connect()        
        except socket.error, (_, err):
            raise errors.TransientError('Failed to connect to SMTP server: %s.' % err)
        try:
            conn.sendmail(mailfrom, mailto, message)
        except smtplib.SMTPServerDisconnected, e:
            raise errors.TransientError('Failed to send mail to SMTP server: %s.' % e)
        except smtplib.SMTPRecipientsRefused, e:
            errs = []
            for address, reason in sorted(e.recipients.items()):
                errs.append("'%s': '%s'" % (address, reason[1]))
            raise errors.MessageError("Failed to send mail: All recipients refused (%s) %s." % (', '.join(errs)))
        except smtplib.SMTPSenderRefused, e:
            raise errors.MessageError("Failed to send mail: Sender refused ('%s': '%s') %s." % (e.sender, e.smtp_error))
        conn.quit()        

    def validate(self,logger):
        if not self.subtype in (AddressInfoParser.SUBTYP_MAIN, AddressInfoParser.SUBTYP_SECOND, AddressInfoParser.SUBTYP_REL):
            raise ParseException(self.pnr, self.__class__.__name__ + \
                    ": Invalid subtype: " + self.subtype + \
                    " Valid values are 1,2,4")
        if self.subtype == AddressInfoParser.SUBTYP_MAIN:
            # nonnull constraints in crew_address
            if self.street == "" and self.co == "":
                logger.warning("%s: Parse warning for pnr=%s: %s" % (self.__class__.__name__, self.pnr, \
                        "Street must not be empty in crew main address."))
                self.street = u'.'
            if self.city == "":
                logger.warning("%s: Parse warning for pnr=%s: %s" % (self.__class__.__name__, self.pnr, \
                        "City must not be empty in crew main address."))
                self.city = u'.'
            if self.country == "":
                message = ("Subject: Crewinfo DIG channel, Crewinfoparser warning empty field \n\n%s: Parse warning for pnr=%s: " \
                        "Country must not be empty in crew main address, record ignored." % (self.__class__.__name__, self.pnr))

                self.sendemail(logger, message)
                logger.warning(message)
                raise ParseException(self.pnr, self.__class__.__name__ + \
                                     ": Country must not be empty in crew main address, record ignored")
        if self.validDateFrom > self.validDateTo:
            raise ParseException(self.pnr, self.__class__.__name__ + \
                    ": Valid-date-from (%s) larger than Valid-date-to (%s)" % (self.validDateFrom, self.validDateTo))
        try:
            # Correct incredibly ancient Valid-date-from
            if self.validDateFrom < CrewDb.MINDATE:
                self.validDateFrom = CrewDb.MINDATE
            AbsDate(self.validDateFrom)
        except:
            raise ParseException(self.pnr, self.__class__.__name__ + \
                    ": Invalid Valid-date-from: " + self.validDateFrom)
        try:
            # We cannot handle dates beyond 20351231
            if self.validDateTo > CrewDb.MAXDATE:
                self.validDateTo = CrewDb.MAXDATE
            else:
                # The whole validDateTo day should count
                self.validDateTo = fromCarmenTime(int(AbsDate(self.validDateTo)) + 1440).strftime("%Y%m%d")
        except:
            raise ParseException(self.pnr, self.__class__.__name__ + \
                    ": Invalid Valid-date-to: " + self.validDateTo)
        try:
            if self.retirementDate.strip() == '':
                # If no retirement date - use MAXDATE for generic handling
                self.retirementDate = CrewDb.MAXDATE
            AbsDate(self.retirementDate)
        except:
            raise ParseException(self.pnr, self.__class__.__name__ + \
                    ": Invalid Retirement date: " + self.retirementDate)


# CrewContainer ----------------------------------------------------------{{{2
class CrewContainer(list):
    """ Container class for objects to be updated in database """
    def __init__(self, crewId, lastValidPerkey):
        list.__init__(self)
        self.crewId = crewId
        self.lastValidPerkey = lastValidPerkey
        self.lastValidRec = None
        self.perkeys = set()

    def addRec(self, cInfo, validPeriods):
        cInfo.crewId = self.crewId
        self.perkeys.add(cInfo.pnr)
        # Remember the most recent information to be stored in tables
        # without history. Note that we cannot use the 'self' list of
        # records because the most recent info should be updated even 
        # if it doesn't match any validity period in crew_employment.
        if self.lastValidRec is None:
            self.lastValidRec = cInfo
        if cInfo.pnr == self.lastValidPerkey:
            if self.lastValidRec.pnr != self.lastValidPerkey or \
                cInfo.validDateTo > self.lastValidRec.validDateTo:
                self.lastValidRec = cInfo

        # Append to list of records to be updated in tables with history
        for (validfrom,validto) in validPeriods:
            cCopy = copy(cInfo)
            cCopy.validDateFrom = validfrom
            cCopy.validDateTo = validto
            self.append(cCopy)


# CrewInfoParser ---------------------------------------------------------{{{2
class CrewInfoParser(MessageHandlerBase):
    """
    The CrewInfoParser gets a whole message at a time. Each message
    contains a number of records as defined in interface
    description 43.6. There are two different kinds of messages:
    "Personal Info" and "Address Info" and thus two different kinds
    of record types with different layout (see bottom of this file).
    """
    def __init__(self, name=None):
        super(CrewInfoParser,self).__init__(name)

    def handle(self, message):
        self._services.logger.info("CrewInfoParser started...")
        M = message.content
        self.crewDb = CrewDb(self._services.getDaveConnector(),self._services.logger)

        if M.find(MSGTYP_PERS,9,28) != -1:
            parser = PersonalInfoParser(self.crewDb, self._services.logger)
        elif M.find(MSGTYP_ADDR,9,28) != -1:
            parser = AddressInfoParser(self.crewDb, self._services.logger)
        else:
            raise errors.MessageError('Unknown message type "%s", expected "%s" or "%s"' % (M[9:28], MSGTYP_PERS, MSGTYP_ADDR))
        self._services.logger.info("Received %s message of type %s" % (parser.type, message.contentType))

        # Calculate record size
        self._services.logger.debug("Message length: %d chars (incl linefeeds)" % (len(M)))
        szRec = struct.calcsize(parser.recFormat)

        # Extract number of records from footer
        # Note that this must be done in a way that is independent of how
        # the linefeed sequences look like. Also, we cannot assume that
        # records are filled with spaces at the end.
        lines = M.splitlines()
        nLines = len(lines)
        x = 1
        while lines[nLines - x][0:8].strip() == "":
            x += 1
        nRecs = int(lines[nLines - x][0:8].strip())
        nInfoRecs = nRecs - 2  # without header and footer...

        # Delete header and footer records
        for z in range(0,x):
            del lines[len(lines) - 1]
        del lines[0]

        # Parse and handle all records
        nHandledRecs = parser.parse(lines)

        # Verify number of handled records
        if nHandledRecs != nInfoRecs:
            self._services.logger.error("Number of handled records (%d) differs from number of records in footer (%d)" % (nHandledRecs,nInfoRecs))

        self._services.logger.info("End of %s message" % parser.type)
        message.setContent((None,None, self.crewDb.ops), DaveContentType())
        return CallNextHandlerResult()


# InfoParser -------------------------------------------------------------{{{2
class InfoParser:
    """Base class for crew info parsers"""
    def __init__(self, crewDb, logger, now=None):
        self.hasError = False
        self.logger = logger
        self.crewDb = crewDb
        self.recFormat = self.infoClass.format
        self.szRec = struct.calcsize(self.recFormat)
        self.encoding = 'utf-8'
        if now is None:
            now = datetime.datetime.now()
        self.now = toCarmenTime(now)


    def parseLine(self, line):
        # Here we assume that the input record is in UTF-8 format since that's what we have been
        # getting so far...
        try:
            s = unicode(line, self.encoding)
            # Parse the record according to the fixed size record definition and strip trailing spaces
            fields = [s[x:x+y].strip() for (x, y) in zip(self.infoClass.fieldstarts, self.infoClass.fieldsizes)]       
        except:
            try:
                if self.encoding == 'utf-8':
                    self.encoding = 'latin-1'
                else:
                    self.encoding = 'utf-8'
                self.logger.warning("Could not parse, trying %s instead, record = %s" % (self.encoding, line))
                s = unicode(line, self.encoding)
                # Parse the record according to the fixed size record definition and strip trailing spaces
                fields = [s[x:x+y].strip() for (x, y) in zip(self.infoClass.fieldstarts, self.infoClass.fieldsizes)]       
            except Exception, e2:
                self.logger.error("Could not parse using %s, discarding record = %s" % (self.encoding, line)).exception(e2)
                return None

        self.logger.debug("Parsed %s record = %s" % (self.type, fields))
        cInfo = self.infoClass(fields)
        try:
            cInfo.validate(self.logger)
        except ParseException, e:
            #  self.logger.error("The record has been discarded.").exception(e)
            self.logger.error("The record has been discarded." +  str(e))
            return None
        return cInfo


    def align(self, sorted):
        """Removes records with duplicate validfrom and changes validto
           if necessary to avoid overlapping periods. Overlaps seem to
           occur quite frequently in HR-data for crew that has changed
           extperkey during the course of their employment.
        """
        result = []
        idx = 0
        while idx < len(sorted):
            rec = sorted[idx]
            idx += 1
            if idx < len(sorted):
                if sorted[idx].validDateFrom == rec.validDateFrom:
                    self.logger.error("Skipped record with duplicate valid-date-from: %s" % rec)
                    continue
                if rec.validDateTo > sorted[idx].validDateFrom:
                    rec.validDateTo = sorted[idx].validDateFrom
                    self.logger.error("Adjusted valid-date-to to avoid overlapping records: %s" % rec)
            result.append(rec)
        return result


    def retiredLongAgo(self, retirementDate):
        """ Return True if crew has retired more than 5 years ago """
        if AbsTime(self.now) - AbsTime(strToTime(retirementDate)) > RelTime(5*365+1,0,0):
            return True
        return False


    def sortByPeriod(rec1,rec2):
        if rec1.validDateFrom > rec2.validDateFrom:
            return 1
        elif rec1.validDateFrom < rec2.validDateFrom:
            return -1
        if rec1.validDateTo > rec2.validDateTo:
            return 1
        elif rec1.validDateTo < rec2.validDateTo:
            return -1
        return 0
    sortByPeriod = staticmethod(sortByPeriod)


# PersonalInfoParser -----------------------------------------------------{{{2
class PersonalInfoParser(InfoParser):
    type = MSGTYP_PERS
    infoClass = CrewPersonalInfo

    def parse(self, lines):
        self.hasError = False
        crewpers = {}
        nRecs = 0
        for line in lines:
            if line == "":
                continue
            nRecs += 1
            pInfo = self.parseLine(line.ljust(self.szRec))
            if pInfo is None:
                # Skip record with errors
                self.hasError = True
                continue

            crewId, validPeriods = self.crewDb.getCrewId(pInfo.pnr, strToTime(pInfo.validDateFrom), strToTime(pInfo.validDateTo))
            if crewId is None:
                self.logger.warning("CREW UNKNOWN perkey=%s" % (pInfo.pnr))
                if self.retiredLongAgo(pInfo.retirementDate):
                    self.logger.info("Skipping perkey %s with retirement date %s" % (pInfo.pnr, pInfo.retirementDate))
                else:
                    self.crewDb.updateUnknownCrew(pInfo)
                    self.hasError = True
                continue
            elif len(validPeriods) == 0:
                self.logger.debug("No employment validity overlap found for record perkey=%s (%s-%s)" % (pInfo.pnr, pInfo.validDateFrom, pInfo.validDateTo))

            if not crewId in crewpers:
                crewpers[crewId] = CrewContainer(crewId, self.crewDb.getLastValidPerkey(crewId))

            crewpers[crewId].addRec(pInfo, validPeriods)

        # Purge corrected unknown crew
        self.crewDb.deleteCorrectedUnknownCrew()

        # Build hash-map of crew from database
        dbCrewMap = {}
        for rec in self.crewDb.getCrew():
            dbCrewMap[rec['id']] = CrewRec.getUnicodeDict(rec)
            
        # Do stuff per crew...
        for crewId in crewpers.keys():
            # Sort by validity period.
            crewpers[crewId].sort(InfoParser.sortByPeriod)
            # Adjust any overlapping records
            persRecs = self.align(crewpers[crewId])

            if len(persRecs) == 0:
                # Crew only exist outside HR validity period (WP FAT-INT 132)
                self.logger.warning("DISCARDED obsolete crew id=%s, perkey=%s" % (crewId, crewpers[crewId].perkeys))
                continue

            if self.retiredLongAgo(crewpers[crewId].lastValidRec.retirementDate):
                self.logger.info("Skipping crew id=%s with retirement date %s" % (crewId, crewpers[crewId].lastValidRec.retirementDate))
                continue

            self.logger.debug("Updating crew with id=%s (%d records)" % (crewId, len(persRecs)))

            # Update table crew with most recent information, only update if changed
            crewRec = CrewRec(crewpers[crewId].lastValidRec)
            if dbCrewMap.get(crewId, {}) != crewRec.__dict__:
                self.crewDb.updateCrew(crewRec.__dict__)

            # Update email address in crew_contact.
            # Note that only the most recent information is updated.
            contactRec = CrewContactRec(crewId,"Email","work",crewpers[crewId].lastValidRec.email)
            self.crewDb.updateCrewContact(crewId, self.type, [contactRec])

            # Update crew_extra_info records if they have changed
            pRecs = []
            for pr in persRecs:
                pRecs.append(CrewAttrRec(pr))
            self.crewDb.updateWithValidity(crewId, pRecs, CrewAttrRec.dbTable, CrewAttrRec.dbCrewFieldName)
        return nRecs


# AddressInfoParser -- ---------------------------------------------------{{{2
class AddressInfoParser(InfoParser):
    type = MSGTYP_ADDR
    infoClass = CrewAddressInfo
    SUBTYP_MAIN = '1'
    SUBTYP_SECOND = '2'
    SUBTYP_REL = '4'

    def parse(self, lines):
        self.hasError = False
        crewaddr = {}
        nRecs = 0
        for line in lines:
            if line == "":
                continue
            nRecs += 1
            aInfo = self.parseLine(line.ljust(self.szRec))
            if aInfo is None:
                # Skip record with errors
                self.hasError = True
                continue

            crewId, validPeriods = self.crewDb.getCrewId(aInfo.pnr, strToTime(aInfo.validDateFrom), strToTime(aInfo.validDateTo))
            if crewId is None:
                self.logger.warning("DISCARDED perkey=%s (crew not found)" % (aInfo.pnr))
                if self.retiredLongAgo(aInfo.retirementDate):
                    self.logger.info("Skipping perkey %s with retirement date %s" % (aInfo.pnr, aInfo.retirementDate))
                else:
                    self.hasError = True
                continue
            elif len(validPeriods) == 0:
                self.logger.debug("No employment validity overlap found for record perkey=%s (%s-%s)" % (aInfo.pnr, aInfo.validDateFrom, aInfo.validDateTo))

            if not crewId in crewaddr:
                crewaddr[crewId] = {}
                crewaddr[crewId][self.SUBTYP_MAIN] = CrewContainer(crewId, self.crewDb.getLastValidPerkey(crewId))
                crewaddr[crewId][self.SUBTYP_SECOND] = CrewContainer(crewId, self.crewDb.getLastValidPerkey(crewId))
                crewaddr[crewId][self.SUBTYP_REL] = CrewContainer(crewId, self.crewDb.getLastValidPerkey(crewId))

            crewaddr[crewId][aInfo.subtype].addRec(aInfo, validPeriods)

        # Do stuff per crew...
        for crewId in crewaddr.keys():
            # Sort by validity period
            crewaddr[crewId][self.SUBTYP_MAIN].sort(InfoParser.sortByPeriod)
            crewaddr[crewId][self.SUBTYP_SECOND].sort(InfoParser.sortByPeriod)
            crewaddr[crewId][self.SUBTYP_REL].sort(InfoParser.sortByPeriod)
            # Adjust any overlapping records
            mainRecs = self.align(crewaddr[crewId][self.SUBTYP_MAIN])
            secRecs = self.align(crewaddr[crewId][self.SUBTYP_SECOND])
            relRecs = crewaddr[crewId][self.SUBTYP_REL]

            if len(mainRecs) > 0:
                if self.retiredLongAgo(crewaddr[crewId][self.SUBTYP_MAIN].lastValidRec.retirementDate):
                    self.logger.info("Skipping crew id=%s with retirement date %s" % (crewId, crewaddr[crewId][self.SUBTYP_MAIN].lastValidRec.retirementDate))
                    continue

            self.logger.debug("Updating crew with id=%s (%d records)" % (crewId, len(mainRecs) + len(secRecs) + len(relRecs)))

            # Merge incoming primary and secondary address records.
            # Note that we don't need to merge existing database
            # records aswell since we're working with total updates.
            # To implement delta updates please see ver. 1.26 of this file.
            #
            # Use aggregate periods of incoming HR main and sec addr 
            # recs as master for incoming HR addr
            pAggr = getAggregates(mainRecs+secRecs)
            mergedAddr = []
            for (s,e) in pAggr:
                mainAddr = getOverlapAddrRec((s,e), mainRecs)
                secAddr = getOverlapAddrRec((s,e), secRecs)
                if not mainAddr is None:
                    master = copy(mainAddr)
                    master.mergeSecondAddr(secAddr)
                elif not secAddr is None:
                    master = copy(secAddr)
                else:
                    continue
                master.validfrom = s 
                master.validto = e
                mergedAddr.append(master)

            # Update crew_address records if they have changed
            self.crewDb.updateWithValidity(crewId, mergedAddr, CrewAddrRec.dbTable, CrewAddrRec.dbCrewFieldName)

            cRecs = []
            # Update employee phone number(s) in crew_contact.
            # Note that only the most recent information is updated.
            if len(mainRecs) > 0:
                lastValidRec = crewaddr[crewId][self.SUBTYP_MAIN].lastValidRec
                cRecs.append(CrewContactRec(crewId,"Tel","main",lastValidRec.phone))
                # If phone numbers exist in contact communication fields
                # these should be updated too.
                for n in [1,2,3,4]:
                    ct = eval("lastValidRec.c_comTyp%d" % n)
                    cn = eval("lastValidRec.c_comNumber%d" % n)
                    if cn != '':
                        if ct == 'MOB':
                            ccTyp = "Mobile"
                        elif ct == 'FAX':
                            ccTyp = 'FAX'
                        elif ct[:3] == 'TEL':
                            ccTyp = "Tel"
                        elif not ct:
                            ccTyp = "Tel"
                        ccWhich = "main%d" % n
                        cRecs.append(CrewContactRec(crewId,ccTyp,ccWhich,cn))

            # Update second phone number in crew_contact.
            # Note that only the most recent information is updated.
            if len(secRecs) > 0:
                sr = crewaddr[crewId][self.SUBTYP_SECOND].lastValidRec
                # Ignore sec. phone if validity date expired (WP FAT-INT 389)
                if AbsTime(strToTime(sr.validDateTo)) >= AbsTime(self.now):
                    cRecs.append(CrewContactRec(crewId,"Tel","secondary",sr.phone))

                for n in range(1, 5):
                    ct = getattr(sr, "c_comTyp%d" % n)
                    cn = getattr(sr, "c_comNumber%d" % n)
                    if cn != '':
                        if ct == 'MOB':
                            ccTyp = "Mobile"
                        elif ct == 'FAX':
                            ccTyp = 'FAX'
                        elif ct[:3] == 'TEL':
                            ccTyp = "Tel"
                        elif not ct:
                            ccTyp = "Tel"
                        ccWhich = "secondary%d" % n
                        cRecs.append(CrewContactRec(crewId,ccTyp,ccWhich,cn))

            # Submit all crew_contact updates, only update if changed
            self.crewDb.updateCrewContact(crewId, self.type, cRecs)

            # Update crew_relatives records if they have changed
            rRecs = []
            for rr in relRecs:
                rRecs.append(CrewRelativesRec(rr))
            self.crewDb.updateWithValidity(crewId, rRecs, CrewRelativesRec.dbTable, CrewRelativesRec.dbCrewFieldName)

        return nRecs


# ParseException ---------------------------------------------------------{{{2
class ParseException(errors.MessageError):
    def __init__(self, pnr, msg):
        self.msg = "Parse error for pnr=%s: %s" % (pnr, msg)
        errors.MessageError.__init__(self, self.msg)
    def __str__(self):
        return self.msg


# DbRec ------------------------------------------------------------------{{{2
class DbRec:
    """Database record objects"""
    def __init__(self, dbRec):
        # This constructor instantiates from db record
        for key,val in dbRec.items():
            setattr(self, key, val)
        self.si = CrewDb.tag

    def sameKeyAs(self, dbRec):
        if self.validfrom == dbRec['validfrom']:
            return True
        return False

    def existIn(self, dbRecs):
        for rec in dbRecs:
            if self.__dict__ == self.getUnicodeDict(rec):
                return True
        return False


# CrewRec ----------------------------------------------------------------{{{2
class CrewRec(DbRec):
    """Record corresponding to table crew"""
    dbTable = 'crew'

    def __init__(self,info):
        self.id = info.crewId
        try: self.name = info.lastName
        except: pass
        try: self.forenames = info.firstName
        except: pass
        try: self.logname = info.sasName
        except: pass
        try: self.birthday = strToDate(info.birthDate)
        except: pass
        try:
            if info.gender == "1":
                self.sex = "M"
            else:
                self.sex = "F"
        except: pass
        self.si = CrewDb.tag
        
    def getUnicodeDict(dbRec):
        return {'id': dbRec['id'],
                'name': xdecode(dbRec['name']),
                'forenames': xdecode(dbRec['forenames']),
                'logname': xdecode(dbRec['logname']),
                'birthday': dbRec['birthday'],
                'sex': dbRec['sex'],
                'si': dbRec['si']}
    getUnicodeDict = staticmethod(getUnicodeDict)


# CrewAttrRec ------------------------------------------------------------{{{2
class CrewAttrRec(DbRec):
    """Record corresponding to table crew_extra_info"""
    dbTable = 'crew_extra_info'
    dbCrewFieldName = 'id'

    def __init__(self,info):
        self.id = info.crewId
        self.validfrom = strToDate(info.validDateFrom)
        self.validto = strToDate(info.validDateTo)
        try: self.personalno = info.personnelId
        except: pass
        try: self.name = info.lastName
        except: pass
        try: self.forenames = info.firstName
        except: pass
        try: self.logname = info.sasName
        except: pass
        try: self.nationality = info.nationality
        except: pass
        try: self.nationality2 = info.nationality2
        except: pass
        try:
            if info.empCountry == "09":        # DK
                if info.maritalstatus=="1": self.maritalstatus = "Ogift"
                elif info.maritalstatus=="2": self.maritalstatus = "Gift"
                elif info.maritalstatus=="3": self.maritalstatus = "Sambo"
                elif info.maritalstatus=="": self.maritalstatus = ""
                elif info.maritalstatus=="0": self.maritalstatus = ""
            else:
                if info.maritalstatus=="1": self.maritalstatus = "Gift"
                elif info.maritalstatus=="2": self.maritalstatus = "Ogift"
                elif info.maritalstatus=="3": self.maritalstatus = "Sambo"
                elif info.maritalstatus=="": self.maritalstatus = ""
                elif info.maritalstatus=="0": self.maritalstatus = ""
        except: pass
        self.si = CrewDb.tag

    def getUnicodeDict(dbRec):
        return {'id': dbRec['id'],
                'validfrom': dbRec['validfrom'],
                'validto': dbRec['validto'],
                'personalno': xstr(dbRec['personalno']),
                'name': xdecode(dbRec['name']),
                'forenames': xdecode(dbRec['forenames']),
                'logname': xdecode(dbRec['logname']),
                'nationality': xstr(dbRec['nationality']),
                'nationality2': xstr(dbRec['nationality2']),
                'maritalstatus': dbRec['maritalstatus'],
                'si': dbRec['si']}
    getUnicodeDict = staticmethod(getUnicodeDict)


# CrewAddrRec ------------------------------------------------------------{{{2
class CrewAddrRec(DbRec):
    """Crew main address (subtype 1) or crew second address (subtype 2)
       Record corresponding to table crew_address
    """
    dbTable = 'crew_address'
    dbCrewFieldName = 'crew'

    def getUnicodeDict(dbRec):
        return {'crew': dbRec['crew'],
                'validfrom': dbRec['validfrom'],
                'validto': dbRec['validto'],
                'street': xdecode(dbRec['street']),
                'street1': xdecode(dbRec['street1']),
                'city': xdecode(dbRec['city']),
                'city1': xdecode(dbRec['city1']),
                'postalcode': xdecode(dbRec['postalcode']),
                'postalcode1': xdecode(dbRec['postalcode1']),
                'country': xstr(dbRec['country']),
                'country1': xstr(dbRec['country1']),
                'si': dbRec['si']}
    getUnicodeDict = staticmethod(getUnicodeDict)


# CrewMainAddrRec --------------------------------------------------------{{{2
class CrewMainAddrRec(CrewAddrRec):
    def __init__(self,info):
        self.crew = info.crewId
        self.validfrom = strToTime(info.validDateFrom)
        self.validto = strToTime(info.validDateTo)
        self.street1 = self.city1 = self.postalcode1 = u''
        self.country1 = ''
        self.street = ', '.join((info.co,info.street)).strip(', ')
        self.city = info.city
        self.postalcode = info.postalCode
        self.country = info.country
        self.si = CrewDb.tag

    def mergeSecondAddr(self, other):
        """Merge second address attributes into a main address record"""
        if not other is None:
            self.street1 = other.street1
            self.city1 = other.city1
            self.postalcode1 = other.postalcode1
            self.country1 = other.country1


# CrewSecAddrRec ---------------------------------------------------------{{{2
class CrewSecAddrRec(CrewAddrRec):
    def __init__(self,info):
        self.crew = info.crewId
        self.validfrom = strToTime(info.validDateFrom)
        self.validto = strToTime(info.validDateTo)
        # nonnull constraints in crew_address
        self.street = self.city = u'.'
        self.postalcode = u''
        self.country = ' '
        self.street1 = ', '.join((info.co,info.street)).strip(', ')
        self.city1 = info.city
        self.postalcode1 = info.postalCode
        self.country1 = info.country
        self.si = CrewDb.tag


# CrewContactRec ---------------------------------------------------------{{{2
class CrewContactRec(DbRec):
    """Record corresponding to table crew_contact"""
    dbTable = 'crew_contact'

    def __init__(self,id,typ,which,val):
        self.crew = id
        self.typ = typ
        self.which = which
        self.val = val
        self.si = CrewDb.tag
        
    def getUnicodeDict(dbRec):
        return {'crew': dbRec['crew'],
                'typ': dbRec['typ'],
                'which': dbRec['which'],
                'val': xdecode(dbRec['val']),
                'si': dbRec['si']}
    getUnicodeDict = staticmethod(getUnicodeDict)


# CrewRelativesRec -------------------------------------------------------{{{2
class CrewRelativesRec(DbRec):
    """Record corresponding to table crew_relatives"""
    dbTable = 'crew_relatives'
    dbCrewFieldName = 'crew'

    def __init__(self,info):
        self.crew = info.crewId
        self.subtype = info.seqno
        self.validfrom = strToTime(info.validDateFrom)
        self.validto = strToTime(info.validDateTo)
        self.co_name = info.c_co
        self.street = info.c_street
        self.appartment = info.c_address2
        self.postalcode = info.c_postalCode
        self.city = info.c_city
        self.city_quarter = info.c_stadsdel
        self.phone = info.c_phone
        self.com_number1 = info.c_comNumber1
        self.com_number2 = info.c_comNumber2
        self.com_number3 = info.c_comNumber3
        self.com_number4 = info.c_comNumber4
        self.com_type1 = info.c_comTyp1
        self.com_type2 = info.c_comTyp2
        self.com_type3 = info.c_comTyp3
        self.com_type4 = info.c_comTyp4
        self.si = CrewDb.tag

    def getUnicodeDict(dbRec):
        return {'crew': dbRec['crew'],
                'subtype': dbRec['subtype'],
                'validfrom': dbRec['validfrom'],
                'validto': dbRec['validto'],
                'co_name': xdecode(dbRec['co_name']),
                'street': xdecode(dbRec['street']),
                'appartment': xdecode(dbRec['appartment']),
                'postalcode': xdecode(dbRec['postalcode']),
                'city': xdecode(dbRec['city']),
                'city_quarter': xdecode(dbRec['city_quarter']),
                'phone': xstr(dbRec['phone']),
                'com_number1': xdecode(dbRec['com_number1']),
                'com_number2': xdecode(dbRec['com_number2']),
                'com_number3': xdecode(dbRec['com_number3']),
                'com_number4': xdecode(dbRec['com_number4']),
                'com_type1': xstr(dbRec['com_type1']),
                'com_type2': xstr(dbRec['com_type2']),
                'com_type3': xstr(dbRec['com_type3']),
                'com_type4': xstr(dbRec['com_type4']),
                'si': dbRec['si']}
    getUnicodeDict = staticmethod(getUnicodeDict)

    def sameKeyAs(self, dbRec):
        if self.validfrom==dbRec['validfrom'] and self.subtype==dbRec['subtype']:
            return True
        return False


# CrewDb -----------------------------------------------------------------{{{2
class CrewDb:
    tag = "DIG HR-sync"
    MINDATE = "19000101"
    MAXDATE = "20351231"
    encoding = "latin-1"

    def __init__(self, dbconn, logger):
        self.dbconn = dbconn
        self.logger = logger
        self.ops = []
        self.unknownPerkeys = None


    def getCrewId(self, extperkey, validfrom, validto):
        """ This method returns a tuple containing crewid and a list
            of valid periods. Each period is a tuple of (from,to).
            In order for a period to be valid it must be fully part of
            the validity periods of both the incoming record and a 
            crew_employment record connecting the extperkey and crewid.
            If no crewid is found for the given period, None
            is returned.
            For ambiguous extperkeys, i.e. those defined for more than
            one crew id, the last defined crew id is returned.
        """
        crewId = None
        validCrew = None
        periods = {}
        search = dave.DaveSearch('crew_employment', [('extperkey','=',extperkey)])
        for rec in self.dbconn.runSearch(search):
            crewId = rec['crew']
            if not crewId in periods:
                periods[crewId] = []
            if validCrew is None:
                validCrew = (crewId,rec['validfrom'])
            vId, vFrom = validCrew
            if crewId != vId:
                self.logger.error("Ambiguous perkey %s defined for both crew %s and %s" % (extperkey, vId, crewId))
            if rec['validfrom'] > vFrom:
                vId = crewId
                validCrew = (vId,rec['validfrom'])
            if rec['validfrom'] < validto and rec['validto'] > validfrom:
                # Overlap found, calculate the overlapping period
                periods[crewId].append((max(rec['validfrom'],validfrom), min(rec['validto'],validto)))
        if crewId is None:
            return None, []
        return vId, periods[vId]


    def getLastValidPerkey(self, crewId):
        """ This method returns the extperkey associated with the given
            crewId. If there are more than one, it returns the one with
            the most recent validity.
        """
        hiValidto = 0
        perkey = None
        search = dave.DaveSearch('crew_employment', [('crew','=',crewId)])
        for rec in self.dbconn.runSearch(search):
            if rec['validto'] > hiValidto:
                perkey = rec['extperkey']
                hiValidto = rec['validto']
        self.logger.debug("crew=%s lastValidPerkey=%s" % (crewId, perkey))
        return perkey


    def getCrew(self, crewId=None):
        filter = []
        if not crewId is None:
            filter.append(('id','=',crewId))
        search = dave.DaveSearch('crew', filter)
        return self.dbconn.runSearch(search)


    def updateCrew(self, map):
        self.makeRecord('crew', 'W', map)


    def updateWithValidity(self, crew, iRecs, table, crewFieldName):
        """ Update records in tables with validity periods.
            Existing records are deleted if validity period doesn't match.
            Incoming records are updated if they differ from existing.
        """
        if len(iRecs) == 0:
            return
        # Get start and end of update period,
        # note that iRecs must be sorted...
        pStart = iRecs[0].validfrom
        pEnd = iRecs[len(iRecs)-1].validto
        search = dave.DaveSearch(table, [
                (crewFieldName, '=', crew),
                ('validto', '>', pStart),
                ('validfrom', '<', pEnd)
                ])
        dbRecs = self.dbconn.runSearch(search)
        for rec in dbRecs:
            if rec['validfrom'] < pStart:
                rec['validto'] = pStart
                self.makeRecord(table, 'U', rec)
            elif not self._hasKey(rec, iRecs):
                self.makeRecord(table, 'D', rec)
        for irec in iRecs:
            if not irec.existIn(dbRecs):
                self.makeRecord(table, 'W', irec.__dict__)


    def _hasKey(self, dbRec, iRecs):
        """ Check if a certain key (excluding crewId) exists in indata """
        for rec in iRecs:
            if rec.sameKeyAs(dbRec):
                return True
        return False


    def updateCrewContact(self, crew, msgtyp, cRecs):
        """ Update crew contacts relevant for the actual message type.
        """
        # Filter out duplicates (cases where e.g. more than one 'TEL2'
        # communication number has been specified)
        cfRecs = []
        for crec in cRecs:
            for cfrec in cfRecs:
                if cfrec.which==crec.which and cfrec.typ==crec.typ:
                    self.logger.warning("Duplicate contact crew=%s typ=%s which=%s" % (crew, crec.typ, crec.which))
                    break
            else:
                cfRecs.append(crec)

        search = dave.DaveSearch('crew_contact', [('crew','=',crew)])
        dbRecs = self.dbconn.runSearch(search)
        # Delete records existing in db but not in indata
        for rec in dbRecs:
            if (rec['typ']=='Email') == (msgtyp==MSGTYP_PERS):
                found = False
                for cfrec in cfRecs:
                    if cfrec.__dict__ == cfrec.getUnicodeDict(rec):
                        found = True
                        break
                if not found:
                    rec['val'] = rec['val'].decode(CrewDb.encoding)
                    self.makeRecord('crew_contact', "D", rec)
        # Insert records existing in indata but not in db
        for cfrec in cfRecs:
            if not cfrec.existIn(dbRecs) and cfrec.val != "":
                self.makeRecord('crew_contact', 'W', cfrec.__dict__)


    def updateUnknownCrew(self, info):
        if self.unknownPerkeys is None:
            self.unknownPerkeys = set()
            # Get existing UNKNOWNs from db to avoid unnecessary updates
            search = dave.DaveSearch('crew_unknown', [('corrected','=','N')])
            for rec in self.dbconn.runSearch(search):
                self.unknownPerkeys.add(rec['extperkey'])
        if info.pnr in self.unknownPerkeys:
            return

        crewMap = {'extperkey': info.pnr,
                   'empcountry': info.empCountry,
                   'corrected': False,
                   'name': info.lastName,
                   'forenames': info.firstName}
        self.logger.debug("Writing crew_unknown for perkey %s" % (info.pnr))
        self.makeRecord('crew_unknown', 'W', crewMap)
        self.unknownPerkeys.add(info.pnr)


    def deleteCorrectedUnknownCrew(self):
        search = dave.DaveSearch('crew_unknown', [('corrected','=','Y')])
        for rec in self.dbconn.runSearch(search):
            # We must check that it is not just marked 'corrected', 
            # but still actually unknown..
            if rec['extperkey'] not in self.unknownPerkeys:
                self.logger.debug("Deleting crew_unknown for perkey %s" % (rec['extperkey']))
                del rec['corrected']
                del rec['si']
                rec['name'] = xdecode(rec['name'])
                rec['forenames'] = xdecode(rec['forenames'])
                self.makeRecord('crew_unknown', 'D', rec)
        

    def makeRecord(self, entity, op, map):
        oper = dave.createOp(entity,op,map.copy())
        self.ops.append(oper)
        return oper


# functions =============================================================={{{1
# strToDate =============================================================={{{2
def strToDate(strDate):
    date = int(AbsDate(strDate)) / 1440

    return date

# strToTime =============================================================={{{2
def strToTime(strTime):
    time = int(AbsTime(strTime))

    return time 

def validDate(strDate):
    """
    Convert date which is outside the supported scope
    """
    if strDate:
        if strDate >= "20991231":
            strDate = "20991231"
        if strDate <= "19010101":
            strDate = "19010101"
    return strDate

# getAggregates =========================================================={{{2
def getAggregates(recList):
    """ 
    Calculate aggregated periods according to the following example:
     
      recList1:     |-----|------------|---------|-------|
      recListn:             |------|-------|-----|-----------|
      Aggreg:       |-----|-|------|---|---|-----|-------|---|
    """
    times = set()
    for r in recList:
        if 'validfrom' in r.__dict__:
            times.add(r.validfrom)
            times.add(r.validto)
        elif 'validDateFrom' in r.__dict__:
            (s,e) = r.getInterval()
            times.add(s)
            times.add(e)
        else:
            raise Exception("Programming error. getAggregates called with objects of type: %s" % (r.__class__))
    ltimes = list(times)
    ltimes.sort()
    idx = 0
    periods = []
    while idx < len(ltimes)-1:
        periods.append((ltimes[idx], ltimes[idx+1]))
        idx += 1
    return periods


# getOverlapAddrRec ======================================================{{{2
def getOverlapAddrRec((start,end), recList):
    """ Looks through a list of non-overlapping Address Info records
        and returns the one overlapping the given period. The list
        may contain either CrewAddressInfo (raw) records or CrewAddrRec
        (database formatted) records but the returned record is
        always of type CrewAddrRec.
    """
    overlap = None
    for r in recList:
        if isinstance(r, CrewAddrRec):
            if start >= r.validfrom and end <= r.validto:
                overlap = r
                break
        elif isinstance(r, CrewAddressInfo):
            (s,e) = r.getInterval()
            if start >= s and end <= e:
                if r.subtype == '1':
                    overlap = CrewMainAddrRec(r)
                else:
                    overlap = CrewSecAddrRec(r)
                break
        else:
            raise Exception("Programming error. getOverlapAddrRec called with objects of type: %s" % (r.__class__))
    return overlap


# xdecode ================================================================{{{2
def xdecode(ustr):
    if ustr is None:
        return u''
    return ustr.decode(CrewDb.encoding)


# xstr ==================================================================={{{2
def xstr(ustr):
    if ustr is None:
        return ''
    return ustr


# format ================================================================={{{1

# spec -------------------------------------------------------------------{{{2
# message ::= { records } 
#
# record type Personal Info:
#------------------------------------------------------------------------
# Personnel             CHAR(8)          "PERNR"
# Valid-date-from       CHAR(8)          CCYYMMDD
# Valid-date-to         CHAR(8)          CCYYMMDD        
# EmpCountry            CHAR(2)          09=DK, 23=SV, 20=NO, 99=International
# Last name             CHAR(40) 
# First name            CHAR(40)
# SAS name              CHAR(40)
# Gender                CHAR(1)          1=male, 2=female
# Personnel ID#         integer(12)      CCYYMMDDnnnn
# Birth date            CHAR(8)          CCYYMMDD
# Nationality           CHAR(3) 
# Nationality 2         CHAR(3) 
# Marital status        CHAR(1)          SE/NO: 1=gift, 2=ogift, 3=sambo
#                                        DK: 1=ogift, 2=gift
# E-mail address        CHAR(80)
# Retirement date       CHAR(8)          CCYYMMDD
#------------------------------------------------------------------------
#
# record type Address Info:
#------------------------------------------------------------------------
# Personnel            CHAR(8)          "PERNR"
# Valid-date-from      CHAR(8)          CCYYMMDD
# Valid-date-to        CHAR(8)          CCYYMMDD        
# Subtype              CHAR(4)          1=Info about employee main address
#                                       2=Info about employee second address
#                                       4=Contact person 1 info
#                                       5=Contact person 2 info (Not used)
# Seqno                CHAR(3)          Distinguishes different contact persons
#                                       Only applicable to Subtype=4
# EmpCountry           CHAR(2)          09=DK, 23=SV, 20=NO, 99=International
# C/o address          CHAR(40)        
# Street address       CHAR(60)
# Postal code          CHAR(10)
# City                 CHAR(40)
# Country              CHAR(3)        
# Phone                CHAR(14)        
# Contact C/o address  CHAR(40)        
# Contact Street addr  CHAR(60)
# Contact Additional   CHAR(40)
# Contact Postal code  CHAR(10)
# Contact City         CHAR(40)
# Contact Stadsdel     CHAR(40)
# Contact Phone        CHAR(14)
# Contact Comm type1   CHAR(4)           01=Phone 2, 02=Mobile phone, 03=Telex, 04=Other
# Contact Comm type2   CHAR(4)           01=Phone 2, 02=Mobile phone, 03=Telex, 04=Other
# Contact Comm type3   CHAR(4)           01=Phone 2, 02=Mobile phone, 03=Telex, 04=Other
# Contact Comm type4   CHAR(4)           01=Phone 2, 02=Mobile phone, 03=Telex, 04=Other
# Contact Comm number1 CHAR(20)
# Contact Comm number2 CHAR(20)
# Contact Comm number3 CHAR(20)
# Contact Comm number4 CHAR(20)
# Retirement date      CHAR(8)           CCYYMMDD
#------------------------------------------------------------------------

# sample ------------------------------------------------------------------{{{2
#         1         2         3         4         5         
# 1234567890123456789012345678901234567890123456789012345687
# ----------------------------------------------------------
#

# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof

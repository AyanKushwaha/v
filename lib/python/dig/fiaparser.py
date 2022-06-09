"""
Customized parser for flight owner information imported from FIA system.
Incoming data is imported to table meal_flight_owner. In addition, owner is
updated in meal_flight_owner table.
"""

import struct

import carmensystems.dig.framework.carmentime as carmentime
import carmensystems.dig.framework.dave as dave
 

from AbsDate import AbsDate
from carmensystems.dig.framework.handler import MessageHandlerBase, CallNextHandlerResult
from carmensystems.dig.framework import errors
from carmensystems.dig.messagehandlers.dave import DaveContentType
from carmensystems.dig.messagehandlers.reports import metaReports, metaDelta


ALL_DAYS = 0

class FIAParser(MessageHandlerBase):
    """
    The FIAParser gets one line at the time. Each line contains information
    about ownership of a flight route with dates.  A new import invalidates all
    older records in the database, so they are deleted.
    """
    def __init__(self, name=None):
        super(FIAParser, self).__init__(name)
        self.errors = []

    def addError(self, errorstr):
        """ Adds an error to the internal error list"""
        self.errors.append(errorstr)

    def clearErrors(self):
        """ Clears the internal error list"""
        self.errors = []
    
    def createReportDict(self, message):
        """ Adds a report dictionary to the list. This is done by using the metadata dictionary
            in the message. It has two value metaDelta where the database operations are kept
            and metaReports where the report dictionary are kept.
        
         """
        
        message.metadata[metaDelta] = {'content': (None, None, self.ops),
                                       'content-type': DaveContentType()} 

        if len(self.errors) == 0:
            message.metadata[metaReports] = []
        else:
            message.metadata[metaReports] = [{'content': '\n'.join(self.errors),
                                              'content-type': 'text/plain',
                                              'destination': [("FLIGHT_OWNER", {'subtype':'ERROR',
                                                                                'subject': 'ERROR: Inconsistency in flight owner file'})]}] 
    
    def handle(self, message):
        """ Main method used for each incoming message """
        
        self._services.logger.info("Started...")
        self.ops = []

        validator = FIAValidator()
        dbMap = {}  # A map with all entries in the database
        
        for rec in self._services.getDaveConnector().runSearch(dave.DaveSearch('meal_flight_owner', [])):
            dbMap[(rec['fd'], rec['legno'], rec['adep'], rec['ades'], rec['validfrom'], rec['doop'])] = rec

        szRec = struct.calcsize(FIALine.format)
        nSuccRec = 0
        for line in message.content.splitlines():

            if not line: 
                continue

            line = line.ljust(szRec)
            try:
                fields = [x for x in struct.unpack(FIALine.format, line)]
                fiaLine = FIALine(fields)
            except Exception, e:
                self.addError('Failed to parse line: %s' % (str(line)))
                self._services.logger.error("Skipping record: %s" % line)
                continue

            # Only consider M (Master) records, A and D shall not be considered
            if fiaLine.flttype != 'M':
                continue

            # One line results in one db entry per day of operation
            for rec in fiaLine.getDbRecords():
             
                if not validator.check_and_add(rec):
                    self._services.logger.debug("Overlapping period. Line not added: %s" % (line))
                    self.addError('Overlapping period. Line not added: %s' % (str(line)))
                    break # Skip the rest of the line if a overlap is found
             
                # Only update if changed
                if not rec.isSameAs(dbMap.get(rec.getKey(), {})):
                    self._services.logger.debug("Writing record: %s" % rec)
                    self.ops.append(dave.createOp('meal_flight_owner', "W", rec.getDbRecord()))
    
                # If exists in dbMap, remove it
                dbMap.pop(rec.getKey(), {})
                nSuccRec += 1

        # Avoid wiping records if empty update
        if nSuccRec > 0:
            # Delete records existing in DB but not in msg
            for dbRec in dbMap.values():
                self._services.logger.debug("Deleting record: %s,%s,%s,%s,%s,%s" % (dbRec['fd'], dbRec['legno'], dbRec['adep'], dbRec['ades'], dbRec['validfrom'], dbRec['doop']))
                self.ops.append(dave.createOp('meal_flight_owner', "D", dbRec))

        
        # We will later on use the UserConfigurableDispatcher and it uses reports as inputs. We will
        # emulate the output of a report in order to use it without modifications
        self.createReportDict(message)
        self.clearErrors()

            
        message.setContent((None, None, self.ops), DaveContentType())
        self._services.logger.info("...Finished")
        return CallNextHandlerResult()


class FIAValidator:
    """ Used for validating the input of the FIA file e.g. duplicate entries or 
        overlapping entries
    """
    
    
    def __init__(self):
        self.records = {}
    
    def check_and_add(self, fiaRecord):
        """ Checks if an entry may be added and returns True is it may be added
            otherwise false.
        """

        if not isinstance(fiaRecord, FIARecord):
            raise Exception("Invalid type, expected FIARecord")
        
        if fiaRecord.fltno in self.records:
            for record in self.records[fiaRecord.fltno]:
                                
                if ((record.datefrom <= fiaRecord.dateto and record.datefrom >= fiaRecord.datefrom) or \
                    (record.dateto <= fiaRecord.dateto and record.dateto >= fiaRecord.datefrom) or \
                    (record.dateto >= fiaRecord.dateto and record.datefrom <= fiaRecord.datefrom)) and \
                    (record.doop == fiaRecord.doop or record.doop == ALL_DAYS or fiaRecord.doop == ALL_DAYS) and \
                    (record.stn_from == fiaRecord.stn_from) and \
                    (record.stn_to == fiaRecord.stn_to) and \
                    (record.legno == fiaRecord.legno):
                    return False

            self.records[fiaRecord.fltno].append(fiaRecord)
            return True   
        else:
            self.records[fiaRecord.fltno] = [fiaRecord]
            return True


class FIARecord:
    """ Represents a FIA Record, a FIA Line may consist of many records """
    
    def __init__(self, region, datefrom, dateto, fltno, stn_from, stn_to,
                 bap, doop, airldesg, rst, rs, rz, ra, rsa, grp, flttype, legno):
        
        self.region = region
        self.datefrom = datefrom 
        self.dateto = dateto 
        self.fltno = fltno 
        self.stn_from = stn_from
        self.stn_to = stn_to
        self.bap = bap
        self.doop = doop
        self.airldesg = airldesg
        self.rst = rst
        self.rs = rs
        self.rz = rz
        self.ra = ra
        self.rsa = rsa
        self.grp = grp
        self.flttype = flttype
        self.legno = legno
    
        self.checkKey("fltno", self.fltno)
        self.checkKey("adep", self.stn_from)
        self.checkKey("ades", self.stn_to)
        self.checkKey("doop", self.doop)
        self.checkKey("legno", self.legno)


    def __str__(self):
        return "%s %s %s-%s %s-%s %s %s" % (self.fltno, self.legno, self.stn_from, self.stn_to, self.datefrom,
                                         self.dateto, self.doop, self.region)

    def getDbRecord(self):
        """ Gets a record formatted to insert as a dave operation """ 
                
        return {'region': self.region,
                'validfrom': self.datefrom,
                'validto': self.dateto,
                'fd': self.fltno,
                'adep': self.stn_from,
                'ades': self.stn_to,
                'bap': self.bap,
                'doop': self.doop,
                'airldesg': self.airldesg,
                'rst': self.rst,
                'rs': self.rs,
                'rz': self.rz,
                'ra': self.ra,
                'rsa': self.rsa,
                'grp': self.grp,
                'flttype': self.flttype,
                'legno': self.legno}   

    
    def isSameAs(self, d):
        """ Compares a record to a entry map """
        try:
            if self.bap == self.xstr(d['bap']) and \
                self.datefrom == d['validfrom'] and \
                self.dateto == d['validto'] and \
                self.doop == int(d['doop']) and \
                self.airldesg == self.xstr(d['airldesg']) and \
                self.rst == self.xstr(d['rst']) and \
                self.rs == self.xstr(d['rs']) and \
                self.rz == self.xstr(d['rz']) and \
                self.ra == self.xstr(d['ra']) and \
                self.rsa == self.xstr(d['rsa']) and \
                self.grp == self.xstr(d['grp']) and \
                self.fltno == d['fd'] and \
                self.flttype == self.xstr(d['flttype']) and \
                self.stn_from == d['adep'] and \
                self.stn_to == d['ades'] and \
                self.legno == int(d['legno']) and \
                self.region == self.xstr(d['region']):
                return True
        except:
            pass
        return False

    def getKey(self):
        """ Gets the primary key of the record """
        return (self.fltno, self.legno, self.stn_from, self.stn_to, self.datefrom, self.doop)

    @staticmethod
    def checkKey(name, value):
        """ Checks that the primary key is valid """
        if value is None or (isinstance(value, str) and value.strip() == ''):
            raise Exception("Key field %s is empty." % name)
    
    @staticmethod
    def xstr(ustr):
        """ Safety function, always returns a string even if input is None """
        if ustr is None:
            return ''
        return ustr


class FIALine:
    """
    Repesents a line in the FIA file. Each line may result in many database records.
    For record layout see section 'format' at the bottom of this file.
    """
    format = "1s 10s 10s 7s 3s 16s 5s 16s 5s 16s 5s 16s 5s 16s 5s 16s 5s 16s 8s 1s 5s 5s 3s"

    def __init__(self, f):
        self.bap = f[0]
        self.datefrom = self.strToDate(f[1])
        self.dateto = self.strToDate(f[2])
        self.doop = f[3].replace(' ', '') # Remove all blanks for safety
        self.airldesg = f[4]
        self.airldesgstext = f[5]
        self.rst = f[6].strip()
        self.rststext = f[7]
        self.rs = f[8].strip()
        self.rsstext = f[9]
        self.rz = f[10].strip()
        self.rzstext = f[11]
        self.ra = f[12].strip()
        self.rastext = f[13]
        self.rsa = f[14].strip()
        self.rsastext = f[15]
        self.grp = f[16].strip()
        self.grpstexr = f[17]
        self.fltno = f[18]
        self.flttype = f[19].strip()
        self.stn_from = f[20].strip()
        self.stn_to = f[21].strip()
        self.legno = f[22].strip()
        # Convert RSS to SKS, RSD to SKD, ...
        if self.rs.upper() in ('RSI', 'RSD', 'RSS', 'RSN'):
            self.region = "SK" + self.rs[2]
        else:
            self.region = ""

        
    def getDbRecords(self):
        """ 
        A generator function is used for iterating over the database records in a line
        """ 
        
        if self.doop == "1234567":
            yield FIARecord(self.region,
                            self.datefrom,
                            self.dateto,
                            self.fltno,
                            self.stn_from,
                            self.stn_to,
                            self.bap,
                            ALL_DAYS,
                            self.airldesg,
                            self.rst,
                            self.rs,
                            self.rz,
                            self.ra,
                            self.rsa,
                            self.grp,
                            self.flttype,
                            int(self.legno))
                
        else:
            for day in self.doop:
                yield FIARecord(self.region,
                                self.datefrom,
                                self.dateto,
                                self.fltno,
                                self.stn_from,
                                self.stn_to,
                                self.bap,
                                int(day),
                                self.airldesg,
                                self.rst,
                                self.rs,
                                self.rz,
                                self.ra,
                                self.rsa,
                                self.grp,
                                self.flttype,
                                int(self.legno))

    @staticmethod
    def strToDate(strDate):
        """
        Converts date string YYYY-mm-dd to days since carmen epoch
        """
        if strDate > "2099-12-30":
            strDate = "2099-12-30"
        if strDate < "1901-01-01":
            strDate = "1901-01-01"
    
        date = int(AbsDate(strDate.replace('-', ''))) / 1440

        return date
                

# spec -------------------------------------------------------------------{{{2
# message ::= { records } 
# record:
#
# region,fd,validfrom,validto,adep,ades
#
# BAP           CHR(1)  B=budget,A=actual,P=prognosis
# DATEFROM      CHR(10) Date (YYYY-MM-DD), ownership from this date
# DATETO        CHR(10) Date (YYYY-MM-DD), ownership to this date
# DOOP          CHR(7)  Day of operation e.g. 1234567 (?)
# AIRLDESG      CHR(3)  Airline designator e.g. SAS
# AIRLDESGSTEXT CHR(16) Text for AIRLDESG
# RST           CHR(5)  Route Sector Total e.g. SKA
# RSTSTEXT      CHR(16) Text for RST
# RS            CHR(5)  Route Sector e.g. RSI
# RSSTEXT       CHR(16) Text for RS
# RZ            CHR(5)  Route Zone e.g. IB
# RZSTEXT       CHR(16) Text for RZ
# RA            CHR(5)  Route Area e.g. OF
# RASTEXT       CHR(16) Text for RA
# RSA           CHR(5)  Route sub Area e.g. 0IB
# RSASTEXT      CHR(16) Text for RSA
# GRP           CHR(5)  Group number e.g. 055
# GRPSTEXR      CHR(16) Text for GRP
# FLTNO         CHR(8)  Flight number e.g. SK 3500
# FLTTYPE       CHR(1)  M=Master,D=diversion,A=alternative
# STN-FROM      CHR(5)  Departure station
# STN-TO        CHR(5)  Arrival station
# LEGNO         CHR(3)  Leg number e.g. 001

# sample ------------------------------------------------------------------{{{2
#
#A2006-03-269999-12-311234567SASSAS             SKA  ROUTE SECT TOTALRSI  INTERCONTINENTALIB   INTERC BL.SPACE 0F   INTERC BL.SPACE 0IB  ASIA BL.SPACE   055  BKK-SIN BL.SPACESK 3500 MBKK  SIN  001
#A2006-03-269999-12-311234567SASSAS             SKA  ROUTE SECT TOTALRSI  INTERCONTINENTALIB   INTERC BL.SPACE 0F   INTERC BL.SPACE 0IB  ASIA BL.SPACE   055  BKK-SIN BL.SPACESK 3501 MSIN  BKK  001
#A2006-11-019999-12-311234567SASSAS             SKA  ROUTE SECT TOTALRSD  DENMARK         DB   DENMARK BL.SPACE1G   DENMARK BL.SPACE1DB  DENMARK BL.SPACE051  CPH-MOW BL.SPACESK 8700 MSVO  CPH  001
#A2006-11-019999-12-311234567SASSAS             SKA  ROUTE SECT TOTALRSD  DENMARK         DB   DENMARK BL.SPACE1G   DENMARK BL.SPACE1DB  DENMARK BL.SPACE051  CPH-MOW BL.SPACESK 8701 MCPH  SVO  001
#A2006-11-019999-12-311234567SASSAS             SKA  ROUTE SECT TOTALRSS  SWEDEN          SB   SWEDEN BL.SPACE 3G   SWEDEN BL.SPACE 3SB  SWEDEN BL.SPACE 052  STO-MOW BL.SPACESK 8702 MSVO  ARN  001
#A2006-11-019999-12-311234567SASSAS             SKA  ROUTE SECT TOTALRSS  SWEDEN          SB   SWEDEN BL.SPACE 3G   SWEDEN BL.SPACE 3SB  SWEDEN BL.SPACE 052  STO-MOW BL.SPACESK 8703 MARN  SVO  001

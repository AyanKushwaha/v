

import carmusr.AuditTrail as AuditTrail
from carmusr.AuditTrail import SearchSimple
from carmusr.AuditTrail import SearchBetween
from carmusr.AuditTrail import ChangeObject
import AbsDate
import RelTime
import AbsTime
import time

import profile

import tempfile
import traceback
import os
import Dates
import carmensystems.rave.api as r
import Cui
import Csl

import carmensystems.dave.dmf as dmf
import modelserver as M
from tm import TM


class TripAuditTrail(object):
    def __init__(self):
        self._conn, self._entityConn = self.getConnection()
    
    def __del__(self):
        """
        De-constructor, closes the connections that was opened against the database
        """
        self._conn.close()
        self._entityConn.close()

    def getAuditTrail(self, headerRows):
        """
        Returns the audit trail defined in getAuditAreas as a list of strings
        """
        areas = self.getAuditAreas()
        trailRows = []
        if headerRows:
            trailRows.extend(headerRows)

        for area in areas.keys():
            trailRows.append(area + ':')
            changes = []
            for auditType in areas[area]:
                for audit in auditType:
                    changes += audit.getAuditTrail(self._conn)
            trailRows.extend(self.printChanges(changes))
            trailRows.append(" ")
        return trailRows

    def getAuditAreas(self):
        """
        Returns a dict of AuditTrail objects, grouped by their Area.
        This method essentially decides what the audit trail is to be run on
        It is considered an error not to have a atleast one search criteria defined
        """

        trip_udor = Cui.CuiCrcEvalInt(Cui.gpc_info, Cui.CuiWhichArea, "object", "trip_udor")
        trip_uuid = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object", "trip_uuid")


        tripID = SearchSimple('udor', '=', AbsDate.AbsDate(trip_udor*1440))
        tripUUID = SearchSimple('id', '=', trip_uuid)

        tripID2 = SearchSimple('trip_udor', '=', AbsDate.AbsDate(trip_udor*1440))
        tripUUID2 = SearchSimple('trip_id', '=', trip_uuid)
            
        tripTrail = TripAudit(self._entityConn, 'trip', [tripID, tripUUID])
        tripFlightTrail = TripFlightDutyAudit(self._entityConn, 'trip_flight_duty', [tripID2, tripUUID2])
        tripGroundTrail = TripGroundDutyAudit(self._entityConn, 'trip_ground_duty', [tripID2, tripUUID2])
        
        return {"Trips": [[tripTrail, tripFlightTrail, tripGroundTrail]]}
        
    
    def getConnection(self):
        """
        Returns the connections to the schema, both at Dave L1 and Entity Level
        """
        m = M.TableManager.instance()
        e = dmf.EntityConnection()
        e.open(m.getConnStr(), m.getSchemaStr())
        return (dmf.Connection(m.getConnStr()), e)
    

    def printChanges(self, changes):
        """
        Produces the textual report of all changes within an Audit Trail Area
        """
        changes.sort(ChangeObject.compare)
        changeRow = []
        changesAlreadyProcessed = []
        lastTime = ""
        for change in changes:
            # Check if change has already been processed.
            # Same change can occur multiple times due to touch statement in time period check.
            if [change.thisRevision.getPK(),change.thisRevision.revid] in changesAlreadyProcessed:
                continue
            changeType = change.getChangeType()
            time = str(AbsTime.AbsTime(change.thisRevision.committs/60))[:-6]
            if changeType in ['added', 'removed']:
                if time != lastTime:
                    lastTime = time
                    changeRow.append(' '  + time + ':')    
                changeRow.append('    ' + change.getEntityText())
            else:
                changeString = change.getChangeString()
                if not changeString:
                    continue
                if time != lastTime:
                    lastTime = time
                    changeRow.append(' ' + time + ':')                   
                changeRow.append('    ' + change.getEntityText())
                changeRow.append('          (changes: '+  changeString + ')')
            changesAlreadyProcessed.append([change.thisRevision.getPK(),change.thisRevision.revid])

        if not changeRow:
            changeRow.append('     No changes made matching the specified intervals.')
        return changeRow


class TripAudit(AuditTrail.AuditTrailBase):
    """
    Class that will perform an audit trail on base breaks.
    """
    
    def __init__(self, entityConn, table, search):
        """
        Constructor that will initialize the AuditTrail object
        """
        self.table = table
        AuditTrail.AuditTrailBase.__init__(self, entityConn, table, None, None, search, noJoinTables=['crew_base_set'])
        self.setEntityTextClass(self)
        self.setChangeStringClass(self)

        self.convDict = {'cc_0': 'FC',
                         'cc_1': 'FP',
                         'cc_2': 'FR',
                         'cc_3': 'FU',
                         'cc_4': 'AP',
                         'cc_5': 'AS',
                         'cc_6': 'AH',
                         'cc_7': 'AU',
                         'cc_8': 'TL',
                         'cc_9': 'TR',
                         'cc_10': 'AH'}

    def getChangeString(self, changeObj):
        changedColumns = changeObj.getChangedColumns()
        if changedColumns:
            changeStrings = [self.convDict.get(col,col) + ': ' + str(old) + ' -> ' + str(new) for
                             (col, old, new) in changedColumns]
            return ', '.join(changeStrings)
        else:
            return None
        pass

    def getEntityText(self, changeObj):
        rev = changeObj.thisRevision
        complement = []
        for i in range(0,10):
            attr = 'cc_%d' % (i)
            val = getattr(rev, attr)
            if val is not None and val != 0:
                complement.append(self.convDict[attr] + ':' + str(val))

        attributes = []

        if rev.area is not None:
            attributes.append("Area: %s" %(rev.area))

        if rev.base is not None:
            attributes.append("Base: %s" % (rev.base))

        if rev.adhoc is not None:
            attributes.append("Adhoc: %s" % (rev.adhoc))

        if rev.locktype is not None and rev.locktype != " ":
            attributes.append("locktype: %s" %(rev.locktype))

        entity = "Trip Values: %s" % (" ".join(complement))
        desc = len(attributes) > 0 and " " + " ".join(attributes) or ""
        return entity + desc

class TripGroundDutyAudit(AuditTrail.AuditTrailBase):
    """
    Class that will perform an audit trail on base breaks.
    """
    
    def __init__(self, entityConn, table, search):
        """
        Constructor that will initialize the AuditTrail object
        """
        AuditTrail.AuditTrailBase.__init__(self, entityConn, table, None, None, search, noJoinTables=['crew_base_set'], pointInTimeJoinTable = 'trip')
        self.setEntityTextClass(self)

    def getEntityText(self, changeObj):
        rev = changeObj.thisRevision
        tab = "  "
        baseDesc = ""
        if rev.trip_optionalvariant == True and rev.base != '-':
            baseDesc = "Optional Base Variant (%s) " % (rev.base)
        
        return "%s%s%s (%s,%s)" % (tab, baseDesc, rev.ground_task_activity, str(rev.task_udor)[:9], rev.ground_task_adep)

class TripFlightDutyAudit(AuditTrail.AuditTrailBase):
    """
    Class that will perform an audit trail on base breaks.
    """
    
    def __init__(self, entityConn, table, search):
        """
        Constructor that will initialize the AuditTrail object
        """
        AuditTrail.AuditTrailBase.__init__(self, entityConn, table, None, None, search, noJoinTables=['crew_base_set'], pointInTimeJoinTable = 'trip')
        self.setEntityTextClass(self)


    def getEntityText(self, changeObj):
        rev = changeObj.thisRevision
        tab = "  "
        baseDesc = ""
#        print "rev = %s" % str(rev)
        if rev.trip_optionalvariant == True and rev.base != '-':
            baseDesc = "Optional Base Variant (%s) " % (rev.base)
        fd = self.formatFlightDes(rev.leg_fd).ljust(6)
        return "%s%s%s (%s,%s)%s" % (tab, baseDesc, fd, str(rev.leg_udor)[:9], rev.leg_adep,
                                     rev.pos and " %s"%(rev.pos) or "")

    
    def formatFlightDes(self, ds):
        '''Basically removes leading zeroes in flight designators.'''
        i = 0
        j = 1
        carrierPart = ""
        numPart = 0
        suffix = ""
        while i<len(ds) and not ds[i].isdigit():
            if ds[i] != ' ':
                carrierPart = carrierPart + ds[i]
            i += 1
        while j<len(ds) and not ds[len(ds)-j].isdigit():
            j += 1
            suffix = ds[len(ds)-j+1:]
        try:
            numPart = int( ds[i:len(ds)-j+1] )
        except:
            numPart = ds[i:]
        strNumPart = str(numPart)
        for i in range(3-len(strNumPart)):
            strNumPart = '0' + strNumPart
        return (carrierPart+strNumPart+suffix).strip()
        
def showFile( hdr, file ):
    '''Uses csl to show a text file'''
    Csl.Csl().evalExpr('csl_show_file("%s","%s",0)' % (hdr , file))

def createFile():
    '''Abstraction function to create a temp file'''
    fname = tempfile.mktemp()
    trailFile = open(fname,"w")
    return fname,trailFile

def Show():
    apa = TripAuditTrail()
    trail = apa.getAuditTrail(["Trip Audit Trail"])
    fileName,trailFile = createFile()
    trailFile.write('\n'.join(trail))
    trailFile.close()
    title = "Trip Audit Trail"
    showFile(title,fileName)

    try:
        os.unlink(fileName)
    except:
        pass



import carmusr.AuditTrail as AuditTrail
from carmusr.AuditTrail import SearchSimple
from carmusr.AuditTrail import SearchBetween
from carmusr.AuditTrail import ChangeObject
import AbsDate
import RelTime
import AbsTime
import time

import profile

import Cui,Gui
import Cfh
import carmstd.cfhExtensions as cfhExtensions
import tempfile
import traceback
import os
import Dates
import carmstd.rave
import carmensystems.rave.api as r

import Csl
from carmensystems.dave import dmf
import modelserver as M

from tm import TM

AUDITTYPE = (ASSIGNMENT, CHECKINOUT, INFORMED, ALLCHECKINOUT) = ("Assignments","Check-in/out","Informed", "ALLCHECKINOUT")

class CrewAuditTrail:
    """
    Class for performing audit trails.

    Inputs:
    schedStart: Start date of activities to look for changes in
    schedEnd:   End date of activities to look for changes in

    the 'search' attribute must also be set with a list of SearchType
    objects that defines the limitations of what to search on, such as crewId
    and either commit-time or commit id.
    
    Examples:
    timeSearch = SearchBetween('dave_revision.committs', histStart, histEnd) #histStart/histEnd as in AbsTime*60
    pubcidSearch = SearchSimple('dave_revision.commitid', '>=', 17376) #pubcid as in published_roster
    crewSearch = SearchSimple('crew', '=', crewId)

    search = [crewSearch, timeSearch]
    
    """
    def __init__(self, crewId, schedStart, schedEnd, pubType=None, histStart=None, histEnd=None):
        self.schedStart = schedStart
        self.schedEnd   = schedEnd
        self.crewId     = crewId
        self.pubType    = pubType
        self.histStart  = histStart
        self.histEnd    = histEnd
        self._showRowPrefices = False
        self._searchCommitId = None

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
        trailRows = []
        if headerRows:
            trailRows.extend(headerRows)

        if self.pubType != "SCHEDULED":
            areas = self.getAuditAreas()
            # Show report in categories (e.g. Assigned, Informed)
            for area in areas.keys():
                trailRows.append(area + ':')
                changes = []
                for auditType in areas[area]:
                    for audit in auditType:
                        changes += audit.getAuditTrail(self._conn)
                trailRows.extend(self.printChanges(changes))
            trailRows.append(' ')
        else:
            self._showRowPrefices = True
            areas = self.getAuditAreas(ASSIGNMENT)
            # Show all entries sorted on time
            changes = []

            for area in areas.keys():
                for auditType in areas[area]:
                    for audit in auditType:
                        changes += audit.getAuditTrail(self._conn)

            if len(changes) > 0:
                self._searchCommitId = min((change.thisRevision.commitid for change in changes))
                areas = self.getAuditAreas(ALLCHECKINOUT, INFORMED)
            else:
                self._searchCommitId = None
                areas = self.getAuditAreas(CHECKINOUT, INFORMED)
                
            for area in areas.keys():
                for auditType in areas[area]:
                    for audit in auditType:
                        changes += audit.getAuditTrail(self._conn)
            trailRows.extend(self.printChanges(changes))
        return trailRows

    def getAuditAreas(self, *areas):
        """
        Returns a dict of AuditTrail objects, grouped by their Area.
        This method essentially decides what the audit trail is to be run on
        It is considered an error not to have a atleast one search criteria defined
        
        areas = list of areas to include. If list is empty then all areas are included.
        """

        self.setupAuditPeriods()
        
        cfdList = []
        assignmentAttrList = []
        crewActivityList = []
        cgdList = []
        cioStatusList = []
        cioEventList = []
        ciFrozenList = []
        informedList = []
        doNotPublishList = []
        crewBBList = []
        
        # If true, shows prefices e.g. INF, CIO in front of the row
        showPrefix = self._showRowPrefices
        
        result = dict()
        if not areas or ASSIGNMENT in areas:
            for auditPeriod in self.auditPeriods:
                cfdList.append(CrewFlightDutyAudit(self._entityConn, auditPeriod.search, auditPeriod.schedStart, auditPeriod.schedEnd, self.crewId))
                crewActivityList.append(CrewActivityAudit(self._entityConn, auditPeriod.search, auditPeriod.schedStart, auditPeriod.schedEnd, self.crewId))
                cgdList.append(CrewGroundDutyAudit(self._entityConn, auditPeriod.search, auditPeriod.schedStart, auditPeriod.schedEnd, self.crewId))
                ciFrozenList.append(CrewCIFrozenAudit(self._entityConn,  auditPeriod.search, auditPeriod.schedStart, auditPeriod.schedEnd, self.crewId))
                assignmentAttrList.append(CrewFlightDutyAttrAudit(self._conn, self._entityConn, auditPeriod.search, auditPeriod.schedStart, auditPeriod.schedEnd, self.crewId))
                assignmentAttrList.append(CrewGroundDutyAttrAudit(self._conn, self._entityConn, auditPeriod.search, auditPeriod.schedStart, auditPeriod.schedEnd, self.crewId))
                assignmentAttrList.append(CrewActivityAttrAudit(self._conn, self._entityConn, auditPeriod.search, auditPeriod.schedStart, auditPeriod.schedEnd, self.crewId))
                crewBBList.append(CrewBaseBreakAudit(self._entityConn, auditPeriod.search, auditPeriod.schedStart, auditPeriod.schedEnd, self.crewId))
            result[ASSIGNMENT] = [cfdList, crewActivityList, cgdList, assignmentAttrList, ciFrozenList, crewBBList]
        if not areas or INFORMED in areas:
            for auditPeriod in self.auditPeriods:
                informedList.append(InformedAudit(self._entityConn,  auditPeriod.search, auditPeriod.schedStart, auditPeriod.schedEnd, self.crewId, showPrefix=showPrefix))
                doNotPublishList.append(DoNotPublishAudit(self._entityConn,  auditPeriod.search, auditPeriod.schedStart, auditPeriod.schedEnd, self.crewId, showPrefix=showPrefix))
            result[INFORMED] = [informedList, doNotPublishList]
        if not areas or CHECKINOUT in areas:
            for auditPeriod in self.auditPeriods:
                cioStatusList.append(CrewCIOAudit(self._entityConn, auditPeriod.search, auditPeriod.schedStart, auditPeriod.schedEnd, self.crewId, 'cio_status', 'status', showPrefix=showPrefix))
                cioEventList.append(CrewCIOAudit(self._entityConn,  auditPeriod.search, auditPeriod.schedStart, auditPeriod.schedEnd, self.crewId, 'cio_event', 'statuscode', showPrefix=showPrefix))
            result[CHECKINOUT] = [cioStatusList, cioEventList]
        if ALLCHECKINOUT in areas:
            # Special case of CHECKINOUT, where all check-ins/outs after the first change (auditPeriod.search) 
            # are considered. Used for Tracking.
            for auditPeriod in self.auditPeriods:
                cioStatusList.append(CrewCIOAudit(self._entityConn, auditPeriod.search, 0, auditPeriod.schedEnd, self.crewId, 'cio_status', 'status', showPrefix=showPrefix))
                cioEventList.append(CrewCIOAudit(self._entityConn,  auditPeriod.search, 0, auditPeriod.schedEnd, self.crewId, 'cio_event', 'statuscode', showPrefix=showPrefix))
            result[CHECKINOUT] = [cioStatusList, cioEventList]

        return result
    
    def getConnection(self):
        """
        Returns the connections to the schema, both at Dave L1 and Entity Level
        """
        m = M.TableManager.instance()
        e = dmf.EntityConnection()
        e.open(m.getConnStr(), m.getSchemaStr())
        return (dmf.Connection(m.getConnStr()), e)
    
    def setupAuditPeriods(self):
        """
        Sets the list of audit periods depending on publish or historical value.

        Note that if self._searchCommitId is set, it is used as the >=commitId to search
        for.
        """

        self.auditPeriods = []
        if self._searchCommitId:
            for start, end, _ in self.getPublishedPeriodsCrew():
                search = SearchSimple('dave_revision.commitid', '>=', self._searchCommitId)
                self.auditPeriods.append(self.AuditPeriod([search], start, end))
        elif not self.pubType is None:
            for start, end, commitId in self.getPublishedPeriodsCrew(): 
                pubcidSearch = SearchSimple('dave_revision.commitid', '>=', commitId)
                self.auditPeriods.append(self.AuditPeriod([pubcidSearch], start, end))
        elif self.histStart and self.histEnd:
            timeSearch = SearchBetween('dave_revision.committs', int(self.histStart)*60, int(self.histEnd)*60)
            self.auditPeriods.append(self.AuditPeriod([timeSearch], self.schedStart, self.schedEnd))
        else:
            raise Exception, "No audit depth given."

    class AuditPeriod:
        """
        Class containing all information about what to audit trail.
        
        """
        def __init__(self, search, schedStart, schedEnd):
            self.search = search
            self.schedStart = schedStart
            self.schedEnd = schedEnd

    def getPublishedPeriodsCrew(self):
        """
        Get periods of published roster with CID
        
        """

        publicationType = TM.publication_type_set[self.pubType]
        crew = TM.crew[self.crewId]

        periodList = []

        for publication in crew.referers("published_roster", "crew"):
            if publication.pubtype == publicationType and \
                   publication.pubstart < self.schedEnd and publication.pubend > self.schedStart:
                periodStart = max(publication.pubstart, self.schedStart)
                periodEnd = min(publication.pubend, self.schedEnd)
                commitId = publication.pubcid
                periodList.append([periodStart, periodEnd, commitId])

        return periodList

    def printChanges(self, changes):
        """
        Produces the textual report of all changes within an Audit Trail Area
        """
        changes.sort(ChangeObject.compare)
        changeRow = []
        changesAlreadyProcessed = []
        lastTime = ""
        schanges = [(AbsTime.AbsTime(change.thisRevision.committs/60), change.getEntityText(), change) for change in changes]

        for changeDate,text,change in schanges:
            # Check if change has already been processed.
            # Same change can occur multiple times due to touch statement in time period check.
            if [change.thisRevision.getPK(),change.thisRevision.revid] in changesAlreadyProcessed:
                continue
            changeType = change.getChangeType()
            time = str(changeDate)[:-6]
            if changeType in ['added', 'removed']:
                if time != lastTime:
                    lastTime = time
                    changeRow.append(' '  + time + ':')    
                changeRow.append(text)
            else:
                changeString = change.getChangeString()
                if not changeString:
                    continue
                if time != lastTime:
                    lastTime = time
                    changeRow.append(' ' + time + ':')                   
                changeRow.append(text)
                changeRow.append('          (changes: '+  changeString + ')')
            changesAlreadyProcessed.append([change.thisRevision.getPK(),change.thisRevision.revid])

        if not changeRow:
            changeRow.append('     No changes made matching the specified intervals.')
        return changeRow





class CrewBaseBreakAudit(AuditTrail.AuditTrailBase):
    """
    Class that will perform an audit trail on base breaks.
    """

    def __init__(self, entityConn, search, periodStart, periodEnd, crewId):
        """
        Constructor that will initialize the AuditTrail object

        """

        internalSearch = search[:]
        internalSearch.append(SearchSimple('crew', '=', crewId))
        self.crewId = crewId

        AuditTrail.AuditTrailBase.__init__(self, entityConn, "crew_base_break", periodStart, periodEnd, internalSearch)

        self.setTimeFields(['st'])
        self.setEntityTextClass(self)

    def getEntityText(self, changeObj):
        """
        Returns the descriptive text for an entity within this AuditTrail
        """
        r = changeObj.thisRevision

        if r.bfr:
            loc = 'before'
        else:
            loc = 'after'
        
        if r.carrier == '-':
            # This is a ground activity basebreak
            return "Base Break %s (%s %s, %s) : %s" % (loc, r.activitycode, r.st, r.adep, r.remotestation)

        else:
            # This is a flight basebreak
            return "Base Break %s (%s %03d %s, %s) : %s" % (loc, r.carrier, r.nr, str(r.st)[0:9], r.adep, r.remotestation)

class InformedAudit(AuditTrail.AuditTrailBase):
    """
    Class that will perform an audit trail on informed.
    """

    def __init__(self, entityConn, search, periodStart, periodEnd, crewId, showPrefix=False):
        """
        Constructor that will initialize the AuditTrail object

        """

        internalSearch = search[:]
        internalSearch.append(SearchSimple('crew', '=', crewId))
        self.crewId = crewId
        self.showPrefix = showPrefix

        AuditTrail.AuditTrailBase.__init__(self, entityConn, "informed", periodStart, periodEnd, internalSearch)

        self.setTimeFields(['startdate', 'enddate'])

        self.setEntityTextClass(self)

    def getEntityText(self, changeObj):
        """
        Returns the descriptive text for an entity within this AuditTrail
        """
        r = changeObj.thisRevision
        startDate = r.startdate.ddmonyyyy()[:9]
        endDate= (r.enddate-RelTime.RelTime(1)).ddmonyyyy()[:9] # Show dates inclusive
        if startDate == endDate:
            return "informed        (%s)" % startDate
        else:
            return "informed        (%s - %s)" %(startDate, endDate)
                
    def getEntityPrefix(self, changeObj):
        if self.showPrefix:
            return "MIF"
        else:
            return ""
        
class DoNotPublishAudit(AuditTrail.AuditTrailBase):
    """
    Class that will perform an audit trail on "do not publish".
    """

    def __init__(self, entityConn, search, periodStart, periodEnd, crewId, showPrefix=False):
        """
        Constructor that will initialize the AuditTrail object

        """

        internalSearch = search[:]
        internalSearch.append(SearchSimple('crew', '=', crewId))
        self.crewId = crewId
        self.showPrefix = showPrefix

        AuditTrail.AuditTrailBase.__init__(self, entityConn, "do_not_publish", periodStart, periodEnd, internalSearch)

        self.setTimeFields(['start_time', 'end_time'])

        self.setEntityTextClass(self)

    def getEntityText(self, changeObj):
        """
        Returns the descriptive text for an entity within this AuditTrail
        """
        r = changeObj.thisRevision
        startDate = r.start_time.ddmonyyyy()[:9]
        endDate= (r.end_time-RelTime.RelTime(1)).ddmonyyyy()[:9] # Show dates inclusive
        if startDate == endDate:
            return "do not publish  (%s)" % startDate
        else:
            return "do not publish  (%s - %s)" %(startDate, endDate)
                
    def getEntityPrefix(self, changeObj):
        if self.showPrefix:
            return "DNP"
        else:
            return ""

class AttributeAudit(AuditTrail.AuditTrailBase):
    """
    Class that will perform audit trail on attribute tables.

    """

    def __init__(self, conn, entityConn, search, periodStart, periodEnd, table, timeFields):
        """
        Constructor that will initialize the AuditTrail object

        """
        AuditTrail.AuditTrailBase.__init__(self, entityConn, table+"_attr", periodStart, periodEnd,
                                           search, pointInTimeJoinTable = table)
        self.setTimeFields(timeFields)
        self.attributePresentationDict = {"TRAINING": self.trainingText,
                                          "INSTRUCTOR": self.instructorText,
                                          "PRIVATE": self.privateText,
                                          "RECURRENT": self.recurrentText,
                                          "BRIEF": self.briefText,
                                          "DEBRIEF": self.debriefText,
                                          "CALLOUT": self.calloutText,
                                          "MEAL_BREAK": self.mealBreakText
                                          }
        self._entityConn = entityConn
        self._conn = conn
        self.periodStart = periodStart
        self.periodEnd = periodEnd

    def mealBreakText(self, r):
        aProps = self.activityProperties(r)
        return "meal break on " + aProps['name']

    def trainingText(self, r):
        aProps = self.activityProperties(r)
        return r.value_str + " training on " + aProps['name']

    def instructorText(self, r):
        aProps = self.activityProperties(r)
        return r.value_str + " instructor on " + aProps['name']

    def privateText(self, r):
        aProps = self.activityProperties(r)
        return r.attr + " on " + aProps['name']
    
    def recurrentText(self, r):
        aProps = self.activityProperties(r)
        return r.attr + " on " + aProps['name']
    
    def briefText(self, r):
        aProps = self.activityProperties(r)
        return r.attr + " " + str(aProps['st'] - RelTime.RelTime(r.value_rel)) + " on " + aProps['name']
    
    def debriefText(self, r):
        aProps = self.activityProperties(r)
        return r.attr + " " + str(AbsTime.AbsTime(r.value_abs)) + " on " + aProps['name']

    def calloutText(self, r):
        aProps = self.activityProperties(r)
        return "%s on %s (rel %s,int %s)" % (r.attr, aProps['name'], r.value_rel, r.value_int)
    
    def activityProperties(self, r):
        return {'name': '',
                'st': None,
                'et': None,
                'ades': None,
                'adep': None,
                }

    def getCorrectTransaction(self, commitid, transactions):
        rev = 0
        result = None
        for transaction in transactions:
            if transaction.commitid > rev and transaction.commitid <= commitid:
                result = transaction
        return result

    def getEntityText(self, changeObj):
        """
        Returns the descriptive text for an entity within this AuditTrail
        """
        r = changeObj.thisRevision
        func = self.attributePresentationDict.get(r.attr, self.defaultPresentation)
        return func(r)
        
    def defaultPresentation(self, r):
        ''' A default printout of an attribute, will not contain any activity info '''
        aProps = self.activityProperties(r)
        values = []
        for prop in ('value_rel', 'value_abs', 'value_int', 'value_str'):
            if hasattr(r, prop):
                val = getattr(r,prop)
                if val is not None:
                    values.append(str(val))
        return "Attribute: " + r.attr + ' (' + ','.join(values) + ') on ' + str(aProps['name'])
    
class CrewFlightDutyAttrAudit(AttributeAudit):
    """
    Class that will perform audit trail on crew_flight_duty_attr table.

    """

    def __init__(self, conn, entityConn, search, periodStart, periodEnd, crewId):
        """
        Constructor that will initialize the AuditTrail object

        """
        internalSearch = search[:]
        internalSearch.append(SearchSimple('cfd_crew', '=', crewId))

        AttributeAudit.__init__(self, conn, entityConn, internalSearch,  periodStart, periodEnd, "crew_flight_duty",
                                ["cfd_leg_udor"])

        self.setEntityTextClass(self)


    def activityProperties(self, r):
        history = AuditTrail.AuditSQL(self._entityConn, 'crew_flight_duty_attr', self.periodStart, self.periodEnd,
                                      [SearchSimple('cfd_crew', '=', r.cfd_crew),
                                       SearchSimple('cfd_leg_fd', '=', r.cfd_leg_fd),
                                       SearchSimple('cfd_leg_udor', '=', r.cfd_leg_udor),
                                       SearchSimple('cfd_leg_adep', '=', r.cfd_leg_adep),
                                       SearchSimple('revid', '=', r.revid)],
                                      pointInTimeJoinTable = 'flight_leg',
                                      overrides = ['crew_flight_duty', 'flight_leg'])
        history.setTimeFields = ['flight_leg.sobt','flight_leg.sibt']

        transactions = history.getTransactions(self._conn)
        leg = self.getCorrectTransaction(r.commitid, transactions)
        
        return {'name': leg.flight_leg_fd + " " + str(leg.flight_leg_udor)[:9],
                'st': leg.flight_leg_sobt,
                'et': leg.flight_leg_sibt,
                'adep': leg.flight_leg_adep,
                'ades': leg.flight_leg_ades,
                }

class CrewGroundDutyAttrAudit(AttributeAudit):
    """
    Class that will perform audit trail on crew_ground_duty_attr table.

    """

    def __init__(self, conn, entityConn, search, periodStart, periodEnd, crewId):
        """
        Constructor that will initialize the AuditTrail object

        """

        internalSearch = search[:]
        internalSearch.append(SearchSimple('cgd_crew', '=', crewId))

        AttributeAudit.__init__(self, conn, entityConn, internalSearch,  periodStart, periodEnd, "crew_ground_duty",
                                ["cgd_task_udor"])

        self.setEntityTextClass(self)


    def activityProperties(self, r):
        history = AuditTrail.AuditSQL(self._entityConn, 'crew_ground_duty_attr', self.periodStart, self.periodEnd,
                                      [SearchSimple('cgd_crew', '=', r.cgd_crew),
                                       SearchSimple('cgd_task_id', '=', r.cgd_task_id),
                                       SearchSimple('cgd_task_udor', '=', r.cgd_task_udor),
                                       SearchSimple('revid', '=', r.revid)],
                                      pointInTimeJoinTable = 'ground_task',
                                      overrides = ['crew_ground_duty','ground_task'])
        history.setTimeFields = ['ground_task.st','ground_task.et']

        transactions = history.getTransactions(self._conn)
        leg = self.getCorrectTransaction(r.commitid, transactions)
        return {'name': leg.ground_task_activity + " " + str(leg.ground_task_udor)[:9],
                'st': leg.ground_task_st,
                'et': leg.ground_task_et,
                'adep': leg.ground_task_adep,
                'ades': leg.ground_task_ades,
                }

class CrewActivityAttrAudit(AttributeAudit):
    """
    Class that will perform audit trail on crew_activity_attr table.
    """

    def __init__(self, conn, entityConn, search, periodStart, periodEnd, crewId):
        """
        Constructor that will initialize the AuditTrail object
        """

        internalSearch = search[:]
        internalSearch.append(SearchSimple('ca_crew', '=', crewId))
        self.crewId = crewId

        AttributeAudit.__init__(self, conn, entityConn, internalSearch,  periodStart, periodEnd, "crew_activity",
                                ["crew_activity.st","crew_activity.et"])

        self.setEntityTextClass(self)


    def activityProperties(self, r):
        return {'name': r.ca_activity + " " + str(r.ca_st),
                'st': r.ca_st,
                'et': r.crew_activity_et,
                'adep': r.crew_activity_adep,
                'ades': r.crew_activity_ades,
                }
        
class CrewCIFrozenAudit(AuditTrail.AuditTrailBase):
    """
    Class that will perform an audit trail on ci_frozen.
    """

    def __init__(self, entityConn, search, periodStart, periodEnd, crewId):
        """
        Constructor that will initialize the AuditTrail object
        """

        internalSearch = search[:]
        internalSearch.append(SearchSimple('crew', '=', crewId))
        self.crewId = crewId

        AuditTrail.AuditTrailBase.__init__(self, entityConn, "ci_frozen", periodStart, periodEnd, internalSearch)

        self.setEntityTextClass(self)
        self.setTimeFields(['dutystart'])

    def getEntityText(self, changeObj):
        """
        Returns the descriptive text for an entity within this AuditTrail
        """

        r = changeObj.thisRevision

        return "Duty start override at "+str(r.dutystart)

class CrewCIOAudit(AuditTrail.AuditTrailBase):
    """
    Class that will perform an audit trail on cio_status and cio_event tables.
    Each table and what the name of the status column is have to be given as aparameter.
    """
    def __init__(self, entityConn, search, periodStart, periodEnd, crewId, table, statusColumn, showPrefix=False):
        """
        Constructor that will initialize the AuditTrail object
        """

        internalSearch = search[:]
        internalSearch.append(SearchSimple('crew', '=', crewId))
        AuditTrail.AuditTrailBase.__init__(self, entityConn, table, periodStart, periodEnd,
                                           internalSearch,
                                           ['ciotime' , statusColumn])
        self.setEntityTextClass(self)
        self.setDataConverter(self.statusConverter)
        self.setTimeFields(['ciotime'])
        self._statusColumn = statusColumn
        self.showPrefix = showPrefix

    def statusConverter(self, thisRevision, prevRevision):
        """
        Callback that will change the status column from a number, to a descriptive string.
        """
        statusCodeDict = {
                0: "Undo check-in",
                1: "Check-in",
                2: "Check-out",
                3: "Recheck-in",
                # Note: 4 is not used.
                5: "Check-in [assisted]",
                6: "Check-out [assisted]",
                7: "Recheck-in [assisted]",
                8: "Automatic check-out",
        }
        if thisRevision:
            scode = getattr(thisRevision, self._statusColumn)
            setattr(thisRevision, self._statusColumn,
                    statusCodeDict.get(scode, "Unknown status [%s]" % scode))
        if prevRevision:
            scode = getattr(prevRevision, self._statusColumn)
            setattr(prevRevision, self._statusColumn,
                    statusCodeDict.get(scode, "Unknown status [%s]" % scode))
        return thisRevision, prevRevision

    def getEntityText(self, changeObj):
        """
        Returns the descriptive text for an entity within this AuditTrail
        """
        r = changeObj.thisRevision
        return "%s (%s)" \
                %(r.ciotime,
                getattr(r, self._statusColumn))
                
    def getEntityPrefix(self, changeObj):
        if self.showPrefix:
            return "CIO"
        else:
            return ""

class CrewGroundDutyAudit(AuditTrail.AuditTrailBase):
    """
    Performs audit trail on crew_ground_duty
    """
    def __init__(self, entityConn, search, periodStart, periodEnd, crewId):
        """
        Constructor that will initialize the AuditTrail object
        """

        internalSearch = search[:]
        internalSearch.append(SearchSimple('crew', '=', crewId))
        AuditTrail.AuditTrailBase.__init__(self, entityConn, 'crew_ground_duty',
                                           periodStart, periodEnd,
                                           internalSearch,
                                           ['locktype', 'pos'],
                                           pointInTimeJoinTable = 'ground_task')
        self.setEntityTextClass(self)
        self.setDataConverter(self.locktypeConverter)
        self.setTimeFields(['ground_task.st', 'ground_task.et'])

    def getEntityText(self, changeObj):
        """
        Returns the descriptive text for an entity within this AuditTrail
        """
        r = changeObj.thisRevision
        return "%s (%s-%s %s%s, %s%s)" \
               %(r.ground_task_activity.ljust(6),
                 str(r.ground_task_st),
                 str(r.ground_task_et)[-5:] + ((str(r.ground_task_et)[:-5]== 
                                                str(r.ground_task_st)[:-5])
                                               and "," or "+,"),
                 r.ground_task_adep,
                 (r.ground_task_adep!=r.ground_task_ades) and "-"+r.ground_task_ades or "",
                 r.pos,
                 ("",", Locked")[r.locktype == 'Locked'])

class CrewActivityAudit(AuditTrail.AuditTrailBase):
    """
    Performs an audit trail on crew_activity
    """
    def __init__(self, entityConn, search, periodStart, periodEnd, crewId):

        internalSearch = search[:]
        internalSearch.append(SearchSimple('crew', '=', crewId))
        AuditTrail.AuditTrailBase.__init__(self, entityConn, 'crew_activity',
                                           periodStart, periodEnd,
                                           internalSearch,
                                           ['locktype', 'et','adep','ades'])
        self.setEntityTextClass(self)
        self.setDataConverter(self.locktypeConverter)
        self.setTimeFields(['st', 'et'])

    def getEntityText(self, changeObj):
        """
        Returns the descriptive text for an entity within this AuditTrail
        """
        r = changeObj.thisRevision
        return "%s (%s-%s %s%s%s)" \
               %(r.activity.ljust(6),
                 str(r.st),
                 str(r.et)[-5:] + ((str(r.et)[:-5]== 
                                    str(r.st)[:-5])
                                   and "," or "+,"),
                 r.adep,
                 (r.adep!=r.ades) and "-"+r.ades or "",
                 ("",", Locked")[r.locktype == 'Locked'])

class CrewFlightDutyAudit(AuditTrail.AuditTrailBase):
    """
    Performs and audit trail on crew_flight_duty
    """
    def __init__(self, entityConn, search, periodStart, periodEnd, crewId):

        internalSearch = search[:]
        internalSearch.append(SearchSimple('crew', '=', crewId))
        AuditTrail.AuditTrailBase.__init__(self, entityConn, 'crew_flight_duty',
                                           periodStart, periodEnd,
                                           internalSearch,
                                           ['locktype','pos'],
                                           pointInTimeJoinTable = 'flight_leg')
        self.setEntityTextClass(self)
        self.setDataConverter(self.locktypeConverter)
        self.setTimeFields(['flight_leg.sobt', 'flight_leg.sibt'])

    def getEntityText(self, changeObj):
        """
        Returns the descriptive text for an entity within this AuditTrail
        """
        r = changeObj.thisRevision
        return "%s (%s-%s %s-%s, %s%s)" \
               %(self.formatFlightDes(r.leg_fd).ljust(6),
                 str(r.flight_leg_sobt),
                 str(r.flight_leg_sibt)[-5:] + ((str(r.flight_leg_sibt)[:-5]== 
                                                 str(r.flight_leg_sobt)[:-5])
                                                and "," or "+,"),
                r.flight_leg_adep,
                r.flight_leg_ades,
                r.pos,
                ("",", Locked")[r.locktype == 'Locked'])

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

class DateDialog( Cfh.Box ):
    '''Shows a dialog, using cfh, asking for two date intervals'''
    def __init__(self, *args):
        Cfh.Box.__init__(self, *args)

        if os.environ['SK_APP'].upper() == 'TRACKING':
            now = AbsTime.AbsTime(
                Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea,
                                      "None", "fundamental.%now%"))
        else:
            gmt = time.gmtime()
            now = AbsTime.AbsTime(gmt[0],gmt[1],gmt[2],0,0)
        now += RelTime.RelTime('24:00')
        oneMonthAgo = AbsTime.AbsTime(now).addmonths(-1, AbsTime.PREV_VALID_DAY)
        ppStart = AbsTime.AbsTime(
                Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea,
                                      "None", "fundamental.%pp_start%"))
        ppEnd = AbsTime.AbsTime(
                Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiNoArea,
                                      "None", "fundamental.%pp_end%"))
        self.schedStart = Cfh.Date(self, "SCHED_START", ppStart)
        self.schedEnd   = Cfh.Date(self, "SCHED_END",   ppEnd)
        self.histStart  = Cfh.Date(self, "HIST_START",  oneMonthAgo)
        self.histEnd    = Cfh.Date(self, "HIST_END",    now)

        if os.environ['SK_APP'].upper() == 'TRACKING':

            # In tracking the pubType SCHEDULED will override the histStart/End values.
            self.pubType = "SCHEDULED"

            # The histStart/End fields won't be shown for trackers.
            form_layout = """
FORM;AUDIT_TRAIL_CREW;Audit Trail Crew
LABEL;Period
SEPARATOR
FIELD;SCHED_START;Start Date
FIELD;SCHED_END;End Date
BUTTON;B_OK;`Ok`;`_Ok`
BUTTON;B_CANCEL;`Cancel`;`_Cancel`
""" 
        else:
            self.pubType = None
            form_layout = """
FORM;AUDIT_TRAIL_CREW;Audit Trail Crew
LABEL;Period
SEPARATOR
FIELD;SCHED_START;Start Date
FIELD;SCHED_END;End Date
COLUMN
LABEL;Change Introduced
SEPARATOR
FIELD;HIST_START;Start Date
FIELD;HIST_END;End Date
BUTTON;B_OK;`Ok`;`_Ok`
BUTTON;B_CANCEL;`Cancel`;`_Cancel`
"""

        self.ok = Cfh.Done(self, "B_OK")
        self.cancel = Cfh.Cancel(self, "B_CANCEL")

        dateDialog_form_file = tempfile.mktemp()
        f = open(dateDialog_form_file,"w")
        f.write(form_layout)
        f.close()
        self.load(dateDialog_form_file)
        os.unlink(dateDialog_form_file)

    def check(self, *args):
        """
        Check the validity of chosen values in the form.
        Checks for invalid time periods and is run when clicking Ok.
        Returns a string when error occurs, string is then displayed in form.

        """
        
        r = Cfh.Box.check(self,*args)
        if r:
            return r

        # Only do the loaded-plan check for tracking, planning will not access the model at all
        if os.environ['SK_APP'].upper() == 'TRACKING':
            planStart = AbsTime.AbsTime(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiWhichArea, "window", 'fundamental.%loaded_data_period_start%'))
            planEnd = AbsTime.AbsTime(Cui.CuiCrcEvalAbstime(Cui.gpc_info, Cui.CuiWhichArea, "window", 'fundamental.%loaded_data_period_end%'))
            if AbsTime.AbsTime(self.schedStart.getValue()) < planStart or AbsTime.AbsTime(self.schedEnd.getValue()) > planEnd:
                return "Chosen period is not loaded."
        
def showFile( hdr, file ):
    '''Uses csl to show a text file'''
    Csl.Csl().evalExpr('csl_show_file("%s","%s",0)' % (hdr , file))

def createFile():
    '''Abstraction function to create a temp file'''
    fname = tempfile.mktemp()
    trailFile = open(fname,"w")
    return fname,trailFile

def show2():
    '''Will pop-up a dialog asking for date intervals, whereafter
    an audit trail is computed by creating an crew audit trail object,
    whereafter the output is shown.'''

    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    context = carmstd.rave.Context('object', area)
    crewList = context.eval(r.foreach('iterators.roster_set',
                                      'crew.%id%',
                                      'crew.%employee_number%'))
    crewList = [crew[1:] for crew in crewList[0]]
    crewId = crewList[0][0]
    crewEmployeeNo = crewList[0][1]
       
    global dateDialog
    try:
        dateDialog == dateDialog
    except:
        dateDialog = DateDialog('Audit Trail Crew')

    dateDialog.show(1)

    if dateDialog.loop() != Cfh.CfhOk:
        return

    schedStartTime = AbsTime.AbsTime(dateDialog.schedStart.valof())
    schedEndTime = AbsTime.AbsTime(dateDialog.schedEnd.valof()) + \
        RelTime.RelTime(1, 00, 00) #
    histStartTime = AbsTime.AbsTime(dateDialog.histStart.valof())
    histEndTime = AbsTime.AbsTime(dateDialog.histEnd.valof()) + \
        RelTime.RelTime(0, 23, 59)

    publicationType = dateDialog.pubType
    # handling empty input values, start times interpreted as
    # the beginning of the universe (1986-01-01 00:00), end times
    # interpreted as the end of the universe (2086-12-31 23:59)
    # (AbsTime should be able to handle dates until 2099,
    # but this caused studio to crash, so I changed it to 2086,
    # as this really is not crucial. If you want to enter higher
    # values, and the system supports it, you still can).
    minTime = AbsTime.AbsTime(1986, 01, 01, 0, 0)
    maxTime = AbsTime.AbsTime(2086, 12, 31, 23, 59)
    if dateDialog.schedStart.valof() == -1:
        schedStartTime = minTime
    if dateDialog.schedEnd.valof() == -1:
        schedEndTime = maxTime
    if dateDialog.histStart.valof() == -1:
        histStartTime = minTime
    if dateDialog.histEnd.valof() == -1:
        histEndTime = maxTime
    # end handling of empty input values.

    headerRows = []
    headerRows.append('Audit Trail for crew %s (%s)' % (crewEmployeeNo, crewId))
    periodtext = 'Period %s - %s' % (
                 AbsDate.AbsDate(schedStartTime),
                 AbsDate.AbsDate(schedEndTime-RelTime.RelTime(0,0,1)))
    if os.environ['SK_APP'].upper() != 'TRACKING':
        periodtext += ', change introduced %s - %s' % (
                      AbsDate.AbsDate(histStartTime),
                      AbsDate.AbsDate(histEndTime-RelTime.RelTime(1,0,0)))
    headerRows.append(periodtext)
    try:
        fileName = ""
        fileName,trailFile = createFile()

        crewAuditTrail = CrewAuditTrail(crewId, schedStartTime, schedEndTime, publicationType, histStartTime, histEndTime)

        auditTrail = crewAuditTrail.getAuditTrail(headerRows)
        trailFile.write('\n'.join(auditTrail))
        trailFile.close()
        title = "Audit Trail for crew %s (%s)" % (crewEmployeeNo, crewId) 
        showFile(title,fileName)
    except InvalidIntervalException, e:
        cfhExtensions.show(e.value)
        return
    except AbortedException, e:
        print e.value
        return
    try:
        os.unlink(fileName)
    except:
        pass

class InvalidIntervalException(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)
class AbortedException(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)

def show():
    show2()
#    profile.run('CrewAuditTrail.show2()','/users/sandberg/foo')
#    import pstats
#    s = pstats.Stats('/users/sandberg/foo')
#    s.sort_stats('time').print_stats(20)
    #s.strip_dirs().print_callers()
    #s.print_callees()


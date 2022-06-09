import Cui,Gui
import AbsTime, AbsDate
import Csl
import tempfile
import traceback
import os
import Dates
import modelserver as M
import carmensystems.studio.plans.Common as Common
import carmensystems.studio.gui.StudioGui as StudioGui
from carmensystems.dave import dmf, baselib
import Crs


def convertDateTime(dateTime,convertToStudioTime=1):
    """
    Convenience function to get a string representation of a date/time
    """
    if convertToStudioTime:
        try:
            convertedCarmTime = Cui.CuiConvertTime(Cui.gpc_info,dateTime)
        except:
            convertedCarmTime = Cui.CuiConvertTime(Cui.gpc_info,int(dateTime))
    else:
        convertedCarmTime = dateTime.getRep()
        
    # Present the time in the users defined format (as default YYMonDD HH:MM)
    theValue = Dates.FDatInt2DateTime(convertedCarmTime)
    return theValue


class EntityISearcher(object):
    """
    Class to extract DAVE level 2 entities, which can be used for Audit Trails.
    """
    def __init__(self):
        """
        Set up database connection
        """
        self.tm = M.TableManager.instance()
        self.conn = dmf.EntityConnection()
        self.conn.open(self.tm.getConnStr(), self.tm.getSchemaStr())       

    def __del__(self):
        """
        Close database connection
        """
        self.conn.close(False)

    def search(self, entityName, searchDict):
        """
        Performs a searach for entities in entityName matching key-value pairs in
        the searchDict.
        
        @ param entityName: Name of entity to search in
        @ param searchDict: Dictionary of column-value pairs for idenitfying an entry
        @return : list of (PK value dict, entityI)
        """
        entitySpec = self.conn.getEntitySpec(entityName)
        filter, key = self._createFilter(entitySpec, searchDict)
        table = self.tm.table(entityName)

        results = []
        self.conn.beginReadTxn()
        try:
            revFilter = baselib.RevisionFilter()
            revFilter.withDeleted(True)
            self.conn.setRealSnapshot(revFilter)
            self.conn.setSelectParams(key)
            
            self.conn.select(entityName, filter, True)

            while True:
                record = self.conn.readRecord()
                if record is None:
                    break
                keyList = record.keyAsList(entitySpec)
                keyDict = record.keyAsDict(entitySpec)
                keyStrings = []
                for i in range(entitySpec.getKeyCount()):
                    type = entitySpec.getKeyColumn(i).getApiType()
                    if type == baselib.TYPE_ABSTIME:
                        value = AbsTime.AbsTime(keyList[i])
                    elif type == baselib.TYPE_DATE:
                        value = AbsDate.AbsDate(keyList[i]*1440)
                    else:
                        value = keyList[i]
                    keyStrings.append(str(value).replace('+', '\+'))
                results.append((table.getOrCreateRef('+'.join(keyStrings)),keyDict))
            return results
        finally:
            self.conn.endReadTxn()
        
            
    def _createFilter(self, entitySpec, keyDict):
        """
        Creates a dave::Filter from input dictionary
        """
        key = baselib.Key(len(keyDict))
        tests = []
        i = 0
        for column, value in keyDict.iteritems():
            tests.append('$.%s=%%:%i'%(column, i+1))
            type = entitySpec.getColumnByAlias(column).getApiType()
            key.setValue(i, self._toBaselibValue(value, type))
            i += 1
        #We only want the last one to do audit trail on
        tests.append('$.next_revid = 0')
        my_filter = baselib.Filter(entitySpec.getName())
        my_filter.where(' AND '.join(tests))
        return my_filter, key
                         
    def _toBaselibValue(self, value, type):
        """
        Convert value to a baselib.Value

        @param value: A Pyhton value
        @param type: A baselib.Type type
        @return: A baselib.Value
        """
        if type == baselib.TYPE_INVALID:
            return baselib.Value()
        elif type == baselib.TYPE_INT:
            return baselib.IntValue(value)
        elif type == baselib.TYPE_DATE:
            return baselib.IntValue(value)
        elif type == baselib.TYPE_ABSTIME:
            return baselib.IntValue(value)
        elif type == baselib.TYPE_RELTIME:
            return baselib.IntValue(value)
        elif type == baselib.TYPE_FLOAT:
            return baselib.FloatValue(value)
        elif type == baselib.TYPE_CHAR:
            return baselib.CharValue(value)
        elif type == baselib.TYPE_BOOL:
            return baselib.BoolValue(value)
        elif type == baselib.TYPE_STRING:
            return baselib.StringValue(value)
        elif type == baselib.TYPE_UUID:
            return baselib.StringValue(value)
        else:
            raise Exception('Unexpected type %i' % type)

class Presentator(object):
    """
    Presentation object for an entity
    """
    SORT_NONE = 0
    SORT_COLUMN = 1
    SORT_DESCRIPTION = 2
    def __init__(self, entity, pkDict = None, sortMethod = None):
        self.entity = entity
        self.entityDesc = entity.desc()
        self.pk = pkDict
        if sortMethod is None:
            self._sortMethod = Presentator.SORT_NONE
        else:
            self._sortMethod = sortMethod

    def present(self, changeType, column, old, new):
        """
        Creates a textual representation of the change, performs default conversion for
        time columns and retrieves the description for the column.
        @param changeType: Modelserver changetype
        @param column: Name of column
        @param old: Old value of column
        @param new: New value of column
        @return :String representation of the change
        """
        columnIndex = self.entityDesc.column(column)
        colType = self.entityDesc.type(columnIndex)

        if colType == M.TIME:
            #We don't wan't to display changes where we go from None -> AbsTime(0)
            if not old and int(new) == 0:
                return None
            if old:
                old = convertDateTime(old)
            if new:
                new = convertDateTime(new)

        return self.presentDefault(changeType, M.description(self.entity, column), old, new)

    def presentDefault(self, changeType, columnDesc, old, new):
        """
        Creates a textual representation of the change using provided descriptions of the
        column and it's old and new values
        
        @param changeType: Modelserver changetype
        @param columnDesc: Column description
        @param old: Old value of column
        @param new: New value of column
        @return : String representation of the change
        """
        if changeType == M.Change.MODIFIED:
            if old:
                return "\t%s changed from: %s to: %s"%(columnDesc,old,new)
            else:
                return "\t%s set to: %s"%(columnDesc,new)              
        elif changeType == M.Change.ADDED:
            return "\t%s: %s"%(columnDesc, new)

    def deleteDesc(self, changeType):
        """
        Creates a textual representation of the deletion of a record of this entity
        @param changeType: Modelserver changetype sent to getTypeString
        @return :String description of the deleted entity
        """
        return "\t%s: %s " % (self.getTypeString(changeType), self.entityDesc.description())

    def getTypeString(self,changeType):
        """
        Returns a string representation of a change type
        @param changeType: modelserver changetype
        @return :String representation of changeType
        """
        return ['Created', 'Changed', 'Deleted'][changeType]

    def setSortMethod(self, method):
        self._sortMethod = method

    def getSortMethof(self):
        return self._sortMethod

    def sort(self, colls):
        """
        Sorts depending on selected sort method, implementation by DSU 'pattern'
         (Decorate, Sort, Undoecorate).
         @param colls: List to sort
         @return : Sorted list depending on sort method selected in Presentator object
        """
        if self._sortMethod == Presentator.SORT_NONE:
            return colls
        elif self._sortMethod == Presentator.SORT_COLUMN:
            return self._sort([(col, (col, old, new)) for col, old, new in colls])
        elif self._sortMethod == Presentator.SORT_DESCRIPTION:
            return self._sort([(M.description(self.entity,col), (col, old, new)) for col, old, new in colls])

    def _sort(self, colls):
        """
        Method to perform the actuall sorting
        @param colls: Decorated list where the first object in the tuple is what to
                       sort after, second is the object itself
        @return : A sorted undecorated list
        """
        colls.sort()
        return [item for (_, item) in colls]

class AuditDomainFactory(EntityISearcher):
    """
    Default implementation of a factory class that returns propper
    entities/presentation names/crew-assignment entities depending on
    the current state of Studio.
    """
    def __init__(self):
        EntityISearcher.__init__(self)

    def getAuditDomain(self, area=Cui.CuiWhichArea):
        """
        Finds out what entities to perform an audit trail on
        
        @param area: CuiArea to evaluate on, defaults to CuiWhichArea

        @return : A list of presentators containing entities to perform audit trail on
                  A presentation name string
                  The entity that connects a crew to one of the entities in the first list
        """
        presentators = []
        presentationName = ""
        crewConnectionEntity = None
        try:
            activityType = Cui.CuiCrcEvalString(Cui.gpc_info, area, "object", "activity_type")
            is_ground_duty = Cui.CuiCrcEvalBool(Cui.gpc_info, area, "object", "ground_duty")
            is_ground_transport = Cui.CuiCrcEvalBool(Cui.gpc_info, area, "object", "ground_transport")
            is_flight = (activityType == "LEG") and not is_ground_duty and not is_ground_transport
            is_activity = False
            if not is_flight and not is_ground_duty and not is_ground_transport:
                is_activity = True

            areaMode = Cui.CuiGetAreaMode(Cui.gpc_info,area)
            crewEntity = None
            crewId = ""
            if areaMode == Cui.CrewMode:
                crewId = Cui.CuiCrcEvalString(Cui.gpc_info, area, "object", "crr_crew_id")
                crewTable = self.tm.table("crew")
                crewEntity = crewTable[crewId]

            if is_ground_duty:
                try:
                    presentators, presentationName, crewConnectionEntity = self.getGroundDuty(area, areaMode, crewEntity, activityType)
                except:
                    presentators, presentationName, crewConnectionEntity = self.getPersonalActivity(area, areaMode, crewId, crewEntity, activityType)
            if is_ground_transport:
               presentators , presentationName, crewConnectionEntity = self.getGroundTransport(area, areaMode, crewEntity)
            if is_flight:
                presentators, presentationName, crewConnectionEntity = self.getFlight(area, areaMode, crewEntity)
            if is_activity:
                presentators, presentationName, crewConnectionEntity = self.getPersonalActivity(area, areaMode, crewId, crewEntity, activityType)

        except:
            traceback.print_exc()

        return presentators, presentationName, crewConnectionEntity       

    def getPersonalActivity(self, area, areaMode, crewId, crew, activityType):
        """
        PACT factory method
        """
        sobt = Cui.CuiCrcEvalAbstime(Cui.gpc_info, area, "object", "departure_orig")
        presentationName = "%s for %s at %s"%(activityType,crewId,convertDateTime(sobt))
        activityTable = self.tm.table("crew_activity")
        activitySetTable = self.tm.table("activity_set")
        try: 
            activity = activitySetTable[activityType]
        except:
            activity = activitySetTable.getOrCreateIdentity(activityType)
        entity = activityTable[(AbsTime.AbsTime(sobt),crew,activity,)]
        if areaMode == Cui.CrewMode:
            crewConnectionEntity = entity
        else:
            crewConnectionEntity = None

        results = self.search('crew_activity',{'st':int(sobt),
                                              'crew':str(crewId),
                                              'activity': str(activityType)})
        presentators = []
        for (entityI, pk) in results:
            presentators.append(Presentator(entityI, pk))
        return presentators, presentationName, crewConnectionEntity


    def getGroundDuty(self, area, areaMode, crew, activityType):
        """
        Ground Duty factory method
        If this method throws, try to get the information from getPersonalActivity
        """
        sobt = Cui.CuiCrcEvalAbstime(Cui.gpc_info, area, "object", "departure_orig")
        try:
            crewId = Cui.CuiCrcEvalString(Cui.gpc_info, area, "object", "crr_crew_id")
            presentationName = "%s for %s at %s"%(activityType,crewId, convertDateTime(sobt))
        except:
            presentationName = "%s at %s"%(activityType, convertDateTime(sobt))
        groundTaskTable = self.tm.table("ground_task")
        try:
            uuid = Cui.CuiCrcEvalString(Cui.gpc_info, area, "object", "ground_uuid")
            entity = groundTaskTable[(AbsTime.AbsTime(sobt),uuid)]
            results = self.search("ground_task", {'st':int(sobt), 'id':uuid})
            if areaMode == Cui.CrewMode:
                crewGroundDutyTable = self.tm.table("crew_ground_duty")
                crewConnectionEntity = crewGroundDutyTable[(entity,crew)]
            else:
                crewConnectionEntity = None
        except:
            raise

        presentators = []
        for (entityI, pk) in results:
            presentators.append(Presentator(entityI, pk))
        return presentators, presentationName, crewConnectionEntity

    def getGroundTransport(self, area, areaMode, crew):
        """
        Ground Transport factory method
        """
        activitySubType = Cui.CuiCrcEvalString(Cui.gpc_info, area, "object", "activity_subtype")
        sobt = Cui.CuiCrcEvalAbstime(Cui.gpc_info, area, "object", "departure_orig")
        departureStation = Cui.CuiCrcEvalString(Cui.gpc_info, area, "object", "departure_airport_name")
        presentationName = "%s departing from %s at %s"%(activitySubType,departureStation,convertDateTime(sobt))
        
        if areaMode == Cui.CrewMode:
            activityTable = self.tm.table("crew_activity")
            activitySetTable = self.tm.table("activity_set")
            activity = activitySetTable[activitySubType]
            entity = activityTable[(AbsTime.AbsTime(sobt),crew,activity,)]
            crewConnectionEntity = entity
            searchDict = {'crew':crew.id, 'st': int(sobt), 'activity': activitySubType}
            results = self.search("crew_activity", searchDict)
        else:
            searchDict = {'st': int(sobt), 'activity': activitySubType, 'adep':departureStation}
            results = self.search("trip_activity", searchDict)
            crewConnectionEntity = None

        presentators = []
        for (entityI, pk) in results:
            presentators.append(Presentator(entityI, pk))
        return presentators, presentationName, crewConnectionEntity

    def getFlight(self, area, areaMode, crew):
        """
        Flight leg factory method
        """
        sobt = Cui.CuiCrcEvalAbstime(Cui.gpc_info, area, "object", "activity_scheduled_start_time")
        number = Cui.CuiCrcEvalInt(Cui.gpc_info, area, "object", "flight_number")
        carrier = Cui.CuiCrcEvalString(Cui.gpc_info, area, "object", "flight_carrier")
        suffix = Cui.CuiCrcEvalString(Cui.gpc_info, area, "object", "flight_suffix")
        departureStation = Cui.CuiCrcEvalString(Cui.gpc_info, area, "object", "departure_airport_name")
        fd = Common.createFd(carrier, number, suffix)
        presentationName = "%s departing from %s at %s"%(fd,departureStation,convertDateTime(sobt))

        searchDict = {'sobt':int(sobt), 'fd':str(fd), 'adep': departureStation}
        results = self.search('flight_leg', searchDict)
        crewConnectionEntity = None
        if areaMode == Cui.CrewMode:
            flightTable = self.tm.table("flight_leg")
            airportTable = self.tm.table("airport")
            adep = airportTable.getOrCreateIdentity(departureStation)
            entity = flightTable[(AbsTime.AbsTime(sobt),fd,adep,)]
            crewFlightDutyTable = self.tm.table("crew_flight_duty")
            crewConnectionEntity = crewFlightDutyTable[(entity,crew)]

        presentators = []
        for (entityI, pk) in results:
            presentators.append(Presentator(entityI, pk))
        return presentators, presentationName, crewConnectionEntity
        
class LegAuditTrail(object):
    """
    Constructor for Leg based audit trail.  
    @param area: Cui area, default CuiWhichArea
    """
    def __init__(self, domainFactory, area=Cui.CuiWhichArea):
        self.header = ""
        self.auditTrailRows = []
        self._area = area
        self._domainFactory = domainFactory

    def run(self, returnstring=False):
        """
        Entry point that performs the audit trail logic. Will ask the AuditDomainFactory for
        entities to perform audit trail on, do this audit trail and present it with a call to
        self.show()
        """

        # Make sure models agree with eachother
        Cui.CuiSyncModels(Cui.gpc_info)
                
        tm = M.TableManager.instance()
        presentators, presentationName, crewConnection = self._domainFactory.getAuditDomain(self._area)
        self.header = presentationName or "Audit Trail"

        # If we have an unsaved leg not connected to a crew, we end up here
        if presentationName and not crewConnection and not presentators:
            self.auditTrailRows.append("This leg is not saved")

        # Set message based on 'preference' times.
        options_preference = Crs.CrsGetModuleResource("preferences", Crs.CrsSearchModuleDef, "RulerTimePresentation")
        dest_airport = Crs.CrsGetModuleResource("preferences", Crs.CrsSearchModuleDef, "DstAirport")
        head1 = ''
        if options_preference == '1':
            head1 = "\n (... Leg times reference with station: %s (not UTC) ... )" % dest_airport
            
        # Are we connected to a crew, say who assigned it and when
        if crewConnection:
            crewid = crewConnection.crew.id
            crewDescription = StudioGui.getInstance().createCrewDescription(crewid)
            try:
                ci = tm.getCommitInfo(crewConnection)
                user = ci.getUser()
                commitTime =  ci.getCommitTime()
                self.auditTrailRows.append("Assigned to: %s by %s at %s%s"%(crewDescription  ,user, convertDateTime(commitTime, 0),head1))
            except:
                user = os.environ.get("USER")
                self.auditTrailRows.append("Assigned to: %s by %s (not saved yet)"%(crewDescription,user))                

        #Get a list of audit trails together with their presentator object
        auditTrails = [(tm.auditTrailI(pres.entity), pres) for pres in presentators]
        explodedTrails = []
        for audits, pres in auditTrails:
            explodedTrails.extend(zip(audits, len(audits)*[pres]))

        #Sort this list because we can have multiple entities that generates audit trails
        # and we want to display them in commit order
        decAuditTrails = [(audit.commitInfo().getCommitId(), i,(audit, pres)) for i,(audit, pres) in enumerate(explodedTrails)]
        decAuditTrails.sort()
        auditTrails = [x for _,_,x in decAuditTrails]
        
        for audit, presentator in auditTrails:
            self.presentRevision(audit, presentator)
        if returnstring:
            return "\n".join(self.auditTrailRows)
        self.show()
    
    def presentRevision(self, audit, presentator):
        """
        Performs the presentation logic so that the information in audit
        gets presented based on the Presentator instance

        @param audit: A single audit from the TM audit trail list
        @param presentator: Presentator instance for the entity that audit was
                             produced from
        @return :Nothing, changes the internal state by adding rows to self.auditTrailRows
        """
        ci = audit.commitInfo()
        diff = audit.diff()
        if not diff:
            return

        changeType = 0
        for d in diff:
            #Assumed that only one diff type per commit and table
            changeType = d.getType()
            continue

        #Say what entity that have been deleted and go to the next audit part
        if changeType == M.Change.REMOVED:
            self.auditTrailRows.append("\n%s by %s at %s"%(presentator.getTypeString(changeType),
                                                           ci.getUser(),
                                                           convertDateTime(ci.getCommitTime(), 0)))
            self.auditTrailRows.append(presentator.deleteDesc(changeType))
            return

        #Handle additions and modifications, print changes per column
        addedHeader = False
        for c in diff:
            c = presentator.sort(c)
            for (column,old,new) in c:
                auditRow = presentator.present(changeType, column, old, new)
                # Add heading only if we know the change results in a visible trail
                if (auditRow and not addedHeader):
                    self.auditTrailRows.append("\n%s by %s at %s"%(presentator.getTypeString(changeType),
                                                                   ci.getUser(),
                                                                   convertDateTime(ci.getCommitTime(), 0)))
                    addedHeader = True
                if auditRow:
                    self.auditTrailRows.append(auditRow)

    def show(self):
        """
        Default implementation to view the report.
        Write the report to file and display using Csl.
        """
        fname = tempfile.mktemp()
        trailFile = open(fname,"w")

        trailString = "\n".join(self.auditTrailRows)
        trailFile.write(trailString)
        trailFile.flush()
        trailFile.close()
        Csl.Csl().evalExpr('csl_show_file("%s","%s",0)' % (self.header, fname))
        try:
            os.unlink(fname)
        except:
            pass
        
def Show(area=Cui.CuiWhichArea):
    try:
        # Gather and build the Audit Trail
        trail = LegAuditTrail(AuditDomainFactory(), area)
        trail.run()
    finally:
        traceback.print_exc()

        
def Get(area=Cui.CuiWhichArea):
    try:
        # Gather and build the Audit Trail
        trail = LegAuditTrail(AuditDomainFactory(), area)
        return trail.run(returnstring=True)
    finally:
        traceback.print_exc()
    
    
            

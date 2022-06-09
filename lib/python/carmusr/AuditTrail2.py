
#
#######################################################
#
# Audit Trail 2
#
# -----------------------------------------------------
# Provide audit trail functionality on any table.
# Compared to CrewAuditTrail this implementation uses
# more functionality from Dave, for example to keep
# track of what is the key in different tables.
# Th audit trail in the modelserver cannot find removed
# rows, but this can.
# -----------------------------------------------------
# Created:    2008-07-09
# By:         Jeppesen, Sten Larsson
#
#######################################################

from AbsTime import AbsTime
from carmensystems.dave import dmf, baselib
import modelserver as M
import traceback
import Dates

class AuditTrail2:
    """
    Used to find rows in database, even deleted ones.
    """

    def __init__(self):
        """
        Create an instance and connect to database
        """
        self.tm = M.TableManager.instance()
        self.conn = dmf.EntityConnection()
        self.conn.open(self.tm.getConnStr(), self.tm.getSchemaStr())

    def __del__(self):
        """
        Disconnect from database.
        """
        self.conn.close(False)

    def search(self, entityName, conditions):
        """
        Find all records in database that matches some conditions.

        @param entityName: Name of the entity (table)
        @param conditions: A dictionary of database column -> value pairs.
                           AbsTimes should be converted to ints.
        @return: A list of tuples where the first is the keys in a list,
                 and the second is a GenericEntityI for use with
                 tm.auditTrailI()
        """
        entitySpec = self.conn.getEntitySpec(entityName)
        (filter, key) = self._create_filter(entitySpec, conditions)
        table = self.tm.table(entityName)

        self.conn.beginReadTxn()
        try:
            # Set up filters
            revFilter = baselib.RevisionFilter()
            revFilter.withDeleted(True)
            self.conn.setRealSnapshot(revFilter)
            self.conn.setSelectParams(key)

            # Perform the lookup
            self.conn.select(entityName, filter, True)
            res = []
            while True:
                record = self.conn.readRecord()
                if record is None:
                    break
                keyList = record.keyAsList(entitySpec)
                keyList2 = []
                keyStrings = []
                for i in range(entitySpec.getKeyCount()):
                    type = entitySpec.getKeyColumn(i).getApiType()
                    if type == baselib.TYPE_ABSTIME:
                        value = AbsTime(keyList[i])
                    else:
                        value = keyList[i]
                    keyList2.append(value)
                    keyStrings.append(str(value).replace('+','\+'))
                res.append((keyList2, table.getOrCreateRef('+'.join(keyStrings))))
            return res

        finally:
            self.conn.endReadTxn()

    def _create_filter(self, entitySpec, conditions):
        """
        Create a filter from the specified conditions.

        @param entitySpec: An dmf.EntitySpec describing the Entity.
        @param conditions: See search
        @return: A tuple where the first item is the filter as a string,
                 and the second is a baselib.Key for the parameter values.
        """
        key = baselib.Key(len(conditions))
        tests = []
        i = 0
        for name, value in conditions.iteritems():
            tests.append('$.%s=%%:%i' % (name, i+1))
            type = entitySpec.getColumnByAlias(name).getApiType()
            key.setValue(i, self._to_value(value, type))
            i += 1

        filter = baselib.Filter(entitySpec.getName())
        filter.where(' and '.join(tests))

        return (filter, key)

    def _to_value(self, value, type):
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

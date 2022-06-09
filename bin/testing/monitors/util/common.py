import xmlrpclib
import httplib
import sys, os

# Exit statuses recognized by Nagios
UNKNOWN = -1
OK = 0
WARNING = 1
CRITICAL = 2


_conn = None
def SQL(sql, dbUrl="", dbSchema=""):
    from carmensystems.dig.framework.dave import DaveConnector
    if dbUrl == "":
        dbUrl = os.environ['DB_URL']
    if dbSchema == "":
        dbSchema = os.environ['DB_SCHEMA']
        
    global _conn
    if _conn is None:
        _conn = DaveConnector(dbUrl, dbSchema)
    l1conn = _conn.getL1Connection()
    l1conn.rquery(sql, None)
    r = []
    try:
        while True:
            l = l1conn.readRow()
            if not l: return r
            r.append(l.valuesAsList())
    finally:
        l1conn.endQuery()
        _conn.close()
        _conn = None

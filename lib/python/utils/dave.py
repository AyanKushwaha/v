

"""
This module contains some classes to facilitate access to Dave functions from
Python:

    L1: a way of iterating using level 1 connections (dmf.Connection)

    EC: an extension to carmensystems.dave.dmf.EntityConnection()

    GM: an extension to carmensystems.dave.genmodel()

    RW: a simplified interface to camensystems.dave.recwriter

Note (1): The same or better functionality is implemented in DIG, which also
has been more extensibly tested.

Note (2): See usage examples last in this file.
"""

# For usage examples: see bottom of this file and 'test_dave.py'.

# imports ================================================================{{{1
import datetime
import logging
import sys

import utils.dt
from carmensystems.dave import genmodel, recwriter, dmf, baselib
from AbsTime import AbsTime
from RelTime import RelTime


# exports ================================================================{{{1
__all__ = ['L1', 'EC', 'GM', 'RW']


# Set up logging --------------------------------------------------------{{{1
log = logging.getLogger('utils.dave')


# Translations to/from internal data formats ============================={{{1

class APITypeEncoder(dict):
    # Numeric API types and names, the names are chosen to fit the 'set'/'get'
    # methods in DAVE, except for 'TimeStamp' which is only used at one place
    # (AFAIK) in 'dave_revision'.

    types_names = (
        (baselib.TYPE_INVALID, None),      # 0
        (baselib.TYPE_ABSTIME, 'AbsTime'), # 65 (A)
        (baselib.TYPE_BOOL, 'Bool'),       # 66 (B)
        (baselib.TYPE_CHAR, 'Char'),       # 67 (C)
        (baselib.TYPE_DATE, 'Date'),       # 68 (D)
        (baselib.TYPE_FLOAT, 'Float'),     # 70 (F)
        (baselib.TYPE_INT, 'Int'),         # 73 (I)
        (baselib.TYPE_RELTIME, 'RelTime'), # 82 (R)
        (baselib.TYPE_STRING, 'String'),   # 83 (S)
        (84, 'TimeStamp'),             # 84 (T) NOT OFFICIAL
        (baselib.TYPE_UUID, 'UUID'),       # 85 (U)
    )
    names = [n for t, n in types_names]
    types = [t for t, n in types_names]

    def __init__(self):
        dict.__init__(self, self.types_names)

    def encode(self, input):
        t = ord(input.upper()[0])
        if not t in self.types:
            raise NotImplementedError("API name '%s' not implemented." % input)
        return t

    def decode(self, input):
        try:
            return self[input]
        except:
            raise NotImplementedError("API type '%s' not implemented." % input)


api_types = APITypeEncoder()


class BaseEncoding:
    """Methods 'encode' and 'decode' are used to translate to/from DAVE
    internal formats."""
    @classmethod
    def encode(cls, input):
        if input is None:
            return None
        else:
            return cls.Codec().encode(input)

    @classmethod
    def decode(cls, input):
        if input is None:
            return None
        else:
            return cls.Codec().decode(input)


class BoolEncoding(BaseEncoding):
    """Convert True/False to '1'/'0'. Note that in tables this will show up as
    'Y'/'N', but the DAVE api requires 1/0."""
    class Codec:
        def encode(self, input):
            return (0, 1)[bool(input)]

        def decode(self, input):
            try:
                return input.upper()[:1] in ('Y', '1', 'T')
            except:
                return bool(input)


class IntEncoding(BaseEncoding):
    """Convert to/from int."""
    class Codec:
        def encode(self, input):
            return input

        def decode(self, input):
            return int(input)


class FloatEncoding(BaseEncoding):
    """Convert to/from float."""
    class Codec:
        def encode(self, input):
            return input

        def decode(self, input):
            return float(input)


class StringEncoding(BaseEncoding):
    """Convert to/from string of characters."""
    class Codec:
        def encode(self, input):
            return input

        def decode(self, input):
            return str(input)


class CharEncoding(BaseEncoding):
    """Convert to/from single character."""
    class Codec(StringEncoding.Codec):
        def encode(self, input):
            return input[:1]


# UUID is stored as a string.
UUIDEncoding = StringEncoding


class RelTimeEncodingA(BaseEncoding):
    """RelTime version: Convert to/from number of minutes."""
    class Codec:
        def encode(self, input):
            return int(input)

        def decode(self, input):
            return RelTime(input)


class RelTimeEncodingD(BaseEncoding):
    """timedelta version: Convert to/from number of minutes."""
    class Codec:
        def encode(self, input):
            return utils.dt.td2m(input)

        def decode(self, input):
            return utils.dt.m2td(input)


class AbsTimeEncodingA(BaseEncoding):
    """AbsTime version: Convert to/from number of minutes since epoch."""
    class Codec:
        def encode(self, input):
            return int(input)

        def decode(self, input):
            return AbsTime(input)


class AbsTimeEncodingD(BaseEncoding):
    """datetime version: Convert to/from number of minutes since epoch."""
    class Codec:
        def encode(self, input):
            return utils.dt.dt2m(input)

        def decode(self, input):
            return utils.dt.m2dt(input)


class DateEncodingA(BaseEncoding):
    """AbsTime version: Convert to/from number of days since epoch."""
    class Codec:
        def encode(self, input):
            # Rounding?
            return int(input) / 1440

        def decode(self, input):
            return AbsTime(1440 * input)


class DateEncodingD(BaseEncoding):
    """datetime version: Convert to/from number of days since epoch."""
    class Codec:
        def encode(self, input):
            return utils.dt.dt2d(input)

        def decode(self, input):
            return utils.dt.d2dt(input)


class TimeStampEncodingA(BaseEncoding):
    """AbsTime version: Convert to/from number of seconds since epoch.
    NOTE: AbsTime is not very well suited for this since it cannot show any
    seconds."""
    class Codec:
        def encode(self, input):
            return int(input)

        def decode(self, input):
            return AbsTime(input / 60)


class TimeStampEncodingD(BaseEncoding):
    """datetime version: Convert to/from number of seconds since epoch."""
    class Codec:
        def encode(self, input):
            return utils.dt.dt2s(input)

        def decode(self, input):
            return utils.dt.s2dt(input)


class EncodingBase(dict):
    def __init__(self):
        dict.__init__(self, {
            baselib.TYPE_BOOL: BoolEncoding,
            baselib.TYPE_CHAR: CharEncoding,
            baselib.TYPE_FLOAT: FloatEncoding,
            baselib.TYPE_INT: IntEncoding,
            baselib.TYPE_STRING: StringEncoding,
            baselib.TYPE_UUID: UUIDEncoding,
        })

    def from_name(self, type_name):
        """Return encoding from a name (like 'Date')."""
        return self[api_types.encode(type_name)]


class EncodingAbsTime(EncodingBase):
    """Encodings for the AbsTime/RelTime family."""
    def __init__(self):
        EncodingBase.__init__(self)
        self.update({
            baselib.TYPE_ABSTIME: AbsTimeEncodingA,
            baselib.TYPE_DATE: DateEncodingA,
            baselib.TYPE_RELTIME: RelTimeEncodingA,
            84: TimeStampEncodingA,
        })


class EncodingDateTime(EncodingBase):
    """Encodings for the datetime/timedelta family."""
    def __init__(self):
        EncodingBase.__init__(self)
        self.update({
            baselib.TYPE_ABSTIME: AbsTimeEncodingD,
            baselib.TYPE_DATE: DateEncodingD,
            baselib.TYPE_RELTIME: RelTimeEncodingD,
            84: TimeStampEncodingD,
        })


class encodings:
    abstime = EncodingAbsTime()
    datetime = EncodingDateTime()
    # Default is to use AbsTime
    default = abstime


# Help classes ==========================================================={{{1

# KeyMaker ---------------------------------------------------------------{{{2
class KeyMaker(list):
    """Return a baselib.Key object with values from tuple or dict."""
    def __init__(self, entity_spec, encoding=encodings.default):
        """Get key column definitions. Append to own (self) list the conversion
        functions."""
        list.__init__(self)
        self.encoding = encoding
        for i in xrange(entity_spec.getKeyCount()):
            col = entity_spec.getKeyColumn(i)
            self.append((col.getName(), col.getApiType()))

    def __str__(self):
        return '<%s key_columns="%s">' % (_strclass(self.__class__), ', '.join([x for x, _ in self]))

    def __call__(self, key_tuple):
        """Return baselib.Key object given a tuple of external values."""
        if len(key_tuple) > len(self):
            msg = 'KeyMaker cannot use more than %d keys, %s contains %d.' % (len(self), key_tuple, len(key_tuple))
            log.error(msg)
            raise ValueError(msg)
        key = baselib.Key(len(key_tuple))
        for i in xrange(len(key_tuple)):
            name, apitype = self[i]
            getattr(key, 'set' + api_types.decode(apitype))(i,
                    self.encoding[apitype].encode(key_tuple[i]))
        return key

    def map2key(self, map):
        """Return baselib.Key object given a record (or other type of
        dictionary)."""
        keys = []
        for n, a in self:
            if n not in map:
                # Partial key
                break
            keys.append(map[n])
        return self(keys)


# Record -----------------------------------------------------------------{{{2
class Record(dict):
    """Record representation. The items are 'raw' data (in internal
    representation). The attributes are converted (external) representation of
    the same data."""
    def __init__(self, map={}, conv=None):
        """ Allow init of record with a dict. """
        dict.__init__(self, map)
        self.__conv = conv

    def __getattr__(self, k):
        if self.__conv is None:
            return self[k]
        return self.__conv[k].decode(self[k])

    def __setattr__(self, k, v):
        if k.startswith('_'):
            dict.__setattr__(self, k, v)
            return
        if self.__conv is None:
            self[k] = v
        else:
            self[k] = self.__conv[k].encode(v)

    def __delattr__(self, k):
        del self[k]

    def __str__(self):
        """ For testing. """
        values = ['%s="%s"' % (k, v) for (k, v) in self.iteritems() if not k.startswith('_')]
        return '<%s %s>' % (_strclass(self.__class__), ' '.join(values))

    def evaluate(self, expr):
        """Evaluate the Python expression. If the expression returns False,
        then the record will be discarded.  Malformed expressions will cause an
        exception."""
        return eval(expr, self.__dict__, self.__dict__)


# ColumnTranslator -------------------------------------------------------{{{2
class ColumnTranslator(dict):
    """Create a dictionary of converter classes, the key is the column name."""
    def __init__(self, entity_spec, encoding=encodings.default):
        dict.__init__(self)
        for ix in xrange(entity_spec.getColumnCount()):
            col = entity_spec.getColumnByNum(ix)
            # Improvement?: Should it be getAlias() instead of getName()?
            self[col.getName()] = encoding[col.getApiType()]


# Level 1 connections (dmf.Connection) ==================================={{{1

# L1 ---------------------------------------------------------------------{{{2
class L1:
    """L1 - Level 1 connection (dmf.Connection).
    To be used for simple iteratations."""
    def __init__(self, conn, translator=None, encoding=encodings.default):
        if isinstance(conn, str):
            self.connection = dmf.Connection(conn)
        else:
            self.connection = conn
        self.translator = translator
        self.encoding = encoding

    def search(self, query, params=None):
        self.connection.rquery(query, params)
        R = self.connection.readRow()
        while R:
            if self.translator is None:
                yield R
            else:
                yield L1Record(R.valuesAsList(), self.translator, self.encoding)
            R = self.connection.readRow()
        self.connection.endQuery()


# L1Record ---------------------------------------------------------------{{{2
class L1Record(dict):
    """
    translator is a sequence of tuples (name, type)
    e.g.
    translator = [('activity', 'String'), ('st', 'AbsTime'), ('et', 'AbsTime')]
    """
    def __init__(self, t, translator, encoding=encodings.default):
        self.translator = translator
        if len(t) != len(translator):
            msg = "%s - Number of values (%d) does not match the number of result fields (%d)." % (
                    _locator(self), len(t), len(translator))
            log.error(msg)
            raise ValueError(msg)
        for i in xrange(len(translator)):
            colname, type_name = translator[i]
            self[colname] = encoding.from_name(type_name).decode(t[i])

    @classmethod
    def fromRow(cls, r, translator, encoding=encodings.default):
        return cls(r.valuesAsList(), translator, encoding)

    def __str__(self):
        values = ['%s="%s"' % (n, self[n])  for n, _ in self.translator]
        return '<%s %s>' % (_strclass(self.__class__), ' '.join(values))

    def __getattr__(self, k):
        return self[k]


# EntityConnection layer ================================================={{{1

# EC ---------------------------------------------------------------------{{{2
class EC(dmf.EntityConnection):
    """
    Extend dmf.EntityConnection().
    """
    def __init__(self, connstr, schema, branch=None, encoding=encodings.default):
        """
        For each method in dmf.EntityConnection, dynamically create a method
        with the same name in this class.
        """

        dmf.EntityConnection.__init__(self)

        if branch is None:
            branch = 1
        self.open(str(connstr), str(schema))
        self.setProgram("%s.%s" % (self.__module__, self.__class__.__name__))
        self.__tables = {}
        self.__encoding = encoding
        self._rev_filter = ECRevisionFilter()

    def __del__(self):
        try:
            self.close()
        except:
            # Warning?
            pass

    def __getattr__(self, tn):
        """ Return handle to the table with name 'tn'. """
        if tn == 'this':
            # SKU-3913 'SWIG' and recursion
            return dmf.EntityConnection.__getattr__(self, tn)
        if not tn in self.__tables:
            self.__load(tn)
        return self.__tables[tn]

    def __delattr__(self, tn):
        if self.inReadTxn():
            self.endReadTxn()
        del self.__tables[tn]

    def __str__(self):
        """ For testing. """
        return '<%s tables="%s">' % (_strclass(self.__class__), ', '.join(self.__tables))

    def __load(self, *args):
        """ Add to the internal table list. """
        for t in args:
            self.__tables[t] = ECResultSet(self, t, self.__encoding)

    @property
    def cid(self):
        self.beginReadTxn()
        cid = self.getSnapshotCid()
        self.endReadTxn()
        return cid

    def _set_snapshot(self):
        self.setSnapshot(self._rev_filter)


# ECRevisionFilter -------------------------------------------------------{{{2
class ECRevisionFilter(baselib.RevisionFilter):
    def __call__(self, with_deleted=False, maxcid=None, mincid=None, skip_revision=None):
        if with_deleted:
            self.withDeleted(True)
        if not maxcid is None:
            self.setMaxCID(maxcid)
        if not mincid is None:
            self.setMinCID(mincid)
        if not skip_revision is None:
            self.setSkipRevid(skip_revision)


# ECResultSet ------------------------------------------------------------{{{2
class ECResultSet:
    """
    Iterate table. Returns Python generator which returns Record object upon
    each iteration.
    """
    def __init__(self, ec, entityName, encoding=encodings.default):
        """ ec is an EC object, entityName is table name. """
        self.ec = ec
        self.entityName = entityName
        self.spec = ec.getEntitySpec(entityName)
        self.filter = baselib.Filter(entityName)
        self.translator = ColumnTranslator(self.spec, encoding)
        self.cid = None

    def __iter__(self):
        """ Reset search conditions. """
        self.filter.clear()
        return self.__iterator()

    def search(self, s):
        """ Search using search condition.  Return generator object. """
        self.filter.clear()
        self.filter.where(s)
        return self.__iterator()

    def record(self, init={}):
        return Record(init, self.translator)

    def __str__(self):
        """ For testing. """
        return '<%s entity=%s filter=%s>' % (
            _strclass(self.__class__),
            self.entityName,
            self.filter
        )

    def __iterator(self):
        """ Return generator object. """
        self.cid = self.ec.beginReadTxn()
        self.ec._set_snapshot()
        self.ec.select(self.entityName, self.filter)
        while True:
            r = self.ec.readRecord()
            if r is None:
                break
            yield Record(r.valuesAsDict(self.spec), self.translator)
        self.ec.endReadTxn()

    def __del__(self):
        if self.ec.inReadTxn():
            self.ec.endReadTxn()


# The generic model layer ================================================{{{1

# GMRecord ---------------------------------------------------------------{{{2
class GMRecord(Record):
    """Wrapper for Row objects."""
    def __init__(self, map, conv, row):
        self.__dict__['_row'] = row
        Record.__init__(self, map, conv)

    def __getattr__(self, k):
        if k == '_row':
            return self.__dict__['_row']
        else:
            return Record.__getattr__(self, k)

    def __setattr__(self, k, v):
        Record.__setattr__(self, k, v)
        self._row.updateRow(self)

    def __delattr__(self, k):
        del self[k]
        self._row.updateRow(self)

    def remove(self):
        """For TableManager compatibility."""
        self._row.setDeleted(True)


# GM ---------------------------------------------------------------------{{{2
class GM(genmodel.Model):
    """ Extend genmodel.Model """
    def __init__(self, connection, schema, branch=None, encoding=encodings.default):
        if branch is None:
            genmodel.Model.__init__(self, connection, schema)
        else:
            genmodel.Model.__init__(self, connection, schema, branch)
        self.__encoding = encoding
        self.__tables = {}

    def __call__(self, *tables):
        self.loadTables(tables)

    def __getattr__(self, var):
        """ Return handle to the table with name 'var'. """
        if not var in self.__tables:
            self.loadTables((var,))
        return self.__tables[var]

    def __del__(self):
        """ To conserve memory. """
        self.unload()
        self.destroyTables()
        genmodel.Model.__del__(self)

    def __str__(self):
        """ For testing. """
        return '<%s tables="%s">' % (_strclass(self.__class__), ', '.join(self.__tables))

    def loadTables(self, tables):
        """ This function is added to make GM a little more similar to
        modelserver. """
        for t in tables:
            self.__tables[t] = GMTable(self, t, self.__encoding)


# GMTable ----------------------------------------------------------------{{{2
class GMTable(genmodel.Table):
    """ Extend genmodel.Table. """
    def __init__(self, model, table_name, encoding=encodings.default):
        genmodel.Table.__init__(self, model, table_name)
        self.__model = model
        self.__table_name = table_name
        self.__spec = self.getEntitySpec()
        self._key = KeyMaker(self.__spec, encoding=encoding)
        self.__translator = ColumnTranslator(self.__spec, encoding)

    def __getitem__(self, k):
        """ Exact key match, return one record. """
        r = self.getRow(self._key(k))
        return GMRecord(r.valuesAsDict(self.__spec), self.__translator, r)

    def __iter__(self):
        """ Reset search conditions. """
        filter = self.getSelector()
        filter.clear()
        return self.__generator()

    def create(self, k):
        """ This method introduced to make this class look more like the
        modelserver equivalent. """
        r = self.addRow(self._key(k))
        return GMRecord(r.valuesAsDict(self.__spec), self.__translator, r)

    def set_filter(self, s):
        """ Limit the loading to a subsection of the table. """
        filter = self.getSelector()
        filter.clear()
        filter.where(s)
        self.setSelector(filter)

    def sql_search(self, s):
        """ Search  using a SQL search condition. (cf modelserver table search). """
        # NOT recommended way of searching
        self.set_filter(s)
        self.__model.unload()
        self.__model.load() # This is why, only working for simple searches, the model
                    # will get confused.
        return self.__generator()

    def py_search(self, s):
        """ Search using a Python expression. """
        return self.__generator(match=s)

    def pk_search(self, key, match=None):
        """ Search using a Python expression and partial key (as a tuple). """
        return self.__generator(key=self._key(key), match=match)

    def __generator(self, match=None, key=None):
        """ Returns generator object. """
        if key is None:
            it = self.begin()
        else:
            keytup = key.valuesAsList()
            keylen = len(keytup)
            it = self.lower_bound(key)
        while not self.isEnd(it):
            n = it.deref()
            if not key is None:
                if n.keyAsList(self.__spec)[:keylen] != keytup:
                    break
            if match is None:
                yield GMRecord(n.valuesAsDict(self.__spec), self.__translator, n)
            else:
                record = GMRecord(n.valuesAsDict(self.__spec), self.__translator, n)
                if record.evaluate(match):
                    # Only return object that matches.
                    yield record
            it.next()
        return


# recwriter =============================================================={{{1

# RWRecord ---------------------------------------------------------------{{{2
class RWRecord(recwriter.Record):
    """Extension to recwriter.Record, has one method for each operation
    type."""
    def __init__(self, table):
        """Prepare the record for insertion of values."""
        log.debug("%s(%s)" % (_locator(self), table))
        recwriter.Record.__init__(self)
        self._table = table
        self._entity_spec = table.getMetaData()
        self.init(self._entity_spec)

    def dbdelete(self, rec):
        """Delete one or many records."""
        log.debug('%s(%s)' % (_locator(self), rec))
        self._table.deleteRecords(KeyMaker(self._entity_spec).map2key(rec))

    def dbupdate(self, rec, skipKey=False):
        """Update an existing record."""
        log.debug('%s(%s)' % (_locator(self), rec))
        self.update(rec, self._entity_spec, skipKey)
        # -2 will tell Dave that the record must exist already.
        self.setRevisionId(-2)
        self._table.addRecord(self)

    def dbwrite(self, rec, skipKey=False):
        """Insert or update."""
        log.debug('%s(%s)' % (_locator(self), rec))
        self.update(rec, self._entity_spec, skipKey)
        if 'revid' in rec:
            self.setRevisionId(rec['revid'])
        self._table.addRecord(self)

    def dbinsert(self, rec, skipKey=False):
        """Insert a new record."""
        log.debug('%s(%s)' % (_locator(self), rec))
        self.update(rec, self._entity_spec, skipKey)
        # 0 will tell Dave that the record cannot exist already.
        self.setRevisionId(0)
        self._table.addRecord(self)


# RW ---------------------------------------------------------------------{{{2
class RW:
    """ Utility for updating database.  See usage notes below.  """
    def __init__(self, conn, branch=None):
        """conn is an EntityConnection (or EC) object."""
        self.__model = recwriter.Model()
        self.__conn = conn
        self.branchid = branch

    def __getattr__(self, entity):
        """Return RWRecord (to be able to call it's
        dbupdate/dbdelete/dbinsert/dbwrite."""
        try:
            table = self.__model.getTable(entity)
        except RuntimeError:
            table = self.__model.newInitTable(entity, self.__conn)
        return RWRecord(table)

    def apply(self):
        """Apply the changes."""
        try:
            revid = self.__conn.beginWriteTxn()
            try:
                if not self.branchid is None:
                    self.__conn.setBranch(self.branchid)
                self.__model.save(self.__conn, True)
                self.__conn.commit('%s' % _locator(self))
                log.debug("%s - committed." % _locator(self))
            except Exception, e:
                log.error("RW.apply() got exception '%s'." % (e,))
                self.__conn.rollback()
                log.warning("%s - rolled back." % _locator(self))
                raise
        except Exception, e:
            self.__model.clear()
            log.warning("%s - rolled back as a result from %s." % (_locator(self), e))
            raise
        return revid


# functions =============================================================={{{1
# Don't know why we had a copy in the first place, but the duplicate in
# carmensystems.common.dave_utils was missing the reason field and crashes
# when the tuple is unpacked.
class txninfo(tuple):
    def __new__(cls, ec, revid):
        rf = baselib.RevisionFilter()
        rf.where('revid = %i' % revid)
        try:
            ec.beginReadTxn()
            txn_info = ec.txnInfo(ec.findTxn(rf)).valuesAsList()
        finally:
            ec.endReadTxn()
        return tuple.__new__(cls, txn_info)

    def __init__(self, ec, revid):
        (
            self.revid,
            self.commitid,
            self.cliprogram,
            self.clihost,
            self.cliuser,
            committs,
            self.remark,
            self.reason
        ) = self
        ce = datetime.datetime(1986, 1, 1) - datetime.datetime(1970, 1, 1)
        self.committs = datetime.datetime.fromtimestamp(committs) + ce


# _locator ---------------------------------------------------------------{{{2
def _locator(o):
    return "%s.%s.%s" % (o.__class__.__module__, o.__class__.__name__,
            sys._getframe(1).f_code.co_name)


# _strclass --------------------------------------------------------------{{{2
def _strclass(cls):
    """ Return 'module.class'. """
    return "%s.%s" % (cls.__module__, cls.__name__)


# Usage Examples ========================================================={{{1

# L1 ---------------------------------------------------------------------{{{2
# connstr = 'oracle:%s/%s@testnet-s4:1521/gtn01tst' % (schema, schema)
# 
# for x in L1(connstr).search(query):
#     print x
# 
# translator = (
#     ('activity', 'String'),
#     ('st', 'AbsTime'),
#     ('et', 'AbsTime'),
#     ('deleted', 'Bool'),
#     ('revid', 'Int'),
# )
# 
# for x in L1Iterator(connstr, translator).search(query):
#     print "---"
#     print "activity :", r.activity
#     print "st       :", r.st
#     print "et       :", r.et

# GM ---------------------------------------------------------------------{{{2
# from utils.dave import GM
# from AbsDate import AbsDate
#
# # init model
# g = GM('oracle:sk_sto_all/sk_sto_all@flm:1521/flm1010', 'sk_sto_all')
# g.flight_leg.set_filter('udor = %d' % int(AbsDate("20070110") / 1440))
# g.load()  ## IMPORTANT
# 
# # search flight_leg for flights with udor = 10Jan2007 and adep = 'ARN'
# for leg in g.flight_leg.py_search("adep == 'ARN'"):
#     print leg.fd, leg.udor, leg.adep, leg.ades

# for r in gm.crew_activity.sql_search("crew = '20370'"):
#     print "---"
#     print "activity :", r.activity
#     print "st       :", r.st
#     print "et       :", r.et

# EC ---------------------------------------------------------------------{{{2
# from tm import TM # to get connstr, ...
# from utils.dave import EC
#
# ec = EC(TM.getConnStr(), TM.getSchemaStr())
#
# # External representation:
# for r in ec.crew_activity.search("crew = '20370'"):
#     print "---"
#     print "activity :", r.activity
#     print "st       :", r.st
#     print "et       :", r.et
#
# # Internal representation:
# for r in ec.crew_activity.search("crew = '20370'"):
#     print "---"
#     print "activity :", r['activity']
#     print "st       :", r['st']
#     print "et       :", r['et']

# RW ---------------------------------------------------------------------{{{2
# from utils.dave import EC, RW
# 
# schema = 'sk_acosta_98'
# connstr = 'oracle:%s/%s@testnet-s4:1521/gtn01tst' % (schema, schema)
# 
# e = EC(connstr, schema)
# r = RW(e)
# for x in e.salary_admin_code:
#     if x.admcode == 'R':
#         x.description = 'one of many retro runs'
#         r.salary_admin_code.dbupdate(x)
# cid = r.apply()

# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=2:
# eof

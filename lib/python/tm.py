
# changelog {{{2
# [acosta:06/304@17:39] First version.
# [acosta:06/331@14:46] Dynamic "mimicking" of TableManager's methods.
# [acosta:07/009@13:55] Added TMC for use with Mirador.
# [acosta:07/127@10:38] Removed module variables _tm and _tables, these now
#   belong to the TableManager instance.  Added function reset() that will use
#   a new instance of TableManager().
# [acosta:07/198@02:06] Fixes for bugzilla #17455.
# [acosta:08/018@11:52] Fix for bugzilla #23313.
# }}}

"""
This module contains 'TM' which is an extension to
'modelserver.TableManager()'.

The module also contains some tools that can be used to find out whether a
table is stored in memory, if it is a Dave table or a table for metadata (e.g.
_entity).
"""

# imports ================================================================{{{1
import modelserver
import new
import unicodedata

# exports ================================================================{{{1
__all__ = ['TM', 'TMC', 'TempTable', 'reset', 'tableType', 'DaveType', 'MemoryType', 'MetaType', 'UnknownType']


# classes ================================================================{{{1

# BaseType ---------------------------------------------------------------{{{2
class BaseType(type):
    """
    This is a base class (modern class) for the different types available.
    """
    _desc = "no type"
    _type = None
    def __str__(cls):
        return cls._desc

    def __eq__(cls, other):
        if hasattr(other, 'entityDesc'):
            return other.entityDesc().entityType() == cls._type
        else:
            return other is cls


# DaveType ---------------------------------------------------------------{{{2
class DaveType(BaseType):
    """ A table stored persistently. """
    _desc = "Dave table"
    _type = modelserver.DAVE
    __metaclass__ = BaseType


# MemoryType -------------------------------------------------------------{{{2
class MemoryType(BaseType):
    """ Temporary memory tables. """
    _desc = "Memory table"
    _type = modelserver.MEMORY
    __metaclass__ = BaseType


# MetaType ---------------------------------------------------------------{{{2
class MetaType(BaseType):
    """ Meta tables, _entity, _fields """
    _desc = "Meta table"
    _type = modelserver.META
    __metaclass__ = BaseType


# UnknownType ------------------------------------------------------------{{{2
class UnknownType(BaseType):
    """ Marks table of unknown type. """
    _desc = "Unknown table type"
    __metaclass__ = BaseType


# TableManager -----------------------------------------------------------{{{2
class TableManager:
    """
    The class 'tm.TableManager' will take care of loading of tables (including
    tables that are referred), thus avoiding problems that could occur when
    referred tables are not loaded.

    All 'modelserver.TableManager()' methods are replicated by "mimicking",
    this makes it possible to use e.g. 'tm.TableManager().save()'.

    'TM' is a global, module instance of the 'tm.TableManager' class.

    Any attribute is interpreted as a table name, and the corresponding
    handle will be returned.

    Example 1 (creating own instance, make sure you only have one instance!):
        import tm
        MYDB = tm.TableManger()
        for c in MYDB.crew.search("(id=51082)"):
            print c.forenames

    Example 2 (better, using global instance):
        from tm import TM
        for x in TM.crew_document.search("&(doc.type=PASSPORT)(crew.id=51082)"):
            print x.docno

        # To load a whole bunch of tables:
        TM(['crew_document', 'crew_employment'])

        # The above call will also load:
        #   'crew_rank_set', 'country', 'crew_employment', 'crew', 'crew_document',
        #   'crew_base_set', 'crew_document_set', 'crew_carrier_set',
        #   'crew_region_set' and 'crew_company_set'
        # since these tables are referred from 'crew_document' and
        # 'crew_employment' and their referred tables.

    Example 3 (alternative):
        from tm import *
        for x in TM.crew:
            print x.id
    """

    # [acosta:06/331@12:36] There is some magic involved here, I don't know
    #                       the exact details, but it works...
    def __init__(self):
        """
        For each method in modelserver.TableManager, dynamically create a
        method with the same name in this class.  This method grabs an instance
        of modelserver.TableManager and calls the corresponding method.

        The reason for this design is that we want to be able to import this
        module without having to call modelserver.TableManager().instance(),
        or import of this module cannot be done from modules loaded in
        StudioCustom.py.

        The instance() is not retrieved until the first call to any of
        TableManager()'s methods.
        """
        self.__tm = None
        self.__tables = {}
        for att in dir(modelserver.TableManager):
            if not att.startswith('_') and callable(getattr(modelserver.TableManager, att)):
                code = 'def %s(self, *a, **k): return self._%s__init_tm().%s(*a, **k)' % (att, self.__class__.__name__, att)
                ccode = compile(code, '<string>', 'exec')
                # [acosta:06/331@12:44] This is very, very murky...
                # [acosta:07/198@02:07] Bug #17455: argument #2 set to
                # globals() instead of {} - gives exception handler a chance
                # to find the correct exception (or else RuntimeError will be
                # thrown).
                f = new.function(ccode.co_consts[0], globals(), att)
                setattr(self.__class__, att, f)

    ## The above __init__ results in a number of methods like these:
    #def addModule(self, *args, **keyw):
    #    return self.__init_tm().addModule(*args, **keyw)
    #def undo(self, *args, **keyw):
    #    return self.__init_tm().undo(*args, **keyw)

    def __call__(self, *args):
        """
        Load tables, if necessary, recurse to load all referred tables
        as well.
        """
        tables = set()
        for arg in args:
            if not arg is None:
                if not isinstance(arg, list) and not isinstance(arg, tuple):
                    arg = [str(arg)]
                tables.update(self.__referred(arg))
        if tables:
            self.loadTables(list(tables))
            for t in tables:
                self.__tables[t] = self.table(t)
        return self

    def __getattr__(self, table):
        """ Return handle to the table with name 'table'. """
        if not table in self.__tables:
            # invoke __call__ to load table.
            self(table)
        return self.__tables[table]

    def __repr__(self):
        return '<%s tm="%s" tables="%s">' % (_strclass(self.__class__), self.__tm, ', '.join(self.__tables))

    __str__ = __repr__

    def reset(self, unload_tables=[]):
        """ Reset by removing tables from internal list,
        causing them to be reloaded when nexed used.
        Default, if none given, is removing all tables.
        A new instance of 'modelserver.TableManager' will be 
        assigned by '__init_tm()' above. """
        self.__tm = None
        if unload_tables:
            for table in unload_tables:
                if self.__tables.has_key(table):
                    del self.__tables[table]
        else:
            self.__tables = {}

    # private methods ----------------------------------------------------{{{3
    def __init_tm(self):
        """ Get modelserver.TableManager instance. """
        # See Bugzilla #15262 and #19410
        if self.__tm is None or not self.__tm.isInstance(self.__tm):
            # This will give a link to the active TableManager if there
            # is one. If not, it will give a new "non-connected" instance
            # Might be a problem if used after closing a database-plan
            self.__tm = modelserver.TableManager.instance()
        return self.__tm

    def __referred(self, iterable):
        """ Find tables that are referred. """
        referred = set()
        for t in iterable:
            if not t in self.__tables:
                referred.add(t)
                for e in self.table('_referer').search('(referer=%s)' % (t)):
                    # recurse
                    if e.entity.entity not in referred:
                        referred.update(self.__referred([e.entity.entity]))
        return referred


# TMC --------------------------------------------------------------------{{{2
class TMC(TableManager):
    """
    Variant of TableManager that does not use the Studio instance.  Can be run
    with mirador, e.g. $CARMSYS/bin/mirador -s pythonmodule

    Example:
       from tm import TMC

       T = TMC('oracle:system/flamenco@flm:1521/flm1010', 'sk_sto_all_acosta_89')

       for c in T.crew:
          print c.id
    """

    def __init__(self, dbconn, schema):
        TableManager.__init__(self)
        self.__tm = modelserver.TableManager.create()
        dbconn = dbconn.encode('ascii')
        schema = schema.encode('ascii')
        self.__tm.connect(dbconn, schema)
        self.__tm.loadSchema()


    # private methods ----------------------------------------------------{{{3
    def __init_tm(self):
        """ Get modelserver.TableManager instance. """
        return self.__tm


# TempTable --------------------------------------------------------------{{{2
class TempTable:
    """
    This class has to be subclassed.  TempTable will create a temporary table,
    if the table does not exist.

    All 'modelserver.GenericTable()' methods are replicated by "mimicking".

    Typical usage:
        from tm import TempTable
        from modelserver import StringColumn, IntColumn

        class ATempTable(TempTable):
            _name = "tmp_a_table"
            _keys = [
                 IntColumn("key", "k")
                ]
            _cols = [
                 StringColumn("message", "M")
                ]

            def refresh(self):
                ...
                self.removeAll()
                ...
                rec = self.create((0,))
                ...

        att = ATempTable()
        for a in att:
            print a.message
    """

    _name = ''
    _keys = []
    _cols = []
    _table = None

    # [acosta:06/331@12:36] There is some magic involved here, I don't know
    #                       the exact details, but it works...
    def __init__(self, name=None, keys=None, cols=None):
        """
        Take care of the creation of the temp table and for each method in
        'modelserver.GenericTable', dynamically create a method with the same
        name in this class.
        """
        # Take care of optional arguments
        if not name is None:
            self._name = name
        if not keys is None:
            self._keys = keys
        if not cols is None:
            self._cols = cols

        # If temporary table already exists, keep its handle, else create
        # [acosta:09/019@16:34] The table gets created here.
        _ = self._get_or_create_table()

        dont_touch_these = ('__init__', '__setattr__', '__repr__', '__str__')
        # Copy methods from modelserver.Table
        for att in dir(modelserver.GenericTable):
            if not att in dont_touch_these and callable(getattr(modelserver.GenericTable, att)):
                code = 'def %s(self, *a, **k): return self._get_or_create_table().%s(*a, **k)' % (att, att)
                ccode = compile(code, '<string>', 'exec')
                # [acosta:06/331@12:44] This is very, very murky...
                # [acosta:07/198@02:07] Bug #17455: argument #2 set to
                # globals() instead of {} - gives exception handler a chance
                # to find the correct exception (or else RuntimeError will be
                # thrown).
                f = new.function(ccode.co_consts[0], globals(), att)
                setattr(self.__class__, att, f)

    ## The above __init__ results in a number of methods like this:
    #def create(self, *args, **keyw):
    #    return self._get_or_create_table().create(*args, **keyw)

    def __repr__(self):
        return '<%s _table="%s" _name="%s" _keys="%s" _cols="%s">' % (_strclass(self.__class__), repr(self._get_or_create_table()), self._name, ', '.join(map(str, self._keys)), ', '.join(map(str, self._cols)))

    __str__ = __repr__

    def _get_or_create_table(self):
        try:
            return getattr(TM, self._name)
        except:
            TM.createTable(self._name, self._keys, self._cols)
            return getattr(TM, self._name)


# private global variables ==============================================={{{1
# Don't touch these!
_tableTypes = [MemoryType, DaveType, MetaType]


# exported instance ======================================================{{{1
# To allow for: 'from tm import TM'
TM = TableManager()


# functions =============================================================={{{1

# reset ------------------------------------------------------------------{{{2
def reset():
    """ reset the global instance of TableManager. """
    global TM
    # [acosta:08/018@11:49] Fix for Bugzilla #23313, the old solution did not
    # update the value of 'TM' in files that imported from this file.
    TM.reset()


# tableType --------------------------------------------------------------{{{2
def tableType(t):
    """
    This function can be used to find out which type a certain table is.

    Example:
        from tm import *

        if tableType(TM.crew) == DaveType:
            # This is a Dave table
            ...
        elif tableType(TM.crew) == MemoryType:
            # This is a temporary table
    """
    try:
        return _tableTypes[_tableTypes.index(t)]
    except:
        return UnknownType


# _strclass --------------------------------------------------------------{{{2
def _strclass(cls):
    return "%s.%s" % (cls.__module__, cls.__name__)


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof

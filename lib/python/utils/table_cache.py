#

#
__version__ = "$Revision$"
"""
table_cache
Module for doing:
Cache and filter Table from TM or EC
@date:18Jul2008
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""
import re
from utils.dave import EC
import tm
import re
class TableCache:
    """
    Base class for caching datatable. Hashed on keys and filters out lines not matching filter
    """
    def __init__(self, tableName, keys, filter={}):
        self._table_name = tableName
        self._filter = filter
        self._raw_keys = keys
        self._items = {}
        self._index = 0
        self._compile_filter()
        self._populate()
        self._keys = self._items.keys()
        self._index = 0
        
    def _compile_filter(self):
        _tmp = re.compile(r'.*')
        for key in self._filter:
            if isinstance(self._filter[key],str):
                self._filter[key]=re.compile(r'%s'%self._filter[key])
            elif type(self._filter[key]) == type(_tmp):
                pass
            else:
                raise TypeError, "Invalid type in filter expression"
            
    
    def _populate(self):
        for entry in self._get_table_iterator():
            try:
                if self._filter and not self._test(entry, self._filter):
                    continue # Line didn't pass filter
                entry_key = []
                for key in self._raw_keys:
                    db_val = self._get_db_val_4_key(entry,key)
                    entry_key += [db_val]
                entry_key = '+'.join(entry_key)
                if self._items.has_key(entry_key): # Hash line
                    self._items[entry_key] += [entry]
                else:
                    self._items[entry_key] = [entry]
            except:
                pass

    def _get_table_iterator(self):
        return []

    def _get_db_val_4_key(self,entry,key):
        return ""
    
    def __repr__(self):
        return repr(self._items)
    
    def __str__(self):
        return repr(self)
    
    def __getitem__(self, key):
        return self._items[key]
    
    def __iter__(self):
        return self                 # simplest iterator creation

    def next(self):
        try:
            _index = self._index
            self._index += 1
            return self._keys[_index]
        except IndexError:
            self._index = 0
            raise StopIteration
        
    def items(self):
        return self._items.items()

    def __len__(self):
        return len(self._items)
    
    def get(self, key, default = [], filter={}): #Possible to further filter list
        
        if filter:
            items = self._items.get(key,default)
            return [element for element in items if self._test(element,filter)]
        
        return self._items.get(key,default)
    
    def _test(self, entry, filter):
        for key in filter:
            try:
                _val = self._get_db_val_4_key(entry,key)
            except:
                return False
            if not filter[key].match(_val):
                return False
        return True
    
class ECTableCache(TableCache):
    """
    Uses EC to read not loaded lines from DB
    """
    def __init__(self, tableName, keys, filter={}):
        self._ec = EC(tm.TM.getConnStr(), tm.TM.getSchemaStr())
        try:
            TableCache.__init__(self,tableName, keys, filter)
        finally:
            if self._ec:
               self._ec.close()
    
    def _get_table_iterator(self):
        return self._ec.__getattr__(self._table_name)
    
    def _get_db_val_4_key(self,entry,key):
        return entry[key]
    
class DaveTableCache(TableCache):
    """
    Uses TM to read loaded model lines
    """
    def __init__(self, tableName, keys, filter={}):
        TableCache.__init__(self,tableName, keys, filter)

    def _get_table_iterator(self):
        return tm.TM.table(self._table_name)
    
    def _get_db_val_4_key(self,entry,key):
        try:
            return  str(entry.getRefI(key))
        except:
            return  str(entry.nget(key))
        return ""

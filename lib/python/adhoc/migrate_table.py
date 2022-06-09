
from AbsTime import AbsTime

def pack_str(val):
    s = val.replace("'",'"')
    return "'"+s+"'"

def pack_val(val):
    if isinstance(val,str):
        return pack_str(val)
    if isinstance(val,bool):
        return "True" if val else "False"
    return str(val)

def pack_row(row):
    ret = ""
    delim= '['
    for v in row:
        ret += delim + pack_val(v)
        delim=','
    return ret+'],'

def matching_row(row, match_row):
    for k in match_row.keys():
        if match_row[k]!=row[k]:
            return False
    return True
            
class MigrateTable:

    def __init__(self, dc, frun, tbl_name, col_names, pk_count):
        self._dc = dc
        self._frun = frun
        self._tbl_name = tbl_name
        self._col_names = col_names
        self._pk_count = pk_count
        self._file = None

    def crt_key(self, row):
        ret = (row[self._col_names[0]],)
        for i in range(1,self._pk_count):
            ret = ret + (row[self._col_names[i]],)
        return ret 

    def crt_row(self,ar):
        row = {}
        for i in range(len(ar)):
            cn = self._col_names[i]
            row[cn] = ar[i]
        return row

    def equal_values(self, r1, r2):
        for i in range(self._pk_count, len(self._col_names)):
            if r1[self._col_names[i]] != r2[self._col_names[i]]:
                return False
        return True

    def load(self, condition):
        self._data = {}
        self._inserted = {}
        self._updated = {}
        self._deleted = {}
        if condition is None:
            condition="1=1"
        for row in self._frun.dbsearch(self._dc,self._tbl_name, condition):
            self._data[self.crt_key(row)] = row

    #def add_row(self,row):
    #    self._data[self.crt_key(row)] = row

    def writeline(self,s):
        self._file.write(s+'\n')

    def write_ar(self,op,ar_name,ar):
        self.writeline("")
        self.writeline(ar_name+' = [')
        for row in ar:
            d = [] 
            for cn in self._col_names:
                d.append(row[cn])
            self.writeline(pack_row(d))
        self.writeline(']')
        self.writeline('')


    def write_orig(self):
        self._file = open('changed_'+self._tbl_name+".py",'wb')
        self.write_ar('D','inserted',self._inserted.values())
        self.write_ar('U','updated',self._updated.values())
        self.write_ar('N','deleted',self._deleted.values())
        self._file.close()

 
    def has_row(self, row):
        k = self.crt_key(row)
        return  (k in self._data)


    def get_row(self, row):
        k = self.crt_key(row)
        if k in self._data:
            return self._data[k].copy()
        return None

    def get_rows(self):
        ret = []    
        for row in self._data.values():
            ret.append(row.copy())
        return ret
    
    def get_matching_rows(self,match_row):
        ret = []
        for row in self._data.values():
            if matching_row(row,match_row):
                ret.append(row.copy())
        return ret

    def put_row(self, ops, row):
        old = self.get_row(row)
        if old is None:
            ops.append(self._frun.createOp(self._tbl_name,'N', row))
            self._inserted[self.crt_key(row)] = row
        elif not self.equal_values(row , old):
            for cn in self._col_names:
                if not cn in row:
                    row[cn] = old[cn]
            ops.append(self._frun.createOp(self._tbl_name,'U', row))
            self._updated[self.crt_key(row)] = old

       
    def del_row(self, ops, row):
        old = self.get_row(row)
        if old is not None:
            ops.append(self._frun.createOp(self._tbl_name,'D', row))
            self._deleted[self.crt_key(row)] = old

    def delete_untouched(self,ops):
        for row in self._data.values():
            k = self.crt_key(row)
            if not (k in self._inserted or k in self._updated or k in self.deleted):
                self.del_row(ops,row)



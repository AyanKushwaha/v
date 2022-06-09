
import sys

_MONTHS = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']

def parse_time(s):
    s = s.strip()
    h = s[0:-3]
    m = s[-2:]
    return int(h)*60+int(m)

def format_time(v):
    return "{:d}:{:02d}".format(v//60,v%60)

def parse_date(s):
    s = s.strip()
    d = int(s[0:2])
    y = int(s[5:9])
    m = _MONTHS.index(s[2:5])+1
    mn = int(s[10:12])
    sc = int(s[13:15])
    return y*100000000+m*1000000+d*10000+mn*100+sc

def format_date(v):
    d = v / 10000
    t = v % 10000
    return "{0:02d}{1}{2:d} {3:02d}:{4:02d}".format(d%100,_MONTHS[(d/100)%100-1],
        d/10000,
        t/100,t%100)

def format_str(s):
    a = s.split('"')
    res = ""
    for x in a:
        res += '"'+x+'"'
    return res

def nice_str(s,lg):
    if lg<2:
        lg = 10
    elif lg>30:
        lg =30
    if len(s)>lg:
        s = s[0:(lg-1)]+'~'
    f = '{:'+str(lg)+'s}'
    return f.format(s)

class RaveEtab:

    _f_name = ""
    _col_typ = []
    _col_nam = []
    _col_lbl = []
    _col_occ_l = []
    _data = []

    def add_col(self, typ, nam, lbl):
        self._col_typ.append(typ)
        self._col_nam.append(nam)
        self._col_lbl.append(lbl)
        if typ=='S':
            lg = -1
        elif typ=='R' or typ=='B':
            lg = 5
        else:
            lg = 10 
        self._col_occ_l.append(lg)

    def del_col(self,ix):
        del self._col_typ[ix]    
        del self._col_nam[ix]
        del self._col_lbl[ix]
        del self._col_occ_l[ix]

    def _parseline(self,r):
        rr= r[0:-1].replace(';',',').split(',')
        res= []
        i=0
        for ix in range(self.col_count()):
            if self._col_typ[ix]=='I':

                if (rr[i].strip().lower()=='void'):
                    res.append(None)
                else:
                    res.append(int(rr[i]))
                i += 1
            elif self._col_typ[ix]=='B':
                if (rr[i].lower()=='void'):
                    res.append(None)
                else:
                    res.append(rr[i].find("true")>=0)
                i += 1
            elif self._col_typ[ix]=='R':
                if (rr[i].strip().lower()=='void'):
                    res.append(None)
                else:
                    res.append(parse_time(rr[i]))
                i += 1
            elif self._col_typ[ix]=='A':
                if (rr[i].strip().lower()=='void'):
                    res.append(None)
                else:
                    res.append(parse_date(rr[i]))
                i += 1
            else:
                rr[i] = rr[i].strip()
                if (rr[i].strip().lower()=='void'):
                    res.append(None)
                    i += 1
                elif rr[i].find('"')!=0:
                    res.append(rr[i])
                    i += 1
                else:
                    s=""
                    while len(s)==0 or s[-1]!='"':
                        ff = rr[i].split('""')
                        if len(s)>0:
                            s+=','
                        s += ff[0]
                        for j in range(1,len(ff)):
                            s += '"'+ff[j]
                        i += 1
                    res.append(s[1:-1])
                lg = 4 if res[ix] is None else len(res[ix])
                if lg>self._col_occ_l[ix]:
                    self._col_occ_l[ix] = lg
        return res
        
    def _readfile(self):
        if self._f_name is None:
            f = sys.stdin
        else:
            f = open(self._f_name,'rb')
        r = f.readline()
        col_count = int(r[0:-1])
        for i in range(col_count):
            r = f.readline()
            a = r[0:-1].replace(';',',').split(',')
            self.add_col(a[0][0], a[0][1:], a[1])
        r = f.readline()
        r = f.readline()
        while len(r)!=0:
            self._data.append(self._parseline(r))                  
            r = f.readline()           
        if not self._f_name is None:
            f.close()

    def save_as_etab(self,name):
        if name is None:
            f = sys.stdout
        elif name.find('.')<0:
            f = open(name+'.etab','wb')
        else:
            f = open(name,'wb')
        f.write(str(self.col_count())+'\n')
        for i in range(self.col_count()):
            s = self._col_typ[i]+self._col_nam[i]
            if len(self._col_lbl[i])>0:
                s += ' "'+self._col_lbl[i]+'"'
            s += ','
            f.write(s+'\n')
        f.write('\n')
        #print "rows: ",len(self._data)
        for row in self._data:
            f.write(self.line_str(row)+'\n')
        if not name is None:
            f.close()

    def save_as_excel(self,name):
        if name is None:
            f = sys.stdout
        elif name.find('.')<0:
            f = open(name+'.csv','wb')
        else:
            f = open(name,'wb')
        s = format_str(self.col_label(0))
        for i in range(1,self.col_count()):
            s += ';'+format_str(self.col_label(i))
        f.write(s+'\n')
        for row in self._data:
            f.write(self.line_excel(row)+'\n')
        if not name is None:
            f.close()

    def save_file(self):
        self.save_as_file(self._f_name)

    def __init__(self,name):
        if name is None:
            self._f_name = None
        #elif name.find('.')<0:
        #    self._f_name = name+'.etab'
        else:
            self._f_name = name
        self._readfile()

    def col_count(self):
        return len(self._col_typ)

    def col_type(self,col_no):
        return self._col_typ[col_no]

    def col_name(self,col_no):
        return self._col_nam[col_no]

    def col_label(self,col_no):
        return self._col_lbl[col_no]

    def row_count(self):
        return len(self._data)

    def row(self,row_no):
        return self._data[row_no]
    
    def col_str(self,v,ix):
        if v[ix] is None:
            return "void"
        elif self.col_type(ix)=='I':
            return str(v[ix])
        elif self.col_type(ix)=='B': 
            return "true" if v[ix] else "false"
        elif self.col_type(ix)=='R': 
            return format_time(v[ix])
        elif self.col_type(ix)=='A':
            return format_date(v[ix])
        else:
            return format_str(v[ix])

    def line_str(self,row):
        if self.col_count()==0:
            return ""
        #if len(row)dd!=15:
        #    sys.stderrprint row
        res = self.col_str(row,0)+','
        for i in range(1,self.col_count()):
            res+= " "+self.col_str(row,i)+','
        return res

    def col_excel(self,v,ix):
        if self.col_type(ix)=='I':
            return str(v[ix])
        elif self.col_type(ix)=='B': 
            return "TRUE" if v[ix] else "FALSE"
        elif self.col_type(ix)=='R': 
            return format_time(v[ix])
        elif self.col_type(ix)=='A':
            return "{}-{}-{}".format(v[ix]//10000,(v[ix]%10000)//199,v[ix]%100)
        else:
            return format_str(v[ix])

    def line_excel(self,row):    
        if self.col_count()==0:
            return ""
        res = self.col_excel(row,0)
        for i in range(1,self.col_count()):
            res += ";"+self.col_excel(row,i)
        return res

    def col_nice(self,v,ix):
        hl = len(self.col_label(ix))
        if hl>10:
            hl=10
        if self.col_type(ix)=='I':
            return "{:10d}".format(v[ix])
        elif self.col_type(ix)=='B': 
            res = "true " if v[ix] else "false"
            if hl>5:
                return ("{:<"+str(hl)+"s}").format(res)
            return res
        elif self.col_type(ix)=='R': 
            res = "{:>5s}".format(format_time(v[ix]))
            if hl>5:
                return ("{:<"+str(hl)+"s}").format(res)
            return res
        elif self.col_type(ix)=='A':
            return "{:04d}-{:02d}-{:02d}".format(v[ix]//10000,(v[ix]%10000)//199,v[ix]%100)
        else:
            lg = self._col_occ_l[ix]
            if lg<hl:
                lg = hl               
            return nice_str(v[ix],lg)

    def hdr_nice(self,ix):
        s = self.col_label(ix)
        lg = self._col_occ_l[ix]
        if len(s)>lg:
            if len(s)>10:
                lg=10
            else:
                lg=len(s)
        return nice_str(s,lg)
 
    def print_nice(self):
        s = self.hdr_nice(0)
        for i in range(1,self.col_count()):
            s += ' '+self.hdr_nice(i)
        print s
        for row in self._data:
            s = self.col_nice(row,0)
            for i in range(1,self.col_count()):
                s += ' '+self.col_nice(row,i)
            print s
        
    def print_tab(self):
        for d in self._data:
            print(d)

            

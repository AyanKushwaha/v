
import RaveObj
import os
import string

END_TERM_OT = [RaveObj.OT_TABLE,RaveObj.OT_MATRIX, RaveObj.OT_ACCUM,RaveObj.OT_CONSTRAINT,RaveObj.OT_RULE,RaveObj.OT_ENUM,RaveObj.OT_ITERATOR,RaveObj.OT_LEVEL]

def is_var(name):
    x = string.punctuation+string.whitespace
    for c in name[1:-1]:
        if c in x and c!='_':
            return False
    return True

class RaveParser:

    _file_count = 0
    _line_count = 0
    _product = '-'

    def __init__(self):
        self.init_parser()
        self._cur = None
        
    def init_parser(self):
        #self._file_count = 0
        self._line_count = 0        

    def set_product(self,p):
        self._product = p.upper()

    def _ends_exp(self,r):
        lg = len(self._exp_end)
        if lg==0 or lg>len(r):
            return False
        if r[-lg:]!=self._exp_end:
            return False
        if lg>1 and len(r)>lg:
            if r[-lg]=='_' or r[-lg].isalnum():
                return False
        self._exp_lvl -= 1
        if self._exp_lvl<1:
            self._exp_end=''
            self.final_obj(self._cur_rf,self._cur,self._code,self._varis, self._param, self._remark)
            self._tbl_phase = 0
            self._varis = None
            self._param = False
            self._remark = None
            self._code = []
        return True
        
    def _parse_token(self):
        self._p_row = self._p_row.lstrip()
        if len(self._p_row)<1:
            return False
        if self._p_row[0]=='%':
            i= self._p_row.find('%',1)
            if i<0:
                raise Exception('missing right %',self._rn,self._p_row)                
            i += 1
        elif self._p_row[0]=='(':
            i = self._p_row.find(')',1)
            if i<0:
                raise Exception('missing ")"',self._rn,self._p_row)
            i += 1
        elif self._p_row[0]=='"':
            i = self._p_row.find('"',1)
            if i<0:
                raise Exception('missing "',self._rn,self._p_row)
            i += 1
        else:            
            i = self._p_row.find(' ')
            j = self._p_row.find('\t')
            if i<0 or (j>=0 and j<i):
                i=j
            j = self._p_row.find('(')
            if i<0 or (j>=0 and j<i):
                i=j
            if i<0:
                i = len(self._p_row)
                while i>0 and self._p_row[i-1].isspace():
                    i -= 1
            if self._ends_exp(self._p_row[0:i]):
                i -= len(self._exp_end)
        x = str(i)+": "+self._p_row
        self._p_tok = self._p_row[0:i]
        self._p_row = self._p_row[i:]

        return True

    def parse_rest(self):
        r = self._p_row
        x = r.strip()
        i = x.find('let')
        if i==0 and (len(x)==3 or x[3].isspace()):
            self._exp_lvl += 1
        i = x.find('parameter')
        if i==0 and (len(x)==9 or x[9].isspace()):
            self._param= True
            x = x[9:].strip()
        i = x.find('remark')
        if i==0 and (len(x)==6 or x[6].isspace()):
            x = x[6:].strip()
            self._remark = x.strip(';,"')
        while True:
            while True:                
                i = r.find('%')
                if self._tbl_phase==1:
                    j = r.find('->')
                    if i== -1 or (j>=0 and j<i):
                        i = j
                elif self._tbl_phase==2:
                    j = r.find(';')
                    if i== -1 or (j>=0 and j<i):
                        i = j
                j = r.find('/*')
                if j<0 or (i>=0 and i<j):
                    break # found an item, or no more comment
                self._ends_exp(r[0:j].strip())
                self._comment=True
                r = r[j+2:]
                j = r.find('*/')
                if j<0:
                    return
                self._comment=False
                r = r[j+2:]
            if i<0:
                self._ends_exp(r[0:-1].strip())
                break
            if r[i]=='%':                
                if i==0 or r[i-1]!='.':
                    m = '.'
                else:
                    j = r.rfind(' ',0,i)+1
                    k = r.rfind('(',0,i)+1
                    j = j if k<j else k
                    m = r[j:i-1]
                r = r[i:]
                i = r.find('%',1)
                if i<0:
                    r = r[1:]
                    continue
                    #self._ends_exp(r[0:-1].strip())
                    #break # illegal; probably found % inside string
                    #raise Exception('missing end %',self._rn,r)
                name = r[0:(i+1)]
                if is_var(name):
                    if self._tbl_phase==2:
                        self._varis.append(name)
                    else:
                        self.add_var_ref(self._cur_rf,self._cur,m,name)
                else:
                    i=0 # just skip the single %
            elif self._tbl_phase>0:
                self._tbl_phase += 1 # 0: no table. 1=before ->. 2=between -> and ; 3= after ;
            r = r[i+1:]
    
    def parse_file(self,path,rf):
        #mod_name = '-'
        self._file_count += 1
        f = open(path+rf.name(),'rb')
        #self._cur_mod=f_name
        self._cur_rf = rf
        self._rn=0
        self._comment=False
        self._exp_end=''
        self._exp_lvl=0
        self._product_ok = True
        self._code = []
        self._cur = None
        self._tbl_phase = 0 # no table
        self._varis = None
        self._param = False
        self._remark = None
        
        #b_module=''
        for row in f:
            self._line_count += 1
            exp = 0
            redef = 0
            glbl = 0
            otyp = RaveObj.OT_UNDEF
            
            self._rn += 1
            self._p_row=row

            if len(self._code)>0 or len(row)>=3:
                self._code.append(row[0:-1])
                
            if len(row)<3:
                continue
            elif self._comment:
                i = row.find('*/')
                if i>=0:
                    self._comment=False
                    self._p_row = row[i+2:]
                    self.parse_rest()
            elif row.strip()[0:2]=='/*':
                self._comment=True
                i = row.find('*/')
                if i>=0:
                    if row.strip()[0:3]=='/*+':
                        rf.add_decor(row[3:i])  
                    self._comment=False
                    self._p_row = row[i+2:]
                    self.parse_rest()
            elif len(self._exp_end)>0:
                self.parse_rest()
            else:
                while self._parse_token():
                    if self._p_tok in RaveObj.OBJ_TNAMES:
                        ot = RaveObj.OBJ_TNAMES.index(self._p_tok)
                    else:
                        ot = RaveObj.OT_UNDEF
                    if self._p_tok=='redefine':
                        redef=1
                        continue
                    elif self._p_tok=='export':
                        exp=1
                        continue
                    elif self._p_tok=='global':
                        glbl=1
                        continue
                    elif self._p_tok=='#if':
                        i = row.find('(')
                        j = row.find(')')
                        if i<0 or j<i:
                            raise Exception('parse error #if 1',rf.name(),self._rn,row)
                        if row[i-7:i].upper() == 'PRODUCT':
                            if row[i+1:j].upper() != self._product:
                                self._exp_end='end'
                                self._exp_lvl=1
                            break
                        else:
                            raise Exception('parse error #if 2',rf.name(),self._rn,row)
                    elif self._p_tok=='end':
                        continue # happens after #if product , if true
                    elif self._p_tok[0] =='(':
                        continue
                    elif RaveObj.category(ot)==RaveObj.OC_MOD:
                        if otyp!=RaveObj.OT_ROOT:
                            otyp = ot
                    elif RaveObj.category(ot)==RaveObj.OC_VAR:
                        otyp = ot                        
                        self._exp_end='end' if ot in END_TERM_OT else ';'
                        if ot == RaveObj.OT_TABLE:
                            self._varis = []
                            self._tbl_phase = 1
                        self._exp_lvl = 1
                    elif RaveObj.category(ot)==RaveObj.OC_MODREF:
                        otyp = ot
                    elif self._p_tok[0]=='%':
                        otyp = RaveObj.OT_VARI
                        name = self._p_tok
                        self._exp_end=';'
                        self._exp_lvl = 1
                        break
                    else:
                        if otyp==RaveObj.OT_ROOT:
                            if self._p_tok != rf.name():
                                raise Exception('module rname error',rf.name(),self._rn,self._p_tok)
                            rf.set_type('root','')
                            #mod_name = self._p_tok
                            break
                        elif otyp==RaveObj.OT_MODULE or otyp==RaveObj.OT_INHERITS:
                            if self._p_tok != rf.name():
                                raise Exception('module iname error',rf.name(),self._rn,self._p_tok)
                            #mod_name = self._p_tok
                            if not self._parse_token():
                                rf.set_type('module','')
                                #mod_name = self._p_tok
                                break
                            if self._p_tok!='inherits':
                                raise Exception('inherits 2 error',rf.name(),self._rn,row)
                            if not self._parse_token():
                                raise Exception('inherits 3 error',rf.name(),self._rn,row)
                            #b_module = self._p_tok
                            rf.set_type('inherits',self._p_tok)
                            otyp = RaveObj.OT_INHERITS
                            name = self._p_tok
                            if name[-1]==';':
                                name = name[0:-1]
                            self.add_mod_ref(rf,otyp,name)
                            break
                        elif otyp == RaveObj.OT_REQUIRE:
                            name = self._p_tok
                            break
                        elif RaveObj.category(otyp)==RaveObj.OC_VAR:
                            name = self._p_tok
                            if name[-1]==';':
                                name = name[0:-1]
                            break
                        elif RaveObj.category(otyp)==RaveObj.OC_MODREF:
                            name = self._p_tok
                            if name[-1]==';':
                                name = name[0:-1]
                            elif name[0] =='"':
                                name = name[1:-1]
                            self.add_mod_ref(rf,otyp,name)
                            #self.add_ref(RaveObj.category(otyp),name,'')
                            self.parse_rest()
                            break
                        else:
                            raise Exception('parse error',rf.name(),self._rn,row)                            
                if RaveObj.category(otyp)==RaveObj.OC_VAR:
                    v = RaveObj.VIS_GLOBAL if glbl>0 else (RaveObj.VIS_EXPORT if exp>0 else RaveObj.VIS_LOCAL)
                    self._cur = RaveObj.RaveObj(otyp,name,rf.name(),self._rn,v)
                    self.add_obj(rf,self._cur)
                    self.parse_rest()            
                elif RaveObj.category(otyp)==RaveObj.OC_MOD:
                    pass
                    #self._cur = RaveObj.RaveObj(mod_name,'',otyp,b_module,self._rn)
                elif (redef+exp)>0:
                    raise Exception('missing variable',rf.name(),self._rn,row)
                else:
                    pass
        f.close()

    def add_obj(self,rf,obj):
        print "add ",obj

    def add_mod_ref(self,rf,otyp,oname):
        print "add_mod_ref",otyp,oname
        
    def add_var_ref(self,rf,var,modref,varref):
        print "add_var_ref ",modref,varref

    def final_obj(self,rf,obj,code,tbl_varis, param, remark):
        print "final_obj",obj
    

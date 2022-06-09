OOBJ_CATS = ['Und','Mod','Var','Ref']

OC_UNDEF = 0
OC_MOD = 1
OC_VAR = 2
OC_MODREF = 3

OBJ_TYPES = ['Undf','Rule','Tabl','Mtrx','Set ','Enum','Accu',     'Grp ','Cstr',      'Itrr', 'Levl', 'Vari','Root','Inhr','Modu','Use ','Impo',      'Requ','Map ','End ','#if']
OBJ_TNAMES = ['-','rule','table','matrix','set','enum','accumulator','group','constraint','iterator','level','-','root','inherits','module','use','import','require','mapping','#if']

OT_UNDEF = 0
OT_RULE = 1
OT_TABLE = 2
OT_MATRIX = 3
OT_SET = 4
OT_ENUM = 5
OT_ACCUM = 6
OT_GROUP = 7
OT_CONSTRAINT = 8
OT_ITERATOR = 9
OT_LEVEL = 10
OT_VARI = 11
OT_ROOT = OT_VARI+1     #12
OT_INHERITS = OT_VARI+2 #13
OT_MODULE = OT_VARI+3   #14
OT_USE = OT_MODULE+1    #15
OT_IMPORT = OT_MODULE+2 #16
OT_REQUIRE = OT_IMPORT+1 #17
OT_MAPPING = OT_IMPORT+2 #18
OT_COUNT = OT_MAPPING+1

TIER_APPL   = 7
TIER_THEME  = 6
TIER_OBJECT = 5
TIER_LEVEL  = 4
TIER_MODEL  = 3
TIER_SYSTEM = 2
TIER_BASE   = 1
TIER_UNDEF  = 0

TIER_TEXTS = [ 'Undef', 'Base', 'System', 'Model', 'Level', 'Object', 'Theme', 'Application']

CARMSYS_MODULES = [
        'alert_server',     'apc_pac',      'apc_rail',     'carmencita',   'fam_optimizer',
        'matador',          'routeinst',    'apc',          'apc_pm',       'buddy_bids',
        'daily_buddy_bids', 'fleet',        'matador_network_model',        'tail',
        'kwdmap','kwdmap_mirador_impl','leave_balance_kwdmap_mirador_impl',
        'leave',            'leave_functions','leave_tables','leave_balance','leave_rules',
        'manpower_mappings', 'training_tables','training_rules','basic','common_rules']

TRG_ROT='rot'
TRG_CCP='ccp'
TRG_CCR='ccr'
TRG_CCT='cct'
TRG_PRE='pre'
TRG_CMP='cmp'
TRG_PTS='pts'

TRG_TEXTS = {
    TRG_ROT: 'BuildAcRotations',
    TRG_CCP: 'Pairing_',
    TRG_CCR: 'Rostering_',
    TRG_CCT: 'Tracking_',
    TRG_PRE: 'PreRostering',
    TRG_CMP: 'Manpower',
    TRG_PTS: 'ParseTest'
    }

TYP_GPC='gpc'
TYP_APC='apc'
TYP_MATADOR='mat'
TYP_URM='urm'

TYP_TEXTS = {
    TYP_GPC: "GPC",
    TYP_APC: "APC",
    TYP_MATADOR: "Matador",
    TYP_URM: "URM"
    }

CREW_CC = 'CC'
CREW_FC = 'FC'

VIS_UNKNOWN = 0
VIS_LOCAL = 1
VIS_EXPORT = 2
VIS_GLOBAL = 3
VIS_TEXTS = ["Unknown", "Local", "Export", "Global"]
VIS_SHORT = ["?", "", "Expo", "Glob" ]    

def category(typ):
    if typ<=OT_UNDEF:
        return OC_UNDEF
    if typ<=OT_VARI:
        return OC_VAR
    if typ<=OT_MODULE:
        return OC_MOD
    if typ<=OT_REQUIRE:
        return OC_MODREF
    return OC_UNDEF

def is_carmsys_module(name):
    return name in CARMSYS_MODULES

def trg_texts(trg_id):
    return TRG_TEXTS[trg_id]

def typ_texts(typ_id):
    return TYP_TEXTS[typ_id]

def modl_hdr(res):
    res.append('f_name')
    res.append('type')
    res.append('module')
    res.append('parent')
    res.append('tier')
    return res
        
def vari_hdr(res):
    #res.append('refs')

    res.append('v_id')
    res.append('v_type')
    res.append('module')
    res.append('v_name')
    res.append('f_name')
    res.append('f_line')
    res.append('visib')
    res.append('param')
    res.append('references')
    return res

def srce_hdr():
    return ['f_name','f_line','v_name','trg_id','trg_count','visib','param','references']

def rel_hdr(res):
    res.append('v_parent')
    res.append('v_child')
    res.append('distance')
    res.append('path')
    res.append('p_height')
    return res
    
class RaveFile:

    _name = ''  # name of the file
    _type = '?' # type (root, inherits, module)
    _parent_name = None
    _parent = ''
    _env_dep = 0
    _children = [] # file children (inherits ...)
    _decor = {}

    def __init__(self,name):
        self._name = name
        self._type='?'
        self._env_dep = 0
        self._trgs = []
        self._objs = []
        self._parent = ''
        self._children = []
        self._decor = {}

    def __repr__(self):
        return self.dsp(2)
        
    def add_child(self,child):
        self._children.append(child)
        child._parent = self

    def add_obj(self,obj):
        self._objs.append(obj)
        #print "obj count: ",len(self._objs)

    def add_decor(self, s):
        i = s.find(' ')
        if i>0:
            k = s[0:i].upper()
            v = s[i+1:].strip()
            self._decor[k] = v

    def put_trg(self,trg):
        if trg not in self._trgs:
            self._trgs.append(trg)

    def set_type(self,typ,parent_name):
        self._type = typ
        self._parent_name = parent_name

    def dsp(self,level):
        if level==2:
            return self.name()+': '+self.type()+' '+self.module()    
        if level==3:
            return self.name()+': '+self.type()+' '+self.module() + ' '+str(len(self._objs))    
        return self.name()

    def print_objs(self,level):
        for o in self._objs:
            print o.dsp(2)
            #if o.name()=='%trip_analysis_costs%':
            #    o.code_dsps()

            
    def name(self):
        return self._name

    def type(self):
        return self._type
    
    def parent_name(self):
        return self._parent_name    

    def module(self):
        if "" == self._parent:
            return self.name()
        return self._parent.module()

    def tier(self):
        if self._parent:
            return self._parent.tier()
        else:
            if 'TIER' in self._decor:
                return int(self._decor['TIER'])
            else:
                return TIER_UNDEF
            
    def tier_desc(self):
        t = self.tier()
        if t==TIER_UNDEF:
            return ""
        return str(t)+": "+TIER_TEXTS[t]
        

    def env_dep(self):
        if "" == self._parent:
            return self._env_dep
        return self.env_dep()

    def get_objs(self):
        return self._objs

    def tbl_modl_fill(self,res,base):
        row = base[:]
        row.append(self.name())
        row.append(self.type())
        row.append(self.module())
        row.append(self.parent_name())
        row.append(self.tier_desc())
        res.append(row)
        
class RaveObj:
    
    _type = OT_UNDEF
    _name = '' 
    _source_name = ''   # table name, or _name if not table 
    #_module = ''        # root file if variable; part of id 
    _file_name = ''     # file with source code 
    _line_no = 0
    _visibility = VIS_UNKNOWN
    _code = []
    _param = False
    _remark = None
    _refs = []
    _orefs = {}
    _badrefs = []
    
    _xrefs = []
    _lvl = 0

    def __init__(self,typ,obj_name,file_name,line_no,visib):
        self._type = typ
        self._name = obj_name
        self._source_name = obj_name
        self._file_name = file_name
        self._line_no = line_no
        self._refs = []
        self._xrefs = []
        self._orefs = {} 
        self._trgs = []
        self._code = []
        self._level = 0
        self._modname = None
        self._visibility = visib
        
    #def __init__(self,module,name,typ,base_module,line_no):
    #    self._module = module
    #    self._name = name
    #    self._source = name
    #    self._type = typ
    #    self._base_module = base_module
    #    self._line_no = line_no
    #    self._refs = []
    #    self._trgs = []
    #    self._code = []

    def clone_table(self,obj_name):
        ret = RaveObj(self._type,self._source_name,self._file_name,self._line_no,self.visibility())
        ret._name = obj_name
        ret._refs = self._refs[:]
        ret._trgs = self._trgs[:]
        ret._code = self._code[:]
        return ret

    def add_ref(self,module,name):
        s = module+'.'+name
        if not s in self._refs:
            self._refs.append(s)

    def add_trg(self,trg,typ,crew):
        self._trgs.append((trg,typ,crew))

    def visibility(self):
        return self._visibility

    def visib_text(self):
        return VIS_TEXTS[self.visibility()]

    def set_code(self,code):
        self._code = code

    def set_remark(self, is_param, remark):
        self._param = is_param
        self._remark = remark
        
    def set_modname(self,name):
        self._modname = name
        #for i in range(len(self._refs)):
        #    k = self._refs[i]
        #    if k.startswith('..'):
        #        self._refs[i] = name+k[1:]
        
    def get_ref_keys(self):
        return self._refs.keys()

    def has_trg(self,trg,typ,crew):
        return (trg,typ,crew) in self._trgs
        
    #def is_leaf(self):
    #    return len(self._refs)==len(self._badrefs)
    
    def name(self):
        return self._name

    def id(self):
        if self.visibility() == VIS_GLOBAL:
            return '$.'+self._name
        return self._modname+'.'+self._name

    def module(self):
        return self._modname

    def otype(self):
        return self._type

    def cat(self):
        return category(self.otype())

    def level(self):
        return self._lvl

    def height(self,h):
        res = 0
        if h>99:
            return 99
        for o in self._xref:
            kand = o.height(h+1)
            if kand>res:
                res = kand
        return res+1
        
    def key(self):
        if self._type==OT_MODULE:
            return self._module
        return self.name()

    def __repr__(self):
        res = self.name()+": "+str(self._line_no)+' '+OBJ_TYPES[self._type]
        return res    

    def is_noref(self):
        return len(self._xrefs)==0 and not self.module().startswith('report') \
               and not self.module().startswith('rules') \
               and not self.module().startswith('crg') \
               and not self.module().startswith('studio')
               
    
    def refs_str(self):
        if self._refs is None or len(self._refs)==0:
            return ''
        ret="refs: "
        delim='['
        for r in self._refs:
            ret += delim+r
            delim=','
        ret += ']'
        return ret

    def xrefs_str(self):
        if self._xrefs is None or len(self._xrefs)==0:
            return ''
        ret="xrefs: "
        delim='['
        for r in self._xrefs:
            ret += delim+r.id()
            delim=','
        ret += ']'
        return ret
        
    def dsp(self,level):
        if level==1:
            return self.__repr__()        
        if level==2:
            s = self.refs_str()
            if len(s)>100:
                s = s[0:100]+'...'
            return self.__repr__()+' '+s #self._source_name+' '+s
        if level==3:
            s = self.xrefs_str()
            if len(s)>100:
                s = s[0:100]+'...'
            return self.__repr__()+' '+s+str(self._param)+str(self._remark)       
        return self.name()

    def add_xref(self,ref):
        self._xrefs.append(ref)

    def adjust_level(self,lv):
        if lv>self._level:
            self._level = lv
            for o in self._xrefs:
                o.adjust_level(lv+1)
    
    def adjust_refs(self,dic):
        lv = 0
        for i in range(len(self._refs)):
            k = self._refs[i]
            if k[0] == '.':
                if self.module() + k[1:] in dic:
                    k = self.module() + k[1:]
                else:
                    k = '$' + k[1:] # try global 
            if k in dic:
                x = dic[k]
                self._orefs[k] = x 
                x.add_xref(self) 
                i = x._level + 1
                if i>lv:
                    lv = i # new level
        self.adjust_level(lv)

    def code_dsps(self):
        if self._code is None or len(self._code)==0:
            print "<No code>"
        else:
            for row in self._code:
                print "        "+row
            
    #def tree_dsp(self,repo,lvl,long_print):
    #    prefix = '  '*(lvl-2)
    #    print prefix+self.name()
    #    for r in self._refs:
    #        if r in repo:
    #            c = repo[r]
    #            if c.level()==lvl:
    #                c.tree_dsp(repo,lvl+1,long_print)
    #            elif long_print:
    #                print prefix+"  ("+r+")"
    #        elif long_print:
    #            print prefix+"  #"+r

    #def xref_dsp(self,prefix,long_print):
    #    print prefix+self.name()
    #    for o in self._xref:
    #        if long_print or o.level() == self.level()-1: 
    #            o.xref_dsp(prefix+"  ",long_print)

    #def _refs_up_dsp(self,height):
    #    for o in self._xref:
    #        o._refs_up_dsp(height-1)
    #    prefix = '  '*height
    #    print prefix+self.name()        

    #def refs_dsp(self,repo):
    #    height = self.height(0)-1
    #    for o in self._xref:
    #        o._refs_up_dsp(height-1)
    #    prefix = '###>'+('  '*height)
    #    prefix = prefix[0:2*height]
    #    print prefix+self.name()
    #    for r in self._refs:
    #        if r in repo:
    #            c = repo[r]
    #            c.tree_dsp(repo,height+3,True)
    #

    def xrefc(self):
        r = len(self._xrefs)
        if r==0 and not self.is_noref(): #probably referenced from outside
            return -1
        return r        
        
    def tbl_vari_fill(self,res,base):
        row = base[:]
        row.append(OBJ_TYPES[self.otype()])
        row.append(self.id())
        row.append(self.module())
        row.append(self.name())
        row.append(self._file_name)
        row.append(self._line_no)
        row.append(VIS_SHORT[self.visibility()])
        if self._param:
            row.append(self._remark)
        else:
            row.append("")
        row.append(self.xrefs_str())
        res.append(row)

    def tbl_srce_fill(self, trg_id, dic):
        src_id = (self._file_name, self._line_no)
        if src_id in dic:
            a = dic[src_id]
            a[3] += ","+trg_id
            a[4] += 1
            if a[7]<0 or self.xrefc()<0:
                a[7] = -1
            else:
                a[7] += self.xrefc()
        else:
            rem = self._remark if self._param else ""
            a = [self._file_name, self._line_no, self.name(),trg_id,1, 
                 VIS_SHORT[self.visibility()], rem, self.xrefc()]
            dic[src_id] = a
                      
    def _tbl_rel_recu(self,res,base,called_id,distance,path):
        row = base[:]
        row.append(self.id())
        row.append(called_id)
        row.append(distance)
        row.append(path)
        row.append(self._level)
        if len(res) >= 1000000:
            if len(res) == 1000000:
                print "limit 1000000 reached for xrefs"
                res.append(row)
            return
        res.append(row)
        if distance>10:
            #print "distance>10", path
            return
        for o in self._xrefs:
            p = '/'+path if len(path)>0 else path
            o._tbl_rel_recu(res,base,called_id,distance+1,self.id()+p)
            
    def tbl_rel_fill(self,res,base):
        if len(self._orefs)==0 and len(self._xrefs)==0:
            row = base[:]
            row.append('-')
            row.append(self.id())
            row.append(0)
            row.append('-')
            row.append(0)
            res.append(row)
        for o in self._xrefs:
            o._tbl_rel_recu(res,base,self.id(),1,'')
            
#def rave_module(module,base_module):
#    return RaveObj(module,'',OT_MODULE,base_module,0)
    
#def rave_vari(module,name,base_module,line_no):
#    return RaveObj(module,name,OT_VARI,base_module,line_no)

#def rave_set(module,name,base_module,line_no):
#    return RaveObj(module,name,OT_SET,base_module,line_no)
    
#def rave_rule(module,name,base_module,line_no):
#    return RaveObj(module,name,OT_RULE,base_module,line_no)

#def rave_constraint(module,name,base_module,line_no):
#    return RaveObj(module,name,OT_CONSTRAINT,base_module,line_no)

#def rave_accu(module,name,base_module,line_no):
#    return RaveObj(module,name,OT_ACCUM,base_module,line_no)

#def rave_group(module,name,base_module,line_no):
#    return RaveObj(module,name,OT_GROUP,base_module,line_no)

#def rave_import(module,name,is_imp):
#    return RaveObj(module,name,OT_IMPORT,'<imp>' if is_imp else '<use>',0)


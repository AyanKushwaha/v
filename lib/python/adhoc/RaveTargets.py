
import os
import string
import RaveParser
import RaveObj

TRG_ROT=RaveObj.TRG_ROT
TRG_CCP=RaveObj.TRG_CCP
TRG_CCR=RaveObj.TRG_CCR
TRG_CCT=RaveObj.TRG_CCT
TRG_PRE=RaveObj.TRG_PRE
TRG_CMP=RaveObj.TRG_CMP
TRG_PTS=RaveObj.TRG_PTS

TYP_GPC=RaveObj.TYP_GPC
TYP_APC=RaveObj.TYP_APC
TYP_MATADOR=RaveObj.TYP_MATADOR
TYP_URM=RaveObj.TYP_URM

CREW_CC = RaveObj.CREW_CC
CREW_FC = RaveObj.CREW_FC

def modl_hdr():
    h = ['trg_id','trg_type','trg_trg','trg_crew']
    return RaveObj.modl_hdr(h) 

def vari_hdr():
    h = ['trg_id','trg_type','trg_trg','trg_crew']
    return RaveObj.vari_hdr(h) 

def srce_hdr():
    return RaveObj.srce_hdr()

def rel_hdr():
    h = ['trg_id']
    return RaveObj.rel_hdr(h)

class RaveTarget(RaveParser.RaveParser):

    def __init__(self,trg,typ,crew):
        self.reset()
        self._trg = trg
        self._typ = typ
        self._crew = crew
        self.set_product(typ)

    def reset(self):
        self._file_count = 0
        self._line_count = 0
        self._cur_obj = None
        self._mod_objs = {}
        self._files = {}
        self._work = []
        self._workread=0
        
    def trg(self):
        return self._trg

    def typ(self):
        return self._typ

    def crew(self):
        return self._crew

    def out_file(self):
        return RaveObj.trg_texts(self.trg())+self._crew

    def __str__(self):
        return self.typ()+' for '+self.out_file()

    def __repr__(self):
        return self._typ+'+'+self._trg+'+'+self._crew

    def parse_target(self,debug):
        do_count=0
        o_count=0
        self.reset()
        self.init_parser()
        fn = self.out_file()
        rf = RaveObj.RaveFile(fn)
        # open the compiler source file for the target, and see what modules to start with
        # This means we know filenames of subclassed modules. During parsing we will find basic modules, and parent modules
        # not yet known, and add them to work array, files to handle.
        self.parse_file('../../../crc/source/',rf)        
        while self._workread < len(self._work):
            rf = self._work[self._workread]
            self._workread += 1
            if debug>2:
                print ("--- from "+rf.name())
            # parse the file
            self.parse_file('../../../crc/modules/',rf)
            if debug>2:
                print "parsedfile ",rf.name(),self._workread,len(self._work)
            fname = rf.parent_name()
            # if a subclassed module, check that parent is accounted for
            if fname != '' and not fname in RaveObj.CARMSYS_MODULES and not fname in self._files:
                ref_rf = RaveObj.RaveFile(rf.parent_name())
                self._work.append(ref_rf)
                self._files[ref_rf.name()] = ref_rf
        for rf in self._work: # done in right order: botton up.
            for o in rf.get_objs():
                o.set_modname(rf.module()) # recursive up; all files inheriting have same module name
                m = o.id()
                if m in self._mod_objs:
                    if debug>=3:
                        print "discarding ",m # it's defined in the subclass
                    do_count += 1
                else:
                    self._mod_objs[m] = o # here are the real methods included for the target
                    o_count += 1
            if debug>=2:
                print "file ",rf.name(),", objs/discarded",o_count,do_count
                o_count=0
                do_count=0
        for o in self._mod_objs.values():
            o.adjust_refs(self._mod_objs)
         
    def add_mod_ref(self,rf,o_typ,fname):
        """ callback - used when "import xxx" found etc """
        #print self._files
        if fname in self._files:
            ref_rf = self._files[fname]
        elif fname in RaveObj.CARMSYS_MODULES:
            return
        else:
            ref_rf = RaveObj.RaveFile(fname)
            self._work.append(ref_rf)
            self._files[ref_rf.name()] = ref_rf
        if o_typ==RaveObj.OT_INHERITS:
            ref_rf.add_child(rf)

    def add_obj(self,rf,obj):
        #obj.set_trg(self._trg,self._typ,self._crew)
        #rf.add_obj(obj)
        self._cur_obj = obj

    def final_obj(self,rf,obj,code,tbl_varis, param, remark):
        if not obj is None:
            obj.set_code(code)
            obj.set_remark(param, remark)
            if tbl_varis is None:
                rf.add_obj(obj)
            elif len(tbl_varis) == 0:
                raise Exception('useless table ',rf.name(),self._rn,obj.name())
            else:
                for nm in tbl_varis:
                    o = obj.clone_table(nm)
                    rf.add_obj(o)
                    

    def add_var_ref(self,rf,var,modref,varref):
        var.add_ref(modref,varref)

    def dsp_type_count(self, objs):
        ar = [0] * RaveObj.OT_COUNT
        for o in objs:
            ar[o.otype()] += 1
        for i in range(len(ar)):
            if ar[i] !=0:
                print RaveObj.OBJ_TYPES[i], ar[i]

    def unrefs_count(self, objs):
        cnt=0
        for o in objs:
            if o.is_noref():
                cnt += 1
        print "unref objs: ",cnt

    def show_statistics(self,debug):
        print "=== statistics ",str(self),"==="
        print "read ",self._file_count
        print "rows ",self._line_count
        print "res  ",len(self._work)
        self.unrefs_count(self._mod_objs.values())
        self.dsp_type_count(self._mod_objs.values())

    def show_modules(self,debug):
        print "=== modules ",str(self),"==="
        war = []
        for w in self._work:
            war.append(w.name())
        war.sort()
        for fn in war:
            f = self._files[fn]
            if debug==3 or fn.startswith('analysis'):
                print "--- "+f.dsp(2)+" ---"
                f.print_objs(2)
                print "--------------------"
            else: 
                print f.dsp(3)

    def show_file(self, debug):
        print "==== file ====="    

    def tbl_modl_fill(self,res):
        trg_row = [repr(self),self.typ(),self.trg(),self.crew()]
        print "trg tbl fill",len(self._mod_objs.values())
        for w in self._work:
            w.tbl_modl_fill(res,trg_row)     
        
    def tbl_vari_fill(self, res):
        trg_row = [repr(self),self.typ(),self.trg(),self.crew()]
        print "trg tbl fill",len(self._mod_objs.values())
        for o in self._mod_objs.values():
            o.tbl_vari_fill(res,trg_row)

    def tbl_srce_fill(self,dic):
        for o in self._mod_objs.values():
            o.tbl_srce_fill(repr(self), dic)

    def tbl_rel_fill(self,res):
        trg_row = [repr(self)]
        for o in self._mod_objs.values():
            o.tbl_rel_fill(res,trg_row)

    def module_objs(self):
        ar = []
        for o in self._mod_objs.values():
            k = (o.module(),o.otype(),o.name(),o )
            ar.append(k)
        ar.sort()
        return ar

    def report_objs(self, level):
        ar = self.module_objs()
        mod_last = ""
        obj_count=0
        tot_count=0
        mod_count=0
        for m, t, n, o in ar:
            if m!=mod_last and m!="":
                print "===== module: ",mod_last,":", obj_count
                obj_count=0
                mod_count +=1
            if level>0:
                print o.dsp(level)
            mod_last = m
            obj_count += 1
            tot_count += 1
        print mod_last,":", obj_count
        mod_count += 1
        print "tot:", mod_count, tot_count

    def report_objs_count(self):
        self.report_objs(0)

    def report_objs_repr(self):
        self.report_objs(1)

        
ALL = [
    RaveTarget(TRG_ROT,TYP_GPC,''),
    RaveTarget(TRG_CCP,TYP_GPC,CREW_FC),
    RaveTarget(TRG_CCP,TYP_APC,CREW_FC),
    RaveTarget(TRG_CCP,TYP_GPC,CREW_CC),
    RaveTarget(TRG_CCP,TYP_APC,CREW_CC),
    RaveTarget(TRG_CCR,TYP_GPC,CREW_FC),
    RaveTarget(TRG_CCR,TYP_MATADOR,CREW_FC),
    RaveTarget(TRG_CCR,TYP_GPC,CREW_CC),
    RaveTarget(TRG_CCR,TYP_MATADOR,CREW_CC),
    RaveTarget(TRG_CCT,TYP_GPC,CREW_FC),
    RaveTarget(TRG_CCT,TYP_GPC,CREW_CC),
    RaveTarget(TRG_PRE,TYP_GPC,''),
    RaveTarget(TRG_CMP,TYP_URM,'')
    ]

PARSE_TEST = [
    RaveTarget(TRG_PTS,TYP_GPC,''),
    ]

def p():
    t = RaveTarget(TRG_PRE,TYP_GPC,'')
    t.parse_target()
    t.show_statistics()
    t.show_modules()

def p0():
    t = RaveTarget(TRG_ROT,TYP_GPC,'')
    t.parse_target()
    t.show_statistics()
    t.show_modules()

def a():
    for t in ALL:
        t.parse_target()
    for t in ALL:
        t.show_statistics()
        

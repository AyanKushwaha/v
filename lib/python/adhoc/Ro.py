
import RaveObj
import RaveTargets
import csv

RO_LIMIT=1000

PATH_IN  = "../../../crc/"
PATH_OUT = "../../../current_carmtmp/crc/"

class Ro:

    _fvaris = {}
    _mvaris = {}

    # status
    # Ro.parse_pts() is a good debug data set with a few 100 variables of different kinds,
    # including 3 redines in calendar_cct.
    # The files are now parsed, and vital information gathered including
    # - file name and row
    # - variable module, name, type (also by tables), visibility
    # References variables, source code are stored, but not very much tested.
    #
    # Used Rave Code is RaveObj, RaveTargets and RaveParse.
    #
    # Next steps:
    # - after all files in a target are collected, go through all variable references;
    #   look them up in the target specific list, and update object references and state in the tuple
    #    (change from INIT to either miss, syst or okey. For each match, also update xref =
    #   all users of the called variable.
    # - Create a var-ref table with
    #   targetid, parent, child, steps, path, level
    #   all children witand then using xref info.
    #   vars with no users are shown as parent='', steps=0,level =0
    #   level is 0 when there are no children, 1 when all children have level 0,
    #   2 when highest child level is 1 etc.
    #
    
    def _parse(self,trgs,debug):
        self._targets = trgs
        for trg in self._targets:
            trg.parse_target(debug)
            trg.show_statistics(debug)
            if debug>0:
                trg.show_modules(debug)

        if debug>0:
            print RaveTargets.vari_hdr()
            i = 0        
            for row in self._tbl_vari():
                print row
                i += 1
                if i>RO_LIMIT:
                    print "limit at",i
                    break
        if debug>0:
            print RaveTargets.rel_hdr()
            i = 0
            for row in self._tbl_rel():
                print row
                i += 1
                if i>RO_LIMIT:
                    print "limit at",i
                    break
                
    def show_modules(self, trgs):
        for trg in trgs:
            trg.show_modules(0)

    def show_objects(self, trgs):
        for trg in trgs:
            trg.report_objs(3)

    def _tbl_modl(self):
        res = []
        #print "modl",len(self._targets)
        for trg in self._targets:
            trg.tbl_modl_fill(res)
        return res
    
    def _tbl_vari(self):
        res = []
        #print "vari",len(self._targets)
        for trg in self._targets:
            trg.tbl_vari_fill(res)
        return res

    def _tbl_srce(self):
        dic = {}
        for trg in self._targets:
            trg.tbl_srce_fill(dic)
        return dic.values()

    def _tbl_rel(self):
        res = []
        for trg in self._targets:
            trg.tbl_rel_fill(res)
        return res

    #def target(self,trg_id,typ,crew):
    #    for trg in self.targets:
    #        if trg.trg() == trg_id and trg.typ() == typ and trg.crew() == crew:
    #            return trg
    #    return None

    def parse_file(self,trg,fn,debug):
        self._targets = [trg]
        rf = RaveObj.RaveFile(fn)
        trg.parse_file(PATH_IN+'modules/',rf)
        for o in trg._mod_objs.values():
            o.adjust_refs(trg._mod_objs)
        trg.report_objs(3)

        #print rf.dsp(3)
        #print rf.print_objs(2)
        #print rf.print_objs(3)

def parse_all():
    r = Ro()
    r._parse(RaveTargets.ALL,0)

def parse_pts():
    r = Ro()
    r._parse(RaveTargets.PARSE_TEST,3)

def objects_pts():
    r = Ro()
    r._parse(RaveTargets.PARSE_TEST,0)
    r.show_objects(RaveTargets.PARSE_TEST)
    
def parse_test(trg_no):
    r = Ro()
    trg = RaveTargets.ALL[trg_no]
    r._parse([trg],2)

def parse_abs():
    r = Ro()
    trg = RaveTargets.ALL[7]
    r.parse_file(trg,"absence",3)
    

def parse_cal():
    r = Ro()
    trg = RaveTargets.ALL[7]
    r.parse_file(trg,"calendar",3)

def write_modl():
    r = Ro()
    r._parse(RaveTargets.ALL,0)
    f = PATH_OUT+'modl.csv';
    with open(f,'wb') as csvfile:
        wrt = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        wrt.writerow(RaveTargets.modl_hdr())
        for row in r._tbl_modl():
            wrt.writerow(row)
    print "Modules written to "+f
        
def write_vari():
    r = Ro()
    r._parse(RaveTargets.ALL,0)
    f = PATH_OUT+'vari.csv';
    with open(f,'wb') as csvfile:
        wrt = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        wrt.writerow(RaveTargets.vari_hdr())
        for row in r._tbl_vari():
            wrt.writerow(row)
    print "Variables written to "+f
    
def write_srce():
    r = Ro()
    r._parse(RaveTargets.ALL,0)
    f = PATH_OUT+'srce.csv';
    with open(f,'wb') as csvfile:
        wrt = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        wrt.writerow(RaveTargets.srce_hdr())
        for row in r._tbl_srce():
            wrt.writerow(row)
    print "Sourcecode written to "+f
                         
    

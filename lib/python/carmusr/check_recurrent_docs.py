#####

##
#####
__version__ = "$Revision$"

"""
File for setting validto dates for documents based on crew training logs
@date: 29May2008
@author: Per Groenberg
@org Jeppesen
"""
import re
from utils.dave import EC
import AbsTime
import tm
import carmensystems.rave.api as R
import utils.table_cache as C



class CheckRecurrent:
    def __init__(self):
        self._crew_emp_cache = C.DaveTableCache('crew_employment',['crew'], {'region':re.compile(r'SKN')})
        self._check_map = {'PC':self._check_PC,
                           'OPC':self._check_OPC,
                           'PGT':self._check_PGT,
                           'CRM':self._check_NORMAL,
                           'LC':self._check_NORMAL,
                           'REC':self._check_NORMAL,
                           'RECSKN':self._check_NORMAL,
                           }
        self._error_validto = AbsTime.AbsTime('01Jan2000 00:00')
        
    def check(self, doc='', doc_list=[],log_list=[]):
        doc_list.sort(cmp=CheckRecurrent._sort_validto)
        log_list.sort(cmp=CheckRecurrent._sort_tim)
        try:
            return self._check_map[doc](doc_list, log_list)
        except KeyError:
            raise Exception("No check implemeted for document %s"%doc)

    def _check_PGT(self, doc_list=[], log_list=[]):
        for doc in doc_list:
            logs = []
            skn_logs = []
            for log in log_list:
                if self._crew_is_norwegian_at_time(log.crew, AbsTime.AbsTime(log.tim)):
                    skn_logs.append(log)
                else:
                    logs.append(log)
            if doc.doc.subtype == 'PGTSKN':
                self._check_doc_vs_logs(doc, skn_logs)
            else:
                self._check_doc_vs_logs(doc, logs)
                
        if len(doc_list)>1:
            for doc1 in doc_list:
                for doc2 in doc_list:
                    if doc1._id == doc2._id:
                        continue
                    elif doc1.validto > doc2.validfrom and \
                             doc1.validfrom < doc2.validto:
                        print "Crew %s has two PGT's overlappings\n%s\n%s"%\
                              (str(doc1.crew.id),str(doc1.doc.subtype),str(doc2.doc.subtype))
                        return []
                    
        return []
    
    def _check_PC(self, doc_list=[], log_list=[]):
        
        for doc in doc_list:
            logs = []
            if 'A4' in doc.doc.subtype.upper():
                logs = self._get_logs_for_acqual(log_list, 'A4')
            elif 'A5' in doc.doc.subtype.upper():
                logs = self._get_logs_for_acqual(log_list, 'A5')
            elif 'A3' in doc.doc.subtype.upper():
                logs = self._get_logs_for_acqual(log_list, 'A3')
            else:
                logs = log_list
            self._check_doc_vs_logs(doc, logs)
            
        return []
    
    def _check_OPC(self, doc_list=[], log_list=[]):
        for doc in doc_list:    
            logs = []
            if 'A3' in doc.doc.subtype.upper() or 'A4' in doc.doc.subtype.upper() or 'A5' in doc.doc.subtype.upper():
                logs += self._get_logs_for_acqual(log_list, 'A4')
                logs += self._get_logs_for_acqual(log_list, 'A5')
                logs += self._get_logs_for_acqual(log_list, 'A3')
                # PCA3 gives both OPCA3 and OPCA4
            else:
                logs = log_list
            
            
            self._check_opc_doc_vs_log(doc, logs)
        return []
    
    def _check_NORMAL(self, doc_list=[], log_list=[]):
        logs = log_list
        for doc in doc_list:
            self._check_doc_vs_logs(doc, logs) 
        
        return []

    def _check_doc_vs_logs(self, doc, logs):
##         doc_validto_year_start = AbsTime.AbsTime(doc.validto.split()[0],1,1,0,0)
##         if doc_validto_year_start != doc.validto:
##             check_time = max(doc_validto_year_start,
##                              doc.validto.addmonths(-3,AbsTime.PREV_VALID_DAY))
##         else:
##             check_time = doc.validto.addmonths(-3,AbsTime.PREV_VALID_DAY)
        if not logs:
            print "No recurrent activity found for doc:\n%s valid to %s\n"%\
                  (str(doc.doc.subtype),str(doc.validto))
            doc.validto = self._error_validto
            return
        prolong = tm.TM.crew_recurrent_set[(doc.doc.subtype,AbsTime.AbsTime('1jan1986'))].validity
##         for log in logs:
##             if log.tim >= check_time and log.tim <= doc.validto:
##                 print "Log:\n%s at %s\nprolongs doc:\n%s validto %s with %d months \n"%\
##                       (str(log.typ)+':'+str(log.code),str(log.tim),
##                        str(doc.doc.subtype),str(doc.validto),prolong)
##                 doc.validto = doc.validto.addmonths(prolong, AbsTime.PREV_VALID_DAY)
##                 break
##         else:
        logs.sort(CheckRecurrent._sort_tim)
        last_valid_log = logs[-1]
##         if doc.validto.split()[1] == 1 and doc.validto.split()[2] == 1:
##             delta_months = prolong + 12
##         else:
##             delta_months = prolong
        new_valid_to = AbsTime.AbsTime(int(last_valid_log.tim.split()[0]),
                                       doc.validto.split()[1],
                                       doc.validto.split()[2],
                                       0,0)
        new_valid_to = new_valid_to.addmonths(prolong, AbsTime.PREV_VALID_DAY)

        if new_valid_to.addmonths(-prolong, AbsTime.PREV_VALID_DAY) < last_valid_log.tim:
            new_valid_to = new_valid_to.addmonths(prolong, AbsTime.PREV_VALID_DAY)
        print "Log:\n%s at %s\nwill set new valid to for doc:\n%s valid to %s\nto:\n%s"%\
              (str(last_valid_log.typ)+':'+str(last_valid_log.code),
               str(last_valid_log.tim),str(doc.doc.subtype),str(doc.validto),str(new_valid_to))
        doc.validto = new_valid_to
            
    def _check_opc_doc_vs_log(self, doc, logs):
        # special handling of OPC
        global crew_doc_cache

        
        
        doc_validto_year_start = AbsTime.AbsTime(doc.validto.split()[0],1,1,0,0)
        check_time = max(doc_validto_year_start,
                         doc.validto.addmonths(-3,AbsTime.PREV_VALID_DAY))
        
        if not logs:
            print "No recurrent activity found for doc:\n%s valid to %s\n"%\
                  (str(doc.doc.subtype),str(doc.validto))
            doc.validto = self._error_validto
            return
        
        pc_docs = crew_doc_cache.get(str(doc.getRefI('crew')),
                                     filter={'doc':re.compile(r'REC\+%s'%doc.doc.subtype.replace("O",""))})

        
        new_opc_date = AbsTime.AbsTime(doc.validto).addmonths(-60,AbsTime.PREV_VALID_DAY)
        logs.sort(CheckRecurrent._sort_tim)
        last_valid_log = logs[-1]


        while new_opc_date <= last_valid_log.tim or \
                  last_valid_log.tim > max(AbsTime.AbsTime(new_opc_date.split()[0],1,1,0,0),
                                           new_opc_date.addmonths(-3,AbsTime.PREV_VALID_DAY)):
            new_opc_date = new_opc_date.addmonths(6, AbsTime.PREV_VALID_DAY)
            print "new_opc_date", new_opc_date
        # Check for 1jan issues etc.
        if new_opc_date.addmonths(-6, AbsTime.PREV_VALID_DAY) < last_valid_log.tim:
            new_opc_date = new_opc_date.addmonths(6, AbsTime.PREV_VALID_DAY)
            print "new_opc_date", new_opc_date
        for pc_doc in pc_docs:
            if new_opc_date == pc_doc.validto:
                print 'New OPC validto %s is covered\nby PC validto %s'%(new_opc_date, pc_doc.validto)
                new_opc_date = new_opc_date.addmonths(6,AbsTime.PREV_VALID_DAY)
        print "Log:\n%s at %s\nwill set new valid to for doc:\n%s valid to %s\nto:\n%s"%\
              (str(last_valid_log.typ)+':'+str(last_valid_log.code),
               str(last_valid_log.tim),str(doc.doc.subtype),str(doc.validto),str(new_opc_date))
        doc.validto = new_opc_date
        
    def _crew_is_norwegian_at_time(self, crew_id, time):
        skn_emp_list = self._crew_emp_cache.get(crew_id, default=[])
        for skn_emp in skn_emp_list:
            if skn_emp.validfrom <= time and skn_emp.validto >= time:
                return True
        return False
    
    def _get_logs_by_code(self, log_list=[],code=""):
        return [log for log in log_list if log.code.upper() == code.upper()]
        
    def _get_logs_for_acqual(self, log_list=[], code=""):
        return [log for log in log_list if \
                (R.eval('leg.%%ac_qual_map%%("%s")'%log.code))[0].upper()  == code.upper()]

    @staticmethod
    def _sort_validto(first, second):
        return cmp(first.validto,second.validto)
    
    @staticmethod
    def _sort_tim(first, second):
        return cmp(first.tim,second.tim)

# "globals"
global crew_doc_cache
crew_doc_cache = None
training_log_cache = None

def check_recurrent_documents():
    """
    Creates a checker object, a list of documents to check
    and two tablecaches, crew_documents and crew_training_log
    Then loops through crew and documents and for each documents sends the lists of crew_documents and
    training actvities to the checker object
    """
    checker = CheckRecurrent()
    # Documents and filter expressions
    documents = {'PC'    :{'doc':re.compile(r'REC\+PC.*') , 'typ':re.compile(r'PC')},
                 'OPC'   :{'doc':re.compile(r'REC\+OPC.*'), 'typ':re.compile(r'.*PC')},
                 'PGT'   :{'doc':re.compile(r'REC\+PGT.*'), 'typ':re.compile(r'SAFETY RECURR/PGT')},
                 'CRM'   :{'doc':re.compile(r'REC\+CRM')  , 'typ':re.compile(r'CRM')},
                 'LC'    :{'doc':re.compile(r'REC\+LC')   , 'typ':re.compile(r'LINE CHECK')},
                 'REC'   :{'doc':re.compile(r'REC\+REC\b'), 'typ':re.compile(r'SAFETY RECURR/PGT')},
                 'RECSKN':{'doc':re.compile(r'REC\+RECSKN'),'typ':re.compile(r'SAFETY RECURR BRA CC')},
                 }
    # load = tm.TM.loadTable('crew_document')
    global crew_doc_cache
    crew_doc_cache = C.DaveTableCache('crew_document',['crew'], {'doc':re.compile(r'REC\+.*')})
    
    print 'docs', len(crew_doc_cache)
    training_log_cache = C.ECTableCache('crew_training_log',['crew'])
    print 'logs', len(training_log_cache)
    crew_need_checking = []
    for crew in tm.TM.crew:
        if crew.id not in ('18970'):
            continue
        print '################# CREW %s ####################'%crew.id 
        try:
            for document in documents:
                print "-----------DOCUMENT %s ---------------"%document
                doc_list = crew_doc_cache.get(crew.id,
                                              filter={'doc':documents[document]['doc']},
                                              default=[])
                if not doc_list:
                    continue
                training_log = training_log_cache.get(crew.id,
                                                      filter={'typ':documents[document]['typ']},
                                                      default=[])
                
                result = checker.check(document,doc_list, training_log)
                             
                    
        except Exception, err:
            print err
            pass
        
## Commented out due, old code from somewhere. Didn't want to remove if yet
## maybe it will be needed 

## # Fix docs for SKN ======================================================={{{1

## # fix skn doc 1 ----------------------------------------------------------{{{2

## def fix_skn_docs():
##     from tm import TM
##     import carmensystems.rave.api as R
##     import AbsTime

##     tim = AbsTime.AbsTime("1Jan1986 00:00")

##     crewList, = R.eval("sp_crew",
##                        R.foreach(R.iter('iterators.roster_set',
##                                         where='fundamental.%is_roster%'),
##                                  'training.%switch_pgt_to_pgtskn%',
##                                  'crew.%id%'))


##     print "crew: ", len(crewList)
##     pgt_doc = TM.crew_document_set[("REC","PGT")]
##     pgtskn_doc = TM.crew_document_set[("REC","PGTSKN")]
##     for (ix, pgt_switch, crewid) in crewList:
##         #print crewid, pgt_req, pgt_reg, pgtskn_req, pgtskn_reg
##         #if (pgtskn_req and not pgtskn_reg and pgt_reg and not pgt_req):
##         if pgt_switch:
##             crew = TM.crew[(crewid,)]
##             #print crewid, pgt_req, pgt_reg, pgtskn_req, pgtskn_reg
##             old_doc = TM.crew_document[(crew,
##                                         pgt_doc,
##                                         tim)]
##             new_doc = TM.crew_document.create((crew,
##                                                pgtskn_doc,
##                                                tim))
##             new_doc.validto = old_doc.validto
##             #print crewid
##             #print old_doc
##             #print new_doc
##             old_doc.remove()
##     Cui.CuiReloadTable('crew_document', 1)
    
## # fix skn doc 2 ----------------------------------------------------------{{{2

## def fix_skn_docs2():
##     from tm import TM
##     import carmensystems.rave.api as R
##     import AbsTime

##     tim = AbsTime.AbsTime("1Jan1986 00:00")

##     crewList, = R.eval("sp_crew",
##                        R.foreach(R.iter('iterators.roster_set',
##                                         where='fundamental.%is_roster%'),
##                                  'training.%create_opc_from_pc%',
##                                  'training.%new_opc_date%',
##                                  'crew.%id%'))

##     print "crew: ", len(crewList)
##     pc_doc = TM.crew_document_set[("REC","PC")]
##     opc_doc = TM.crew_document_set[("REC","OPC")]
##     for (ix, create_opc, opc_date, crewid) in crewList:
##         #print crewid, pgt_req, pgt_reg, pgtskn_req, pgtskn_reg
##         #if (pgtskn_req and not pgtskn_reg and pgt_reg and not pgt_req):
##         if create_opc:
##             crew = TM.crew[(crewid,)]
##             #print crewid, pgt_req, pgt_reg, pgtskn_req, pgtskn_reg
##             old_doc = TM.crew_document[(crew,
##                                        pc_doc,
##                                        tim)]
##             new_doc = TM.crew_document.create((crew,
##                                                opc_doc,
##                                                tim))
##             new_doc.validto = opc_date
##             acq = old_doc.ac_qual
##             if acq == "37":
##                 opc_acq = "38"
##             else:
##                 opc_acq = "37"
##             new_doc.ac_qual = opc_acq
            
##             #print crewid
##             #print pc_doc
##             #print new_doc
##             #old_doc.remove()
##     Cui.CuiReloadTable('crew_document', 1)

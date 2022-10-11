from AbsTime import AbsTime
import re

import adhoc.fixrunner as fixrunner

__version__ = '2022_03_1_a'

# Historical data to be considered upto 5 years from now
valid_from = int(AbsTime("01Jan2017"))

PC, _pc, _pc_, OPC, _opc, _opc_ = "PC", "_pc", "_pc_", "OPC", "_opc", "_opc_"
LPC, _lpc, _lpc_, OTS, _ots, _ots_ = "LPC", "_lpc", "_lpc_", "OTS", "_ots", "_ots_"
REC = "REC"

SIM_ACT = {PC: LPC, OPC: OTS}


class PcOpcFixer(object):
    def __init__(self, dc):
        self.dc = dc
        self.link_crews = self.get_link_crews()

    def get_link_crews(self):
        link_contract_types = []
        link_crews = []
        for row in fixrunner.dbsearch(self.dc, 'crew_contract_set', "agmtgroup IN ('SVS_FD_AG', 'SV_CC_AG')"):
            link_contract_types.append(row['id'])
        for row in fixrunner.dbsearch(self.dc, 'crew_contract', "contract IN %s" % str(tuple(link_contract_types))):
            link_crews.append(row['crew'])
        return set(link_crews)

        
    def pc_lpc_replace(self, pc_lpc, string):
        return re.sub(r"\b{}\b".format(pc_lpc), SIM_ACT[pc_lpc], string)
    
    def crew_is_link(self, crew):
        crew_is_link = crew in self.link_crews
        return crew in self.link_crews

    def get_ops_for_activity_group(self):
        print "Entering get_ops_for_activity_group"
        # activity_group table update
        ops = []
        needs_update = False
        for row in fixrunner.dbsearch(self.dc, 'activity_group', "id IN ('{}', '{}')".format(PC, OPC)):
            if row['id'] not in (OPC,):
                ops.append(fixrunner.createOp('activity_group', 'D',
                                              {'id': row['id'],
                                              }))
            needs_update = True
        if needs_update:
            for row in [PC, OPC]:
                ops.append(fixrunner.createOp('activity_group', 'N',
                                                {'id': SIM_ACT[row],
                                                 'cat':REC,
                                                 'si': "{} simulator".format(SIM_ACT[row]),
                                                }))
        return ops
    
    def get_ops_for_activity_group_period(self):
        print "Entering get_ops_for_activity_group_period"
        # activity_group_period table update
        needs_update = False
        ops = []
        activity_group_period = []
        for row in fixrunner.dbsearch(self.dc, 'activity_group_period', "id IN ('{}', '{}')".format(PC, OPC)):
            if row['id'] not in (OPC,):
                ops.append(fixrunner.createOp('activity_group_period', 'D',
                                             {'id': row['id'],
                                             }))
            activity_group_period.append(row)
            needs_update = True
        if needs_update:
            for row in activity_group_period:
                row['id'] = SIM_ACT[row['id']]
                if row['si'].startswith(PC):
                    row['si'] = row['si'].replace(PC, LPC)
                else:
                    row['si'] = row['si'].replace(OPC, OTS)
                ops.append(fixrunner.createOp('activity_group_period', 'N', row))
        return ops
    
    def get_ops_for_activity_set(self):
        print "Entering get_ops_for_activity_set"
        ops = []
        # activity_set table update
        row_ix = 0
        for row in fixrunner.dbsearch(self.dc, 'activity_set', "grp IN ('{}', '{}')".format(PC, OPC)):
            row_ix += 1
            print "activity_set: row #%s: %s" % (row_ix, str(row))
            row['si'] = row['si'].replace(OPC, OTS)
            row['si'] = row['si'].replace(PC, LPC)
            if row['grp'] in (OPC,):
                action = 'N'
            else:
                action = 'U'
                # create new copy, keep old one as well for link crew
            ops.append(fixrunner.createOp('activity_set', action,
                                            {'id': row['id'],
                                             'grp': SIM_ACT[row['grp']],
                                             'si': self.pc_lpc_replace(row['grp'], row['si']),
                                            }))
           
        return ops
    
    def get_ops_for_crew_document_set(self):
        print "Entering get_ops_for_crew_document_set"
        # crew_document_set table update
        ops = []
        crew_document_set = []
        for row in fixrunner.dbsearch(self.dc, 'crew_document_set', "SUBSTR(subtype, 1, 2) = '{}' or SUBSTR(subtype, 1, 3) = '{}' or SUBSTR(subtype, -2, 2) = '{}' or SUBSTR(subtype, -3, 3) = '{}'".format(PC, OPC, PC, OPC)):
            if row['subtype'] not in (OPC, ):
                ops.append(fixrunner.createOp('crew_document_set', 'D',
                                              {'typ': row['typ'],
                                               'subtype': row['subtype'],
                                              }))
            crew_document_set.append(row)
        for row in crew_document_set:
            if row['subtype'].startswith(PC) or row['subtype'].endswith(PC):
                row['subtype'] = row['subtype'].replace(PC, LPC)
            else:
                row['subtype'] = row['subtype'].replace(OPC, OTS)
            ops.append(fixrunner.createOp('crew_document_set', 'N', row))
          
        return ops
    
    def get_ops_for_crew_document(self):
        print "Entering get_ops_for_crew_document"
        # crew_document table update
        ops = []
        crew_document = []
        for row in fixrunner.dbsearch(self.dc, 'crew_document', "SUBSTR(doc_subtype, 1, 2) = '{}'".format(PC)):
            ops.append(fixrunner.createOp('crew_document', 'D',
                                            {'crew': row['crew'],
                                             'doc_typ': row['doc_typ'],
                                             'doc_subtype': row['doc_subtype'],
                                            }))
            crew_document.append(row)
        for row in fixrunner.dbsearch(self.dc, 'crew_document', "SUBSTR(doc_subtype, 1, 3) = '{}'".format(OPC)):
            if self.crew_is_link(row['crew']):
                continue
            ops.append(fixrunner.createOp('crew_document', 'D',
                                            {'crew': row['crew'],
                                             'doc_typ': row['doc_typ'],
                                             'doc_subtype': row['doc_subtype'],
                                            }))
            crew_document.append(row)
        for row in crew_document:
            if row['doc_subtype'].startswith(PC):
                row['doc_subtype'] = row['doc_subtype'].replace(PC, LPC)
            else:
                row['doc_subtype'] = row['doc_subtype'].replace(OPC, OTS)
            ops.append(fixrunner.createOp('crew_document', 'N', row))
               
        return ops
    
    def get_ops_for_crew_recurrent_set(self):
        print "Entering get_ops_for_crew_recurrent_set"
        # crew_recurrent_set table update
        ops = []
        crew_recurrent_set = []
        for row in fixrunner.dbsearch(self.dc, 'crew_recurrent_set', "SUBSTR(typ, 1, 2) = '{}' or SUBSTR(typ, 1, 3) = '{}'".format(PC, OPC)):
            if not row['typ'] in (OPC,):
                ops.append(fixrunner.createOp('crew_recurrent_set', 'D',
                                                {'typ': row['typ']}))
            crew_recurrent_set.append(row)
        for row in crew_recurrent_set:
            if row['typ'].startswith(PC):
                row['typ'] = row['typ'].replace(PC, LPC)
            else:
                row['typ'] = row['typ'].replace(OPC, OTS)
            ops.append(fixrunner.createOp('crew_recurrent_set', 'N', row))
           
        return ops
    
    def get_ops_for_training_log_set(self):
        print "Entering get_ops_for_training_log_set"
        # training_log_set table update
        ops = []
        training_log_set = []
        for row in fixrunner.dbsearch(self.dc, 'training_log_set', "SUBSTR(typ, 1, 2) = '{}' or SUBSTR(typ, 1, 3) = '{}'".format(PC, OPC)):
            if not row['typ'] in (OPC,):
                ops.append(fixrunner.createOp('training_log_set', 'D',
                                                {'typ': row['typ']}))
            training_log_set.append(row)
        for row in training_log_set:
            if row['typ'].startswith(PC):
                row['typ'] = row['typ'].replace(PC, LPC)
            else:
                row['typ'] = row['typ'].replace(OPC, OTS)
            ops.append(fixrunner.createOp('training_log_set', 'N', row))
        return ops
    
    def get_ops_for_crew_training_log(self):
        print "Entering get_ops_for_crew_training_log"
        # crew_training_log table update
        ops = []
        crew_training_log = []
        for row in fixrunner.dbsearch(self.dc, 'crew_training_log', "tim>={} and (SUBSTR(typ, 1, 2) = '{}' or SUBSTR(typ, 1, 3) = '{}')".format(valid_from, PC, OPC)):
            crew = row['crew']
            if self.crew_is_link(crew) and row['typ'] in (OPC, ):
                continue
            ops.append(fixrunner.createOp('crew_training_log', 'D',
                                           {'crew': row['crew'],
                                            'typ': row['typ'],
                                            'tim' : row['tim'],
                                            'code' : row['code']}))
            crew_training_log.append(row)
        for row in crew_training_log:
            if row['typ'].startswith(PC):
                row['typ'] = row['typ'].replace(PC, LPC)
            else:
                row['typ'] = row['typ'].replace(OPC, OTS)
            ops.append(fixrunner.createOp('crew_training_log', 'N', row))
               
        return ops
    
    def get_ops_for_simulator_set(self):
        print "Entering get_ops_for_simulator_set"
        # simulator_set table update
        ops = []
        simulator_set = []
        for row in fixrunner.dbsearch(self.dc, 'simulator_set', "grp IN ('{}', '{}')".format(PC, OPC)):
            if row['grp'] not in (OPC,):
                ops.append(fixrunner.createOp('simulator_set', 'D',
                                                {'grp': row['grp'],
                                                 'legtime': row['legtime']}))
            simulator_set.append(row)
        for row in simulator_set:
            row['grp'] = SIM_ACT[row['grp']]
            row['simdesc'] = self.pc_lpc_replace(PC, row['simdesc'])
            row['simdesc'] = self.pc_lpc_replace(OPC, row['simdesc'])
            ops.append(fixrunner.createOp('simulator_set', 'N', row))
         
        return ops
    
    def get_ops_for_lpc_opc_ots_composition(self):
        print "Entering get_ops_for_lpc_opc_ots_composition"
        # lpc_ots_composition table update
        ops = []
        lpc_opc_ots_composition = []
        for row in fixrunner.dbsearch(self.dc, 'lpc_opc_ots_composition', "simtype_grp IN ('{}', '{}')".format(PC, OPC)):
            if row['simtype_grp'] not in (OPC,):
                ops.append(fixrunner.createOp('lpc_opc_ots_composition', 'D',
                                                {'simtype_grp': row['simtype_grp'],
                                                 'simtype_legtime': row['simtype_legtime'],
                                                 'qual': row['qual'],
                                                 'validfrom': row['validfrom']}))
            lpc_opc_ots_composition.append(row)
        for row in lpc_opc_ots_composition:
            row['simtype_grp'] = SIM_ACT[row['simtype_grp']]
            ops.append(fixrunner.createOp('lpc_opc_ots_composition', 'N', row))
        return ops
    
    def get_ops_for_simulator_briefings(self):
        print "Entering get_ops_for_simulator_briefings"
        # simulator_briefings table update
        ops = []
        simulator_briefings = []
        for row in fixrunner.dbsearch(self.dc, 'simulator_briefings', "simtype_grp IN ('{}', '{}')".format(PC, OPC)):
            if row['simtype_grp'] not in (OPC,):
                ops.append(fixrunner.createOp('simulator_briefings', 'D',
                                                {'simtype_grp': row['simtype_grp']}))
            simulator_briefings.append(row)
        for row in simulator_briefings:
            row['simtype_grp'] = SIM_ACT[row['simtype_grp']]
            ops.append(fixrunner.createOp('simulator_briefings', 'N', row))
                    
        return ops
    
    def get_ops_for_simulator_composition(self):
        print "Entering get_ops_for_simulator_composition"
        # simulator_composition table update
        ops = []
        simulator_composition = []
        for row in fixrunner.dbsearch(self.dc, 'simulator_composition', "grp IN ('{}', '{}')".format(PC, OPC)):
            if row['grp'] not in (OPC,):
                ops.append(fixrunner.createOp('simulator_composition', 'D',
                                                {'grp': row['grp']}))
            simulator_composition.append(row)
        for row in simulator_composition:
            row['grp'] = SIM_ACT[row['grp']]
            row['si'] = self.pc_lpc_replace(PC, row['si'])
            row['si'] = self.pc_lpc_replace(OPC, row['si'])
            ops.append(fixrunner.createOp('simulator_composition', 'N', row))
        return ops
    
    def get_ops_for_special_schedules(self):
        print "Entering get_ops_for_special_schedules"
        # special_schedules table update
        ops = []
        special_schedules = []
        for row in fixrunner.dbsearch(self.dc, 'special_schedules', "validfrom>={} and str_val IN ('{}', '{}')".format(valid_from, PC, OPC)):
            if self.crew_is_link(row['crewid']) and row['str_val'] in (OPC,):
                continue
            ops.append(fixrunner.createOp('special_schedules', 'D',
                                            {'crewid': row['crewid'],
                                             'typ': row['typ'],
                                             'validfrom': row['validfrom'],
                                             'str_val': row['str_val']}))
            special_schedules.append(row)
        for row in special_schedules:
            row['str_val'] = SIM_ACT[row['str_val']]
            ops.append(fixrunner.createOp('special_schedules', 'N', row))
         
        return ops
    
    def get_ops_for_agreement_validity(self):
        print "Entering get_ops_for_agreement_validity"
        # agreement_validity table update
        ops = []
        agreement_validity = []
        for row in fixrunner.dbsearch(self.dc, 'agreement_validity'):
            if _pc in row['id'] or _opc in row['id'] or _pc_.upper() in row['id'] or _opc_.upper() in row['id']:
                if not (_opc in row['id'] or _opc_.upper() in row['id']):
                    ops.append(fixrunner.createOp('agreement_validity', 'D',
                                                    {'id': row['id'],
                                                     'validfrom': row['validfrom']}))
                agreement_validity.append(row)
        for row in agreement_validity:
            row['id'] = row['id'].replace(_pc, _lpc)
            row['id'] = row['id'].replace(_opc, _ots)
            row['id'] = row['id'].replace(_pc_.upper(), _lpc_.upper())
            row['id'] = row['id'].replace(_opc_.upper(), _ots_.upper())
            row['si'] = self.pc_lpc_replace(PC, row['si'])
            row['si'] = self.pc_lpc_replace(OPC, row['si'])
            ops.append(fixrunner.createOp('agreement_validity', 'N', row))
          
        return ops
    
    def get_ops_for_rule_exception(self):
        print "Entering get_ops_for_rule_exception"
        # rule_exception table update
        ops = []
        rule_exception = []
        for row in fixrunner.dbsearch(self.dc, 'rule_exception', "starttime>={}".format(valid_from)):
            rule = row["ruleid"]
            if self.crew_is_link(row['crew']) and _opc_ in rule:
                continue
            if _pc_ in rule or _opc_ in rule:
                ops.append(fixrunner.createOp('rule_exception', 'D',
                                                {'crew': row['crew'],
                                                 'ruleid': row['ruleid'],
                                                 'starttime': row['starttime'],
                                                 'activitykey': row['activitykey']}))
                rule_exception.append(row)
        for row in rule_exception:
            row['ruleid'] = row['ruleid'].replace(_pc_, _lpc_)
            row['ruleid'] = row['ruleid'].replace(_opc_, _ots_)
            row['ruleremark'] = self.pc_lpc_replace(PC, row['ruleremark'])
            row['ruleremark'] = self.pc_lpc_replace(OPC, row['ruleremark'])
            ops.append(fixrunner.createOp('rule_exception', 'N', row))
        return ops

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    print "Entering fixit"
    ops = []
    pc_opc_fixer = PcOpcFixer(dc)   
    ops += pc_opc_fixer.get_ops_for_activity_group()
    ops += pc_opc_fixer.get_ops_for_activity_group_period()
    ops += pc_opc_fixer.get_ops_for_activity_set()
    ops += pc_opc_fixer.get_ops_for_crew_document_set()
    ops += pc_opc_fixer.get_ops_for_crew_document()
    ops += pc_opc_fixer.get_ops_for_crew_recurrent_set()
    ops += pc_opc_fixer.get_ops_for_training_log_set()
    ops += pc_opc_fixer.get_ops_for_crew_training_log()
    ops += pc_opc_fixer.get_ops_for_simulator_set()
    ops +=pc_opc_fixer.get_ops_for_lpc_opc_ots_composition()
    ops += pc_opc_fixer.get_ops_for_simulator_briefings()
    ops += pc_opc_fixer.get_ops_for_simulator_composition()
    ops += pc_opc_fixer.get_ops_for_special_schedules()
    ops += pc_opc_fixer.get_ops_for_agreement_validity()
    ops += pc_opc_fixer.get_ops_for_rule_exception()


    op_counter = 0
    for op in ops:
        op_counter += 1
        print "op #%s: %s" % (op_counter, str(op))
    return ops

fixit.program = 'sks-547.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


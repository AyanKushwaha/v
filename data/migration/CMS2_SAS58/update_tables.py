#!/bin/env python


"""
SKPROJ-53 New Training Codes
Sprint: SAS58
"""


import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from AbsDate import AbsDate

__version__ = '2017-12-08d'

validfrom = int(AbsTime('01Jul2017 00:00'))
validto = int(AbsTime('31Dec2035 00:00'))

validfrom_date = int(AbsDate('01Jul2017'))/1440
validto_date = int(AbsDate('31Dec2035'))/1440


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    newAct = 'W' # W updates if exists or creates if not. 'N' creates new record.
    updAct = 'W' # W updates if exists or creates if not. 'U' updates existing record.
    updStat = updAct
    log_types_t = {}
    #CC
    log_types_t['si_base_day'] =  'Base Day'
    log_types_t['si_conv_A2'] =   'Conversion A2'
    log_types_t['si_conv_A3A4'] = 'Conversion A3A4'
    log_types_t['si_conv_737'] =  'Conversion 737'
    log_types_t['si_care_sh'] =   'Care SH'
    log_types_t['si_care_lh'] =   'Care LH'
    log_types_t['si_device'] =    'Device'
    log_types_t['si_scc'] =       'SCC Course'
    log_types_t['si_p4s'] =       'AP LH Course'
    log_types_t['si_s4s'] =       'AS Course'
    log_types_t['si_tw13'] =      'AP Refresh Day'
    log_types_t['si_tw12'] =      'AS Refresh Day'
    log_types_t['si_tw10'] =      'AH Refresh Day'
    log_types_t['si_rgt_cx7'] =   'RGT CC'
    log_types_t['si_wd'] =        'Wet Drill'
    #FD
    log_types_t['si_sop2'] =      'SOP A2'
    log_types_t['si_sop3'] =      'SOP 737'
    log_types_t['si_sop4'] =      'SOP A4'
    log_types_t['si_sop6'] =      'SOP A3'
    log_types_t['si_perf2'] =     'PERF A2'
    log_types_t['si_perf3'] =     'PERF 737'
    log_types_t['si_perf4'] =     'PERF A4'
    log_types_t['si_perf6'] =     'PERF A3'
    log_types_t['si_oma2'] =      'OMA A2'
    log_types_t['si_oma3'] =      'OMA 737'
    log_types_t['si_e30'] =       '737 AC specific emergency' #maybe also update E20, E40 and E60 and maybe change to 'Emergency 737'
    log_types_t['si_occcrm'] =    'OCC CRM'
    log_types_t['si_crm'] =       'CRM'
    log_types_t['si_icrm'] =      'Initial CRM'
    # all the STD activities and other keep old activities should most likely be added to training_log_set if their si should be shown in crew_training_log and in TPMS



    si_inst = ''
    id_inst = ''

    activities = []

    # base day trainee
    activities.append({'id': 'I2B',  'si': log_types_t['si_base_day'], 'inst': 'OL'})
    activities.append({'id': 'I4B',  'si': log_types_t['si_base_day'], 'inst': 'OL'})
    activities.append({'id': 'I3B',  'si': log_types_t['si_base_day'], 'inst': 'OL'})
    activities.append({'id': 'C2B',  'si': log_types_t['si_base_day'], 'inst': 'OL'})
    activities.append({'id': 'C4B',  'si': log_types_t['si_base_day'], 'inst': 'OL'})
    activities.append({'id': 'C3B',  'si': log_types_t['si_base_day'], 'inst': 'OL'})
    activities.append({'id': 'IA4B', 'si': log_types_t['si_base_day'], 'inst': 'OL'})
    activities.append({'id': 'CA4B', 'si': log_types_t['si_base_day'], 'inst': 'OL'})

    # Conversion Activities CC
    activities.append({'id': 'I2C',  'si': log_types_t['si_conv_A2'],  'inst': 'OL'})
    activities.append({'id': 'I4C',  'si': log_types_t['si_conv_A3A4'],'inst': 'OL'})
    activities.append({'id': 'I3C',  'si': log_types_t['si_conv_737'], 'inst': 'OL'})
    activities.append({'id': 'Q2C',  'si': log_types_t['si_conv_A2'],  'inst': 'OL'})
    activities.append({'id': 'Q4C',  'si': log_types_t['si_conv_A3A4'],'inst': 'OL'})
    activities.append({'id': 'Q3C',  'si': log_types_t['si_conv_737'], 'inst': 'OL'})
    activities.append({'id': 'C2C',  'si': log_types_t['si_conv_A2'],  'inst': 'OL'})
    activities.append({'id': 'C4C',  'si': log_types_t['si_conv_A3A4'],'inst': 'OL'})
    activities.append({'id': 'C3C',  'si': log_types_t['si_conv_737'], 'inst': 'OL'})
    activities.append({'id': 'IA4C', 'si': log_types_t['si_conv_A3A4'],'inst': 'OL'})
    activities.append({'id': 'CA4C', 'si': log_types_t['si_conv_A3A4'],'inst': 'OL'})

    # Care Activities CC
    activities.append({'id': 'I2S',   'si': log_types_t['si_care_sh'], 'inst': 'OL'})
    activities.append({'id': 'I4S',   'si': log_types_t['si_care_lh'], 'inst': 'OL'})
    activities.append({'id': 'I3S',   'si': log_types_t['si_care_sh'], 'inst': 'OL'})
    activities.append({'id': 'Q2S',   'si': log_types_t['si_care_sh'], 'inst': 'OL'})
    activities.append({'id': 'Q4S',   'si': log_types_t['si_care_lh'], 'inst': 'OL'})
    activities.append({'id': 'Q3S',   'si': log_types_t['si_care_sh'], 'inst': 'OL'})
    activities.append({'id': 'IA4S',  'si': log_types_t['si_care_lh'], 'inst': 'OL'})

    # Device Activities CC
    activities.append({'id': 'I2D',  'si': log_types_t['si_device'], 'inst': 'OL'})
    activities.append({'id': 'I4D',  'si': log_types_t['si_device'], 'inst': 'OL'})
    activities.append({'id': 'I3D',  'si': log_types_t['si_device'], 'inst': 'OL'})
    activities.append({'id': 'IA4D', 'si': log_types_t['si_device'], 'inst': 'OL'})

    # SCC, AP LH and AS Activities CC
    activities.append({'id': 'SCC', 'si': log_types_t['si_scc'], 'inst': 'OL', 'xcat': 'SCC'})
    activities.append({'id': 'P4S', 'si': log_types_t['si_p4s'], 'inst': 'OL'})
    activities.append({'id': 'S4S', 'si': log_types_t['si_s4s'], 'inst': 'OL'})

    # "Refreshdagar" AP, AS, AH activity for CC
    activities.append({'id': 'TW13', 'si': log_types_t['si_tw13'], 'inst': 'OL', 'actStat': 'UPD', 'instStat': 'NEW'}) # only update of si for trainee act
    activities.append({'id': 'TW12', 'si': log_types_t['si_tw12'], 'inst': 'OL', 'actStat': 'UPD', 'instStat': 'NEW'}) # only update of si for trainee act
    activities.append({'id': 'TW10', 'si': log_types_t['si_tw10'], 'inst': 'OL', 'actStat': 'UPD', 'instStat': 'NEW'}) # only update of si for trainee act

    # RGT activity for CC Trainee/Instructor
    activities.append({'id': 'CX7', 'si': log_types_t['si_rgt_cx7'], 'actStat': 'UPD'}) # only update of si from "course".
    activities.append({'id': 'OLR', 'si': 'Instr RGT CC'})

    # STD activity for CC Instructor (the corresponding trainee codes already exist)
    activities.append({'id': 'OLN22', 'si':  'Instr Safety training A2'})
    activities.append({'id': 'OLN24', 'si':  'Instr Safety training A3A4'})
    activities.append({'id': 'OLN38', 'si':  'Instr Safety training 737'})
    activities.append({'id': 'OLNF38', 'si': 'Instr Safety training 737'})
    activities.append({'id': 'OLNF52', 'si': 'Instr Safety training A2'})
    activities.append({'id': 'OLNF56', 'si': 'Instr Safety training A3A4'})
    activities.append({'id': 'OLNQ13', 'si': 'Instr Safety training 737'})
    activities.append({'id': 'OLNQ22', 'si': 'Instr Safety training A2'})
    activities.append({'id': 'OLNQ24', 'si': 'Instr Safety training A3A4'})


    #Auscultation - Instuderingsdag and Instructor meeting
    activities.append({'id': 'IDS', 'si': 'Instructor day for study'})
    activities.append({'id': 'ISM', 'si': 'Instructor meeting', 'actStat': 'UPD'}) # only update of si
    ### CC and FD common
    activities.append({'id': 'WD', 'si': log_types_t['si_wd']})

    # FD SOP activities for Trainee/Instructor
    activities.append({'id': 'SOP2', 'si': log_types_t['si_sop2'], 'inst': 'OX'})
    activities.append({'id': 'SOP3', 'si': log_types_t['si_sop3'], 'inst': 'OX'})
    activities.append({'id': 'SOP4', 'si': log_types_t['si_sop4'], 'inst': 'OX'})
    activities.append({'id': 'SOP6', 'si': log_types_t['si_sop6'], 'inst': 'OX'})

    # FD SOP activities for Trainee/Instructor
    activities.append({'id': 'PERF2', 'si': log_types_t['si_perf2'], 'inst': 'OXPER2'})
    activities.append({'id': 'PERF3', 'si': log_types_t['si_perf3'], 'inst': 'OXPER3'})
    activities.append({'id': 'PERF4', 'si': log_types_t['si_perf4'], 'inst': 'OXPER4'})
    activities.append({'id': 'PERF6', 'si': log_types_t['si_perf6'], 'inst': 'OXPER6'})

    # FD OMB & OMC activities for Instructor
    activities.append({'id': 'OXOMC', 'si': 'Instr OMC'})
    activities.append({'id': 'OXOMB', 'si': 'Instr OMB'})

    # FD OMA activities for Trainee/Instructor
    activities.append({'id': 'OMA2', 'si': log_types_t['si_oma2'], 'inst': 'OX'})
    activities.append({'id': 'OMA3', 'si': log_types_t['si_oma2'], 'inst': 'OX'})

    # FD OCC activities for Trainee/Instructor
    activities.append({'id': 'OCCRM', 'si':log_types_t['si_occcrm'], 'inst': 'OXOCRM'})
    activities.append({'id': 'CRM',   'si': log_types_t['si_crm'],   'inst': 'OX'})
    activities.append({'id': 'ICRM',  'si': log_types_t['si_icrm']})
    activities.append({'id': 'OLICRM','si': 'Instr ICRM'})

    # Instructor activities: OA EX, EN, EH, EK, EJ, E activities for trainee
    activities.append({'id': 'OXOA92','si':  'Instr Pilot day'})
    activities.append({'id': 'OLEX',  'si':  'Instr RGT refresher'})
    activities.append({'id': 'OLT3',  'si':  'OLT3 Instr Newhire RGT 737'})
    activities.append({'id': 'OLT2',  'si':  'OLT2 Instr Newhire RGT A2'})
    activities.append({'id': 'OLR',   'si':  'OLR  Instr RGT'})
    activities.append({'id': 'OLE6',  'si':  'Instr AC demo A3 and RGT E60'})
    activities.append({'id': 'OLE4',  'si':  'Instr AC demo A4 and RGT E40'})
    activities.append({'id': 'OLE2',  'si':  'Instr AC demo A2 and RGT E20'})
    activities.append({'id': 'OLE3',  'si':  'Instr AC demo 737 and RGT E30'})
    activities.append({'id': 'E30',   'si':  log_types_t['si_e30'], 'grp': 'EMG-PGT'})

    # Instructor Trainee activities: BTLB, AC, LROC, LROP, LIFUSB, ETOPS, B
    activities.append({'id': 'OXBTLB', 'si': 'Instr BTLB'})
    activities.append({'id': 'OXLROC', 'si': 'Instr LROC'})
    activities.append({'id': 'OXLROP', 'si': 'Instr LROP'})
    activities.append({'id': 'OXLIFB', 'si': 'Instr LIFUSB'})
    activities.append({'id': 'OXETOP', 'si': 'Instr ETOPS'})

    activities.append({'id': 'ICB', 'si': 'Briefing day instr training'})
    activities.append({'id': 'ICC', 'si': 'Instr candidate course'})
    activities.append({'id': 'ICCR','si': 'Instr candidate course refresh'})
    activities.append({'id': 'CCS', 'si': 'Commander candidate seminar'})
    activities.append({'id': 'CFU', 'si': 'Commander follow up seminar'})
    activities.append({'id': 'TCAM','si': 'Team CRM Assesment Method'})

    activities.append({'id': 'OXICB', 'si': 'Instr ICB'})
    activities.append({'id': 'OXICC', 'si': 'Instr ICC'})
    activities.append({'id': 'OLICC', 'si': 'Instr ICC'})
    activities.append({'id': 'OXICCR','si': 'Instr ICCR'})
    activities.append({'id': 'OLICCR','si': 'Instr ICCR'})
    activities.append({'id': 'OXCCS', 'si': 'Instr CCS'})
    activities.append({'id': 'OXCFU', 'si': 'Instr CFU'})
    activities.append({'id': 'OXTCAM','si': 'Instr TCAM'})

    grp = 'COD'
    for act in activities:
        if not 'actStat' in act:
            updStat = newAct
            ops.append(fixrunner.createOp('activity_set_period', updStat, {'id': act['id'], 'validfrom': validfrom, 'validto': validto, 'si': ''}))
            # If si is set then that value is shown in Studio Info window instead of the si from activity_set
        else:
            updStat = updAct
        if 'grp' in act:
            grp = act['grp']
        else:
            grp = 'COD'
        ops.append(fixrunner.createOp('activity_set', updStat, {'id': act['id'], 'grp': grp, 'si': act['si']}))
        if 'inst' in act:
            updStat = newAct
            if len(act['inst']) == 2:
                id_inst = act['inst'] + act['id']
            else:
                id_inst = act['inst']
            si_inst = 'Instr ' + act['si']
            ops.append(fixrunner.createOp('activity_set', updStat, {'id': id_inst, 'grp': 'COD', 'si': si_inst}))
            if not 'actStat' in act or 'instStat' in act:
                ops.append(fixrunner.createOp('activity_set_period', newAct, {'id': id_inst, 'validfrom': validfrom, 'validto': validto, 'si': ''}))
        if 'xcat' in act:
            ops.append(fixrunner.createOp('cabin_training', newAct, {'taskcode': act['id'], 'validfrom': validfrom_date, 'validto': validto_date, 'base': '', 'qualgroup': 'ANY', 'typ': act['xcat']}))


    # CC Attributes
    ops.append(fixrunner.createOp('training_log_set', newAct, {'typ': 'CC INSTR AUSC', 'grp': 'EDUCATION'}))
    ops.append(fixrunner.createOp('training_log_set', newAct, {'typ': 'CC INSTR EXAM', 'grp': 'EDUCATION'}))

    return ops


fixit.program = 'update_tables.py (%s)' % __version__
if __name__ == '__main__':
    fixit()

# -*- coding: utf-8 -*-

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2015_03_13__02'

extsys = 'S2'
validfrom = int(AbsTime('01FEB2015 00:00'))
validto = int(AbsTime('31DEC2035 00:00'))

salary_crew_activities = [
    [extsys, 'BUDG_ACT_F', validfrom, validto, 'FREEDAY', 100, 'Stipulated day off'],
    [extsys, 'BUDG_ACT_F0', validfrom, validto, 'FREEDAY', 100, 'C/A: Compensation for overtime'],
    [extsys, 'BUDG_ACT_F1', validfrom, validto, 'FREEDAY', 100, 'Legitimated day off'],
    [extsys, 'BUDG_ACT_F10', validfrom, validto, 'FREEDAY', 100, 'Day off in conx. with OX-duty'],
    [extsys, 'BUDG_ACT_F11', validfrom, validto, 'FREEDAY', 100, 'None'],
    [extsys, 'BUDG_ACT_F12', validfrom, validto, 'FREEDAY', 100, 'Day off, special reasons'],
    [extsys, 'BUDG_ACT_F14', validfrom, validto, 'FREEDAY', 100, 'Day off, not to be removed'],
    [extsys, 'BUDG_ACT_F2', validfrom, validto, 'FREEDAY', 100, 'Requested day off'],
    [extsys, 'BUDG_ACT_F20', validfrom, validto, 'FREEDAY', 100, 'Day off in conx. with OX-duty'],
    [extsys, 'BUDG_ACT_F22', validfrom, validto, 'FREEDAY', 100, 'Day off, requested, no salary'],
    [extsys, 'BUDG_ACT_F3', validfrom, validto, 'FREEDAY', 100, 'Compensated day off'],
    [extsys, 'BUDG_ACT_F31', validfrom, validto, 'FREEDAY', 100, 'Compensated day off, NOT entitled to additional days'],
    [extsys, 'BUDG_ACT_F32', validfrom, validto, 'FREEDAY', 100, 'Compensated day off in conx. with duty exceptions'],
    [extsys, 'BUDG_ACT_F33', validfrom, validto, 'FREEDAY', 100, 'Compensated day off'],
    [extsys, 'BUDG_ACT_F34', validfrom, validto, 'FREEDAY', 100, 'Used in conx. with altered sling-day off'],
    [extsys, 'BUDG_ACT_F35', validfrom, validto, 'FREEDAY', 100, 'Compensated day off in conx with \'Förtroendemannavtal C/A\''],
    [extsys, 'BUDG_ACT_F36', validfrom, validto, 'FREEDAY', 100, '4XNG - extra freeday'],
    [extsys, 'BUDG_ACT_F3C', validfrom, validto, 'FREEDAY', 100, 'SC compensation day'],
    [extsys, 'BUDG_ACT_F3M', validfrom, validto, 'FREEDAY', 100, 'Compensated day off, Agreement K01, Commuter'],
    [extsys, 'BUDG_ACT_F3S', validfrom, validto, 'FREEDAY', 100, 'Guaranteed compensation day'],
    [extsys, 'BUDG_ACT_F4', validfrom, validto, 'FREEDAY', 100, 'Day off in connection with sundays and holidays'],
    [extsys, 'BUDG_ACT_F42', validfrom, validto, 'FREEDAY', 100, 'Requested Day off in connection with sundays and holidays'],
    [extsys, 'BUDG_ACT_F45', validfrom, validto, 'FREEDAY', 100, 'Half week-end off (until 31.10.06)'],
    [extsys, 'BUDG_ACT_F5', validfrom, validto, 'FREEDAY', 100, 'Transfer day - stationed crew'],
    [extsys, 'BUDG_ACT_F6', validfrom, validto, 'FREEDAY', 100, 'Meeting/office duty day off without compensation'],
    [extsys, 'BUDG_ACT_F61', validfrom, validto, 'FREEDAY', 100, 'Meeting on day off with compensation'],
    [extsys, 'BUDG_ACT_F62', validfrom, validto, 'FREEDAY', 100, 'Meeting on day off with compensation ref \'Förtroendemannavtal C/A\''],
    [extsys, 'BUDG_ACT_F65', validfrom, validto, 'FREEDAY', 100, 'Teaching on free day'],
    [extsys, 'BUDG_ACT_F7', validfrom, validto, 'FREEDAY', 100, 'Special day off'],
    [extsys, 'BUDG_ACT_F71', validfrom, validto, 'FREEDAY', 100, 'Special day off forced'],
    [extsys, 'BUDG_ACT_F72', validfrom, validto, 'FREEDAY', 100, 'Special day off requested'],
    [extsys, 'BUDG_ACT_F73', validfrom, validto, 'FREEDAY', 100, 'Not used 2005'],
    [extsys, 'BUDG_ACT_F7S', validfrom, validto, 'FREEDAY', 100, 'Guaranteeed F7-day'],
    [extsys, 'BUDG_ACT_F8', validfrom, validto, 'FREEDAY', 100, 'Days off part time'],
    [extsys, 'BUDG_ACT_F81', validfrom, validto, 'FREEDAY', 100, 'Days off part time'],
    [extsys, 'BUDG_ACT_F82', validfrom, validto, 'FREEDAY', 100, 'Requested day off, part time'],
    [extsys, 'BUDG_ACT_F84', validfrom, validto, 'FREEDAY', 100, 'Moved F88 in connection with VA'],
    [extsys, 'BUDG_ACT_F85', validfrom, validto, 'FREEDAY', 100, 'Days off part time'],
    [extsys, 'BUDG_ACT_F88', validfrom, validto, 'FREEDAY', 100, 'Day off, part time CC'],
    [extsys, 'BUDG_ACT_F89', validfrom, validto, 'FREEDAY', 100, 'Compensation day for SKD crew with summer contract'],
    [extsys, 'BUDG_ACT_F9', validfrom, validto, 'FREEDAY', 100, 'Requested day off/unions'],
    [extsys, 'BUDG_ACT_FE', validfrom, validto, 'FREEDAY', 100, 'Extra F-day'],
    [extsys, 'BUDG_ACT_FF', validfrom, validto, 'FREEDAY', 100, 'Compensated day off, forward'],
    [extsys, 'BUDG_ACT_FK', validfrom, validto, 'FREEDAY', 100, 'Day off in connection with KD duty'],
    [extsys, 'BUDG_ACT_FN', validfrom, validto, 'FREEDAY', 100, 'Temps F-day'],
    [extsys, 'BUDG_ACT_FP', validfrom, validto, 'FREEDAY', 100, 'None'],
    [extsys, 'BUDG_ACT_FS', validfrom, validto, 'FREEDAY', 100, 'Prioritized (super) free day'],
    [extsys, 'BUDG_ACT_IL8', validfrom, validto, 'FREEDAY', 100, 'Part-time Illness day'],
    [extsys, 'BUDG_ACT_LA35', validfrom, validto, 'FREEDAY', 100, 'F/D + C/A Forced LA'],
    [extsys, 'BUDG_ACT_LA53', validfrom, validto, 'FREEDAY', 100, 'Retiree, part time OSL/CPH, placed in min. 3 in block'],
    [extsys, 'BUDG_ACT_LA55', validfrom, validto, 'FREEDAY', 100, 'Part time'],
    [extsys, 'BUDG_ACT_LA58', validfrom, validto, 'FREEDAY', 100, 'LOA, flight crew part time, locked days'],
    [extsys, 'BUDG_ACT_LA8', validfrom, validto, 'FREEDAY', 100, 'Partial LOA by law'],
    [extsys, 'BUDG_ACT_LA84', validfrom, validto, 'FREEDAY', 100, 'Partial LOA - not law'],
    [extsys, 'BUDG_ACT_LA85', validfrom, validto, 'FREEDAY', 100, 'F/D Parttime'],
    [extsys, 'ABS_ACT_ILR', validfrom, validto, '300', 100, 'IL 00:00-23:59 Illnes, report-back'],
    [extsys, 'ABS_ACT_LA4', validfrom, validto, '500', 100, 'Not used 2005'],
    [extsys, 'ABS_ACT_LA5', validfrom, validto, '500', 100, 'None'],
    [extsys, 'ABS_ACT_LA7', validfrom, validto, '500', 100, 'LOA, creating own company'],
    [extsys, 'ABS_ACT_LA44', validfrom, validto, '500', 100, 'C/A LA special reasons'],
    [extsys, 'ABS_ACT_LA47', validfrom, validto, '500', 100, 'C/A LA 12-18 mths after 10 years employment'],
    [extsys, 'ABS_ACT_LA46', validfrom, validto, '500', 100, 'C/A special LA 1991'],
    [extsys, 'ABS_ACT_LA41', validfrom, validto, '500', 100, 'C/A LA with advance notice'],
    [extsys, 'ABS_ACT_LA42', validfrom, validto, '509', 100, 'C/A LA last minute'],
    [extsys, 'ABS_ACT_LA48', validfrom, validto, '500', 100, 'C/A LA binding for 1-3 years'],
    [extsys, 'ABS_ACT_LA80', validfrom, validto, '500', 100, 'F/D LA (agreement 02 JAN 92)'],
    [extsys, 'ABS_ACT_LA83', validfrom, validto, '525', 100, 'CPH C/A Unpaid education'],
    [extsys, 'ABS_ACT_LA87', validfrom, validto, '500', 100, 'CPH C/A Sabbatical year'],
    [extsys, 'ABS_ACT_LA86', validfrom, validto, '500', 100, 'CPH C/A Special parent LA'],
    [extsys, 'ABS_ACT_LA89', validfrom, validto, '500', 100, 'C/A voluntary leave of absence'],
    [extsys, 'ABS_ACT_LA88', validfrom, validto, '500', 100, 'C/A forced leave of absence'],
    [extsys, 'ABS_ACT_LA31', validfrom, validto, '500', 100, 'F/D LA with advanced notice'],
    [extsys, 'ABS_ACT_LA32', validfrom, validto, '509', 100, 'F/D LA last minute'],
    [extsys, 'ABS_ACT_LA33', validfrom, validto, '500', 100, 'F/D released to associated airlines'],
    [extsys, 'ABS_ACT_LA36', validfrom, validto, '500', 100, 'F/D special LA 1991'],
    [extsys, 'ABS_ACT_LA37', validfrom, validto, '500', 100, 'F/D LA (agreement 02 JAN 92)'],
    [extsys, 'ABS_ACT_LA39', validfrom, validto, '500', 100, 'LOA'],
    [extsys, 'ABS_ACT_IL12', validfrom, validto, '300', 100, 'Illness, more than 14 days'],
    [extsys, 'ABS_ACT_IL14', validfrom, validto, '300', 100, 'Illness allowance Swedish crew'],
    [extsys, 'ABS_ACT_IL6', validfrom, validto, '300', 100, 'Illness  due LA6'],
    [extsys, 'ABS_ACT_IL7', validfrom, validto, '300', 25, 'Illness while on duty'],
    [extsys, 'ABS_ACT_IL4', validfrom, validto, '300', 100, 'Illness, Swedish crew: IL on day off'],
    [extsys, 'ABS_ACT_IL5', validfrom, validto, '300', 100, 'Illness'],
    [extsys, 'ABS_ACT_IL2', validfrom, validto, '300', 100, 'Illness, Danish crew'],
    [extsys, 'ABS_ACT_IL3', validfrom, validto, '300', 100, 'Illness, Norwegian crew'],
    [extsys, 'ABS_ACT_IL1', validfrom, validto, '300', 100, 'Illness, Swedish crew'],
    [extsys, 'ABS_ACT_LA76', validfrom, validto, '400', 100, 'LOA maternity, from week 22/2002'],
    [extsys, 'ABS_ACT_LA77', validfrom, validto, '400', 100, 'LOA maternity, 8 + 6 weeks'],
    [extsys, 'ABS_ACT_LA70', validfrom, validto, '500', 100, 'LOA unknown'],
    [extsys, 'ABS_ACT_LA71', validfrom, validto, '500', 100, 'LOA - Creating own Company'],
    [extsys, 'ABS_ACT_LA72', validfrom, validto, '500', 100, 'loa'],
    [extsys, 'ABS_ACT_LA73', validfrom, validto, '500', 100, 'loa'],
    [extsys, 'ABS_ACT_IL7R', validfrom, validto, '300', 25, 'IL7 12:00-12:01 Illnes, report-back'],
    [extsys, 'ABS_ACT_LA92R', validfrom, validto, '420', 100, 'LA due contactday, report back'],
    [extsys, 'ABS_ACT_IL12R', validfrom, validto, '300', 100, 'Illness, more than 14 days, report-back'],
    [extsys, 'ABS_ACT_LA22', validfrom, validto, '552', 100, 'C/A LA due studies 1991'],
    [extsys, 'ABS_ACT_LA21', validfrom, validto, '525', 100, 'Swedish crew - LA due studies'],
    [extsys, 'ABS_ACT_LA20', validfrom, validto, '525', 100, 'Not used 2005'],
    [extsys, 'ABS_ACT_IL41', validfrom, validto, '300', 100, 'Illness, Swedish crew: IL on day off'],
    [extsys, 'ABS_ACT_LA', validfrom, validto, '500', 100, 'LOA'],
    [extsys, 'ABS_ACT_LA68', validfrom, validto, '500', 100, 'LOA'],
    [extsys, 'ABS_ACT_LA67', validfrom, validto, '500', 100, 'LOA unknown reason'],
    [extsys, 'ABS_ACT_LA66', validfrom, validto, '400', 100, 'special parent LA'],
    [extsys, 'ABS_ACT_LA65', validfrom, validto, '420', 100, 'Father\'s share of final 8 weeks of regular maternity LA'],
    [extsys, 'ABS_ACT_LA64', validfrom, validto, '420', 100, '14 days maternity LA from date of birth'],
    [extsys, 'ABS_ACT_LA63', validfrom, validto, '400', 100, 'Extended maternity LA'],
    [extsys, 'ABS_ACT_LA62', validfrom, validto, '400', 100, 'Pregnancy and maternity LA'],
    [extsys, 'ABS_ACT_IL4R', validfrom, validto, '300', 100, 'IL4 00:00-23:59 Illnes, Swedish crew: IL on day off, report-back'],
    [extsys, 'ABS_ACT_LA91R', validfrom, validto, '420', 100, 'LA due sick child, report back'],
    [extsys, 'ABS_ACT_IL', validfrom, validto, '300', 100, 'Illness'],
    [extsys, 'ABS_ACT_ID', validfrom, validto, '300', 100, 'Illnes for deputy crew'],
    [extsys, 'ABS_ACT_MI', validfrom, validto, '535', 100, 'Military service'],
    [extsys, 'ABS_ACT_LA59', validfrom, validto, '500', 100, 'LOA more than 1 year, not to be removed'],
    [extsys, 'ABS_ACT_LA92', validfrom, validto, '420', 100, 'LA due contactday'],
    [extsys, 'ABS_ACT_LA91', validfrom, validto, '420', 100, 'LA due sick child'],
    [extsys, 'ABS_ACT_LA52', validfrom, validto, '500', 100, 'C/A released to assiocated airlines'],
    [extsys, 'ABS_ACT_LA57', validfrom, validto, '500', 100, 'LOA, flight crew, agreement 05jan02 not to be removed'],
    [extsys, 'ABS_ACT_VA_CC', validfrom, validto, '200', 100, 'Vacation'],
    [extsys, 'ABS_ACT_VA8_CC', validfrom, validto, '200', 100, 'Vacation'],
    [extsys, 'ABS_ACT_VA1H_CC', validfrom, validto, '200', 100, 'Vacation without salary high rate SKN'],
    [extsys, 'ABS_ACT_VA1D_CC', validfrom, validto, '200', 100, 'Vacation without salary double rate SKN'],
    [extsys, 'ABS_ACT_VA3_CC', validfrom, validto, '200', 100, 'Vacation'],
    [extsys, 'ABS_ACT_VA1_CC', validfrom, validto, '200', 100, 'Vacation without salary'],
    [extsys, 'ABS_ACT_VAH_CC', validfrom, validto, '200', 100, 'Vacation with high rate SKN'],
    [extsys, 'ABS_ACT_VAD_CC', validfrom, validto, '200', 100, 'Vacation with double rate SKN'],
    [extsys, 'ABS_ACT_VA1_FC', validfrom, validto, '203', 100, 'Vacation without salary'],
    ]

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    for sca in salary_crew_activities:
        ops.append(fixrunner.createOp('salary_crew_activity', 'N', {
                    'extsys':      sca[0],
                    'intartid':    sca[1],
                    'validfrom':   sca[2],
                    'validto':     sca[3],
                    'extartid':    sca[4],
                    'extent' :     sca[5],
                    'note':        sca[6]
                    }))

    print "done"
    return ops


fixit.program = 'skcms_405-2.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



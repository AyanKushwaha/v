import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '2015_03_04__02'

extsys = 'S2'
validfrom = int(AbsTime('01FEB2015 00:00'))
validto = int(AbsTime('31DEC2035 00:00'))

salary_articles = [[extsys, '031', validfrom, validto, 'TEMPCREW', 'Temporary crew hours'],
                   [extsys, '032', validfrom, validto, 'TEMPCREWOT', 'Temporary crew overtime'],
                   [extsys, '160', validfrom, validto, 'OTPT', 'Overtime for part time crew'],
                   [extsys, '162', validfrom, validto, 'CALM_OTFC', 'Overtime for calendar month / flight crew'],
                   [extsys, '163', validfrom, validto, 'CALW', 'Calender week (42 hrs)'],
                   [extsys, '16B', validfrom, validto, 'BOUGHT', 'Bought day ( > 6 hours) FC and CC 14 pct'],
                   [extsys, '16D', validfrom, validto, 'DUTYP', 'Duty pass overtime (former L204)'],
                   [extsys, '16C', validfrom, validto, 'BOUGHT_8', 'Bought day (<= 6 hours) CC and FC 8 pct'],
                   [extsys, 'q16', validfrom, validto, 'F7S', 'F7S days'],
                   [extsys, '290', validfrom, validto, 'F31_F33', 'Comp days'],
                   [extsys, 'q17', validfrom, validto, 'F0_F3', 'Comp days other'],
                   [extsys, 'ob1', validfrom, validto, 'LRLOW', 'Loss of rest (low)'], # FIXME: Obsolete?
                   [extsys, '048', validfrom, validto, 'SCC', 'Senior cabin crew allowance'],
                   [extsys, '049', validfrom, validto, 'MDC', 'Maitre de cabin (purser allowance)'],
                   [extsys, '051', validfrom, validto, 'INST_LCI', 'Instructor - LCI'],
                   [extsys, '053', validfrom, validto, 'INST_SIM', 'Instructor - Simulator'],
                   [extsys, '054', validfrom, validto, 'INST_SIM_BR', 'Instructor - Simulator (Brief/Debrief)'],
                   [extsys, '055', validfrom, validto, 'INST_CC', 'Instructor - CC'],
                   [extsys, '056', validfrom, validto, 'INST_SKILL_TEST', 'Instructor - Skill-Test'],
                   [extsys, '052', validfrom, validto, 'INST_LCI_LH', 'Instructor - LCI (LH)'],
                   [extsys, '057', validfrom, validto, 'INST_LIFUS_ACT', 'Instructor - Simulator'],
                   [extsys, '058', validfrom, validto, 'INST_CRM', 'Instructor - CRM'],
                   [extsys, '059', validfrom, validto, 'INST_CLASS', 'Instructor - Classroom'],
                   [extsys, '709', validfrom, validto, 'PERDIEM_TAX_DAY', None],
                   [extsys, '702', validfrom, validto, 'PERDIEM_TAX_DOMESTIC', ' '],
                   [extsys, '706', validfrom, validto, 'PERDIEM_TAX_INTER', ' '],
                   [extsys, '205', validfrom, validto, 'VA_REMAINING_YR', 'VA days year account'],
                   [extsys, '200', validfrom, validto, 'VA_PERFORMED', 'Performed VA'],
                   [extsys, '701', validfrom, validto, 'PERDIEM_SALDO', 'Per Diem saldo, if positive'],
                   [extsys, '971', validfrom, validto, 'MEAL', 'Meal on board deduction FC and CC']]

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    for sa in salary_articles:
        ops.append(fixrunner.createOp('salary_article', 'N', {
                    'extsys':      sa[0],
                    'extartid':    sa[1],
                    'validfrom':   sa[2],
                    'validto':     sa[3],
                    'intartid':    sa[4],
                    'note':        sa[5]
                    }))

    print "done"
    return ops


fixit.program = 'skcms_405.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



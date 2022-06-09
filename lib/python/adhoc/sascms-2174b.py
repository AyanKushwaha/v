#!/bin/env python


"""
SASCMS-2174B - Balancing report distribution, migration of old configuration
"""

import adhoc.fixrunner as fixrunner


__version__ = '1'


@fixrunner.run
@fixrunner.once
def fixit(dc, *a, **k):
    ops = []
    for rpt in ['AMBI','VACATION_P','VACATION_R','VACATIONYF','VACATIONYC','VACATION_Y','COMPDAYS','VAC_LISTS']:
        ops += [
            fixrunner.createOp('dig_reporttype_set', 'N', {
                'maintype': 'SALARY_EXPORT',
                'subtype': rpt
            })]
        for rcpt in ['*','DK','SE','NO','JP','CN']:
            if rpt == 'VACATION_P' and rcpt != 'DK': continue
            if rpt == 'VACATION_R' and rcpt != 'DK': continue
            if rpt == 'VACATIONYF' and rcpt != 'DK' and rcpt != 'NO': continue
            if rpt == 'VACATIONYC' and rcpt != 'NO': continue
            if rpt == 'VACATION_Y' and rcpt != 'SE': continue
            if rpt == 'VAC_LISTS' and rcpt != 'SE' and rcpt != 'NO': continue
            ops += [
                fixrunner.createOp('dig_reportrecipient_set', 'N', {
                    'reporttype_maintype': 'SALARY_EXPORT',
                    'reporttype_subtype':rpt,
                    'rcpttype': rcpt
                })]
            ops += [
                fixrunner.createOp('dig_reportrecipient_set', 'N', {
                    'reporttype_maintype': 'BALANCING_REPORT',
                    'reporttype_subtype':rpt,
                    'rcpttype': rcpt
                })]
            
    for rpt in ['*','PERDIEM','OVERTIME','TEMP_CREW','SUPERVIS']:
        ops += [
            fixrunner.createOp('dig_reporttype_set', 'N', {
                'maintype': 'SALARY_EXPORT',
                'subtype': rpt
            })]
        if rpt == "OVERTIME": ops += [
            fixrunner.createOp('dig_reporttype_set', 'N', {
                'maintype': 'CONVERSION_REPORT',
                'subtype': rpt
            })]
        for rcpt in ['*','DK','SE','NO','JP','CN']:
            if rpt == 'TEMP_CREW' and rcpt != 'DK': continue
            ops += [
                fixrunner.createOp('dig_reportrecipient_set', 'N', {
                    'reporttype_maintype': 'SALARY_EXPORT',
                    'reporttype_subtype':rpt,
                    'rcpttype': rcpt
                })]
            if rpt == "OVERTIME" and rcpt == "DK": ops += [
                fixrunner.createOp('dig_reportrecipient_set', 'N', {
                    'reporttype_maintype': 'CONVERSION_REPORT',
                    'reporttype_subtype':rpt,
                    'rcpttype': rcpt
                })]
    d = '$CARMDATA/REPORTS/SALARY_RELEASE/'
    ops += [
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'AMBI',
            'recipient_rcpttype':'DK',
            'protocol':'file',
            'target':d+'ambicph.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'AMBI',
            'recipient_rcpttype':'DK',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk",
            'subject':"BALANCING REPORT AMBI",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'VACATION_P',
            'recipient_rcpttype':'DK',
            'protocol':'file',
            'target':d+'vacph0.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'VACATION_P',
            'recipient_rcpttype':'DK',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk",
            'subject':"BALANCING REPORT VACATION DAYS PERFORMED",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'VACATION_R',
            'recipient_rcpttype':'DK',
            'protocol':'file',
            'target':d+'vacph1.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'VACATION_R',
            'recipient_rcpttype':'DK',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk",
            'subject':"BALANCING REPORT VACATION DAYS REMAINING",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'VACATIONYF',
            'recipient_rcpttype':'DK',
            'protocol':'file',
            'target':d+'vacph2.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'VACATIONYF',
            'recipient_rcpttype':'DK',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk",
            'subject':"BALANCING REPORT VACATION DAYS YEAR ACCOUNT",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'VACATIONYF',
            'recipient_rcpttype':'NO',
            'protocol':'file',
            'target':d+'vaoslf.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'VACATIONYF',
            'recipient_rcpttype':'NO',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk",
            'subject':"BALANCING REPORT VACATION DAYS YEAR ACCOUNT (FD)",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'VACATIONYC',
            'recipient_rcpttype':'NO',
            'protocol':'file',
            'target':d+'vaosla.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'VACATIONYC',
            'recipient_rcpttype':'NO',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk",
            'subject':"BALANCING REPORT VACATION DAYS YEAR ACCOUNT (CC)",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'VACATION_Y',
            'recipient_rcpttype':'SE',
            'protocol':'file',
            'target':d+'vasto3.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'VACATION_Y',
            'recipient_rcpttype':'SE',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk",
            'subject':"BALANCING REPORT VACATION DAYS YEAR ACCOUNT",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'PERDIEM',
            'recipient_rcpttype':'DK',
            'protocol':'file',
            'target':d+'pdiemcph.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'PERDIEM',
            'recipient_rcpttype':'DK',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk;Perdiem.Danmark@sas.dk",
            'subject':"BALANCING REPORT Per Diem DK",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'PERDIEM',
            'recipient_rcpttype':'NO',
            'protocol':'file',
            'target':d+'pdiemosl.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'PERDIEM',
            'recipient_rcpttype':'NO',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk;;Perdiem.Norge@sas.no",
            'subject':"BALANCING REPORT Per Diem NO",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'PERDIEM',
            'recipient_rcpttype':'SE',
            'protocol':'file',
            'target':d+'pdiemsto.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'PERDIEM',
            'recipient_rcpttype':'SE',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk;Ulf.Christofferson@sas.se",
            'subject':"BALANCING REPORT Per Diem SE",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'SUPERVIS',
            'recipient_rcpttype':'DK',
            'protocol':'file',
            'target':d+'svcph.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'SUPERVIS',
            'recipient_rcpttype':'DK',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk",
            'subject':"BALANCING REPORT Instructor Allowance DK",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'SUPERVIS',
            'recipient_rcpttype':'NO',
            'protocol':'file',
            'target':d+'svosl.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'SUPERVIS',
            'recipient_rcpttype':'NO',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk",
            'subject':"BALANCING REPORT Instructor Allowance NO",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'SUPERVIS',
            'recipient_rcpttype':'SE',
            'protocol':'file',
            'target':d+'svsto.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'SUPERVIS',
            'recipient_rcpttype':'SE',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk",
            'subject':"BALANCING REPORT Instructor Allowance SE",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'OVERTIME',
            'recipient_rcpttype':'DK',
            'protocol':'file',
            'target':d+'ussalcph.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'OVERTIME',
            'recipient_rcpttype':'DK',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk;Leo.Hjorth@sas.dk;Bo.Dithmar@sas.dk",
            'subject':"BALANCING REPORT Overtime DK",
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'CONVERSION_REPORT',
            'recipient_reporttype_subtype':'OVERTIME',
            'recipient_rcpttype':'DK',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk;Leo.Hjorth@sas.dk;Bo.Dithmar@sas.dk",
            'subject':"Convertible Crew",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'OVERTIME',
            'recipient_rcpttype':'NO',
            'protocol':'file',
            'target':d+'ussalosl.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'OVERTIME',
            'recipient_rcpttype':'NO',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk;Rita.Madssen@sas.no;Harald.Hoier@sas.no",
            'subject':"BALANCING REPORT Overtime NO",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'OVERTIME',
            'recipient_rcpttype':'SE',
            'protocol':'file',
            'target':d+'ussalsto.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'OVERTIME',
            'recipient_rcpttype':'SE',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk",
            'subject':"BALANCING REPORT Overtime NO",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'TEMP_CREW',
            'recipient_rcpttype':'DK',
            'protocol':'file',
            'target':d+'tempcdk.sal',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'TEMP_CREW',
            'recipient_rcpttype':'DK',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk;Leo.Hjorth@sas.dk;Bo.Dithmar@sas.dk",
            'subject':"BALANCING REPORT Temporary Crew Allowance",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'TEMP_CREW',
            'recipient_rcpttype':'NO',
            'protocol':'file',
            'target':d+'tempcno.sal',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'TEMP_CREW',
            'recipient_rcpttype':'NO',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk;Rita.Madssen@sas.no;Harald.Hoier@sas.no",
            'subject':"BALANCING REPORT Temporary Crew Allowance",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'COMPDAYS',
            'recipient_rcpttype':'DK',
            'protocol':'file',
            'target':d+'fdaycph.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'COMPDAYS',
            'recipient_rcpttype':'DK',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk",
            'subject':"BALANCING REPORT Freedays/Comp.days",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'COMPDAYS',
            'recipient_rcpttype':'NO',
            'protocol':'file',
            'target':d+'fdayosl.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'COMPDAYS',
            'recipient_rcpttype':'NO',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk",
            'subject':"BALANCING REPORT Freedays/Comp.days",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'COMPDAYS',
            'recipient_rcpttype':'SE',
            'protocol':'file',
            'target':d+'fdaysto.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'COMPDAYS',
            'recipient_rcpttype':'SE',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk",
            'subject':"BALANCING REPORT Freedays/Comp.days",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'VAC_LISTS',
            'recipient_rcpttype':'NO',
            'protocol':'file',
            'target':d+'vaperosl.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'VAC_LISTS',
            'recipient_rcpttype':'NO',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk,68157@sas.no",
            'subject':"BALANCING REPORT Vacation Lists",
        }),
        
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'SALARY_EXPORT',
            'recipient_reporttype_subtype':'VAC_LISTS',
            'recipient_rcpttype':'SE',
            'protocol':'file',
            'target':d+'vapersto.dat',
        }),
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': 'BALANCING_REPORT',
            'recipient_reporttype_subtype':'VAC_LISTS',
            'recipient_rcpttype':'SE',
            'protocol':'mail',
            'target':"CPHPGCrewSystems@sas.dk",
            'subject':"BALANCING REPORT Vacation Lists",
        }),
        
        ]
    return ops


fixit.program = 'sascms-2174b.py (%s)' % __version__


if __name__ == '__main__':
    # reverting results from earlier runs (revids)
    fixit()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof

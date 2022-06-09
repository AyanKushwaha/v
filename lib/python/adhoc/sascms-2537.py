#!/bin/env python


"""
SASCMS-2537 - RFI53 Error messages in Crew Meal
"""

import adhoc.fixrunner as fixrunner


__version__ = '1'


@fixrunner.run
@fixrunner.once
def fixit(dc, *a, **k):
    ops = []

    reporttype = "CREW_MEAL"
    report_subtypes = ['*','CreateCari','DeleteCari','ERROR']
    rcpttypes       = [{ 'rcpttype': '*', 'label': 'All crew meal errors', 'pattern': '.*' },
                       { 'rcpttype': 'ERROR_NO_ORDERS_DATE', 'label': 'Crew meal No order entries for date', 'pattern': 'Could not create meal_order entry for date' },
                       { 'rcpttype': 'ERROR_INV_CUSTOMER', 'label': 'Crew meal Invalid customer', 'pattern': 'Customer not valid' },
                       { 'rcpttype': 'ERROR_DELIVER_SAS', 'label': 'Crew meal Delivery failed SAS', 'pattern': 'Delivery has failed SAS' },
                       { 'rcpttype': 'ERROR_DELIVER_SUPP', 'label': 'Crew meal Delivery failed Supplier', 'pattern': 'Delivery has failed SUPPLIER' },
                       { 'rcpttype': 'FATAL_ERROR', 'label': 'Crew meal fatal error', 'pattern': 'DIG channel \'meal\' fatal error' },
                       { 'rcpttype': 'EMPTY_PDF_FILE', 'label': 'Crew meal empty PDF file', 'pattern': 'Order has empty PDF file' },
                       { 'rcpttype': 'EMPTY_XML_FILE', 'label': 'Crew meal empty XML file', 'pattern': 'Order has empty XML file' },
                       { 'rcpttype': 'OUTSIDE_LOADED_DATA', 'label': 'Crew meal order data outside loaded data', 'pattern': 'Order data is outside the report servers loaded data' }]

    # creating dig_reporttype_set entries
    for subtype in report_subtypes:
        ops += [
            fixrunner.createOp('dig_reporttype_set', 'N', {
                'maintype': reporttype,
                'subtype': subtype
            })]

    # creating dig_reportrecipient_set entries
    for subtype in report_subtypes:
        for rcpttype in rcpttypes:
            if rcpttype['rcpttype'] == '*' or subtype == '*' or subtype == 'ERROR':
                ops += [
                    fixrunner.createOp('dig_reportrecipient_set', 'N', {
                    'reporttype_maintype': reporttype,
                    'reporttype_subtype': subtype,
                    'rcpttype': rcpttype['rcpttype']
                    })]
                if subtype == 'ERROR' and rcpttype['rcpttype'] != '*':
                    ops += [fixrunner.createOp('dig_recipients', 'N', {
                        'recipient_reporttype_maintype': reporttype,
                        'recipient_reporttype_subtype': subtype,
                        'recipient_rcpttype': rcpttype['rcpttype'],
                        'protocol': 'mail',
                        'target': 'CMOS@sas.dk'
                    })]
                    
    ops += [fixrunner.createOp('dig_recipients', 'N', {
                        'recipient_reporttype_maintype': 'CREW_MEAL',
                        'recipient_reporttype_subtype': 'CreateCari',
                        'recipient_rcpttype': "*",
                        'protocol': 'mq',
                        'target': 'CQT324A%(dig_settings/mq/out_qsuffix)@%(dig_settings/mq/manager)'
                    })]
    ops += [fixrunner.createOp('dig_recipients', 'N', {
                        'recipient_reporttype_maintype': 'CREW_MEAL',
                        'recipient_reporttype_subtype': 'DeleteCari',
                        'recipient_rcpttype': "*",
                        'protocol': 'mq',
                        'target': 'CQT324B%(dig_settings/mq/out_qsuffix)@%(dig_settings/mq/manager)'
                    })]
    

    # creating dig_recipient entry
    ops += [
        fixrunner.createOp('dig_recipients', 'N', {
            'recipient_reporttype_maintype': reporttype,
            'recipient_reporttype_subtype': subtype,
            'recipient_rcpttype': "*",
            'protocol':'mail',
            'target':'CMOS@sas.dk'
        })]

    # creating dig_string_patterns entries
    for rcpttype in rcpttypes:
        ops += [
            fixrunner.createOp('dig_string_patterns', 'N', {
                'recipient_reporttype_maintype': 'CREW_MEAL',
                'recipient_reporttype_subtype': 'ERROR',
                'recipient_rcpttype': rcpttype['rcpttype'],
                'label': rcpttype['label'],
                'pattern': rcpttype['pattern']
            })]
    
    return ops


fixit.program = 'sascms-2537.py (%s)' % __version__


if __name__ == '__main__':
    fixit()

#!/bin/env python


"""
SASCMS-4507 New flight owner table. Adding default destination for 
errors when populating the meal_flight_owver table.

"""

import adhoc.fixrunner as fixrunner

__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    # Add default configuration for flight owner error message
    
    if len(fixrunner.dbsearch(dc, 'dig_reporttype_set', "maintype='FLIGHT_OWNER' and subtype='ERROR'")) == 0:
        ops.append(fixrunner.createop('dig_reporttype_set', 'N', {'maintype': 'FLIGHT_OWNER',
                                                                  'subtype': 'ERROR',
                                                                  'si': 'Flight owner errors'}))
    else:
        print "dig_reporttype_set row already exists."


    if len(fixrunner.dbsearch(dc, 'dig_reportrecipient_set', "reporttype_maintype='FLIGHT_OWNER' and reporttype_subtype='ERROR' and rcpttype='*'")) == 0:
        ops.append(fixrunner.createop('dig_reportrecipient_set', 'N', {'reporttype_maintype': 'FLIGHT_OWNER',
                                                                       'reporttype_subtype': 'ERROR',
                                                                       'rcpttype': '*',
                                                                       'si': ''}))
    else:
        print "dig_reportrecepient_set row already exists."

    
    if len(fixrunner.dbsearch(dc, 'dig_recipients', "recipient_reporttype_maintype='FLIGHT_OWNER' and recipient_reporttype_subtype='ERROR' and recipient_rcpttype='*'")) == 0:
        ops.append(fixrunner.createop('dig_recipients', 'N', {'recipient_reporttype_maintype' : 'FLIGHT_OWNER',
                                                              'recipient_reporttype_subtype' : 'ERROR',
                                                              'recipient_rcpttype'  : '*',
                                                              'protocol': 'mail',
                                                              'target': 'CPHPGcrewSystems@sas.dk',
                                                              'subject' : '',
                                                              'si': ''}))
    else:
        print "dig_recepients row already exists."
    
    return ops


fixit.program = 'sascms-4507.py (%s)' % __version__


if __name__ == '__main__':
    fixit()

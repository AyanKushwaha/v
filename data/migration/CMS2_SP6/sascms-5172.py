#!/bin/env python


"""
SASCMS-5172: Populate the new version of apt_restrictions
"""

import adhoc.fixrunner as fixrunner
import os
from subprocess import call


__version__ = '1'


def entry(apt, resttyp, subtyp, ac_qual, all, first, four):
    return {'station'      : apt,
            'restr_typ'    : resttyp,
            'restr_subtype': subtyp,
            'ac_qual'      : ac_qual,
            'lifus_all'    : all,
            'lifus_first'  : first,
            'lifus_four'   : four}


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    data = [entry('ORD','TRAINING','CAPT','A3A4','N','Y','N'),
            
            entry('SVO','TRAINING','CAPT','A2','N','N','Y'),
            entry('LED','TRAINING','CAPT','A2','N','N','Y'),
            entry('NCE','TRAINING','CAPT','A2','N','N','Y'),
            entry('GZP','TRAINING','CAPT','A2','N','N','Y'),
            
            entry('SVO','TRAINING','CAPT','37','N','N','Y'),
            entry('LED','TRAINING','CAPT','37','N','N','Y'),
            entry('LYR','TRAINING','CAPT','37','N','N','Y'),

            entry('SVO','TRAINING','CAPT','M8','Y','N','N'),
            entry('LED','TRAINING','CAPT','M8','Y','N','N'),

            entry('SVO','TRAINING','CAPT','CJ','N','N','Y'),
            entry('LED','TRAINING','CAPT','CJ','N','N','Y'),
            entry('NCE','TRAINING','CAPT','CJ','N','N','Y')]

    
    for d in data:
        if len(fixrunner.dbsearch(dc, 'apt_restrictions', ' AND '.join((
            "station='%s'" % d['station'],
            "restr_typ='%s'" % d['restr_typ'],
            "restr_subtype='%s'" % d['restr_subtype'],
            "ac_qual='%s'" % d['ac_qual'])))) == 0:
            ops.append(fixrunner.createop('apt_restrictions', 'N', d))
        else:
            print 'Entry already exists'


    return ops


fixit.program = 'sascms-5172.py (%s)' % __version__


if __name__ == '__main__':
    fixit()

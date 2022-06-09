"""
* SASCMS-5403: Add new entries in leave_entitlement for norwegian crew
"""

import adhoc.fixrunner as fixrunner
import os
from AbsTime import AbsTime
import pdb

__version__ = '1'

#@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    new_entries = [{'cat':'C', 'base':'TRD', 'company':'BU', 'account':'F7', 'entdate': int(AbsTime('01Jan2013'))/(24*60), 
      'transactiondate':int(AbsTime('01Jan2013'))/(24*60), 'amount': 0, 'inadvance':True},
      {'cat':'C', 'base':'TRD', 'company':'SK', 'account':'F7', 'entdate': int(AbsTime('01Jan2013'))/(24*60), 
      'transactiondate':int(AbsTime('01Jan2013'))/(24*60), 'amount': 0, 'inadvance':True},
      {'cat':'C', 'base':'TRD', 'company':'SK', 'account':'VA', 'entdate': int(AbsTime('01Jan2013'))/(24*60), 
      'transactiondate':int(AbsTime('01Jan2013'))/(24*60), 'amount': 4200},
      {'cat':'C', 'base':'TRD', 'company':'BU', 'account':'VA', 'entdate': int(AbsTime('01Jan2013'))/(24*60), 
      'transactiondate':int(AbsTime('01Jan2013'))/(24*60), 'amount': 4200},
      
      {'cat':'C', 'base':'SVG', 'company':'BU', 'account':'F7', 'entdate': int(AbsTime('01Jan2013'))/(24*60), 
      'transactiondate':int(AbsTime('01Jan2013'))/(24*60), 'amount': 0, 'inadvance':True},
      {'cat':'C', 'base':'SVG', 'company':'SK', 'account':'F7', 'entdate': int(AbsTime('01Jan2013'))/(24*60), 
      'transactiondate':int(AbsTime('01Jan2013'))/(24*60), 'amount': 0, 'inadvance':True},
      {'cat':'C', 'base':'SVG', 'company':'SK', 'account':'VA', 'entdate': int(AbsTime('01Jan2013'))/(24*60), 
      'transactiondate':int(AbsTime('01Jan2013'))/(24*60), 'amount': 4200},
      {'cat':'C', 'base':'SVG', 'company':'BU', 'account':'VA', 'entdate': int(AbsTime('01Jan2013'))/(24*60), 
      'transactiondate':int(AbsTime('01Jan2013'))/(24*60), 'amount': 4200},
      
      {'cat':'C', 'base':'OSL', 'company':'BU', 'account':'F7', 'entdate': int(AbsTime('01Jan2013'))/(24*60), 
      'transactiondate':int(AbsTime('01Jan2013'))/(24*60), 'amount': 0, 'inadvance':True},
      {'cat':'C', 'base':'OSL', 'company':'SK', 'account':'F7', 'entdate': int(AbsTime('01Jan2013'))/(24*60), 
      'transactiondate':int(AbsTime('01Jan2013'))/(24*60), 'amount': 0, 'inadvance':True},
      {'cat':'C', 'base':'OSL', 'company':'SK', 'account':'VA', 'entdate': int(AbsTime('01Jan2013'))/(24*60), 
      'transactiondate':int(AbsTime('01Jan2013'))/(24*60), 'amount': 4200},
      {'cat':'C', 'base':'OSL', 'company':'BU', 'account':'VA', 'entdate': int(AbsTime('01Jan2013'))/(24*60), 
      'transactiondate':int(AbsTime('01Jan2013'))/(24*60), 'amount': 4200},
      ]


    for entry in new_entries:
        if len(fixrunner.dbsearch(dc, 'leave_entitlement', 
                    "cat='%s' AND base='%s' AND company='%s' AND account='%s' AND entdate='%s'" % (entry['cat'],
                                                                                                    entry['base'],
                                                                                                    entry['company'],
                                                                                                    entry['account'],
                                                                                                    entry['entdate']))) == 0:
                                                                                               
            op = fixrunner.createOp('leave_entitlement', 'N', entry)
            ops.append(op)
        else:
            print "Entry with cat='%s' AND base='%s' AND company='%s' AND account='%s' AND entdate='%s' already exists" % (entry['cat'],
                                                                                                    entry['base'],
                                                                                                    entry['company'],
                                                                                                    entry['account'],
                                                                                                    entry['entdate'])



    return ops


fixit.program = 'sascms-5403.py (%s)' % __version__


if __name__ == '__main__':
    fixit()

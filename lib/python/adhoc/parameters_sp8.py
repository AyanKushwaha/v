

"""
This file adds parameters to the database.
Parameters are added to the tables property_set and property.
We will create a new version of this file for each delivery where this is needed.

Resolves parameter additions for:
CR 300
CR 404

SQL> desc property_set
 Name                                      Null?    Type
 ----------------------------------------- -------- ----------------------------
 REVID                                     NOT NULL NUMBER(10)
 DELETED                                   NOT NULL CHAR(1 CHAR)
 PREV_REVID                                NOT NULL NUMBER(10)
 NEXT_REVID                                NOT NULL NUMBER(10)
 BRANCHID                                  NOT NULL NUMBER(10)
 ID                                        NOT NULL VARCHAR2(30 CHAR)
 SI                                                 VARCHAR2(200 CHAR)
 
SQL> desc property
 Name                                      Null?    Type
 ----------------------------------------- -------- ----------------------------
 REVID                                     NOT NULL NUMBER(10)
 DELETED                                   NOT NULL CHAR(1 CHAR)
 PREV_REVID                                NOT NULL NUMBER(10)
 NEXT_REVID                                NOT NULL NUMBER(10)
 BRANCHID                                  NOT NULL NUMBER(10)
 ID                                        NOT NULL VARCHAR2(30 CHAR)
 VALIDFROM                                 NOT NULL NUMBER(10)
 VALIDTO                                            NUMBER(10)
 VALUE_REL
 VALUE_ABS
 VALUE_INT
 VALUE_STR
 VALUE_BOOL
 SI                                                 VARCHAR2(200 CHAR)
 
"""




import fixrunner
import datetime
import RelTime
import AbsTime


__version__ = '2010-06_01'

validstart = int(AbsTime.AbsTime('1Jul2010'))
validto =  int(AbsTime.AbsTime('31Dec2035'))

bl_start_rel = int(RelTime.RelTime('15:00'))

property_set = ({'id':'max_sectors_fdp_fd_skd',
                 'si':'Max active sectors in extended FDP for SKD'},
                {'id':'max_sectors_fdp_fd_skn',
                 'si':'Max active sectors in extended FDP for SKN'},
                {'id':'max_sectors_fdp_fd_sks',
                 'si':'Max active sectors in extended FDP for SKS'},
                {'id':'max_sectors_fdp_fd_other',
                 'si':'Max active sectors in extended FDP for others'},
                {'id':'bl_day_resched_limit_skn',
                 'si':'BL day resched limit SKN'})

property  = ({'id':'max_sectors_fdp_fd_skd',
              'validfrom':validstart,
              'validto':validto,
              'value_int': 6,
              'si':'Max active sectors in extended FDP for SKD'},
             {'id':'max_sectors_fdp_fd_skn',
              'validfrom':validstart,
              'validto':validto,
              'value_int': 3,
              'si':'Max active sectors in extended FDP for SKN'},
             {'id':'max_sectors_fdp_fd_sks',
              'validfrom':validstart,
              'validto':validto,
              'value_int': 6,
              'si':'Max active sectors in extended FDP for SKS'},
             {'id':'max_sectors_fdp_fd_other',
              'validfrom':validstart,
              'validto':validto,
              'value_int': 6,
              'si':'Max active sectors in extended FDP for others'},
             {'id':'bl_day_resched_limit_skn',
              'validfrom':validstart,
              'validto':validto,
              'value_rel': bl_start_rel,
              'si':'BL day resched limit SKN'})

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    property_set_ops = [
        fixrunner.createOp('property_set', 'N', this_property_set)
	for this_property_set in property_set
        ]

    property_ops = [
        fixrunner.createOp('property', 'N', this_property)
        for this_property in property
        ]

    op_list =  property_set_ops + property_ops
    return op_list

fixit.program = 'parameters_sp8.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



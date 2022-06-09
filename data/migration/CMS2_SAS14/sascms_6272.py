

"""
This file adds parameters to the database.
Parameters are added to the tables property_set and property.
We will create a new version of this file for each delivery where this is needed.

Resolves parameter additions for SASCMS-6272

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




import adhoc.fixrunner as fixrunner
import datetime
import RelTime
import AbsTime


__version__ = '2014-02_03'

validstart = int(AbsTime.AbsTime('1Jan2011'))
validto =  int(AbsTime.AbsTime('31Dec2035'))

buffer_limit_rel = int(RelTime.RelTime('2:00'))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    op_list = []
    
    op_list.append(fixrunner.createOp('property_set', 'N', {
        'id':'subq_duty_time_7_days_buffer',
        'si':'Max duty time in 7 days for early warning'
    }))

    op_list.append(fixrunner.createOp('property_set', 'N', {
        'id':'subq_duty_time_28_days_buffer',
        'si':'Max duty time in 28 days for early warning'
    }))

    op_list.append(fixrunner.createOp('property_set', 'N', {
        'id':'subq_block_time_calendar_year_buffer',
        'si':'Max block time in calendar year for early warning'
    }))

    op_list.append(fixrunner.createOp('property', 'N', {
        'id':'subq_duty_time_7_days_buffer',
        'validfrom':validstart,
        'validto':validto,
        'value_rel': buffer_limit_rel,
        'si':'Max duty time in 7 days for early warning'
    }))

    op_list.append(fixrunner.createOp('property', 'N', {
        'id':'subq_duty_time_28_days_buffer',
        'validfrom':validstart,
        'validto':validto,
        'value_rel': buffer_limit_rel,
        'si':'Max duty time in 28 days for early warning'
    }))

    op_list.append(fixrunner.createOp('property', 'N', {
        'id':'subq_block_time_calendar_year_buffer',
        'validfrom':validstart,
        'validto':validto,
        'value_rel': buffer_limit_rel,
        'si':'Max block time in calendar year for early warning'
    }))

    return op_list

fixit.program = 'sascms_6272.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



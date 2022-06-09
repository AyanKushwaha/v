

"""
This file adds a comparer type to the database, table leave_comparer_set.
Jira is SKCMS-3

Table LEAVE_COMPARER_SET
REVID		NUMBER(10,0)		No		1	
DELETED		CHAR(1 CHAR)		No		2	
PREV_REVID	NUMBER(10,0)		No		3	
NEXT_REVID	NUMBER(10,0)		No		4	
BRANCHID	NUMBER(10,0)		No		5	
NAME		VARCHAR2(20 CHAR)	No		6	
SI		VARCHAR2(200 CHAR)	Yes		7	

 
"""




import adhoc.fixrunner as fixrunner


__version__ = '2014-08_15_'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    op_list = []
    
    op_list.append(fixrunner.createOp('leave_comparer_set', 'N', {
        'name':'VACNUM',
        'si':'Explicit vacation priority number'
    }))

    return op_list

fixit.program = 'skcms_3.py (%s)' % __version__

if __name__ == '__main__':
    fixit()





"""
Resolves CR 404.

Add an agreement called 'bl_days_skn_cc' valid from 01Feb2010 to the table 
'agreement_validity'

SQL> desc agreement_validity
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
 SI                                                 VARCHAR2(200 CHAR)
 
"""

import fixrunner
import datetime


__version__ = '2010-04-15'

# Time management stuff
EPOCH = datetime.datetime(1986, 1, 1)

#def to_dave_time(dt):
#    """Return now as DAVE time."""
#    timestamp = dt - EPOCH
#    return timestamp.days * 1440 + timestamp.seconds / 60
    
def to_dave_date(dt):
    """Return now as DAVE date."""
    timestamp = dt - EPOCH
    return timestamp.days
    
validstart = to_dave_date(datetime.datetime(2010, 7, 1))
validto = to_dave_date(datetime.datetime(2011, 1, 1))



agreement_validity = {'id':'bl_days_skn_cc',
                      'validfrom':validstart,
                      'validto':validto,
                      'si':'BL day for SKN CC CR404'}

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    return [
        fixrunner.createOp('agreement_validity', 'N', agreement_validity),
    ]

fixit.program = 'cr404.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



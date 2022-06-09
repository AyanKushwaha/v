#
#$Header:$
#
__version__ = "$Revision:$"
"""
dummt_data_repo
Module for doing:

Holding example response xml-strings!
@date:08Feb2012
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""

import os
import interbids.rostering.jcr_to_crewportal

def get_trips(*args, **kwds):

    return _get_trips_xml()


def get_all_trips(*args, **kwds):
     #return _get_tripss_xml()     
    return get_trips()

def get_rosters(*args, **kwds):
    #return _get_rosters_xml()  
    return _get_rosters_xml()

def _get_trips_rave():
    """
    use acual code
    """
    ret = jcr_to_crewportal.get_all_trips()
   # print ret
    return ret

def _get_rosters_rave():
    ret = jcr_to_crewportal.get_rosters('15459')
    ret = ret.replace('crewid="15459"',
                      'crewid="ch"')
    return ret    

def _get_trip_xml():
    """
    Return a dummy xml of one trip!
    Copied from file:
    /carm/proj/skcms/pergr_users/sk_cms2_bid5_user_2/current_carmdata/EXPORT/INTERBIDS/trip_data_20120203_1043.xml
    """
    file_name = os.path.join(os.environ.get('CARMDATA'),
                             'EXPORT',
                             'INTERBIDS',
                             'trip_data_20120203_1043.xml')
    fd = None
    ret = []
    try:
        fd = open(file_name)
        rows = fd.readlines()
        return ''.join(rows)
    finally:
        if fd is not None:
            fd.close()
            

def _get_rosters_xml():
    """
    Return dummy pre-assigmments
    Copied from file
    /carm/documents/Customer/Projects/SAS_IB5/Implementation/datasource/preassignments/preassigments.xml

    """
    file_name = '/carm/documents/Customer/Projects/SAS_IB5/Implementation/datasource/preassignments/preassigments.xml'
    fd = None
    ret = []
    try:
        fd = open(file_name)
        rows = fd.readlines()
        for ix in range(0, len(rows)):
            if 'crewid' in rows[ix] :
                rows[ix]=rows[ix].replace('"de"','"ch"')        
        return ''.join(rows)
    finally:
        if fd is not None:
            fd.close()
  

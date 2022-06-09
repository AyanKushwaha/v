#!/usr/bin/env python

# The purpose of this script is to fix some of delete objects in crew_user_filter table that have validto to too far into the future
# The validto value for those records are set to validfrom + 1
# By doing this JMP does not refreshed in old deleted record for example from crew_user_filter --> published_roster. And that will prevent refrence not found error

from carmensystems.dave import baselib, dmf

import os


TABLE_NAME = 'crew_user_filter'

CREW_IDS = [
    '42886',
    '18825',
    '44764',
    '26787',
    '27966',
    '39668'
]


def main():
    print "START"
    conn = create_connection()
    try:
        old_recs = read_old_records(conn)        
        print "old_recs:\n" , 
        for old_rec in old_recs:
            print old_rec		
        fix_record_values(old_recs)        
        add_recs = get_add_records(old_recs)
        del_recs = get_delete_records(old_recs)

        write_records(conn, add_recs, 'Revived deleted crew_user_filter records')
        write_records(conn, del_recs, 'Deleted revived crew_user_filter records')
    finally:
        conn.close()

def create_connection():
    DB_SCHEMA = os.getenv('DB_SCHEMA')    
    DB_CONN = os.getenv('DB_URL')

    conn = dmf.EntityConnection()
    conn.open(DB_CONN, DB_SCHEMA)
    conn.setProgram('sks_191_fix_crew_user_filter.py')
    return conn


def read_old_records(conn):
    rev_filter = create_revision_filter()
    filt, params = create_filter()
    spec = conn.getEntitySpec(TABLE_NAME)

    recs = []
    conn.beginReadTxn()
    try:
        conn.setSnapshot(rev_filter)
        conn.setSelectParams(params)
        conn.select(TABLE_NAME, filt)

        for rec in conn.iterRecordsAsDict(spec):
            recs.append(rec)

        return recs
    finally:
        conn.endReadTxn()


def create_revision_filter():
    rev_filter = baselib.RevisionFilter()
    rev_filter.withDeleted(True)
    return rev_filter


def create_filter():
    assert len(CREW_IDS) < 100

    params = baselib.Result(len(CREW_IDS))
    crew_ins = []

    for i, crew_id in enumerate(CREW_IDS):
        params.setString(i, crew_id)
        crew_ins.append('%:{0}'.format(i + 1))

    filt = baselib.Filter(TABLE_NAME)
    filt.where2('crew', 'IN ({0})'.format(', '.join(crew_ins)))
    filt.where2('deleted', "= 'Y'")
    filt.where2('val', "= 'MISMATCH'")
    filt.where2('validto', '> 16829380')

    return filt, params


def fix_record_values(old_recs):
    for rec in old_recs:
        rec['validto'] = rec['validfrom'] + 1


def get_add_records(old_recs):
    add_recs = []
    for old_rec in old_recs:
        add_rec = old_rec.copy()
        add_rec['deleted'] = 'N'
        add_rec['revid'] = baselib.RevisionNew
        add_recs.append(add_rec)
    return add_recs


def get_delete_records(old_recs):
    del_recs = []
    for old_rec in old_recs:
        del_rec = old_rec.copy()
        del_rec['deleted'] = 'Y'
        del_rec['revid'] = baselib.RevisionNone
        del_recs.append(del_rec)
    return del_recs


def write_records(conn, recs, msg):
    spec = conn.getEntitySpec(TABLE_NAME)

    conn.beginWriteTxn()
    try:
        entity = conn.openEntity(TABLE_NAME)
        for rec in recs:
            entity.update(rec, spec)
            conn.writeEntity()
        conn.flushEntity()

        conn.commit(msg)
    except:
        conn.rollback()
        raise


main()

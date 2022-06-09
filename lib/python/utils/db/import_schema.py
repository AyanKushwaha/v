import subprocess
import cx_Oracle
import json
from string import Template
from subprocess import call
import argparse
import os

########## Parse command line and JSON arguments ###########
parser = argparse.ArgumentParser(description='Imports CMS Database dumps')
parser.add_argument('source_schema', metavar='s', help='The name of the source schema')
parser.add_argument('dest_schema', metavar='d', help='The name of the destination schema')
parser.add_argument('dumpfile', metavar='f', help='The name of the dumpfile(s), without the _<n>.dmp ending')
parser.add_argument('parallel', metavar='p', help='The number of parallel dumpfiles to import')
args = vars(parser.parse_args())

argfile = open(os.environ['CARMSYSTEMNAME'] + '.json', 'r')
args.update(json.load(argfile))

if 'date' in args:
    args['time'] = str(args['date'] * 1440)
    args['timethreemonthsbefore'] = str((args['date'] - 90) * 1440)
    args['datesixdaysbefore'] = str(args['date'] - 6)
    args['date'] = str(args['date'])

########## Set up parameters ###########
if(args['mode'] == 'stripped'):
    parfile_templates = ['stripped_import_data.template',
                         'stripped_import_dave_filters.template',
                         'stripped_import_dave_revision.template',
                         'stripped_import_dave_tables.template',
                         'stripped_import_indexes.template',
                         'stripped_import_metadata.template']
else:
    parfile_templates = ['full_import_all.template']
    

parfiles = dict([(f, '/tmp/'+f.split('.')[0]+'_'+args['dest_schema']+'.par') for
                f in parfile_templates])

sys_connect = args['sys_login']+'@'+args['db_url']
user_connect = args['dest_schema']+'/'+args['dest_schema']+'@'+args['db_url']

#The new schema is created through a sequence
#of statements creating the user and granting permissions
def _schema_creation_statements():
    with open('create_schema.template') as f:
        s = f.read()
        s = Template(s).substitute(args)
    return map(lambda v: v.strip(), s.strip().split(';')[:-1])

#Todo check success/fail
def create_schema():
    print "create_schema"
    connection = cx_Oracle.connect(sys_connect)
    cursor = connection.cursor()
    for s in _schema_creation_statements():
        print s
        cursor.execute(s)
    connection.commit()
    connection.close()

def create_par_files():
    print "Creating parameter files"
    for tn in parfile_templates:
        with open(tn) as f:
            s = f.read()
        with open(parfiles[tn], 'w') as f:
            f.write(Template(s).substitute(args))
            print parfiles[tn]
    print "Done creating parameter files"

def db_import(connection_string, parfile):
    print "importing", parfile
    call(['impdp', connection_string, 'PARFILE='+parfile])
    
def import_metadata():
    db_import(sys_connect, parfiles['stripped_import_metadata.template'])

def import_dave_filters():
    db_import(sys_connect, parfiles['stripped_import_dave_filters.template'])

def import_data():
    db_import(sys_connect, parfiles['stripped_import_data.template'])

def import_dave_revision_data():
    db_import(sys_connect, parfiles['stripped_import_dave_revision.template'])

def import_dave_tables():
    db_import(sys_connect, parfiles['stripped_import_dave_tables.template'])

def import_indexes():
    db_import(sys_connect, parfiles['stripped_import_indexes.template'])
    
def import_all():
    db_import(sys_connect, parfiles['full_import_all.template'])

def create_index_on_revid():
    connection = cx_Oracle.connect(user_connect)
    cursor = connection.cursor()
    cursor.execute('CREATE INDEX revision_imp ON dave_updated_tables(revid)')
    connection.commit()
    connection.close()

def drop_index_on_revid():
    connection = cx_Oracle.connect(user_connect)
    cursor = connection.cursor()
    cursor.execute('DROP INDEX revision_imp')
    connection.commit()
    connection.close()

def recreate_dave_updated_tables():
    with open('data_tables') as f:
        tables = map(lambda s:s.strip().lower(), f.readlines())

    insert_statement = "INSERT INTO dave_updated_tables (revid, tablename, branchid) SELECT DISTINCT revid, '%s', 1 FROM %s"

    print "Start fixing dave_updated_tables"
    connection = cx_Oracle.connect(user_connect)

    for t in tables:
        s = insert_statement%(t, t)
        print "running", s
        cursor = connection.cursor()
        cursor.execute(s)
        print cursor.rowcount, "rows created"

    connection.commit()
    connection.close()

#Needed to make reference rosters work
def insert_magic_revision():
    print "Insert magic dave revision"
    insert_statement = "INSERT INTO dave_revision (revid, commitid, cliprogram, clihost, cliuser, committs, remark) VALUES (0, 999999999, 'GenericEntityHandler', 'h1crm23a', 'carmadm', 743687866, 'schema creation')"
    connection = cx_Oracle.connect(user_connect)
    cursor = connection.cursor()
    cursor.execute(insert_statement)
    print cursor.rowcount, "rows created"
    connection.commit()
    connection.close()


#TODO
#read parameters
#setup mappings

create_schema()
create_par_files()
if(args['mode'] == 'stripped'):
    import_metadata()
    import_dave_filters()
    import_data()
    recreate_dave_updated_tables()
    create_index_on_revid()
    import_dave_revision_data()
    insert_magic_revision()
    drop_index_on_revid()
    import_dave_tables()
    import_indexes()
else:
    import_all()

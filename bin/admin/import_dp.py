#!/usr/bin/env python
from argparse import ArgumentParser
import os
import sys
import logging
import datetime
import subprocess 
import calendar


test_env = "/opt/Carmen/CARMUSR/PROD_TEST"
prod_env = "/op/Carmen/CARMUSR/PROD"




# export oracle environment variables if they dont exist
def add_oracle_env_vars():
    if not os.environ.has_key("ORACLE_HOME"):
        logging.info("Setting environment variables for oracle...")
    	if 'devdb01' in os.uname()[1]:
            os.environ['ORACLE_HOME'] = "/u01/app/grid/12.1.0"
        else:
            # os.environ['ORACLE_HOME'] = "/u01/app/oracle/product/11.2.0/dbhome_1"
            # os.environ['ORACLE_HOME'] = "/u01/app/product/12.1.0/oracle"
            
            os.environ['PATH'] = "%s/bin:%s" % (os.getenv('ORACLE_HOME'), os.getenv('PATH'))
            logging.info('Added environment variables for oracle')




def parse_params():

    args = ArgumentParser(description="Oracle data pump")
    args.add_argument("-c", "--connection", help="Database connection string")
    args.add_argument("-d", "--dumpfile", required=True, help="Name of the dumpfile") 
    args.add_argument("-l", "--logfile", help="Name of the logfile")
    args.add_argument("-p", "--directory", help="Oracle directory name")
    args.add_argument("-P", "--parallel", default=1, help="specify number of parallel processes")
    args.add_argument("-v", "--verbose", action='store_true', help="Oracle directory name")
    args.add_argument("-t", "--type", default='live', help="Type of schema")
    args.add_argument("-T", "--targetschema", help="Target schema name")
    args.add_argument("-S", "--sourceschema", help="Source schema name")
    args._optionals.title = "Flag arguments:"
    return args.parse_args()


def get_month():
    ctime = datetime.date.today()
    if ctime.day >= 15:
        if ctime.month == 12:
            return "jan"
        return calendar.month_abbr[ctime.month +1].lower()
    return calendar.month_abbr[ctime.month].lower()



def get_env():
    if os.path.exists(test_env):
        return "test"
    elif os.path.exists(prod_env):
        return "prod"
    else:
        return "dev"




def db_connect(client):
    try:
        import cx_Oracle as oracle
        logging.info("Connecting to %s..." % client)
        logging.debug("Connecting to %s...." % client)
        connection = oracle.connect(client);
    except:
        logging.error("User password was not changed. Change it manually")
        exit(0)
    logging.info("Successfully connected to %s" % client)
    logging.debug("Successfully connected to %s" % client)
    return connection




def change_user_password(connection, username):
    query = "ALTER USER %s IDENTIFIED BY %s" % (username.upper(), username.lower())
    logging.debug("Exectuting %s" % query);
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        logging.debug("Password for %s is changed" % username)
    except:
        logging.error("Could not execute %s" % query)
        exit(0)
    finally:
        logging.debug("Closing the connection...")
	connection.close()
        logging.debug("Connection closed")
    logging.debug("Successfully executed %s" % query)
    

def get_env_var(env_key):
    env = os.environ.get(env_key, "null")

    if env == 'null':
        logging.error("%s was not found in environment" % env_key)
        exit(1)
    logging.debug("Successfully fetch %s from environment" % env_key)
    return env



def run():
    add_oracle_env_vars()
    parser = parse_params()
    
    DIR = "EXP"
    
    ctime = datetime.datetime.utcnow()
    time_f = ctime.strftime("%Y%m%d_%H%M%SUTC")

    if not parser.directory:
        parser.directory = DIR
    

    if parser.verbose:
      loglevel = logging.DEBUG
    else:
      loglevel = logging.INFO

    logging.basicConfig(level=loglevel)

    if not parser.connection:
        if parser.type.lower() == "live":
            parser.connection = get_env_var("DB_ADM_URL")[7:]
        else:
            parser.connection = get_env_var("DB_ADM_URL_HISTORY")[7:]

    if not parser.sourceschema:
        if parser.dumpfile.find('__') == -1:
            exit(-1)
        parser.sourceschema =  parser.dumpfile[parser.dumpfile.find('_')+1 : parser.dumpfile.find("__")]

    if not parser.sourceschema:
        logging.error("Bad name of dumpfile: %s" % parser.dumpfile)
        exit(1)

    if not parser.logfile:
        parser.logfile = "Carmen_import_db_%s_%s.log" % (parser.sourceschema, time_f)
        
    if parser.sourceschema.find('live') != -1:
        schema_type = 'live'
    elif parser.sourceschema.find('history') != -1:
        schema_type = "history"
    else:
        schema_type = "rep"
    job = "imp_%s_%s" % (schema_type, time_f[:-3])

    if not parser.targetschema or len(parser.targetschema) == 0:
        target = "cms_%s_%s_%s" % (get_env(), get_month(), parser.type)
    else:
        target = parser.targetschema
    parser.connection = parser.connection.replace('cmstest-scan', os.uname()[1].split('.')[0] , 1)
    params = (parser.connection, parser.directory, parser.dumpfile, parser.logfile, parser.sourceschema, target, job, parser.parallel)
    cmd = "%s DIRECTORY=%s DUMPFILE=%s LOGFILE=%s REMAP_SCHEMA=%s:%s JOB_NAME=%s PARALLEL=%s TABLE_EXISTS_ACTION=REPLACE "
    cmd = cmd % params
    print "impdp " + cmd 
    logging.info("Schema import started...")
    #  os.system(cmd)
    db_imp = subprocess.Popen(["impdp", cmd], stdout=subprocess.PIPE)
    if db_imp.wait() != 0:
        logging.error("Not all data got imported. Probably there are some issues in the database to run the following command")
        logging.error(cmd)
        exit(1)
    logging.info("%s was successfully imported!" % parser.sourceschema)
    logging.info("Change %s password in the oracle database" % target)
    conn = db_connect(parser.connection)
    change_user_password(conn, target)



if __name__ == "__main__":
    run()

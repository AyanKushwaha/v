#!/usr/bin/env python



import time
from argparse import ArgumentParser
import os
import logging
import subprocess
from datetime import datetime


# export oracle environment variable and path
def add_oracle_env_variable():
    if not os.environ.has_key("ORACLE_HOME"):
        logging.info("Setting environment variables for oracle...")
    	if 'devdb01' in os.uname()[1]:
            os.environ['ORACLE_HOME'] = "/u01/app/grid/12.1.0"
    	else:
            # os.environ['ORACLE_HOME'] = "/u01/app/oracle/product/11.2.0/dbhome_1"
            # os.environ['ORACLE_HOME'] = "/u01/app/product/12.1.0/oracle" 
            os.environ['PATH'] = "%s/bin:%s" % (os.environ['ORACLE_HOME'], os.environ["PATH"])
            logging.info("Added environment variables for oracle")


# parse the command line parameters
def add_cmd_params():
    args = ArgumentParser(description="Export data from the database")
    args.add_argument("-c", "--connection", help="database username and password to setup a conection to the database")
    args.add_argument("-s", "--sourceschema", help="Specify schema to export")
    args.add_argument("-d", "--dumpfile",  help="Name of the dump file")
    args.add_argument("-t", "--type",  help="Type of the schema [live/history]")
    args.add_argument("-l", "--logfile",   help="Name of the log file")
    args.add_argument("-p", "--parallel", default=1, help="specify number of parallel processes")
    args.add_argument("-j", '--job', help="Type the name of the job")
    args.add_argument("-v", "--version", help="Specify the version of oracle database")
    args.add_argument("-o", "--directory", default='EXP', help="Specify the data pump directory")
    args.add_argument("--nocompression", default=True, action="store_true", help="Set compression to none")
    args.add_argument("--verbose", default=False, action="store_true", help="Set logging mode")
    args._optionals.title = "Flag arguments"
    return args.parse_args()


def get_env_var(env_key):
    env = os.environ.get(env_key, "null")
  
    if env == 'null':
        logging.error("%s was not found in environment" % env_key)
        exit(1)
    logging.debug("Successfully fetch %s from environment" % env_key)
    return env

# main loop of expdp
def run():
    add_oracle_env_variable()

    current_time = datetime.utcnow()
    f_t =  current_time.strftime("%Y-%m-%d %H:%M:%S")
    ftime = current_time.strftime("%Y%m%d_%H%M%SUTC") 
    #DO NOT CHANGE THE FORMAT OF FLASHBASH.
    flashback="\"TO_TIMESTAMP('%s', 'YYYY-MM-DD HH24:MI:SS')\"" % f_t

   

    parser = add_cmd_params()



    if parser.dumpfile:
        dump_file = parser.dumpfile + "_%s__%s_%%U.dmp"
        log_file = parser.dumpfile + "_%s_%s.log"
    else:
        dump_file = "Carmen_%s__%s_%%U.dmp"
        log_file = "Carmen_%s_%s.log"
  
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
        if parser.type:
            if parser.type == "live":
                parser.sourceschema = get_env_var("DB_SCHEMA")
            elif parser.type == "history":
                parser.sourceschema = get_env_var("DB_SCHEMA_HISTORY")
            else:
                logging.error("Worng type of schema: %r" % parser.type)
                logging.error("Available type of schema are live and history")
                exit(1)
        else:
            parser.sourceschema = get_env_var("DB_SCHEMA")


     
    parser.dumpfile = dump_file % (parser.sourceschema, ftime)
    parser.logfile = log_file % (parser.sourceschema, ftime)


    if not parser.job:
	if parser.sourceschema.find('live') != -1:
            schema_type = 'live'
	elif parser.sourceschema.find('history') != -1:
	    schema_type = "history"
        else:
	    schema_type = "rep"
        ##  schema_type = 'live' if parser.schema.find('live') != -1 else 'history'
        parser.job = "exp_%s_%s" % (schema_type, ftime[:-3])

    parser.connection = parser.connection.replace('cmstest-scan', os.uname()[1].split('.')[0] , 1)
    params = (parser.connection, parser.sourceschema, parser.directory, parser.dumpfile, parser.logfile, parser.parallel, parser.job, "STATISTICS", flashback)
    cmd = "%s SCHEMAS=%s DIRECTORY=%s DUMPFILE=%s LOGFILE=%s PARALLEL=%s JOB_NAME=%s EXCLUDE=%s FLASHBACK_TIME=%s " % params 
    if parser.version:
        cmd = cmd + " VERSION=%s" % parser.version    
    if parser.nocompression:
	cmd = cmd + " COMPRESSION=NONE" 
    print "expdp " + cmd
    logging.info("Schema export started...")
    db_exp = subprocess.Popen(["expdp", cmd], stdout=subprocess.PIPE)
    if db_exp.wait() != 0:
        logging.error("Not all data was exported. Probably there are some issues in the database to run the following command")
        logging.error(cmd)
        exit(1)
    logging.info("%s was successfully exported!" % parser.sourceschema)
    logging.info("Exported schema")

if __name__ == "__main__":
    run()

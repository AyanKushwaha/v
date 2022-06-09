#!/usr/bin/env python3

from __future__ import print_function

import logging
import signal
import time
import pprint
import sys
import os
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from subprocess import PIPE, STDOUT, Popen

import cx_Oracle as oc

__author__ = "Mahdi Abdinejadi <mahdi.abdinejadi@hiq.se>"
__version__ = "0.0.1"


"""
This module list database user sessions, and connected processes.
This script can be set to kill database connected processes on the host that script is executing or
simply print the list of session in STDOUT/json/csv file.
"""


def kill_process(pid):
    """ This function kill unix like operating system process by pid

    This function uses os module to kill process with signal 9 kill signal in safe way.

    """
    try:
        os.kill(int(pid), signal.SIGKILL)
        logging.debug("Killed pid %s with %s signal" % (pid, str(signal.SIGKILL)))
    except OSError as e:
        logging.error("OS error to kill pid %s: %s" % (pid, e.strerror))
    except:
        logging.error("Can not kill pid %s" % pid)


def get_db_sessions(connection, schema=""):
    """ This function connect to database and query for active sessions list

    This function list all active sessions for the set schema or all schemas that have name like 'SK', 'CMS',
    and 'CREWWEB'. The result of query to database would be the return. If connection to database failed,
    it will exit the script process with exit code 1 / Error.

    Args:
        schema (str): schema name of target query if empty all schema would be query
        connection (str): connection string containing username/password@hotname:PortNumnber/ServiceName

    Returns:
        sessions (list): List dictionaries containing schema_name, id, created, sessions as key
        [{"schema": schema , "id": user_id, "created": created, "sessions": [
            {"osuser": OSUSER, "machine": MACHINE, "process": PROCESS, "module": MODULE }]}]


    """

    logging.debug("cx_oracle version: %s" % oc.version)
    try:
        con = oc.connect(connection)
        logging.debug("Oracle client is established with: %s" % connection)
    except oc.DatabaseError as e:
        err, = e.args
        logging.error("Oracle connection error code: " + err.code)
        logging.error("Oracle connection error message: " + err.message)
        exit(1)
    except:
        logging.error("Oracel connection failed!!!")
        exit(1)
    cur = con.cursor()
    if schema == "":
        cur.execute("SELECT username, user_id, created FROM all_users WHERE USERNAME LIKE 'SK%' OR USERNAME LIKE 'CMS%' OR USERNAME LIKE 'CREWWEB%' ")
    else:
        logging.debug("query is SELECT username, user_id, created FROM all_users WHERE USERNAME = '" + schema + "'")
        cur.execute("SELECT username, user_id, created FROM all_users WHERE USERNAME = '" + schema + "'")

    db_schemas = []
    db_results = []
    for (username, user_id, created) in cur:
        db_schemas.append(
            {"schema": username, "id": str(user_id), "created": str(created)})
        logging.debug("schema is: %s, id is: %s, created is: %s" %
                      (username, user_id, created))

    for item in db_schemas:
        session_query = "SELECT username, OSUSER, MACHINE, PROCESS, MODULE FROM v$session WHERE USERNAME = '" + \
            item["schema"] + "' "
        cur.execute(session_query)
        logging.debug("DB query is: %s" % session_query)
        sessions = []
        for (username, OSUSER, MACHINE, PROCESS, MODULE) in cur:
            session = {"osuser": OSUSER, "machine": MACHINE,
                "process": PROCESS, "module": MODULE}
            sessions.append(session)
        # Sort the session by machine name
        item["sessions"] = sorted(sessions, key=lambda k: k["machine"])
        db_results.append(item)
        logging.info("Schema: %s created at: %s number of sessions: %s" % (item.get("schema"), item.get("created"), len(item.get("sessions"))))
    cur.close()
    con.close()
    logging.info("db_results list is populated with sessions information")
    logging.debug(pprint.pformat(db_results))
    return db_results


def execution(schema, connection, kill, list_all, output, json_stdout):
    """ This is the main execution function in this module and it get database session to show or kill

    This function call get_db_sessions to get list of schemas with their sessions. Then if list_all is True
    it will print sessions information to STDOUT. If kill is True, it will call kill_process by pids on the
    current host (Does not kill root processes).
    Note: to kill processes user must have privilage.

    Args:
        schema (str): schema name if empty string all schema would be consider
        connection (str): database connection string to db connect
        kill (bool): value to kill corresponding processes of database sessions
        list_all (bool): value to list all database schemas and number of sessions
        output (str): set output to json or csv file
        json_stdout (bool): set to true if expected to print out database sessions in json

    """

    sessions = get_db_sessions(connection=connection, schema=schema)
    if list_all:
        logging.debug("List all schemas and its sessions to stdout")
        print(pprint.pformat(sessions))
    if json_stdout:
        import json
        logging.info("print sessions to stdout with json format")
        print(json.dumps(sessions))
    if output != "":
        logging.debug("output file is: %s", output)
        if output.lower().endswith("csv"):
            import csv
            logging.debug("csv lib imported")
            try:
                csv_file = open(output, "w+")
                logging.debug("csv_file is: " + str(csv_file))
                csv_header = ["schema"] + sessions[0].get("sessions")[0].keys()
                csv_writer = csv.DictWriter(csv_file,csv_header) 
                logging.debug("csv_writer is ready: " + str(csv_writer))
                csv_writer.writerow(dict(zip(csv_header, csv_header)))
                logging.debug("csv header is written to output: %s", str(dict(zip(csv_header, csv_header))))
                for sc in sessions:
                    for se in sc['sessions']:
                        se["schema"] = sc.get("schema")
                        csv_writer.writerow(se)

                csv_file.close()
                logging.debug("csv_writer is done: " + str(csv_writer))
            except IOError as e:
                logging.error("IO error: " + e.strerror)
            except:
                logging.error("CSV writing error")
                logging.info("csv output file is created")
        elif output.lower().endswith("json"):
            import json
        logging.debug("json lib imported")
        try:
            json_file = open(output, "w+")
            logging.debug("json_file is: " + str(json_file))
            logging.debug("json string is: %s", json.dumps(sessions))
            json_file.write(json.dumps(sessions))
            json_file.close()
        except IOError as e:
           logging.error("IO error: " + e.strerror)
        except:
            logging.error("JSON writing error")
        logging.info("json output file is created")


    if kill:
        if os.getuid() == 0: # check user if have privilage
            host_name = os.uname()[1]
            logging.debug("User is privilaged to kill processes on host: %s" % host_name)
            pids = []
            for item in sessions:
                for se in item["sessions"]:
                    if se.get("machine") == host_name and se.get("osuser") != "root":
                        pids.append(se.get("process"))
            for p in set(pids):
                kill_process(p)
                logging.debug("call function to kill pid: %s" % p)
            logging.info("All database session corresponding os processes are killed at: %s" % host_name)

        else:
            logging.error("User is not privileged. Please run this command as root")
            exit(1)


def run():
    """ This function parse and check or set all variables to execute the module execution function.

    This function first set all argparser variables and then try to parse them. There are some values that need to be
    set with default values. It also initialize logging object class according to argparser values which are set by user.
    And finally, it calls the execution function with proper values.

    """
    ap = ArgumentParser(description=__doc__, formatter_class=RawDescriptionHelpFormatter)
    ap.add_argument('-s', '--schema', help='set schema name (database user)')
    ap.add_argument('-c', '--connection', help='set database connection string (if not set environment connection string will be used)')
    ap.add_argument('-k', '--kill', default=False, action='store_true',\
        help='set kill all corresponding porcess of databse session only on the script execution host')
    ap.add_argument('-l', '--listed', default=False, action='store_true',\
        help='list all database sessions and corresponding processes')
    ap.add_argument('-j', '--json', default=False, action='store_true', help='set print out result as json') 
    ap.add_argument('-o', '--output', help='set output file name and only for json or csv end the output file with .json or .csv')
    ap.add_argument('-v', '--verbos', default=False, action='store_true', help='set logging to verbos (debug level)')

    args = ap.parse_args()
    
    if args.verbos:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    output = ""
    if args.output:
        if args.output.endswith("csv") or args.output.endswith("json"):
            output = args.output
            logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)
            logging.debug("output is set to: %s", output)
        else:              
            logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel, filename=args.output, handlers=[logging.StreamHandler])
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    if args.connection:
        db_conn = args.connection
    else:
        db_conn = os.environ.get("DB_ADM_URL", "null")
        if db_conn == "null":
            logging.error("DB connection string can not be extracted from environment variables")
            exit(1)
        else:
            db_conn = db_conn.strip("oracle:")
            db_conn_splits = db_conn.split("%")
            if len(db_conn_splits) > 1:
                db_conn = db_conn_splits[0] + "/" + db_conn_splits[1].split("/")[1]
            logging.debug("DB connection is: %s", db_conn)

    if args.schema:
        schema = args.schema
    else:
        schema = ""


    logging.info("ArgumentParser is done")
    
    execution(schema=schema, connection=db_conn, kill=args.kill, list_all=args.listed, output=output, json_stdout=args.json)


def handler(signum, frame):
    """ This function handles signals

    This is simple signal handler. To check other type of signals go to:
    https://docs.python.org/2/library/signal.html#signal.getsignal


    """
    print ('Signal handler called with signal: ' + str(signum), file=sys.stderr)
    exit(1)


if __name__ == '__main__':
    """ Main function to report start and end time and run the main function run()
        Signal handler is registered here as well.
    """
    start_time = time.strftime("%c")
    signal.signal(signal.SIGINT, handler) # Register signal
    run()
    end_time = time.strftime("%c")



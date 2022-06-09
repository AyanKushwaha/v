#! /usr/bin/env python2.6

from __future__ import print_function

__author__="Mahdi Abdinejadi <mahdi.abdinejadi@hiq.se>"
__version__= "1.1"


"""
This is test script to invoke multipule rpc request toward Interbids report workers with specified time out.
"""

import traceback
import time
import os
import logging
import signal
import json
import xml.dom.minidom as mdom
from argparse import ArgumentParser, RawDescriptionHelpFormatter
# from progressbar import ProgressBar, Percentage, Bar, ETA
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool, TimeoutError, Manager
import rpc # This module is need to run this script which is located at $CARMUSR/bin/shell/rpc.py


# Global variables definition
callback_result = Manager().list() # Place holder for callback function results required for multiprocessing.
callbacks = {} # Result of call backs would be store hear from callback_result
module = os.path.basename(__file__).split('.')[0].upper() # module name of current file
logger = None # Global logger object
backend = "" # Global backend server

def config_logging(name=None, log_level=logging.ERROR, files=[]):
    """ Set up logging and pass it to global variable logger

    Simple logging configuration function.
    Args:
        name (str): unix like time stamp
        log_level (int): logging level - default value logging.ERROR
        file (list): list of file name to output logs

    Returns:
        logger (Logger): logging object
    """
    global logger
    logformat = logging.Formatter(fmt='[%(asctime)s %(name)-4s %(levelname)-8s %(funcName)s %(lineno)d] %(message)s', datefmt='%d%m%Y_%H:%M:%S')
    if name == None:
        logger = logging.getLogger()
        logger.setLevel(log_level)
        h = logging.StreamHandler()
        h.setFormatter(logformat)
        logger.addHandler(h)
    else:
        logger = logging.getLogger(name)
        logger.setLevel(log_level)
    for f in files:
        fh = logging.FileHandler(f)
        fh.setLevel(log_level)
        fh.setFormatter(logformat)
        logger.addHandler(fh)
    return logger


def csv_writer(csv_output, csv_map, csv_header):
    """ This is simple csv file writer

    This function write csv file as output.

    Args:
        csv_output (str): file name of csv file
        csv_map (list):  list of tuples which contains row of csv
        csv_header (list) : list of keys of CSV

    """
    import csv
    try:
        csv_file = open(csv_output, "w")
        logging.debug("csv_file is: " + str(csv_file))
        csv_writer = csv.DictWriter(csv_file, csv_header)
        logging.debug("csv_writer is ready: "+ str(csv_writer))
        csv_writer.writerow(dict(zip(csv_header,csv_header)))
        for i in csv_map:
            csv_writer.writerow(dict(zip(csv_header, i)))

        logging.debug("csv_writer is done: "+ str(csv_writer))
        logging.info("csv file is created")
    except IOError as e:
        logging.error("IO error: " + e.strerror)
    except:
        logging.error("csv writing error")


def to_json(json_dictionary):
    """ This simple function to dump dictionary to json string.
    Simply pass a dictionary to this function and get json string.

    Args:
        json_dictionary (dict): dictionary to converted to json formated string.

    Returns:
        json_dump (str): json_formated string
    """
    logging.info("print json_dictionary to stdout with json format")
    print(json.dumps(json_dictionary))


def callback_func(x):
    """ callback function to collect callback results 
    This function would be invoked as callback function when rpc call result returns. Then it will simply append the rpc return to callback_result list.
    
    Args:
            x (tuple): 	Rpc_call return which contains crew_id=int , status=int, time_of_execution=float, result=str
    """
    callback_result.append(x)
    logger = logging.getLogger()
    callback_result.append(x)
    logger.debug("cb_func result is: {0}".format(x))


# TODO: Document it
class AsyncFactory:
    def __init__(self, func, timeout=5, callback=None ,default_return=None ,processes=5):
        self.func = func
        self.timeout = timeout
	self.callback = callback
        self.default_return = default_return
        self.pool = Pool(processes)
        self.logger = logging.getLogger()
	self.logger.debug("func: {0}  timeout: {1}  default_return: {2}  processes: {3}".format(func.__name__, timeout, default_return, processes))


    def call_maper(self, args_list):
	self.logger.debug("args_list length is: {0} and first item is: {1}".format(len(args_list), args_list[0]))
	for a in args_list:
	    self.pool.apply_async(rpc_call, a, callback=self.callback)
	self.logger.debug("apply_async is done")

    def wait(self):
        self.pool.close()
        self.pool.join()
        self.logger.error("AsyncFactory is done.")

    def terminate(self):
        self.pool.terminate()
        self.pool.join()
        self.logger.error("AsyncFactory terminated!!!")

def get_active_crew_list(db_cursor, agreement):
    """ This function get database connection and execute query

    Simply get database connection and build respective query and execute it. Then return the result as list of ids

    Args:
        db_cursor (database cursor): Oracle database cursor object
        agreement (str): crew agreemet to filter out cabin crew or flight deck on sql query

    Returns:
        ids (list): list of ids - 5 digit integer number
    """
    query = """ select DISTINCT CREW.ID from CREW, CREW_CONTRACT, CREW_CONTRACT_SET where CREW.NEXT_REVID = 0 and CREW.DELETED = 'N'
  and CREW.RETIREMENTDATE is null and CREW.ID = CREW_CONTRACT.CREW and CREW_CONTRACT.NEXT_REVID = 0 and CREW_CONTRACT.DELETED = 'N'
  and CREW_CONTRACT_SET.DELETED ='N' and CREW_CONTRACT_SET.NEXT_REVID = 0 and CREW_CONTRACT_SET.AGMTGROUP like '{0}'
  and CREW_CONTRACT_SET.ID = CREW_CONTRACT.CONTRACT """.format(agreement)
    db_cursor.execute(query)
    ids = []
    for (id, ) in db_cursor:
        try:
            int_id = int(id)
            ids.append(int_id)
        except ValueError:
            logging.error("Error occurred during parsing id: {0} to int".format(id))
    logging.info("Crew list with agreement {0} populated with size: {1}".format(agreement, len(ids)))
    return ids


def rpc_call_wrapper(args):
    """ Simple wrapper for rpc_call in case of using map_async call
    This function get a tuple of arguments and wrap it to call the rpc_call function.
    Args:
            args (tuple):  arguments
    
    Return:
            rpc_call(): return the rpc_call(*args)
    """
    return rpc_call(*args)


def rpc_call(crew_id, timeout, crew_type="c", backend_rpc=""):
    """ This function call rpc to get result from backend report worker with time out

    This function...

    Args:
        crew_id (int): crew id
        timeout (int): rpc call time out in seconds
        crew_type (char): c for cabin crew and f for flight deck
	backend_rpc (str): backend report worker

    Return:
        Respond (tuple): 	contains crew_id=int , status=int, time_of_execution=float, result=str
                            	status (int): 0 = successful, 1 = failed with exception from rpc module, 2 = timeout, 3 = others
				backend (str) backend rpc portal
                            	result (str): 0: xml rpc respond in xml format, 1: exception, 2: timeout string
    """

    logger = config_logging(name="rpc")
    logger.info("crew_id: {0} crew_type: {1}  timeout: {2}  backend_rpc: {3}".format(crew_id, crew_type, timeout, backend_rpc))
    respond = {}
    def rpc_call_closure():
        logger = config_logging(name="closure")
        start_time = time.time()
        try:
            if backend_rpc != "":
                backend = backend_rpc
            else:
                backend = "portal_manpower_" + crew_type
            rpc_reply = rpc.get_rosters(crew_id, host=backend)
	    logger.debug("$$$ Call rpc and rpc_reply: {0} ".format(rpc_reply))
            status = 0  # Successfull
        except Exception as e:
            result = str(e)
            status = 1 # Failed
        end_time = time.time()
        time_of_execution = round (end_time - start_time, 2)
	logger.info("Respond got status: {0} and result is: {1}".format(status, rpc_reply))
	return (crew_id, status, time_of_execution, backend, rpc_reply) 

    tpool = ThreadPool(1)
    tpobj = tpool.apply_async(rpc_call_closure)
    try:
        respond = tpobj.get(timeout)
        tpool.close()
        tpool.join()
        logger.debug("result is appended to callback_result: {0}".format(respond))
        return respond
    except TimeoutError:
    	logger.error("TimoutError exception caught")
	return (crew_id, 2, timeout, backend_rpc, "TimeooutError")
    except Exception as e:
	logger.error("## Exception caught: {0}".format(str(e)))
	return (crew_id, 3, timeout, backend_rpc, e)

def execution(db_con_obj, cabin_crew, pworker, timeout, runtime, json, output):
    """ This is the main execution function in this module and it ...

    This function ...

    Args:
        db_con_obj (): database connection string like schema/pass@host:port/service_name
        cabin_crew (boolean): True for cabin crew and False for flight deck
        pworker (int): number of process workers to run the rpc query
        timeout (int): number of seconds for rpc call to be timeout
        runtime (int): number of minutes to let this script call rpc and continue execution
        json (boolean): if True results would be dumpted to stdout
        output (str): print out the result to the file name: output
    """

    db_cursor = db_con_obj.cursor()
    cc_crew = []
    fd_crew =[]
    if cabin_crew:
        cc_crew = get_active_crew_list(db_cursor, "%_CC_AG")
        crew_type = 'c'
    else:
        fd_crew = get_active_crew_list(db_cursor, "%_FD_AG")
        crew_type = 'f'
    db_cursor.close()
    db_con_obj.close()
    logger.info("Populated crew lists and ready to rpc calls and database connection is closed!")

    async_terminate = {'break': False}

    def handler(signum, frame):
        logging.error("Signal Ctrl+C caught!!!")
        async_terminate['break'] = True

    signal.signal(signal.SIGINT, handler)

    async_obj = AsyncFactory(rpc_call_wrapper, callback=callback_func ,timeout=timeout,processes=pworker)
    stime = time.time()
    logger.info("Start of acync calls: {0} from backend rpc: {1}".format(stime, backend))

    if backend != "":
	args_list = [(crew, timeout, crew_type,backend) for crew in cc_crew + fd_crew ] 
    else:
        args_list = [(crew, timeout, crew_type,) for crew in cc_crew + fd_crew ] 
    logger.debug("Created args_list {0}".format(args_list[:2] + args_list[-2:]))
    async_map_obj = async_obj.call_maper(args_list)

    logger.debug("async_terminate['break']: {0}".format( async_terminate['break']))

    # widgets = ['Progress: ', Percentage(), ' ', Bar(), ' ', ETA() ]
    # pbar = ProgressBar(widgets=widgets, maxval=len(args_list)).start()
    counter = 0
    while(not async_terminate['break']):                                                                                                                                               
        time.sleep(1)                                                                                                                              
        try:                                                                                                                                       
            while (len(callback_result) > 0):                                                                                                      
                (c, s, t, b, r) = callback_result.pop()                                                                                               
                callbacks[c] = (s,t, b, r)                                                                                                                                                                                                            
                logger.debug("Added item to callback_set: {0}".format((c, s, b, t)))                                                                  
        except Exception as e:                                                                                                                     
            logger.error("Failed to get callback_result.pop() {0}".format(str(e)))                                                                            
        # pbar.update(len(callbacks))
        if counter % 5 == 0:                                                                                                                       
            logger.debug("Counter: {0}, callbacks: {1}, args_list: {2}, time condition is: {3} to {4}".format(counter,len(callbacks), len(args_list),(stime + (runtime * 60.0)), time.time()))         
        if (runtime > 0 and (stime + (runtime * 60.0)) < time.time()) or (len(callbacks) >= len(args_list)):                                       
            logger.info("while loop breaks...")                                                                                                    
            break                                                                                                                                  
        counter += 1
    # pbar.finish()                                                                                                                               
    async_obj.terminate()                                                                                                                          
    logger.info("While loop is done and async_terminate['break'] is: {0}".format(async_terminate['break']))                                        
    logger.info("While loop is done and counter is: {0}  callback_result is: {1}".format(counter, len(callbacks)))                                 


    # Simple print output ...
    # print("########################################")
    # for k,(s, t, _) in callbacks.iteritems(): 
    #     print(k, s, t )
    #     print("=======================================")
    # print("########################################")

    if output:
        if os.path.basename(output).split('.')[-1] == "csv":
            csv_writer(output, [(c, s, t ) for c,(s, t, _) in callbacks.iteritems()], ['Crew id', 'Status code', 'Time of execution'])
        else:
            try:
                f = open(output, "w")
                for c, (s, t, r) in  callbacks.iteritems():
                    f.write("\n======================================\n")
                    f.write("Crew id: {0}   status code: {1}    timeof execution: {2}\n".format(c,s,t))
                    f.write(r)
                f.close()
                logging.info("File {0} is created".format(output))
            except IOError as e:
                logging.error("IO error: {0}".format(e))
            except Exception as e:
                logging.error("File writing error: {0}".format(e))
    if json:
        to_json({'Keys': ['Crew id', 'Status code', 'Time of execution'], 'Results': [(c, s, t ) for c,(s, t, _) in callbacks.iteritems()]})
        logging.info("json output file is created")


    logging.info("Job is done")


def run():
    """ This function parse and check or set all variables to execute the module execution function.

    This function first set all argparser variables and then try to parse them. There are some values that need to be
    set with default values. It also initialize logging object class according to argparser values which are set by user.
    And finally, it calls the execution function with proper values.

    """
    ap = ArgumentParser(description=__doc__, formatter_class=RawDescriptionHelpFormatter)
    ap.add_argument('-d', '--db_con', help='set database connection string if not running cmsshell like: cms_test_jul_live/PASS@cmstest-scan.net.sas.dk:1521/CMST')
    ap.add_argument('-c', '--cabin_crew', default=False, action='store_true', help='set True for cabin crew and False for flight deck default is True')
    ap.add_argument('-s', '--single_crew', default=0, help='set single crew rpc call towards all report workers NOTE: json and output will be ignored and  only print out the result... ')
    ap.add_argument('-o', '--output', help='set file output if the file end with csv or log to get csv or logs otherwise dump of result would be created')
    ap.add_argument('-b', '--backend', help='set rpc call backend like: portal_manpower_f, portal_manpower_c, portal_latest, portal_publish')
    ap.add_argument('-v', '--verbose', default=False, action='store_true', help='set logging to verbose (debug level)')
    ap.add_argument('-j', '--json', default=False, action='store_true', help='set print out result as json')
    ap.add_argument('-r', '--runtime', type=int, default=0, help='set timer to run out of rpc call in minutes default is 0 - no run time limit')
    ap.add_argument('-t', '--timeout', type=int, default=25, help='set time out for rpc call in seconds default is 25 seconds (default time out is IB is 15 but here we have some overheads)')
    ap.add_argument('-p', '--pworker', type=int, default=4, help='set number of process workers for rpc call default is 4')


    args = ap.parse_args()

    if args.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO
    if args.output: 
    	if os.path.basename(args.output).split('.')[-1] == "log":
        	config_logging(log_level=loglevel, files=[args.output])
	elif not os.path.basename(args.output).split('.')[-1] == "cvs":
		logging.error("No correct output file is set for logging. output file should have .log or .csv suffix !!!")
		exit(1)
    else:
        config_logging(log_level=loglevel)

    logging.debug(args.single_crew)
    if args.single_crew:
        if args.backend:
            logger.debug("Sending rpc call to: {0}".format(args.backend))
            logger.info("%### {0} ###%".format(args.backend))
            c, s, t, b, r = rpc_call(args.single_crew, args.timeout, backend_rpc=args.backend)
            if s == 0:
                rxml = mdom.parseString(r)
                print (rxml.toprettyxml())
            else:
                logger.debug("Rpc called failed for crew: {0}, {1}".format(c, s))
        else:    
            for b in ['portal_manpower_f', 'portal_manpower_c', 'portal_latest', 'portal_publish']:
                c, s, t, b, r = rpc_call(args.single_crew, args.timeout, backend_rpc=b)
            if s == 0:
                rxml = mdom.parseString(r)
                print (rxml.toprettyxml())
            else:
                logger.debug("Rpc called failed for crew: {0}, {1}".format(c, s))
        return

    if args.db_con:
          db_con_stripted = args.db_con
    else:
        db_connection = os.environ.get("DB_URL", "NO_CONNECTION_STRING")
        db_schema = os.environ.get("DB_SCHEMA", "NO_SCHEMA_STRING")
        logger.info("Environment variables: DB_SCHEMA is: {0} and DB_URL is: {1}".format(db_schema, db_connection))
        db_con_stripted = db_schema + "/" + db_schema + "@" + db_connection.split("%")[-1]
	if db_connection[0:7] == "oracle:":
		db_con_stripted = db_connection[7:]
	else:
		db_con_stripted = db_connection
    logger.info("Connection string is: {0}".format(db_con_stripted))
    try:
            import cx_Oracle as oc
            con = oc.connect(db_con_stripted)
            # con = oc.connect("cms_test_jul_live/cms_test_jul_live@cmstest-scan.net.sas.dk:1521/CMST") # sample connection
            logger.debug("Successfully connected to database")
    except oc.DatabaseError as e:
            err, = e.args
            logger.error("Oracle connection error code: {0}".format(err.code))
            logger.error("Oracle connection error message: {0}".format(err.message))
            exit(1)
    except:
            logger.error("Connecting to database failed...")
            exit(1)

    if args.backend:
        global backend
        backend = args.backend
    logger.info("ArgumentParser is done")
    # Pass required variable to execution function
    execution(con, args.cabin_crew, args.pworker, timeout=args.timeout, runtime=args.runtime, json=args.json, output=args.output)


if __name__ == '__main__':
    """ Main function to report start and end time and run the main function run()
        Signal handler is registered here as well.
    """
    start_time = time.time()
    run()
    time.sleep(2)
    end_time = time.time()
    end_time_str = time.strftime('%Y%m%d %H:%M:%S', time.localtime(end_time))
    logging.critical("End of the execution at {0} and took: {1:0.2f} seconds.\n\n".format(end_time_str, (end_time - start_time)))
    logging.shutdown() # tell logger to finish up and flush in order to terminate gracefully.



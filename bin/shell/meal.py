from xmlrpclib import ServerProxy
from carmensystems.dig.framework.dave import DaveSearch, DaveMultiSearch, DaveConnector, DaveStorer
from dig.DigJobQueue import DigJobQueue
from utils import TimeServerUtils
import carmensystems.dig.framework.carmentime as carmenttime
from AbsTime import AbsTime
import os, sys
import subprocess
import time

valid_regions = ["SKS", "SKD", "SKN"]

def _execute_shell_cmd(cmd, args):
    """ Executes a shell command and returns the return code, stdout and sterr
    """
    proc = subprocess.Popen([cmd, args], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    (out, err) = proc.communicate()
    ret = proc.wait()
    return (ret, out, err)


def _submit_job(params):
    """ Submits a meal job with the parameters specified 
        @param params: Dictionary of parameters
        
    """
    
    djq = DigJobQueue('meal', 
                      'crew_meal_manual_job', 
                      'report_sources.report_server.rs_CrewMealOrderReport', 
                      '1', 
                      os.environ["DB_URL"], 
                      os.environ["DB_SCHEMA"], 
                      False)

    timeserver = TimeServerUtils.TimeServerUtils(useSystemTimeIfNoConnection=True)
    starttime = AbsTime(carmenttime.toCarmenTime(timeserver.getTime()))

    params['runByUser'] = os.path.expandvars('$USER')
    params['starttime'] = str(starttime)
    params['reload'] = '1'
    
    id = djq.submitJob(params, 0, starttime)
    
    print "Job ID: %s" % (id)


def start_rs():
    """ Starts a report server for meal i.e.
        sysmondctl start
        sysmondctl start SAS_RS_WORKER_LATEST forced=True
        sysmondctl start meal forced=True
        
        The servers are stopeed with sysmondctl exit
        
    """

    ret, std, err = _execute_shell_cmd("sysmondctl", "status")

    start_server = False
    start_latest = False
    start_meal = False

    if ret != 0 and std.count("sysmond instance is not running") > 0:
        start_server = True
        start_latest = True
        start_meal = True
    elif ret == 0:
        start_latest = std.count("SAS_RS_WORKER_LATEST") == 0
        start_meal = std.count("meal")  == 0
    else:
        print "Failed to get sysmond status"
    
    if start_server:
        print "Starting sysmond"
        ret, std, err  = _execute_shell_cmd("sysmondctl", "start")
        time.sleep(5) # We must wait until the server is up and running
         
    if start_latest and ret == 0 and std.count("error") == 0:
        print "Starting SAS_RS_WORKER_LATEST worker"
        ret, std, err = _execute_shell_cmd("sysmondctl", "start SAS_RS_WORKER_LATEST forced=true")

    if start_meal and ret == 0 and std.count("error") == 0:
        print "Starting meal channel"
        ret, std, err = _execute_shell_cmd("sysmondctl", "start meal forced=true")
        
    if ret != 0 or std.count("error") > 0:
        print "Failed to start meal report server:\n\r StdOut:\n\r %s StdErr:\n\r %s" % (std, err)
    else:
        print "Meal report server is running"

    
def create_forecast(month, load_air_port=None, region=None, send = False):
    """ Starts a meal forecast job. 
        Example:
        meal forecast Jan2012 CPH SKD
        meal forecast Jan2012 CPH SKD

        @param month: The meal month (and year), e.g. Jan2011
        @param load_air_port: the load airport e.g. CPH or "" for all airports
        @param region: The region e.g. SKS, SKD.
 
    """

    month = str(month)
    load_air_port = load_air_port and str(load_air_port)
    region = region and str(region)

    if not region in valid_regions and region is not None:
        print "Invalid region"
        return

    firstdate = AbsTime("01%s 00:00" % month)
    lastdate = firstdate.addmonths(1)
    
    commands = "create"
    if send:
        commands += ";send;"

    job_params = {'forecast':'true',
                  'commands': commands,
                  'loadAirport': load_air_port, 
                  'region' : region, 
                  'fromDate':str(firstdate),
                  'toDate':str(lastdate)}
    
    _submit_job(job_params)


def create_order(day, load_air_port=None, region=None, send = False):
    """ Starts a meal order job. 
        Example:
        meal create_order 01Jan2012 CPH SKD
        meal create_order 01Jan2012

        @param day: The meal load day , e.g. 01Jan2011
        @param load_air_port: the load airport e.g. CPH or "" for all airports
        @param region: The region e.g. SKS, SKD.
 
    """

    day = str(day)
    load_air_port = load_air_port and str(load_air_port)
    region = region and str(region)

    if not region in valid_regions and region is not None:
        print "Invalid region"
        return
        
    day = AbsTime("%s 00:00" % day)

    commands = "create"
    if send:
        commands += ";send;"


    job_params = {'forecast':'false',
                  'commands': commands,
                  'loadAirport': load_air_port, 
                  'region' : region, 
                  'fromDate':str(day)}
    
    _submit_job(job_params)


def create_update(update_time, load_air_port=None, region=None):
    """ Starts a meal udpate job. 
        Example:
        meal create_update "01Jan2012 15:14" CPH SKD
        meal create_update "01Jan2012 04:00"

        @param update_time: The meal load update time, e.g. "01Jan2011 06:34"
        @param load_air_port: the load airport e.g. CPH or "" for all airports
        @param region: The region e.g. SKS, SKD.
 
    """

    update_time = str(update_time)
    load_air_port = load_air_port and str(load_air_port)
    region = region and str(region)

    if not region in valid_regions and region is not None:
        print "Invalid region"
        return
        
    update_time = AbsTime(update_time)

    commands = "create;update;"

    job_params = {'forecast':'false',
                  'commands': commands,
                  'loadAirport': load_air_port, 
                  'region' : region, 
                  'updateTime':str(update_time)}
    
    _submit_job(job_params)


def send(order_type, order_num):
    """ Sends a meal order to suppliers. 
        Example:
        meal send order 95301
        meal send forecast 1488

        @param order_type:  order, forecast, or update
        @param order_num: order number
 
    """

    if order_type == "order":
        forecast = 'false'
    elif order_type == "forecast":
        forecast = 'true'
    elif order_type == "update":
        print "Explicit send is not supported for updates"
        return 
    else:
        print "Invalid order type %s" % (order_type)
        return 

    job_params = {'forecast': forecast,
                  'commands': 'send',
                  'order0': str(order_num)}
    
    _submit_job(job_params)


def cancel(order_type, order_num):
    """ Sends a meal order to suppliers. 
        Example:
        meal cancel order 95301
        meal cancel forecast 1488

        @param order_type:  order, forecast, or update
        @param order_num: order number
 
    """

    if order_type == "order":
        forecast = 'false'
    elif order_type == "forecast":
        forecast = 'true'
    elif order_type == "update":
        print "Update orders cannot be cancelled"
        return 
    else:
        print "Invalid order type %s" % (order_type)
        return 

    job_params = {'forecast': forecast,
                  'commands': 'send',
                  'order0': str(order_num)}
    
    _submit_job(job_params)

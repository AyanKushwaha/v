#! /usr/bin/env python

__author__="Oscar Grandell <oscar.grandell@hiq.se>"
__version__= "0.1"

import time
import rpc
import logging
import threading
import signal
import os
import sys
import random
"""
This is test script to invoke multiple rpc request toward Interbids report workers with specified time out.
"""

stop = threading.Event()
exit = threading.Event()

class LoadTestThread(threading.Thread):

    def __init__(self, id, crewid):
        threading.Thread.__init__(self, name=id)
        self.id = id
        if self.id is None:
            self.id = uuid.uuid4()
        self.crewid = crewid

    def run(self):
        rpc.jmp_get_assignments(self.crewid, 'portal_manpower_c') #1s
        rpc.jmp_crew_init(self.crewid, 'portal_manpower_c') #2s
        time.sleep(5)
        rpc.get_rosters(self.crewid, 'portal_publish') #3s
        rpc.jmp_type_based_routing_info(self.crewid, 'portal_manpower_c') #<1s
        rpc.jmp_get_bid_list(self.crewid, 'portal_manpower_c') #4s
        time.sleep(5)
        rpc.jmp_create_bid(self.crewid, 'portal_manpower_c') #6s
        time.sleep(10)
        rpc.jmp_get_bid(self.crewid, 'portal_manpower_c') #1s
        time.sleep(5)
        rpc.jmp_delete_bid(self.crewid, 'portal_manpower_c') #4s
        # Total execution time ~50sec

def run(st=10, fixed_crew=None):
    id = [0]  # mutable int
    sleep_time = st

    #crew_list = os.listdir(os.path.expandvars("$CARMDATA/manpower/crew_information/LEAVE"))

    #Random set of crew pick from Interbids.
    crew_list_dk = ['10112', '10174', '10281', '10293', '10585', '11294', '11642', '11880', '12385', '12518', '13364', '13671', '13980', '14125', '14547', '16168', '16289', '16454', '16897']
    crew_list_se = ['15840', '15850', '15959', '16053', '16068', '16086', '16087', '16117', '16136', '16138', '16159', '16171', '16174', '16204', '16234', '16241', '16251', '16254', '16255']
    crew_list_nk = ['86706', '86708', '86709', '86710', '86711', '86712', '86713', '86714', '86718', '86725', '86726', '86729', '86731', '86733', '86734', '86735', '86736', '86738', '86740']
    crew_list = crew_list_dk+crew_list_se+crew_list_nk

    def start():
        id[0]+=1

        #try;
        crew = crew_list[(id[0]-1) % len(crew_list)] #fixed_crew or random.choice(crew_list)
        #except:
        #    do_sigint()
        print "Using crew %s for simulation" % crew
        LoadTestThread(id[0], crew).start()
        return stop.is_set()
    if sleep_time:
        repeat_timer(sleep_time, start)
    else:
        start()

    def status():
        print "main: %d sessions running."%len(get_threads())
    repeat_timer(10, status)

    repeat_timer(1, sys.stdout.flush)

    def do_sigint(sig, frame):
        if not stop.is_set():
            print "main: stopping myself..."
            stop.set()
        elif not exit.is_set():
            print "main: stopping others..."
            exit.set()
        else:
            print "main: Killing myself..."
            os.kill(os.getpid(), 9)
    signal.signal(signal.SIGINT, do_sigint)

    while not (stop.is_set() and get_threads() == []):
        time.sleep(0.1)
    print "main: %d threads running, main thread says bye"%len(get_threads())

def get_threads():
    return [x for x in threading.enumerate() if isinstance(x, LoadTestThread)]

def repeat_timer(interval, fun, *args, **kwargs):
    def run():
        if not fun(*args, **kwargs):
            t = threading.Timer(interval, run)
            t.daemon = True
            t.start()
    run()

if __name__ == '__main__':
    """ Main function to report start and end time and run the main function run()
        Signal handler is registered here as well.
    """
    if sys.argv[1] == "-h":
        print "Usage: python bin/shell/IB_stresstest.py [-u <users per hour>]"
        print "-u <users per hour>      - Default 360, i.e. one user every 10:th second"
        sys.exit(1)

    try:
        if sys.argv[1] == "-u":
            st = float(3600 / int(sys.argv[2]))
            print "%s users per hour, i.e. starting one thread every %s second" % (sys.argv[2], st)
    except:
        st = 10

    start_time = time.time()
    run(st=st)
    # time.sleep(2)
    end_time = time.time()
    end_time_str = time.strftime('%Y%m%d %H:%M:%S', time.localtime(end_time))
    logging.critical("End of the execution at {0} and took: {1:0.2f} seconds.\n\n".format(end_time_str, (end_time - start_time)))
    logging.shutdown() # tell logger to finish up and flush in order to terminate gracefully.
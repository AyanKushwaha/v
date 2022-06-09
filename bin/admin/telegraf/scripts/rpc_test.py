#! /usr/bin/env python

import os
import sys
import time
import signal
sys.path.insert(0, os.environ['CARMUSR'] + "/bin/shell")

import rpc as r

class Timeout():
    """Timeout class using ALARM signal."""
    class Timeout(Exception):
        pass

    def __init__(self, sec):
        self.sec = sec

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)

    def __exit__(self, *args):
        signal.alarm(0)    # disable alarm

    def raise_timeout(self, *args):
        raise Timeout.Timeout()

# print len(r.list_functions("portal_latest"))essage = ''
influx_message = ''
for b in ['portal_latest','portal_publish','portal_manpower_f','portal_manpower_c']:
# b = sys.argv[1]
	h, rpc = r._getrpc(b)
	influx_message += 'cms_rpc,backend=' + b
	start_time = time.time()
	try:
		with Timeout(30):
       			rpc_return = rpc.RaveServer.evalPythonString('2+2') 
		if rpc_return == '4':
			res = 'success'
		else:
			res = 'failed'
	except Timeout.Timeout:
		res="timeout"
	except Exception as e:
		res = 'error'
	end_time = time.time()
	influx_message += ',test=python_eval result="' + res +'",duration=' + str(end_time - start_time) + '\n'

print influx_message
#print 'cms_rpc,backend=portal_latest,test=python_eval return="ERROR",duration=1.1'
#print 'cms_rpc,backend=portal_publish,test=python_eval return="ERROR",duration=1.1'

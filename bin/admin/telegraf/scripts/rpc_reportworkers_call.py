#! /usr/bin/env python

import os
import sys
import time
sys.path.insert(0, os.environ['CARMUSR'] + "/bin/shell")

import rpc as r
# print len(r.list_functions("portal_latest"))essage = ''
influx_message = ''
for b in ['portal_latest','portal_publish','portal_manpower_f','portal_manpower_c']:
# b = sys.argv[1]
	h, rpc = r._getrpc(b)
	influx_message += 'cms_rpc,backend=' + b
	start_time = time.time()
	try:
       		rpc_return = rpc.RaveServer.evalPythonString('2+2') 
		if rpc_return == '4':
			res = 'success'
		else:
				res = 'failed'
	except Exception as e:
		res = 'error'
	end_time = time.time()
	influx_message += ',test=python_eval result="' + res +'",duration=' + str(end_time - start_time) + '\n'
# influx_message += ',test=python_eval result="' + res +'",duration=' + str(end_time - start_time) + ' '

print influx_message
#print 'cms_rpc,backend=portal_latest,test=python_eval return="ERROR",duration=1.1'
#print 'cms_rpc,backend=portal_publish,test=python_eval return="ERROR",duration=1.1'

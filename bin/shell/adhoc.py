import os

def list():
	"Lists available ad-hoc scripts"
	l = [x[:-3] for x in os.listdir(os.path.expandvars("$CARMUSR/lib/python/adhoc")) if x[-3:] == '.py' and x not in ('fixrunner.py', '__init__.py')]
	print '\n'.join(l)

def run(script):
	"Runs a specific ad-hoc script"
	fn = os.path.expandvars("$CARMUSR/lib/python/adhoc/%s.py" % script)
	if not os.path.isfile(fn):
		raise IOError("Adhoc script %s not found" % script)
	

def info(script):
	"Gets information about a specific script"
	fn = os.path.expandvars("$CARMUSR/lib/python/adhoc/%s.py" % script)
        if not os.path.isfile(fn):
                raise IOError("Adhoc script %s not found" % script)
	

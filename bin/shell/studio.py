"Studio startup commands"
import sys, os

def _startStudio(type='t'):
        retcode = os.system("$CARMUSR/bin/studio.sh -S %s" % (type))
		
def tracking():
	"Starts Tracking studio"
        _startStudio(type='t')
        
def planning():
        "Starts Planning studio"
        _startStudio('p')

def prestudio():
        "Starts Prestudio studio"
        _startStudio('m')

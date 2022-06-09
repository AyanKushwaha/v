

import adhoc.fixrunner as fixrunner
import shutil
import os 


__version__ = '1'

@fixrunner.run
def fixit(dc, *a, **k):
    """
    Copy $CARMDATA/ETABLES/select_Tracking.etab to $CARMDATA/ETABLES/select_DayOfOps.etab
    The table contains rules to filter in the filter form and should show up in the 
    same way for DayOfOps as in Tracking.
    """
    try:  
        os.environ["CARMDATA"]
    except KeyError: 
        print "The envrionment variable CARMDATA has not been set"
        sys.exit(1)

    try:
        shutil.copy2(os.path.join(os.environ['CARMDATA'],'ETABLES/select_Tracking.etab'), os.path.join(os.environ['CARMDATA'],'ETABLES/select_DayOfOps.etab'))
    except IOError:
        print "The file could either not be found or could not be copied for some reason."

fixit.program = 'sascms_6619.py (%s)' % __version__

if __name__ == '__main__':
    fixit()



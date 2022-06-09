# Close one application as soon as another one has closed
#
# Arvid Ericsson, Jeppesen 2012

from optparse import OptionParser
import time
import win32api
import win32gui
import win32con

def read_commandline_parameters():
    '''
    Read command line parameters
    '''
    parser = OptionParser()
    
    parser.add_option("--lc",    help = "Primary Window Class Name of window to wait for (optional)")
    parser.add_option("--ln",    help = "Primary Window Name (Caption) of window to wait for (optional)")
    parser.add_option("--ec",    help = "Secondary Window Class Name of window to wait for (optional)")
    parser.add_option("--en",    help = "Secondary Window Name (Caption) of window to wait for (optional)")
    parser.add_option("--sleep", help = "Sleep time between polling for primary being closed. Default is 4 seconds.")	
	
    # Parse the command line
    (opts, args) = parser.parse_args()
    # Return the options as a dictionary of option:value
    return vars(opts)

def setup():
    settings = {}
    params = read_commandline_parameters()

    if params['lc'] is None and params['ln'] is None:
        raise Exception("ERROR: You must specify Window Class Name or Window Name for the primary process!")

    settings["primary_windowclassname"] = params['lc']
    settings["primary_windowname"] = params['ln']

    if params['ec'] is None and params['en'] is None:
        raise Exception("ERROR: You must specify Window Class Name or Window Name for the Exceed on Demand process!")

    settings["secondary_windowclassname"] = params['ec']
    settings["secondary_windowname"] = params['en']
    
    if params['sleep'] is None:
         settings["sleeptime"] = 4         
    else:
         settings["sleeptime"] = int(params['sleep'])
         
    return settings

         
def main():
    settings = setup()

    # Wait for the primary window to stop existing
    while win32gui.FindWindow(settings["primary_windowclassname"], settings["primary_windowname"]):
        time.sleep(settings["sleeptime"])

    # Now the primary window doesn't exist anymore. Kill the secondary!
    secondary_hwnd = win32gui.FindWindow(settings["secondary_windowclassname"], settings["secondary_windowname"])
    win32api.SendMessage(secondary_hwnd, win32con.WM_CLOSE)



if __name__=='__main__':
    main()
